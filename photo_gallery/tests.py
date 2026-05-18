from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import UserProfile, Tag, Photo, Like


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.tag = Tag.objects.create(name='Nature')
        self.photo = Photo.objects.create(
            title='Test Photo',
            description='A test photo',
            image=SimpleUploadedFile('test.jpg', b'fake_image_content'),
            uploaded_by=self.user,
        )
        self.photo.tags.add(self.tag)

    def test_user_profile_created_on_user_create(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_tag_auto_slug(self):
        tag = Tag.objects.create(name='Sunset Landscape')
        self.assertEqual(tag.slug, 'sunset-landscape')

    def test_photo_str(self):
        self.assertEqual(str(self.photo), 'Test Photo')

    def test_photo_ordering(self):
        photo2 = Photo.objects.create(
            title='Second Photo',
            image=SimpleUploadedFile('test2.jpg', b'more_fake'),
            uploaded_by=self.user,
        )
        photos = Photo.objects.all()
        self.assertEqual(photos[0], photo2)

    def test_like_creation(self):
        like = Like.objects.create(user=self.user, photo=self.photo, value='like')
        self.assertEqual(str(like), 'testuser liked Test Photo')
        self.assertEqual(self.photo.total_likes(), 1)
        self.assertEqual(self.photo.total_dislikes(), 0)

    def test_dislike(self):
        Like.objects.create(user=self.user, photo=self.photo, value='dislike')
        self.assertEqual(self.photo.total_dislikes(), 1)
        self.assertEqual(self.photo.total_likes(), 0)

    def test_unique_like_constraint(self):
        Like.objects.create(user=self.user, photo=self.photo, value='like')
        with self.assertRaises(Exception):
            Like.objects.create(user=self.user, photo=self.photo, value='dislike')


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.tag = Tag.objects.create(name='Nature')
        self.photo = Photo.objects.create(
            title='Test Photo',
            image=SimpleUploadedFile('test.jpg', b'fake_image_content'),
            uploaded_by=self.user,
        )
        self.photo.tags.add(self.tag)

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_shows_photos(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Photo')

    def test_home_page_filter_by_tag(self):
        response = self.client.get(reverse('home') + '?tag=nature')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Photo')

    def test_home_page_filter_invalid_tag(self):
        response = self.client.get(reverse('home') + '?tag=nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_photo_detail_page(self):
        response = self.client.get(reverse('photo_detail', args=[self.photo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_detail.html')
        self.assertContains(response, 'Test Photo')

    def test_photo_detail_404(self):
        response = self.client.get(reverse('photo_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_creates_user_and_profile(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='testpass123')
        response = self.client.post(reverse('register'), {
            'username': 'existing',
            'email': 'dup@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct')

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('profile'))

    def test_profile_page(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_profile_update(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('profile'), {
            'username': 'testuser',
            'email': 'updated@example.com',
            'bio': 'New bio content',
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.profile.bio, 'New bio content')

    def test_password_change(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)

    def test_like_photo_requires_login(self):
        response = self.client.post(reverse('like_photo', args=[self.photo.pk]), {'value': 'like'})
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('like_photo', args=[self.photo.pk]))

    def test_like_photo_toggle(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('like_photo', args=[self.photo.pk]), {'value': 'like'})
        self.assertRedirects(response, reverse('photo_detail', args=[self.photo.pk]))
        self.assertEqual(self.photo.total_likes(), 1)

        response = self.client.post(reverse('like_photo', args=[self.photo.pk]), {'value': 'like'})
        self.assertEqual(self.photo.total_likes(), 0)

    def test_like_then_dislike(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('like_photo', args=[self.photo.pk]), {'value': 'like'})
        self.client.post(reverse('like_photo', args=[self.photo.pk]), {'value': 'dislike'})
        self.assertEqual(self.photo.total_likes(), 0)
        self.assertEqual(self.photo.total_dislikes(), 1)


class FormTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_form_requires_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'nouser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')

    def test_register_form_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'nouser',
            'email': 'no@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'didn')

    def test_register_form_short_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'nouser',
            'email': 'no@example.com',
            'password1': 'short',
            'password2': 'short',
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_update_form_invalid_email(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('profile'), {
            'username': 'testuser',
            'email': 'notanemail',
            'bio': 'test',
        })
        self.assertEqual(response.status_code, 200)
