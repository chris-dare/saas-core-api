"""The :mod:`app.utils.messaging` module contains resuable utils for messaging users via SMS or email
"""
import json
from enum import Enum
from typing import Any, List, Optional, Union

import requests
from app.core.config import settings
from pydantic import BaseModel, EmailStr

# Author: Christopher Dare


class MessagingProviders(Enum):
    TWILIO = "twilio"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    HUBTEL = "hubtel"


class ModeOfMessageDelivery(Enum):
    SMS = "sms"
    EMAIL = "email"


class MessageClientResponse(BaseModel):
    is_sent: bool = False
    response: Optional[dict] = None
    message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


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
        elif provider == MessagingProviders.HUBTEL:
            self.api_base_url = f"{settings.HUBTEL_SMS_BASE_URL}/messages/send"
            self.client_id = settings.HUBTEL_CLIENT_ID
            self.api_key = settings.HUBTEL_CLIENT_SECRET
            self.from_address = settings.HUBTEL_FROM_ADDRESS
        elif provider == MessagingProviders.SENDGRID:
            from sendgrid import SendGridAPIClient

            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        elif provider == MessagingProviders.MAILGUN:
            self.api_key = settings.MAILGUN_API_KEY
            self.api_base_url = settings.MAILGUN_BASE_URL
        else:
            raise Exception("Unsupported messaging provider")

    def send(self, recipient: str, message: str, template: Any = None):
        raise NotImplementedError(
            "This is an abstract class method which needs implementation in order to be used"
        )


class SMSMessageClient(MessageClient):
    def send(self, recipient: str, message: str, template: Any = None):
        client_response = MessageClientResponse()
        if self.provider == MessagingProviders.TWILIO:
            client_response = self.client.messages.create(
                messaging_service_sid=self.messaging_service_sid,
                body=message,
                to=recipient,
            )
        elif self.provider == MessagingProviders.HUBTEL:
            response = requests.get(
                f"{self.api_base_url}?clientsecret={self.api_key}&clientid={self.client_id}from={self.from_address}&to={recipient}&content={message}",
                auth=(self.client_id, self.api_key),
            )
            if response.status_code == 201 or response.status_code == 200:
                client_response.is_sent = response.json().get("status") != "0"
                client_response.response = client_response.json()
                client_response.message = (
                    "SMS sent successfully!"
                    if client_response.is_sent
                    else "SMS failed to send!"
                )
        else:
            raise Exception("Unsupported messaging provider")
        return client_response


class EmailMessageClient(MessageClient):
    def send(
        self,
        recipients: Union[List, EmailStr],
        subject: str,
        message: Optional[str] = None,
        template: Optional[str] = None,
        template_vars: Optional[BaseModel] = None,
    ):
        client_response = MessageClientResponse()
        recipients if isinstance(recipients, list) else [str(recipients)]
        html_content = None
        if not message and not template:
            raise ValueError(
                "Please provide a template or message in order to send an email!"
            )
        if message:
            html_content = message
        if self.provider == MessagingProviders.SENDGRID:
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=settings.EMAILS_FROM_EMAIL,
                to_emails=recipients,
                subject=subject,
                html_content=html_content,
            )
            try:
                client_response.response = self.client.send(message)
            except Exception as e:
                raise e
        elif self.provider == MessagingProviders.MAILGUN:
            recipients = recipients if isinstance(recipients, list) else [recipients]
            mailgun_data = {
                "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
                "to": recipients,
                "subject": f"{subject}",
            }
            if template:
                mailgun_data["template"] = template
                mailgun_data["h:X-Mailgun-Variables"] = json.dumps(template_vars)
            elif message:
                mailgun_data["text"] = message
            try:
                client_response.response = requests.post(
                    f"{self.api_base_url}",
                    auth=("api", self.api_key),
                    data=mailgun_data,
                )
                client_response.is_sent = (
                    200 <= client_response.response.status_code < 300
                )
                if client_response.is_sent:
                    client_response.message = "Email sent successfully!"
            except Exception as e:
                client_response.response = None
                client_response.is_sent = False
                client_response.message = (
                    f"Failed to send message via {self.__class__}: {str(e)}"
                )
                # TODO: Log this error via Sentry
        else:
            raise Exception("Unsupported messaging provider")

        return client_response


def send_sms(
    mobile: str,
    message: str,
    provider: Union[str, MessagingProviders] = MessagingProviders.TWILIO,
):
    client = SMSMessageClient(provider=provider)
    return client.send(message=message, recipient=mobile)


mailgun_client = EmailMessageClient(provider=MessagingProviders.MAILGUN)
