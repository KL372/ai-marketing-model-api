# generation/prompt_engine.py
# Purpose: Build system+user messages for OpenAI based on stage/channel,
# inject examples per channel/style, and append optional style/tone/instructions.

import json
import os
from typing import Dict, List

# Channel-specific example lines used to "prime" style expectations.
EXAMPLES = {
    "twitter": {
        "witty": "Desk getting wild? FlexiMat’s got you covered—literally. 😏 #DeskGlowUp",
        "meme": "Me: ‘I’ll clean my desk tomorrow.’ FlexiMat: ‘You mean today.’ 😎🧼 #ProcrastinatorProblems",
        "poll": "Poll: Would you rather have a tidy desk or a creative mess? Vote below! #WorkspaceDebate",
        "question": "Ever spilled coffee on your notes? ☕😱 What’s your worst desk disaster? #FlexiMatSaves",
        "announcement": "Introducing FlexiMat: the foldable, washable desk mat for all your study & work needs! #DeskUpgrade",
        "call-to-action": "Transform your desk. Grab a FlexiMat today! [link] #StudyHack",
        "": "Introducing FlexiMat: the foldable, washable desk mat for all your study & work needs! #DeskUpgrade"  # default
    },
    "instagram": {
        "storytelling": "Meet Alex—between late-night study sessions and coffee runs, their desk took a beating. FlexiMat made cleanup (and life) a breeze. 🌟 #StudyStory",
        "meme": "That feeling when you spill juice but remember you’ve got a FlexiMat. 😅🧃 #LifeSaverMat",
        "visual": "Clean lines. Bold colors. Your desk, your vibe. FlexiMat fits any style—swipe for inspo! 🎨✨ #WorkspaceAesthetic",
        "announcement": "Just dropped: FlexiMat! Fold, wash, repeat—never stress a messy desk again. Link in bio. #FlexiLaunch",
        "poll": "Which FlexiMat color would you pick for your desk? 🔵 Blue 🟣 Purple 🟢 Green Vote in our story! #DeskChoice",
        "": "Just dropped: FlexiMat! Fold, wash, repeat—never stress a messy desk again. Link in bio. #FlexiLaunch"
    },
    "email": {
        "personalized": "Hi Jamie, Ready for a smoother semester? Keep your desk clean and your mind focused with FlexiMat. Enjoy 10% off—just for you!",
        "story": "From coffee spills to midnight snack crumbs, FlexiMat’s seen it all—and comes out spotless every time. Find your perfect study buddy today!",
        "announcement": "Exciting news: FlexiMat is here! Foldable, washable, and built for busy students and pros. Order now for free shipping!",
        "limited-time offer": "Hurry—FlexiMat’s Back-to-School Sale ends soon! Get yours now and save 15%. Use code DESK15 at checkout.",
        "": "Exciting news: FlexiMat is here! Foldable, washable, and built for busy students and pros. Order now for free shipping!"
    },
    "linkedin": {
        "thought-leadership": "Did you know a tidy desk boosts productivity by 25%? FlexiMat empowers professionals to do their best work—clean, organized, and focused. #WorkplaceWellness",
        "announcement": "Proud to introduce FlexiMat: the ultimate desk mat for professionals and students alike. Let’s redefine workspace standards together. #Innovation",
        "poll": "How often do you clean your workspace? ⬜ Daily ⬜ Weekly ⬜ Only during spring cleaning! Let’s share best practices. #ProductivityPoll",
        "case study": "Case Study: After adopting FlexiMat, ACME Co. employees reported less desk clutter and higher job satisfaction. Discover the results inside. #DeskTransformation",
        "expert q&a": "Q: Why is desk hygiene important for remote teams? A: ‘A clean workspace reduces distractions and boosts morale,’ says Dr. Tan, productivity expert. #AskTheExpert",
        "": "Proud to introduce FlexiMat: the ultimate desk mat for professionals and students alike. Let’s redefine workspace standards together. #Innovation"
    }
}

# Path to JSON templates for awareness/consideration/conversion
TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), 'prompts', 'templates.json'
)
_templates: Dict = None


def load_templates() -> Dict:
    """Load templates.json once and cache in module-level _templates."""
    global _templates
    if _templates is None:
        with open(TEMPLATE_PATH, 'r') as f:
            _templates = json.load(f)
    return _templates

def select_example(channel, style):
    """
    Pick a channel-specific example string based on optional `style`.
    Falls back to channel default when style not provided or unknown.
    """
    channel = channel.lower()
    style = (style or "").lower()
    channel_examples = EXAMPLES.get(channel, {})
    example_text = channel_examples.get(style, channel_examples.get("", ""))
    print(f"Selected example for channel='{channel}', style='{style}': {example_text}")
    return channel_examples.get(style, channel_examples.get("", ""))


def build_prompt_messages(
    stage: str,
    channel: str,
    data: Dict[str, str]
) -> List[Dict[str, str]]:
    """
    Build system+user messages for a given funnel stage and channel.

    data should include:
      product, target_audience, industry,
      marketing_objective, business_background, benefits
    Optional (appended after the template): style, tone, more_instructions
    """
    templates = load_templates()
    section = templates.get(stage, {}).get('default', {})
    system_msg = section.get('system', '')
    user_template = section.get('user', '')
    
    # Select the example based on channel and style
    example_text = select_example(channel, data.get('style', ''))
    
    # Fill the example into the template
    filled = user_template.replace('{{channel}}', channel)
    filled = filled.replace('{{example}}', example_text)
    
    for key, val in data.items():
        # Avoid replacing placeholders for style, tone, more_instructions here (unless you want to put them in the template itself)
        # they are appended as explicit sections to avoid clobbering.
        if key in ['style', 'tone', 'more_instructions']:
            continue
        placeholder = f'{{{{{key}}}}}'
        filled = filled.replace(placeholder, str(val))
        
     # --- Append additional info ---
    if data.get("style"):
        filled += f"\n\n**Style:** {data['style']}"
    if data.get("tone"):
        filled += f"\n\n**Tone:** {data['tone']}"
    if data.get("more_instructions"):
        filled += (
            f"\n\n**Additional Instructions:** {data['more_instructions']}\n"
            "If these instructions conflict with anything above, follow the additional instructions."
        )
    # Return in Chat Completions message format    
    return [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': filled}
    ]
