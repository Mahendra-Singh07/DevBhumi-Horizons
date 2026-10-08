"""SEO helpers: sitemap.xml and robots.txt (both must live at the domain root)."""
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_GET

from .models import Package


class StaticPagesSitemap(Sitemap):
    """The fixed public pages."""
    protocol = "https"
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["home", "explore", "destinations", "about"]

    def location(self, item):
        return reverse(item)


class PackageSitemap(Sitemap):
    """One entry per active package (inactive ones are not public, so not listed)."""
    protocol = "https"
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Package.objects.filter(is_active=True).order_by("id")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("package_detail", args=[obj.slug])


sitemaps = {"pages": StaticPagesSitemap, "packages": PackageSitemap}


@require_GET
def robots_txt(request):
    """Allow crawling of public pages; keep Google out of login, payment and account pages."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /travel/auth/",
        "Disallow: /travel/profile/",
        "Disallow: /travel/my-bookings/",
        "Disallow: /travel/payment/",
        "Disallow: /travel/invoice/",
        "Disallow: /travel/booking/",
        "Disallow: /travel/search/",
        "",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")