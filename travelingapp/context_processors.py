from django.conf import settings


def google_client_id(request):
    return {"GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID}


# ---- Phase H: one source of truth for contact details + booking policy ----
SITE = {
    "name": "DevBhumi Horizons",
    "email": "devbhumihorizons@gmail.com",       # <-- confirm
    "phone": "+91 79824 79183",                  # <-- confirm
    "address": "Faridabad, Haryana 121003",
    "policy_updated": "2 October 2026",
}


def site_info(request):
    """Makes SITE and POLICY available in every template.
    POLICY reads the SAME constants views.py uses to calculate refunds,
    so the policy pages / FAQ can never disagree with what the code does."""
    from . import views   # imported lazily to avoid import cycles at startup

    advance = views.BOOKING_ADVANCE_AMOUNT
    percent = views.CANCELLATION_REFUND_PERCENT
    return {
        "SITE": SITE,
        "POLICY": {
            "advance": advance,
            "window_days": views.CANCELLATION_WINDOW_DAYS,
            "refund_percent": percent,
            "refund_amount": advance * percent / 100,
        },
        # True only while Razorpay test keys are in use -> demo notice disappears
        # automatically when you ever switch to live keys.
        "PAYMENTS_TEST_MODE": str(getattr(settings, "RAZORPAY_KEY_ID", "")).startswith("rzp_test_"),
    }