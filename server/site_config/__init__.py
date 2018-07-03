import json

from django.shortcuts import redirect

from site_config.site_config import SiteConfig


class SiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.GET.get("_hostname", request.META.get("HTTP_HOST"))
        if host:
            host = host.casefold()
        host_config = HOSTNAMES.get(host)

        if not host_config or host_config.redirect:
            return redirect("{scheme}://{host}{path}".format(
                scheme=request.scheme,
                host=DEFAULT_CONFIG.hostname,
                path=request.get_full_path()
            ))
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


def find_site_configurations():
    from django.conf import settings

    from importlib import import_module

    configs = getattr(settings, "SITE_CONFIG", {})
    for name, config_dict in configs.items():
        site_module = import_module(config_dict["module"])
        config = getattr(site_module, "SITE_CONFIG", None)
        if config:
            if "hostnames" in config_dict:
                config.hostnames = config_dict["hostnames"]
            add_configuration(config, site_module, name)


def add_configuration(config: SiteConfig, module, name):
    hostnames = config.hostnames
    if not hostnames:
        raise Exception(
            f"Site configuration '{name}' must have at least one hostname")

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
