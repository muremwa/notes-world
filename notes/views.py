# other imports
from itertools import chain
from random import choices
import re
from typing import Literal, Type

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
from django.http import Http404, HttpResponseForbidden
from django.utils.timezone import now

from markdown_deux import markdown

# models & forms (local imports)
from .forms import NoteForm, NoteForeignForm, CommentForm, TagForm
from account.models import Connection, Profile
from .models import Note, Comment, Reply, Tag


notes_signal = Signal(['note', 'user', 'comment', 'reply', 'mentioned'])


# all user notes
class NoteIndex(generic.ListView):
    template_name = 'notes/index.html'
    context_object_name = "notes"

    def connected_users_notes(self):
        return chain(
            Note.objects.filter(privacy="PB"),  # public notes
            Note.objects.notes_user_can_see(self.request.user)  # connected users notes
        )

    def get_queryset(self):
        notes = chain(self.request.user.note_set.all(), self.connected_users_notes())
        sanitized_notes = []
        for note in notes:
            if note not in sanitized_notes:
                sanitized_notes.append(note)

        _tags = self.request.GET.get('tag', '').split(',')

        for _tag in _tags:
            if _tag:
                if _tag == 'me':
                    sanitized_notes = filter(lambda note_: note_.user == self.request.user, sanitized_notes)

                elif _tag == 'others':
                    sanitized_notes = filter(lambda note_: note_.user != self.request.user, sanitized_notes)

                else:
                    tag_objs = Tag.objects.filter(name__iexact=_tag)

                    if tag_objs.count() > 0:
                        sanitized_notes = filter(lambda note_: tag_objs[0] in note_.tags.all(), sanitized_notes)
                    else:
                        sanitized_notes = []

        return sorted(sanitized_notes, key=lambda note_: note_.pk, reverse=True)

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(reverse('base_account:account-index'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        _query_tags = list(map(lambda tag: tag.strip(), self.request.GET.get('tag', '').split(',')))
        query_tags = Tag.objects.filter(name__in=_query_tags)
        tags = Tag.objects.exclude(name__in=_query_tags)

        context.update({
            'tags': {*query_tags, *choices(tags, k=(6-query_tags.count()))},
            'q_tag': self.request.GET.get('tag', ''),
            'q_tags': _query_tags,
            'count': self.request.user.note_set.count()
        })
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
            if Connection.objects.exist(self.request.user, context['note'].user, status=True):
                context['connected_note'] = True
        return context


# note creation
class NoteCreate(LoginRequiredMixin, generic.CreateView):
    form_class = NoteForm
    template_name = 'notes/note_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'input_name': 'new note',
            'second_btn': {
                'name': 'Save and edit tags',
                'url': f'{self.request.path}?editTags=1'
            }
        })
        return context

    def get_success_url(self):
        if self.request.GET.get('editTags', '0') == '1':
            return reverse("notes:add-tag", kwargs={"pk": str(self.object.pk)})
        return super().get_success_url()

    # user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def add_tags_to_note(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if note.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'GET':
        form = TagForm(instance=note)

        return render(request, 'notes/tag_edit.html', {
            'note': note,
            'form': form
        })

    elif request.method == 'POST':
        form = TagForm(instance=note, data=request.POST)

        if form.is_valid() and form.changed_data:
            form.save()

        return redirect(f'{reverse("notes:note-page", kwargs={"pk": str(note.pk)})}#note-tags')

    else:
        raise Http404


# note editing
class NoteEdit(LoginRequiredMixin, generic.UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_edit.html'

    def get_form(self, form_class=None):
        note = get_object_or_404(Note, pk=self.kwargs.get('pk'))
        if self.request.user == note.user:
            form_class = NoteForm
        else:
            form_class = NoteForeignForm
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'input_name': 'edit note',
            'can_edit': self.request.user.profile in context.get('note').collaborators.all(),
        })

        if self.object.user == self.request.user:
            context.update({
                'second_btn': {
                    'name': 'edit tags too',
                    'url': f'{self.request.path}?editTags=1'
                }
            })
        return context

    def get_success_url(self):
        if self.request.GET.get('editTags', '0') == '1' and self.request.user == self.object.user:
            return reverse("notes:add-tag", kwargs={"pk": str(self.object.pk)})
        return super().get_success_url()

    def form_valid(self, form):
        form.instance.last_modified = now()
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
    def _user_linking(user, add_punctuation):
        """Actual transforming users links to markdown"""
        url = reverse("base_account:foreign-user", kwargs={"user_id": str(user.pk)})
        line = '[@{user_name}]({user_url}){punct}'.format(
            user_name=user.username,
            user_url=url,
            punct=add_punctuation
        )
        return line

    # process comment
    def _process_comment(self, comment_text):
        """Takes a comment or reply and returns a markdown version with links to all tagged users"""
        mentioned = []
        split_comment = comment_text.split(" ")

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
                split_comment[k] = self._user_linking(user, punctuation)

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
        process = self._process_comment(comment)
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
                if user_ != self.request.user and user_ != comment.note.user:
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
                comment.modified = now()
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
                if user_ != self.request.user and user_ != new_reply.comment.user:
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
                if user_ != user and user_ != reply.comment.user:
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
        if Connection.objects.exist(request.user, add_this.user, status=True):
            note.collaborators.add(add_this)
            notes_signal.send(add_collaborator, note=note, user=add_this.user)
        else:
            raise PermissionDenied(f"@{add_this.user.username} cannot be a collaborator, they are not in your network")
    return redirect(reverse("notes:edit-collaborators",  args=[str(kwargs['note_id'])]))


# remove collaboration
@login_required
def rm_collaborator(request, **kwargs):
    note = get_object_or_404(Note, id=kwargs['note_id'])
    remove_this = get_object_or_404(Profile, user=kwargs['user_id'])

    if request.user != note.user:
        raise Http404
    else:
        note.collaborators.remove(remove_this)
        notes_signal.send(rm_collaborator, note=note, user=remove_this.user)

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
        note.collaborators.clear()
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
            response.update({
                'success': True,
                'message': 'Comment Deleted'
            })
        else:
            raise Http404
    else:
        response.update({
            'success': False,
            'message': "server couldn't complete your request"
        })
    return JsonResponse(response)


def retrieve(what: Type[Comment | Reply], what_: Literal['comment', 'reply'], what_id: int, user_: User, response):
    try:
        obj = what.objects.get(pk=what_id)
        if obj.user == user_:
            response['success'] = True
            if what_ == 'reply':
                response['text'] = obj.original_reply
            else:
                response['text'] = obj.original_comment
        else:
            response.update({
                'success': False,
                'message': f'the {what_} does not belong to you'
            })

    except ObjectDoesNotExist:
        response.update({
            'success': False,
            'message': f'The {what_} does not exits'
        })

    return response


@login_required
def get_comment_or_reply(request, **kwargs):
    response = {}
    what_item = kwargs.get('what', '')

    if what_item == "comment":
        result = retrieve(Comment, 'comment', kwargs['what_id'], request.user, response)

    elif what_item == "reply":
        result = retrieve(Reply, 'reply', kwargs['what_id'], request.user, response)

    else:
        raise Http404

    return JsonResponse(result)
