"""
AI-powered referral letter generator.
Falls back to template-based generation if OpenAI not configured.
"""
import json
from typing import List
from .client import get_client
import logging

logger = logging.getLogger(__name__)


async def generate_referral_letter_ai(child_data: dict, language: str = "en") -> dict:
    """Generate referral letter using GPT-4o."""
    client = get_client()

    if client is None:
        logger.info("Using template-based referral letter (OpenAI not configured)")
        letter = f"""To the Medical Officer,
{child_data.get('facility_name', 'RBSK Clinic')}

Subject: Developmental Assessment Referral — {child_data['name']}

Dear Medical Officer,

I am writing to refer {child_data['name']}, age {child_data['age']}, for a comprehensive developmental assessment. Observations at {child_data.get('awc_name', 'the Anganwadi Center')} indicate areas requiring specialist evaluation.

The child's Predictive Development Risk Score is {child_data.get('pdrs_score', 'N/A')}/100 ({child_data.get('risk_level', 'AMBER')} risk). Domains flagged: {', '.join(child_data.get('domains_flagged', ['multiple areas']))}.

Assessment under applicable government schemes ({', '.join(child_data.get('schemes', ['RBSK']))}) is recommended.

Respectfully,
{child_data.get('aww_name', 'Anganwadi Worker')}
"""
        whatsapp = (
            f"Dear Parent, {child_data['name']} has been referred for a free developmental assessment "
            f"at {child_data.get('facility_name', 'RBSK Clinic')}. Please contact your AWW for details."
        )
        return {"letter_text": letter, "whatsapp_summary": whatsapp}

    prompt = f"""
Write a professional developmental referral letter for an Indian child.
This is for RBSK (Rashtriya Bal Swasthya Karyakram) or government specialist referral.

Child: {child_data['name']}, Age: {child_data.get('age', 'N/A')}, AWC: {child_data.get('awc_name', 'AWC')}, {child_data.get('district', 'District')}
AWW Name: {child_data.get('aww_name', 'Anganwadi Worker')}
PDRS Score: {child_data.get('pdrs_score', 'N/A')}/100 ({child_data.get('risk_level', 'AMBER')})
Domains of concern: {', '.join(child_data.get('domains_flagged', []))}
Key observations: {', '.join(child_data.get('key_observations', []))}
Applicable schemes: {', '.join(child_data.get('schemes', ['RBSK']))}
Facility: {child_data.get('facility_name', 'District Hospital RBSK Clinic')}

Write a formal but readable letter (3 short paragraphs).
Also write a 1-2 sentence WhatsApp message for the parent in {language}.

Return JSON:
{{
  "letter_text": "...",
  "whatsapp_summary": "..."
}}

Return ONLY the JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )

    result = response.choices[0].message.content.strip()
    if "```" in result:
        result = result.split("```json")[-1].split("```")[0].strip()

    return json.loads(result)
