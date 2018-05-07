from django import template

from utils import make_absolute_url

register = template.Library()


@register.simple_tag(takes_context=True)
def absolutize(context, url):
    return make_absolute_url(url, context["hostname"])
