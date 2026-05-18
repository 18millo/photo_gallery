from django.apps import AppConfig


class PhotoGalleryConfig(AppConfig):
    name = 'photo_gallery'

    def ready(self):
        import photo_gallery.models
