from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render


def not_logged_in(request):
    return render(request, "user/not_logged_in.djhtml")


def with_user(view_fn):
    def wrapped_fn(request, *args, **kwargs):
        if not request.user.is_anonymous():
            return view_fn(request, request.user, *args, **kwargs)
        else:
            try:
                user = authenticate(pk=request.GET["uid"],
                                    token=request.GET["token"])
                if user:
                    messages.success(request, "Welcome back!")
                    login(request, user)
                    return view_fn(request, user, *args, **kwargs)
            except KeyError:
                messages.error(request,
                               "You must be logged in to view that page.")

            return not_logged_in(request)

    return wrapped_fn

