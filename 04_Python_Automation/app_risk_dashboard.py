import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(
    page_title="Elliptic Crypto Forensic AML Dashboard",
    page_icon="🪙",
    layout="wide"
)

st.title("🪙 Elliptic Bitcoin Forensic AML & Financial Crime Dashboard")
st.markdown("**Domain:** Crypto Anti-Money Laundering (AML) | **Dataset:** Elliptic Bitcoin On-Chain Network (Classes, Edges & Features)")

@st.cache_data
def load_elliptic_data():
    # Path to dataset folder
    folder_path = "elliptic_bitcoin_dataset"
    classes_file = os.path.join(folder_path, "elliptic_txs_classes.csv")
    edges_file = os.path.join(folder_path, "elliptic_txs_edgelist.csv")
    features_file = os.path.join(folder_path, "elliptic_txs_features.csv")

    if not os.path.exists(classes_file):
        # Fallback to current directory if not inside folder
        classes_file = "elliptic_txs_classes.csv"
        edges_file = "elliptic_txs_edgelist.csv"
        features_file = "elliptic_txs_features.csv"

    if os.path.exists(classes_file):
        classes_df = pd.read_csv(classes_file)
        class_map = {'1': 'Illicit (High Risk)', '2': 'Licit (Legitimate)', 'unknown': 'Unlabeled'}
        classes_df['risk_category'] = classes_df['class'].map(class_map)

        # Load Edges for degree calculation (Volume of connected flows)
        if os.path.exists(edges_file):
            edges_df = pd.read_csv(edges_file)
            tx_degrees = edges_df['txId1'].value_counts().reset_index()
            tx_degrees.columns = ['txId', 'connection_count']
            classes_df = pd.merge(classes_df, tx_degrees, on='txId', how='left').fillna({'connection_count': 0})
        else:
            classes_df['connection_count'] = 0

        # Load first few timestamp/feature columns from features file without crashing RAM
        if os.path.exists(features_file):
            feat_cols = pd.read_csv(features_file, nrows=5, header=None)
            # Read first 2 columns: txId and Time Step
            features_df = pd.read_csv(features_file, header=None, usecols=[0, 1], names=['txId', 'time_step'])
            classes_df = pd.merge(classes_df, features_df, on='txId', how='left')
        else:
            classes_df['time_step'] = 1

        return classes_df
    else:
        st.error("⚠️ Elliptic dataset files not found! Please check folder location.")
        return pd.DataFrame()

df = load_elliptic_data()

if not df.empty:
    # Sidebar Filters
    st.sidebar.header("🔍 Forensic Filters")
    selected_class = st.sidebar.multiselect(
        "Select Risk Category:",
        options=df["risk_category"].unique(),
        default=df["risk_category"].unique()
    )
    
    filtered_df = df[df["risk_category"].isin(selected_class)]

    # Key Metrics
    total_txns = len(filtered_df)
    illicit_txns = len(filtered_df[filtered_df["class"] == '1'])
    licit_txns = len(filtered_df[filtered_df["class"] == '2'])
    illicit_rate = (illicit_txns / total_txns * 100) if total_txns > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔗 Total Bitcoin Transactions", f"{total_txns:,}")
    col2.metric("🚨 Illicit Transactions (Ransom/Scam)", f"{illicit_txns:,}")
    col3.metric("✅ Legitimate Flow", f"{licit_txns:,}")
    col4.metric("📈 Illicit Alert Rate (%)", f"{illicit_rate:.2f}%")

    st.markdown("---")

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📌 Risk Classification Breakdown")
        class_counts = filtered_df['risk_category'].value_counts().reset_index()
        class_counts.columns = ['Risk Category', 'Count']
        fig_bar = px.bar(
            class_counts, x='Risk Category', y='Count',
            color='Risk Category',
            color_discrete_map={
                'Illicit (High Risk)': '#E63946',
                'Licit (Legitimate)': '#2A9D8F',
                'Unlabeled': '#A8DADC'
            }
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("⏱️ Transaction Volume Over Time Steps")
        if 'time_step' in filtered_df.columns:
            time_trend = filtered_df.groupby(['time_step', 'risk_category']).size().reset_index(name='count')
            fig_line = px.line(
                time_trend, x='time_step', y='count', color='risk_category',
                labels={'time_step': 'Time Step (Elliptic Timeline)', 'count': 'Transaction Count'},
                color_discrete_map={
                    'Illicit (High Risk)': '#E63946',
                    'Licit (Legitimate)': '#2A9D8F',
                    'Unlabeled': '#A8DADC'
                }
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # Detailed High Risk Drilldown Table
    st.subheader("⚠️ High-Risk Illicit Bitcoin Transactions (Network Connections)")
    illicit_table = filtered_df[filtered_df["class"] == '1'][["txId", "risk_category", "connection_count", "time_step"]].sort_values(by="connection_count", ascending=False).head(100)
    st.dataframe(illicit_table, use_container_width=True)
