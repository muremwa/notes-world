from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse
from account.models import Profile


# notes model
class Note(models.Model):
    privacy_options = (("PB", "public"), ("CO", "connected"), ("PR", "private"),)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=500)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    collaborative = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)
    privacy = models.CharField(max_length=2, choices=privacy_options, default="PR")
    collaborators = models.ManyToManyField(Profile, blank=True)

    # get the last time it was modified
    def get_last_modified(self):
        respond_with = None
        if self.last_modified:
            current_time = str(datetime.now())
            modified_time = str(self.last_modified)
            time_format = "%Y-%m-%d %H:%M:%S.%f"
            difference = datetime.strptime(current_time, time_format) - \
                         datetime.strptime(modified_time[:-6], time_format)
            days = difference.days
            # remove 180 seconds before hand as the server time is 3 hours behind
            seconds = difference.seconds - (3*(60*60))
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
            else:
                respond_with = "{} days ago".format(int(days))

        return respond_with

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
        return reverse("notes:note-page", args=[str(self.id)])

    # get a readable name
    def __str__(self):
        return "{} by {}".format(self.title, self.user)


    class Meta:
        ordering = ["-created"]


# comments model
class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_date = models.DateField(auto_now_add=True)
    comment_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return "comment by {} on {}".format(self.user, self.note)
