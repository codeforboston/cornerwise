from django.contrib.auth import authenticate, get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django.contrib.auth import login, logout

from datetime import datetime
import json
import logging

import pytz

from shared.request import make_response, make_message, ErrorResponse
from shared.mail import render_email_body
from user import tasks
from .contact import ContactForm
from user.mail import updates_context
from user.models import Subscription, UserProfile
from user.utils import not_logged_in, with_user

logger = logging.getLogger(__file__)

User = get_user_model()


@make_response("subscribed.djhtml", "subscribe_error.djhtml")
@require_POST
def subscribe(request):
    """
    Set up a new subscription.
    """
    # Validate the request:
    try:
        query_dict = json.loads(request.POST["query"])
    except KeyError:
        raise ErrorResponse("Missing a 'query' field")
    except ValueError:
        raise ErrorResponse("Malformed JSON in 'query' field.")

    new_user = False
    has_subscriptions = False

    try:
        email = request.POST["email"]
        user = User.objects.get(email=email)
        has_subscriptions = user.subscriptions.filter(active=True).exists()
    except KeyError as kerr:
        raise ErrorResponse("Missing required key:" + kerr.args[0], {})
    except User.DoesNotExist:
        language = request.GET.get("language", "en-US")
        lang, _reg = language.split("-", 1)
        user = User.objects.create(
            is_active=False,
            username=email,
            email=email, )
        profile = UserProfile.objects.create(user=user, language=lang,
                                             site_name=request.site_name)
        profile.save()
        new_user = True

    try:
        subscription = Subscription(site_name=request.site_name,
                                    address=request.POST.get("address"))
        subscription.set_validated_query(query_dict)
        subscription.user = user
        subscription.save()
    except (ValidationError, ValueError) as exc:
        raise ErrorResponse("Invalid subscription", {"exception": exc.args})
    except Exception as exc:
        logging.exception("Error while creating subscription:")
        raise ErrorResponse("Invalid subscription", {"exception": exc.args})

    return {
        "new_user": new_user,
        "active": user.is_active,
        "email": user.email,
        "has_subscriptions": has_subscriptions
    }


@make_response()
def confirm(request):
    try:
        user = authenticate(pk=request.GET["uid"], token=request.GET["token"])

        if not user:
            raise ErrorResponse("Invalid user id or token")

        if "sub" in request.GET:
            subscription = user.subscriptions.get(pk=request.GET["sub"])
        else:
            subscription = user.subscriptions.all().order_by("-created")[0]
        subscription.confirm()
        make_message(request, {
            "title": "Subscription confirmed",
            "text": ("Now that we know you are who you say you are, "
                     "we'll send you updates about projects in the "
                     "area you selected."),
            "tags": "success"
        })
        return redirect(subscription.map_url)
    except KeyError as kwerr:
        raise ErrorResponse("Missing required param: " + kwerr.args[0])
    except Subscription.DoesNotExist:
        raise ErrorResponse("Invalid token or subscription id.")
    except IndexError:
        raise ErrorResponse("That user does not have a subscription")


@make_response("task_message.djhtml", redirect_back=True)
def do_resend_email(request):
    try:
        email = request.POST["email"]
        user = User.objects.get(email=email)
        task_id = tasks.resend_user_key.delay(user.pk)
    except KeyError:
        raise ErrorResponse("Bad request", status=405)
    except User.DoesNotExist:
        raise ErrorResponse(
            "There is no registered user with that email address.",
            redirect_back=True)

    return {
        "status": "OK",
        "task_id": task_id,
        "pending_message": "We're sending an email to " + email,
        "success_message": "We've sent a new login link to " + email,
    }


def resend_email(request):
    if request.method == "GET":
        return not_logged_in(request)

    return do_resend_email(request)


def user_login(request, token, pk):
    user = authenticate(pk=pk, token=token)
    if not user:
        return render(request, "token_error.djhtml", status=403)

    login(request, user)
    return redirect(reverse("manage-user"))


def change_log(request):
    """
    Show a summary of changes based on criteria in the query string. Intended
    mostly for debugging purposes at the moment.
    """
    params = request.GET.copy()
    try:
        since = pytz.utc.localize(
            datetime.strptime(params["since"], "%Y%m%d"))

        del params["since"]
    except KeyError as _kerr:
        raise ErrorResponse("Missing required param: since")
    except ValueError as _err:
        raise ErrorResponse("'since' should have the format YYYYmmdd")

    if "sub_id" in request.GET:
        sub = get_object_or_404(Subscription, pk=request.GET["sub_id"])
    else:
        sub = Subscription(created=since, site_name=request.site_name)
        sub.set_validated_query(params)

    html, _text = render_email_body(
        "updates",
        updates_context(request.user,
                        sub.summarize_updates(since)),
        inline=False)
    return HttpResponse(html)


@with_user
def deactivate_account(_request, user):
    user.profile.deactivate()

    return redirect("/")


def user_logout(request):
    logout(request)

    return redirect("/")


def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request=request)
        if form.is_valid():
            form.save()
            if form.send_email():
                return JsonResponse({
                    "title": "Email sent",
                    "message": "Thanks for your feedback!"
                })
            else:
                return JsonResponse({"title": "Email sent",
                                     "message": "Your comment has been recorded."})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        return HttpResponse("bad request method", status=405)

