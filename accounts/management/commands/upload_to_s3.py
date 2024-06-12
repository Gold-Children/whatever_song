from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Upload local static files to S3'

    def handle(self, *args, **options):
        static_dir = settings.BASE_DIR / 'static'
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    file_name = os.path.relpath(file_path, static_dir)
                    default_storage.save(f'static/{file_name}', f)
        self.stdout.write(self.style.SUCCESS('Successfully uploaded static files to S3'))
