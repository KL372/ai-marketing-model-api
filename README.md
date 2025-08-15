# AI Marketing Model API (Flask)

Flask API that generates channel-specific marketing copy using OpenAI.
- POST /generate -> returns options: [{hook, body_text, call_to_action}, ...]
- GET /health -> small JSON for uptime checks

## Prerequisites
- Python 3.10+
- pip

## Quick Start
```bash
# from ai-marketing-model-api/
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env         # put your real OpenAI key in .env
python app.py                # API at http://localhost:5001
```
Health check: open http://localhost:5001/health

## Configuration (.env)
```ini
OPENAI_API_KEY=sk-REPLACE_ME
# If your key is project-scoped (sk-proj-...), also set:
# OPENAI_PROJECT=proj_XXXXXXXX
PORT=5001
```
The app loads .env early (e.g., in openai_client.py using load_dotenv(find_dotenv())).

## Endpoints

### GET /health
Response:
```json
{ "ok": true }
```

### POST /generate
Content-Type: application/json
Body (example):
```json
{
  "stage": "awareness",
  "channel": "Email",
  "product": "Eco Bottle",
  "target_audience": "Urban commuters",
  "industry": "Consumer goods",
  "marketing_objective": "Drive site visits",
  "business_background": "DTC e-commerce",
  "benefits": "Reusable, BPA-free, leakproof",
  "style": "personalized",
  "tone": "friendly",
  "more_instructions": "Keep under 120 words",
  "n_options": 3
}
```
Response:
```json
{
  "options": [
    { "hook": "...", "body_text": "...", "call_to_action": "..." },
    { "hook": "...", "body_text": "...", "call_to_action": "..." },
    { "hook": "...", "body_text": "...", "call_to_action": "..." }
  ]
}
```

#### cURL smoke test
Git Bash / macOS / Linux
```bash
curl -X POST http://localhost:5001/generate   -H "Content-Type: application/json"   -d '{"stage":"awareness","channel":"Email","product":"Eco Bottle","target_audience":"Urban commuters","industry":"Consumer goods","marketing_objective":"Drive site visits","business_background":"DTC e-commerce","benefits":"Reusable, BPA-free, leakproof","style":"personalized","tone":"friendly","n_options":2}'
```
Windows CMD
```cmd
curl -X POST http://localhost:5001/generate ^
  -H "Content-Type: application/json" ^
  -d "{"stage":"awareness","channel":"Email","product":"Eco Bottle","target_audience":"Urban commuters","industry":"Consumer goods","marketing_objective":"Drive site visits","business_background":"DTC e-commerce","benefits":"Reusable, BPA-free, leakproof","style":"personalized","tone":"friendly","n_options":2}"
```

## Project Structure
```
ai-marketing-model-api/
  app.py
  openai_client.py
  requirements.txt
  .env.example
  .gitignore
```

## Implementation Notes
- CORS is enabled in app.py so the UI (port 3000) can call the API (port 5001).
- The OpenAI client is created with OPENAI_API_KEY; if you use a project-scoped key (sk-proj-...), also set OPENAI_PROJECT and pass it when creating the client.

## Troubleshooting
- 401 invalid_api_key -> confirm .env has a valid key (no quotes/spaces); for sk-proj-... add OPENAI_PROJECT. Restart the server.
- 415 Unsupported Media Type -> ensure Content-Type: application/json is sent in requests.
- CORS error in browser -> confirm flask-cors is installed and CORS(app) is called.
- UI can't reach API -> ensure the server is running on port 5001 and the UI's BACKEND_URL matches.

## Notes
- Do not commit .env, .venv/, or __pycache__/ (see .gitignore).
- To change the port, set PORT in .env.
