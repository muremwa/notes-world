from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timesince import timesince

from account.models import Profile, Connection


# notes manager
class NoteManager(models.Manager):
    @staticmethod
    def notes_user_can_see(user):
        """takes a user and returns all notes from the users connected users"""
        connected_users = Connection.objects.get_user_conn(user)
        q_sets = [list(Note.objects.filter(user=connected_user)) for connected_user in connected_users]
        if not q_sets:
            return []
        notes = [note for q_set in q_sets for note in q_set]
        return [note for note in notes if note.privacy != "PR"]

    def collaborations(self, user):
        """notes that the user is a collaborator on"""
        notes = self.notes_user_can_see(user)
        return [note for note in notes if user.profile in note.collaborators.all()]


# notes model
class Note(models.Model):
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
    tags = models.ManyToManyField('Tag')
    objects = NoteManager()

    class Meta:
        ordering = ["-created"]

    # get a readable name
    def __str__(self):
        return "{} by {}".format(self.title, self.user)

    # get the last time it was modified
    def get_last_modified(self):
        respond_with = None

        if self.last_modified:
            respond_with = f'{timesince(self.last_modified)} ago'

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
class Comment(models.Model):
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
        response = None
        if self.created:
            response = f'{timesince(self.created)} ago'
        return response

    def is_modified(self):
        if self.modified:
            if self.modified > self.created:
                return True
            else:
                return False
        else:
            return False

    @property
    def stamp(self):
        return self.modified.timestamp() if self.is_modified() else self.created.timestamp()

    @property
    def created_stamp(self):
        return self.created.timestamp()

    @property
    def reply_url(self):
        return reverse('notes:reply-comment', kwargs={'comment_id': str(self.pk)})

    @property
    def action_url(self):
        return reverse('api:comment-actions-v2', kwargs={'comment_pk': str(self.pk)})

    def get_absolute_url(self):
        return f"{reverse('notes:note-page', args=[str(self.note.pk)])}#comment{self.pk}"

    def __str__(self):
        return "comment by {} on {}".format(self.user, self.note)


class Reply(models.Model):
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
        return f'{timesince(self.created)} ago'

    def get_absolute_url(self):
        return f"{reverse('notes:reply-comment', args=[str(self.comment.pk)])}#reply{self.pk}"

    def __str__(self):
        return "Reply by {} to {}".format(self.user, self.comment)


class Tag(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.name} (Tag)"
