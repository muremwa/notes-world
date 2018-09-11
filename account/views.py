from django.shortcuts import render, redirect, reverse
from .forms import SignUpForm, ProfileForm
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

# models
from .models import Profile

# sign ups
from django.contrib.auth import authenticate, login


# account page
class AccountIndex(generic.TemplateView):
    template_name = 'account/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_of_users"] = Profile.objects.all().count()


# signup
class SignUp(View):
    form_class = SignUpForm
    template_name = 'account/signup.html',

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            "form": self.form_class,
            "input_name": "sign up",
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse("base_account:profile"))


# profile
class ProfilePage(LoginRequiredMixin, generic.TemplateView):
    template_name = 'account/profile.html'


# profile edit
class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "account/profile_create.html"
    template_name_suffix = "_create"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['input_name'] = "edit profile"
        return context
