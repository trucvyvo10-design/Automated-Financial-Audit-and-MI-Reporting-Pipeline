import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set Streamlit Page Config
st.set_page_config(
    page_title="Executive Financial Crime & Risk Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Title & Subtitle
st.title("🛡️ Core Banking Financial Crime & Risk MI Dashboard")
st.markdown("**Domain:** Anti-Money Laundering (AML) & Transaction Monitoring | **Dataset:** 50,000 GL Core Banking Logs")

# Load Data Function
@st.cache_data
def load_data():
    data_path = "raw_core_banking_logs.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
        return df
    else:
        st.error("⚠️ File 'raw_core_banking_logs.csv' not found. Please run gl_dataset_generator.py first!")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Sidebar Filters
    st.sidebar.header("🔍 Filter Risk Metrics")
    selected_channel = st.sidebar.multiselect(
        "Select Banking Channel:",
        options=df["channel"].unique(),
        default=df["channel"].unique()
    )
    
    selected_type = st.sidebar.multiselect(
        "Select Transaction Type:",
        options=df["transaction_type"].unique(),
        default=df["transaction_type"].unique()
    )
    
    # Filter Data
    filtered_df = df[
        (df["channel"].isin(selected_channel)) & 
        (df["transaction_type"].isin(selected_type))
    ]

    # Key Performance Indicators (KPIs)
    total_vol = filtered_df["amount"].sum()
    total_txns = len(filtered_df)
    suspicious_txns = filtered_df["is_suspicious_flag"].sum()
    risk_rate = (suspicious_txns / total_txns * 100) if total_txns > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Transaction Volume", f"${total_vol:,.2f}")
    col2.metric("📊 Total Transactions", f"{total_txns:,}")
    col3.metric("🚨 Suspicious Alerts (Structuring)", f"{suspicious_txns:,}")
    col4.metric("📈 Risk Alert Rate (%)", f"{risk_rate:.2f}%")

    st.markdown("---")

    # Interactive Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📌 Risk Alerts by Channel")
        channel_risk = filtered_df.groupby("channel")["is_suspicious_flag"].sum().reset_index()
        fig_channel = px.bar(
            channel_risk, x="channel", y="is_suspicious_flag",
            labels={"is_suspicious_flag": "Alert Count", "channel": "Banking Channel"},
            color="is_suspicious_flag",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_channel, use_container_width=True)

    with col_chart2:
        st.subheader("💳 Volume Distribution by Transaction Type")
        type_vol = filtered_df.groupby("transaction_type")["amount"].sum().reset_index()
        fig_type = px.pie(
            type_vol, values="amount", names="transaction_type",
            hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_type, use_container_width=True)

    # Detailed High-Risk Alert Drilldown Table
    st.subheader("⚠️ High-Risk AML Structuring Alerts Drilldown")
    high_risk_table = filtered_df[filtered_df["is_suspicious_flag"] == 1][[
        "transaction_id", "account_number", "transaction_timestamp", 
        "transaction_type", "amount", "channel"
    ]].sort_values(by="amount", ascending=False)
    
    st.dataframe(high_risk_table, use_container_width=True)
