# Financial Crime Analytics & On-Chain AML Forensic Pipeline

## Executive Overview
This repository delivers an end-to-end Financial Crime, Anti-Money Laundering (AML), and Forensic Analytics infrastructure designed to detect, analyze, and visualize high-risk illicit activity within large-scale financial transaction networks. 

Moving beyond synthetic general ledger simulations, this project integrates the **Elliptic Bitcoin Dataset**-a real-world cryptocurrency network dataset mapped by Elliptic and MIT researchers - to provide actionable forensic insights across 200,000+ transaction entities.

---

## Interactive Forensic AML Dashboard

<img width="1398" height="900" alt="Screenshot 2026-09-29 at 10 03 40 PM" src="https://github.com/user-attachments/assets/c434a040-f954-4e41-80fd-bb06bbac7332" />
<img width="1400" height="900" alt="Screenshot 2026-09-29 at 11 53 29 PM" src="https://github.com/user-attachments/assets/99285db5-38d9-419e-9814-00fef94890f2" />


### Key Capabilities:
- **On-Chain Risk Quantification**: Real-time identification and aggregation of confirmed illicit entities (scams, ransomware, darknet markets) versus legitimate financial flow.
- **Network Topology Analysis**: Deep-dive degree calculations measuring transaction connection density (inbound/outbound flows) across transaction edges.
- **Time-Step Trend Mapping**: Dynamic temporal tracking of illicit transaction volumes across discrete network time steps to observe pattern shifts.
- **Granular Forensic Drilldown**: Executive-ready drilldown tables isolating high-risk transaction IDs ranked by network connection complexity.

---

## Dataset Architecture & Pipeline Design

The forensic engine processes three interconnected layers from the Elliptic Bitcoin Dataset:

1. **Transaction Classes (`elliptic_txs_classes.csv`)**: Primary risk mapping categorizing transactions into *Illicit (High Risk)*, *Licit (Legitimate)*, and *Unlabeled*.
2. **Network Edgelist (`elliptic_txs_edgelist.csv`)**: Directed graph flows mapping inputs and outputs to calculate total network connection degrees for each entity.
3. **Aggregated Features (`elliptic_txs_features.csv`)**: 166 local and aggregated graph attributes representing transaction characteristics and temporal time steps.

---

## Repository Structure

```text
.
├── 01_General_Ledger_Audit/        # Core Accounting & Schema Auditing Files
├── 02_Forensic_Whitepapers/        # Benford's Law & Internal Control Frameworks
├── 03_SQL_Engine/                  # Advanced Window Functions & Analytical Queries
├── 04_Python_Automation/           # Interactive Streamlit App & Data Pipeline
│   ├── elliptic_bitcoin_dataset/   # Real-World Elliptic CSV Files
│   └── app_risk_dashboard.py       # Streamlit Executive Forensic Dashboard
└── README.md                       # Project Documentation

## Advanced Senior Capabilities

- **Machine Learning Fraud Scoring**: Trained Random Forest Classifier delivering 0–100% Risk Probability Scores across 150,000+ unlabeled Bitcoin entities.
- **Graph Topology Mining**: Integrated network degree connections to identify high-velocity transaction nodes within directed graph flows.
- **Enterprise Containerization**: Fully dockerized application environment for seamless deployment.

---

## Docker Deployment

To run the application inside a container:

1. Build the Docker image:
   ```bash
   docker build -t aml-forensic-dashboard .
