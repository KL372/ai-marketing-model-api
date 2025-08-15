# clustering/pipeline.py
# Purpose: Train/serve a hierarchical clustering pipeline over mixed-type data
# using Gower distance. Provides .fit() for training, .predict() for assigning
# a new record to the nearest neighbor's flat cluster, and .save/.load.
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
    
    """
    Gower-based hierarchical clustering for mixed categorical/numeric data.

    Parameters
    ----------
    k : int
        Number of flat clusters to form (used when cutting the linkage tree).
    method : str
        Linkage criterion (e.g., 'average'). Must be compatible with
        distance-based linkage.
    current_date : datetime | None
        "Today" reference used to compute `tenure_days`. If None, defaults
        to datetime.now() at instantiation; for reproducible results, pass
        a fixed date during training and inference.

    Attributes
    ----------
    Z : np.ndarray | None
        Linkage matrix from scipy.cluster.hierarchy.linkage over the
        condensed Gower distance.
    X_train : pd.DataFrame | None
        DataFrame of training features:
        ['Loyalty Tier','Gender','Location','tenure_days'].
    """
    
    def __init__(self, k=6, method='average', current_date=None):
        self.k = k
        self.method = method
        self.current_date = current_date or datetime.now()
        self.Z = None
        self.X_train = None  # training features for distance computations

    def fit(self, df: pd.DataFrame):
        
        """
        Fit the model: compute `tenure_days`, store training features,
        compute Gower distances, and build the hierarchical linkage.

        Notes
        -----
        - Expects df to contain columns: 'Date Joined', 'Loyalty Tier',
          'Gender', 'Location' (matching inference keys).
        - Gower cat mask: [True, True, True, False].
        """
        
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
        
        """
        Assign a new record to a flat cluster via nearest-neighbor strategy.

        Steps
        -----
        1) Build 1-row DF from `record`.
        2) Compute its `tenure_days` using the same `current_date`.
        3) Concatenate with X_train and recompute Gower on combined set.
        4) Take distances from the new row to the training set.
        5) Cut the training dendrogram into `k` flat clusters and return
           the cluster label of the nearest training neighbor.

        Returns
        -------
        int : cluster label (1..k)
        """
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
        """Serialize the fitted object (including X_train, Z, current_date)."""
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str):
        """Load a serialized GowerHierarchicalClusterer."""
        return joblib.load(path)
