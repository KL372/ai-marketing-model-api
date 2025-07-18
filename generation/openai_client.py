import os
import openai
from .prompt_engine import build_prompt_messages
from dotenv import load_dotenv

# 1) Load .env (does nothing if the var is already in the environment)
load_dotenv()

# Make sure your OPENAI_API_KEY is set in the environment!
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_content(
    stage: str,
    channel: str,
    data: dict,
    n_options: int = 3,
    temperature: float = 0.7,
    max_tokens: int = 200
) -> list[str]:
    """
    - stage: one of "awareness", "consideration", "conversion"
    - channel: e.g. "Twitter", "LinkedIn", "Email"
    - data: dict with keys matching your template placeholders
    - n_options: how many variants to return
    - temperature / max_tokens: tune as needed
    """
    # 1) Build the system+user messages from your template
    messages = build_prompt_messages(stage, channel, data)

    # 2) Call the OpenAI ChatCompletion API
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        n=n_options,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # 3) Extract the generated text from each choice
    return [choice.message.content.strip() for choice in response.choices]
