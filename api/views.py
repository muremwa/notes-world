from rest_framework import viewsets, permissions

from notes.models import Note
from .serializers import NoteSerializer


class NoteApi(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAdminUser,)
