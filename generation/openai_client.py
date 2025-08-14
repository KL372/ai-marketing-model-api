import os
import openai
import json
from .prompt_engine import build_prompt_messages
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI Key loaded:", os.getenv("OPENAI_API_KEY")[:8])


def generate_content(
    stage: str,
    channel: str,
    data: dict,
    n_options: int = 3,
    temperature: float = 0.7,
    max_tokens: int = 200
) -> list[dict]:
    """
    Generates n_options of marketing content as dicts with keys: hook, body_text, call_to_action.
    - stage: one of "awareness", "consideration", "conversion"
    - channel: e.g. "Twitter", "LinkedIn", "Email"
    - data: dict with keys matching your template placeholders
    - n_options: how many variants to return
    - temperature / max_tokens: tune as needed
    """
    messages = build_prompt_messages(stage, channel, data)
    print("Prompt messages being sent to OpenAI:", messages)
    print("Model:", "gpt-4o")
    print("n_options:", n_options, "temperature:", temperature, "max_tokens:", max_tokens)
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n = n_options,
            response_format={"type": "json_object"}
            
        )
        print(f"Using temperature={temperature}, max_tokens={max_tokens}, channel={channel}, stage={stage}")

        print("Raw OpenAI API response received!")
    except Exception as e:
        print("OpenAI API call error:", e)  # <--- This will show you the actual error in your terminal
        raise  # This lets Flask handle it as a 500 error

    results = []
    for choice in response.choices:
        try:
            print("OpenAI response content:", choice.message.content)
            results.append(json.loads(choice.message.content.strip()))
        except Exception as e:
            print("JSON parse error:", e, "content was:", choice.message.content.strip())
            results.append({"error": str(e), "raw": choice.message.content.strip()})
    return results


