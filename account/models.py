from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from itertools import chain

# create a ew profile every time a user is made
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    gender_options = (("M", "MALE"), ("F", "FEMALE"), ("NON", "PREFER NOT TO SAY"),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="profile.jpg", blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=3, choices=gender_options, blank=True, null=True)
    pen_name = models.CharField(max_length=200)
    objects = models.Manager()

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return "profile for {}".format(self.user)

    @staticmethod
    def get_absolute_url():
        return reverse("base_account:profile")


# connection model manager
class ConnectionManager(models.Manager):
    # check if a connection exists
    def main_conn(self, user1, user2):
        q_set_1 = (
                models.Q(conn_sender=user1) &
                models.Q(conn_receiver=user2.profile)
        )
        q_set_2 = (
                models.Q(conn_sender=user2) &
                models.Q(conn_receiver=user1.profile)
        )
        x = []
        connection_1 = Connection.objects.filter(q_set_1)
        connection_2 = Connection.objects.filter(q_set_2)
        connections = chain(connection_1, connection_2)
        for connection in connections:
            x.append(connection)

        return x

    def exist(self, user_1, user_2):
        """
        checks if a connection exists and returns true or false
        """
        result = False
        connections = self.main_conn(user1=user_1, user2=user_2)
        if len(connections) > 0:
            result = True
        return result

    # return a connection
    def get_conn(self, user_1, user_2):
        """
        return a connection from the parameters
        """
        result = None
        connections = self.main_conn(user1=user_1, user2=user_2)
        if len(connections) > 0:
            result = connections[0]

        return result


# connected users
class Connection(models.Model):
    conn_sender = models.ForeignKey(User, on_delete=models.CASCADE)
    conn_receiver = models.ForeignKey(Profile, blank=False, on_delete=models.CASCADE)
    since = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    objects = ConnectionManager()

    def get_status(self):
        if self.approved:
            status = "approved"
        else:
            status = "pending"
        return status

    def __str__(self):
        return "connection between {} and {}".format(self.conn_sender, self.conn_receiver)
