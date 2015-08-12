from django.http import JsonResponse

from django.shortcuts import render_to_response
from django.template.loader import render_to_string

import logging

logger = logging.getLogger("logger")

class ErrorResponse(Exception):
    def __init__(self, message, data):
        super(Exception, self).__init__(self, message)
        self.data = data


def make_response():
    def constructor_fn(view):
        def wrapped_view(req):
            accepts = req.META["HTTP_ACCEPT"]
            logger.info(accepts)

            try:
                data = view(req)
            except ErrorResponse as err:
                data = err.data
                # render error template or return JSON with proper error code


            # Render the response
            return JsonResponse(data)

        return wrapped_view

    return constructor_fn
