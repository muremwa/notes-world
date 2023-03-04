from typing import List

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from notes.views import add_collaborator, notes_signal, CommentProcessing, EditComment, CommentReply, ReplyActions, \
    rm_collaborator
from api.views import comment_actions_v2, AllCommentsV2
from notes.models import Comment, Reply, Note
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
                message = f"{instance.user.get_full_name()} commented on your note '{instance.note.title}'."
            else:
                message = f"{instance.user.get_full_name()} replied to your comment on '{instance.comment.note.title}'."

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
                message = f"{item.user.get_full_name()} mentioned you in a {subject_name} {__p} {subject}."
                Notification.objects.create(to_user=user, message=message, url=url)


@receiver(notes_signal, sender=add_collaborator)
@receiver(notes_signal, sender=rm_collaborator)
def dispatch_added_collaboration_notification(sender, **kwargs):
    note: Note = kwargs.get('note')
    user: User = kwargs.get('user')

    if note and user:
        prefix = "You were added as" if sender == add_collaborator else "You are no longer"

        Notification.objects.create(
            to_user=user,
            message=f"{prefix} a collaborator on {note.title}",
            url=note.get_absolute_url()
        )


@receiver(post_save, sender=Connection)
def dispatch_connection_requests_notification(sender, instance: Connection, **kwargs):
    """
    Notify a user of connection requests, received request or accepted request
    """
    is_sent = sender == Connection and kwargs.get('created', False)
    request_sender: User = instance.conn_sender
    request_receiver: User = instance.conn_receiver.user

    if is_sent:
        Notification.objects.create(
            to_user=request_receiver,
            message=f"{request_sender.get_full_name()} sent you a connection request.",
            url=request_sender.profile.get_absolute_url()
        )

    else:
        update_fields: frozenset | None = kwargs.get('update_fields')

        if update_fields and 'approved' in update_fields:
            Notification.objects.create(
                to_user=request_sender,
                message=f"{request_receiver.get_full_name()} accepted your connection request.",
                url=request_receiver.profile.get_absolute_url()
            )
