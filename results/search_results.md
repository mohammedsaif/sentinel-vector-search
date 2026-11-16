# SENTINEL semantic search results

Collection `sentinel_corpus` | model `gemini-embedding-2-preview` (3072 dims) | cosine similarity | top 5

## Query 1: What should an investigator check when a new device makes a large payment?

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7979 | playbook | playbook/pb-ato-new-device.txt | 1 | Playbook: Account takeover from a new device Overview: An attacker gains control of the customer's mobile or internet banking, registers a new device and ... |
| 2 | 0.7914 | guideline | guideline/rbi-digital-payment-security.txt | 3 | A new device followed quickly by a large payment to a new beneficiary is a classic account-takeover pattern. |
| 3 | 0.7743 | investigator_note | investigator_note/note-090-ato-new-device.txt | 1 | Case SEN-2026-86269 / Typology suspected: Account takeover from a new device / Status: Escalated Summary: Branch staff raised a concern and referred the ... |
| 4 | 0.7601 | investigator_note | investigator_note/note-065-ato-new-device.txt | 1 | Case SEN-2026-51774 / Typology suspected: Account takeover from a new device / Status: False positive Summary: Alert raised by the real-time rules engine. ... |
| 5 | 0.7581 | playbook | playbook/pb-ato-new-device.txt | 2 | 3) Check whether the registered mobile number or email changed recently. 4) Call the customer on the number held before any recent change. 5) Check whether ... |

## Query 2: A customer reported an unauthorised debit five days after the alert. How much of the loss do they bear?

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.8210 | guideline | guideline/rbi-customer-liability.txt | 2 | 3. Limited liability: When the customer reports a third-party breach between four and seven working days after the alert, liability is limited to the ... |
| 2 | 0.8026 | guideline | guideline/rbi-customer-liability.txt | 1 | Issuer: RBI 1. Purpose: This guidance sets out how much of a loss a customer bears when money leaves their account through an electronic transaction they ... |
| 3 | 0.7909 | guideline | guideline/rbi-customer-liability.txt | 3 | Any loss after the report is borne by the bank. Investigators should therefore record exactly when the customer first reported the issue and through which ... |
| 4 | 0.7056 | guideline | guideline/rbi-failed-transactions-tat.txt | 1 | Issuer: RBI 1. Principle: When a transaction fails because of a technical issue, communication failure or non-availability of funds at the beneficiary end, ... |
| 5 | 0.7039 | playbook | playbook/pb-loan-app.txt | 2 | Keep device and session logs, alert delivery records, the customer's first report with its timestamp, beneficiary bank responses and every call note. These ... |

## Query 3: How do we spot an account that receives money from many victims and moves it out quickly?

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7984 | playbook | playbook/pb-mule-account.txt | 1 | Playbook: Mule account receiving fraud proceeds Overview: An account receives money from many unrelated victims and moves it out within minutes to other ... |
| 2 | 0.7467 | playbook | playbook/pb-job-scam-mule.txt | 1 | Playbook: Job scam used to recruit mules Overview: Victims are offered part-time work such as 'payment processing' or 'rating products' and are asked to ... |
| 3 | 0.7438 | guideline | guideline/rbi-mule-accounts.txt | 1 | Issuer: RBI 1. What a mule account is: A mule account is a bank account used to receive and move the proceeds of fraud. The holder may be complicit, may ... |
| 4 | 0.7380 | playbook | playbook/pb-ato-new-device.txt | 1 | Playbook: Account takeover from a new device Overview: An attacker gains control of the customer's mobile or internet banking, registers a new device and ... |
| 5 | 0.7322 | investigator_note | investigator_note/note-080-mule-account.txt | 1 | Case SEN-2026-95799 / Typology suspected: Mule account receiving fraud proceeds / Status: Escalated Summary: Alert raised by the real-time rules engine. ... |

## Query 4: The victim was selling a sofa online and the buyer sent a QR code saying scan it to receive the money

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7549 | playbook | playbook/pb-qr-scam.txt | 1 | Playbook: QR code and 'scan to receive' scam Overview: The fraudster sends a QR code or payment link claiming the victim will receive money, for example for ... |
| 2 | 0.7270 | investigator_note | investigator_note/note-083-qr-scam.txt | 1 | Case SEN-2026-18130 / Typology suspected: QR code and 'scan to receive' scam / Status: Confirmed fraud Summary: Case received from the national cybercrime ... |
| 3 | 0.7051 | playbook | playbook/pb-qr-scam.txt | 2 | - Request a hold on the funds. - Explain to the customer that the PIN is only used to pay. Evidence to keep: Keep device and session logs, alert delivery ... |
| 4 | 0.6999 | investigator_note | investigator_note/note-005-qr-scam.txt | 1 | Case SEN-2026-27038 / Typology suspected: QR code and 'scan to receive' scam / Status: False positive Summary: Branch staff raised a concern and referred ... |
| 5 | 0.6792 | guideline | guideline/rbi-customer-awareness.txt | 1 | Issuer: RBI 1. Messages: Customers should be told repeatedly that the bank will never ask for their PIN, OTP, password or CVV, never ask them to install ... |

## Query 5: How many days does the bank have to credit the disputed amount back to the customer?

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7995 | guideline | guideline/rbi-customer-liability.txt | 3 | Any loss after the report is borne by the bank. Investigators should therefore record exactly when the customer first reported the issue and through which ... |
| 2 | 0.7542 | guideline | guideline/rbi-failed-transactions-tat.txt | 1 | Issuer: RBI 1. Principle: When a transaction fails because of a technical issue, communication failure or non-availability of funds at the beneficiary end, ... |
| 3 | 0.7383 | guideline | guideline/rbi-customer-liability.txt | 1 | Issuer: RBI 1. Purpose: This guidance sets out how much of a loss a customer bears when money leaves their account through an electronic transaction they ... |
| 4 | 0.7351 | guideline | guideline/rbi-failed-transactions-tat.txt | 2 | For card transactions at merchants, the acquirer should complete the reversal within the prescribed time. 4. Dispute handling: Customers should be able to ... |
| 5 | 0.7335 | chargeback | chargeback/cb-064-debited-but-not-credited.txt | 1 | Chargeback reference CB-321476 / Reason: debited but not credited / Merchant: StreamBay (OTT subscription) Customer claim: The customer's UPI payment failed ... |

## Query 6: The customer's phone suddenly lost signal in the evening and then money was transferred out

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7144 | investigator_note | investigator_note/note-069-digital-arrest.txt | 1 | Case SEN-2026-68079 / Typology suspected: Digital arrest impersonation scam / Status: Customer error Summary: Alert raised by the real-time rules engine. ... |
| 2 | 0.7100 | playbook | playbook/pb-sim-swap.txt | 1 | Playbook: SIM swap fraud Overview: The attacker gets a duplicate SIM for the victim's number, receives OTPs and re-registers banking apps on their own ... |
| 3 | 0.6992 | investigator_note | investigator_note/note-034-sim-swap.txt | 1 | Case SEN-2026-42077 / Typology suspected: SIM swap fraud / Status: Customer error Summary: Branch staff raised a concern and referred the case. Customer is ... |
| 4 | 0.6985 | investigator_note | investigator_note/note-030-fake-customer-care.txt | 1 | Case SEN-2026-35318 / Typology suspected: Fake customer care number / Status: Confirmed fraud Summary: Case received from the national cybercrime reporting ... |
| 5 | 0.6947 | investigator_note | investigator_note/note-072-digital-arrest.txt | 1 | Case SEN-2026-44003 / Typology suspected: Digital arrest impersonation scam / Status: False positive Summary: Case received from the national cybercrime ... |

## Query 7: Merchant ticket sizes do not match its business category and customers don't recognise the merchant name

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7469 | investigator_note | investigator_note/note-057-transaction-laundering.txt | 1 | Case SEN-2026-13133 / Typology suspected: Merchant collusion and transaction laundering / Status: Confirmed fraud Summary: Flagged by the network-level risk ... |
| 2 | 0.7356 | playbook | playbook/pb-transaction-laundering.txt | 1 | Playbook: Merchant collusion and transaction laundering Overview: A merchant processes payments for an undisclosed business, such as gambling or fraud ... |
| 3 | 0.7195 | chargeback | chargeback/cb-008-unauthorised-transaction.txt | 1 | Chargeback reference CB-970071 / Reason: unauthorised transaction / Merchant: TiffinGo (food delivery) Customer claim: The customer says they did not make ... |
| 4 | 0.7171 | chargeback | chargeback/cb-079-unauthorised-transaction.txt | 1 | Chargeback reference CB-745533 / Reason: unauthorised transaction / Merchant: TiffinGo (food delivery) Customer claim: The customer says they did not make ... |
| 5 | 0.7159 | investigator_note | investigator_note/note-053-friendly-fraud.txt | 1 | Case SEN-2026-48737 / Typology suspected: First-party misuse and friendly fraud / Status: False positive Summary: Customer called the helpline to report the ... |

## Query 8: Elderly customer kept on a video call by people claiming to be police broke an FD and transferred money

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7701 | playbook | playbook/pb-digital-arrest-copy.txt | 1 | Playbook: Digital arrest impersonation scam Overview: Callers posing as police, customs or a regulator tell the victim they are implicated in a crime and ... |
| 2 | 0.7595 | investigator_note | investigator_note/note-069-digital-arrest.txt | 1 | Case SEN-2026-68079 / Typology suspected: Digital arrest impersonation scam / Status: Customer error Summary: Alert raised by the real-time rules engine. ... |
| 3 | 0.7576 | playbook | playbook/pb-digital-arrest-copy.txt | 2 | Containment and next steps: - Raise immediate hold requests. - Help the customer file a report on the 1930 helpline. - Flag elderly customers for branch- ... |
| 4 | 0.7529 | investigator_note | investigator_note/note-010-digital-arrest.txt | 1 | Case SEN-2026-25096 / Typology suspected: Digital arrest impersonation scam / Status: Confirmed fraud Summary: Branch staff raised a concern and referred ... |
| 5 | 0.7480 | investigator_note | investigator_note/note-008-digital-arrest.txt | 1 | Case SEN-2026-54541 / Typology suspected: Digital arrest impersonation scam / Status: Confirmed fraud Summary: Flagged by the network-level risk score. ... |

## Query 9: My UPI payment failed but the money was debited from my account. When will I get it back?

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7954 | guideline | guideline/rbi-failed-transactions-tat.txt | 1 | Issuer: RBI 1. Principle: When a transaction fails because of a technical issue, communication failure or non-availability of funds at the beneficiary end, ... |
| 2 | 0.7365 | chargeback | chargeback/cb-080-debited-but-not-credited.txt | 1 | Chargeback reference CB-273021 / Reason: debited but not credited / Merchant: YatraLane (travel booking) Customer claim: The customer's UPI payment failed ... |
| 3 | 0.7246 | chargeback | chargeback/cb-064-debited-but-not-credited.txt | 1 | Chargeback reference CB-321476 / Reason: debited but not credited / Merchant: StreamBay (OTT subscription) Customer claim: The customer's UPI payment failed ... |
| 4 | 0.7238 | chargeback | chargeback/cb-005-debited-but-not-credited.txt | 1 | Chargeback reference CB-488196 / Reason: debited but not credited / Merchant: HP Pump 2291 (fuel station) Customer claim: The customer's UPI payment failed ... |
| 5 | 0.7223 | chargeback | chargeback/cb-003-debited-but-not-credited.txt | 1 | Chargeback reference CB-145548 / Reason: debited but not credited / Merchant: HP Pump 2291 (fuel station) Customer claim: The customer's UPI payment failed ... |

## Query 10: What evidence does a merchant need to win a goods-not-received dispute?

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7360 | chargeback | chargeback/cb-067-goods-not-received.txt | 1 | Chargeback reference CB-591644 / Reason: goods not received / Merchant: KurtaCo (fashion retail) Customer claim: The customer says the order was never ... |
| 2 | 0.7309 | chargeback | chargeback/cb-083-goods-not-received.txt | 1 | Chargeback reference CB-130477 / Reason: goods not received / Merchant: HP Pump 2291 (fuel station) Customer claim: The customer says the order was never ... |
| 3 | 0.7304 | chargeback | chargeback/cb-039-goods-not-received.txt | 1 | Chargeback reference CB-419739 / Reason: goods not received / Merchant: ShopNova (electronics e-commerce) Customer claim: The customer says the order was ... |
| 4 | 0.7277 | chargeback | chargeback/cb-006-goods-not-received.txt | 1 | Chargeback reference CB-105547 / Reason: goods not received / Merchant: YatraLane (travel booking) Customer claim: The customer says the order was never ... |
| 5 | 0.7261 | chargeback | chargeback/cb-023-goods-not-received.txt | 1 | Chargeback reference CB-908688 / Reason: goods not received / Merchant: TiffinGo (food delivery) Customer claim: The customer says the order was never ... |

## Query 11 (payload filter): Customer shared an OTP with a caller pretending to be from the bank

Filter: `doc_type = investigator_note`

| # | score | doc_type | source_document | chunk | text |
|---|---|---|---|---|---|
| 1 | 0.7695 | investigator_note | investigator_note/note-064-otp-vishing.txt | 1 | Case SEN-2026-41194 / Typology suspected: OTP phishing and vishing / Status: Confirmed fraud Summary: Alert raised by the real-time rules engine. Customer ... |
| 2 | 0.7671 | investigator_note | investigator_note/note-029-otp-vishing.txt | 1 | Case SEN-2026-95498 / Typology suspected: OTP phishing and vishing / Status: Confirmed fraud Summary: Alert raised by the real-time rules engine. Customer ... |
| 3 | 0.7520 | investigator_note | investigator_note/note-050-otp-vishing.txt | 1 | Case SEN-2026-70089 / Typology suspected: OTP phishing and vishing / Status: False positive Summary: Branch staff raised a concern and referred the case. ... |
| 4 | 0.7501 | investigator_note | investigator_note/note-046-otp-vishing.txt | 1 | Case SEN-2026-85674 / Typology suspected: OTP phishing and vishing / Status: False positive Summary: Branch staff raised a concern and referred the case. ... |
| 5 | 0.7416 | investigator_note | investigator_note/note-051-otp-vishing.txt | 1 | Case SEN-2026-95798 / Typology suspected: OTP phishing and vishing / Status: False positive Summary: Flagged by the network-level risk score. Customer is ... |
