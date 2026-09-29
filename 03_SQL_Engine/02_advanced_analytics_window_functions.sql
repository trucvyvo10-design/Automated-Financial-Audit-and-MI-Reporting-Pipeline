-- ====================================================================
-- ADVANCED SQL TRANSACTION ANALYTICS & RISK DETECTION
-- Key Techniques: CTEs, Window Functions (ROW_NUMBER, LAG, LEAD, SUM OVER)
-- Business Purpose: Detect AML Structuring & Suspicious Velocity Patterns
-- ====================================================================

USE core_banking_db;

-- --------------------------------------------------------------------
-- 1. DETECT STRUCTURING / SMURFING PATTERNS (Lách ngưỡng AML $10,000)
-- Scenario: Multiple cash deposits/transfers just below $10,000 (e.g., $8,000 - $9,999)
-- --------------------------------------------------------------------
WITH Structuring_Transactions AS (
    SELECT 
        transaction_id,
        account_number,
        transaction_timestamp,
        transaction_type,
        amount,
        channel,
        -- Calculate running total per account over a rolling window
        SUM(amount) OVER(
            PARTITION BY account_number 
            ORDER BY transaction_timestamp 
            RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW
        ) AS rolling_24h_volume,
        -- Get previous transaction timestamp for time-difference analysis
        LAG(transaction_timestamp, 1) OVER(
            PARTITION BY account_number 
            ORDER BY transaction_timestamp
        ) AS prev_tx_time
    FROM fact_transactions
    WHERE amount BETWEEN 8000 AND 9999.99
)
SELECT 
    transaction_id,
    account_number,
    transaction_timestamp,
    amount,
    rolling_24h_volume,
    TIMESTAMPDIFF(MINUTE, prev_tx_time, transaction_timestamp) AS minutes_since_last_tx,
    CASE 
        WHEN rolling_24h_volume >= 10000 THEN 'HIGH_RISK_STRUCTURING_EXCEEDED'
        ELSE 'MONITOR_BORDERLINE_PATTERN'
    END AS risk_flag
FROM Structuring_Transactions
ORDER BY rolling_24h_volume DESC;


-- --------------------------------------------------------------------
-- 2. HIGH-FREQUENCY VELOCITY DETECTION (Rapid Consecutive Transactions)
-- Scenario: Identify accounts executing > 3 transactions within 5 minutes
-- --------------------------------------------------------------------
WITH Ranked_Transactions AS (
    SELECT 
        transaction_id,
        account_number,
        transaction_timestamp,
        amount,
        ROW_NUMBER() OVER(
            PARTITION BY account_number 
            ORDER BY transaction_timestamp
        ) AS tx_sequence,
        LEAD(transaction_timestamp, 2) OVER(
            PARTITION BY account_number 
            ORDER BY transaction_timestamp
        ) AS third_subsequent_tx_time
    FROM fact_transactions
)
SELECT 
    account_number,
    transaction_id,
    transaction_timestamp AS sequence_start_time,
    third_subsequent_tx_time,
    TIMESTAMPDIFF(SECOND, transaction_timestamp, third_subsequent_tx_time) AS velocity_window_seconds
FROM Ranked_Transactions
WHERE third_subsequent_tx_time IS NOT NULL
  AND TIMESTAMPDIFF(SECOND, transaction_timestamp, third_subsequent_tx_time) <= 300
ORDER BY velocity_window_seconds ASC;
