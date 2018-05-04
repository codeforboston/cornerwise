from django.core.exceptions import ValidationError
from django.contrib.gis.measure import D

from site_config.site_config import SiteConfig


class SomervilleConfig(SiteConfig):
    hostnames = ["somerville.cornerwise.org", "cornerwise.somervillema.gov", "default"]
    name = "Somerville"

    extra_context = {
        "site_description": ("Find and explore current and future zoning "
                             "projects near you - City of Somerville.")
    }

    js_config = {
        "includeRegions": ["somerville"]
    }

    max_subscription_radius = D(ft=300)

    def validate_subscription_query(self, sub, query):
        if sub.box:
            raise ValidationError(
                f"Region queries are not supported for the Somerville area.")
        if sub.center and sub.radius:
            if sub.radius > self.max_subscription_radius:
                raise ValidationError(
                    f"Queries of greater than 300 feet are not allowed")
        return query


SITE_CONFIG = SomervilleConfig()
