# django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from django.dispatch import Signal

# normal
import random
from itertools import chain

# models & forms +
from .models import Profile, Connection
from .forms import SignUpForm, ProfileForm, UserEditForm
from django.contrib.auth.models import User

# sign ups
from django.contrib.auth import authenticate, login

account_signal = Signal(providing_args=['connection', ])


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

    def get_notifications(self):
        notifications = self.request.user.notification_set.all()
        for notification in notifications:
            notification.seen = True
            notification.save()
        return notifications

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new'] = self.request.user.notification_set.filter(seen=False).count()
        context['notifications'] = self.get_notifications()
        return context


class ProfileUserEdit(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "account/profile_create.html"

    def get_success_url(self):
        return reverse("base_account:profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_details'] = True
        context['input_name'] = "edit details"
        if self.request.user != context['user']:
            raise Http404
        return context


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
class ConnectedUser(LoginRequiredMixin, generic.TemplateView):
    template_name = "account/connect.html"

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        suggestions = []

        # checks whether a user has requests to them and they aren't approved
        requests = self.request.user.profile.connection_set.filter(approved=False)
        # suggestions
        for i in range(10):
                suggestion = random.choice(users)
                status = Connection.objects.exist(request.user, suggestion)
                if suggestion != self.request.user and suggestion not in suggestions and not status:
                    suggestions.append(suggestion)

        # sent connections
        sent_connections = self.request.user.connection_set.filter(approved=False)

        return render(request, self.template_name, {
            'suggestions': suggestions,
            "connected": Connection.objects.get_user_conn(self.request.user),
            "requests": requests,
            "sent_connections": sent_connections,
        })


class ForeignUser(LoginRequiredMixin, generic.TemplateView):
    template_name = 'account/foreign_user.html'

    def connected(self, user):
        conn_types = ['no_conn', 'req_sent', 'req_received', 'connected']
        if Connection.objects.exist(self.request.user, user):
            conn = Connection.objects.get_conn(self.request.user, user)
            if conn.approved:
                return conn_types[-1]
            else:
                if conn.conn_sender == user:
                    return conn_types[2]
                elif conn.conn_receiver.user == user:
                    return conn_types[1]
        else:
            return conn_types[0]

    @staticmethod
    def user_notes(user, conn_type):
        pub_notes = user.note_set.filter(privacy="PB")
        if conn_type == "connected":
            co_notes = user.note_set.filter(privacy="CO")
            return chain(co_notes, pub_notes)
        else:
            return pub_notes

    def mutual_conns(self, user):
        conns = []
        my_conns = Connection.objects.get_user_conn(self.request.user)
        foreign_conns = Connection.objects.get_user_conn(user)

        for user_ in my_conns:
            if user_ in foreign_conns:
                conns.append(user_)
        return conns

    def get(self, request, *args, **kwargs):
        foreign_user = get_object_or_404(User, pk=kwargs['user_id'])
        if foreign_user == request.user:
            return redirect(reverse("base_account:connected"))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['foreign_user'] = get_object_or_404(User, pk=kwargs['user_id'])
        context['conn'] = Connection.objects.get_conn(self.request.user, context['foreign_user'])
        context['conn_type'] = self.connected(context['foreign_user'])
        context['mutual_users'] = self.mutual_conns(context['foreign_user'])
        context['notes'] = self.user_notes(context['foreign_user'], context['conn_type'])
        return context


# send a connection request
@login_required
def connect(request, user_id):
    if request.method == "POST":
        response = {}
        sender = request.user
        receiver = get_object_or_404(User, pk=user_id).profile
        exists = Connection.objects.exist(user_1=sender, user_2=receiver.user)
        if not exists:
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
@login_required
def accept(request, conn_id):
    if request.method == "POST":
        response = {}
        _connection = get_object_or_404(Connection, pk=conn_id)

        if _connection.approved:
            response['state'] = "already approved"
            response['accepted'] = False
        else:
            _connection.approved = True
            _connection.save()
            response['state'] = "you have approved"
            response['accepted'] = True
            account_signal.send(accept, connection=_connection)

        return JsonResponse(response)
    else:
        raise Http404


# delete an existing request
@login_required
def dis_connect(request, user_id):
    if request.method == "POST":
        friend = get_object_or_404(User, pk=user_id)
        response = {}
        status = Connection.objects.exist(request.user, friend)

        if not status:
            response['exited'] = False
            response['state'] = "connection no longer exists"
        else:
            connection = Connection.objects.get_conn(request.user, friend)
            connection.delete()
            response['exited'] = True
            response['state'] = "disconnected"

        return JsonResponse(response)
    else:
        raise Http404


# deny a connection request
@login_required
def deny(request, conn_id):
    if request.method == "POST":
        conn_request = get_object_or_404(Connection, pk=conn_id)
        response = {}
        if not conn_request.approved:
            conn_request.delete()
            response['denied'] = True
            response['state'] = "you have cancelled the request"
        elif conn_request.approved:
            response['denied'] = False
            response['state'] = "you cannot cancel an approved request"

        return JsonResponse(response)
    else:
        raise Http404
