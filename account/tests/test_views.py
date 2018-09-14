from django.test import TestCase
from django.test import tag
from django.shortcuts import reverse, get_object_or_404
from django.db.models import Q
from django.http import Http404

from django.contrib.auth.models import User
from account.models import Profile, Connection


@tag('for_views')
class ViewsTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(
            username="testview",
            password="testview"
        )
        self.user_2 = User.objects.create(
            username="testview2",
            password="testview2"
        )
        self.user_3 = User.objects.create(
            username="testview3",
            password="testview3"
        )
        self.connection_1 = Connection.objects.create(
            conn_sender=self.user_2,
            conn_receiver=self.user_3.profile
        )
        self.client.force_login(self.user_1)
        self.profile = Profile.objects.get(user=self.user_1)

    # views return 200
    @tag('account_200')
    def test_views_200(self):
        print("testing views with no arguments")
        paths = [
            ["account-index", 'account/index.html'],
            ["profile", 'account/profile.html'],
            ["sign-up", 'account/signup.html'],
            ["connected", 'account/connect.html']
        ]
        for path, template in paths:
            url = reverse("base_account:"+path)
            print("testing "+url)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)

    # sign-up post request
    @tag('sign_up')
    def test_sign_up_post(self):
        user_data = {
            "username": "test1",
            "first_name": "test 1",
            "last_name": "test last",
            "email": "test@mail.com",
            "password": "newworldp@s",
            "password_confirmation": "newworldp@s",
        }
        url = reverse("base_account:sign-up")
        response_post = self.client.post(url, data=user_data)
        self.assertEqual(response_post.status_code, 200)
        self.assertContains(response_post, "test1")

    # test the profile edit
    @tag('prof-edit')
    def test_profile_edit(self):
        print("testing the profile edit...")
        url = reverse("base_account:profile-edit", args=[str(self.profile.id)])
        invalid_url = reverse("base_account:profile-edit", args=[str(100)])
        response_get = self.client.get(url)
        response_get_invalid = self.client.get(invalid_url)
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(response_get_invalid.status_code, 404)
        form_data = {
            "pen_name": "test pen",
            "occupation": "nurse",
        }
        response_post = self.client.post(url, data=form_data)
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(response_post.url, reverse("base_account:profile"))

    # test the ajax user requests
    print("testing the ajax user requests")

    @tag('connect')
    def test_requests_connect(self):
        print("connect...")
        url = reverse("base_account:connect", args=[str(self.user_2.id)])
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 404)
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 200)
        qset = (
                Q(conn_sender=self.user_1) &
                Q(conn_receiver=self.user_2.profile)
        )
        connection = Connection.objects.filter(qset)[0]
        self.assertEqual(response_post.json()['sent'], True)
        self.assertEqual(connection.conn_sender, self.user_1)
        self.assertEqual(connection.conn_receiver, self.user_2.profile)
        self.assertEqual(connection.approved, False)
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 200)
        self.assertEqual(response_post.json()['sent'], False)

    @tag('accept')
    def test_requests_accept(self):
        print("accept...")
        url = reverse("base_account:accept", args=[str(self.connection_1.id)])
        response_get_accept = self.client.get(url)
        self.assertEqual(response_get_accept.status_code, 404)
        response_post_accept = self.client.post(url)
        self.assertEqual(response_post_accept.status_code, 200)
        self.assertEqual(response_post_accept.json()['accepted'], True)
        connection = Connection.objects.get(pk=self.connection_1.id)
        self.assertEqual(connection.approved, True)

        # id does not exist
        response_post_accept = self.client.post(url)
        self.assertEqual(response_post_accept.status_code, 200)
        self.assertEqual(response_post_accept.json()['accepted'], False)

    @tag('disconnect')
    def test_requests_disconnect(self):
        print("disconnect...")
        self.client.force_login(self.user_2)
        self.connection_1.approved = True
        self.connection_1.save()
        url = reverse("base_account:exit", args=[str(self.user_3.id)])
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 404)
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 200)
        try:
            connection = get_object_or_404(Connection, pk=self.connection_1.id)
        except Http404:
            connection = 404
        self.assertEqual(connection, 404)
        self.assertEqual(response_post.json()['exited'], True)

        # if does not exist
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 200)
        self.assertEqual(response_post.json()['exited'], False)
        self.assertEqual(response_post.json()['state'], "connection no longer exists")

    @tag('deny')
    def test_request_deny(self):
        print("deny...")
        # if approved
        self.client.force_login(self.user_3)
        self.connection_1.approved = True
        self.connection_1.save()
        url = reverse("base_account:deny", args=[str(self.connection_1.id)])
        response_post_true = self.client.post(url)
        self.assertEqual(response_post_true.status_code, 200)
        self.assertEqual(response_post_true.json()['denied'], False)
        self.assertEqual(response_post_true.json()['state'], "you cannot deny an approved request")
        self.connection_1.approved = False
        self.connection_1.save()

        # if not approved
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 404)
        response_post = self.client.post(url)
        try:
            connection = get_object_or_404(Connection, pk=self.connection_1.id)
        except Http404:
            connection = False
        self.assertEqual(connection, False)
        self.assertEqual(response_post.json()['denied'], True)

        # if does not exist
        response_post = self.client.post(url)
        self.assertEqual(response_post.status_code, 404)
