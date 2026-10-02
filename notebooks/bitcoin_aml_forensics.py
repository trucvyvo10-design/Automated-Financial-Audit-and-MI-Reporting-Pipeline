import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve

# 1. LOAD DATASET
# Giả định file csv đã được join giữa classes và features
# df chứa các cột: 'txId', 'time_step', 'class', feature_1, ..., feature_165
# In Elliptic dataset: class '1' = illicit, class '2' = licit, class 'unknown'/'0' = unlabeled

df = pd.read_csv('elliptic_txs_joined.csv')

# Lọc các giao dịch có dán nhãn (1 và 2) để train/test
labeled_df = df[df['class'].isin(['1', '2'])].copy()
labeled_df['target'] = labeled_df['class'].apply(lambda x: 1 if str(x) == '1' else 0)

# Unlabeled dataset
unlabeled_df = df[~df['class'].isin(['1', '2'])].copy()

feature_cols = [c for c in df.columns if c not in ['txId', 'time_step', 'class', 'target']]

# 2. TEMPORAL TRAIN / TEST SPLIT (Ngăn chặn Data Leakage)
# Train: Time Step 1 đến 34 | Test: Time Step 35 đến 49
train_mask = labeled_df['time_step'] <= 34
test_mask = labeled_df['time_step'] > 34

X_train = labeled_df.loc[train_mask, feature_cols]
y_train = labeled_df.loc[train_mask, 'target']

X_test = labeled_df.loc[test_mask, feature_cols]
y_test = labeled_df.loc[test_mask, 'target']

print(f"Train set (Steps 1-34): {X_train.shape[0]} transactions")
print(f"Test set (Steps 35-49): {X_test.shape[0]} transactions")

# 3. TRAIN RANDOM FOREST MODEL
rf_model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=15, 
    random_state=42, 
    class_weight='balanced',
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# 4. MODEL EVALUATION ON TEST SET (GROUND TRUTH ONLY)
y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
y_pred_default = (y_pred_proba >= 0.5).astype(int)

print("\n--- TEST SET CLASSIFICATION REPORT (TEMPORAL SPLIT) ---")
print(classification_report(y_test, y_pred_default, target_names=['Licit (0)', 'Illicit (1)']))

# 5. ALERT VOLUME VS. PRECISION CURVE (THREHSOLD TUNING FOR COMPLIANCE)
thresholds = np.linspace(0.1, 0.95, 85)
alert_volumes = []
precisions = []
recalls = []

for t in thresholds:
    alerts = (y_pred_proba >= t).astype(int)
    num_alerts = alerts.sum()
    
    tp = ((alerts == 1) & (y_test == 1)).sum()
    fp = ((alerts == 1) & (y_test == 0)).sum()
    
    prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    rec = tp / (y_test == 1).sum()
    
    alert_volumes.append(num_alerts)
    precisions.append(prec)
    recalls.append(rec)

# Plotting the Killer Chart
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:red'
ax1.set_xlabel('Decision Threshold (Risk Score Cutoff)', fontsize=12)
ax1.set_ylabel('Alert Volume Generated (Count)', color=color, fontsize=12)
line1 = ax1.plot(thresholds, alert_volumes, color=color, linewidth=2, label='Alert Volume')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.5)

ax2 = ax1.twinx()  
color = 'tab:blue'
ax2.set_ylabel('Precision (True Illicit Rate %)', color=color, fontsize=12)
line2 = ax2.plot(thresholds, precisions, color=color, linewidth=2.5, linestyle='-', label='Precision')
ax2.tick_params(axis='y', labelcolor=color)

# Added Title & Layout
plt.title('Compliance Capacity Optimization: Alert Volume vs. Precision Curve', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.savefig('docs/alert_precision_threshold_curve.png', dpi=300)
plt.show()

# 6. UNLABELED RISK SCORING (PRIORITIZATION FOR INVESTIGATION)
X_unlabeled = unlabeled_df[feature_cols]
unlabeled_df['predicted_risk_score'] = rf_model.predict_proba(X_unlabeled)[:, 1]

# High Risk Unlabeled Queue for Compliance Officers
high_risk_queue = unlabeled_df[unlabeled_df['predicted_risk_score'] >= 0.8].sort_values(by='predicted_risk_score', ascending=False)
print(f"\nFlagged {len(high_risk_queue)} unlabeled transactions with Risk Score >= 0.80 for prioritized audit.")
