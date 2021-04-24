from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def clean_tags(q_tags, arg):
    qq_tags = q_tags.copy()
    if arg in qq_tags:
        qq_tags.remove(arg)
    return ','.join(qq_tags)


@register.filter
@stringfilter
def new_tag_f(q_tag, arg):
    if len(q_tag) == 0:
        return arg
    return f'{q_tag},{arg}'
