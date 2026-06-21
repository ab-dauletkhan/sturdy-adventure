from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Test OK")

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('test/', test_view),
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)