# import os
# import pandas as pd
# import numpy as np
# from typing import Tuple
# from datetime import datetime
# from gower import gower_matrix
# from scipy.spatial.distance import squareform
# from scipy.cluster.hierarchy import linkage, fcluster
# from sklearn.metrics import (
#     silhouette_score,
#     calinski_harabasz_score,
#     davies_bouldin_score
# )

# def load_data(path: str, current_date: datetime) -> Tuple[pd.DataFrame, pd.DataFrame]:
#     """
#     Load raw data, compute tenure_days, and return full df + feature matrix X.
#     """
#     df = pd.read_excel(path)
#     df['tenure_days'] = (current_date - pd.to_datetime(df['Date Joined'])).dt.days
#     X = df[['Loyalty Tier', 'Gender', 'Location', 'tenure_days']]
#     return df, X

# def compute_gower_distance(
#     X: pd.DataFrame,
#     cat_features: list = [True, True, True, False]
# ) -> Tuple[np.ndarray, np.ndarray]:
#     """
#     Compute the Gower distance matrix and its condensed form.
#     """
#     D = gower_matrix(X, cat_features=cat_features)
#     D_condensed = squareform(D, checks=False)
#     return D, D_condensed

# def cluster_hierarchical(
#     D_condensed: np.ndarray,
#     k: int,
#     method: str = 'average'
# ) -> Tuple[np.ndarray, np.ndarray]:
#     """
#     Perform hierarchical clustering and return linkage Z and flat labels.
#     """
#     Z = linkage(D_condensed, method=method)
#     labels = fcluster(Z, k, criterion='maxclust')
#     return Z, labels

# def evaluate_clusters(
#     X: pd.DataFrame,
#     D_precomputed: np.ndarray,
#     labels: np.ndarray
# ) -> dict:
#     """
#     X: DataFrame with both categorical and numeric columns.
#     D_precomputed: full Gower distance matrix.
#     labels: cluster labels array.
#     """
#     # 1. Silhouette on the precomputed Gower distances
#     sil = silhouette_score(D_precomputed, labels, metric='precomputed')

#     # 2. One-hot encode all categorical columns
#     X_enc = pd.get_dummies(X, drop_first=True)

#     # 3. Compute CH & DB on the numeric matrix
#     ch = calinski_harabasz_score(X_enc.values, labels)
#     db = davies_bouldin_score(X_enc.values, labels)

#     return {'silhouette': sil, 'calinski_harabasz': ch, 'davies_bouldin': db}

# def evaluate_k_range(
#     X: pd.DataFrame,
#     D_precomputed: np.ndarray,
#     D_condensed: np.ndarray,
#     k_min: int = 2,
#     k_max: int = 10,
#     method: str = 'average'
# ) -> pd.DataFrame:
#     """
#     Compute evaluation metrics for each k in [k_min..k_max] and return as DataFrame.
#     """
#     records = []
#     for k in range(k_min, k_max + 1):
#         _, labels = cluster_hierarchical(D_condensed, k, method)
#         scores = evaluate_clusters(X, D_precomputed, labels)
#         records.append({'k': k, **scores})
#     return pd.DataFrame.from_records(records)

# def main():
#     # CONFIGURE
#     data_path = os.path.join('..', 'my_data', 'sample_customer_database_5000_singapore.xlsx')
#     current_date = datetime(2025, 6, 11)

#     # 1) Load and prepare data
#     df, X = load_data(data_path, current_date)

#     # 2) Compute Gower distances
#     D, D_cond = compute_gower_distance(X)

#     # 3) Evaluate metrics over a range of k
#     eval_df = evaluate_k_range(X, D, D_cond, k_min=2, k_max=10)
#     print("Cluster evaluation (k vs. scores):")
#     print(eval_df.to_string(index=False))

#     # 4) Choose best k by max Silhouette
#     best_k = int(eval_df.loc[eval_df['silhouette'].idxmax(), 'k'])
#     print(f"\n→ Best number of clusters by Silhouette: k = {best_k}")

#     # 5) Final clustering with best_k
#     Z, labels = cluster_hierarchical(D_cond, best_k)
#     df['cluster'] = labels

#     # 6) Save assignments
#     out_csv = 'hierarchical_cluster_assignments.csv'
#     df.to_csv(out_csv, index=False)
#     print(f"Cluster assignments saved to `{out_csv}`")

# if __name__ == '__main__':
#     main()


# clustering/cluster.py(2)

# import os
# import pandas as pd
# import numpy as np
# from typing import Tuple
# from datetime import datetime
# from gower import gower_matrix
# from scipy.spatial.distance import squareform
# from scipy.cluster.hierarchy import linkage, fcluster
# from sklearn.metrics import (
#     silhouette_score,
#     calinski_harabasz_score,
#     davies_bouldin_score
# )
# from sklearn.preprocessing import StandardScaler

# def load_data(path: str, current_date: datetime) -> Tuple[pd.DataFrame, pd.DataFrame]:
#     df = pd.read_excel(path)
#     df['tenure_days'] = (current_date - pd.to_datetime(df['Date Joined'])).dt.days
#     X = df[['Loyalty Tier', 'Gender', 'Location', 'tenure_days']]
#     return df, X

# def compute_gower_distance(
#     X: pd.DataFrame,
#     cat_features: list = [True, True, True, False]
# ) -> Tuple[np.ndarray, np.ndarray]:
#     D = gower_matrix(X, cat_features=cat_features)
#     D_condensed = squareform(D, checks=False)
#     return D, D_condensed

# def prepare_mixed_numeric(
#     X: pd.DataFrame
# ) -> np.ndarray:
#     """
#     Mixed encoding:
#       - Ordinal for Loyalty Tier
#       - Binary for Gender
#       - One-hot for Location
#       - Numeric tenure_days
#     Then standardize all features.
#     """
#     df = X.copy()

#     # 1) Ordinal encode Loyalty Tier
#     tier_map = {'Silver': 1, 'Gold': 2, 'Platinum': 3}
#     df['tier_ord'] = df['Loyalty Tier'].map(tier_map)

#     # 2) Binary encode Gender (Female=1, Male=0)
#     df['gender_bin'] = (df['Gender'] == 'Female').astype(int)

#     # 3) One-hot encode Location (drop_first to avoid collinearity)
#     loc_ohe = pd.get_dummies(df['Location'], prefix='loc', drop_first=True)

#     # 4) Combine numeric features
#     X_num = pd.concat([
#         df[['tenure_days', 'tier_ord', 'gender_bin']],
#         loc_ohe
#     ], axis=1)

#     # 5) Standardize to zero mean, unit variance
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X_num)

#     return X_scaled

# def cluster_hierarchical(
#     D_condensed: np.ndarray,
#     k: int,
#     method: str = 'average'
# ) -> Tuple[np.ndarray, np.ndarray]:
#     Z = linkage(D_condensed, method=method)
#     labels = fcluster(Z, k, criterion='maxclust')
#     return Z, labels

# def evaluate_clusters(
#     X: pd.DataFrame,
#     D_precomputed: np.ndarray,
#     labels: np.ndarray
# ) -> dict:
#     """
#     - Silhouette on Gower distances (mixed-type)
#     - CH & DB on mixed-encoded, standardized numeric matrix
#     """
#     # 1) Silhouette (mixed-type support via Gower)
#     sil = silhouette_score(D_precomputed, labels, metric='precomputed')

#     # 2) Prepare mixed-numeric matrix
#     X_mixed_num = prepare_mixed_numeric(X)

#     # 3) Calinski–Harabasz & Davies–Bouldin (numeric only)
#     ch = calinski_harabasz_score(X_mixed_num, labels)
#     db = davies_bouldin_score(X_mixed_num, labels)

#     return {
#         'silhouette': sil,
#         'calinski_harabasz': ch,
#         'davies_bouldin': db
#     }

# def evaluate_k_range(
#     X: pd.DataFrame,
#     D_precomputed: np.ndarray,
#     D_condensed: np.ndarray,
#     k_min: int = 2,
#     k_max: int = 10,
#     method: str = 'average'
# ) -> pd.DataFrame:
#     records = []
#     for k in range(k_min, k_max + 1):
#         _, labels = cluster_hierarchical(D_condensed, k, method)
#         scores = evaluate_clusters(X, D_precomputed, labels)
#         records.append({'k': k, **scores})
#     return pd.DataFrame.from_records(records)

# def main():
#     data_path = os.path.join('..', 'data', 'sample_customer_database_5000_singapore.xlsx')
#     current_date = datetime(2025, 6, 11)

#     df, X = load_data(data_path, current_date)
#     D, D_cond = compute_gower_distance(X)

#     # Evaluate silhouette + CH + DB across k = 2..10
#     eval_df = evaluate_k_range(X, D, D_cond, 2, 10)
#     print(eval_df.to_string(index=False))

#     best_k = int(eval_df.loc[eval_df['silhouette'].idxmax(), 'k'])
#     print(f"Best k by silhouette: {best_k}")

#     Z, labels = cluster_hierarchical(D_cond, best_k)
#     df['cluster'] = labels
#     df.to_csv('hierarchical_cluster_assignments.csv', index=False)
#     print("Saved cluster assignments.")

# if __name__ == '__main__':
#     main()

# clustering/cluster.py (turned old cluster.py into a thin wrapper that simply loads pretrained pipeline and exposes aget_segment function )

from clustering.pipeline import GowerHierarchicalClusterer
import os

# Load the serialized pipeline at import time
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), 'cluster_pipeline.pkl')
clusterer = GowerHierarchicalClusterer.load(PIPELINE_PATH)

def get_segment(data: dict) -> int:
    """
    data must include keys:
      'Loyalty Tier', 'Gender', 'Location', 'Date Joined'
    """
    return clusterer.predict(data)
