from modeltranslation.translator import register, TranslationOptions

from .models import Banner, Category, City, Product


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('banner_title', 'banner_subtitle')


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ('name',)
