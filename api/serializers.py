import re

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User

from account.models import Profile
from notes.models import Note, Comment


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title', 'created', 'last_modified', 'privacy', 'user')


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'created', 'last_modified', 'user')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if re.search(r'@', data.get('username', '')):
            raise ValidationError(_('no @ signs on username'), code="at_sign")
        
        if data.get('email', None) is None:
            raise ValidationError(_('Email field is missing'), code='email-mia')

        if not re.search(r'\w+@\w+\.\w+', data.get('email', '')):
            raise ValidationError(_('Enter a valid email address'), code='email-wrong')

        return data

    def create(self, validated_data):
        user = User(
            username=validated_data.get('username', None),
            email=validated_data.get('email', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user


class NoteCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("title", "content", "privacy")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'note', 'user', 'original_comment', 'created')


class ApiUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    profile = serializers.ImageField(source='profile.image')

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'profile')


class ApiProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    user_id = serializers.IntegerField(source='pk')
    profile_url = serializers.URLField(source='get_absolute_url')

    class Meta:
        model = Profile
        fields = ('username', 'user_id', 'profile_url')


class ApiCommentSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(source='pk')
    key = serializers.FloatField(source='stamp')
    user = ApiUserSerializer(many=False)
    mentioned = ApiProfileSerializer(many=True)
    time = serializers.CharField(source='get_created')
    text = serializers.CharField(source='original_comment')
    edited = serializers.BooleanField(source='is_modified')
    replies = serializers.IntegerField(source='reply_set.count')
    reply_url = serializers.URLField()
    action_url = serializers.URLField()

    class Meta:
        model = Comment
        fields = (
            'comment_id', 'key', 'user', 'time', 'text', 'edited', 'replies', 'reply_url', 'action_url', 'mentioned',
        )


class ApiNoteSerializer(serializers.ModelSerializer):
    note = serializers.CharField(source='title')
    user = ApiUserSerializer(many=False)
    comments = ApiCommentSerializer(many=True, source='comment_set')

    class Meta:
        model = Note
        fields = ('id', 'note', 'user', 'comments')
