from django.test import TestCase

from django.contrib.auth.models import User
from account.models import Profile


class AccountModelTest(TestCase):
    # test data
    def setUp(self):
        self.user_1 = User.objects.create(
            username="testing1",
            password="testing1"
        )

    def test_profile_created(self):
        try:
            test_profile = Profile.objects.get(user=self.user_1)
            print(test_profile)
        except:
            test_profile = None
            print(test_profile)
        self.assertEqual(test_profile.user, self.user_1)
