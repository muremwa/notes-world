from django.test import TestCase
from django.contrib.auth.models import User

from .serializers import ApiCommentSerializer
from notes.models import Note, Comment


class ApiTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create(username="testing", password="testing")
        self.user_2 = User.objects.create(username="testing1", password="testing")
        self.note = Note.objects.create(
            user=self.user_1,
            title="test_note1",
            content="test_content1",
            collaborative=True,
            privacy="CO"
        )
        self.comment = Comment.objects.create(
            user=self.user_1,
            note=self.note,
            original_comment="this is just a test comment @test1 don't be surprised @muremwa",
            comment_text="this is just a test comment @test1 don't be surprised @muremwa",
        )
        self.comment.mentioned.add(self.user_2.profile)

    def test_comment_serializer(self):
        data = ApiCommentSerializer(self.comment).data
        self.assertEqual(data.get('text'), self.comment.comment_text)
