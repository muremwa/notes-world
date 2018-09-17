from rest_framework import serializers
from notes.models import Note


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Note
        fields = ('url', 'id', 'title', 'content', 'created', 'last_modified',)
