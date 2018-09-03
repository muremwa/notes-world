from django.db import models
from django.contrib.auth.models import User


# notes model
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=500)
    content = models.TextField()
    # shared_to = models.ManyToManyField(User)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    collaborative = models.BooleanField(default=False)
    # collaborators = models.ManyToManyField(User)

    def __str__(self):
        return "note by {}".format(self.user)


# comments model
class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_date = models.DateField(auto_now_add=True)
    comment_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return "comment by {} on {}".format(self.user, self.note)


# collaborators
class Collaborators(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    Collaborators = models.ManyToManyField(User)
    name = models.CharField(max_length=500, default="{}-collaborators".format(note))
