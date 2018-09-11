from django.shortcuts import redirect, reverse
from django.views import generic
from django.urls import reverse_lazy

# models & forms (local imports)
from .models import Note
from .forms import NoteForm


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
class NotePage(generic.DetailView):
    template_name = 'notes/note.html'
    model = Note

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collaborators"] = context['note'].collaborators.all()
        return context


# note creation
class NoteCreate(generic.CreateView):
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
class NoteEdit(generic.UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['input_name'] = "edit note"
        return context


# note delete
class NoteDelete(generic.DeleteView):
    model = Note
    success_url = reverse_lazy("notes:index")
