# generation/openai_client.py
# Purpose: Wrap OpenAI Chat Completions call with messages from prompt_engine
# and return parsed JSON objects for each choice
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
    Generate n_options pieces of marketing content with keys:
    hook, body_text, call_to_action.

    Parameters
    ----------
    stage : {'awareness','consideration','conversion'}
    channel : e.g., 'Twitter','LinkedIn','Email','Instagram'
    data : dict
        Must include fields expected by the templates; optional style/tone/more_instructions.
    n_options : int
        Number of choices to request from the model.
    temperature : float
        Creativity setting (higher = more diverse).
    max_tokens : int
        Max tokens for each completion.

    Returns
    -------
    list[dict]
        Each element is a parsed JSON object (or {error, raw} on parse failure).
    """
    # Build messages using the prompt engine
    messages = build_prompt_messages(stage, channel, data)
    print("Prompt messages being sent to OpenAI:", messages)
    print("Model:", "gpt-4o")
    print("n_options:", n_options, "temperature:", temperature, "max_tokens:", max_tokens)
    try:
        # Build messages using the prompt engine
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
         # Allow Flask to handle as 500; error logged for debugging
        print("OpenAI API call error:", e)  # <--- This will show the actual error in]terminal
        raise  # This lets Flask handle it as a 500 error
    
    # Parse each choice's content into JSO
    results = []
    for choice in response.choices:
        try:
            print("OpenAI response content:", choice.message.content)
            results.append(json.loads(choice.message.content.strip()))
        except Exception as e:
            # Capture raw content for debugging when JSON parsing fails
            print("JSON parse error:", e, "content was:", choice.message.content.strip())
            results.append({"error": str(e), "raw": choice.message.content.strip()})
    return results


