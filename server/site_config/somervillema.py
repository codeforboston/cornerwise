from django.core.exceptions import ValidationError
from django.contrib.gis.measure import D

from site_config.site_config import SiteConfig


class SomervilleConfig(SiteConfig):
    group_name = "somervillema"
    hostnames = ["somerville.cornerwise.org", "cornerwise.somervillema.gov", "default"]
    name = "Somerville"

    extra_context = {
        "site_description": ("Find and explore current and future zoning "
                             "projects near you - City of Somerville.")
    }

    js_config = {
        "includeRegions": ["somerville"],
        "minSubscribeRadius": 300,
        "maxSubscribeRadius": 300,
    }

    query_defaults = {"region_name": "Somerville, MA"}

    max_subscription_radius = D(ft=300).m

    def validate_subscription_query(self, sub, query):
        if sub.region_name:
            if sub.region_name != "Somerville, MA":
                raise ValidationError(
                    f"Subscriptions on this site are restricted to the Somerville area.")
        else:
            query["region_name"] = "Somerville, MA"
            sub.region_name = "Somerville, MA"
        if sub.box:
            raise ValidationError(
                f"Region queries are not supported for the Somerville area.")
        if sub.center and sub.radius:
            if sub.radius - self.max_subscription_radius >= 0.5:
                raise ValidationError(
                    f"Queries of greater than 300 feet are not allowed")
        return query


SITE_CONFIG = SomervilleConfig()
