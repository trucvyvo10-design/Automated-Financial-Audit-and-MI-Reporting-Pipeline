# 📋 INTERNAL CONTROL AUDIT CHECKLIST (ACCA F1/F3 FRAMEWORK)
> **Target System:** Core Banking & General Ledger Operations  
> **Domain:** Financial Crime, Internal Controls & Risk Assessment

---

## 1. Governance & Authorisation Controls (ACCA F1 Focus)
- [ ] **Dual Authorisation / Four-Eyes Principle:** Are all manual journal entries over $10,000 required to be approved by a secondary supervisor?
- [ ] **Segregation of Duties (SoD):** Are roles restricted so that staff initiating payment transactions cannot approve or reconcile General Ledger accounts?
- [ ] **Delegation of Authority (DoA):** Is there an automated system block preventing junior officers from approving transaction limits beyond their tier?

## 2. General Ledger Integrity & Reconciliation (ACCA F3 Focus)
- [ ] **Debit / Credit Trial Balance Equality:** Is an automated integrity check executed daily to ensure Total Debits equal Total Credits ($\sum \text{Debit} - \sum \text{Credit} = 0$)?
- [ ] **Suspense Account Clearance:** Are suspense and clearing accounts monitored and cleared within a maximum 24-hour SLA?
- [ ] **Unusual Late-Period Entries:** Are manual journal entries posted after business hours or during period-end closing flagged for forensic audit?

## 3. Financial Crime & AML Threshold Controls
- [ ] **Cash Transaction Reporting (CTR):** Are cash deposits/withdrawals exceeding $10,000 automatically flagged for Regulatory Reporting?
- [ ] **Structuring / Smurfing Detection:** Are dynamic window functions deployed to detect multiple sub-threshold transactions (e.g., $8,000–$9,999) executed within 24 hours?
- [ ] **Sanctions & PEP Screening:** Are counterparty accounts automatically screened against global sanction lists prior to clearing?
