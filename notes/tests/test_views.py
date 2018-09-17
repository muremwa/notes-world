from django.test import TestCase, tag
from django.shortcuts import reverse, NoReverseMatch

from django.contrib.auth.models import User
from notes.models import Note


class TestViews(TestCase):
    # set up
    def setUp(self):
        self.user_1 = User.objects.create(username="testing", password="testing")
        self.user_2 = User.objects.create(username="testing1", password="testing1")
        self.client.force_login(self.user_1)
        self.note = Note.objects.create(
            user=self.user_1,
            title="test_note",
            content="test_content"
        )

    @tag('notes200')
    def test_views_200(self):
        paths = ['index', 'note-page']
        for path in paths:
            try:
                url = reverse("notes:"+path)
            except NoReverseMatch:
                url = reverse("notes:"+path, args=[str(self.note.id)])
            print(url)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @tag('note-page')
    def test_note_page(self):
        print("testing note pages")
        paths = [
            [reverse("notes:note-page", args=[str(self.note.id)]), 200],
            [reverse("notes:note-page", args=[str(100)]), 404]
        ]

        for path, code in paths:
            print(path+" = "+str(code))
            response = self.client.get(path)
            self.assertEqual(response.status_code, code)

    @tag('note-create')
    def test_note_creation(self):
        print("testing note creation")
        url = reverse("notes:note-create")
        valid_data = {
            "user": self.user_2,
            "title": "test title",
            "content": "test content",
        }        

        valid_response = self.client.post(url, data=valid_data)
        self.assertEqual(valid_response.status_code, 200)
        self.assertTemplateUsed(valid_response, 'notes/note_edit.html')

    # test collaborate page
    @tag('collaborate_page')
    def test_collaborate(self):
        print('testing collaborate page')
        self.note.collaborators.add(self.user_2.profile)
        self.client.force_login(user=self.user_2)
        url = reverse('notes:collaborate_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/collaboration-page.html')
        self.assertEqual(response.context['collaborations'], Note.objects.collaborations(self.user_2))
        self.assertEqual(response.context['collaborations'][0], self.note)
