"""
clustering/cluster.py
Purpose: Thin wrapper around the serialized GowerHierarchicalClusterer artifact.
- Resolves the path to the saved pipeline (cluster_pipeline.pkl)
- Loads it once at import time (avoids per-request disk I/O)
- Exposes a small helper function `get_segment()` used by the Flask /cluster route
"""
from clustering.pipeline import GowerHierarchicalClusterer
import os

# Absolute path to the serialized model artifact, relative to this file.
# Example: <project>/ai-marketing-model-api/clustering/cluster_pipeline.pkl
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), 'cluster_pipeline.pkl')
# Load the trained clustering pipeline ONCE at import time.
# This keeps request handling fast (no repeated disk reads).
# If the file is missing/incompatible, an exception will be raised on import.
clusterer = GowerHierarchicalClusterer.load(PIPELINE_PATH)

def get_segment(data: dict) -> int:
    """
    Return the flat cluster label for a single customer record.

    Parameters
    ----------
    data : dict
        Must include the following keys (strings):
          - 'Loyalty Tier' : categorical (e.g., 'Gold', 'Silver', ...)
          - 'Gender'       : categorical (e.g., 'Male', 'Female', ...)
          - 'Location'     : categorical (e.g., 'Singapore')
          - 'Date Joined'  : date string parseable by pandas.to_datetime (e.g., '2023-06-12')

        Notes:
          - Extra keys (e.g., 'product', 'channel') are ignored by the model.
          - The model internally derives `tenure_days` from 'Date Joined'
            using the `current_date` stored in the saved artifact.

    Returns
    -------
    int
        Cluster label in the range [1..k], where `k` was set when the model was trained.

    Possible Errors
    ---------------
    - FileNotFoundError / UnpicklingError: if the artifact is missing or incompatible.
    - ValueError: if 'Date Joined' cannot be parsed into a date.
    """

    return clusterer.predict(data)
