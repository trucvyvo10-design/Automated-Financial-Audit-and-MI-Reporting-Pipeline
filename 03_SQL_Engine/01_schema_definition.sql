-- ====================================================================
-- CORE BANKING TRANSACTION DATABASE SCHEMA
-- Domain: Financial Crime Risk, Compliance & Forensic Analytics
-- Target: High-volume raw banking transaction logs (50,000+ records)
-- ====================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS core_banking_db;
USE core_banking_db;

-- 1. Table: Customers (Thông tin Khách hàng)
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    customer_type VARCHAR(20) CHECK (customer_type IN ('INDIVIDUAL', 'CORPORATE')),
    risk_rating VARCHAR(10) CHECK (risk_rating IN ('LOW', 'MEDIUM', 'HIGH', 'PEP')), -- PEP: Politically Exposed Person
    kyc_status VARCHAR(20) DEFAULT 'VERIFIED',
    country_code VARCHAR(5) DEFAULT 'VN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table: Accounts (Tài khoản Ngân hàng)
CREATE TABLE IF NOT EXISTS dim_accounts (
    account_number VARCHAR(25) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    account_type VARCHAR(20) CHECK (account_type IN ('SAVINGS', 'CHECKING', 'CORPORATE_PAYROLL')),
    currency VARCHAR(5) DEFAULT 'VND',
    current_balance DECIMAL(18, 2) DEFAULT 0.00,
    account_status VARCHAR(15) DEFAULT 'ACTIVE',
    opened_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
);

-- 3. Table: Fact Transactions (Nhật ký Giao dịch Core Banking Logs)
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id VARCHAR(35) PRIMARY KEY,
    account_number VARCHAR(25) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'ATM_CASH')),
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(5) DEFAULT 'VND',
    channel VARCHAR(20) CHECK (channel IN ('MOBILE_BANKING', 'INTERNET_BANKING', 'ATM', 'COUNTER_BRANCH')),
    counterparty_account VARCHAR(25), -- Tài khoản đối ứng
    counterparty_bank VARCHAR(50),    -- Ngân hàng đối ứng
    branch_id VARCHAR(10),
    is_suspicious_flag TINYINT(1) DEFAULT 0, -- Cờ báo động rủi ro ban đầu từ hệ thống
    FOREIGN KEY (account_number) REFERENCES dim_accounts(account_number)
);

-- Create Indexes for Query Optimization (Tối ưu truy vấn cho Window Functions)
CREATE INDEX idx_tx_account_time ON fact_transactions(account_number, transaction_timestamp);
CREATE INDEX idx_tx_amount ON fact_transactions(amount);
