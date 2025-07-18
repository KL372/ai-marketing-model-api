#  move all of the core functions (load_data, compute_gower_distance, prepare_mixed_numeric, cluster_hierarchical, evaluate_clusters, evaluate_k_range) from the previous cluster.py into a single class:

import os
import pandas as pd
import numpy as np
from datetime import datetime
from gower import gower_matrix
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import joblib

class GowerHierarchicalClusterer:
    def __init__(self, k=6, method='average', current_date=None):
        self.k = k
        self.method = method
        self.current_date = current_date or datetime.now()
        self.Z = None
        self.X_train = None  # training features for distance computations

    def fit(self, df: pd.DataFrame):
        # 1) Compute tenure_days
        df = df.copy()
        df['tenure_days'] = (self.current_date - pd.to_datetime(df['Date Joined'])).dt.days
        # 2) Store training features
        self.X_train = df[['Loyalty Tier','Gender','Location','tenure_days']]
        # 3) Compute Gower distance & linkage tree
        D = gower_matrix(self.X_train, cat_features=[True,True,True,False])
        D_cond = squareform(D, checks=False)
        self.Z = linkage(D_cond, method=self.method)
        return self

    def predict(self, record: dict) -> int:
        # Build single-row DataFrame
        df_new = pd.DataFrame([record])
        df_new['tenure_days'] = (self.current_date - pd.to_datetime(df_new['Date Joined'])).dt.days
        X_new = df_new[['Loyalty Tier','Gender','Location','tenure_days']]
        # Combine with training data
        X_combined = pd.concat([self.X_train, X_new], ignore_index=True)
        D_combined = gower_matrix(X_combined, cat_features=[True,True,True,False])
        # Get distances of new sample to training set
        n = len(self.X_train)
        dist_to_train = D_combined[-1, :n]
        # Find nearest neighbor’s cluster
        labels_train = fcluster(self.Z, self.k, criterion='maxclust')
        return int(labels_train[dist_to_train.argmin()])

    def save(self, path: str):
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str):
        return joblib.load(path)
