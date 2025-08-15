# templates.json NOTES

- Stages: awareness, consideration, conversion
- Each stage has:
  - "system": role/persona instructions
  - "user": template with placeholders:
    {{channel}}, {{product}}, {{target_audience}}, {{industry}},
    {{marketing_objective}}, {{business_background}}, {{benefits}}, {{example}}
- Output contract: model must return a **single-line JSON** object with keys:
  "hook", "body_text", "call_to_action"
  - If a field is not needed for the style, it should be "" (empty string).
