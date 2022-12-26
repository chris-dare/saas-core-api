"""The :mod:`app.utils.messaging` module contains resuable utils for messaging users via SMS or email
"""
# Author: Christopher Dare

from enum import Enum
from typing import Any

from app.core.config import settings

class MessagingProviders(Enum):
    TWILIO = "twilio"


class ModeOfMessageDelivery(Enum):
    SMS = "sms"
    EMAIL = "email"


class MessageClient:

    def __init__(self, provider: str = MessagingProviders.TWILIO, *args, **kwargs):

        self.provider = provider
        self.from_address = None

        if provider == MessagingProviders.TWILIO:
            from twilio.rest import Client as TwilioClient

            # Your Account SID from twilio.com/console
            account_sid = settings.TWILIO_ACCOUNT_SID
            # Your Auth Token from twilio.com/console
            auth_token  = settings.TWILIO_AUTH_TOKEN

            self.client = TwilioClient(account_sid, auth_token)
            self.messaging_service_sid = settings.TWILIO_MESSAGING_SERVICE_SID
        else:
            raise Exception("Unsupported messaging provider")

    def send(self, recipient: str, message: str, template: Any = None):
        raise NotImplementedError("This is an abstract class method which needs implementation in order to be used")



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


def send_sms(mobile: str, message: str, provider: str = MessagingProviders.TWILIO):
    client = SMSMessageClient(provider=provider)
    client.send(message=message, recipient=mobile)
