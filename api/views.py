from rest_framework import views, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404

from .serializers import NotesSerializer, NoteSerializer, UserSerializer, NoteCreationSerializer, CommentSerializer
from notes.models import Note, Comment
from django.contrib.auth.models import User

from itertools import chain


class NotesApi(views.APIView):
    @staticmethod
    def get(request):
        user_notes = request.user.note_set.all()
        shared_notes = Note.objects.notes_user_can_see(request.user)
        public_notes = Note.objects.filter(privacy="PB")
        notes = chain(user_notes, shared_notes, public_notes)
        data = NotesSerializer(notes, many=True).data
        return Response(data)


class NoteAPi(views.APIView):
    @staticmethod
    def get(request, note_id):
        note = get_object_or_404(Note, pk=note_id)
        data = NoteSerializer(note).data
        if note.user != request.user:
            if request.user not in Note.objects.notes_user_can_see(request.user):
                if note.privacy != "PB":
                    raise Http404
        return Response(data)


class UserCreateApi(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class NoteCreationApi(views.APIView):
    def get(self, *args, **kwargs):
        raise Http404

    @staticmethod
    def post(request):
        title = request.data['title']
        content = request.data['content']
        privacy = request.data['privacy']
        user = request.user
        note = Note.objects.create(
            user=user,
            title=title,
            content=content,
            privacy=privacy
        )
        note.save()
        return Response({
            "title": title,
            "privacy": privacy,
            "user": user.username
        })


# comments
class AllComments(views.APIView):
    def shape(self, comment):
        return {
            'username': comment.user.username,
            'full_name': comment.user.get_full_name(),
            'profile': comment.user.profile.image.url,
            'time': comment.get_created(),
            'text': comment.original_comment,
            'edited': comment.is_modified(),
            'replies': comment.reply_set.all().count(),
        }
        

    def get(self, *args, **kwargs):
        comments = Comment.objects.filter(note=kwargs['pk'])
        data = []
        for comment in comments:
            data.append(self.shape(comment))

        return Response(data)
