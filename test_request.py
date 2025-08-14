import requests
BASE = "http://localhost:5001"
def test_cluster():
    payload = {
        "product": "Eco Bottle",
        "channel": "email",
        "Date Joined": "2023-01-15",
        "Loyalty Tier": "Gold",
        "Gender": "Female",
        "Location": "Tampines"
    }
    r = requests.post(f"{BASE}/cluster", json=payload)
    print("CLUSTER →", r.status_code, r.json())
    return r.json().get("cluster")
def test_generate(cluster_label=None):
    payload = {
        "stage": "awareness",
        "channel": "Twitter",
        "product": "Eco Bottle",
        "target_audience": "Urban commuters",
        "industry": "Ecommerce",
        "marketing_objective": "Build brand recognition",
        "business_background": "We make sustainable products.",
        "benefits": "Reusable, eco-friendly",
        "n_options": 2
    }
    if cluster_label is not None:
        payload["segment"] = cluster_label
    r = requests.post(f"{BASE}/generate", json=payload)
    print("GENERATE →", r.status_code)
    for i, opt in enumerate(r.json().get("options", []), 1):
        print(f"Option {i}:")
        print(" Hook:", opt.get("hook"))
        print(" Body:", opt.get("body_text"))
        print(" CTA:", opt.get("call_to_action"))
        print()
if __name__ == "__main__":
    seg = test_cluster()
    test_generate(seg)

