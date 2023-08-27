from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class ErrorCode(Enum):
    INACTIVE_USER = "Inactive user"
    INCORRECT_EMAIL_OR_PASSWORD = "Incorrect email or password"
    INVALID_OTP = "Invalid OTP"
    MISSING_EMAIL_OR_MOBILE = "Please provide either email or mobile"
    USER_NOT_FOUND = "We could not find a user with the provided email or mobile"
    FAILED_TO_SEND_OTP = (
        "Sorry, we had trouble sending your verification code. Please try again"
    )


class APIErrorMessage(BaseModel):
    message: str = "Sorry, an error occurred whilst processing your request"
    success: bool = False
    status_code: int = 400
    errors: Optional[list[Any]] = []


class InactiveUserAPIErrorMessage(APIErrorMessage):
    message: str = ErrorCode.INACTIVE_USER.value
    errors: list[Any] = [ErrorCode.INACTIVE_USER.name]


class IncorrectEmailOrPasswordAPIErrorMessage(APIErrorMessage):
    message: str = ErrorCode.INCORRECT_EMAIL_OR_PASSWORD.value
    errors: list[Any] = [ErrorCode.INCORRECT_EMAIL_OR_PASSWORD.name]


class FailedToSendOTPAPIErrorMessage(APIErrorMessage):
    message: str = ErrorCode.FAILED_TO_SEND_OTP.value
    errors: list[Any] = [ErrorCode.FAILED_TO_SEND_OTP.name]


class InvalidOTPAPIErrorMessage(APIErrorMessage):
    message: str = ErrorCode.INVALID_OTP.value
    errors: list[Any] = [ErrorCode.INVALID_OTP.name]


class MissingEmailOrMobileAPIErrorMessage(APIErrorMessage):
    message: str = ErrorCode.MISSING_EMAIL_OR_MOBILE.value
    errors: list[Any] = [ErrorCode.MISSING_EMAIL_OR_MOBILE.name]


class UserNotFoundAPIErrorMessage(APIErrorMessage):
    message: str = ErrorCode.USER_NOT_FOUND.value
    errors: list[Any] = [ErrorCode.USER_NOT_FOUND.name]


def get_api_error_message(error_code: ErrorCode, as_dict=True) -> APIErrorMessage:
    """Returns an API error message based on the error code
    Parameters
    ----------
    error_code : ErrorCode
        The error code
    as_dict : bool, optional
        Whether to return the error message as a dictionary, by default True

    Returns
    -------
    APIErrorMessage
        The API error message
    """
    if error_code == ErrorCode.INACTIVE_USER:
        error_message = InactiveUserAPIErrorMessage()
    elif error_code == ErrorCode.INCORRECT_EMAIL_OR_PASSWORD:
        error_message = IncorrectEmailOrPasswordAPIErrorMessage()
    elif error_code == ErrorCode.INVALID_OTP:
        error_message = InvalidOTPAPIErrorMessage()
    elif error_code == ErrorCode.MISSING_EMAIL_OR_MOBILE:
        error_message = MissingEmailOrMobileAPIErrorMessage()
    elif error_code == ErrorCode.USER_NOT_FOUND:
        error_message = UserNotFoundAPIErrorMessage()
    elif error_code == ErrorCode.FAILED_TO_SEND_OTP:
        error_message = FailedToSendOTPAPIErrorMessage()
    else:
        error_message = APIErrorMessage()
    # convert to dictionary if required
    if as_dict:
        error_message = error_message.dict()
    return error_message
