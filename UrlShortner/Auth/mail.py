from django.core.mail import send_mail
from django.conf import settings

# from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.core.mail import EmailMessage


def send_welcome_email(user):
    subject = "Welcome to UrlShortner"
    message = f"hello {user.username} \n\n welcome to URL.ly. Your username is {user.username} and your email is {user.email} \n\n Thank you for signing up"
    to_email = [user.email]
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, to_email, fail_silently=True)


def send_verification_mail(user):
    current_site = settings.SITE_DOMAIN
    protocol = settings.PROTOCOL
    email_subject = "Email Verification"
    message2 = render_to_string(
        "emails/email_verification.html",
        {
            "user": user,
            "protocol": protocol,
            "domain": current_site,
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


def send_contact_email(contact):
    email_subject = f"New Notofication {contact.email}"
    message = f"""
you have recieved a new message

name: {contact.name}
Email: {contact.email}

message: {contact.message}
    """
    team_mail = ["ghostcoder420@gmail.com"]

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, team_mail)
    email.send(fail_silently=False)
