from django.utils.translation import get_language

from .models import Category, Banner


def site_context(request):
    categories = Category.objects.all()
    banners = Banner.objects.filter(is_active=True)
    return {
        'categories': categories,
        'banners': banners,
        'current_language': get_language(),
    }