import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Configuration - Clean Corporate Theme
st.set_page_config(
    page_title="Elliptic Bitcoin Forensic AML Dashboard",
    layout="wide"
)

st.title("Elliptic Bitcoin Forensic AML & Financial Crime Dashboard")
st.markdown("**Domain:** On-Chain Financial Crime Analysis | **Dataset:** Elliptic Bitcoin Network (Classes, Edgelist & Aggregated Features)")

@st.cache_data
def load_full_elliptic_data():
    folder_path = "elliptic_bitcoin_dataset"
    classes_file = os.path.join(folder_path, "elliptic_txs_classes.csv")
    edges_file = os.path.join(folder_path, "elliptic_txs_edgelist.csv")
    features_file = os.path.join(folder_path, "elliptic_txs_features.csv")

    # Fallback paths
    if not os.path.exists(classes_file):
        classes_file = "elliptic_txs_classes.csv"
        edges_file = "elliptic_txs_edgelist.csv"
        features_file = "elliptic_txs_features.csv"

    if os.path.exists(classes_file):
        # 1. Load Classes
        classes_df = pd.read_csv(classes_file)
        class_map = {'1': 'Illicit (High Risk)', '2': 'Licit (Legitimate)', 'unknown': 'Unlabeled'}
        classes_df['risk_category'] = classes_df['class'].map(class_map)

        # 2. Load Edgelist (Network Connections Degree)
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

        # 3. Process Features File (Extracting Time Step & Transaction Aggregates)
        if os.path.exists(features_file):
            # Read first 5 feature columns efficiently (txId, time_step, feature_1, feature_2, feature_3)
            features_df = pd.read_csv(
                features_file, 
                header=None, 
                usecols=[0, 1, 2, 3, 4], 
                names=['txId', 'time_step', 'tx_fee_norm', 'input_count_norm', 'output_count_norm']
            )
            classes_df = pd.merge(classes_df, features_df, on='txId', how='left')
        else:
            classes_df['time_step'] = 1
            classes_df['tx_fee_norm'] = 0

        return classes_df
    else:
        st.error("Error: Elliptic dataset files not found. Please verify file directory.")
        return pd.DataFrame()

df = load_full_elliptic_data()

if not df.empty:
    # Sidebar Filters
    st.sidebar.header("Forensic Filters")
    selected_class = st.sidebar.multiselect(
        "Select Risk Category:",
        options=df["risk_category"].unique(),
        default=df["risk_category"].unique()
    )
    
    filtered_df = df[df["risk_category"].isin(selected_class)]

    # Executive Metrics
    total_txns = len(filtered_df)
    illicit_txns = len(filtered_df[filtered_df["class"] == '1'])
    licit_txns = len(filtered_df[filtered_df["class"] == '2'])
    illicit_rate = (illicit_txns / total_txns * 100) if total_txns > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", f"{total_txns:,}")
    col2.metric("Illicit Entities Flagged", f"{illicit_txns:,}")
    col3.metric("Licit Entities Verified", f"{licit_txns:,}")
    col4.metric("Illicit Exposure Rate", f"{illicit_rate:.2f}%")

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
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.subheader("Transaction Volume Trend Across Time Steps")
        if 'time_step' in filtered_df.columns:
            time_trend = filtered_df.groupby(['time_step', 'risk_category']).size().reset_index(name='count')
            fig_line = px.line(
                time_trend, x='time_step', y='count', color='risk_category',
                labels={'time_step': 'Time Step', 'count': 'Transaction Count'},
                color_discrete_map={
                    'Illicit (High Risk)': '#D90429',
                    'Licit (Legitimate)': '#2B9348',
                    'Unlabeled': '#8D99AE'
                }
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # Detailed High Risk Network Table
    st.subheader("High-Risk Illicit Transaction Network Analysis")
    cols_to_show = ["txId", "risk_category", "time_step", "total_network_degree", "inbound_connections", "outbound_connections"]
    cols_present = [c for c in cols_to_show if c in filtered_df.columns]
    
    illicit_table = filtered_df[filtered_df["class"] == '1'][cols_present].sort_values(by="total_network_degree", ascending=False).head(100)
    st.dataframe(illicit_table, use_container_width=True)
import networkx as nx

@st.cache_data
def calculate_graph_metrics(edges_df):
    # Build Directed Graph from transaction flow
    G = nx.from_pandas_edgelist(edges_df, source='txId1', target='txId2', create_using=nx.DiGraph())
    
    # Calculate PageRank (node importance in money flow)
    pagerank = nx.pagerank(G, max_iter=50)
    pr_df = pd.DataFrame(list(pagerank.items()), columns=['txId', 'pagerank_score'])
    return pr_df
