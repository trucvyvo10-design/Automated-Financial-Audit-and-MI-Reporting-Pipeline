import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("Processing Elliptic Features & Training Model...")

folder_path = "elliptic_bitcoin_dataset"
classes_path = os.path.join(folder_path, "elliptic_txs_classes.csv")
features_path = os.path.join(folder_path, "elliptic_txs_features.csv")

# Load data
classes = pd.read_csv(classes_path if os.path.exists(classes_path) else "elliptic_txs_classes.csv")
features = pd.read_csv(features_path if os.path.exists(features_path) else "elliptic_txs_features.csv", header=None)

# Merge classes and features (first 30 feature columns for efficiency)
feature_cols = [0, 1] + list(range(2, 32))
features_sub = features[feature_cols]
col_names = ['txId', 'time_step'] + [f'feat_{i}' for i in range(1, 31)]
features_sub.columns = col_names

df = pd.merge(classes, features_sub, on='txId')

# Filter labeled dataset for training
labeled_df = df[df['class'].isin(['1', '2'])].copy()
labeled_df['target'] = labeled_df['class'].map({'1': 1, '2': 0}) # 1: Illicit, 0: Licit

X = labeled_df.drop(columns=['txId', 'class', 'target'])
y = labeled_df['target']

# Train Random Forest Classifier
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Predict risk probabilities for ALL transactions (including Unlabeled)
X_all = df.drop(columns=['txId', 'class'])
df['predicted_risk_score'] = model.predict_proba(X_all)[:, 1] * 100

# Save predictions summary for fast Dashboard loading
output_df = df[['txId', 'class', 'time_step', 'predicted_risk_score']]
output_df.to_csv("elliptic_ml_predictions.csv", index=False)
print("Successfully generated 'elliptic_ml_predictions.csv' with ML Risk Scores!")
