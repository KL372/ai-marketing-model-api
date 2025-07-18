#select the proper stage/template, insert channel and all user‐supplied fields, and output the system+user messages for OpenAI.

import json
import os
from typing import Dict, List

TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), 'prompts', 'templates.json'
)
_templates: Dict = None


def load_templates() -> Dict:
    global _templates
    if _templates is None:
        with open(TEMPLATE_PATH, 'r') as f:
            _templates = json.load(f)
    return _templates


def build_prompt_messages(
    stage: str,
    channel: str,
    data: Dict[str, str]
) -> List[Dict[str, str]]:
    """
    Build system+user messages for a given funnel stage and channel.
    data should include keys: product, target_audience, industry,
    marketing_objective, business_background, benefits.
    """
    templates = load_templates()
    section = templates.get(stage, {}).get('default', {})
    system_msg = section.get('system', '')
    user_template = section.get('user', '')

    # Insert channel into details as well
    filled = user_template.replace('{{channel}}', channel)
    for key, val in data.items():
        placeholder = f'{{{{{key}}}}}'
        filled = filled.replace(placeholder, str(val))

    return [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': filled}
    ]
