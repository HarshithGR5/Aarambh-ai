"""
Activity recommendation generator.
Falls back to mock response if OpenAI not configured.
"""
import json
from typing import List
from .client import get_client
import logging

logger = logging.getLogger(__name__)

DOMAIN_NAMES = {
    "PHYSICAL_MOTOR": "Physical and Motor Development",
    "LANGUAGE_LITERACY": "Language and Communication",
    "COGNITIVE": "Thinking and Learning",
    "SOCIAL_EMOTIONAL": "Social and Emotional Skills",
    "AESTHETIC_CULTURAL": "Creative and Cultural Activities",
    "LEARNING_HABITS": "Learning Habits and Attention",
}

MOCK_RECOMMENDATIONS = [
    {
        "title": "Clay Shapes Play",
        "description": "Give the child a small ball of clay or mud. Ask them to roll it, flatten it, and make simple shapes like balls and ropes. Sit with them and do it together.",
        "materials": ["clay", "mud", "dough"],
        "duration_minutes": 10,
        "how_it_helps": "Strengthens hand muscles and fine motor coordination needed for writing.",
    },
    {
        "title": "Story Stones",
        "description": "Collect 5 smooth stones. Draw simple pictures on each (sun, tree, animal). Ask the child to pick stones and tell a story using the pictures.",
        "materials": ["stones", "chalk or paint"],
        "duration_minutes": 8,
        "how_it_helps": "Builds language, narrative skills, and creative thinking.",
    },
    {
        "title": "Sorting Seeds",
        "description": "Mix two types of seeds or beans. Ask the child to sort them by type into two bowls. Count together after sorting.",
        "materials": ["two types of seeds/beans", "two small bowls"],
        "duration_minutes": 7,
        "how_it_helps": "Develops fine motor control, categorization skills, and early math concepts.",
    },
]


async def generate_activity_recommendations(
    child_name: str,
    age_months: int,
    domain_code: str,
    concern: str,
    language: str = "hi",
) -> List[dict]:
    """Generate culturally appropriate developmental activities."""
    client = get_client()

    if client is None:
        logger.info("Mock recommendations (OpenAI not configured)")
        return MOCK_RECOMMENDATIONS

    prompt = f"""
You are a child development specialist creating play-based activities for Indian children
aged 3-6, aligned with NEP 2020 ECCE framework and designed for Anganwadi use.

Child: {child_name}, Age: {age_months} months
Domain to support: {DOMAIN_NAMES.get(domain_code, domain_code)}
Specific concern: {concern}
Language for output: {language}

Generate 3 simple, culturally appropriate play activities:
- Use items available in rural Indian homes (clay, stones, leaves, fabric)
- Duration: 5-10 minutes each
- No specialized materials required

Return JSON array:
[
  {{
    "title": "Short activity name",
    "description": "2-3 sentence clear instruction for parent/AWW",
    "materials": ["item1", "item2"],
    "duration_minutes": 5,
    "how_it_helps": "One sentence explaining developmental benefit"
  }}
]

Return ONLY the JSON. No other text.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=900,
    )

    result_text = response.choices[0].message.content.strip()
    if "```" in result_text:
        result_text = result_text.split("```json")[-1].split("```")[0].strip()

    return json.loads(result_text)
