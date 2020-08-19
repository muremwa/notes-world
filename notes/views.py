# other imports
from itertools import chain
from datetime import datetime
import re

# django imports
from django.shortcuts import redirect, reverse,  get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.views import generic, View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.dispatch import Signal
from django.http import Http404

from markdown_deux import markdown

# models & forms (local imports)
from .forms import NoteForm, NoteForeignForm, CommentForm
from account.models import Connection, Profile
from .models import Note, Comment, Reply


notes_signal = Signal(providing_args=['note', 'user', 'comment', 'reply', 'mentioned'])


# all user notes
class NoteIndex(generic.ListView):
    template_name = 'notes/index.html'
    context_object_name = "notes"

    def connected_users_notes(self):
        public_note = Note.objects.filter(privacy="PB")
        # get all connected users
        other_notes = Note.objects.notes_user_can_see(self.request.user)
        return chain(public_note, other_notes)

    def get_queryset(self):
        notes = chain(self.request.user.note_set.all(), self.connected_users_notes())
        sanitized_notes = []
        for note in notes:
            if note not in sanitized_notes:
                sanitized_notes.append(note)
        return sanitized_notes

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(reverse('base_account:account-index'))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.request.user.note_set.all().count()
        return context


# each note page
class NotePage(LoginRequiredMixin, generic.DetailView):
    template_name = 'notes/note.html'
    model = Note

    def get_context_data(self, **kwargs):
        # does the user want the old comment section?
        comment_section = self.request.GET.get('normal_comment_section', None)
        prev_comment_section = self.request.session.setdefault('normal_comment_section', False)

        if comment_section is not None and int(comment_section) != int(prev_comment_section):
            self.request.session['normal_comment_section'] = bool(int(comment_section))

        context = super().get_context_data(**kwargs)
        additional_context = {
            'collaborators': context.get('note').collaborators.all(),
            'connected_note': False,
            'normal_comment_section': self.request.session.get('normal_comment_section', False)
        }

        # add comment section context if the user wants the old comment section
        if self.request.session.get('normal_comment_section', False):
            additional_context.update({
                'comments': context.get('note').comment_set.all(),
                'comment_count': context.get('note').comment_set.count(),
                'form': CommentForm,
                'input_name': 'comment',
                'action_url': reverse("notes:comment", args=[str(context.get('note').pk)])
            })
        context.update(additional_context)

        if self.request.user != context['note'].user and context['note'].privacy == "CO":
            if Connection.objects.exist(self.request.user, context['note'].user):
                context['connected_note'] = True
        return context


# note creation
class NoteCreate(LoginRequiredMixin, generic.CreateView):
    form_class = NoteForm
    template_name = 'notes/note_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['input_name'] = "new note"
        return context

    # user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# note editing
class NoteEdit(LoginRequiredMixin, generic.UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_edit.html'
    note = None

    @classmethod
    def set_note(cls, note_id):
        cls.note = Note.objects.get(pk=note_id)

    def get(self, request, *args, **kwargs):
        self.set_note(kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if self.request.user == self.note.user:
            form_class = NoteForm
        else:
            form_class = NoteForeignForm
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['input_name'] = "edit note"
        context['collaborators'] = context['note'].collaborators.all()
        return context

    def post(self, request, *args, **kwargs):
        self.set_note(kwargs['pk'])
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.last_modified = datetime.now()
        form.instance.last_modifier = int(self.request.user.id)
        return super().form_valid(form)


# note delete
class NoteDelete(LoginRequiredMixin, generic.DeleteView):
    model = Note
    success_url = reverse_lazy("notes:index")


# collaborations page
class Collaborations(LoginRequiredMixin, generic.TemplateView):
    template_name = "notes/collaboration-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collaborations'] = Note.objects.collaborations(self.request.user)
        return context


# collaboration form
class CollaboratorsEdit(LoginRequiredMixin, generic.TemplateView):
    template_name = "notes/collaborators.html"
    permission_denied_message = "You cannot edit collaborators for a note you do not own"

    def get_note(self):
        return Note.objects.get(id=self.kwargs['pk'])

    def collaborators(self):
        return self.get_note().collaborators.all()

    def collaboration_suggestions(self):
        suggestions = []
        conns = Connection.objects.get_user_conn(self.request.user)
        not_ = self.collaborators()
        for conn in conns:
            if conn.profile not in not_:
                suggestions.append(conn)
        return suggestions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collaborators'] = self.collaborators()
        context['note'] = self.get_note()
        context['suggestions'] = self.collaboration_suggestions()

        if context['note'].user.pk != self.request.user.pk:
            raise PermissionDenied("Only the owner of '{note}' can see this page".format(
                note=context['note'].title
            ))

        return context


class CommentProcessor:
    """
    This class can be inherited to enable a view process a comment
    user the 'mark' method (short for markdown) to process a comment
    """
    @staticmethod
    def user_linking(user, add_punctuation):
        """Actual transforming users links to markdown"""
        url = reverse("base_account:foreign-user", kwargs={"user_id": str(user.pk)})
        # TODO:: Ensure this line can get relative domains instead of fixed ones
        line = '[@{user_name}](http://127.0.0.1:8000{user_url}){punct}'.format(
            user_name=user.username,
            user_url=url,
            punct=add_punctuation
        )
        return line

    # process comment
    def process_comment(self, comment_text):
        """Takes a comment or reply and returns a markdown version with links to all tagged users"""
        mentioned = []
        split_comment = comment_text.split(" ")
        new_comment = comment_text

        for k, text in enumerate(split_comment):
            if re.search(r'@\w+', text):
                name = text.split('@')[-1]

                # check if punctuation is present and if it's illegal
                ex_name = [string for string in re.split(r'(\W*$)', name) if string]
                punctuation = ''
                if len(ex_name) == 2:
                    name = ex_name[0]
                    punctuation = ex_name[1]
                    if punctuation in ['@', '#']:
                        continue

                try:
                    user = User.objects.get(username__exact=name)
                    mentioned.append(user)
                except ObjectDoesNotExist:
                    continue
                split_comment[k] = self.user_linking(user, punctuation)

        return {
            'comment': " ".join(split_comment),
            'mentioned': mentioned
        }

    # make it html
    def mark(self, comment):
        """
        Main method to use processor
        :param comment: a original comment
        :type comment: string
        :return: a dict with mentioned users (a list: mentioned)
        and the processed comment(html version of the comment as a string: processed_comment)
        :rtype: dict
        """
        process = self.process_comment(comment)
        return {
            'mentioned': process.get('mentioned', []),
            'processed_comment': markdown(process.get('comment', ''))
        }


class CommentProcessing(LoginRequiredMixin, CommentProcessor, View):
    # raise 404 error if its a get request
    def get(self, *args, **kwargs):
        raise Http404

    # process
    def post(self, *args, **kwargs):
        form = CommentForm(self.request.POST)
        if form.is_valid():
            original_text = form.cleaned_data['comment']
            post_process = self.mark(original_text)
            browser_text = post_process['processed_comment']
            mentioned = post_process['mentioned']
            comment = Comment(
                user_id=self.request.user.id,
                note_id=kwargs['note_id'],
                comment_text=browser_text,
                original_comment=original_text,
            )
            comment.save()
            notify = []
            for user_ in mentioned:
                if user_ != self.request.user and user_ != get_object_or_404(Note, pk=kwargs['note_id']).user:
                    comment.mentioned.add(user_.profile)
                    notify.append(user_)
            if notify:
                notes_signal.send(self.__class__, comment=comment, mentioned=notify)

        url = reverse("notes:note-page", args=[str(kwargs['note_id'])]) + "#comments"
        return redirect(url)


class EditComment(CommentProcessing):
    def post(self, *args, **kwargs):
        form = CommentForm(self.request.POST)
        comment = Comment.objects.get(pk=kwargs['comment_id'])
        if comment.user == self.request.user:
            if form.is_valid():
                comment.original_comment = form.cleaned_data['comment']
                post_process = self.mark(form.cleaned_data['comment'])
                comment.comment_text = post_process['processed_comment']
                comment.modified = datetime.now()
                comment.save()
                notify = []
                for user_ in post_process['mentioned']:
                    if user_.profile not in comment.mentioned.all():
                        if user_ != self.request.user:
                            comment.mentioned.add(user_.profile)
                            notify.append(user_)

                if len(notify):
                    notes_signal.send(self.__class__, comment=comment, mentioned=notify)
        else:
            raise Http404

        return redirect(reverse("notes:note-page", args=[str(comment.note.id)])+"#comment"+str(kwargs['comment_id']))


class CommentReply(CommentProcessing):
    def get(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['comment_id'])
        replies = comment.reply_set.all()
        return render(self.request, 'notes/reply.html', {
            'comment': comment,
            'replies': replies,
            'form': CommentForm,
        })

    def post(self, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['comment_id'])
        form = CommentForm(self.request.POST)
        if form.is_valid():
            reply_ = form.cleaned_data['comment']
            post_process = self.mark(reply_)
            new_reply = Reply(
                original_reply=reply_,
                reply_text=post_process['processed_comment'],
                comment=comment,
                user=self.request.user
            )
            new_reply.save()
            notify = []
            for user_ in post_process['mentioned']:
                if user_ != self.request.user:
                    new_reply.mentioned.add(user_.profile)
                    notify.append(user_)

            if len(notify):
                notes_signal.send(self.__class__, reply=new_reply, mentioned=notify)

        return redirect(reverse("notes:reply-comment", args=[str(comment.id)])+"#replies")


class ReplyActions(CommentProcessing):
    @staticmethod
    def delete_reply(reply):
        reply.delete()

    def edit_reply(self, reply, new_reply_text, user):
        post_process = self.mark(new_reply_text)
        reply.original_reply = new_reply_text
        reply.reply_text = post_process['processed_comment']
        reply.modified = True
        reply.save()
        notify = []

        for user_ in post_process['mentioned']:
            if user_.profile not in reply.mentioned.all():
                if user_ != user:
                    reply.mentioned.add(user_.profile)
                    notify.append(user_)

        if len(notify):
            notes_signal.send(self.__class__, reply=reply, mentioned=notify)

    def post(self, *args, **kwargs):
        reply = get_object_or_404(Reply, pk=kwargs['reply_id'])

        # editing reply
        if kwargs['option'] == "edit":
            form = CommentForm(self.request.POST)
            if form.is_valid():
                self.edit_reply(reply, form.cleaned_data['comment'], self.request.user)
            return redirect(reverse("notes:reply-comment", args=[str(reply.comment.id)])+"#reply"+str(reply.id))

        # deleting reply
        elif kwargs['option'] == "delete":
            if self.request.user == reply.user:
                self.delete_reply(reply)
            else:
                raise Http404
            return redirect(reverse("notes:reply-comment", args=[str(reply.comment.id)])+"#replies")

        else:
            raise Http404


# add collaborator
@login_required
def add_collaborator(request, **kwargs):
    note = get_object_or_404(Note, id=kwargs['note_id'])
    add_this = get_object_or_404(Profile, user=kwargs['user_id'])

    if request.user != note.user:
        raise PermissionDenied("You are not authorised to add a collaborator")
    else:
        note.collaborators.add(add_this)
        notes_signal.send(add_collaborator, note=note, user=add_this.user)
    return redirect(reverse("notes:edit-collaborators", args=[str(kwargs['note_id'])]))


# remove collaboration
@login_required
def rm_collaborator(request, **kwargs):
    note = get_object_or_404(Note, id=kwargs['note_id'])
    remove_this = get_object_or_404(Profile, user=kwargs['user_id'])

    if request.user != note.user:
        raise Http404
    else:
        note.collaborators.remove(remove_this)

    return redirect(reverse("notes:edit-collaborators", args=[str(kwargs['note_id'])]))


# make a note collaborative
@login_required
def make_collaborative(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if request.user != note.user:
        raise Http404
    else:
        note.collaborative = True
        if note.privacy != "PB":
            note.privacy = "CO"

        note.save()

    return redirect(reverse("notes:edit-collaborators", args=[str(note.id)]))


# make not collaborative
@login_required
def undo_collaborative(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if note.user != request.user:
        raise Http404
    else:
        collaborators = note.collaborators.all()
        # remove all collaborators first
        for collaborator in collaborators:
            note.collaborators.remove(collaborator)
        # make collaborative false
        note.collaborative = False
        note.save()

    return redirect(reverse("notes:note-page", args=[str(note_id)]))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    response = {}

    if comment.user == request.user or comment.note.user == request.user:
        if request.method == "POST":
            comment.delete()
            response['success'] = True
            response['message'] = "Comment Deleted"
        else:
            raise Http404
    else:
        response['success'] = False
        response['message'] = "server couldn't complete your request"

    return JsonResponse(response)


def retrieve(what, what_, what_id, user_, response):
    try:
        obj = what.objects.get(pk=what_id)
        if obj.user == user_:
            response['success'] = True
            if what_ == 'reply':
                response['text'] = obj.original_reply
            else:
                response['text'] = obj.original_comment
        else:
            response['success'] = False
            response['message'] = "the {} does not belong to you".format(what_)

    except ObjectDoesNotExist:
        response['success'] = False
        response['message'] = "The {} does not exist".format(what_)

    return response


@login_required
def get_comment_or_reply(request, **kwargs):
    response = {}

    if kwargs['what'] == "comment":
        result = retrieve(Comment, 'comment', kwargs['what_id'], request.user, response)

    elif kwargs['what'] == "reply":
        result = retrieve(Reply, 'reply', kwargs['what_id'], request.user, response)

    else:
        raise Http404

    return JsonResponse(result)
