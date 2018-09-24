from django import forms
from .models import Note, Comment
from pagedown.widgets import PagedownWidget


# note creation or edit form
class NoteForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget)
    class Meta:
        model = Note
        fields = ("title", 'content', 'privacy')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment_text',)
