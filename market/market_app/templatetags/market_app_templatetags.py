from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
@stringfilter
def add_path(filename):
    filename = filename[:1] + filename[-4:]
    return f"assets/img/icons/departments/{filename}"
