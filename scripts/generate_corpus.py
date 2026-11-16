"""
Generate the SENTINEL document corpus used for this assignment.

The corpus is SYNTHETIC. It was written for coursework and summarises the
*kind* of guidance found in RBI / NPCI circulars in plain language, together
with fictional fraud playbooks, investigator case notes and chargeback
narratives. It is not official regulatory text. Verify any rule against the
current RBI / NPCI circular before relying on it.

Output layout (one folder per document type, which the loader uses as the
`doc_type` payload field):

    data/raw/
        guideline/      RBI and NPCI guideline summaries
        playbook/       fraud-typology investigation playbooks
        investigator_note/
        chargeback/     chargeback / dispute narratives

Raw files deliberately contain the noise real exports have (repeated
headers, page footers, smart quotes, odd whitespace, a few exact duplicate
files) so that the cleaning step has something real to do.

Usage:
    python scripts/generate_corpus.py            # writes data/raw
    python scripts/generate_corpus.py --seed 7   # different case details
"""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

DISCLAIMER = (
    "Note: synthetic summary prepared for the SENTINEL coursework corpus. "
    "It paraphrases public guidance and is not an official RBI or NPCI text."
)

# --------------------------------------------------------------------------
# 1. Guideline summaries (RBI / NPCI)
# --------------------------------------------------------------------------
GUIDELINES: list[tuple[str, str, str, list[tuple[str, str]]]] = [
    ("rbi-customer-liability", "RBI", "Customer liability in unauthorised electronic banking transactions", [
        ("Purpose", "This guidance sets out how much of a loss a customer bears when money leaves their account through an electronic transaction they did not authorise. It covers internet banking, mobile banking, UPI, card-present and card-not-present transactions, and prepaid instruments issued by banks. The aim is to give customers confidence in digital channels while making banks responsible for the security of the systems they run."),
        ("Zero liability", "A customer has zero liability when the unauthorised transaction happened because of contributory fraud, negligence or a deficiency on the part of the bank, whether or not the customer reported it. A customer also has zero liability when the breach lies elsewhere in the system, neither with the bank nor with the customer, provided the customer tells the bank within three working days of receiving the transaction alert."),
        ("Limited liability", "When the customer reports a third-party breach between four and seven working days after the alert, liability is limited to the transaction value or a fixed cap, whichever is lower. The cap depends on the account type: about five thousand rupees for basic savings accounts, ten thousand rupees for most savings accounts and smaller credit cards, and twenty-five thousand rupees for current accounts and higher-limit credit cards. Reports made after seven working days are handled under the bank's board-approved policy."),
        ("Customer negligence", "Where the loss is due to the customer's own negligence, such as sharing a password, PIN or OTP, the customer bears the full loss until the unauthorised transaction is reported. Any loss after the report is borne by the bank. Investigators should therefore record exactly when the customer first reported the issue and through which channel."),
        ("Bank obligations", "The bank must credit the disputed amount to the customer's account as a shadow reversal within ten working days of the report, without waiting for an insurance claim. The complaint must be resolved and liability established within ninety days. The burden of proving customer liability lies on the bank, so case files must hold logs, device data and alert delivery records."),
        ("Reporting channels", "Banks must give customers round-the-clock ways to report unauthorised transactions, including a website link, an SMS reply option, a toll-free number and a branch option. Each report must be acknowledged immediately with a complaint number and a timestamp, because the timestamp decides which liability band applies."),
    ]),
    ("rbi-fraud-risk-management", "RBI", "Fraud risk management and fraud reporting by banks", [
        ("Scope", "Banks are expected to have a board-approved fraud risk management policy, a dedicated fraud risk management function and a special committee of the board that monitors large-value frauds. The policy must cover prevention, early detection, investigation, reporting to the regulator and to law enforcement, and staff accountability."),
        ("Early warning signals", "Banks should run an early warning signal framework for credit and transaction accounts. Signals include sudden spikes in transaction volume, frequent changes of registered mobile number or email, many small credits followed by rapid withdrawals, and transactions with entities already flagged. Accounts that breach thresholds are red-flagged and reviewed within a fixed time."),
        ("Natural justice", "Before an account holder or borrower is classified as a fraud, the bank must give them notice of the findings and a reasonable opportunity to respond. The decision must be recorded with reasons. Investigators should keep their notes factual and evidence-based because they may be shared in this process."),
        ("Reporting", "Frauds must be reported to the regulator through the prescribed online system within the defined timeline after detection, and cases above a threshold must be referred to law enforcement. Delayed reporting is itself a supervisory concern, so the date of detection must be recorded accurately in the case management system."),
        ("Staff accountability", "Every fraud case should include a staff accountability review that checks whether controls were bypassed, whether alerts were ignored and whether any employee was involved. Findings feed back into process changes and training."),
    ]),
    ("rbi-digital-payment-security", "RBI", "Digital payment security controls", [
        ("Governance", "Regulated entities offering internet and mobile banking or card payments must put in place a governance framework for digital payment security that is approved by the board. It should cover risk assessment of each product, secure development, testing before release and periodic review."),
        ("Device and application security", "Mobile banking and UPI applications should bind the customer to a specific device and SIM, detect rooted or jail-broken phones, block screen overlay and screen-recording where possible, and refuse to run when remote access tools are detected. Applications must time out idle sessions and must not store credentials in plain text."),
        ("Transaction monitoring", "Entities should monitor transactions in real time using rules and risk scoring. Typical controls include velocity limits on the number and value of transactions, limits on new payees, extra checks for a first transaction from a new device, and alerts when the location or behaviour of a session is unusual."),
        ("Customer alerts", "Customers must receive an alert for every transaction and for every change to sensitive settings such as mobile number, email, device registration or limits. Alerts should say how to report a transaction the customer does not recognise."),
        ("Change of device", "When a customer registers a new device, the entity should apply a cooling period or reduced limits for high-value transactions, re-verify the customer through more than one factor, and notify the old contact details. A new device followed quickly by a large payment to a new beneficiary is a classic account-takeover pattern."),
    ]),
    ("rbi-authentication", "RBI", "Authentication of digital payment transactions", [
        ("Two factors", "Digital payment transactions should be authenticated with at least two distinct factors drawn from something the customer knows, something the customer has and something the customer is. At least one factor should be dynamic, meaning it is created for the transaction and cannot be reused."),
        ("Risk-based authentication", "Entities may apply stronger checks to riskier transactions, using signals such as amount, device history, location, beneficiary history and behavioural patterns. Low-risk transactions can follow a lighter path as long as the minimum standard is met."),
        ("Beyond SMS OTP", "Guidance encourages moving beyond SMS one-time passwords alone, because SIM swap and OTP phishing attacks target them. Options include app-based authentication, device binding with a PIN, biometrics and passkeys."),
        ("Cross-border card-not-present", "For card-not-present transactions from abroad on Indian-issued cards, issuers are expected to validate the transaction when the overseas merchant or acquirer asks for authentication."),
    ]),
    ("rbi-kyc-cdd", "RBI", "Know Your Customer and customer due diligence", [
        ("Risk categorisation", "Customers are placed in low, medium or high risk categories based on identity, occupation, geography, nature of business, expected transaction pattern and delivery channel. The category decides how often KYC is refreshed and how closely transactions are watched."),
        ("Periodic updation", "KYC must be refreshed periodically: more often for high-risk customers and less often for low-risk ones. A failed or overdue KYC refresh is a useful signal when an account suddenly starts receiving many credits."),
        ("Video KYC", "Video-based customer identification is allowed when it is carried out live by trained staff, with liveness checks, geo-tagging inside India, capture of an official document and random questions. Recorded sessions must be kept for audit."),
        ("Beneficial ownership", "For companies, partnerships and trusts, the entity must identify the natural persons who ultimately own or control the customer. Shell entities with nominee directors are a common vehicle for mule accounts and transaction laundering."),
        ("Monitoring", "Accounts should be monitored against the declared profile. A student account that receives hundreds of small UPI credits from unrelated people and moves the money out within minutes does not match its profile and should be reviewed."),
    ]),
    ("rbi-failed-transactions-tat", "RBI", "Turnaround time for failed transactions and compensation", [
        ("Principle", "When a transaction fails because of a technical issue, communication failure or non-availability of funds at the beneficiary end, the customer's money must be returned within a defined turnaround time. If the provider misses that time, it must pay compensation to the customer without the customer having to ask."),
        ("UPI", "For a UPI transaction where the customer's account is debited but the beneficiary account is not credited, the amount should be auto-reversed by the next working day. Delays beyond that attract compensation of one hundred rupees per day."),
        ("Cards and ATMs", "For an ATM withdrawal where the account is debited but cash is not dispensed, the reversal should happen within five days. For card transactions at merchants, the acquirer should complete the reversal within the prescribed time."),
        ("Dispute handling", "Customers should be able to raise a failed-transaction complaint in the app. Investigators should distinguish genuine failed transactions from false claims by checking switch logs and the beneficiary bank's response code."),
    ]),
    ("rbi-integrated-ombudsman", "RBI", "Integrated ombudsman scheme and internal grievance redress", [
        ("Escalation", "A customer can approach the ombudsman if their complaint to the regulated entity is rejected, is not satisfactorily resolved, or receives no reply within thirty days. The scheme covers banks, non-bank payment system participants and many NBFCs."),
        ("Internal ombudsman", "Larger entities must appoint an internal ombudsman who reviews complaints that the entity proposes to reject in whole or in part. This creates an independent check before a customer is told no."),
        ("Implication for fraud teams", "Every rejected fraud dispute may be reviewed later. Case notes should therefore show the evidence used, the timeline of the customer's report and the reasoning behind the liability decision."),
    ]),
    ("rbi-cyber-incident-reporting", "RBI", "Cyber security incident reporting", [
        ("Timelines", "Regulated entities must report significant cyber security incidents to the regulator quickly, and the national computer emergency response team expects reports within six hours of noticing certain incidents. Examples include data breaches, compromise of payment systems, ransomware and large-scale phishing aimed at customers."),
        ("Customer-facing phishing", "When fraudsters clone the entity's website or app, or run fake customer-care numbers, the entity should report the domains, request takedown and warn customers through its channels."),
        ("Link to fraud operations", "A spike in account-takeover cases with the same pattern may be the visible side of a cyber incident. Fraud and security teams should share indicators such as IP ranges, device fingerprints and phishing domains."),
    ]),
    ("rbi-card-tokenisation", "RBI", "Card tokenisation and card-on-file", [
        ("Tokenisation", "Merchants and payment aggregators are not allowed to store actual card numbers. Card details are replaced with tokens that are specific to the merchant and device. A stolen token is of limited use outside its context."),
        ("Customer consent", "Tokenisation must be done only with explicit customer consent and additional factor authentication. Customers must be able to view and delete their tokens."),
        ("Fraud angle", "Card-testing attacks and data breaches at merchants are less damaging when card-on-file data is tokenised. Investigators looking at card-not-present fraud should check whether the transaction used a token, and which token requestor created it."),
    ]),
    ("rbi-emandate-recurring", "RBI", "E-mandates for recurring card and UPI payments", [
        ("Registration", "A recurring payment mandate on a card or UPI must be registered with additional factor authentication. The customer must get a pre-debit notification before each charge, with an option to opt out."),
        ("Thresholds", "Recurring debits up to a set value can run without additional authentication for each charge, while higher amounts need it. Some categories such as insurance premiums and mutual fund subscriptions have a higher threshold."),
        ("Disputes", "Many chargebacks labelled as subscription fraud are cases where the customer forgot a mandate or a free trial converted to paid. Investigators should check the mandate registration record and pre-debit notification log before treating the case as unauthorised."),
    ]),
    ("rbi-payment-aggregators", "RBI", "Payment aggregators and merchant onboarding", [
        ("Merchant due diligence", "Payment aggregators must carry out due diligence on merchants they onboard, including KYC of the business and its owners, verification of the website or business premises, and checks that the declared business category matches the actual activity."),
        ("Escrow", "Funds collected for merchants must be kept in an escrow account and settled within defined timelines. Aggregators must not use merchant funds for their own purposes."),
        ("Transaction laundering", "Transaction laundering happens when an onboarded merchant processes payments for another, often illegal, business. Signals include a mismatch between declared category and ticket size, sudden volume growth, high refund or chargeback ratios and customers who complain about a different business name on their statement."),
    ]),
    ("rbi-ppi", "RBI", "Prepaid payment instruments", [
        ("Types", "Prepaid wallets come in small and full-KYC variants. Small PPIs have low loading limits and cannot be used for cash withdrawal or fund transfer to bank accounts. Full-KYC PPIs have higher limits and broader use."),
        ("Fraud risk", "Wallets are attractive for layering stolen money because loads and spends are fast. Watch for many wallets loaded from one card, wallets loaded and emptied within minutes, and wallets linked to devices seen in other fraud cases."),
        ("Liability", "The customer liability framework for unauthorised transactions also applies to PPIs, so wallet issuers must keep the same evidence as banks."),
    ]),
    ("rbi-mule-accounts", "RBI", "Mule accounts and their detection", [
        ("What a mule account is", "A mule account is a bank account used to receive and move the proceeds of fraud. The holder may be complicit, may have rented the account for a fee, or may be unaware that their KYC was misused. Mule networks let fraudsters break the money trail across many accounts and banks."),
        ("Detection", "Banks are encouraged to use data analytics and machine learning models to spot mule accounts. Typical features include account age, the ratio of inward to outward flows, the number of unique remitters, time between credit and debit, device sharing across accounts and links to complaints on the national cybercrime portal."),
        ("Action", "Suspected mule accounts should be frozen or debit-restricted following the bank's policy, the holder should be contacted for an explanation, and the case should be reported. Opening accounts in bulk through the same business correspondent or the same device is a strong signal."),
    ]),
    ("rbi-outsourcing-third-party", "RBI", "Outsourcing and third-party risk in payments", [
        ("Accountability", "A regulated entity remains responsible for activities it outsources, including customer onboarding, collections and technology services. Contracts must give the entity audit rights and require prompt reporting of incidents."),
        ("Insider risk", "Staff at outsourced call centres and business correspondents can misuse customer data. Controls include masking of sensitive fields, access logging, and periodic review of who looked at which account."),
    ]),
    ("npci-upi-dispute-redressal", "NPCI", "UPI dispute and complaint redressal", [
        ("Online dispute resolution", "UPI apps must let customers raise a complaint about a transaction inside the app. The complaint flows through the UPI system to the remitter bank, the beneficiary bank and the app provider so that each party can act on it within set timelines."),
        ("Auto-reversal and status checks", "Many complaints are resolved automatically: if the beneficiary bank confirms that the credit did not happen, the remitter bank reverses the debit. Complaint handlers should first check the final transaction status before manual investigation."),
        ("Escalation path", "Unresolved complaints move from the app provider to the bank, then to the NPCI dispute mechanism and finally to the ombudsman. Each step has a turnaround time that should be tracked in the case system."),
        ("Fraud complaints", "A complaint that a customer was tricked into paying is not the same as a failed transaction. It is handled as a fraud report: the remitter bank asks the beneficiary bank to place a hold on the funds if they are still available, and the customer is advised to file a report on the national cybercrime portal."),
    ]),
    ("npci-upi-chargeback", "NPCI", "UPI chargeback, re-presentment and arbitration", [
        ("Chargeback", "The remitter bank can raise a chargeback on behalf of its customer for reasons such as goods or services not delivered, a duplicate debit, a debit without a matching credit, or an amount different from what was agreed. A chargeback must be raised within the allowed window after the transaction date."),
        ("Re-presentment", "The beneficiary bank, usually on behalf of the merchant, can contest the chargeback by re-presenting the transaction with evidence such as delivery proof, a signed invoice or service logs. The remitter bank then reviews the evidence."),
        ("Pre-arbitration and arbitration", "If the parties still disagree, the case goes to pre-arbitration and then to arbitration by the NPCI committee, which decides based on the evidence submitted by both banks."),
        ("Good practice", "Fraud teams should tag chargebacks that look like first-party misuse, such as a customer who disputes a delivery that was signed for. Repeated chargebacks by the same customer across merchants should feed into risk scoring."),
    ]),
    ("npci-upi-limits", "NPCI", "UPI transaction limits", [
        ("Standard limit", "The standard per-transaction UPI limit for person-to-person payments is one lakh rupees, and banks can set lower limits for their customers. Many banks also cap the number of transactions per day."),
        ("Higher category limits", "Certain merchant categories such as tax payments, hospitals, educational institutions, capital markets and insurance can accept higher UPI amounts. Investigators should check the merchant category code before treating a high-value transaction as unusual."),
        ("New user limits", "Banks and apps often apply a reduced limit for the first day after a customer registers on a new device or app. This cooling-off limit is a key control against account takeover."),
    ]),
    ("npci-upi-device-binding", "NPCI", "UPI device and SIM binding", [
        ("Binding", "When a customer sets up UPI, the app verifies that the SIM holding the registered mobile number is present in the device, usually by sending an outbound SMS. The UPI profile is then bound to that device."),
        ("Re-registration", "Changing the phone or SIM requires the customer to re-register and to set or validate the UPI PIN with debit card details or Aadhaar-based OTP. This is the step attackers target in SIM swap and account takeover."),
        ("Signals", "A device change followed within minutes by a UPI PIN reset and a high-value payment to a new payee is a strong account-takeover pattern. So is the same device registering UPI profiles for many different mobile numbers."),
    ]),
    ("npci-upi-collect", "NPCI", "UPI collect requests and pull-payment risk", [
        ("How collect works", "A collect request lets a payee ask a payer to approve a debit. The payer sees the request in their app and must enter their UPI PIN to approve it."),
        ("Abuse", "Fraudsters send collect requests with notes such as 'refund', 'cashback' or 'receive money', hoping the victim thinks entering the PIN will receive funds. Entering the UPI PIN always sends money; it never receives it."),
        ("Controls", "NPCI has moved to restrict person-to-person collect requests and limit their value. Apps should show clear warnings on collect requests and let customers block unknown requesters."),
    ]),
    ("npci-upi-lite", "NPCI", "UPI Lite and small-value on-device payments", [
        ("Design", "UPI Lite lets customers make small-value payments from an on-device balance without entering a UPI PIN for each payment. The balance and per-payment limits are kept small to limit loss."),
        ("Risk", "If a phone is stolen while unlocked, the Lite balance can be spent. Customers should be able to disable Lite and move the balance back to their account remotely."),
    ]),
    ("npci-frm", "NPCI", "Fraud risk monitoring in UPI", [
        ("Central monitoring", "NPCI provides fraud risk monitoring services that score UPI transactions using patterns seen across the whole network. Banks combine this score with their own rules before approving or declining a transaction."),
        ("Shared intelligence", "Network-level monitoring can spot a mule account receiving payments from customers of many banks, which a single bank cannot see. Banks are expected to act on alerts and report confirmed fraud back to improve the models."),
        ("Feedback loop", "Investigator outcomes, such as confirmed fraud, false positive or customer error, should be recorded in a structured way so they can be fed back as labels for model training."),
    ]),
    ("npci-aeps", "NPCI", "Aadhaar Enabled Payment System fraud", [
        ("How AePS works", "AePS lets customers withdraw cash, check balances and transfer money at a business correspondent point using their Aadhaar number and fingerprint."),
        ("Fraud patterns", "Fraudsters have used cloned fingerprints made from leaked property or registration records to withdraw money from victims' accounts without OTP. Victims often notice only when they see an SMS for a withdrawal they did not make."),
        ("Controls", "Customers can lock their Aadhaar biometrics, and banks and NPCI apply liveness detection and velocity limits per business correspondent. Investigators should check the terminal ID, operator and location of each withdrawal."),
    ]),
    ("npci-upi-circle", "NPCI", "Delegated UPI payments", [
        ("Delegation", "A primary user can let a trusted secondary user make UPI payments from the primary user's account, either with full delegation inside a monthly limit or with approval for each payment."),
        ("Risk", "Delegation can be abused in coercion and family-fraud cases. Investigators should check who set up the delegation, when, and from which device, before treating a secondary user's payment as unauthorised."),
    ]),
    ("mha-cybercrime-reporting", "MHA", "National cybercrime reporting and the 1930 helpline", [
        ("Reporting", "Victims of financial cyber fraud can call the 1930 helpline or file a complaint on the national cybercrime reporting portal. The complaint is shared with banks and payment providers through the citizen financial cyber fraud reporting system."),
        ("Golden hour", "Funds can often be frozen if the complaint reaches the beneficiary bank before the fraudster moves the money onward. Reporting within the first hour gives the best chance of recovery."),
        ("Bank action", "On receiving a complaint, banks should place a lien or hold on the amount in the beneficiary account, trace onward transfers and update the status on the system so that the trail can be followed across banks."),
    ]),
    ("npci-imps-neft-recall", "NPCI", "Recall of fraudulent IMPS and account transfers", [
        ("Recall", "When a customer reports that an IMPS or account transfer was fraudulent, the remitter bank sends a recall request to the beneficiary bank. The beneficiary bank checks whether the funds are still in the account and places a hold if they are."),
        ("Return of funds", "Funds held under a fraud complaint are usually returned only after the beneficiary account holder has had a chance to respond, or on the order of a court or law enforcement agency."),
        ("Investigator checks", "Check how quickly the beneficiary moved the money, whether it went to other accounts at the same bank, and whether the beneficiary account has other fraud complaints."),
    ]),
    ("rbi-customer-awareness", "RBI", "Customer awareness on digital fraud", [
        ("Messages", "Customers should be told repeatedly that the bank will never ask for their PIN, OTP, password or CVV, never ask them to install screen-sharing apps, and never ask them to scan a QR code to receive money."),
        ("Digital arrest", "A growing scam involves callers posing as police, customs or regulator officials who claim the victim is under investigation and must transfer money to a 'safe account'. No real agency arrests people over video calls or asks for money transfers."),
        ("Role of investigators", "When a case involves social engineering, the investigator should record the script the fraudster used so that awareness messages can be updated."),
    ]),
    ("rbi-beneficiary-cooling", "RBI", "Controls on new beneficiaries and first transactions", [
        ("Cooling period", "Many banks apply a cooling period after a beneficiary is added, during which only a small amount can be sent. This gives the genuine customer time to see the alert and stop an attacker."),
        ("Name check", "Showing the beneficiary's registered name before the payment is confirmed helps customers spot when they are about to pay someone unexpected."),
        ("Signals", "Adding several beneficiaries in a short time, adding a beneficiary right after a password or device change, or sending the first transfer to a new beneficiary at night are all risk signals."),
    ]),
    ("rbi-credit-card-conduct", "RBI", "Credit card conduct and dispute rules", [
        ("Disputes", "Card issuers must have a process for disputed transactions, give customers a provisional credit while the dispute is investigated where the rules require it, and keep customers informed of progress."),
        ("Unsolicited cards", "Issuing or upgrading a card without explicit consent is prohibited. If a customer is billed for a card they did not ask for, the issuer must reverse the charges."),
        ("Lost cards", "Once a customer reports a lost or stolen card, they are not liable for transactions after the report. The issuer must block the card immediately and confirm the block."),
    ]),
]

# --------------------------------------------------------------------------
# 2. Fraud typologies -> playbooks, investigator notes
# --------------------------------------------------------------------------
TYPOLOGIES = [
    dict(key="ato-new-device", name="Account takeover from a new device",
         summary="An attacker gains control of the customer's mobile or internet banking, registers a new device and quickly drains the account through high-value payments to new payees.",
         signals=["first login from a device never seen on the account", "UPI PIN reset or password reset minutes before the payment",
                  "high-value payment to a beneficiary added the same day", "login location far from the customer's usual city",
                  "transaction at an unusual hour for this customer", "old device still active in the same period"],
         checks=["compare the device fingerprint with the customer's device history", "check the time gap between device registration, PIN reset and payment",
                 "check whether the registered mobile number or email changed recently", "call the customer on the number held before any recent change",
                 "check whether the beneficiary account has other fraud complaints", "review IP address and geolocation against previous sessions"],
         actions=["block the new device and force re-registration", "place a hold request with the beneficiary bank",
                  "reset credentials after verifying the customer in person or by video", "advise the customer to report on the 1930 helpline"]),
    dict(key="sim-swap", name="SIM swap fraud",
         summary="The attacker gets a duplicate SIM for the victim's number, receives OTPs and re-registers banking apps on their own phone.",
         signals=["customer's phone suddenly loses network", "telecom operator reports a recent SIM change",
                  "UPI re-registration on a new device right after the SIM change", "OTPs delivered while the customer says their phone had no signal",
                  "several transactions in quick succession after re-registration"],
         checks=["query the telecom SIM-change date through the available API", "match the time of SIM change with the device registration",
                 "check whether the customer's email was also changed", "check the KYC documents used for the duplicate SIM if police request them"],
         actions=["block all digital channels until the customer is re-verified", "mark the case for customer zero-liability review if reported in time",
                  "share the attacker device fingerprint with the fraud intelligence team"]),
    dict(key="otp-vishing", name="OTP phishing and vishing",
         summary="A fraudster calls or messages the customer pretending to be the bank, a courier or a utility, and tricks them into sharing an OTP or card details.",
         signals=["customer reports a call from someone claiming to be bank staff", "OTP requested and used within seconds",
                  "card-not-present transaction at a merchant the customer never used", "customer mentions KYC update, card block or reward points"],
         checks=["listen to or read the customer's account of the call and note the script", "check whether the OTP was entered from the customer's device or elsewhere",
                 "check the merchant and acquirer of the transaction", "look for other customers reporting the same caller number"],
         actions=["block the card and reissue", "raise a chargeback where the network rules allow it",
                  "record the customer's sharing of the OTP for the liability decision", "report the caller number to the telecom regulator portal"]),
    dict(key="remote-access", name="Remote access app scam",
         summary="The victim is persuaded to install a screen-sharing or remote-control app, after which the fraudster watches them enter credentials or operates the phone directly.",
         signals=["a remote access application was installed shortly before the transactions", "screen-sharing session active during the banking session",
                  "transactions made while the customer was on a call", "unusual touch or typing patterns compared with the customer's behaviour"],
         checks=["review the app's security telemetry for remote access tools", "compare session behaviour biometrics with the customer's history",
                 "establish who suggested installing the app and why"],
         actions=["advise the customer to uninstall the app and reset credentials", "block the device until it is cleaned",
                  "update app controls to block known remote access tools"]),
    dict(key="qr-scam", name="QR code and 'scan to receive' scam",
         summary="The fraudster sends a QR code or payment link claiming the victim will receive money, for example for an item they are selling online. Scanning and entering the PIN sends money instead.",
         signals=["victim was selling an item on an online marketplace", "payment note says 'receive' or 'refund'",
                  "several small payments followed by a larger one to the same payee", "payee VPA created recently"],
         checks=["check the age of the payee VPA and the beneficiary account", "check how many other payers sent money to the same VPA",
                 "check the transaction notes and the QR code source if available"],
         actions=["report the payee VPA to the beneficiary bank for blocking", "request a hold on the funds",
                  "explain to the customer that the PIN is only used to pay"]),
    dict(key="collect-request", name="Fraudulent UPI collect request",
         summary="The victim approves a collect request believing it is a refund, cashback or prize, and the money is debited.",
         signals=["collect request from an unknown requester", "request note mentions refund, cashback, lottery or reward",
                  "customer approved the request within seconds of receiving it", "requester has sent collect requests to many users"],
         checks=["check the requester's VPA history across complaints", "check whether the customer had any genuine pending refund"],
         actions=["block the requester VPA", "request a hold with the beneficiary bank", "add the requester to the collect block list"]),
    dict(key="mule-account", name="Mule account receiving fraud proceeds",
         summary="An account receives money from many unrelated victims and moves it out within minutes to other accounts, wallets or cash withdrawals.",
         signals=["many inward credits from unrelated remitters in a short time", "outward transfers within minutes of each credit",
                  "account recently opened or long dormant and suddenly active", "balance kept close to zero",
                  "same device or IP used by other flagged accounts", "complaints on the national cybercrime portal naming the account"],
         checks=["calculate inflow-outflow ratio and average holding time", "map onward transfers to find the next layer",
                 "check whether the account holder's profile matches the volume", "check the business correspondent or branch that opened the account"],
         actions=["debit-freeze the account under policy", "contact the account holder for an explanation",
                  "report the account and linked accounts", "mark linked devices for monitoring"]),
    dict(key="job-scam-mule", name="Job scam used to recruit mules",
         summary="Victims are offered part-time work such as 'payment processing' or 'rating products' and are asked to receive and forward money through their accounts.",
         signals=["customer says they were offered a work-from-home job", "regular inflows followed by forwarding to the same set of accounts",
                  "messages mention commission on each transfer", "young customer with a new account and sudden high volume"],
         checks=["interview the account holder about how they got the job", "identify the accounts they forwarded money to",
                 "check social media or messaging handles they were contacted through"],
         actions=["restrict the account and explain the legal risk to the holder", "report the recruiter's accounts and handles"]),
    dict(key="investment-task-scam", name="Investment and task scam",
         summary="Victims are added to messaging groups promising high returns on trading or simple online tasks. Early small payouts build trust before large deposits are taken.",
         signals=["several payments of increasing size to different accounts over days", "small credits returned to the victim early on",
                  "payments described as deposit, upgrade fee or tax for withdrawal", "beneficiary accounts change frequently"],
         checks=["build the timeline of payments and any small returns", "check whether beneficiary accounts are linked to other complaints",
                 "record the platform or app name the victim used"],
         actions=["advise the victim to stop further payments", "file hold requests for every beneficiary account", "report the app or site"]),
    dict(key="digital-arrest", name="Digital arrest impersonation scam",
         summary="Callers posing as police, customs or a regulator tell the victim they are implicated in a crime and keep them on a video call until they transfer money to a 'verification' account.",
         signals=["customer was on a long video call during the transfers", "large transfers, often from fixed deposits broken the same day",
                  "customer mentions police, customs, a parcel with drugs or a court order", "transfers to accounts with no prior relationship"],
         checks=["confirm whether a fixed deposit was closed or a loan taken before the transfer", "check whether branch staff noticed distress",
                 "trace beneficiary accounts quickly because funds move fast"],
         actions=["raise immediate hold requests", "help the customer file a report on the 1930 helpline",
                  "flag elderly customers for branch-level checks on large FD closures"]),
    dict(key="card-testing", name="Card testing and BIN attack",
         summary="Fraudsters run many small authorisations on generated or stolen card numbers to find which ones work, then use the valid cards for larger purchases.",
         signals=["many low-value authorisations at the same merchant within minutes", "high decline rate with codes for invalid card or CVV",
                  "card numbers in a sequential range from the same BIN", "same IP or device across many cards"],
         checks=["group declines by merchant, IP and BIN range", "identify which cards had a successful authorisation",
                 "check whether the merchant is a small donation or digital goods site"],
         actions=["block or reissue the cards that were successfully tested", "ask the acquirer to add velocity controls at the merchant"]),
    dict(key="skimming", name="Card skimming and cloning",
         summary="Card data is copied at an ATM or point-of-sale terminal and used to make a cloned card.",
         signals=["card-present transactions in a city where the customer was not", "magstripe fallback used instead of chip",
                  "several cards with a common point of purchase in the days before", "customer still holds the physical card"],
         checks=["run a common point of purchase analysis across affected cards", "confirm the customer's location at the time",
                 "check the entry mode of each transaction"],
         actions=["block and reissue affected cards", "inform the acquirer of the compromised terminal or ATM"]),
    dict(key="friendly-fraud", name="First-party misuse and friendly fraud",
         summary="The genuine customer makes a purchase and then disputes it as unauthorised or not received to get their money back.",
         signals=["purchase made from the customer's usual device and location", "delivery confirmed at the customer's address",
                  "customer has disputed several purchases with different merchants", "dispute raised after the return window closed"],
         checks=["compare the device and IP with the customer's history", "obtain delivery proof and any customer communication from the merchant",
                 "review the customer's past dispute history"],
         actions=["reject the dispute with evidence where justified", "add a first-party risk flag to the customer profile"]),
    dict(key="transaction-laundering", name="Merchant collusion and transaction laundering",
         summary="A merchant processes payments for an undisclosed business, such as gambling or fraud proceeds, through its own merchant account.",
         signals=["ticket sizes that do not match the declared business", "sudden growth in volume at a newly onboarded merchant",
                  "customers who do not recognise the merchant name", "high chargeback or refund ratio", "payments coming mostly at night"],
         checks=["visit or verify the merchant's premises and website", "sample customer complaints for the business name they expected",
                 "compare the merchant category code with actual product sold"],
         actions=["suspend settlement pending review", "report to the acquirer and payment aggregator risk team"]),
    dict(key="refund-abuse", name="Refund abuse",
         summary="Customers or insiders exploit refund flows, for example by claiming refunds for items returned empty or by issuing refunds to accounts they control.",
         signals=["refunds issued to a different card or account than the original payment", "the same staff member approving many refunds",
                  "refunds without a matching original transaction"],
         checks=["match each refund to the original transaction", "review the approver of each refund"],
         actions=["block refund rights for the involved staff pending review", "recover funds where possible"]),
    dict(key="loan-app", name="Fraudulent loan app",
         summary="An unregistered lending app collects contacts and photos, gives a small loan and then extorts repayment far above the loan amount by threatening borrowers.",
         signals=["customer pays many small amounts to different accounts described as loan repayment", "customer reports threats or morphed photos",
                  "app not linked to any regulated lender"],
         checks=["check whether the lender named in the app is regulated", "list all beneficiary accounts the customer paid"],
         actions=["report the app and beneficiary accounts", "advise the customer on how to report harassment"]),
    dict(key="aeps-cloning", name="AePS biometric cloning",
         summary="Cloned fingerprints are used at business correspondent points to withdraw cash from victims' accounts without OTP.",
         signals=["AePS cash withdrawals the customer did not make", "withdrawals at a business correspondent far from the customer's home",
                  "several victims linked to the same terminal", "customer had registered a property or document recently"],
         checks=["get the terminal ID, operator ID and location", "check how many accounts were debited at the same terminal"],
         actions=["advise the customer to lock biometrics", "suspend the business correspondent terminal pending inquiry"]),
    dict(key="insider", name="Insider-assisted fraud",
         summary="A staff member or outsourced agent misuses access to change customer contact details, open accounts or leak data.",
         signals=["mobile number changed by a staff user without a customer request", "accounts opened in bulk by the same employee",
                  "staff account viewing customer records outside working hours"],
         checks=["review the audit trail of the staff user", "compare change requests with customer service tickets"],
         actions=["suspend the staff user's access", "escalate to vigilance and human resources"]),
    dict(key="synthetic-id", name="Synthetic identity accounts",
         summary="Fraudsters combine real and fake identity details to open accounts that are later used as mules or for credit bust-out.",
         signals=["identity documents that pass checks but have little history", "same address or phone across many new applicants",
                  "rapid credit limit usage soon after opening"],
         checks=["link applicants by shared attributes", "re-verify documents with the issuing source"],
         actions=["freeze linked accounts pending review", "update onboarding rules with the shared attributes"]),
    dict(key="promo-abuse", name="Cashback and promotion abuse",
         summary="Users create many accounts or devices to claim first-transaction cashback repeatedly.",
         signals=["many new accounts on the same device or IP", "first transactions of exactly the cashback threshold amount",
                  "cashback credited and moved out immediately"],
         checks=["cluster accounts by device fingerprint", "check the merchants used for the qualifying transaction"],
         actions=["claw back the cashback", "block the device cluster from promotions"]),
    dict(key="triangulation", name="Triangulation fraud on online marketplaces",
         summary="A fraudster lists goods at low prices, takes orders from real buyers and fulfils them by buying from a real merchant with stolen cards.",
         signals=["shipping address differs from the cardholder's billing address", "orders for high-demand electronics",
                  "cardholder disputes a purchase that was delivered to a stranger"],
         checks=["compare billing and shipping details", "identify the marketplace seller who triggered the order"],
         actions=["refund the cardholder through chargeback", "share the seller details with the marketplace"]),
    dict(key="fake-customer-care", name="Fake customer care number",
         summary="Victims search online for a helpline, call a fake number and are guided to share details or install apps.",
         signals=["customer says they found the number through an internet search", "call with 'support' followed by a payment or app install",
                  "refund or complaint was the reason for the call"],
         checks=["record the number called and where it was found", "check for other cases with the same number"],
         actions=["report the number and listing for takedown", "publish the official helpline prominently"]),
]

CITIES = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Kolkata", "Jaipur", "Lucknow", "Kochi",
          "Ahmedabad", "Indore", "Patna", "Bhubaneswar", "Guwahati", "Coimbatore", "Nagpur", "Mysuru", "Jamtara", "Nuh"]
DEVICES = ["Android device (Redmi)", "Android device (Samsung)", "Android device (Vivo)", "Android device (Oppo)",
           "iPhone", "Android emulator", "Android device (Realme)", "Android device (OnePlus)"]
CHANNELS = ["UPI", "IMPS", "internet banking", "card-not-present", "mobile banking", "UPI", "UPI"]
TIMES = ["02:14", "03:47", "23:52", "11:05", "14:30", "19:21", "01:09", "06:40", "22:18", "09:55"]
OUTCOMES = [
    ("Confirmed fraud", "Case confirmed as fraud. Customer liability assessed under the bank's policy; recovery requested from the beneficiary bank."),
    ("Confirmed fraud", "Fraud confirmed. Partial funds frozen at the beneficiary bank; remaining amount had already moved to a second-layer account."),
    ("False positive", "Customer confirmed the transaction as genuine. Alert closed as a false positive; rule threshold noted for tuning."),
    ("Escalated", "Escalated to the senior investigator because linked accounts appear in other open cases."),
    ("Customer error", "Customer made the payment by mistake to a wrong but genuine payee. Reclassified as a wrong-credit request, not fraud."),
]

# --------------------------------------------------------------------------
# 3. Chargeback narratives
# --------------------------------------------------------------------------
CB_REASONS = [
    ("goods not received", "The customer says the order was never delivered.",
     "delivery proof with a signature or OTP-confirmed delivery", "the courier tracking shows the parcel returned to origin"),
    ("unauthorised transaction", "The customer says they did not make or authorise the payment.",
     "device and IP logs showing the payment came from the customer's registered device", "the payment came from a newly registered device in another state"),
    ("duplicate debit", "The customer was charged twice for one purchase.",
     "proof that two separate orders were placed", "the gateway retried after a timeout and both attempts were captured"),
    ("amount differs", "The customer was charged more than the agreed price.",
     "the signed invoice showing the higher amount", "the invoice shows a lower amount than the debit"),
    ("service not as described", "The customer says the service was not delivered as promised.",
     "service logs and the accepted terms", "the merchant could not show the service was provided"),
    ("credit not processed", "The customer returned the item but the refund never came.",
     "proof that the returned item was not received or was damaged", "the warehouse confirmed receipt of the return"),
    ("debited but not credited", "The customer's UPI payment failed at the merchant but the account was debited.",
     "a settlement record showing the merchant received the funds", "switch logs show the beneficiary bank timed out and no credit was posted"),
    ("cancelled subscription", "The customer cancelled a subscription but was charged again.",
     "the active mandate record and usage after the claimed cancellation", "the cancellation request was logged before the debit date"),
]
MERCHANTS = [("electronics e-commerce", "ShopNova"), ("food delivery", "TiffinGo"), ("travel booking", "YatraLane"),
             ("online education", "SkillKart"), ("gaming wallet", "PlayVault"), ("fashion retail", "KurtaCo"),
             ("OTT subscription", "StreamBay"), ("grocery delivery", "QuickBasket"), ("fuel station", "HP Pump 2291"),
             ("hospital", "CityCare Hospital"), ("insurance premium", "SecureLife"), ("mobile recharge", "RechargePe")]


PAST = {"check": "checked", "compare": "compared", "review": "reviewed", "call": "called", "listen": "listened",
        "look": "looked", "query": "queried", "match": "matched", "calculate": "calculated", "map": "mapped",
        "interview": "interviewed", "identify": "identified", "build": "built", "record": "recorded",
        "confirm": "confirmed", "trace": "traced", "group": "grouped", "run": "ran", "obtain": "obtained",
        "visit": "visited", "sample": "sampled", "get": "got", "link": "linked", "re-verify": "re-verified",
        "cluster": "clustered", "list": "listed", "establish": "established"}


def past(clause: str) -> str:
    verb, _, rest = clause.partition(" ")
    return f"{PAST.get(verb, verb)} {rest}"


def money(rng: random.Random, lo: int, hi: int) -> str:
    return f"Rs {rng.randrange(lo, hi, 7):,}"


def noisy(text: str, title: str, rng: random.Random) -> str:
    """Add the clutter typical of exported documents."""
    header = "SENTINEL KNOWLEDGE BASE  |  CONFIDENTIAL — INTERNAL USE ONLY"
    paras = text.split("\n\n")
    pages = max(1, -(-len(paras) // 3))
    out, page = [header, "", title.upper(), ""], 1
    for i, p in enumerate(paras):
        p = p.replace("'", "’") if rng.random() < 0.5 else p
        if rng.random() < 0.3:
            p = p.replace(". ", ".  ", 2)  # double spaces
        out.append(p + ("   " if rng.random() < 0.3 else ""))
        out.append("")
        if (i + 1) % 3 == 0 and i + 1 < len(paras):
            out += [f"Page {page} of {pages}", "\f" + header, ""]
            page += 1
    out.append(f"Page {page} of {pages}")
    sep = "\r\n" if rng.random() < 0.2 else "\n"
    return sep.join(out)


def write(doc_type: str, doc_id: str, title: str, body: str, rng: random.Random) -> Path:
    folder = RAW / doc_type
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{doc_id}.txt"
    path.write_text(noisy(body, title, rng), encoding="utf-8", newline="")
    return path


def build_guidelines(rng):
    paths = []
    for doc_id, issuer, title, sections in GUIDELINES:
        body = [f"Issuer: {issuer}", DISCLAIMER]
        for i, (h, t) in enumerate(sections, 1):
            body.append(f"{i}. {h}\n{t}")
        paths.append(write("guideline", doc_id, f"{issuer} — {title}", "\n\n".join(body), rng))
    return paths


def build_playbooks(rng):
    paths = []
    for t in TYPOLOGIES:
        body = [
            f"Playbook: {t['name']}", f"Overview\n{t['summary']}",
            "Detection signals\n" + "\n".join(f"- {s[0].upper() + s[1:]}." for s in t["signals"]),
            "What the investigator should check\n" + "\n".join(f"{i}) {c[0].upper() + c[1:]}." for i, c in enumerate(t["checks"], 1)),
            "Containment and next steps\n" + "\n".join(f"- {a[0].upper() + a[1:]}." for a in t["actions"]),
            "Evidence to keep\nKeep device and session logs, alert delivery records, the customer's first report with its timestamp, "
            "beneficiary bank responses and every call note. These decide the customer liability outcome and may be reviewed by the ombudsman.",
        ]
        paths.append(write("playbook", f"pb-{t['key']}", f"Playbook — {t['name']}", "\n\n".join(body), rng))
    return paths


def build_notes(rng, n=92):
    paths = []
    openers = ["Alert raised by the real-time rules engine.", "Customer called the helpline to report the transaction.",
               "Case received from the national cybercrime reporting system.", "Flagged by the network-level risk score.",
               "Branch staff raised a concern and referred the case."]
    for i in range(1, n + 1):
        t = rng.choice(TYPOLOGIES)
        case = f"SEN-{2026}-{rng.randint(10000, 99999)}"
        city, home = rng.sample(CITIES, 2)
        sigs = rng.sample(t["signals"], k=min(len(t["signals"]), rng.randint(2, 4)))
        chks = rng.sample(t["checks"], k=min(len(t["checks"]), rng.randint(2, 3)))
        status, outcome = rng.choice(OUTCOMES)
        amt = money(rng, 2_000, 480_000)
        body = [
            f"Case {case} | Typology suspected: {t['name']} | Status: {status}",
            f"Summary\n{rng.choice(openers)} Customer is based in {home}. Disputed amount {amt} via {rng.choice(CHANNELS)} "
            f"at {rng.choice(TIMES)}. Session originated from {city} on {rng.choice(DEVICES)}.",
            "Observations\n" + " ".join(f"Noted {s}." for s in sigs),
            "Checks performed\n" + " ".join(f"I {past(c)}." for c in chks),
            f"Outcome\n{outcome}",
        ]
        if rng.random() < 0.4:
            body.insert(3, f"Customer statement\nCustomer says: “{rng.choice(['I did not do this payment', 'Someone called me saying my KYC was expiring', 'I only shared the code to get my refund', 'My phone had no signal all evening', 'I was told to keep the video call on'])}.”")
        paths.append(write("investigator_note", f"note-{i:03d}-{t['key']}", f"Investigator note {case}", "\n\n".join(body), rng))
    return paths


def build_chargebacks(rng, n=92):
    paths = []
    for i in range(1, n + 1):
        reason, claim, merchant_ev, finding = rng.choice(CB_REASONS)
        mcat, mname = rng.choice(MERCHANTS)
        amt = money(rng, 199, 85_000)
        won = rng.random() < 0.5
        body = [
            f"Chargeback reference CB-{rng.randint(100000, 999999)} | Reason: {reason} | Merchant: {mname} ({mcat})",
            f"Customer claim\n{claim} Amount {amt} paid via {rng.choice(['UPI', 'credit card', 'debit card', 'UPI', 'wallet'])}.",
            f"Merchant response\nThe merchant re-presented the transaction and submitted {merchant_ev}." if not won
            else f"Merchant response\nThe merchant did not submit sufficient evidence within the re-presentment window.",
            f"Investigation\nThe dispute analyst found that {finding}." if won
            else f"Investigation\nThe dispute analyst reviewed the merchant's evidence against the customer's claim and the customer's previous disputes.",
            "Decision\n" + ("Chargeback accepted in the customer's favour; amount credited back." if won
                            else "Chargeback declined; the merchant's evidence was found valid. Customer informed of the ombudsman route."),
        ]
        paths.append(write("chargeback", f"cb-{i:03d}-{reason.replace(' ', '-')}", f"Chargeback narrative {i:03d}", "\n\n".join(body), rng))
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    if RAW.exists():
        shutil.rmtree(RAW)
    paths = build_guidelines(rng) + build_playbooks(rng) + build_notes(rng) + build_chargebacks(rng)
    # a few exact duplicates, as happens when files are exported twice
    for p in rng.sample(paths, 6):
        p.with_name(p.stem + "-copy.txt").write_bytes(p.read_bytes())
    total = sum(1 for _ in RAW.rglob("*.txt"))
    print(f"Wrote {total} raw files to {RAW.relative_to(ROOT)} (including 6 duplicates)")


if __name__ == "__main__":
    main()
