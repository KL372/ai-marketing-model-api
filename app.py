# app.py
# Purpose: Expose REST endpoints for health, content generation, and (demo)
# clustering. Applies channel-specific temperature/max_tokens tuning.
from flask import Flask, request, jsonify
from clustering.cluster import get_segment
from generation.openai_client import generate_content
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # enable cross-origin requests from the UI

@app.route('/')
def home():
    """
    Health check endpoint.
    Returns a simple JSON message to confirm the API is running.
    Useful for debugging and deployment checks.
    """

    return jsonify({"message": "AI Marketing API is running."})

@app.route('/cluster', methods=['POST'])
#Purpose: run customer segmentation and return cluster assignment + summary stats.
def cluster_api():
    """
    Demo endpoint: run customer segmentation and return cluster assignment.

    Request JSON must contain:
      product, channel, Date Joined, Loyalty Tier, Gender, Location
    """
    data = request.get_json() or {}
     # Minimal input validation: all required fields must be present
    if not all(k in data for k in ('product','channel','Date Joined','Loyalty Tier','Gender','Location')):
        return jsonify({"error":"Missing clustering inputs"}), 400

    try:
        segment = get_segment(data)
        return jsonify({"cluster": segment})
    except Exception as e:
        # Bubble up any model/IO/parsing errors
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_api():
    """
    Generate channel-appropriate marketing copy.

    Expected JSON:
      Required: stage, channel, product, target_audience, industry,
                marketing_objective, business_background, benefits
      Optional: style, tone, more_instructions, n_options

    Returns:
      {"options": [{"hook": "...", "body_text": "...", "call_to_action": "..."}, ...]}
    """
    data = request.get_json() or {}
    # Validate that all required prompt fields are present
    required = [
        'stage','channel','product','target_audience','industry',
        'marketing_objective','business_background','benefits'
    ]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
      
    # Ensure optional fields are present, even if empty
    data.setdefault('style', "")
    data.setdefault('tone', "")
    data.setdefault('more_instructions', "")
    
    # --- BEGIN: Temperature and max_tokens logic ---
    channel = data.get('channel', '').lower()
    stage = data.get('stage', '').lower()

    # sensible defaults
    temperature = 0.7
    max_tokens = 120

   # per-channel tuning (kept conservative for professional channels)
    if channel == "twitter":
        temperature = 0.95# More creative for short posts
        max_tokens = 80
    elif channel == "linkedin":
        temperature = 0.6  # More professional tone
        max_tokens = 120
    elif channel == "email":
        temperature = 0.5 # More factual and concise
        max_tokens = 180
    elif channel == "instagram":
        temperature = 0.85 # More playful and engaging
        max_tokens = 120
     # --- END: Temperature and max_tokens adjustment logic ---
        
    try:
        # Call OpenAI content generation with the adjusted parameters
        options = generate_content(
            data['stage'],
            data['channel'],
            data,
            n_options = data.get('n_options', 3),
            temperature=temperature,
            max_tokens=max_tokens
        )
        return jsonify({"options": options})
    except Exception as e:
        # Return API error if generation fails
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run Flask app on all network interfaces, port 5001
    # Debug mode enabled for development
    # Dev server (do not use in production)
    app.run(host='0.0.0.0', port=5001, debug=True)



