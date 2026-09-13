from django.db import models


# Create your models here.
class Package(models.Model):
    package_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    hero_image = models.ImageField(upload_to="packages/")
    short_description = models.TextField()
    # title = models.CharField(max_length = 100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    title_with_duration = models.CharField(max_length = 100)
    package_duration = models.CharField(max_length=50)
    difficulty = models.CharField(max_length = 50)
    max_people = models.CharField(max_length=50)          # display text, e.g. "6-10" — unchanged
    total_seats = models.PositiveIntegerField(default=10)  # NEW — actual number used for seat-limit enforcement
    season = models.CharField(max_length = 50)
    food_stay = models.TextField()
    # travel_driver = models.TextField()
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default = False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.package_name

class Location(models.Model):
    region = models.CharField(max_length= 50)
    place = models.CharField(max_length = 50)
    altitude = models.CharField(max_length =200)
    base_point = models.CharField(max_length = 200)
    nearest_town = models.CharField(max_length = 200)
    package = models.OneToOneField(Package, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.package.package_name} - Location"
    
class Itineary(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="itineraries")
    day_number = models.IntegerField()
    day_title = models.CharField(max_length= 50)
    # day_discription = models.TextField()
    def __str__(self):
        return f"{self.package.package_name} - Day {self.day_number} ({self.day_title})"
    

class ItinearyPoint(models.Model):
    itinerary = models.ForeignKey(Itineary, on_delete=models.CASCADE, related_name="points")
    point = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.itinerary.package.package_name} - Day {self.itinerary.day_number}: {self.point}"


class TravelDriver(models.Model):
    package = models.OneToOneField(
        Package,
        on_delete=models.CASCADE,
        related_name="travel_driver"
    )

    vehicle = models.CharField(max_length=100)
    charge_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    total_days = models.PositiveIntegerField()
    driver_addon = models.CharField(max_length=100)

    @property
    def total_driver_charge(self):
        return self.charge_per_day * self.total_days

    def __str__(self):
        return self.package.package_name

from decimal import Decimal
class PricingBreakdown(models.Model):
    package = models.OneToOneField(
        Package, 
        on_delete=models.CASCADE, 
        related_name = "pricing"
    )
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    # our_commission = models.DecimalField(max_digits=8, decimal_places=2)
    driver_charges = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.package.package_name
    
    @property
    def our_commission(self):
        return self.base_cost * Decimal("20") / Decimal("100")

    @property
    def final_price(self):
        return self.base_cost + self.our_commission

    @property
    def total_with_driver(self):
        return self.final_price +self.driver_charges
    
class PackageGallery(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length = 100, blank=True)

    def __str__(self):
        return f"{self.package.package_name}-Gallery"


class Subscribers(models.Model):
    email = models.EmailField(unique=True)
    subscribe_on = models.DateTimeField(auto_now_add= True)



from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class User(AbstractUser):
    username = None  # remove — email hi login field hai
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # createsuperuser ke time email+password ke alawa kuch aur nahi maangega

    objects = CustomUserManager()

    def __str__(self):
        return self.email


from django.utils import timezone
import secrets

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name= "otps")

    otp = models.CharField(max_length = 6)
    created_at = models.DateTimeField(auto_now_add = True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() <= self.expires_at

    @staticmethod
    def generate_otp():
        return str(secrets.randbelow(900000)+ 100000)

    def __str__(self):
        return f"OTP for {self.user.email}"


class Booking(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings")
    name = models.CharField(max_length= 50)
    email = models.EmailField()
    phone = models.CharField(max_length= 20)
    package = models.ForeignKey(Package, default=1, on_delete=models.CASCADE)
    travel_date = models.DateField()
    travelers = models.PositiveIntegerField()
    special_request = models.TextField(blank=True, null=True )
    booking_date = models.DateTimeField(auto_now_add=True)
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="pending")
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f'{self.name} - ({self.package.package_name})'


    
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}'s profile"

    # @property ki wajah se hum method ko attribute ki tarah access kar sakte hai:
    @property
    def initials(self):
        first = self.user.first_name[:1] if self.user.first_name else ""
        last = self.user.last_name[:1] if self.user.last_name else ""
        return (first + last).upper() or self.user.email[:2].upper()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # """Har naye User ke saath ek khaali Profile bhi apne aap ban jaata hai —
    # isse kabhi 'Profile does not exist' wali error nahi aayegi."""
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)