from django.shortcuts import redirect, reverse,  get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.contrib.auth.decorators import login_required

# models & forms (local imports)
from .models import Note
from .forms import NoteForm
from account.models import Connection, Profile


# all user notes
class NoteIndex(generic.ListView):
    template_name = 'notes/index.html'
    context_object_name = "notes"

    def get_queryset(self):
        return self.request.user.note_set.all()

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(reverse('base_account:account-index'))
        else:
            return super().get(request, *args, **kwargs)


# each note page
class NotePage(LoginRequiredMixin, generic.DetailView):
    template_name = 'notes/note.html'
    model = Note

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collaborators"] = context['note'].collaborators.all()
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
def remove_collaborator(request, **kwargs):
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
