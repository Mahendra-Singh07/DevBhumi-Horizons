from django.urls import path
from .views import*

urlpatterns = [
    path('', view_home, name='home'),
    path('explore/', view_explore, name='explore'),
    path('destinations/', view_destinations, name='destinations'),
    path('about/', view_about, name='about'), 
    path('booking/', view_booking, name='booking'),
    # path('view1/', view_view1, name='view1'),
    # path('view2', view_view2, name='view2'),
    # path('view3', view_view3, name='view3'),
    path('subscribe/', view_subscribe,  name='subscribe'),
    path('package/<slug:slug>/', view_package_detail, name='package_detail'),
    path('search/', view_searchDestinations, name='search'),
    # path('login/', view_login, name='login')
    
    path("auth/signup/", view_signup, name="signup"),
    path("auth/verify-otp/", view_verify_otp, name="verify_otp"),
    path("auth/resend-otp/", view_resend_otp, name="resend_otp"),
    path("auth/login/", view_login, name="login"),
    path("auth/logout/", view_logout, name="logout"),
    path("profile/", view_profile, name="profile"),
    path("my-bookings/", view_my_bookings, name="my_bookings"),
    
    path("auth/google/", view_google_login, name="google_login"),
    path("auth/forgot-password/", view_forgot_password, name="forgot_password"),
    path("auth/reset-password/", view_reset_password, name="reset_password"),
    path("payment/<int:booking_id>/", view_payment, name="payment"),
    path("payment/verify/", verify_payment, name="verify_payment"),
]