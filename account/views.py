from django.shortcuts import render, redirect, reverse
from .forms import SignUpForm, ProfileForm
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# models
from .models import Profile

# sign ups
from django.contrib.auth import authenticate, login


# account page
def index(request):
    users = Profile.objects.all().count()
    return render(request, 'account/index.html', {
        # "heading2": title,
        "no_of_users": users,
    })


# signup
def signUp(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse("base_account:profile"))


    else:
        form = SignUpForm()

    return render(request, 'account/signup.html', {"form": form})


# profile
@login_required
def profile(request):
    return render(request, 'account/profile.html')


# profile edit
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "account/profile_create.html"
    template_name_suffix = "_create"
