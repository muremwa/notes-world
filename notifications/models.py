from django.db import models

from django.contrib.auth.models import User
from notes.models import Timing

class Notification(models.Model, Timing):
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField()
    seen = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    objects = models.Manager()

    class Meta:
        ordering = ['-created']

    def get_created(self):
        return self.how_long_ago(self.created)

    def __str__(self):
        return "notification to {}".format(self.to_user)
