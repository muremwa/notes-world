from itertools import chain

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.core.validators import ValidationError


# create a ew profile every time a user is made
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    gender_options = (("M", "MALE"), ("F", "FEMALE"), ("NON", "PREFER NOT TO SAY"),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="profile.jpg", upload_to="profile_images/")
    occupation = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=3, choices=gender_options, blank=True, null=True)
    pen_name = models.CharField(max_length=200)
    objects = models.Manager()

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @staticmethod
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return "profile for {}".format(self.user)

    def get_absolute_url(self):
        return reverse("base_account:foreign-user", kwargs={"user_id": str(self.user.pk)})


# connection model manager
class ConnectionManager(models.Manager):
    @staticmethod
    def main_conn(user1, user2):
        """Fetches the Connection between user1 and user2 """
        q_set_1 = (
                models.Q(conn_sender=user1) &
                models.Q(conn_receiver=user2.profile)
        )
        q_set_2 = (
                models.Q(conn_sender=user2) &
                models.Q(conn_receiver=user1.profile)
        )
        return list(
            chain(Connection.objects.filter(q_set_1), Connection.objects.filter(q_set_2))
        )

    def exist(self, user_1, user_2, **kwargs):
        """
        checks if a connection exists and returns true or false
        """
        status = kwargs.get('status', False)
        result = False
        connections = self.main_conn(user1=user_1, user2=user_2)
        if len(connections) > 0:
            result = True

            if status and not connections[0].approved:
                result = False

        return result

    def get_conn(self, user_1, user_2):
        """return a connection from the parameters between user_1 and user_2"""
        result = None
        connections = self.main_conn(user1=user_1, user2=user_2)
        if connections:
            result = connections[0]

        return result

    @staticmethod
    def get_user_conn(user):
        """looking for connection that exist for the user"""
        q_set = (
                models.Q(conn_sender=user) |
                models.Q(conn_receiver=user.profile)
        )
        connected = []
        connected_obj = Connection.objects.filter(q_set)
        for obj in connected_obj:
            if obj.approved:
                if obj.conn_sender == user:
                    connected.append(obj.conn_receiver.user)
                else:
                    connected.append(obj.conn_sender)

        return connected


# connected users
class Connection(models.Model):
    conn_sender = models.ForeignKey(User, on_delete=models.CASCADE)
    conn_receiver = models.ForeignKey(Profile, blank=False, on_delete=models.CASCADE)
    since = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_date = models.DateTimeField(blank=True, null=True)
    objects = ConnectionManager()

    class Meta:
        unique_together = ('conn_sender', 'conn_receiver')

    def get_status(self):
        if self.approved:
            status = "approved"
        else:
            status = "pending"
        return status

    def save(self, *args, **kwargs):
        if self.approved:
            self.approved_date = now()
        super().save(*args, **kwargs)

    def clean(self):
        if ConnectionManager().exist(self.conn_sender, self.conn_receiver.user):
            raise ValidationError(_('The connection already exists'))

        if self.conn_receiver.user == self.conn_sender:
            raise ValidationError(_('?'))

        return super().clean()

    @property
    def connected_since(self):
        s_ = None
        if self.approved:
            s_ = timesince(self.approved_date)
        return s_

    @property
    def connection_sent_when(self):
        return timesince(self.since)

    def __str__(self):
        return "connection between {} and {}".format(self.conn_sender, self.conn_receiver)
