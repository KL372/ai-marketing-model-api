# ai-marketing-model-api
Flask API for ML clustering and AI content generation

# AI Marketing Model API

This is the backend API for the AI Marketing Content Generator project. It exposes two endpoints:

- `POST /cluster`: Determines customer segment using a pre-trained clustering model
- `POST /generate`: Generates marketing content using OpenAI based on product, funnel stage, and channel

## 🔧 Tech Stack
- Python 3.10+
- Flask
- OpenAI API
- scikit-learn (for clustering)
- Joblib (for model loading)

## 📁 Project Structure

ai-marketing-model-api/
│
├── app.py # Main Flask app
├── clustering/
│ └── cluster.py # Loads clustering model and returns segment
│
├── generation/
│ ├── openai_client.py # Calls OpenAI API
│ ├── prompt_engine.py # Builds prompts from JSON templates
│ └── prompts/templates.json # Prompt templates (by funnel stage & channel)
│
├── requirements.txt # Python dependencies
├── README.md # This file
└── .gitignore

