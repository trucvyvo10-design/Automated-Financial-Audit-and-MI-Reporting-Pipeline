import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(
    page_title="Elliptic Bitcoin Forensic AML Dashboard",
    layout="wide"
)

st.title("Elliptic Bitcoin Forensic AML & Financial Crime Dashboard")
st.markdown("**Domain:** On-Chain Financial Crime Analysis | **AI/ML Engine:** Random Forest Fraud Scoring (0-100%)")

@st.cache_data
def load_full_elliptic_data():
    folder_path = "elliptic_bitcoin_dataset"
    classes_file = os.path.join(folder_path, "elliptic_txs_classes.csv")
    edges_file = os.path.join(folder_path, "elliptic_txs_edgelist.csv")
    ml_file = "elliptic_ml_predictions.csv"

    if not os.path.exists(classes_file):
        classes_file = "elliptic_txs_classes.csv"
        edges_file = "elliptic_txs_edgelist.csv"

    if os.path.exists(classes_file):
        classes_df = pd.read_csv(classes_file)
        class_map = {'1': 'Illicit (High Risk)', '2': 'Licit (Legitimate)', 'unknown': 'Unlabeled'}
        classes_df['risk_category'] = classes_df['class'].map(class_map)

        # Merge ML Predictions
        if os.path.exists(ml_file):
            ml_df = pd.read_csv(ml_file)
            classes_df = pd.merge(classes_df, ml_df[['txId', 'predicted_risk_score']], on='txId', how='left')
        else:
            classes_df['predicted_risk_score'] = 0.0

        # Load Edgelist (Connections Degree)
        if os.path.exists(edges_file):
            edges_df = pd.read_csv(edges_file)
            in_degree = edges_df['txId2'].value_counts().reset_index()
            in_degree.columns = ['txId', 'inbound_connections']
            out_degree = edges_df['txId1'].value_counts().reset_index()
            out_degree.columns = ['txId', 'outbound_connections']
            
            classes_df = pd.merge(classes_df, in_degree, on='txId', how='left').fillna({'inbound_connections': 0})
            classes_df = pd.merge(classes_df, out_degree, on='txId', how='left').fillna({'outbound_connections': 0})
            classes_df['total_network_degree'] = classes_df['inbound_connections'] + classes_df['outbound_connections']
        else:
            classes_df['total_network_degree'] = 0

        return classes_df
    else:
        st.error("Error: Dataset files not found.")
        return pd.DataFrame()

df = load_full_elliptic_data()

if not df.empty:
    # Sidebar Filters (Added unique key='main_risk_filter' to avoid Duplicate ID error)
    st.sidebar.header("Forensic Filters")
    selected_class = st.sidebar.multiselect(
        "Select Risk Category:",
        options=df["risk_category"].unique(),
        default=df["risk_category"].unique(),
        key="main_risk_filter"
    )
    
    filtered_df = df[df["risk_category"].isin(selected_class)]

    # Executive Metrics
    total_txns = len(filtered_df)
    illicit_txns = len(filtered_df[filtered_df["class"] == '1'])
    licit_txns = len(filtered_df[filtered_df["class"] == '2'])
    avg_ml_risk = filtered_df['predicted_risk_score'].mean() if 'predicted_risk_score' in filtered_df.columns else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", f"{total_txns:,}")
    col2.metric("Confirmed Illicit Entities", f"{illicit_txns:,}")
    col3.metric("Verified Licit Entities", f"{licit_txns:,}")
    col4.metric("Avg ML Risk Score", f"{avg_ml_risk:.2f}%")

    st.markdown("---")

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Risk Classification Distribution")
        class_counts = filtered_df['risk_category'].value_counts().reset_index()
        class_counts.columns = ['Risk Category', 'Count']
        fig_bar = px.bar(
            class_counts, x='Risk Category', y='Count',
            color='Risk Category',
            color_discrete_map={
                'Illicit (High Risk)': '#D90429',
                'Licit (Legitimate)': '#2B9348',
                'Unlabeled': '#8D99AE'
            }
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, width="stretch")

    with col_chart2:
        st.subheader("ML Fraud Risk Distribution (0-100%)")
        if 'predicted_risk_score' in filtered_df.columns:
            fig_hist = px.histogram(
                filtered_df, x="predicted_risk_score", nbins=50,
                labels={'predicted_risk_score': 'ML Predicted Risk Score (%)'},
                color_discrete_sequence=['#D90429']
            )
            st.plotly_chart(fig_hist, width="stretch")

    # High Risk Drilldown Table with ML Risk Score
    st.subheader("High-Risk AI Fraud Predictions Drilldown")
    show_cols = ["txId", "risk_category", "predicted_risk_score", "total_network_degree", "inbound_connections", "outbound_connections"]
    present_cols = [c for c in show_cols if c in filtered_df.columns]
    
    illicit_table = filtered_df.sort_values(by="predicted_risk_score" if 'predicted_risk_score' in filtered_df.columns else "total_network_degree", ascending=False)[present_cols].head(100)
    
    st.dataframe(illicit_table, width="stretch")
