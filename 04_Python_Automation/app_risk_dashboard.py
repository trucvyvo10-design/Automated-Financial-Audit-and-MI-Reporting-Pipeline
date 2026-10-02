import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(
    page_title="Elliptic Bitcoin Forensic AML Dashboard",
    layout="wide"
)

# Tạo thư mục docs lưu chart
os.makedirs('docs', exist_ok=True)

st.title("Elliptic Bitcoin Forensic AML & Financial Crime Dashboard")
st.caption("Domain: On-Chain Financial Crime Analysis | Engine: Batch Transaction Monitoring & Forensic Analytics")

@st.cache_data(ttl=3600, show_spinner=False)
def load_full_elliptic_dataset():
    # 1. Tìm đường dẫn file đúng trong dự án
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    classes_path = os.path.join(base_dir, 'elliptic_txs_classes.csv')
    features_path = os.path.join(base_dir, 'elliptic_txs_features.csv')
    
    if not os.path.exists(classes_path):
        # Fallback nếu đường dẫn gọi từ thư mục gốc repo
        classes_path = '04_Python_Automation/elliptic_txs_classes.csv'
        features_path = '04_Python_Automation/elliptic_txs_features.csv'

    classes_df = pd.read_csv(classes_path)
    features_df = pd.read_csv(features_path, header=None)

    # 2. Ghép toàn bộ 203,769 Transaction Nodes
    feature_cols = list(range(2, 167))
    features_sub = features_df[[0, 1] + feature_cols]
    col_names = ['txId', 'time_step'] + [f'feature_{i}' for i in feature_cols]
    features_sub.columns = col_names
    
    df = pd.merge(classes_df, features_sub, on='txId')
    
    # 3. Temporal Train/Test Split (Steps 1-34 Train | Steps 35-49 Test)
    labeled_df = df[df['class'].isin(['1', '2'])].copy()
    labeled_df['target'] = labeled_df['class'].apply(lambda x: 1 if str(x) == '1' else 0)
    
    train_mask = labeled_df['time_step'] <= 34
    feat_list = [c for c in labeled_df.columns if c not in ['txId', 'time_step', 'class', 'target']]
    
    X_train = labeled_df.loc[train_mask, feat_list]
    y_train = labeled_df.loc[train_mask, 'target']
    
    # 4. Huấn luyện Random Forest
    rf = RandomForestClassifier(n_estimators=50, max_depth=12, random_state=42, class_weight='balanced', n_jobs=-1)
    rf.fit(X_train, y_train)
    
    # Risk score cho toàn bộ 203,769 transaction nodes
    df['predicted_risk_score'] = rf.predict_proba(df[feat_list])[:, 1]
    return df

with st.spinner("Processing Full Elliptic Bitcoin Dataset (203,769 Transaction Nodes)..."):
    try:
        df = load_full_elliptic_dataset()
    except Exception as e:
        st.error(f"Error loading full dataset: {e}")
        st.stop()

# COMPLIANCE CONTROLS
st.sidebar.header("Compliance Operations Control")
risk_cutoff = st.sidebar.slider("Risk Cutoff Threshold", 0.10, 0.95, 0.75, 0.05, key="cutoff_slider")
time_range = st.sidebar.slider("Filter Time Step", 1, 49, (1, 49), key="time_slider")

filtered_df = df[(df['time_step'] >= time_range[0]) & (df['time_step'] <= time_range[1])]
alerts_df = filtered_df[filtered_df['predicted_risk_score'] >= risk_cutoff]

# METRICS DISPLAY
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
