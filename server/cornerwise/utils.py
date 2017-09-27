"""General utilities shared across all applications.

"""
from datetime import datetime
import inspect
import re

from django.conf import settings

protocol = "https" if settings.IS_PRODUCTION else "http"

def make_absolute_url(path):
    if re.match(r"^https?://", path):
        return path

    return "{protocol}://{domain}{path}".format(protocol=protocol,
                                                domain=settings.SERVER_DOMAIN,
                                                path=path)


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


deserializers = {
    (datetime, int): datetime.fromtimestamp,
    (datetime, float): datetime.fromtimestamp
}

def adapt_arg(arg, param_spec, deserializers):
    ann = param_spec.annotation
    if ann:
        if isinstance(arg, ann):
            return arg

        try:
            return deserializers[(ann, type(arg))](arg)
        except KeyError:
            raise Exception(f"No suitable adapter found for {ann}")

    return arg


def adapt_args(args, kwargs, spec, deserializers=deserializers):
    parameters = spec.parameters
    adapted_args = [
        adapt_arg(arg, parameters[arg_name], deserializers)
        for arg, arg_name in zip(args, parameters)
    ]

    adapted_kwargs = {
        arg_name: adapt_arg(kwargs[arg_name], parameters[arg_name], deserializers)
        for arg_name in kwargs
    }

    return adapted_args, adapted_kwargs


def adapt(fn):
    spec = inspect.signature(fn)
    def wrapped_fn(*args, **kwargs):
        adapted_args, adapted_kwargs = adapt_args(args, kwargs, spec)
        return fn(*adapted_args, **adapted_kwargs)
    return wrapped_fn
