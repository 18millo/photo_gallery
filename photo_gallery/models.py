from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Photo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    tags = models.ManyToManyField(Tag, related_name='photos', blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.interactions.filter(value='like').count()

    def total_dislikes(self):
        return self.interactions.filter(value='dislike').count()


class Like(models.Model):
    LIKE_CHOICES = [('like', 'Like'), ('dislike', 'Dislike')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='interactions')
    value = models.CharField(max_length=7, choices=LIKE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'photo')

    def __str__(self):
        return f"{self.user.username} {self.value}d {self.photo.title}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
