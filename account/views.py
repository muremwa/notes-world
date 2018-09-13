from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.db.models import Q
from django.http import JsonResponse
import random

# models & forms
from .models import Profile, Connection
from .forms import SignUpForm, ProfileForm
from django.contrib.auth.models import User

# sign ups
from django.contrib.auth import authenticate, login


# account page
class AccountIndex(generic.TemplateView):
    template_name = 'account/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_of_users"] = Profile.objects.all().count()


# sign up
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse('base_account:profile'))

    else:
        form = SignUpForm()

    return render(request, 'account/signup.html', {
        'form': form,
        'input_name': "sign up"
    })

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


# connected page
class ConnectedUser(generic.TemplateView):
    template_name = "account/connect.html"

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        suggestions = []
        qset_1 = (
            Q(conn_receiver=self.request.user.profile) &
            Q(approved=False)
        )
        requests = Connection.objects.filter(qset_1).distinct()
        qset = (
            Q(conn_sender=self.request.user.profile.user) |
            Q(conn_receiver=self.request.user.profile)
        )
        connected = []
        checking = []
        connected_obj = Connection.objects.filter(qset).distinct()

        for obj in connected_obj:
            if obj.conn_sender == self.request.user:
                checking.append(obj.conn_receiver.user)
            else:
                checking.append(obj.conn_sender)

        for obj in connected_obj:
            if obj.approved:
                if obj.conn_sender == self.request.user:
                    connected.append(obj.conn_receiver.user)
                else:
                    connected.append(obj.conn_sender)

        # suggestions
        for i in range(10):
                suggestion = random.choice(users)
                if suggestion != self.request.user and suggestion not in suggestions and suggestion not in checking:
                    suggestions.append(suggestion)


        return render(request, self.template_name, {
            'suggestions': suggestions,
            "connected": connected,
            "requests": requests,
        })


# send a connection request
def connect(request, id):
    if request.method == "POST":
        response = {}
        sender = request.user
        receiver = get_object_or_404(User, pk=id).profile
        qset = (
            Q(conn_sender=request.user) &
            Q(conn_receiver=receiver)
        )
        qset_2 = (
            Q(conn_sender=receiver.user) &
            Q(conn_receiver=request.user.profile)
        )
        checking_1 = Connection.objects.filter(qset)
        checking_2 = Connection.objects.filter(qset_2)

        if len(checking_1) == 0 and len(checking_2) == 0:
            Connection.objects.create(
                conn_sender=sender,
                conn_receiver=receiver
            )
            response['sent'] = True
        else:
            response['sent'] = False
            response['state'] = "request is sent already"

        return JsonResponse(response)

    else:
        raise Http404


# accept a connection request
def accept(request, id):
    if request.method == "POST":
        response = {}
        _connection = get_object_or_404(Connection, pk=id)

        if _connection.approved:
            response['state'] = "already approved"
            response['accepted'] = False
        else:
            _connection.approved = True
            _connection.save()
            response['state'] = "you have approved"
            response['accepted'] = True

        return JsonResponse(response)
    else:
        raise Http404


# delete an existing request
def dis_connect(request, id):
    if request.method == "POST":
        friend = get_object_or_404(User, pk=id)
        response = {}
        qset_1 = (
            Q(conn_sender=request.user) &
            Q(conn_receiver=friend.profile)
        )
        qset_2 = (
            Q(conn_sender=friend) &
            Q(conn_receiver=request.user.profile)
        )

        _connection = Connection.objects.filter(qset_1)
        _connection_2 = Connection.objects.filter(qset_2)

        if len(_connection_2) == 0 and len(_connection) == 0:
            response['exited'] = False
            response['state'] = "connection no longer exists"
        else:
            if len(_connection) > 0:
                connection = _connection[0]
            else:
                connection = _connection_2[0]

            connection.delete()
            response['exited'] = True
            response['state'] = "disconnected"

        return JsonResponse(response)
    else:
        raise Http404


# deny a connection request
def deny(request, id):
    if request.method == "POST":
        conn_request = get_object_or_404(Connection, pk=id)
        response = {}
        if not conn_request.approved:
            conn_request.delete()
            response['denied'] = True
            response['state'] = "you have denied the request"
        elif conn_request.approved:
            response['denied'] = False
            response['state'] = "you cannot deny an approved request"

        return JsonResponse(response)
    else:
        raise Http404
