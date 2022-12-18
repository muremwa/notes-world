from datetime import datetime
from itertools import chain

from django.shortcuts import get_object_or_404, redirect, reverse, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import views, generics
from rest_framework import status
from django.http import Http404

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


class AllComments(views.APIView, CommentProcessor):
    @staticmethod
    def shape(comment, user_id, host):
        if comment.modified:
            stamp = comment.modified.timestamp()
        else:
            stamp = comment.created.timestamp()

        return {
            'key': stamp + comment.pk,
            'username': comment.user.username,
            'full_name': comment.user.get_full_name(),
            'profile': comment.user.profile.image.url,
            'comment_id': comment.pk,
            'time': comment.get_created(),
            'text': comment.original_comment,
            'edited': comment.is_modified(),
            'editable': comment.user.pk == user_id,
            'replies': comment.reply_set.count(),
            'reply_url': "http://" + host + reverse('notes:reply-comment', kwargs={'comment_id': str(comment.pk)}),
            'action_url': "http://" + host + reverse('api:comment-actions', kwargs={'pk': str(comment.pk)}),
        }

    def get(self, *args, **kwargs):
        host = self.request.META.get('HTTP_HOST', '')
        comments = Comment.objects.filter(note=kwargs.get('pk'))
        note = get_object_or_404(Note, pk=kwargs.get('pk'))

        user = self.request.user

        return Response({
            'note': str(note),
            'owner_id': note.user.pk,
            'user': {
                'id': user.pk,
                'username': user.username,
                'full_name': user.get_full_name(),
                'profile': user.profile.image.url,
            },
            'comments': [self.shape(comment, user.pk, host) for comment in comments]
        })

    def post(self, *args, **kwargs):
        host = self.request.META.get('HTTP_HOST', '')
        note = get_object_or_404(Note, pk=kwargs.get('pk', None))
        user_comment = self.request.data.get('comment', '')
        processed_data = self.mark(user_comment)
        user = self.request.user

        comment = Comment(
            note=note,
            user=user,
            comment_text=processed_data.get('processed_comment', ''),
            original_comment=user_comment,
        )
        comment.save()

        for mentioned_user in processed_data.get('mentioned'):
            comment.mentioned.add(mentioned_user.profile)

        notes_signal.send(self.__class__, comment=comment, mentioned=processed_data.get('mentioned'))

        return Response({
            'comment': self.shape(comment, user.pk, host)
        })


@api_view(['POST'])
def comment_actions(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    response = Response(status=status.HTTP_403_FORBIDDEN)

    if 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
        http_method = request.META['HTTP_X_HTTP_METHOD_OVERRIDE']

        # handle a delete request
        if http_method == "DELETE":
            if request.user == comment.user or request.user == comment.note.user:
                comment.delete()
                response = Response({'success': True}, status=status.HTTP_200_OK)
            else:
                response = Response(status=status.HTTP_403_FORBIDDEN)

        # handle a patch request
        elif http_method == 'PATCH':
            if comment.user == request.user:
                processor = CommentProcessor()
                comment_text = request.data.get('original_comment', '')
                processed_comment = processor.mark(comment_text)
                comment.comment_text = processed_comment.get('processed_comment')
                comment.original_comment = comment_text
                comment.modified = datetime.now()
                comment.save()
                notify = []

                # add mentioned users
                for mentioned in processed_comment.get('mentioned'):
                    if mentioned.profile not in comment.mentioned.all():
                        comment.mentioned.add(mentioned.profile)
                        notify.append(mentioned)

                # notify new mentioned users
                if notify:
                    notes_signal.send(comment_actions, comment=comment, mentioned=notify)

                response = Response({
                    'new_key': comment.modified.timestamp() + comment.pk,
                    'success': True,
                    'changed': True,
                    'comment_id': comment.pk,
                    'comment': comment_text,
                    'replies': comment.reply_set.count(),
                    'error_message': None,
                })
            else:
                response = Response(status=status.HTTP_403_FORBIDDEN)

    return response


def get_user(request):
    username_query = request.GET.get('username', None)
    ava_users = User.objects.filter(username__iexact=username_query)

    if ava_users.count() < 1:
        return render(request, 'notes/user_not_found.html', {'failed_user': username_query})

    return redirect(reverse('base_account:foreign-user', kwargs={'user_id': str(ava_users[0].pk)}))


class AllCommentsV2(views.APIView, CommentProcessor):

    def get(self, *args, **kwargs):
        note = Note.objects.get(pk=kwargs.get('note_pk'))
        return Response({
            'current_user': ApiUserSerializer(self.request.user).data,
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
            for mentioned_user in processed_comment.get('mentioned'):
                comment.mentioned.add(mentioned_user.profile)

            # notify mentioned
            notes_signal.send(self.__class__, comment=comment, mentioned=processed_comment.get('mentioned'))

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
