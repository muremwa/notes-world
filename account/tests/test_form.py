from django.test import TestCase, tag
from django.urls import reverse

class AccountFormTestCase(TestCase):
    @tag('username_@')
    def test_username(self):
        print("testing @ on username")
        url = reverse("base_account:sign-up")
        data_ = {
            'username': "2424@24",
            'first_name': "anne",
            'last_name': "test",
            'password1': 'tester@form1',
            'password2': 'tester@form1'
        }
        response = self.client.post(url, data_)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertContains(response, 'no @ signs on username')
