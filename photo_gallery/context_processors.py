from .models import UserProfile


def user_profile(request):
    ctx = {}
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        ctx['user_profile'] = profile
        if profile.profile_picture:
            ctx['avatar_url'] = profile.profile_picture.url
        else:
            ctx['avatar_url'] = None
    return ctx
