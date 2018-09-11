from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

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

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return "profile for {}".format(self.user)

    def get_absolute_url(self):
        return reverse("base_account:profile")
