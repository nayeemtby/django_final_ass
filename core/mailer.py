from typing import Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def sendMail(to: str, subject: str, template: str, ctx: dict[str, object]):
    message = render_to_string(template, ctx)
    send_email = EmailMultiAlternatives(subject, '', to=[to])
    send_email.attach_alternative(message, "text/html")
    send_email.send()
