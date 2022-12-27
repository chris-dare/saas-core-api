"""The :mod:`app.utils.messaging` module contains resuable utils for messaging users via SMS or email
"""
# Author: Christopher Dare

from enum import Enum
from typing import Any, List, Union

from pydantic import EmailStr

from app.core.config import settings


class MessagingProviders(Enum):
    TWILIO = "twilio"
    SENDGRID = "sendgrid"


class ModeOfMessageDelivery(Enum):
    SMS = "sms"
    EMAIL = "email"


class EmailTemplate(Enum):
    NEW_USER_WELCOME = ""


class MessageClient:
    def __init__(self, provider: str = MessagingProviders.TWILIO, *args, **kwargs):

        if isinstance(provider, str):
            try:
                provider = MessagingProviders(provider)
            except ValueError:
                raise ValueError(f"{provider} is not a supported messaging provider")

        self.provider = provider
        self.from_address = None

        if provider == MessagingProviders.TWILIO:
            from twilio.rest import Client as TwilioClient

            # Your Account SID from twilio.com/console
            account_sid = settings.TWILIO_ACCOUNT_SID
            # Your Auth Token from twilio.com/console
            auth_token = settings.TWILIO_AUTH_TOKEN

            self.client = TwilioClient(account_sid, auth_token)
            self.messaging_service_sid = settings.TWILIO_MESSAGING_SERVICE_SID
        elif provider == MessagingProviders.SENDGRID:
            from sendgrid import SendGridAPIClient

            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        else:
            raise Exception("Unsupported messaging provider")

    def send(self, recipient: str, message: str, template: Any = None):
        raise NotImplementedError(
            "This is an abstract class method which needs implementation in order to be used"
        )


class SMSMessageClient(MessageClient):
    def send(self, recipient: str, message: str, template: Any = None):
        if self.provider == MessagingProviders.TWILIO:
            message = self.client.messages.create(
                messaging_service_sid=self.messaging_service_sid,
                body=message,
                to=recipient,
            )
        else:
            raise Exception("Unsupported messaging provider")


class EmailMessageClient(MessageClient):
    def send(
        self,
        recipients: Union[List, EmailStr],
        subject: str,
        template: EmailTemplate,
    ):
        response = None
        if self.provider == MessagingProviders.TWILIO:
            response = self.client.messages.create(
                messaging_service_sid=self.messaging_service_sid,
                body=message,
                to=recipients,
            )
        elif self.provider == MessagingProviders.SENDGRID:
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=settings.EMAILS_FROM_EMAIL,
                to_emails=recipients,
                subject=subject,
                html_content="<strong>and easy to do anywhere, even with Python</strong>",
            )
            try:
                response = self.client.send(message)
            except Exception as e:
                raise e
        else:
            raise Exception("Unsupported messaging provider")

        return response


def send_sms(
    mobile: str,
    message: str,
    provider: Union[str, MessagingProviders] = MessagingProviders.TWILIO,
):
    client = SMSMessageClient(provider=provider)
    client.send(message=message, recipient=mobile)


def send_email(
    recipients: Union[List[EmailStr], EmailStr],
    message: str,
    template: EmailTemplate,
    subject: str,
    provider: MessagingProviders = MessagingProviders.SENDGRID,
):
    client = EmailMessageClient(provider=provider)
    return client.send(recipients=recipients, subject=subject, template=template)
