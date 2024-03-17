# Healthcare Wallets Overview (Draft)

# Market

Over 600 million Africans do not have healthcare coverage and are reliant on family members in the diaspora to send remittances to cover their healthcare needs. (IMF, 2021). Studies reveal a direct correlation between remittances and greater access to health care (Rwanda Journal of Medicine and Health Sciences, 2018). Additionally, higher remittances per capita were found to be associated with the increased emergency or unplanned hospital visits. This backs our customer research conducted in Ghana which reveals that many individuals and households struggle to save towards their healthcare and find themselves in difficult situations when the need arises.

## How the Innovation Works - Embed healthcare savings into everyday spending

Our solution is a digital healthcare savings wallet that builds contributions from payments and remittances while ensuring that these savings can only be spent on healthcare needs. These which is embedded into remittance and bill payments via APIs in partnership with payment service providers. Everytime a payment is made by a user, a percentage of that gets deposited into their healthcare wallet.

In addition to this, wallets can be topped up by others such as:

* A user's employer
* Family and friends

## Key Concepts

### Healthcare Wallets

A `User` is a person with access to a Serenity app. Users can be administrators, caregivers, patients, payer beneficiaries or practitioners. A user is uniquely identified by their mobile number and email address.

A `User` can sign up as a caregiver. Users can also register dependents - like their daughter, spouse or dad - under them. Users can request for services, pay bills. Dependents may include minors, the elderly or even other registered users

`Payers` are organizations that sponsor healthcare benefits of users, which has 1 or more `Users`, typically known as healthcare beneficiaries. When sponsored by a `Payer`, a `User `is given a `HealthcareWallet `managed by the `Payer `. This wallet is held in trust by a `Trustee `, like Zeepay, Axis or Old Mutual. Futhermore, each `HealthcareWallet `may have a `HealthcarePolicy ` which determines how the wallet's balance may be spent. These policies determine:

* The maximum spend limit
* The copay amount/percentage contributed by the user for all - or different types of bills
* The out of pocket limit for copay contributions by the user
* Healthcare service exclusions
* Number of dependents allowed
* Healthcare providers who can/can't receive payments from this wallet (All or some)

Based on this, here is a sample wallet policy:

- 5% copay for all services
- GHS 5000 out of pocket limit for copayments
- All services covered except hospitalizations and surgeries
- 4 maximum dependents allowed
- Accepted at all Serenity partner hospitals

We would like to provide every Serenity user with a cash wallet held in trust by a licensed trustee like Zeepay or Old Mutual.

We will partner with organizations such as Axis Pensions Trust to provide corporate wallets for employees and their patient dependents.

## Patient records

Patient records are created for users and their dependents. A patient record is uniquely identified by a combination of the following:

* Gender
* Birth date
* Name
* Mobile number

`Patient` identities are verified with a government issued ID. A `Patient`'s Ownership of mobile numbers are verified by SMS OTPs.

Users can also view select health records of themselves of their dependents. Users can view the records of all patients:

1. Whose verified mobile numbers are the same as the `User`.
2. Who have different verified numbers but have confirmed that health records can be disclosed to the requesting `User`

### Healthcare providers

A healthcare provider `Organization` renders care to patients (users and dependents). Each patient receives a unique identifier per provider they interact with. This helps facilitate private identification and exchange of patient records between users and providers.

A healthcare provider also offer commercial `Products` and `HealthcareServices` to patients, which are paid for by `Users` or payer `Organizations`

## OKRs and Roadmap

TBD
