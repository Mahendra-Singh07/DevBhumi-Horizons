from django.shortcuts import render, redirect, get_object_or_404
from .models import Subscribers, Booking, Package
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import User, EmailOTP, Profile


# Create your views here.
def view_home(request):
    return render(request, 'travelingapp/home.html')

def view_explore(request):
    # packages = Package.objects.filter(is_active=True)

    return render(request, "travelingapp/explore-treks.html",
        # {
        #     "packages": packages
        # }
    )
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




# def view_view1(request):
#     return render(request, 'travelingapp/traveling-view-detail.html')

# def view_view2(request):
#     return render(request, 'travelingapp/traveling-view-detail2.html')

# def view_view3(request):
#     return render(request, 'travelingapp/traveling-view-detail3.html')



# def view_subscribe(request):
#     if request.method == "POST":
#         email = request.POST.get("email")

#         subscribe = Subscribers.objects.filter(email=email).first()

#         if subscribe:
#             messages.warning(request, "You already subscribed")
#         else:
#             Subscribers.objects.create(email=email)
#             messages.success(request, "Successfully subscribed")

#     return redirect(reverse("home") + "#contact")


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
            messages.success(request, "Subscribe Successfully")

        # 'created' is False when the email already exists.
        else:
            messages.warning(request, "You Already Subscribe")

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


def view_booking(request):
    if request.method == "POST":

        # this is for error protection 
        # kyuki jab hum booking m koi field fill nahi hoti toh error aata h
        # halaki jo filed required nahi hoti option h, usme hum null= True and blank =True likh dete h 
        # but jo required hoti h aur fill nahi kiya toh error aata h 
        # html m field m required likhne se problem solve toh ho jati h but koi bhi ushe change krr sakta h 
        # so hame backend m ye use krte h taki sab field fill ho koi rhh jaye toh ye msg aaye error na aaye 

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        travel_date = request.POST.get("travel_date")
        travelers = request.POST.get("total_travelers")
        special_request = request.POST.get("request")
        if not name:
            messages.error(request, "Name is required")
            return redirect("booking")
        
        if not email:
            messages.error(request, "Email is Required")
            return redirect("booking")
        if not phone:
            messages.error(request, "Phone number is required.")
            return redirect("booking")

        if not travel_date:
            messages.error(request, "Travel date is required.")
            return redirect("booking")

        if not travelers:
            messages.error(request, "Please enter number of travelers.")
            return redirect("booking")

        
        package = get_object_or_404(Package, slug=request.POST.get("package_slug"))
        booking = Booking.objects.create(
            name= name,
            email = email,
            phone = phone,
            travel_date = travel_date,
            travelers = travelers,
            package = package,
            special_request = special_request,
        )
        if request.user.is_authenticated:
            booking.user = request.user
            booking.save()

        messages.success(request, "Booked Successfully")
        return redirect('booking')

    package = Package.objects.all()
    return render(request, "travelingapp/booking.html",{
        "packages": package,
        "name" : request.GET.get("name"),
        "email" : request.GET.get("email"),
        "travelers" : request.GET.get("total_travelers", "1"),
        "special": request.GET.get("request"),
        "package_slug": request.GET.get("package_slug")
    })


def view_package_detail(request, slug):
    package = get_object_or_404(Package, slug=slug, is_active=True)

    related_packages = Package.objects.filter(
        is_active=True,
        location__region=package.location.region
    ).exclude(id=package.id)[:4]

    d1 = {"package":package,
          "food_items": package.food_stay.split("\n"),
          "related_packages": related_packages}

    packages = Package.objects.all()
    return render(request, 'travelingapp/traveling-view-detail.html', d1)




def view_searchDestinations(request):

    keyword = request.GET.get("q", "")

    packages = Package.objects.filter(
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


# def view_login(request):
#     return render(request, 'travelingapp/login.html')

import json
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, BadHeaderError
import smtplib

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
    except (smtplib.SMTPException, BadHeaderError):
        return False


@require_POST
def view_signup(request):
    # if request.method == "POST":
    data = json.loads(request.body)
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


@require_POST
def view_verify_otp(request):
    data = json.loads(request.body)
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

@require_POST
def view_resend_otp(request):
    data = json.loads(request.body)
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

@require_POST
def view_login(request):
    data = json.loads(request.body)
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

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        profile.phone = request.POST.get("phone", "").strip()
        profile.address = request.POST.get("address", "").strip()

        dob = request.POST.get("date_of_birth")
        profile.date_of_birth = dob or None

        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")

    return render(request, "travelingapp/profile.html", {"profile": profile})

def view_my_bookings(request):
    if not request.user.is_authenticated:
        return redirect("home")

    bookings = request.user.bookings.all().order_by("-booking_date")
    return render(request, "travelingapp/my_bookings.html", {"bookings": bookings})



import requests

@require_POST
def view_google_login(request):
    data = json.loads(request.body)
    access_token = data.get("access_token", "")

    if not access_token:
        return JsonResponse({"success": False, "error": "Missing Google token."}, status=400)

    # Ask Google itself who this token belongs to — this is the verification step.
    # If the token is fake/expired/tampered, Google will simply refuse to answer.
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

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



@require_POST
def view_forgot_password(request):
    data = json.loads(request.body)
    email = data.get("email", "").strip().lower()

    if not email:
        return JsonResponse({"success": False, "error": "Email is required."}, status=400)

    user = User.objects.filter(email=email, is_active=True).first()

    if not user:
        return JsonResponse({"success": False, "error": "No account found with this email."}, status=400)

    if not _send_otp_email(user):
        return JsonResponse({"success": False, "error": "Couldn't send reset code — check the email address."}, status=400)

    return JsonResponse({"success": True, "message": "Reset code sent.", "email": email})


@require_POST
def view_reset_password(request):
    data = json.loads(request.body)
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