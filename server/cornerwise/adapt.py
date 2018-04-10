from datetime import datetime, timedelta
import inspect
import numbers
import typing
from typing import Tuple

from django.db import models

import pytz


def takes_iterable(fn):
    fn.takes_iterable = True
    return fn


def now_utc():
    return pytz.utc.localize(datetime.utcnow())


def adapt_datetime(arg, _type) -> datetime:
    if isinstance(arg, numbers.Number):
        return datetime.fromtimestamp(arg)
    if isinstance(arg, timedelta):
        return now_utc() - arg


@takes_iterable
def adapt_model(arg, Model):
    if isinstance(arg, int):
        return Model.objects.get(pk=arg)
    if isinstance(arg, Model):
        return arg
    try:
        return Model.objects.filter(pk__in=arg)
    except TypeError:
        return None


def adapt_iterable(args, it, deserializers):
    if not args:
        return []

    try:
        it_type = it.__args__[0]

        des = get_deserializer(it_type, deserializers)
        if des and des.takes_iterable:
            return des(args, it_type)

        return (adapt_arg(arg, it_type, deserializers) for arg in args)
    except (IndexError, TypeError):
        return args


def adapt_tuple(args, ann, deserializers):
    return (
        adapt_arg(arg, ttype, deserializers)
        for arg, ttype in
        zip(args, ann.__args__)
    )


DESERIALIZERS = {
    datetime: adapt_datetime,
    models.Model: adapt_model,
}

def get_deserializer(ann, deserializers):
    for t in ann.__mro__:
        deserializer = deserializers.get(t)
        if deserializer:
            return deserializer


def adapt_arg(arg, ann, deserializers=DESERIALIZERS):
    if not ann or ann is inspect._empty:
        return arg

    if ann.__module__ == "typing":
        if typing.Iterable in ann.__mro__:
            return adapt_iterable(arg, ann, deserializers)
        elif typing.Tuple in ann.__mro__:
            return adapt_tuple(arg, ann, deserializers)

    if isinstance(arg, ann):
        return arg

    deserializer = get_deserializer(ann, deserializers)
    if deserializer:
        adapted = deserializer(arg, ann)
        if adapted:
            return adapted

    return arg


def adapt_args(args: list, kwargs: dict, spec: inspect.Signature,
               deserializers=DESERIALIZERS) -> Tuple[list, dict]:
    """Takes the arguments to a function (as an arg list and a dict of keyword
    args) and adapts them according to the spec.
    """
    parameters = spec.parameters
    adapted_args = [
        adapt_arg(arg, parameters[arg_name].annotation, deserializers)
        for arg, arg_name in zip(args, parameters)
    ]

    adapted_kwargs = {
        arg_name: adapt_arg(kwargs[arg_name], parameters[arg_name].annotation, deserializers)
        for arg_name in kwargs
    }

    return adapted_args, adapted_kwargs


def adapt_with_serializers(deserializers):
    """Function decorator that inspects the type annotations for the decorated
    function and when the function is called, attempts to convert the arguments
    to the correct types using the specified deserializers.
    """
    def wrapper(fn):
        spec = inspect.signature(fn)
        def wrapped_fn(*args, **kwargs):
            "Wrapped function with adapted arguments"
            adapted_args, adapted_kwargs = adapt_args(args, kwargs, spec, deserializers)
            return fn(*adapted_args, **adapted_kwargs)
        wrapped_fn.__name__ = fn.__name__
        wrapped_fn.__module__ = fn.__module__

        return wrapped_fn

    return wrapper

adapt = adapt_with_serializers(DESERIALIZERS)
