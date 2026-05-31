"""
GPT-4o NLP extraction: text → structured developmental markers.
Falls back to mock response if OpenAI not configured.
"""
import json
from typing import List
from .client import get_client
import logging

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """
You are a developmental screening assistant for Aarambh AI, India's child development platform.
You analyze field observations from Anganwadi workers about children aged 3-6 years.

Extract developmental markers from the observation text and return ONLY a valid JSON array.
Each marker must have: domain, type, severity, description, confidence.

Domains (use exact codes):
- PHYSICAL_MOTOR: gross/fine motor, movement, coordination
- LANGUAGE_LITERACY: speech, language, vocabulary, communication
- COGNITIVE: thinking, learning, memory, problem-solving
- SOCIAL_EMOTIONAL: social interaction, emotions, behavior, peer relations
- AESTHETIC_CULTURAL: creativity, play, cultural activities
- LEARNING_HABITS: attention, engagement, curiosity, persistence

Types: POSITIVE (developmental strength), CONCERN (needs monitoring), FLAG (needs referral)
Severity: MILD, MODERATE, SIGNIFICANT (only for CONCERN and FLAG types)
Confidence: 0.0 to 1.0

Be conservative — only mark FLAG for clear developmental red flags.
Return ONLY the JSON array. No other text.
"""

MOCK_MARKERS = [
    {
        "domain": "SOCIAL_EMOTIONAL",
        "type": "CONCERN",
        "severity": "MODERATE",
        "description": "Child shows limited peer interaction during group activities",
        "confidence": 0.75,
    },
    {
        "domain": "LANGUAGE_LITERACY",
        "type": "POSITIVE",
        "severity": None,
        "description": "Child responds appropriately to instructions and uses sentences",
        "confidence": 0.85,
    },
]


async def extract_observation_markers(english_text: str, child_age_months: int) -> List[dict]:
    """Extract structured developmental markers from observation text."""
    client = get_client()

    if client is None:
        logger.info("Mock marker extraction (OpenAI not configured)")
        return MOCK_MARKERS

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Child age: {child_age_months} months\n\nObservation: {english_text}"},
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
    result_text = result_text.strip("` \n")

    return json.loads(result_text)


async def translate_to_english(text: str, source_language: str) -> str:
    """Translate regional language text to English."""
    client = get_client()

    if client is None:
        return text

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Translate the following text to English. Return ONLY the translation.",
            },
            {"role": "user", "content": f"Language: {source_language}\nText: {text}"},
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
