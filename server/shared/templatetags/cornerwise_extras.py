from django import template

from utils import make_absolute_url

register = template.Library()

@register.filter
def absolutize(url):
    return make_absolute_url(url)
