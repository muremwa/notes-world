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
            content="test_content",
            collaborative=True
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

    # test collaboration removal and add page
    @tag('edit-collaboration')
    def test_collaboration_form_page(self):
        print("testing collaboration form page")
        self.user_3 = User.objects.create(username="testing3", password="testing3")
        self.note.collaborators.add(self.user_2.profile)
        self.note.collaborators.add(self.user_3.profile)
        self.client.force_login(self.user_1)
        url = reverse("notes:edit-collaborators", args=[str(self.note.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/collaborators.html')
        c = self.note.collaborators.all()
        for i in range(len(c)):
            self.assertEqual(response.context['collaborators'][i], c[i])

    # add collaborator
    @tag('add-collaboration')
    def test_add_collaborator(self):
        print("testing add collaboration")
        url = reverse("notes:add-collaborator", kwargs={'note_id': str(self.note.id), 'user_id': str(self.user_2.id)})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("notes:edit-collaborators", args=[str(self.note.id)]))
        collaborator = None
        for coll_ in self.note.collaborators.all():
            if coll_ == self.user_2.profile:
                collaborator = coll_.user
        self.assertEqual(collaborator.id, self.user_2.id)

        url = reverse("notes:add-collaborator", kwargs={'note_id': 200, 'user_id': str(self.user_2.id)})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

        url = reverse("notes:add-collaborator", kwargs={'note_id': str(self.note.id), 'user_id': 1000})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    # remove collaborator
    @tag('remove-collaboration')
    def test_remove_collaborator(self):
        print("testing remove collaboration")
        self.user_3 = User.objects.create(username="testing3", password="testing3")
        self.note.collaborators.add(self.user_3.profile)
        self.note.save()
        count = self.note.collaborators.all().count()
        url = reverse("notes:remove-collaborator",
                      kwargs={'note_id': str(self.note.id), 'user_id': str(self.user_3.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("notes:edit-collaborators", args=[str(self.note.id)]))
        self.assertEqual(self.note.collaborators.all().count(), (count-1))

        url = reverse("notes:remove-collaborator", kwargs={'note_id': str(self.note.id), 'user_id': 1000})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = reverse("notes:remove-collaborator", kwargs={'note_id': 1000, 'user_id': str(self.user_3.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # make collaborative
    @tag('make-collaborative')
    def test_make_collaborative(self):
        self.note_1 = Note.objects.create(user=self.user_1, title="test_note", content="test_content")
        print("testing making collaborative")
        url = reverse("notes:make-collaborative", args=[str(100)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = reverse("notes:make-collaborative", args=[str(self.note_1.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("notes:edit-collaborators", args=[str(self.note_1.id)]))
        note = Note.objects.get(id=self.note_1.id)
        self.assertEqual(note.collaborative, True)
        self.assertEqual(note.privacy, "CO")

        self.note_1.collaborative = False
        self.note_1.privacy = "PB"
        self.note_1.save()
        url = reverse("notes:make-collaborative", args=[str(self.note_1.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("notes:edit-collaborators", args=[str(self.note_1.id)]))
        note = Note.objects.get(id=self.note_1.id)
        self.assertEqual(note.collaborative, True)
        self.assertEqual(note.privacy, "PB")
