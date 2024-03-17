# create enums for user gender

import enum

import pycountry


class AdministrativeGender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class NamePrefixType(str, enum.Enum):
    MR = "Mr"
    MISS = "Miss"
    MRS = "Mrs"
    DR = "Dr"
    MASTER = "Master"
    PROF = "Prof"
    HON = "Hon"


class MedicalDegreeType(str, enum.Enum):
    DOCTOR_OF_MEDICINE = "MD"
    DOCTOR_OF_CHIROPRACTIC = "DC"
    """
    TODO: Update textchoieces with the following. To be done when this is needeed
    DDS - Doctor of Dental Surgery, Doctor of Dental Science
    DMD - Doctor of Dental Medicine, Doctor of Medical Dentistry
    DO or OD - Doctor of Optometry, Doctor of Osteopathic Medicine
    DPM - Doctor of Podiatric Medicine
    DPT - Doctor of Physical Therapy
    DScPT - Doctor of Science in Physical Therapy
    DSN - Doctor of Science in Nursing
    DVM - Doctor of Veterinary Medicine
    ENT - Ear, nose and throat specialist
    GP - General Practitioner
    GYN - Gynecologist
    MD - Doctor of Medicine
    MS - Master of Surgery
    OB/GYN - Obstetrician and Gynecologist
    PharmD - Doctor of Pharmacy
    """


class NationalIdType(str, enum.Enum):
    NATIONAL_IDENTIFICATION_NUMBER = "National Identification Number"
    BANK_VERIFICATION_NUMBER = "Bank Verification Number"
    PASSPORT = "Passport"
    DRIVERS_LICENCE = "Drivers Licence"
    VOTERS_CARD = "Voters Card"


class OrganizationType(str, enum.Enum):
    INSURANCE_COMPANY = "ins"
    PAYER = "pay"
    HEALTHCARE_PROVIDER = "prov"


class PractitionerType(str, enum.Enum):
    CLINICAL_STAFF = "clinical-staff"
    NON_CLINICAL_STAFF = "non-clinical-staff"
    UNKNOWN = "unknown"  # a proper value is applicable but not known


class OperatingCountryType(str, enum.Enum):
    """Countries where Serenity Corporate Care operates
    All enum names should be in the ISO 3166-1 alpha-2 format.
    All enum values should be the short name of a country
    e.g.
        GH = "Ghana"
    """

    GH = "Ghana"

    def as_valueset(country: str = None):
        import schemas

        valueset = []
        countries = [OperatingCountryType(country)] if country else OperatingCountryType
        for i in countries:
            _country: pycountry.countries.Country = pycountry.countries.get(
                alpha_2=i.name
            )
            if not _country:
                continue  # account for errors in enum names.
            regions = [
                str(j.name) for j in pycountry.subdivisions.get(country_code=i.name)
            ]
            valueset.append(
                schemas.GenericValueset(
                    name=i.value,
                    choices=regions,
                    description=f"Subdivisions for '{_country.official_name}'",
                ),
            )
        return valueset


class OrganizationVerificationType(str, enum.Enum):
    TAX_IDENTIFICATION_NUMBER = "tax-identification-number"
    CERTIFICATE_OF_REGISTRATION = "certificate-of-registration"
    CORPORATE_BANK_ACCOUNT = "corporate-bank-account"
    CORPORATE_MOBILE_MONEY_ACCOUNT = "corporate-mobile-money-account"


class PaymentContributionType(str, enum.Enum):
    COPAY = "copay"
    COINSURANCE = "coinsurance"


class WalletCurrencyType(str, enum.Enum):
    GHS = "GHS"
    # NGN = "NGN"
    # USD = "USD"


class WalletStatusType(str, enum.Enum):
    CREATED = "created"
    ACTIVE = "active"
    SUSPENDED = "suspended"


COUNTRY_CURRENCY_MAP = {
    OperatingCountryType.GH.value: WalletCurrencyType.GHS.value,
}
