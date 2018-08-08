from django import template
from django.urls import reverse

import io
import pprint

from utils import make_absolute_url

register = template.Library()


@register.simple_tag(takes_context=True)
def absolutize(context, url):
    return make_absolute_url(url, context.get("hostname"))


@register.simple_tag(takes_context=True)
def absolute_url(context, url_name, *args, **kwargs):
    url = reverse(url_name, args=args, kwargs=kwargs)
    return make_absolute_url(url, context.get("hostname"))


@register.filter()
def pretty_print(x):
    with io.StringIO() as buff:
        pprint.pprint(x, buff)
        buff.seek(0)
        return buff.read()
