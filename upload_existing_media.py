# upload_existing_media.py
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traveling_project.settings")
django.setup()

from pathlib import Path
from django.conf import settings
import cloudinary.uploader
import cloudinary_storage.storage  # Cloudinary ko settings se configure karta hai
from travelingapp.models import Package, PackageGallery, Profile

if not settings.USE_CLOUDINARY:
    raise SystemExit("Pehle .env mein USE_CLOUDINARY=True karo")

names = set()
names |= {p.hero_image.name for p in Package.objects.exclude(hero_image="")}
names |= {g.image.name for g in PackageGallery.objects.exclude(image="")}
names |= {p.profile_picture.name for p in Profile.objects.exclude(profile_picture="").exclude(profile_picture__isnull=True)}

for name in sorted(names):
    local = Path(settings.MEDIA_ROOT) / name
    if not local.exists():
        print("MISSING:", name)
        continue
    public_id = "media/" + os.path.splitext(name)[0]
    r = cloudinary.uploader.upload(
        str(local), public_id=public_id, resource_type="image",
        overwrite=False, unique_filename=False, use_filename=False, tags="media",
    )
    print("OK", name, "->", r["public_id"])