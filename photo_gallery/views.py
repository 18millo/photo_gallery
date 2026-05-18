from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Photo, Tag, Like, UserProfile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def home(request):
    tag_slug = request.GET.get('tag')
    photos = Photo.objects.all()
    tags = Tag.objects.annotate(photo_count=Count('photos'))
    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
        photos = photos.filter(tags=selected_tag)
    return render(request, 'home.html', {
        'photos': photos,
        'tags': tags,
        'selected_tag': selected_tag,
    })


def photo_detail(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    user_interaction = None
    if request.user.is_authenticated:
        user_interaction = Like.objects.filter(
            user=request.user, photo=photo
        ).first()
    return render(request, 'photo_detail.html', {
        'photo': photo,
        'user_interaction': user_interaction,
    })


@login_required
def like_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    value = request.POST.get('value', 'like')
    if value not in ['like', 'dislike']:
        value = 'like'
    interaction, created = Like.objects.get_or_create(
        user=request.user,
        photo=photo,
        defaults={'value': value},
    )
    if not created:
        if interaction.value == value:
            interaction.delete()
        else:
            interaction.value = value
            interaction.save()
    return redirect('photo_detail', pk=pk)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, f'Account created for {username}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'u_form': u_form,
        'p_form': p_form,
    })
