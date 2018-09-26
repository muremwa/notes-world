# django imports
from django.shortcuts import redirect, reverse,  get_object_or_404
from django.views import generic, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist

# other imports
from itertools import chain
from markdown_deux import markdown
import re

# models & forms (local imports)
from .models import Note, Comment
from .forms import NoteForm, CommentForm
from account.models import Connection, Profile
from django.contrib.auth.models import User


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
        context = super().get_context_data(**kwargs)
        context["collaborators"] = context['note'].collaborators.all()
        context['form'] = CommentForm
        context['input_name'] = "comment"
        context['comments'] = context['note'].comment_set.all()
        context['comment_count'] = context['comments'].count()
        context['action_url'] = reverse("notes:comment", args=[str(context['note'].id)])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['input_name'] = "edit note"
        context['collaborators'] = context['note'].collaborators.all()
        print("here")
        print(context['collaborators'])
        return context

    def form_valid(self, form):
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
        return context


class CommentProcessing(View):
    # raise 404 error if its a get request
    def get(self, *args, **kwargs):
        raise Http404

    def user_linking(self, user, split, url, addition, **kwargs):
        line = '[{}](http://127.0.0.1:8000{})'
        new_user = user
        if addition:
            new_user = user + kwargs['add']
            line = '[{}](http://127.0.0.1:8000{}){}'
        user_index = split.index(new_user)
        if addition:
            new_line = line.format(user, url, kwargs['add'])
        else:
            new_line = line.format(user, url)
        split[user_index] = new_line
        return split

    # process comment
    def process_comment(self, comment_text):
        users = re.findall(r'@\w*', comment_text, re.I | re.M)
        split_comment = comment_text.split(" ")
        connect_url = reverse("base_account:connected")
        new_users = []

        for user in users:
            try:
                name = user.split("@")[-1]
                User.objects.get(username__exact=name)
                new_users.append(user)
            except ObjectDoesNotExist:
                continue
        
        for user_ in new_users:
            try:
                split_comment = self.user_linking(user_, split_comment, connect_url, False)
            except ValueError:
                try:
                    split_comment = self.user_linking(user_, split_comment, connect_url, True, add=",")
                except ValueError:
                    try:
                        split_comment = self.user_linking(user_, split_comment, connect_url, True, add=".")
                    except ValueError:
                        try:
                            split_comment = self.user_linking(user_, split_comment, connect_url, True, add="?")
                        except ValueError:
                            continue

        result = " ".join(split_comment)
        return result

    # make it html
    def mark(self, comment):
        processed_comment = self.process_comment(comment)
        result = markdown(processed_comment)
        return result

    # process comment
    def post(self, *args, **kwargs):
        form = CommentForm(self.request.POST)
        if form.is_valid():
            text = self.mark(form.cleaned_data['comment'])
            Comment.objects.create(
                user_id=self.request.user.id,
                note_id=kwargs['note_id'],
                comment_text=text
            )
        url = reverse("notes:note-page", args=[str(kwargs['note_id'])]) + "#comments"
        return redirect(url)


# add collaborator
@login_required
def add_collaborator(request, **kwargs):
    note = get_object_or_404(Note, id=kwargs['note_id'])
    add_this = get_object_or_404(Profile, user=kwargs['user_id'])

    if request.user != note.user:
        raise Http404
    else:
        note.collaborators.add(add_this)
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
