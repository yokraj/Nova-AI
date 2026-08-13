"""Security Headers Module.

Defines enterprise HTTP security header dictionaries and helper functions.
"""

from typing import Dict


def get_security_headers() -> Dict[str, str]:
    """Returns standard enterprise HTTP security headers dictionary."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Cache-Control": "no-store, max-age=0",
    }


def apply_security_headers(headers_dict: Dict[str, str]) -> Dict[str, str]:
    """Applies security headers to an existing headers dictionary."""
    sec = get_security_headers()
    headers_dict.update(sec)
    return headers_dict
