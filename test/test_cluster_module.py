# test_cluster_module.py
import os
from clustering.cluster import load_data, compute_gower_distance, cluster_hierarchical, evaluate_clusters
from datetime import datetime

# Build an absolute path to the Excel file in your `data/` folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))   # one level up from test/
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'sample_customer_database_5000_singapore.xlsx')

# 1. Load a small sample of your data
df, X = load_data(DATA_FILE, datetime(2025,6,11))
# X_small = X.iloc[:100]  # speed up

# 2. Compute distances
D, D_cond = compute_gower_distance(X)

# 3. Cluster with k=3 for a quick check
Z, labels = cluster_hierarchical(D_cond, k=6)
print("Labels:", labels[:10])

# 4. Evaluate
scores = evaluate_clusters(X, D, labels)
print("Scores:", scores)
