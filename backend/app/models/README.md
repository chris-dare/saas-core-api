# # Overview of major entities and their relationships

A `User` is a person with access to a Serenity app. Users can be administrators, caregivers, patients, payer beneficiaries or practitioners. A user is uniquely identified by their mobile number. They also have a unique email address, for communication purposes.

A `User` can create an organization `(Payer)`, which has 1 or more `Users`, typically known as healthcare beneficiaries.

Each `User` is given a `HealthcareWallet `managed by the `Payer`. One or more users may be administators of a `Payer`. Futhermore, each `HealthcareWallet `may has a `HealthcarePolicy ` which determines how the wallet's balance may be spent. These policies determine:

* The maximum spend limit
* The copay amount/percentage for all - or different types of bills
* The patient's out of pocket limit for copayments
* Healthcare service exclusions
* Number of dependents allowed
* Healthcare providers who can receive payments from this wallet (All or some)

A User can sign up as a caregiver. Users can also register dependents under them. A dependent is a patient whom the user can request for services, pay bills and view select health records on behalf of a patient. Dependents may include minors, the elderly or even other registered users

Patient records are created for users and their dependents. A patient record is uniquely identified by a combination (composite key) of the following:

* Gender
* Birth date
* Name
* Mobile number

`Patient` identities are verified with a government issued ID. A `Patient`'s Ownership of mobile numbers are verified by SMS OTPs.

Users can view the records of all patients:

1. whose verified mobile numbers are the same as the `User`.
2. who have different verified numbers but have confirmed that access be granted to the `User`

Healthcare providers

A healthcare provider `Organization` renders care to patients (users and dependents). Each patient receives a unique identifier per provider they interact with. This helps facilitate private identification and exchange of patient records between users and providers.

A healthcare provider also offer commercial `Products` and `HealthcareServices` to patients, which are paid for by `Users` or payer `Organizations`
