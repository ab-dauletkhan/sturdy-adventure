import json
import os

from django.utils.translation import get_language

_cache = {}


def _load():
    if _cache:
        return
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
    for lang in ('kk', 'en', 'ru'):
        with open(os.path.join(base, f'{lang}.json'), encoding='utf-8') as f:
            _cache[lang] = json.load(f)


def t(key, **kwargs):
    _load()
    lang = (get_language() or 'kk')[:2]
    if lang not in _cache:
        lang = 'kk'
    value = _cache[lang].get(key) or _cache['kk'].get(key, key)
    return value.format(**kwargs) if kwargs else value


class LazyTranslation:
    def __init__(self, key, **kwargs):
        self.key = key
        self.kwargs = kwargs

    def __str__(self):
        return t(self.key, **self.kwargs)

    def __format__(self, spec):
        return format(str(self), spec)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)


def lazy_t(key, **kwargs):
    return LazyTranslation(key, **kwargs)
