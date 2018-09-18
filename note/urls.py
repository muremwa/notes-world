from django.contrib import admin
from django.urls import path, include, reverse
from django.views.generic import RedirectView

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

    # favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL+"favicon.ico")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

