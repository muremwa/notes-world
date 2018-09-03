from django.contrib import admin
from django.urls import path, include
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

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

