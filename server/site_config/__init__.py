import json
import os
import pkgutil


class SiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.GET.get("_hostname", request.META.get("HTTP_HOST")).lower()
        host_config = HOSTNAMES.get(host, HOSTNAMES["default"])
        request.site_config = host_config
        request.site_hostname = host
        request.site_name = host_config["hostname"]

        return self.get_response(request)


def context_processor(request):
    if request.site_config:
        js_config = request.site_config.get("js_config", {})
        context = {"site_config": json.dumps(js_config),
                   "hostname": request.site_hostname,
                   "logo_text": request.site_config.get("logo_text")}
        context.update(request.site_config.get("extra_context", {}))
        return context

    return {}


# Maps module hostnames to their configuration.
HOSTNAMES = {}
MODULES = {}


def find_site_configurations(path=None):
    if not path:
        path = os.path.dirname(__file__)

    for module_finder, name, _ in pkgutil.iter_modules([path]):
        site_module = module_finder.find_module(name)\
                                   .load_module(name)
        config = getattr(site_module, "SITE_CONFIG", None)
        config and add_configuration(config, site_module, name)


def add_configuration(config, module, name):
    hostnames = config.get("hostnames", [])
    if not hostnames:
        raise Exception(f"Site configuration '{name}' must have at least one hostname")

    config.setdefault("name", name)
    # Default hostname:
    config.setdefault("hostname", hostnames[0])

    for hostname in hostnames:
        if hostname not in HOSTNAMES:
            HOSTNAMES[hostname] = config
            MODULES[hostname] = module
        else:
            return False

    return True


find_site_configurations()
