from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager

# Custom manager for user


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, payload: dict):
        payload.setdefault("is_superuser", False)
        payload["password"] = self.make_random_password()
        user = self._create_user(**payload)
        return user

    # (Note) Will come back to this later. (?)How will we treat super user accounts on the system??
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("uuid", str(uuid4()))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
