from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.template import RequestContext

from django.contrib.auth import login, logout

from datetime import datetime, timedelta
import json
import logging
import re

from cornerwise.utils import today
from shared.request import make_response, make_redirect_response, ErrorResponse
from user import changes, tasks
from user.models import Subscription, UserProfile
from user.utils import not_logged_in, with_user


logger = logging.getLogger(__file__)

def user_dict(user):
    return {}

# These correspond to the filters the user can apply.
valid_keys = {"projects", "text", "box", "region"}


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
    Set up a new subscription.
    """
    # Validate the request:
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
            raise ErrorResponse("Invalid filter options", {"query": query_dict})

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
            language = request.GET.get("language", "en-US")
            lang, _reg = language.split("-", 1)
            user = User.objects.create(username=email,
                                       email=email,)
            profile = UserProfile.objects.create(user=user,
                                                 language=lang)
            profile.save()
            new_user = True

    try:
        subscription = Subscription()
        subscription.set_validated_query(query_dict)
        user.subscriptions.add(subscription)
    except Exception as exc:
        raise ErrorResponse("Invalid subscription",
                            {"exception": exc.args})

    return {"new_user": new_user,
            "active": user.is_active,
            "email": user.email}


@make_redirect_response()
def confirm_subscription(request):
    try:
        user = authenticate(pk=request.GET["uid"],
                            token=token.GET["token"])

        if not user:
            raise ErrorResponse("Invalid user id or token")

        subscription = user.subscriptions.get(id=sub_id)
        subscription.confirm()
        return {"title": "Subscription confirmed",
                "text": ("Now that we know you are who you say you are, "
                         "we'll send you updates about projects in the "
                         "area you selected."),
                "tags": "success"}
    except KeyError as kwerr:
        raise ErrorResponse("Missing required param: " + kwerr.args[0])
    except Subscription.DoesNotExist:
        raise ErrorResponse("Invalid token or subscription id.")


@make_response("task_message.djhtml", redirect_back=True)
def do_resend_email(request):
    try:
        email = request.POST["email"]
        user = User.objects.get(email=email)
        task_id = tasks.resend_user_key.delay(user.id)
    except KeyError:
        raise ErrorResponse("Bad request", status=405)
    except User.DoesNotExist:
        raise ErrorResponse(
            "There is no registered user with that email address.",
            redirect_back=True)

    return {"status": "OK",
            "task_id": task_id,
            "pending_message": "We're sending an email to " + email,
            "success_message": "We've sent a new login link to " + email,}


def resend_email(request):
    if request.method == "GET":
        return not_logged_in(request)

    return do_resend_email(request)


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
        user.is_active = True
        user.save()

    return render(request, "user/manager.djhtml",
                  {"user": user,
                   "subscriptions": user.subscriptions},
                  context_instance=RequestContext(request))


def default_view(request):
    return redirect(reverse("manage-user"))


@make_response("user/subscription.djhtml")
def show_change_summary(request, user, sub_id, since, until=None):
    """
    Displays a summary of the changes recorded for a given subscription within
    a time period specified by `since` and `until`.
    """
    try:
        sub = Subscription.objects.get(user=user, pk=sub_id)
        summary = changes.summarize_subscription_updates(sub, since, until)
        return {"since": since,
                "until": until,
                "subscription": sub,
                "changes": summary}
    except Subscription.DoesNotExist:
        raise ErrorResponse("Invalid subscription ID",
                            status=404,
                            redirect_back=True)
    except KeyError:
        raise ErrorResponse("Missing subscription id",
                            redirect_back=True)


@with_user
def change_summary(request, user):
    sub_id = request.GET["subscription_id"]
    since = None
    until = None
    days = None

    if "since" in request.GET:
        try:
            since = datetime.fromtimestamp(float(request.GET["since"]))
        except ValueError:
            since = None
    else:
        try:
            days = abs(int(request.GET["days"]))
        except (KeyError, ValueError):
            days = 7

    if days:
        since = today() - timedelta(days=days)
    elif "until" in request.GET:
        try:
            until = datetime.fromtimestamp(float(request.GET["until"]))
        except (TypeError, ValueError):
            pass

    return show_change_summary(request, user, sub_id, since, until)


@with_user
def delete_subscription(request, user):
    try:
        sub_id = request.POST["subscription_id"]
        subscription = user.subscriptions.get(pk=sub_id)
        subscription.delete()
        messages.success(request, "Subscription deleted")
    except Subscription.DoesNotExist:
        messages.error(request, "Invalid subscription ID")
    except KeyError:
        messages.error(request, "Missing parameter 'subscription_id'")
    return redirect(reverse(manage))


@make_redirect_response()
def test_redirect_response(request):
    return "All set!"


def user_logout(request):
    logout(request)

    return redirect("/")

