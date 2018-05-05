import json
import os
import pkgutil

from site_config.site_config import SiteConfig


class SiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.GET.get("_hostname", request.META.get("HTTP_HOST")).lower()
        host_config = HOSTNAMES.get(host, DEFAULT_CONFIG)
        request.site_config = host_config
        request.site_hostname = host
        request.site_name = host_config.hostname

        return self.get_response(request)


def context_processor(request):
    if request.site_config:
        js_config = request.site_config.js_config
        context = {"site_config": json.dumps(js_config),
                   "hostname": request.site_hostname,
                   "logo_text": request.site_config.logo_text}
        context.update(request.site_config.extra_context)
        return context

    return {}


def site_config(site_name) -> SiteConfig:
    return HOSTNAMES.get(site_name, DEFAULT_CONFIG)


by_hostname = site_config


def by_name(name: str) -> SiteConfig:
    return NAMES.get(name.lower())


def base_url(site_name):
    return site_config(site_name).hostname



# Maps module hostnames to their configuration.
DEFAULT_CONFIG = None
HOSTNAMES = {}
NAMES = {}


def find_site_configurations(path=None):
    if not path:
        path = os.path.dirname(__file__)

    for module_finder, name, _ in pkgutil.iter_modules([path]):
        site_module = module_finder.find_module(name)\
                                   .load_module(name)
        config = getattr(site_module, "SITE_CONFIG", None)
        config and add_configuration(config, site_module, name)


def add_configuration(config: SiteConfig, module, name):
    hostnames = config.hostnames
    if not hostnames:
        raise Exception(f"Site configuration '{name}' must have at least one hostname")

    NAMES[config.name.lower()] = config

    for hostname in hostnames:
        if hostname == "default":
            global DEFAULT_CONFIG
            DEFAULT_CONFIG = config
            continue
        if hostname not in HOSTNAMES:
            HOSTNAMES[hostname] = config
        else:
            return False

    return True


find_site_configurations()
