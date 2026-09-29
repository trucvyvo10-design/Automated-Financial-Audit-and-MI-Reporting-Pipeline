# 📑 Technical Whitepaper #1: Applying Benford's Law & SQL Window Functions to Uncover Financial Statement Anomalies

**Author:** Compliance & Risk Analytics Specialist  
**Framework:** ACCA F3 Forensic Perspective & Advanced SQL Data Engineering  

---

## 1. Executive Summary
Financial statement manipulation often manifests through sub-threshold transaction splitting and artificial number generation. This whitepaper details a quantitative forensic method combining **Benford's Law (First-Digit Law)** with **Advanced SQL Window Functions** to automatically detect anomalous patterns in multi-currency Core Banking transaction logs.

## 2. Theoretical Framework: Benford's Law
Benford's Law predicts the naturally occurring frequency of leading digits in logarithmic financial datasets:

$$P(d) = \log_{10}\left(1 + \frac{1}{d}\right)$$

* **Digit 1:** Expected frequency $\approx 30.1\%$
* **Digit 9:** Expected frequency $\approx 4.6\%$

Significant deviations in first-digit distribution (especially spikes near approval thresholds like $9,000–$9,999) indicate manual intervention, structuring, or fraud.

## 3. SQL Detection Logic
By leveraging CTEs and `LAG()` / `SUM() OVER()` functions, the pipeline identifies rapid sequential transfers designed to evade the $10,000 AML threshold:

```sql
SELECT 
    account_number,
    amount,
    SUM(amount) OVER(PARTITION BY account_number ORDER BY transaction_timestamp) AS rolling_total
FROM fact_transactions
WHERE amount BETWEEN 8000 AND 9999.99;
