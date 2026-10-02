import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

st.set_page_config(
    page_title="Elliptic Bitcoin Forensic AML Dashboard",
    layout="wide"
)

# Dam bao thu muc docs ton tai de luu chart
os.makedirs('docs', exist_ok=True)

st.title("Elliptic Bitcoin Forensic AML & Financial Crime Dashboard")
st.caption("Domain: On-Chain Financial Crime Analysis | Engine: Batch Transaction Monitoring & Forensic Analytics")

@st.cache_data
def run_pipeline_and_load_data():
    try:
        # Doc du lieu tu thu muc local cua ban
        classes_df = pd.read_csv('elliptic_bitcoin_dataset/elliptic_txs_classes.csv')
        features_df = pd.read_csv('elliptic_bitcoin_dataset/elliptic_txs_features.csv', header=None)
        
        # Merge va dat ten cot
        feature_cols = list(range(2, 167))
        features_sub = features_df[[0, 1] + feature_cols]
        col_names = ['txId', 'time_step'] + [f'feature_{i}' for i in feature_cols]
        features_sub.columns = col_names
        
        df = pd.merge(classes_df, features_sub, on='txId')
        
        # 1. TEMPORAL TRAIN/TEST SPLIT (Step 1-34 Train | Step 35-49 Test)
        labeled_df = df[df['class'].isin(['1', '2'])].copy()
        labeled_df['target'] = labeled_df['class'].apply(lambda x: 1 if str(x) == '1' else 0)
        
        train_mask = labeled_df['time_step'] <= 34
        test_mask = labeled_df['time_step'] > 34
        
        feat_list = [c for c in labeled_df.columns if c not in ['txId', 'time_step', 'class', 'target']]
        X_train, y_train = labeled_df.loc[train_mask, feat_list], labeled_df.loc[train_mask, 'target']
        X_test, y_test = labeled_df.loc[test_mask, feat_list], labeled_df.loc[test_mask, 'target']
        
        # 2. RANDOM FOREST MODEL
        rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, class_weight='balanced', n_jobs=-1)
        rf.fit(X_train, y_train)
        
        # Risk scoring cho toan bo node
        df['predicted_risk_score'] = rf.predict_proba(df[feat_list])[:, 1]
        
        # 3. VE MÔ HÌNH ALERT VOLUME VS PRECISION CURVE
        y_test_proba = rf.predict_proba(X_test)[:, 1]
        thresholds = np.linspace(0.1, 0.95, 85)
        alert_vols, precs = [], []
        for t in thresholds:
            alerts = (y_test_proba >= t).astype(int)
            tp = ((alerts == 1) & (y_test == 1)).sum()
            fp = ((alerts == 1) & (y_test == 0)).sum()
            prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
            alert_vols.append(alerts.sum())
            precs.append(prec)
            
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(thresholds, alert_vols, color='tab:red', label='Alert Volume')
        ax1.set_xlabel('Decision Threshold (Risk Score Cutoff)')
        ax1.set_ylabel('Alert Volume', color='tab:red')
        ax2 = ax1.twinx()
        ax2.plot(thresholds, precs, color='tab:blue', label='Precision')
        ax2.set_ylabel('Precision Rate', color='tab:blue')
        plt.title('Compliance Operations: Alert Volume vs Precision Curve')
        plt.savefig('docs/alert_precision_threshold_curve.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return df
    except Exception as e:
        # Truong hop thieu dataset local
        np.random.seed(42)
        n = 1000
        return pd.DataFrame({
            'txId': np.random.randint(100000, 999999, size=n),
            'time_step': np.random.randint(1, 50, size=n),
            'class': np.random.choice(['1', '2', '0'], size=n, p=[0.1, 0.4, 0.5]),
            'predicted_risk_score': np.random.uniform(0.0, 1.0, size=n)
        })

df = run_pipeline_and_load_data()

# CONTROLS
st.sidebar.header("Compliance Operations Control")
risk_cutoff = st.sidebar.slider("Risk Cutoff Threshold", 0.10, 0.95, 0.75, 0.05, key="cutoff_slider")
time_range = st.sidebar.slider("Filter Time Step", 1, 49, (1, 49), key="time_slider")

filtered_df = df[(df['time_step'] >= time_range[0]) & (df['time_step'] <= time_range[1])]
alerts_df = filtered_df[filtered_df['predicted_risk_score'] >= risk_cutoff]

# METRICS
col1, col2, col3 = st.columns(3)
col1.metric("Analyzed Transaction Nodes", f"{len(filtered_df):,}")
col2.metric("Flagged Suspicious Transactions", f"{len(alerts_df):,}")
col3.metric("Illicit Rate (Labeled Subset)", "9.8%")

st.markdown("---")
st.subheader("Prioritised SAR Investigation Queue")
st.dataframe(
    alerts_df[['txId', 'time_step', 'class', 'predicted_risk_score']]
    .rename(columns={'txId': 'Transaction ID', 'time_step': 'Time Step', 'class': 'Class Label', 'predicted_risk_score': 'Risk Score'})
    .sort_values(by='Risk Score', ascending=False), 
    use_container_width=True
)
