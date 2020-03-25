from functools import reduce

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse

from account.models import Profile, Connection


class Timing:
    @staticmethod
    def difference(og_time, time):
        current_time = str(og_time)
        modified_time = str(time)
        time_format = "%Y-%m-%d %H:%M:%S.%f"
        difference = datetime.strptime(current_time, time_format) - datetime.strptime(modified_time[:-6], time_format)
        return difference

    def how_long_ago(self, time):
        difference = self.difference(time=time, og_time=(str(datetime.now())))
        days = difference.days
        # remove 180 seconds before hand as the server time is 3 hours behind
        seconds = difference.seconds - (3 * (60 * 60))
        minutes = (seconds / 60)
        hours = (minutes / 60)

        if days < 1:
            if hours < 1:
                if minutes < 1:
                    if seconds < 20:
                        respond_with = "just now"
                    else:
                        respond_with = "{} seconds ago".format(int(seconds))
                else:
                    respond_with = "{} minutes ago".format(int(minutes))
            else:
                respond_with = "{} hours ago".format(int(hours))
        elif days < 50:
            respond_with = "{} days ago".format(int(days))

        elif days < 365:
            respond_with = "{} months ago".format(int(int(days)/28))

        elif days < (365*2):
            respond_with = "1 year ago"

        else:
            respond_with = "{} years ago".format(int(int(days)/365))

        return respond_with


# notes manager
class NoteManager(models.Manager):
    @staticmethod
    def notes_user_can_see(user):
        """takes a user and returns all notes from the users connected users"""
        connected_users = Connection.objects.get_user_conn(user)
        q_sets = [list(Note.objects.filter(user=connected_user)) for connected_user in connected_users]
        notes = reduce(lambda set_1, set_2: set_1 + set_2, q_sets)
        return [note for note in notes if note.collaborative]

    def collaborations(self, user):
        """notes that the user is a collaborator on"""
        collaborations = []
        notes = self.notes_user_can_see(user)

        for note in notes:
            if user.profile in note.collaborators.all():
                collaborations.append(note)
        return collaborations


# notes model
class Note(models.Model, Timing):
    privacy_options = (("PB", "public"), ("CO", "connected"), ("PR", "private"),)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=500)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    collaborative = models.BooleanField(default=False)
    last_modified = models.DateTimeField(null=True, blank=True)
    last_modifier = models.CharField(max_length=5, blank=True, null=True)
    privacy = models.CharField(max_length=2, choices=privacy_options, default="PR")
    collaborators = models.ManyToManyField(Profile, blank=True)
    objects = NoteManager()

    class Meta:
        ordering = ["-created"]

        # get a readable name
    def __str__(self):
        return "{} by {}".format(self.title, self.user)

    # get the last time it was modified
    def get_last_modified(self):
        if self.last_modified:
            respond_with = self.how_long_ago(self.last_modified)
        else:
            respond_with = None

        return respond_with

    # last modifier
    def get_last_modifier(self):
        modifier = None
        if self.last_modifier:
            modifier = User.objects.get(id=self.last_modifier)
        return modifier

    # get privacy name
    def get_privacy(self):
        if self.privacy == "PR":
            privacy = "private"
        elif self.privacy == "CO":
            privacy = "connected friends only"
        else:
            privacy = "public"
        return privacy

    # url
    def get_absolute_url(self):
        return reverse("notes:note-page", args=[str(self.pk)])


# comments model
class Comment(models.Model, Timing):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    original_comment = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(null=True)
    mentioned = models.ManyToManyField(Profile)
    objects = models.Manager()

    class Meta:
        ordering = ['-created']

    def get_created(self):
        if self.created:
            response = self.how_long_ago(self.created)
        else:
            response = None
        return response

    def is_modified(self):
        if self.modified:
            if self.modified > self.created:
                return True
            else:
                return False
        else:
            return False

    def __str__(self):
        return "comment by {} on {}".format(self.user, self.note)


class Reply(models.Model, Timing):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_text = models.TextField()
    original_reply = models.CharField(max_length=140)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.BooleanField(default=False)
    mentioned = models.ManyToManyField(Profile)
    objects = models.Manager()

    class Meta:
        ordering = ['-created']
        verbose_name_plural = "Replies"

    def get_created(self):
        return self.how_long_ago(self.created)

    def __str__(self):
        return "Reply by {} to {}".format(self.user, self.comment)
