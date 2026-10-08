from django.shortcuts import render, redirect, get_object_or_404
from .models import Subscribers, Booking, Package, User, EmailOTP, Profile, Review
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse


import json
from django.utils import timezone
from datetime import timedelta
# from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
# import smtplib

from django.db.models import Q, Avg, Sum

import requests

# from django.db.models import Sum

from django.db import transaction
import razorpay

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.mail import EmailMessage
# from weasyprint import HTML

from django.utils.dateparse import parse_date

from django_ratelimit.decorators import ratelimit

from .validators import validate_image_file
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)

def email_key(group, request):
    """Rate-limit key based on the email in the JSON body, not the IP —
    so an attacker can't dodge the limit just by switching IPs/VPNs while
    still targeting the same victim's inbox."""
    try:
        data = json.loads(request.body)
        return data.get("email", "").strip().lower() or "unknown"
    except Exception:
        return "unknown"


def _read_json(request):
    """Parse the JSON body safely. Returns a dict, or None if the body is not
    valid JSON / not a JSON object (so the view can answer 400 instead of crashing with a 500)."""
    try:
        data = json.loads(request.body)
    except ValueError:      # bad JSON and bad encoding both land here
        return None
    return data if isinstance(data, dict) else None


def _str(data, key):
    """data[key] as a string — anything that is not a string (number, list, null) becomes ''.
    Stops {"email": 123} from crashing .strip()."""
    value = data.get(key, "")
    return value if isinstance(value, str) else ""


BAD_JSON_RESPONSE = {"success": False, "error": "Invalid request."}


# Create your views here.
def view_home(request):
    return render(request, 'travelingapp/home.html')



def view_explore(request):
    packages = Package.objects.filter(is_active=True).annotate(
        avg_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True))
    )
                # Yahan Q istemal karne ki asli wajah ye hai: 
                # Django ka filter= parameter (jo Avg()/Sum()/Count() jaise aggregate functions ke andar hota hai) 
                # sirf Q object hi accept karta hai — ye ek syntax requirement hai Django ki taraf se, 
                # seedha filter=reviews__is_approved=True likhna Python-syntax error dega 
                # (keyword argument ke andar doosra = nahi chal sakta). 
                # Isliye condition ko Q(...) mein wrap karna zaroori hai, 
                # chahe wo ek hi condition ho, koi OR/AND na ho.
    destination = request.GET.get("destination", "").strip()
    if destination:
        packages = packages.filter(
            Q(package_name__icontains=destination) |
            Q(location__place__icontains=destination) |
            Q(location__region__icontains=destination)
        )

    season = request.GET.get("season", "").strip()
    if season:
        packages = packages.filter(season__icontains=season)

    difficulty = request.GET.get("difficulty", "").strip()
    if difficulty:
        packages = packages.filter(difficulty__iexact=difficulty)

    min_price = request.GET.get("min_price", "").strip()
    if min_price.isdigit():
        packages = packages.filter(price__gte=min_price)

    max_price = request.GET.get("max_price", "").strip()
    if max_price.isdigit():
        packages = packages.filter(price__lte=max_price)

    packages = packages.order_by("package_name")

    # Dropdown options built from whatever actually exists in the DB —
    # avoids "Moderate" vs "moderate" style mismatches with hardcoded lists.
    all_seasons = (
        Package.objects.filter(is_active=True)
        .exclude(season="").values_list("season", flat=True).distinct()
    )
    all_difficulties = (
        Package.objects.filter(is_active=True)
        .exclude(difficulty="").values_list("difficulty", flat=True).distinct()
    )

    return render(request, "travelingapp/explore-treks.html", {
        "packages": packages,
        "destination": destination,
        "season": season,
        "difficulty": difficulty,
        "min_price": min_price,
        "max_price": max_price,
        "all_seasons": all_seasons,
        "all_difficulties": all_difficulties,
    })
# Ab agar hum likhenge:
    # packages = Package.objects.all()
# To saare 10 packages website par dikh jayenge.
# Lekin agar likhege:
    # packages = Package.objects.filter(is_active=True)
# To sirf:
    # Kedarnath
    # Badrinath
# website par dikhenge.
# Baaki admin me rahenge, lekin users ko nahi dikhai denge.
# Ye production websites me bahut use hota hai

def view_destinations(request):
    return render(request, 'travelingapp/destinations.html')

def view_about(request):
    return render(request, 'travelingapp/about.html')




def view_subscribe(request):
    if request.method == "POST":

        # Get the email entered by the user from the form
        email = request.POST.get("email")

        # get_or_create() checks if the email already exists.
        # If it exists -> returns the existing object.
        # If it doesn't exist -> creates a new object.
        subscriber, created = Subscribers.objects.get_or_create(email=email)

        # 'created' is True only when a new subscriber is created.
        if created:
            messages.success(request, "Subscribe Successfully", extra_tags="newsletter")

        # 'created' is False when the email already exists.
        else:
            messages.warning(request, "You Already Subscribe", extra_tags="newsletter")

    # Redirect back to the contact section of the home page
    return redirect(reverse("home") + "#contact")

# ============================================================================
# Why do we write "subscriber, created"?
# ============================================================================

# get_or_create() returns TWO values together.
#
# Example:
#
#     (<Subscriber Object>, True)
#
# or
#
#     (<Subscriber Object>, False)
#
# Since two values are returned, we store them in two variables:
#
#     subscriber, created = Subscribers.objects.get_or_create(email=email)
#
# subscriber -> Stores the Subscriber object.
# created    -> Stores True or False.

# agar m sirf ek hi vaiable likhta hu
#---> created = Subscribers.objects.get_or_create(...)

# To created ke andar actually ye aa raha hai:
# (<Subscriber Object>, True)
# ya
# (<Subscriber Object>, False)

# Ye tuple hai.
# Python me non-empty tuple hamesha True hota hai.

# Isliye:
# if created:

# ➡️ Hamesha True chalega.

# ============================================================================
# What is a Tuple?
# ============================================================================

# A tuple is a collection that stores multiple values together.
#
# Example:
#
#     data = ("Mahendra", 20)
#
# Here:
#     "Mahendra" -> First value
#     20         -> Second value
#
# We can unpack the tuple like this:
#
#     name, age = data
#
# Now:
#     name = "Mahendra"
#     age  = 20
#
# In the same way:
#
#     subscriber, created = Subscribers.objects.get_or_create(email=email)
#
# subscriber receives the first value (Subscriber Object).
# created receives the second value (True or False).





# from django.db.models import Avg
def view_package_detail(request, slug):
    package = get_object_or_404(Package, slug=slug, is_active=True)

    related_packages = Package.objects.filter(
        is_active=True,
        location__region=package.location.region
    ).exclude(id=package.id)[:4]

    approved_reviews = package.reviews.filter(is_approved=True).order_by("-created_at")
    average_rating = approved_reviews.aggregate(avg=Avg("rating"))["avg"]

    d1 = {"package":package,
            "food_items": package.food_stay.split("\n"),
            "related_packages": related_packages,
            "reviews": approved_reviews,
            "average_rating": average_rating,
            "review_count": approved_reviews.count(),
        }

    return render(request, 'travelingapp/traveling-view-detail.html', d1)




def view_searchDestinations(request):

    keyword = request.GET.get("q", "")

    packages = Package.objects.filter(
        is_active = True,
        package_name__icontains=keyword
    )[:5]

    data = []

    for package in packages:
        data.append({
            "package_name": package.package_name,
            "slug": package.slug,
        })

    return JsonResponse(data, safe=False)

    # Django ka JsonResponse() default mein dictionary (dict) expect karta hai.
    # but hum list bhej rahe h isliye safe = False lagaya h 
    # it means django says m abhi list bhej raha hu dictionary nahi ishhe bhi JsonResponse bana krr bhej do

    # safe=False data ko safe/unsafe nahi bana raha. Ye bas Django ki default restriction ko allow karta hai ki top-level JSON data list bhi ho sakta hai.

def _send_otp_email(user):
    EmailOTP.objects.filter(user = user).delete()
    otp_code = EmailOTP.generate_otp() 
    EmailOTP.objects.create(
        user = user,
        otp = otp_code,
        expires_at = timezone.now() + timedelta(minutes = 10),
    )
    try: 
        send_mail(
            subject="Your DevBhumi Horizons verification code",
            message=f"Your OTP is {otp_code}. It expires in 10 minutes.",
            from_email = settings.DEFAULT_FROM_EMAIL,    # Kis email se bhejna hai
            recipient_list=[user.email]                  # Kisko bhejna hai
        )
        return True
    # except (smtplib.SMTPException, BadHeaderError):
    #     return False
    except Exception:
        # SMTP error, Brevo API error (401/429/5xx), timeout, blocked network...
        # print("OTP email failed:", type(e).__name__, "-", str(e)[:200])
        logger.exception("OTP email could not be sent")
        return False

@ratelimit(key='ip', rate='5/h', block= False )
@require_POST
def view_signup(request):
    if getattr(request, 'limited', False):
        return JsonResponse({
            "success": False, "error": "Too many signup attempts. Please try again in a while."
        }, status=429)
    # if request.method == "POST":
    # data = json.loads(request.body)
    data = _read_json(request)
    if data is None:
        return JsonResponse(BAD_JSON_RESPONSE, status=400)

    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirmPassword", "")

    if not first_name or not last_name or not email or not password:
        return JsonResponse({"success": False, "error": "All fields are required"}, status= 400)
            
    if len(password) <8:
        return JsonResponse({"success": False, "error": "Password must be at least 8 characters."}, status = 400)

    if password != confirm_password:
        return JsonResponse({"success": False, "error": "Password do not match"}, status = 400)

    # if User.objects.filter(email = email).exists():
    #     return JsonResponse({"success": False, "error": "An account with this email already exists."}, status = 400)

    existing  = User.objects.filter(email = email).first()

    # Already verified user
    if existing and existing.is_active:
        return JsonResponse({"success": False, "error": "An account with this email already exists"}, status= 400)

    # Existing but unverified user
    if existing and not existing.is_active:
        existing.first_name = first_name
        existing.last_name = last_name
        existing.set_password(password)
        existing.save()

        user = existing
    else:
        user = User.objects.create_user(
            first_name = first_name, 
            last_name = last_name,
            email = email,
            password = password,
            # confirm_password = confirm_password
        )

        user.is_active = False
        user.save()

    # _send_otp_email(user)
    # return JsonResponse({"success": True, "message": "OTP sent to your email.", "email": email})

    if not _send_otp_email(user):
        if not existing:
            user.delete()  # rollback, taaki galat-email se ghost accounts na banein
        return JsonResponse({"success": False, "error": "Couldn't send OTP — check the email address."}, status=400)

    return JsonResponse({"success": True, "message": "OTP sent to your email.", "email": email})

# ---------- Verify OTP ----------
@ratelimit(key=email_key, rate='6/10m', block=False)
@require_POST
def view_verify_otp(request):

    if getattr(request, 'limited', False):
        return JsonResponse({
            "success": False, "error": "Too many signup attempts. Please try again in a while."
        }, status=429)
    
    # data = json.loads(request.body)
    data = _read_json(request)
    if data is None:
        return JsonResponse(BAD_JSON_RESPONSE, status = 400)

    email = data.get("email","").strip().lower()
    otp_code = data.get("otp", "").strip()

    try:
        user = User.objects.get(
            email = email,
            is_active = False
        )
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Invalid request."}, status=400)

    otp_obj = EmailOTP.objects.filter(
        user = user,
        otp = otp_code,
    ).order_by("-created_at").first()

    if not otp_obj:
        return JsonResponse({"success": False, "error": "Incorrect OTP."}, status= 400)

    if not otp_obj.is_valid():
        return JsonResponse({"success": False, "error": "OTP expired. Please request a new one."}, status=400)

    user.is_active = True
    user.save()
    EmailOTP.objects.filter(user=user).delete()

    login(request, user)  # verify hote hi auto-login

    return JsonResponse({"success": True, "message": "Account verified successfully."})

@ratelimit(key=email_key, rate='3/10m', block=False)
@require_POST
def view_resend_otp(request):

    if getattr(request, 'limited', False):
        return JsonResponse({
            "success": False, "error": "Too many resend requests. Please wait a few minutes and try again."
        }, status=429)

    # data = json.loads(request.body)
    data = _read_json(request)
    if data is None:
        return JsonResponse(BAD_JSON_RESPONSE, status=400)
    
    email = data.get("email", "").strip().lower()

    try: 
        user = User.objects.get(
            email = email,
            is_active = False
        )
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Invalid request."}, status= 400)

    _send_otp_email(user)
    return JsonResponse({"success": True, "message": "OTP resent."})

# ---------- Login ----------
@ratelimit(key='ip', rate='10/15m', block=False)
@require_POST
def view_login(request):

    if getattr(request, 'limited', False):
        return JsonResponse({
            "success": False, "error": "Too many requests. Please wait a few minutes and try again."
        }, status=429)
    
    # data = json.loads(request.body)
    data = _read_json(request)
    if data is None:
        return JsonResponse(BAD_JSON_RESPONSE, status= 400)
    
    email = data.get("email", "").strip().lower()
    password = data.get("password","")

    user = authenticate(request, username = email, password = password)

    if not user:
        return JsonResponse({"success": False, "error": "Invalid Username or Password"}, status= 400)

    if not user.is_active:
        return JsonResponse({"success": False, "error": "Please verify your email first.", "needs_otp": True, "email": email}, status=403)

    login(request, user)
    return JsonResponse({"success": True, "message": "Logged in successfully."})

# @require_POST
# def view_login(request):
#     data = json.loads(request.body)
#     email = data.get("email", "").strip().lower()
#     password = data.get("password", "")

#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return JsonResponse({"success": False, "error": "Invalid email or password."}, status=400)

#     # check_password works regardless of is_active — authenticate() would have
#     # silently rejected inactive users here and always said "invalid credentials"
#     if not user.check_password(password):
#         return JsonResponse({"success": False, "error": "Invalid email or password."}, status=400)

#     if not user.is_active:
#         _send_otp_email(user)  # resend right away so they can verify immediately
#         return JsonResponse({
#             "success": False,
#             "needs_otp": True,
#             "email": email,
#             "error": "Please verify your email first. We've sent you a new OTP.",
#         }, status=403)

#     login(request, user)
#     return JsonResponse({"success": True, "message": "Logged in successfully."})

@require_POST
def view_logout(request):
    logout(request)
    return JsonResponse({"success": True})



# from .validators import validate_image_file
# from django.core.exceptions import ValidationError

def view_profile(request):
    if not request.user.is_authenticated:
        return redirect("home")

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        if not first_name or not last_name:
            messages.error(request, "First and last name can't be empty.")
            return redirect("profile")

        # Validate the photo FIRST — before saving anything — so a bad upload
        # doesn't leave the rest of the form half-applied.
        uploaded = request.FILES.get("profile_picture")
        if uploaded:
            try:
                validate_image_file(uploaded)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return redirect("profile")

        dob_raw = request.POST.get("date_of_birth")
        dob = None
        if dob_raw:
            try:
                dob = parse_date(dob_raw)
            except ValueError:
                dob = None
            if dob is None or dob>timezone.now().date():
                messages.error(request, "Please enter a valid date of birth.")
                return redirect("profile")
                
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        profile.phone = request.POST.get("phone", "").strip()
        profile.address = request.POST.get("address", "").strip()
        profile.date_of_birth = dob     # a real date, or None if the field was left empty

        # if request.FILES.get("profile_picture"):
        #     profile.profile_picture = request.FILES["profile_picture"]

        if uploaded:
            # Delete the previous photo file so replaced images don't pile up in storage
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)
            profile.profile_picture = uploaded
        profile.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")

    return render(request, "travelingapp/profile.html", {"profile": profile})

def view_my_bookings(request):
    if not request.user.is_authenticated:
        return redirect("home")

    bookings = request.user.bookings.all().order_by("-booking_date")
    return render(request, "travelingapp/my_bookings.html", {
        "bookings": bookings,
        "today": timezone.now().date(),
    })



# import requests

@require_POST
def view_google_login(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid request."}, status=400)
    access_token = data.get("access_token", "") if isinstance(data, dict) else ""

    if not access_token or not isinstance(access_token, str):
        return JsonResponse({"success": False, "error": "Missing Google token."}, status=400)

    try:
        # Step 1: kis app ke liye ye token bana? Hamare liye hona chahiye.
        token_resp = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"access_token": access_token},
            timeout=10,
        )
        if token_resp.status_code != 200:
            return JsonResponse({"success": False, "error": "Could not verify Google account."}, status=400)
        token_info = token_resp.json()
        if token_info.get("aud") != settings.GOOGLE_CLIENT_ID:
            logger.warning("Google login rejected: token was issued to a different app")
            return JsonResponse({"success": False, "error": "Could not verify Google account."}, status=400)

        # Step 2: Google se pucho token kiska hai.
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except (requests.RequestException, ValueError):
        logger.exception("Google token verification failed")
        return JsonResponse({"success": False, "error": "Could not reach Google. Please try again."}, status=502)

    if resp.status_code != 200:
        return JsonResponse({"success": False, "error": "Could not verify Google account."}, status=400)


    info = resp.json()
    email = (info.get("email") or "").strip().lower()
    email_verified = info.get("email_verified", False)
    first_name = info.get("given_name") or ""
    last_name = info.get("family_name") or ""

    if not email or not email_verified:
        return JsonResponse({"success": False, "error": "Google account email isn't verified."}, status=400)

    user = User.objects.filter(email=email).first()

    if user:
        # Google has just proven this person owns the email — safe to activate
        # even a stuck/unverified account from an earlier manual signup attempt.
        changed = False
        if not user.is_active:
            user.is_active = True
            changed = True
        if not user.first_name and first_name:
            user.first_name = first_name
            changed = True
        if not user.last_name and last_name:
            user.last_name = last_name
            changed = True
        if changed:
            user.save()
    else:
        user = User.objects.create_user(
            email=email,
            password=None,  # no password — this account only ever logs in via Google
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = True
        user.save()

    login(request, user)
    return JsonResponse({"success": True, "message": "Logged in with Google."})


@ratelimit(key=email_key, rate='3/10m', block=False)
@require_POST
def view_forgot_password(request):

    if getattr(request, 'limited', False):
        return JsonResponse({
            "success": False, "error": "Too many requests. Please wait a few minutes and try again."
        }, status=429)
    
    # data = json.loads(request.body)
    data = _read_json(request)
    if data is None:
        return JsonResponse(BAD_JSON_RESPONSE, status=400)
    
    email = data.get("email", "").strip().lower()

    if not email:
        return JsonResponse({"success": False, "error": "Email is required."}, status=400)

    user = User.objects.filter(email=email, is_active=True).first()

    if not user:
        return JsonResponse({"success": False, "error": "No account found with this email."}, status=400)

    if not _send_otp_email(user):
        return JsonResponse({"success": False, "error": "Couldn't send reset code — check the email address."}, status=400)

    return JsonResponse({"success": True, "message": "Reset code sent.", "email": email})

@ratelimit(key=email_key, rate='6/10m', block=False)
@require_POST
def view_reset_password(request):

    if getattr(request, 'limited', False):
        return JsonResponse({
            "success": False, "error": "Too many requests. Please wait a few minutes and try again."
        }, status=429)
    
    # data = json.loads(request.body)
    data = _read_json(request)
    if data is None:
        return JsonResponse(BAD_JSON_RESPONSE, status=400)
    
    email = data.get("email", "").strip().lower()
    otp_code = data.get("otp", "").strip()
    new_password = data.get("new_password", "")
    confirm_new_password = data.get("confirm_new_password", "")

    if not email or not otp_code or not new_password:
        return JsonResponse({"success": False, "error": "All fields are required."}, status=400)

    if new_password != confirm_new_password:
        return JsonResponse({"success": False, "error": "Passwords do not match."}, status=400)

    if len(new_password) < 8:
        return JsonResponse({"success": False, "error": "Password must be at least 8 characters."}, status=400)

    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "Invalid request."}, status=400)

    otp_obj = EmailOTP.objects.filter(user=user, otp=otp_code).order_by("-created_at").first()

    if not otp_obj:
        return JsonResponse({"success": False, "error": "Incorrect OTP."}, status=400)

    if not otp_obj.is_valid():
        return JsonResponse({"success": False, "error": "OTP expired. Please request a new one."}, status=400)

    user.set_password(new_password)
    user.save()
    EmailOTP.objects.filter(user=user).delete()

    login(request, user)  # fresh password just proven via OTP — safe to log them straight in

    return JsonResponse({"success": True, "message": "Password reset successfully."})


# from django.db.models import Sum
@ratelimit(key='user', rate='5/h', block=False)
def view_booking(request):
    if request.method == "POST":

        # getattr() is a Python built-in function used to get an attribute from an object.
        if getattr(request, 'limited', False):  # Get the value of 'limited' from the request object.
                                                # If 'limited' does not exist, return False instead of raising an error.
            messages.error(request, "Too many booking attempts. Please try again in a while.")
            return redirect("booking")


        # Server-side login enforcement — matches the frontend's
        # data-requires-auth gate, so even a bypassed/direct POST can't
        # sneak past it.
        if not request.user.is_authenticated:
            messages.error(request, "Please login to complete your booking.")
            return redirect("home")

        # Demo-safety cap — one account can only have this many bookings
        # "active" (pending or paid) at once. This is the real fix for
        # someone spam-creating bookings — rate-limiting alone only slows
        # down login/signup, it doesn't cap what a logged-in user can do.
        # MAX_ACTIVE_BOOKINGS_PER_USER = 5

        # active_booking_count = Booking.objects.filter(
        #     user= request.user, 
        #     payment_status__in = ["pending", "paid"]
        # ).count()

        # if active_booking_count >= MAX_ACTIVE_BOOKINGS_PER_USER:
        #     messages.error(request,
        #         f"You can have up to {MAX_ACTIVE_BOOKINGS_PER_USER} active bookings at a time. "
        #         f"Please complete payment or cancel an existing booking before creating a new one."
        #     )
        #     return redirect("my_bookings")

        
        name = request.POST.get("name")
        email = request.user.email  # always the account email — never trust the form for this
        phone = request.POST.get("phone")
        travel_date = request.POST.get("travel_date")
        travelers = request.POST.get("total_travelers")
        special_request = request.POST.get("request")

        if not name:
            name = f"{request.user.first_name} {request.user.last_name}".strip()

        if not name:
            messages.error(request, "Name is required")
            return redirect("booking")

        if not phone:
            messages.error(request, "Phone number is required.")
            return redirect("booking")
        
        package = get_object_or_404(Package, slug=request.POST.get("package_slug"), is_active=True)

        # Travel date must be one of the package's admin-approved, still-active,
        # not-in-the-past departure dates — never a free-typed/tampered value.
        if not travel_date:
            messages.error(request, "Please select a travel date.")
            return redirect("booking")
 
        valid_date = package.departure_dates.filter(
            date=travel_date, is_active=True, date__gte=timezone.now().date() 
        ).exists()                                     
 
        if not valid_date:
            messages.error(request, "Please select a valid, available travel date for this package.")
            return redirect("booking")

        # Safe int conversion — travelers_raw could be "", None, or garbage
        # (empty field, tampered request, etc.) — int() alone would crash.
        try:
            travelers_requested = int(travelers)
            if travelers_requested < 1:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid number of travelers.")
            return redirect("booking")


        # 1) Duplicate-booking check FIRST — resume/redirect before touching seat counts,
        #    so a user's own pending booking never gets blocked by its own seat-hold.
        existing_booking = Booking.objects.filter(
            user=request.user,
            package=package,
            travel_date=travel_date,
            payment_status__in=["pending", "paid"],
        ).order_by("-booking_date").first()

        if existing_booking:
            if existing_booking.payment_status == "paid":
                messages.info(request, "You've already booked this package for this date. Check My Bookings for details.")
                return redirect("my_bookings")
            else:
                messages.info(request, "You already have a pending booking for this package on this date — complete the payment to confirm it.")
                return redirect("payment", booking_id=existing_booking.id)

        # 2) Seat-limit check — only reached for genuinely new bookings now.
        seats_taken = Booking.objects.filter(
            package=package,
            travel_date=travel_date,
            payment_status__in=["pending", "paid"],
        ).aggregate(total=Sum("travelers"))["total"] or 0

        seats_left = package.total_seats - seats_taken

        if seats_left <= 0:
            messages.error(request, f"Sorry, {package.package_name} is fully booked for {travel_date}. Please choose a different date.")
            return redirect("booking")

        if travelers_requested > seats_left:
            messages.error(request, f"Only {seats_left} seat(s) left for {package.package_name} on {travel_date}. Please reduce travelers or pick another date.")
            return redirect("booking")

        booking = Booking.objects.create(
            name=name,
            email=email,
            phone=phone,
            travel_date=travel_date,
            travelers=travelers_requested,  # validated int, not the raw POST string
            package=package,
            special_request=special_request,
            user=request.user,
        )

        send_admin_pending_booking_notification(booking)

        return redirect("payment", booking_id=booking.id)

    package = Package.objects.filter(is_active = True)

    dates_by_package = {}
    for pkg in package:
        available = pkg.departure_dates.filter(
            is_active=True, date__gte=timezone.now().date() 
        ).order_by("date")
        dates_by_package[pkg.slug] = [d.date.isoformat() for d in available]

    return render(request, "travelingapp/booking.html", {
        "packages": package,
        "name": request.GET.get("name"),
        "email": request.GET.get("email"),
        "travelers": request.GET.get("total_travelers", "1"),
        "special": request.GET.get("request"),
        "package_slug": request.GET.get("package_slug"),
        "dates_json": json.dumps(dates_by_package),
    })


# from django.db import transaction
# import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

BOOKING_ADVANCE_AMOUNT = 1000  # rupees — fixed deposit to confirm a booking

def view_payment(request, booking_id):
    # User must be logged in before making a payment.
    if not request.user.is_authenticated:
        messages.error(request, "Please login to continue.")
        return redirect("home")

    # Only allow the logged-in user to access their own booking.
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    # Paid bookings should not be paid again.
    if booking.payment_status == "paid":
        messages.info(request, "This booking is already paid.")
        return redirect("my_bookings")

    # Cancelled bookings cannot be paid.
    if booking.payment_status == "cancelled":
        messages.info(request, "This booking was cancelled, so it can't be paid.")
        return redirect("my_bookings")

    # Razorpay expects the amount in paise.
    amount_paise = BOOKING_ADVANCE_AMOUNT * 100

    # Reuse the existing Razorpay order if one already exists.
    # This prevents a new order from being created on every page refresh.
    order_id = booking.razorpay_order_id

    if not order_id:
        order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"booking_{booking.id}",
            "payment_capture": 1,
            "notes": {
                "booking_id": str(booking.id)
            },
        })

        # Save the Razorpay order ID with this booking.
        order_id = order["id"]

        booking.razorpay_order_id = order_id
        booking.save(update_fields=["razorpay_order_id"])

    # Get the package's total price.
    # Use the detailed pricing if available.
    total_price = booking.package.price

    if hasattr(booking.package, "pricing"):
        total_price = booking.package.pricing.final_price

    # Calculate the amount that will remain after the advance payment.
    remaining_amount = total_price - BOOKING_ADVANCE_AMOUNT

    return render(request, "travelingapp/payment.html", {
        "booking": booking,
        "order_id": order_id,
        "amount_paise": amount_paise,
        "amount_rupees": BOOKING_ADVANCE_AMOUNT,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "total_price": total_price,
        "remaining_amount": remaining_amount,
    })


@require_POST
def verify_payment(request):
    # User must be logged in to verify a payment.
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "error": "Please log in again to confirm your payment."
            },
            status=401
        )

    # Read and validate the JSON request.
    try:
        data = json.loads(request.body)
        booking_id = int(data.get("booking_id"))
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({"success": False,"error": "Invalid payment request."},status=400 )

    # Get the payment details returned by Razorpay.
    params_dict = {
        "razorpay_order_id": str(data.get("razorpay_order_id", "")),
        "razorpay_payment_id": str(data.get("razorpay_payment_id", "")),
        "razorpay_signature": str(data.get("razorpay_signature", "")),
    }

    # All three Razorpay values are required.
    if not all(params_dict.values()):
        return JsonResponse({"success": False, "error": "Invalid payment request."}, status=400)

    # Verify that the payment response was genuinely signed by Razorpay.
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"success": False, "error": "Payment verification failed."}, status=400)


    # Lock the booking while updating its payment status.
    # This prevents two requests from updating the same booking at the same time.
    with transaction.atomic():
        # Make sure:
        # 1. The booking exists.
        # 2. The booking belongs to the logged-in user.
        # 3. The Razorpay order belongs to this booking.
        booking = (Booking.objects.select_for_update().filter(
                id=booking_id,
                user=request.user,
                razorpay_order_id=params_dict["razorpay_order_id"]
            )
            .first()
        )

        # The payment does not belong to this booking.
        if booking is None:
            return JsonResponse({"success": False, "error": "This payment doesn't match your booking."}, status=400)

        # Handle duplicate payment verification requests.
        if booking.payment_status == "paid":

            # Same payment sent again.
            if booking.razorpay_payment_id == params_dict["razorpay_payment_id"]:
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Payment already confirmed."
                    }
                )

            # A different payment was received for an already-paid booking.
            # print("DUPLICATE PAYMENT on booking", booking.id, "-", params_dict["razorpay_payment_id"])
            logger.error("Duplicate payment on booking %s (payment id %s)", booking.id, params_dict["razorpay_payment_id"])
            return JsonResponse({"success": False, "error": "This booking is already paid. If you were charged twice, please contact us with your payment ID."}, status=409)

        # Cancelled bookings cannot receive payments.
        if booking.payment_status == "cancelled":
            return JsonResponse({"success": False, "error": "This booking was cancelled, so the payment can't be applied. Please contact us."}, status=400)

        # Mark the booking as paid.
        booking.payment_status = "paid"

        # Save the Razorpay payment ID for future reference.
        booking.razorpay_payment_id = params_dict["razorpay_payment_id"]

        booking.save(
            update_fields=[
                "payment_status",
                "razorpay_payment_id"
            ]
        )

    # Send emails after the database transaction is complete.
    # so the database row isn't locked while we wait on email.
    send_invoice_email(booking)
    send_admin_payment_confirmed_notification(booking)

    return JsonResponse({"success": True,"message": "Payment verified successfully."})



# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from django.core.mail import EmailMessage
# from weasyprint import HTML


def _invoice_context(booking):
    total_price = booking.package.price
    if hasattr(booking.package, "pricing"):
        total_price = booking.package.pricing.final_price

    amount_paid = BOOKING_ADVANCE_AMOUNT
    balance_due = total_price - amount_paid

    return {
        "booking": booking,
        "total_price": total_price,
        "amount_paid": amount_paid,
        "balance_due": balance_due,
    }


def generate_invoice_pdf_bytes(booking):
    """Renders the invoice template to PDF bytes — used by both the
    download button and the auto-emailed invoice, so there's one source
    of truth for what an invoice looks like."""

    # Imported here, not at the top of the file: WeasyPrint needs system libraries
    # (Pango). If the server doesn't have them, a top-level import would crash this
    # whole module at startup and take the entire site down. Here, only PDF
    # generation fails — and send_invoice_email / download_invoice handle that.
    from weasyprint import HTML
    
    context = _invoice_context(booking)
    context["for_pdf"] = True

    html = render_to_string("travelingapp/invoice.html", context)
    return HTML(string=html).write_pdf()


def send_invoice_email(booking):

    """Best-effort — if this fails, the payment itself must NOT be treated
    as failed, since it already succeeded and was verified."""
    try:
        pdf_bytes = generate_invoice_pdf_bytes(booking)
        filename = f"Invoice_DBH-{booking.id:05d}.pdf"

        email = EmailMessage(
            subject=f"Your DevBhumi Horizons Invoice — DBH-{booking.id:05d}",
            body=(
                f"Hi {booking.name},\n\n"
                f"Thank you for booking {booking.package.package_name} with DevBhumi Horizons!\n"
                f"We've received your advance payment. Your invoice is attached to this email.\n\n"
                f"See you in the mountains!\n"
                f"— DevBhumi Horizons"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        email.attach(filename, pdf_bytes, "application/pdf")
        email.send()
        return True
    except Exception:
        # print("Invoice email failed:", type(e).__name__, "-", str(e))
        logger.exception("Invoice email failed for booking %s", booking.id)
        return False


def _can_view_invoice(request, booking):
    # Only the booking's owner (or site staff) can see an invoice. Old guest bookings
    # (no user attached) used to be open to anyone, but booking ids are 1, 2, 3...
    # so anyone could walk through them and read other people's name/phone/email.
    if not request.user.is_authenticated:
        return False
    return booking.user_id == request.user.id or request.user.is_staff


def view_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.payment_status != "paid":
        messages.error(request, "Invoice is only available after payment is completed.")
        return redirect("my_bookings")

    if not _can_view_invoice(request, booking):
        return redirect("home")

    context = _invoice_context(booking)
    context["for_pdf"] = False

    return render(request, "travelingapp/invoice.html", context)


def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.payment_status != "paid":
        messages.error(request, "Invoice is only available after payment is completed.")
        return redirect("my_bookings")

    if not _can_view_invoice(request, booking):
        return redirect("home")

    try:
        pdf_bytes = generate_invoice_pdf_bytes(booking)
    except Exception:
        logger.exception("Invoice PDF could not be generated for booking %s", booking.id)
        messages.error(request, "Couldn't generate the invoice PDF right now. Please try again later.")
        return redirect("my_bookings")

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_DBH-{booking.id:05d}.pdf"'
    
    return response



CANCELLATION_WINDOW_DAYS = 3       # cancel this many days (or more) before travel_date to qualify for a refund
CANCELLATION_REFUND_PERCENT = 50   # % of the advance refunded if cancelled within the window

def send_cancellation_email(booking, refund_amount):
    try:
        if refund_amount>0:
            body=(
                f"Hi {booking.name},\n\n"
                f"Your booking for {booking.package.package_name} ({booking.travel_date}) has been cancelled.\n"
                f"A refund of ₹{refund_amount:.0f} will be credited to your original payment method within 5-7 business days.\n\n"
                f"We hope to see you on another trip soon!\n"
                f"— DevBhumi Horizons"
            )
        else:
            body=(
                f"Hi {booking.name},\n\n"
                f"Your booking for {booking.package.package_name} ({booking.travel_date}) has been cancelled.\n"
                f"As per our cancellation policy, no refund is applicable for this cancellation.\n\n"
                f"We hope to see you on another trip soon!\n"
                f"— DevBhumi Horizons"
            )
            

        email = EmailMessage(
            subject =f"Booking Cancelled — DBH-{booking.id:05d}",
            body = body,
            from_email = settings.DEFAULT_FROM_EMAIL,
            to = [booking.email]

        )
        email.send()
        return True
        
    except Exception:
        # print("Cancellation email failed:", type(e).__name__, "-", str(e))
        logger.exception("Cancellation email failed for booking %s", booking.id)
        return False


@require_POST
def cancel_booking(request, booking_id):

    # Lock the booking row for the whole cancel (same idea as verify_payment).
    # Without the lock, a double-click / two tabs could run this twice at once:
    # both requests would see "paid" and BOTH would send a refund to Razorpay.
    # With the lock, the second request waits, then sees "cancelled" and stops.

    # transaction.atomic() 
        # Multiple database operations ko ek single transaction ke andar run karta hai.
        # Agar transaction ke beech mein koi error aaye, to saare database changes rollback ho jaate hain.
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update(), id=booking_id)
            # select_for_update():
            # Selected database row ko lock karta hai jab tak transaction complete nahi hoti.
            #
            # Ye concurrent requests se bachne ke liye use hota hai.
            # Example: Agar do requests same booking ko ek hi time par process karein,
            # to ek request row ko lock karegi aur doosri request ko wait karna padega.
            #
            # Isse dono requests ek hi booking ko simultaneously modify nahi kar paati.

        if not request.user.is_authenticated or booking.user_id != request.user.id:
            messages.error(request, "You can't cancel this booking.")
            return redirect("my_bookings")

        if booking.payment_status == "cancelled":
            messages.info(request, "This booking is already cancelled.")
            return redirect("my_bookings")

        if booking.travel_date < timezone.now().date():
            messages.error(request, "This trip has already passed — it can't be cancelled.")
            return redirect("my_bookings")

        days_before_trip = (booking.travel_date - timezone.now().date()).days
        refund_amount = 0

        if booking.payment_status == "paid":
            if days_before_trip >= CANCELLATION_WINDOW_DAYS:
                refund_amount = (BOOKING_ADVANCE_AMOUNT * CANCELLATION_REFUND_PERCENT) / 100

                try:
                    refund = razorpay_client.payment.refund(booking.razorpay_payment_id, {
                        "amount": int(refund_amount * 100),  # Razorpay expects paise
                    })
                    booking.razorpay_refund_id = refund.get("id", "")
                except Exception:
                    # print("Refund failed:", type(e).__name__, "-", str(e))
                    logger.exception("Razorpay refund failed for booking %s", booking.id)
                    messages.error(request, "Couldn't process the refund — please contact support to cancel this booking.")
                    return redirect("my_bookings")

        booking.payment_status = "cancelled"
        booking.cancelled_at = timezone.now()
        booking.refund_amount = refund_amount
        booking.save()

    # Email AFTER the transaction, so the row isn't locked while we wait on the mail server.
    send_cancellation_email(booking, refund_amount)

    if refund_amount > 0:
        messages.success(request, f"Booking cancelled. ₹{refund_amount:.0f} will be refunded to your original payment method within 5-7 business days.")
    else:
        messages.success(request, "Booking cancelled. No refund is applicable as per our cancellation policy.")

    return redirect("my_bookings")



def send_admin_pending_booking_notification(booking):
    """Best-effort — must never block the customer's booking flow.
    Sent to DEFAULT_FROM_EMAIL — same inbox used to send everything else."""
    try:
        send_mail(
            subject=f"New booking received — {booking.package.package_name}",
            message=(
                f"A new booking just came in.\n\n"
                f"Name: {booking.name}\n"
                f"Email: {booking.email}\n"
                f"Phone: {booking.phone}\n"
                f"Package: {booking.package.package_name}\n"
                f"Travel Date: {booking.travel_date}\n"
                f"Travelers: {booking.travelers}\n"
                f"Special Request: {booking.special_request or '-'}\n"
                f"Booking ID: {booking.id}\n\n"
                f"Status: Pending payment — advance not yet paid."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        return True
    except Exception:
        # print("Admin notification email failed:", type(e).__name__, "-", str(e))
        logger.exception("Admin notification email failed for booking %s", booking.id)
        return False


def send_admin_payment_confirmed_notification(booking):
    """Best-effort — fires only when payment actually succeeds."""
    try:
        send_mail(
            subject=f"Advance payment received — {booking.package.package_name}",
            message=(
                f"Advance payment has been received for this booking.\n\n"
                f"Name: {booking.name}\n"
                f"Email: {booking.email}\n"
                f"Phone: {booking.phone}\n"
                f"Package: {booking.package.package_name}\n"
                f"Travel Date: {booking.travel_date}\n"
                f"Travelers: {booking.travelers}\n"
                f"Special Request: {booking.special_request or '-'}\n"
                f"Booking ID: {booking.id}\n"
                f"Payment ID: {booking.razorpay_payment_id}\n"
                f"Amount Paid: ₹{BOOKING_ADVANCE_AMOUNT}\n\n"
                f"Status: PAID — advance confirmed."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        return True
    except Exception:
        # print("Admin payment-confirmed email failed:", type(e).__name__, "-", str(e))
        logger.exception("Admin payment-confirmed email failed for booking %s", booking.id)
                        # %s ek placeholder hai.
                        # yaha %s ki jagah booking.id ki value aa jayegi
        return False


@require_POST
def view_add_review(request, booking_id):
    booking = get_object_or_404(Booking, id = booking_id)

    if not request.user.is_authenticated or booking.user_id!=request.user.id:
        messages.error(request, "You can't review this booking.")
        return redirect("my_bookings")

    if booking.payment_status != "paid":
        messages.error(request, "You can only review a booking after the advance is paid.")
        return redirect("my_bookings")

    if booking.travel_date >= timezone.now().date():
        messages.error(request, "You can review this trip once the travel date has passed.")
        return redirect("my_bookings")

    if hasattr(booking, "review"):
        messages.info(request, "You've already reviewed this booking.")
        return redirect("my_bookings")

    rating = request.POST.get("rating")
    comment = request.POST.get("comment", "").strip()

    try:
        rating = int(rating)
        if rating<1 or rating>5:
            raise ValueError

    except (TypeError, ValueError):
        messages.error(request, "Please select a rating between 1 and 5.")
        return redirect("my_bookings")


    if not comment:
        messages.error(request, "Please write a few words about your trip.")
        return redirect("my_bookings")

    Review.objects.create(
        booking = booking,
        user = request.user,
        package = booking.package,
        rating = rating,
        comment = comment,
    )
    messages.success(request, "Thanks for your review! It'll appear on the site once approved.")
    return redirect("my_bookings")
 

# ---------- Legal pages (Phase H) ----------
def view_privacy(request):
    return render(request, "travelingapp/privacy_policy.html")

def view_terms(request):
    return render(request, "travelingapp/terms.html")

def view_refund_policy(request):
    return render(request, "travelingapp/refund_policy.html")

