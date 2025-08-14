# test/test_cluster_module.py
import os
import pandas as pd
from datetime import datetime

from clustering.pipeline import GowerHierarchicalClusterer
from scipy.cluster.hierarchy import fcluster
from gower import gower_matrix
from sklearn.metrics import silhouette_score

# Build an absolute path to the Excel file in your `data/` folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))   # one level up from test/
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'sample_customer_database_5000_singapore.xlsx')

def main():
    # --- 1) Load data (parse 'Date Joined' for tenure calculation) ---
    # Requires 'openpyxl' installed for reading .xlsx
    df = pd.read_excel(DATA_FILE, parse_dates=['Date Joined'])

    # (Optional) speed-up for quick test runs
    # df = df.sample(n=1000, random_state=42).reset_index(drop=True)

    # --- 2) Fit class-based clusterer ---
    # Use the same reference date you used previously (2025-06-11)
    ref_date = datetime(2025, 6, 11)
    model = GowerHierarchicalClusterer(k=6, current_date=ref_date).fit(df)

    # --- 3) Derive labels from the fitted linkage tree ---
    labels = fcluster(model.Z, 6, criterion='maxclust')

    print("Labels (first 10):", labels[:10])

    # --- 4) Evaluate with silhouette on the Gower distance matrix ---
    # model.X_train columns: ['Loyalty Tier','Gender','Location','tenure_days']
    D = gower_matrix(model.X_train, cat_features=[True, True, True, False])
    score = silhouette_score(D, labels, metric='precomputed')

    print("Silhouette score:", float(score))

if __name__ == "__main__":
    main()
