from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.template import RequestContext

from django.contrib.auth import login, logout

import json

from shared.request import make_response, ErrorResponse
from .models import Subscription, UserProfile
from .tasks import send_user_key


def user_dict(user):
    return {}

# These correspond to the filters the user can apply.
valid_keys = {"projects", "text", "box"}


def validate_query(d):
    # Remove unrecognized keys:
    for k in set(d.keys()).difference(valid_keys):
        del d[k]

    if "projects" in d:
        d["projects"] = d["projects"].lower()
        if d["projects"] not in {"all", "null"}:
            del d["projects"]

    # Verify that all the keys are well-formed
    return d


@make_response("subscribed.djhtml", "subscribe_error.djhtml")
def subscribe(request):
    """
    Set up a new subscription. If the supplied
    """
    if request.method != "POST":
        raise ErrorResponse("Request must use POST method.", status=405)

    try:
        query_dict = json.loads(request.POST["query"])
    except KeyError:
        raise ErrorResponse("Missing a 'query' field")
    except ValueError:
        raise ErrorResponse("Malformed JSON in 'query' field.")

    if query_dict != {}:
        query_dict = validate_query(query_dict)
        if not query_dict:
            raise ErrorResponse("Invalid query", {"query": query_dict})

    user = request.user
    new_user = False

    if user.is_anonymous():
        try:
            email = request.POST["email"]
            user = User.objects.get(email=email)
        except KeyError as kerr:
            raise ErrorResponse(
                "Missing required key:" + kerr.args[0],
                {})
        except User.DoesNotExist:
            user = User.objects.create(username=email,
                                       email=email)
            UserProfile.objects.create(user=user)
            new_user = True

    try:
        subscription = Subscription()
        subscription.set_validated_query(query_dict)
        user.subscriptions.add(subscription)
    except Exception as exc:
        raise ErrorResponse("Invalid subscription",
                            {"exception": exc.args})

    messages.success(request, "Subscription added")
    return {"new_user": new_user,
            "active": user.is_active,
            "email": user.email}


@make_response()
def resend_email(request):
    try:
        user = User.objects.get(email=request.POST["email"])
        send_user_key.delay(user)
    except KeyError:
        raise ErrorResponse("Bad request", status=405)
    except User.DoesNotExist:
        pass

    return {"status": "OK"}


def do_login(request, token, uid):
    try:
        user = User.objects.get(pk=uid)
        if user.token == token:
            login(request, user)
            # Should the old token be invalidated at each login, or should it
            #  only be regenerated when emails are sent?

            # user.generate_token()
            return user
    except User.DoesNotExist:
        return None


def with_user(view_fn):
    def wrapped_fn(request, **kwargs):
        if request.user:
            return view_fn(request, request.user, **kwargs)
        else:
            try:
                user = do_login(request,
                                request.GET["token"],
                                request.GET["uid"])
                if user:
                    return view_fn(request, user, **kwargs)
            except KeyError:
                messages.error(request,
                               "You must be logged in to view that page.")

            return redirect("/")

    return wrapped_fn


def user_login(request, token, pk):
    user = authenticate(pk=pk, token=token)
    if not user:
        return render(request, "token_error.djhtml",
                      status=403)

    login(request, user)
    return redirect(reverse(manage))


@with_user
def activate_account(request, user):
    user.activate()

    return redirect(reverse("manage-user"))


@with_user
def deactivate_account(request, user):
    user.deactivate()

    return redirect("/")


@with_user
def manage(request, user):
    if not user.is_active:
        user.activate()
        messages.success(request,
                         "Thank you for confirming your account.")

    return render(request, "user/manager.djhtml",
                  {"user": user,
                   "subscriptions": user.subscriptions},
                  context_instance=RequestContext(request))


@with_user
def delete_subscription(request, user, sub_id):
    try:
        subscription = user.subscriptions.get(pk=sub_id)
        subscription.delete()
        messages.success(request, "Subscription deleted")
    except Subscription.DoesNotExist:
        messages.error(request, "Invalid subscription ID")
    return redirect(reverse(manage))


# Should there be a user logout?
def user_logout(request):
    logout(request)

    return redirect("/")
