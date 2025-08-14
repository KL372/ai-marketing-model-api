import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello as JSON. Output a JSON object with: \"hook\", \"body_text\", \"call_to_action\"."}
    ],
    temperature=0.7,
    max_tokens=200,
    n=1,
    response_format={"type": "json_object"}
)
print(response.choices[0].message.content)
