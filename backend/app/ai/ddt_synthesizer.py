"""
DDT (Developmental Digital Twin) portrait synthesizer.
Falls back to rule-based portrait if OpenAI not configured.
"""
import json
from .client import get_client
import logging

logger = logging.getLogger(__name__)

DDT_PROMPT = """
You are a developmental specialist writing a Developmental Digital Twin portrait
for an Anganwadi child in India. Write with warmth, clinical accuracy, and cultural sensitivity.

Child Information:
- Name: {name}
- Age: {age_years} years {age_months_rem} months
- Gender: {gender}
- AWC: {awc_name}, {district}, {state}

Developmental Data (PDRS Scores — higher = more concern):
{domain_scores}

Recent Observations Summary:
{observations_summary}

Milestone Status (missed critical milestones):
{missed_milestones}

Write a 3-4 paragraph Developmental Digital Twin portrait that:
1. Opens with the child's name and what they can do well (strengths first)
2. Describes developmental progress across the 6 domains with specific observations
3. Identifies areas for support with professional, non-alarmist language
4. Closes with school readiness assessment and recommended next steps

Also provide:
- school_readiness_flag: "ON_TRACK" | "DEVELOPING" | "NEEDS_SUPPORT"
- school_readiness_note: One sentence about school readiness
- recommended_actions: List of 2-3 specific recommended actions for AWW

Return as JSON:
{{
  "portrait_text": "...",
  "school_readiness_flag": "...",
  "school_readiness_note": "...",
  "recommended_actions": ["...", "..."]
}}

Return ONLY the JSON.
"""


async def synthesize_ddt(
    child_data: dict,
    domain_scores: dict,
    observations: list,
    missed_milestones: list,
    drawing_summary: str = None,
) -> dict:
    """Generate the full Developmental Digital Twin portrait."""
    client = get_client()

    if client is None:
        logger.info("Using rule-based DDT portrait (OpenAI not configured)")
        from ..services.ddt_service import build_mock_portrait, get_school_readiness
        portrait = build_mock_portrait(
            child_data["name"], child_data["age_months"], domain_scores, missed_milestones
        )
        school_flag, school_note = get_school_readiness(
            sum(domain_scores.values()) // len(domain_scores) if domain_scores else 50
        )
        return {
            "portrait_text": portrait,
            "school_readiness_flag": school_flag,
            "school_readiness_note": school_note,
            "recommended_actions": [
                "Continue regular developmental observations",
                "Engage parents with home-based activity recommendations",
                "Review milestone assessments monthly",
            ],
        }

    obs_text = "\n".join(
        [f"- [{obs['domain']}] {obs['description']}" for obs in observations[-10:]]
    ) or "No recent observations recorded."

    missed_text = "\n".join(
        [f"- [{m['domain']}] Age {m['age_min']}-{m['age_max']}m: {m['text']}" for m in missed_milestones]
    ) or "No missed critical milestones."

    domain_text = "\n".join([f"- {domain}: {score}/100 (concern level)" for domain, score in domain_scores.items()])

    prompt = DDT_PROMPT.format(
        name=child_data["name"],
        age_years=child_data["age_months"] // 12,
        age_months_rem=child_data["age_months"] % 12,
        gender=child_data["gender"],
        awc_name=child_data.get("awc_name", "Anganwadi Center"),
        district=child_data.get("district", "District"),
        state=child_data.get("state", "State"),
        domain_scores=domain_text,
        observations_summary=obs_text,
        missed_milestones=missed_text,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1200,
    )

    result = response.choices[0].message.content.strip()
    if "```" in result:
        result = result.split("```json")[-1].split("```")[0].strip()

    return json.loads(result)
