from django.contrib import messages
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render_to_response, render

import logging
import json
import re

logger = logging.getLogger("logger")


class ErrorResponse(Exception):
    def __init__(self, message, data=None, status=401, err=None,
                 redirect_back=None):
        super(Exception, self).__init__(self, message)
        self.data = {"error": message}
        if data:
            self.data.update(data)
        self.status = status
        self.exception = err
        self.redirect_back = redirect_back


def make_response(template=None, error_template="error.djhtml",
                  shared_context=None, redirect_back=False):
    """
    View decorator

    Tailor the response to the requested data type, as specified
    in the Accept header. Expects the wrapped view to return a
    dict. If the request wants JSON, renders the dict as JSON data.
    """
    def constructor_fn(view):
        def wrapped_view(req, *args, **kwargs):
            use_template = template
            status = 200
            should_redirect_back = redirect_back
            try:
                data = view(req, *args, **kwargs)

                if isinstance(data, HttpResponse):
                    return data
                if shared_context:
                    data.update(shared_context)
            except ErrorResponse as err:
                data = err.data
                use_template = error_template
                status = err.status
                should_redirect_back = err.redirect_back

                # render error template or return JSON with proper error
                # code

            jsonp_callback = req.GET.get("callback")

            if jsonp_callback:
                content = json.dumps(data, cls=DjangoJSONEncoder)
                body = "{callback}({json})".format(callback=jsonp_callback,
                                                   json=content)

                response = HttpResponse(body, status=status)
                response["Content-type"] = "application/javascript"
                return response

            accepts = req.META.get("HTTP_ACCEPT", "text/html")

            if not use_template \
               or re.search(r"application/json", accepts) \
               or req.GET.get("format", "").lower() == "json":
                response = JsonResponse(data, status=status)
                response["Access-Control-Allow-Origin"] = "*"
                return response

            if should_redirect_back:
                if "error" in data:
                    messages.error(req, data["error"])
                    return do_redirect_back(req)
                elif "message" in data:
                    messages.success(req, data["message"])
                    return do_redirect_back(req)

            return render(req, use_template, data, status=status)

        return wrapped_view

    return constructor_fn


def json_view(view):
    def json_handler(req, *args, **kwargs):
        resp = HttpResponse(json.dumps(view(req, *args, **kwargs),
                                       cls=DjangoJSONEncoder))
        resp["Content-type"] = "application/json"
        return resp

    return json_handler


def make_message(request, data):
    extra_tags = None
    if isinstance(data, str):
        message = data
        level = messages.SUCCESS
    elif isinstance(data, dict):
        level = data.get("level", "success")
        level = getattr(messages, level.upper())
        message = json.dumps(data, cls=DjangoJSONEncoder)
        extra_tags = "json"
    elif isinstance(data, tuple):
        (message, level) = data

    if isinstance(level, str):
        level = getattr(messages, level.upper())

    messages.add_message(request, level, message, extra_tags=extra_tags)


def redirect_back(request, default="/"):
    back_url = request.META.get("HTTP_REFERER", default)
    return redirect(back_url)

do_redirect_back = redirect_back
