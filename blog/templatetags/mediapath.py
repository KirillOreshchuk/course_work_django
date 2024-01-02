from django import template

register = template.Library()


@register.filter()
def mediapath(values):
    if values:
        return f'/media/{values}'


@register.simple_tag
def mediapath(values):
    if values:
        return f'/media/{values}'


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

