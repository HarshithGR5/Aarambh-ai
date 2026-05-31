"""
GPT-4o Vision drawing analysis (Crayon Intelligence™).
Falls back to mock response if OpenAI not configured.
"""
import base64
import json
from .client import get_client
import logging

logger = logging.getLogger(__name__)

DRAWING_ANALYSIS_PROMPT = """
You are a developmental psychology expert analyzing a child's drawing using the
Goodenough-Harris Draw-A-Person framework, adapted for Indian Anganwadi field use.

The child is aged {age_months} months ({age_years} years {age_rem} months).

Analyze this drawing and return ONLY valid JSON with these exact fields:
{{
  "fine_motor_score": 0-100,
  "cognitive_score": 0-100,
  "spatial_org_score": 0-100,
  "figure_complexity": 0-100,
  "emotional_tone": "POSITIVE" | "NEUTRAL" | "CONCERNING",
  "ai_summary": "2-3 sentence professional developmental assessment in English",
  "domain_flags": {{
    "PHYSICAL_MOTOR": "ON_TRACK" | "DEVELOPING" | "NEEDS_ATTENTION",
    "COGNITIVE": "ON_TRACK" | "DEVELOPING" | "NEEDS_ATTENTION"
  }},
  "goodenough_harris_points": 0-100
}}

Age-calibrated expectations:
- Age 36-48 months: Basic circle, some facial features
- Age 48-60 months: Clear head, 2-4 body parts, arms emerging
- Age 60-72 months: Full figure, 6+ body parts, arms+legs, clothing details

Return ONLY the JSON. No other text.
"""

MOCK_ANALYSIS = {
    "fine_motor_score": 65,
    "cognitive_score": 70,
    "spatial_org_score": 62,
    "figure_complexity": 58,
    "emotional_tone": "NEUTRAL",
    "ai_summary": (
        "The drawing shows a basic human figure with identifiable head and facial features. "
        "Fine motor control is developing appropriately for the child's age range. "
        "Spatial organization and figure complexity are within expected developmental norms."
    ),
    "domain_flags": {
        "PHYSICAL_MOTOR": "DEVELOPING",
        "COGNITIVE": "ON_TRACK",
    },
    "goodenough_harris_points": 62,
}


async def analyze_drawing(image_bytes: bytes, age_months: int, context: str = "free_drawing") -> dict:
    """Analyze a child's drawing using GPT-4o Vision."""
    client = get_client()

    if client is None:
        logger.info("Mock drawing analysis (OpenAI not configured)")
        return MOCK_ANALYSIS

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    age_years = age_months // 12
    age_rem = age_months % 12

    prompt = DRAWING_ANALYSIS_PROMPT.format(
        age_months=age_months,
        age_years=age_years,
        age_rem=age_rem,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        max_tokens=800,
        temperature=0.2,
    )

    result_text = response.choices[0].message.content.strip()
    if "```" in result_text:
        result_text = result_text.split("```json")[-1].split("```")[0].strip()

    return json.loads(result_text)
