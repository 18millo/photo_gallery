from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def avatar_url(user_profile, size=40):
    if user_profile and user_profile.profile_picture:
        return user_profile.profile_picture.url
    return None


@register.simple_tag
def avatar_initials(user):
    if not user or not user.is_authenticated:
        return '?'
    name = user.get_full_name() or user.username
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()
