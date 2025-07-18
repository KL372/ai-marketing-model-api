from flask import Flask, request, jsonify
from clustering.cluster import get_segment
from generation.openai_client import generate_content
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "AI Marketing API is running."})

@app.route('/cluster', methods=['POST'])
def cluster_api():
    data = request.get_json() or {}
    # You probably want more fields here, but this is minimal:
    if not all(k in data for k in ('product','channel','Date Joined','Loyalty Tier','Gender','Location')):
        return jsonify({"error":"Missing clustering inputs"}), 400

    try:
        segment = get_segment(data)
        return jsonify({"cluster": segment})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_api():
    data = request.get_json() or {}
    # required fields for prompt:
    required = [
        'stage','channel','product','target_audience','industry',
        'marketing_objective','business_background','benefits'
    ]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        options = generate_content(
            data['stage'],
            data['channel'],
            data,
            n_options = data.get('n_options', 3)
        )
        return jsonify({"options": options})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


# Key changes:

# The /generate route now pulls out stage and channel explicitly.

# We pass the entire data dict plus n_options into generate_content.

# The response JSON is now { "options": [ … ] } to match your multiple‐variants API.
