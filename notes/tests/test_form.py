from django.test import TestCase, tag
from django.urls import reverse

from notes.models import Note
from django.contrib.auth.models import User

class NoteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='test_form_note',
            password='test_form_pass'
        )
        self.client.force_login(self.user)

    @tag('notes_scripts')
    def test_note_scripts(self):
        print('notes scripts')
        url = reverse("notes:note-create")
        data = {
            'title': 'test note',
            'content': 'this is just a test <script></script>',
            'privacy': "PR"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_edit.html')
        self.assertContains(response, 'no scripts allowed!')
