from django.test import TestCase, tag
from django.urls import reverse

from django.contrib.auth.models import User
from notes.models import Note
from account.models import Connection


class NoteTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="testing", password="testing")
        self.user_2 = User.objects.create(username="testing1", password="testing1")
        self.user_3 = User.objects.create(username="testing3", password="testing3")
        self.note = Note.objects.create(
            user=self.user_1,
            title="test_note1",
            content="test_content1",
            collaborative=True,
            privacy="CO"
        )
        self.note_2 = Note.objects.create(
            user=self.user_2,
            title="test_note2",
            content="test_content2",
            collaborative=True,
            privacy="CO"
        )
        self.note_3 = Note.objects.create(
            user=self.user_3,
            title="test_note3",
            content="test_content3",
            collaborative=True,
            privacy="CO"
        )
        self.note.collaborators.add(self.user_2.profile, self.user_3.profile)
        self.note_2.collaborators.add(self.user_3.profile, self.user_1.profile)
        self.note_3.collaborators.add(self.user_1.profile, self.user_2.profile)

    @tag('note-manager')
    def test_note_manager(self):
        print("testing note manager")
        self.connection_1 = Connection.objects.create(
            conn_sender=self.user_1,
            conn_receiver=self.user_2.profile,
            approved=True
        )
        self.connection_1 = Connection.objects.create(
            conn_sender=self.user_2,
            conn_receiver=self.user_3.profile,
            approved=True
        )
        self.connection_1 = Connection.objects.create(
            conn_sender=self.user_1,
            conn_receiver=self.user_3.profile,
            approved=True
        )

        self.user_4 = User.objects.create(username="testing4", password="testing4")
        collaborators = Note.objects.collaborations(self.user_1)
        print(collaborators)
        self.assertEqual(len(collaborators), 2)
        collaborators = Note.objects.collaborations(self.user_2)
        self.assertEqual(len(collaborators), 2)
        collaborators = Note.objects.collaborations(self.user_3)
        self.assertEqual(len(collaborators), 2)
        collaborators = Note.objects.collaborations(self.user_4)
        self.assertEqual(len(collaborators), 0)
