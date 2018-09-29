from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from notes.models import Note


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

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user


class NoteCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("title", "content", "privacy")
