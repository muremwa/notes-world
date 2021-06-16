from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils.timesince import timesince


class Notification(models.Model):
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
        return f'{timesince(self.created)} ago'

    def del_url(self):
        return reverse("notifications:delete", args=[str(self.pk)])

    def __str__(self):
        return "notification to {}".format(self.to_user)
