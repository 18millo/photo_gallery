from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from photo_gallery.models import Tag, Photo, UserProfile
import urllib.request
import io


PHOTO_DATA = [
    {"title": "Misty Mountain Sunrise", "tags": ["Nature", "Landscape", "Mountains"], "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"},
    {"title": "Serene Forest Path", "tags": ["Nature", "Forest", "Landscape"], "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800"},
    {"title": "Golden Hour Beach", "tags": ["Nature", "Beach", "Sunset"], "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"},
    {"title": "Autumn Colors", "tags": ["Nature", "Forest", "Landscape"], "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800"},
    {"title": "Northern Lights Dance", "tags": ["Nature", "Night", "Landscape"], "url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800"},
    {"title": "Mountain Lake Reflection", "tags": ["Nature", "Mountains", "Water"], "url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800"},
    {"title": "Desert Dunes at Dusk", "tags": ["Nature", "Desert", "Sunset"], "url": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800"},
    {"title": "Rainforest Canopy", "tags": ["Nature", "Forest", "Tropical"], "url": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800"},
    {"title": "Waterfall in the Woods", "tags": ["Nature", "Water", "Forest"], "url": "https://images.unsplash.com/photo-1439853949127-fa647821eba0?w=800"},
    {"title": "Rolling Green Hills", "tags": ["Nature", "Landscape", "Countryside"], "url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800"},
    {"title": "Portrait in Golden Light", "tags": ["Portrait", "People", "Artistic"], "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800"},
    {"title": "Street Musician", "tags": ["People", "Street", "Urban"], "url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800"},
    {"title": "Dancer in Motion", "tags": ["People", "Artistic", "Portrait"], "url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=800"},
    {"title": "Urban Architecture", "tags": ["Architecture", "Urban", "City"], "url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=800"},
    {"title": "Historic Cathedral", "tags": ["Architecture", "Historic", "City"], "url": "https://images.unsplash.com/photo-1438032005730-c779502df39b?w=800"},
    {"title": "Cherry Blossom Tunnel", "tags": ["Nature", "Spring", "Artistic"], "url": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=800"},
    {"title": "Wildflower Meadow", "tags": ["Nature", "Spring", "Landscape"], "url": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800"},
    {"title": "Foggy City Morning", "tags": ["City", "Urban", "Atmosphere"], "url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800"},
    {"title": "Night City Lights", "tags": ["City", "Night", "Urban"], "url": "https://images.unsplash.com/photo-1519500098989-cd6c6e5a31f3?w=800"},
    {"title": "Coastal Cliffs", "tags": ["Nature", "Ocean", "Landscape"], "url": "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=800"},
    {"title": "Lavender Fields", "tags": ["Nature", "Landscape", "Artistic"], "url": "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=800"},
    {"title": "Snowy Mountain Peak", "tags": ["Nature", "Mountains", "Winter"], "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800"},
    {"title": "Candid Street Portrait", "tags": ["People", "Street", "Portrait"], "url": "https://images.unsplash.com/photo-1504593811423-6dd665756598?w=800"},
    {"title": "Artist at Work", "tags": ["People", "Artistic", "Portrait"], "url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800"},
    {"title": "Bridge at Twilight", "tags": ["Architecture", "City", "Night"], "url": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800"},
    {"title": "Tropical Paradise", "tags": ["Nature", "Beach", "Tropical"], "url": "https://images.unsplash.com/photo-1509233725247-49e657c54213?w=800"},
    {"title": "Ethereal Lake", "tags": ["Nature", "Water", "Landscape"], "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800"},
    {"title": "Sunset Silhouette", "tags": ["Artistic", "Nature", "Sunset"], "url": "https://images.unsplash.com/photo-1518066000714-58c45f1a2c0a?w=800"},
    {"title": "Geometric Patterns", "tags": ["Architecture", "Modern", "Artistic"], "url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=800"},
    {"title": "Vintage Street Corner", "tags": ["Urban", "Street", "Architecture"], "url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800"},
    {"title": "Aurora Over Mountains", "tags": ["Nature", "Night", "Mountains"], "url": "https://images.unsplash.com/photo-1504333638930-c8787321eee0?w=800"},
    {"title": "Morning Dew Drops", "tags": ["Nature", "Macro", "Artistic"], "url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800"},
    {"title": "City Skyline Sunset", "tags": ["City", "Sunset", "Urban"], "url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800"},
    {"title": "Misty Waterfall", "tags": ["Nature", "Water", "Landscape"], "url": "https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=800"},
    {"title": "Street Art Mural", "tags": ["Street", "Urban", "Artistic"], "url": "https://images.unsplash.com/photo-1529686342540-1b43aec0df75?w=800"},
    {"title": "Ocean Waves Crashing", "tags": ["Nature", "Ocean", "Water"], "url": "https://images.unsplash.com/photo-1505228395891-9a51e7e86bf6?w=800"},
    {"title": "Autumn Forest Path", "tags": ["Nature", "Forest", "Landscape"], "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800"},
    {"title": "Minimalist Architecture", "tags": ["Architecture", "Modern", "Minimal"], "url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=800"},
    {"title": "Candid Joyful Laugh", "tags": ["People", "Portrait", "Artistic"], "url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800"},
    {"title": "Historic Bridge", "tags": ["Architecture", "Historic", "City"], "url": "https://images.unsplash.com/photo-1514924013411-cbf25faa35bb?w=800"},
    {"title": "Starry Night Sky", "tags": ["Nature", "Night", "Landscape"], "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"},
    {"title": "Urban Alleyway", "tags": ["Urban", "Street", "City"], "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800"},
    {"title": "Mountain Sunrise", "tags": ["Mountains", "Nature", "Sunrise"], "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800"},
    {"title": "Glass Building Reflection", "tags": ["Architecture", "Modern", "Urban"], "url": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=800"},
    {"title": "Calm Lake Sunset", "tags": ["Nature", "Water", "Sunset"], "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"},
    {"title": "Vintage Car Classic", "tags": ["Artistic", "Urban", "Vintage"], "url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800"},
    {"title": "Bamboo Forest", "tags": ["Nature", "Forest", "Artistic"], "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800"},
    {"title": "Rainy Street Reflections", "tags": ["Street", "Urban", "Night"], "url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800"},
    {"title": "Sunset Silhouette Beach", "tags": ["Sunset", "Beach", "Nature"], "url": "https://images.unsplash.com/photo-1509233725247-49e657c54213?w=800"},
]


class Command(BaseCommand):
    help = 'Seed the database with sample photos from Unsplash'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default='gallery_admin', help='Username for sample uploader')
        parser.add_argument('--max', type=int, default=0, help='Max photos to seed (0 = all)')

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['user']
        max_photos = options['max']

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('gallery123')
            user.save()
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

        tag_map = {}
        all_tag_names = set()
        for photo in PHOTO_DATA:
            all_tag_names.update(photo['tags'])

        for name in sorted(all_tag_names):
            tag, _ = Tag.objects.get_or_create(name=name)
            tag_map[name] = tag

        self.stdout.write(f'Tags ready: {len(tag_map)}')

        photos_to_process = PHOTO_DATA
        if max_photos > 0:
            photos_to_process = PHOTO_DATA[:max_photos]

        count = 0
        total = len(photos_to_process)

        for i, data in enumerate(photos_to_process):
            title = data['title']
            if Photo.objects.filter(title=title).exists():
                self.stdout.write(f'  [{i+1}/{total}] Skipping "{title}"')
                continue

            self.stdout.write(f'  [{i+1}/{total}] Downloading: {title}...', ending='')
            self.stdout.flush()
            try:
                req = urllib.request.Request(
                    data['url'],
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; PhotoGallery/1.0)'}
                )
                with urllib.request.urlopen(req, timeout=20) as response:
                    img_data = response.read()

                photo = Photo(
                    title=title,
                    description=f"Beautiful {title.lower()} photograph.",
                    uploaded_by=user,
                )
                photo.image.save(f"sample_{i+1}.jpg", ContentFile(img_data), save=True)
                for tag_name in data['tags']:
                    photo.tags.add(tag_map[tag_name])
                count += 1
                self.stdout.write(self.style.SUCCESS(f' {len(img_data)//1024}KB'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f' FAILED: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Seeded {count} photos (total in DB: {Photo.objects.count()})'
        ))
