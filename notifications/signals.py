from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse

from .models import Notification
from notes.models import Comment, Reply
from notes.views import add_collaborator, notes_signal, CommentProcessing, EditComment, CommentReply, ReplyActions
from account.models import Connection
from account.views import accept, account_signal


# notify a note's owner that a comment on it has been made
@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, **kwargs):
    if kwargs['created']:
        note_owner = instance.note.user
        if instance.user != note_owner:
            Notification.objects.create(
                to_user=note_owner,
                message="{} commented on {}".format(instance.user.get_full_name(), instance.note),
                url=instance.note.get_absolute_url()+"#comment"+str(instance.id)
            )


# notify a comment's owner that it has been replied to
@receiver(post_save, sender=Reply)
def notify_new_reply(sender, instance, **kwargs):
    if kwargs['created']:
        comment_owner = instance.comment.user
        if instance.user != comment_owner:
            Notification.objects.create(
                to_user=comment_owner,
                message="{} replied to your comment on {}".format(instance.user.get_full_name(), instance.comment.note),
                url=reverse('notes:reply-comment', args=[str(instance.comment.id)])+"#reply"+str(instance.id)
            )


def notify_mention_now(user, message, url):
    Notification.objects.create(
        to_user=user,
        message=message,
        url=url
    )


def notify_mention_middle(type, users, obj, url, **kwargs):
    for user in users:
        to = user
        message = "{} mentioned you in their {} on {}".format(obj.user.get_full_name(), type, kwargs['to_what'])
        notify_mention_now(to, message, url)


def notify_mention_top(type, mentioned, location_url, **kwargs):
    if type == CommentProcessing or type == EditComment:
        notify_mention_middle('comment', mentioned, kwargs['comment'], location_url, to_what=kwargs['comment'].note)
    elif type == CommentReply or type == ReplyActions:
        notify_mention_middle('reply', mentioned, kwargs['reply'], location_url, to_what=kwargs['reply'].comment)


# notify a user they have been mentioned in a comment
@receiver(notes_signal, sender=CommentProcessing)
def notify_mentioning_comment(sender, **kwargs):
    type = sender
    comment = kwargs['comment']
    mentioned = kwargs['mentioned']
    url = reverse("notes:note-page", args=[str(comment.note.id)])+"#comment"+str(comment.id)
    notify_mention_top(type, mentioned, url, comment=comment)


# notify a user they have been mentioned in an edited comment
@receiver(notes_signal, sender=EditComment)
def notify_mentioning_comment_edit(sender, **kwargs):
    type = sender
    comment = kwargs['comment']
    mentioned = kwargs['mentioned']
    url = reverse("notes:note-page", args=[str(comment.note.id)])+"#comment"+str(comment.id)
    notify_mention_top(type, mentioned, url, comment=comment)


# notify a user they have been mentioned in a reply
@receiver(notes_signal, sender=CommentReply)
def notify_mentioning_reply(sender, **kwargs):
    type = sender
    reply = kwargs['reply']
    mentioned = kwargs['mentioned']
    url = reverse("notes:reply-comment", args=[str(reply.comment.id)])+"#reply"+str(reply.id)
    notify_mention_top(type, mentioned, url, reply=reply)


# notify a user they have been mentioned in an edited reply
@receiver(notes_signal, sender=ReplyActions)
def notify_mentioning_reply(sender, **kwargs):
    type = sender
    reply = kwargs['reply']
    mentioned = kwargs['mentioned']
    url = reverse("notes:reply-comment", args=[str(reply.comment.id)])+"#reply"+str(reply.id)
    notify_mention_top(type, mentioned, url, reply=reply)


# notify a user of the new requests they have
@receiver(post_save, sender=Connection)
def notify_received_request(sender, instance, **kwargs):
    if kwargs['created']:
        Notification.objects.create(
            to_user=instance.conn_receiver.user,
            message="{} sent you a connection request. Click here to see.".format(instance.conn_sender.get_full_name()),
            url=reverse('base_account:foreign-user', args=[str(instance.conn_sender.id)])
        )


# notify a user their request has been accepted
@receiver(account_signal, sender=accept)
def notify_accepted_request(sender, **kwargs):
    connection = kwargs['connection']
    to_user_ = connection.conn_sender
    from_user = connection.conn_receiver.user
    message = "{} accepted your connection request. You are now connected. " \
              "Click here to see.".format(from_user.get_full_name())
    url = reverse("base_account:foreign-user", args=[str(from_user.id)])

    Notification.objects.create(
        to_user=to_user_,
        message=message,
        url=url
    )


# notify a user that they have been added as a collaborator
@receiver(notes_signal, sender=add_collaborator)
def notify_collaboration(sender, **kwargs):
    to = kwargs['user']
    message = "You were added as a collaborator on {}".format(kwargs['note'])
    url= kwargs['note'].get_absolute_url()

    Notification.objects.create(
        to_user=to,
        message=message,
        url=url
    )
