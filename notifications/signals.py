from typing import List

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse

from notes.views import add_collaborator, notes_signal, CommentProcessing, EditComment, CommentReply, ReplyActions
from api.views import comment_actions_v2, AllCommentsV2
from account.views import accept, account_signal
from notes.models import Comment, Reply
from account.models import Connection
from .models import Notification


@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Reply)
def dispatch_comment_or_reply_notification(sender, instance: Comment | Reply, **kwargs):
    """
    Notify a Note owner they have a new comment
    Notify a Comment owner they have a new reply
    """
    if kwargs.get('created'):
        is_comment = sender == Comment
        item_owner = instance.note.user if is_comment else instance.comment.user

        if instance.user != item_owner:
            if is_comment:
                message = f"{instance.user.get_full_name()} commented on your note '{instance.note.title}'"
            else:
                message = f"{instance.user.get_full_name()} replied to your comment on '{instance.comment.note.title}'"

            Notification.objects.create(
                to_user=item_owner,
                message=message,
                url=instance.get_absolute_url()
            )


# create notifications for mentioning on comments or replies
@receiver(notes_signal, sender=ReplyActions)
@receiver(notes_signal, sender=CommentReply)
@receiver(notes_signal, sender=CommentProcessing)
@receiver(notes_signal, sender=EditComment)
@receiver(notes_signal, sender=comment_actions_v2)
@receiver(notes_signal, sender=AllCommentsV2)
def dispatch_mentioned_notification(sender, **kwargs):
    is_comment = sender not in [CommentReply, ReplyActions]
    item: Comment | Reply = kwargs.get('comment' if is_comment else 'reply')
    mentioned: List[User] | None = kwargs.get('mentioned')

    if item:
        url = item.get_absolute_url()

        if mentioned:
            if is_comment:
                subject = item.note.title
                subject_name = 'comment'
                __p = 'on'

            else:
                subject = f"comment by {item.comment.user.get_full_name()} on {item.comment.note.title}"
                subject_name = 'reply'
                __p = 'to'

            for user in mentioned:
                message = f"{item.user.get_full_name()} mentioned you in a {subject_name} {__p} {subject}"
                Notification.objects.create(to_user=user, message=message, url=url)


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
    url = kwargs['note'].get_absolute_url()

    Notification.objects.create(
        to_user=to,
        message=message,
        url=url
    )
