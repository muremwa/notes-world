from itertools import chain
from typing import Dict

from django.shortcuts import get_object_or_404, redirect, reverse, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import views, generics
from rest_framework import status
from django.http import Http404
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .serializers import NotesSerializer, NoteSerializer, UserSerializer, ApiUserSerializer, ApiNoteSerializer, \
    ApiCommentSerializer
from notes.views import CommentProcessor, notes_signal
from notes.models import Note, Comment


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


def get_user(request):
    username_query = request.GET.get('username', None)
    ava_users = User.objects.filter(username__iexact=username_query)

    if ava_users.count() < 1:
        return render(request, 'notes/user_not_found.html', {'failed_user': username_query})

    return redirect(reverse('base_account:foreign-user', kwargs={'user_id': str(ava_users[0].pk)}))


class AllCommentsV2(views.APIView, CommentProcessor):

    def process_token(self, serial_data: Dict) -> Dict:
        """
        This checks whether there is a token on the user; if not a new one is created
        """
        if serial_data.get('token') is None:
            new_token = Token.objects.create(user_id=self.request.user.pk)
            serial_data.update({
                'token': new_token.key
            })
        return serial_data

    def get(self, *args, **kwargs):
        note = Note.objects.get(pk=kwargs.get('note_pk'))
        return Response({
            'current_user': self.process_token(ApiUserSerializer(self.request.user, token=True).data),
            'notes_info': ApiNoteSerializer(note).data
        })

    def post(self, *args, **kwargs):
        response = {'success': False}
        res_status = status.HTTP_400_BAD_REQUEST
        note = get_object_or_404(Note, pk=kwargs.get('note_pk'))
        posted_comment = self.request.data.get('comment')

        if posted_comment:
            processed_comment = self.mark(posted_comment)
            comment = Comment.objects.create(
                note=note,
                user=self.request.user,
                comment_text=processed_comment.get('processed_comment'),
                original_comment=posted_comment
            )

            # add mentioned
            notify = []
            for mentioned_user in processed_comment.get('mentioned'):
                comment.mentioned.add(mentioned_user.profile)

                if mentioned_user != self.request.user and mentioned_user != comment.note.user:
                    notify.append(mentioned_user)

            # notify mentioned
            notes_signal.send(self.__class__, comment=comment, mentioned=notify)

            res_status = status.HTTP_201_CREATED
            response.update({
                'success': True,
                'comment': ApiCommentSerializer(comment).data
            })

        else:
            response.update({
                'success': False,
                'message': 'Missing data \'comment\''
            })

        return Response(response, status=res_status)


@api_view(['DELETE', 'PATCH'])
def comment_actions_v2(request, comment_pk):
    response = {'success': False}
    res_status = status.HTTP_403_FORBIDDEN
    comment = get_object_or_404(Comment, pk=comment_pk)

    # update a comment
    if request.method == 'PATCH':
        if request.user == comment.user:
            posted_comment = request.data.get('comment')

            if posted_comment:
                processor = CommentProcessor()
                processed_comment = processor.mark(posted_comment)
                comment.original_comment = posted_comment
                comment.comment_text = processed_comment.get('processed_comment')
                comment.modified = timezone.now()
                comment.save()
                notify = []

                # add mentioned users
                for mentioned in processed_comment.get('mentioned'):
                    if mentioned.profile not in comment.mentioned.all():
                        comment.mentioned.add(mentioned.profile)

                        if mentioned != comment.note.user:
                            notify.append(mentioned)

                # notify new mentioned users
                if notify:
                    notes_signal.send(comment_actions_v2, comment=comment, mentioned=notify)

                res_status = status.HTTP_200_OK
                response.update({
                    'success': True,
                    'comment': ApiCommentSerializer(comment).data
                })

            else:
                res_status = status.HTTP_400_BAD_REQUEST
                response.update({
                    'success': False,
                    'message': 'Missing data \'comment\'.'
                })

    # delete a comment
    elif request.method == 'DELETE':
        if request.user == comment.user or request.user == comment.note.user:
            comment.delete()
            res_status = status.HTTP_200_OK
            response.update({'success': True, 'comment_id': comment_pk})

    return Response(response, status=res_status)
