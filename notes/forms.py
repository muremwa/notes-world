import re

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Note, Tag
from .widgets import NotesWorldMarkdownEditor


# note creation or edit form
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("title", 'content', 'privacy')
        widgets = {
            'title': forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "enter a descriptive title for your note"
            }),
            'privacy': forms.Select(attrs={"class": "form-select"}),
            'content': NotesWorldMarkdownEditor()
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        if re.search(r'</script>', data, re.I | re.M):
            raise ValidationError(_("no scripts allowed!"), code="scripts")

        return data


class NoteForeignForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('content',)
        widgets = {
            'content': NotesWorldMarkdownEditor()
        }


class CommentForm(forms.Form):
    comment = forms.CharField(max_length=140, widget=forms.Textarea(attrs={
        "class": "form-control",
        "placeholder": "add comment here (use '@username' to mention someone)"
    }))


class TagsField(forms.ModelMultipleChoiceField):
    widget = forms.SelectMultiple(attrs={
        "class": "form-control",
        "id": "tags-select"
    })

    def label_from_instance(self, obj):
        return f'{obj.name}'


class TagForm(forms.ModelForm):
    tags = TagsField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Note
        fields = ('tags',)
