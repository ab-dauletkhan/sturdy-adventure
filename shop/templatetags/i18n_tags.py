from django import template

from shop.json_translations import t as _t

register = template.Library()


@register.simple_tag
def translate(key, **kwargs):
    return _t(key, **kwargs)


@register.filter
def translate_status(status):
    return _t(f'status.{status}')
