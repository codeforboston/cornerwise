import django.contrib.auth as auth
from django.shortcuts import render

from shared.request import make_response


def user_dict(user):
    return {}


@make_response
def login(request):
    user = auth.authenticate(username=request.POST["username"],
                             password=request.POST["password"])
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return user_dict(user)
        else:
            return {"error": "That user account has been disabled."}

    return {"error": "Invalid username or password"}


@make_response
def logout(request):
    auth.logout(request)
    return {}
