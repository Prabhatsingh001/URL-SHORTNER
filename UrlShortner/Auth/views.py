# from typing import Any
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token, password_reset_token
from django.core.mail import EmailMessage

from django.views.generic import TemplateView


# Create your views here.
CusUser = get_user_model()


# def index(request):
#     return render(request, "index.html")


class IndexView(TemplateView):
    template_name = "index.html"


# def about(request):
#     return render(request, "about.html")


class AboutView(TemplateView):
    template_name = "about.html"


# def contact(request):
#     return render(request, "contact.html")


class ContactView(TemplateView):
    template_name = "contact.html"


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("confirm-password")

        if CusUser.objects.filter(email=email).exists():
            messages.error(request, "email already exists")
            return redirect("accounts:signup")

        if CusUser.objects.filter(username=username).exists():
            messages.error(request, "username already exists")
            return redirect("accounts:signup")

        if password != password2:
            messages.error(request, "passwords do not match")
            return redirect("accounts:signup")
        if len(password) < 8:
            messages.error(request, "password must be at least 8 characters")
            return redirect("accounts:signup")

        if len(username) < 4:
            messages.error(request, "username must be at least 4 characters")
            return redirect("accounts:signup")

        if len(username) > 20:
            messages.error(request, "username must be at most 20 characters")
            return redirect("accounts:signup")
        if len(password) > 20:
            messages.error(request, "password must be at most 20 characters")
            return redirect("accounts:signup")

        user = CusUser.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.set_password(password)  # Hash the password
        user.is_active = False
        user.save()
        messages.success(request, "User created successfully")

        # welcome email
        subject = "Welcome to UrlShortner"
        message = f"hello {user.username} \n\n welcome to URL.ly. Your username is {user.username} and your email is {user.email} \n\n Thank you for signing up"
        to_email = [user.email]
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, to_email, fail_silently=True)

        # account activation email
        current_site = get_current_site(request)
        email_subject = "Email Verification"
        message2 = render_to_string(
            "emails/email_verification.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.send(fail_silently=True)

        return redirect("accounts:login")
    return render(request, "signup.html")


def resend_verification_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = get_object_or_404(CusUser, email=email)

        if user.is_active:
            messages.success(request, "user is already verified!!!")
            return redirect("accounts:login")

        current_site = get_current_site(request)
        email_subject = "Email Verification"
        message2 = render_to_string(
            "emails/email_verification.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.send(fail_silently=True)

        return redirect("accounts:login")
    return render(request, "login.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CusUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CusUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Email verified successfully")
        return redirect("accounts:login")
    else:
        messages.error(request, "Email verification failed")
        return redirect("accounts:login")


def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("index")


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("accounts:login")

        try:
            user = CusUser.objects.get(email=email)
        except CusUser.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            return redirect("accounts:login")

        if not user.is_active:
            messages.error(request, "Please verify your email before logging in.")
            return redirect("accounts:login")

        user = authenticate(request, username=email, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, "Login successful.")
            return redirect("url:home")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("accounts:login")

    return render(request, "login.html")


@login_required()
def profile(request):
    return render(request, "profile.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "email is required to reset password")

        try:
            user = CusUser.objects.get(email=email)
            current_site = get_current_site(request)
            email_subject = "reset password"
            message2 = render_to_string(
                "emails/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": password_reset_token.make_token(user),
                },
            )

            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            email.send(fail_silently=True)
            messages.success(request, "Password reset email sent successfully")
            return redirect("accounts:login")
        except CusUser.DoesNotExist:
            messages.error(request, "User with this email does not exist")
            return redirect("accounts:forgot_password")
    return render(request, "forgot_password.html")


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CusUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CusUser.DoesNotExist):
        user = None

    if user is not None and password_reset_token.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            confirm_password = request.POST.get("confirm-password")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect("accounts:reset_password", uidb64=uidb64, token=token)

            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect("accounts:login")
        return render(request, "reset_password.html", {"user": user})
    else:
        messages.error(request, "Password reset link is invalid or has expired")
        return redirect("accounts:login")


"""
detailview
-> used to create details of anything
-> cannot be paginated
->fetches one object using primary key or slug

"""


# class indexview(TemplateView):
#     template_name = "index.html"

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super().get_context_data(**kwargs)
#         context["books"] = books.objects.all()
#         return context
