import uuid

import phonenumbers
import sentry_sdk
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import RegexValidator
from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .managers import UserManager

# Custom Authentication User Model
from app.utils.security import generate_password

class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.TextField(unique=True, default=uuid.uuid4, editable=False, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    mobile = models.CharField(
        _("mobile"), max_length=30, blank=True, unique=True, validators=[phone_regex]
    )
    national_mobile_number = models.CharField(
        _("mobile number in national format"), max_length=30, blank=True, null=True,
    )
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    state = models.CharField(_("state"), default="new_user", max_length=200)

    # User CRUD manager
    objects = UserManager()

    # Custom django user configurations
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        from app.utils.parser import parse_mobile_number
        self.first_name = self.first_name.capitalize() if self.first_name else self.first_name
        self.last_name = self.last_name.capitalize() if self.last_name else self.last_name
        # update national phone number and save
        old_mobile = self.mobile
        try:
            self.mobile = parse_mobile_number(self.mobile)
            self.national_mobile_number = parse_mobile_number(self.mobile, international_format=False)
        except (ValidationError) as e:
            if isinstance(e, Exception):
                sentry_sdk.capture_exception(error=e)
            sentry_sdk.capture_message(message=f"Invalid number for {self.fullname} ({self.mobile}: {e}")
        try:
            return super(User, self).save(*args, **kwargs)
        except IntegrityError as e:
            self.mobile = old_mobile
            return super(User, self).save(*args, **kwargs)

    def get_phone_number(self) -> phonenumbers.PhoneNumber:
        """Returns a user's mobile as an instance of phonenumbers.PhoneNumber"""
        mobile = None
        if self.mobile:
            mobile = self.mobile
            if mobile[0] != "+":
                mobile = f"+{mobile}"
            try:
                mobile = phonenumbers.parse(mobile)
            except phonenumbers.NumberParseException as err:
                sentry_sdk.capture_exception(error=err)
                mobile = None
        return mobile

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
