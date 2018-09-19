from django.test import TestCase, tag

from django.contrib.auth.models import User
from account.models import Profile, Connection


class AccountModelTest(TestCase):
    # test data
    def setUp(self):
        self.user_1 = User.objects.create(username="testing1", password="testing1")
        self.user_2 = User.objects.create(username="testing2", password="testing2")
        self.user_3 = User.objects.create(username="testing3", password="testing3")
        self.connection_1 = Connection.objects.create(conn_sender=self.user_1, conn_receiver=self.user_2.profile)
        self.connection_2 = Connection.objects.create(conn_sender=self.user_2, conn_receiver=self.user_3.profile)

    def test_profile_created(self):
        print("testing if a profile is made when a user is created...")
        test_profile = Profile.objects.get(user=self.user_1)
        print(test_profile)
        self.assertEqual(test_profile.user, self.user_1)

    # test the model manager for connection
    @tag('conn-exist')
    def test_connection_manager_exist(self):
        print("testing connection exist in ConnectionManager...")
        # exists
        state = Connection.objects.exist(self.user_1, self.user_2)
        self.assertEqual(state, True)
        state_2 = Connection.objects.exist(self.user_3, self.user_2)
        self.assertEqual(state_2, True)

        # does not exist
        state_3 = Connection.objects.exist(self.user_3, self.user_1)
        self.assertEqual(state_3, False)

    # returns the connection
    @tag('get-connection')
    def test_connection_manager_get_conn(self):
        print("testing get connection in ConnectionManger...")
        connection = Connection.objects.get_conn(self.user_1, self.user_2)
        self.assertEqual(connection, self.connection_1)

        connection_2 = Connection.objects.get_conn(self.user_3, self.user_2)
        self.assertEqual(connection_2, self.connection_2)

        connection_3 = Connection.objects.get_conn(self.user_1, self.user_3)
        self.assertEqual(connection_3, None)

    # test get_user_conn
    @tag('get_user_conn')
    def test_get_user_conn(self):
        print("testing get_user_conn")
        conns = Connection.objects.get_user_conn(self.user_2)
        self.assertEqual(conns, [])

        self.connection_1.approved = True
        self.connection_1.save()
        conns = Connection.objects.get_user_conn(self.user_2)
        self.assertEqual(conns, [self.user_1])

        self.connection_2.approved = True
        self.connection_2.save()
        conns = Connection.objects.get_user_conn(self.user_2)
        self.assertEqual(conns, [self.user_3, self.user_1])
