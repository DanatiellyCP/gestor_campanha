from django import template

register = template.Library()

@register.filter
def friendly_key(value):
    if not isinstance(value, str):
        return value
    return value.replace('_', ' ').capitalize()
