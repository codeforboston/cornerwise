from django.http import JsonResponse

from django.shortcuts import render_to_response
from django.template.loader import render_to_string

import logging
import re

logger = logging.getLogger("logger")

class ErrorResponse(Exception):
    def __init__(self, message, data=None, status=401):
        super(Exception, self).__init__(self, message)
        self.data = data or { "error": message }
        self.status = status


def make_response(template=None, error_template="error.html"):
    """
    View decorator

    Tailor the response to the requested data type, as specified
    in the Accept header. Expects the wrapped view to return a
    dict. If the request wants JSON, renders the dict as JSON data.
    """
    def constructor_fn(view):
        def wrapped_view(req):
            use_template = template
            status = 200
            try:
                data = view(req)
            except ErrorResponse as err:
                data = err.data
                use_template = error_template
                status = err.status
                # render error template or return JSON with proper error
                # code

            accepts = req.META["HTTP_ACCEPT"]
            typestring, _ = accepts.split(";", 1)

            if not use_template or re.search(r"application/json", typestring):
                response = JsonResponse(data, status=status)
                # TODO: We may (or may not!) want to be more restrictive
                # in the future:
                response["Access-Control-Allow-Origin"] = "*"
                return response

            return render_to_response(use_template, data, status=status)

        return wrapped_view

    return constructor_fn
