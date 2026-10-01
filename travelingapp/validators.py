import os

from django.core.exceptions import ValidationError
from PIL import Image

MAX_UPLOAD_SIZE_MB = 2
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def validate_image_file(file):
    # 1) Size — huge files can fill storage / slow the site down
    if file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Image must be smaller than {MAX_UPLOAD_SIZE_MB} MB.")

    # 2) Extension whitelist
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Only JPG, PNG, or WebP images are allowed.")

    # 3) Real content check — a renamed .exe/.php/.html file passes the extension
    #    check above, but Pillow will refuse to open it as an actual image.
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError("This file isn't a valid image.")
    finally:
        file.seek(0)  # verify() moves the file pointer — reset so Django can still save it
    # Image.verify() file ko read karta hai, isliye pointer move ho sakta hai.
    # Phir Django ko file save karni hai.
    # Agar pointer end par hai, Django ko problematic/empty data mil sakta hai.
    # Isliye:
     
       # file.seek(0)
    # ka matlab:
        # File pointer ko wapas beginning par le jao.