"""Real client IP for django-ratelimit when the app runs behind a hosting proxy.

Behind Render/Railway, REMOTE_ADDR is the PLATFORM'S proxy, not the visitor, so
key='ip' would put every visitor in one shared bucket. The X-Forwarded-For
header lists the real chain, but its LEFT side can be forged by the client.
Proxies we trust append to the RIGHT, so we count from the right:

    TRUSTED_PROXY_COUNT = 0  -> ignore the header, use REMOTE_ADDR (local dev)
    TRUSTED_PROXY_COUNT = 1  -> the last entry is the visitor (one proxy in front)
    TRUSTED_PROXY_COUNT = 2  -> second-last entry, and so on
"""
import ipaddress
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def client_ip(request):
    remote = request.META.get("REMOTE_ADDR") or "127.0.0.1"
    count = getattr(settings, "TRUSTED_PROXY_COUNT", 0)
    if logger.isEnabledFor(logging.DEBUG):
        # Temporary aid: set LOG_LEVEL=DEBUG on the host to see what the proxy sends.
        logger.debug("ratelimit: remote=%s xff=%r count=%s",
                     remote, request.META.get("HTTP_X_FORWARDED_FOR", ""), count)
    if count <= 0:
        return remote

    header = request.META.get("HTTP_X_FORWARDED_FOR", "")
    parts = [p.strip() for p in header.split(",") if p.strip()]
    if len(parts) < count:
        # Fewer entries than proxies we expected -> TRUSTED_PROXY_COUNT is probably
        # too high (or the request bypassed the proxy). Fail safe, but say so.
        logger.warning("ratelimit: X-Forwarded-For has %d entries but TRUSTED_PROXY_COUNT=%d; "
                       "falling back to REMOTE_ADDR=%s", len(parts), count, remote)
        return remote

    candidate = parts[-count]
    try:
        addr = ipaddress.ip_address(candidate)
    except ValueError:
        logger.warning("ratelimit: invalid IP in X-Forwarded-For; falling back to REMOTE_ADDR=%s", remote)
        return remote

    if not addr.is_global:
        # A private/loopback/link-local address can't be a real visitor on the
        # internet: we have most likely picked an internal proxy hop.
        logger.warning("ratelimit: picked non-public IP %s from X-Forwarded-For; "
                       "TRUSTED_PROXY_COUNT=%d is probably too low", candidate, count)
    return candidate