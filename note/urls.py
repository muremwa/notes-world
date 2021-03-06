from django.views.generic import RedirectView
from django.urls import path, include, re_path
from django.views.static import serve
from django.contrib import admin

# static and media
from django.conf import settings
# from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # account
    path('account/', include("account.urls")),

    # notes
    path('notes/', include("notes.urls")),

    # redirect to notes
    path('', RedirectView.as_view(url="/notes/")),

    # api(s)
    path('api/', include('api.urls')),

    # notifications
    path('notifications/', include("notifications.urls")),

    # favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL+"favicon.ico")),

    # media  | comment out when debug is true
    re_path('^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]


# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
