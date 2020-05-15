from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Notification


# new notifications
def new_notification(request):
    response = {'new': request.user.notification_set.filter(seen=False).count()}
    return JsonResponse(response)


# mark a notification as opened
def make_opened(request, notification_id):
    result = dict()
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=notification_id)
        if request.user == notification.to_user:
            result['success'] = True
            notification.opened = True
            notification.save()
        else:
            result['success'] = False
    else:
        result['success'] = False
    return JsonResponse(result)


# delete notification
def delete_notification(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, pk=notification_id)

        if request.user == notification.to_user:
            notification.delete()
            return JsonResponse({'success': True, "message": "Notification deleted"})
