# create enums for user gender

import enum


class AdministrativeGender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"


class NationalIdType(str, enum.Enum):
    NATIONAL_IDENTIFICATION_NUMBER = "National Identification Number"
    BANK_VERIFICATION_NUMBER = "Bank Verification Number"
    PASSPORT = "Passport"
    DRIVERS_LICENCE = "Drivers Licence"
    VOTERS_CARD = "Voters Card"
