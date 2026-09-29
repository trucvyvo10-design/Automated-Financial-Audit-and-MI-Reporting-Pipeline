import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuration
NUM_RECORDS = 50000
START_DATE = datetime(2026, 1, 1)

print("🚀 Generating 50,000+ Mock Banking Transactions...")

# Generate Customer & Account IDs
customer_ids = [f"CUST_{i:05d}" for i in range(1, 1001)]
account_numbers = [f"ACC_VN_{i:08d}" for i in range(1, 1501)]

data = []

for i in range(1, NUM_RECORDS + 1):
    tx_id = f"TXN_2026_{i:07d}"
    acc_num = random.choice(account_numbers)
    # Random timestamps over 90 days
    random_seconds = random.randint(0, 90 * 24 * 3600)
    tx_time = START_DATE + timedelta(seconds=random_seconds)
    
    tx_type = random.choice(['DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'ATM_CASH'])
    channel = random.choice(['MOBILE_BANKING', 'INTERNET_BANKING', 'ATM', 'COUNTER_BRANCH'])
    
    # Simulate Structuring Pattern near $10,000 (8000 - 9999 USD converted or equivalent)
    if random.random() < 0.05:  # 5% anomalous transactions
        amount = round(random.uniform(8500.00, 9950.00), 2)
        is_suspicious = 1
    else:
        amount = round(random.exponential(scale=1500) + 10, 2)
        is_suspicious = 0
        
    data.append({
        'transaction_id': tx_id,
        'account_number': acc_num,
        'transaction_timestamp': tx_time.strftime('%Y-%m-%d %H:%M:%S'),
        'transaction_type': tx_type,
        'amount': amount,
        'currency': 'USD',
        'channel': channel,
        'is_suspicious_flag': is_suspicious
    })

# Convert to DataFrame & Save
df = pd.DataFrame(data)
df.to_csv('raw_core_banking_logs.csv', index=False)
print("✅ Successfully generated raw_core_banking_logs.csv with 50,000 records!")
