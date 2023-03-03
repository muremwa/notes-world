from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Notification


# new notifications
@login_required
def new_notification(request):
    response = {'new': request.user.notification_set.filter(seen=False).count()}
    return JsonResponse(response)


# mark a notification as opened
@login_required
def make_opened(request, notification_id):
    result = dict()
    code = 400

    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=notification_id)

        if request.user == notification.to_user and not notification.opened:
            result['success'] = True
            notification.opened = True
            notification.save()
            code = 200
        else:
            result['success'] = False
    else:
        result['success'] = False
    return JsonResponse(result, status=code)


# delete notification
@login_required
def delete_notification(request, notification_id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, pk=notification_id)

        if request.user == notification.to_user:
            notification.delete()
            return JsonResponse({'success': True, "message": "Notification deleted"})


@login_required
def bulk_delete_notifications(request):
    notifications_deleted = 0

    if request.method == 'POST':
        try:
            _from_date = int(request.POST.get('from', 0))
            _to_date = request.POST.get('to', 0)
            _all = False

            if _to_date == 'all':
                _to_date = _from_date + 1
                _all = True
            else:
                _to_date = int(_to_date)

            if (_from_date != _to_date) and (_to_date > _from_date):
                from_ = timezone.now()
                _del = (0,)

                if _from_date > 0:
                    from_ = from_ - timezone.timedelta(days=_from_date)

                notifications = request.user.notification_set.filter(created__date__lte=from_)

                if _all:
                    _del = notifications.delete()
                else:
                    to_ = timezone.now() - timezone.timedelta(days=_to_date)
                    _del = notifications.filter(created__date__gte=to_).delete()

                notifications_deleted = _del[0]

        except ValueError:
            pass

    return redirect(f'{reverse("base_account:profile")}?nd={notifications_deleted}')
