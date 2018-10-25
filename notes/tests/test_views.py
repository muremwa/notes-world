from django.test import TestCase, tag
from django.shortcuts import reverse, NoReverseMatch

from django.contrib.auth.models import User
from notes.models import Note, Comment
from account.models import Connection

# TODO:: add the tests for edit comment, reply, reply edit, delete reply or comment


class TestViews(TestCase):
    # set up
    def setUp(self):
        self.user_1 = User.objects.create(username="testing", password="testing")
        self.user_2 = User.objects.create(username="testing1", password="testing1")
        self.connection = Connection.objects.create(conn_sender=self.user_2, conn_receiver=self.user_1.profile,
                                                    approved=True)
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

    # testing remove collaboration
    @tag('remove-collaborative')
    def test_remove_collaboration(self):
        print("testing remove collaboration")
        self.client.force_login(self.user_1)

        url = reverse("notes:undo-collaborative", args=[str(1000)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self.note.collaborators.add(self.user_2.profile)
        self.note.save()
        url = reverse("notes:undo-collaborative", args=[str(self.note.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("notes:note-page", args=[str(self.note.id)]))
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.collaborators.all().count(), 0)
        self.assertEqual(note.collaborative, False)

        self.client.force_login(self.user_2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


@tag("commenting")
class CommentsTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="testing", password="testing")
        self.user_2 = User.objects.create(username="testing1", password="testing")
        self.user_3 = User.objects.create(username="testing2", password="testing")
        self.note = Note.objects.create(
            user=self.user_1,
            title="test_note",
            content="test_content",
            collaborative=True
        )
        self.comment = Comment.objects.create(
            user=self.user_1,
            note=self.note,
            comment_text="this is just a test comment @test1 don't be surprised @muremwa",
        )
        self.comment.mentioned.add(self.user_2.profile)

    # testing comment submission
    @tag("submit-comment")
    def test_comment_submit(self):
        print("testing comment submit")
        self.client.force_login(self.user_1)
        url = reverse("notes:comment", args=[str(self.note.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(url, data={"comment": "hello world"})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(url, data={"comment": "hello world 2"}, follow=True)
        redirects_to = reverse("notes:note-page", args=[str(self.note.id)]) + "#comments"
        self.assertRedirects(response, redirects_to)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['comment_count'], 3)
        comment = Comment.objects.filter(comment_text__contains="hello world 2")[0]
        self.assertEqual(comment.comment_text, "<p>hello world 2</p>\n")
        self.assertEqual(comment.original_comment, "hello world 2")
        self.assertEqual(comment.user, self.user_1)

    # tagged users
    @tag("comment-mentioned")
    def test_mentioned(self):
        connect_1 = "http://127.0.0.1:8000"+reverse("base_account:foreign-user", args=[str(self.user_1.id)])
        connect_2 = "http://127.0.0.1:8000" + reverse("base_account:foreign-user", args=[str(self.user_2.id)])
        self.client.force_login(self.user_1)
        print("testing mentioned")
        url = reverse("notes:comment", args=[str(self.note.id)])
        data_ = {
            "comment": "this is just a test comment @testing1 don't be surprised @testing"
        }
        end_result = "<p>this is just a test comment <a href=\"{}\">@testing1</a>" \
                     " don't be surprised <a href=\"{}\">@testing</a></p>\n".format(connect_2, connect_1)
        response = self.client.post(url, data=data_)
        comments = self.note.comment_set.all()
        comment = comments[0].comment_text
        self.assertEqual(response.status_code, 302)
        self.assertEqual(comment, end_result)
        self.assertEqual(comments[0].mentioned.all().count(), 1)

    @tag("comment-edit")
    def test_comment_edit(self):
        user_3 = "http://127.0.0.1:8000"+reverse('base_account:foreign-user', args=[str(self.user_3.id)])
        user_2 = "http://127.0.0.1:8000"+reverse('base_account:foreign-user', args=[str(self.user_2.id)])
        init_count = self.comment.mentioned.all().count()
        print("comment edit")
        data = {
            'comment': 'this is the new comment @testing2 @testing1'
        }
        url = reverse('notes:edit-comment', args=[str(self.comment.id)])
        expected_comment = "<p>this is the new comment <a href=\"{}\">@testing2</a> <a href=\"{}\"" \
                           ">@testing1</a></p>".format(user_3, user_2)
        # get logged in
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

        # post logged out redirect
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login')+"?next="+url)

        # post logged in wrong user
        self.client.force_login(self.user_2)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

        # post logged in right user
        self.client.force_login(self.user_1)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(pk=self.comment.id)
        self.assertRedirects(response, reverse('notes:note-page', args=[str(comment.id)])+"#comment"+str(comment.id))
        self.assertEqual(comment.original_comment, data['comment'])
        self.assertEqual(comment.comment_text, expected_comment+"\n")
        self.assertEqual(comment.mentioned.count(), init_count+1)
