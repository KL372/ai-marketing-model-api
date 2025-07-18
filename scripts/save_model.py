# scripts/save_model.py

import os
import pandas as pd
from datetime import datetime
from clustering.pipeline import GowerHierarchicalClusterer

# 0) Compute project root and data path robustly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))           # .../ai-marketing-model-api/scripts
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)                        # .../ai-marketing-model-api
DATA_PATH = os.path.join(PROJECT_ROOT, 'data',
    'sample_customer_database_5000_singapore.xlsx')

# 1) Load full dataset
df = pd.read_excel(DATA_PATH)

# 2) Train pipeline
pipeline = GowerHierarchicalClusterer(
    k=6,
    current_date=datetime(2025,6,11)
)
pipeline.fit(df)

# 3) Serialize to clustering/
OUT_PATH = os.path.join(PROJECT_ROOT, 'clustering', 'cluster_pipeline.pkl')
pipeline.save(OUT_PATH)
print(f"✅ Pipeline saved to {OUT_PATH}")


