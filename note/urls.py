from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.views.static import serve

# static and media
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # account
    path('account/', include("account.urls")),

    # notes
    path('notes/', include("notes.urls")),

    # redirect to notes
    path('', RedirectView.as_view(url="/notes/")),

    # Accounts and authentication
    path('accounts/', include("django.contrib.auth.urls")),

    # api(s)
    path('api/', include('api.urls')),

    # notifications
    path('notifications/', include("notifications.urls")),

    # favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL+"favicon.ico")),

    # media
    re_path('^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
