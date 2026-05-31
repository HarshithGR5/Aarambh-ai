from datetime import date
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.child import Child
from ..models.referral import Referral, ReferralFacility, GovernmentScheme, ReferralStatus
from ..models.pdrs import PDRSScore, RiskLevel
from ..services.pdrs_service import get_latest_pdrs, get_age_months
import logging

logger = logging.getLogger(__name__)


def get_applicable_schemes(domain_scores: dict, db: Session) -> List[GovernmentScheme]:
    """Determine which government schemes apply based on PDRS domain scores."""
    schemes = db.query(GovernmentScheme).filter(GovernmentScheme.is_active == True).all()
    applicable = []

    for scheme in schemes:
        if scheme.code == "RBSK":
            applicable.append(scheme)
        elif scheme.code == "NPPCD" and domain_scores.get("LANGUAGE_LITERACY", 0) >= 60:
            applicable.append(scheme)
        elif scheme.code == "DIVYANGJAN":
            high_risk = sum(1 for s in domain_scores.values() if s >= 70)
            if high_risk >= 2:
                applicable.append(scheme)

    return applicable


def get_nearest_facility(district_id: Optional[int], db: Session) -> Optional[ReferralFacility]:
    """Get the nearest referral facility for the given district."""
    if district_id:
        facility = (
            db.query(ReferralFacility)
            .filter(ReferralFacility.district_id == district_id, ReferralFacility.is_active == True)
            .first()
        )
        if facility:
            return facility
    return db.query(ReferralFacility).filter(ReferralFacility.is_active == True).first()


def generate_referral_letter(child_name: str, age_months: int, awc_name: str, facility_name: str,
                              pdrs_score: int, risk_level: str, domain_scores: dict,
                              scheme_names: List[str]) -> str:
    age_str = f"{age_months // 12} years {age_months % 12} months"
    flagged_domains = [d.replace("_", " ").title() for d, s in domain_scores.items() if s >= 60]
    domains_text = ", ".join(flagged_domains) if flagged_domains else "multiple developmental areas"
    schemes_text = ", ".join(scheme_names) if scheme_names else "RBSK"

    letter = f"""To the Medical Officer,
{facility_name}

Subject: Developmental Assessment Referral — {child_name}

Dear Medical Officer,

I am writing to refer {child_name}, age {age_str}, enrolled at {awc_name}, for a comprehensive developmental assessment. This referral is generated through the Aarambh AI Developmental Digital Twin platform following systematic observation and milestone assessment.

Our field observations indicate areas of developmental concern in {domains_text}. The child's Predictive Development Risk Score (PDRS) is {pdrs_score}/100, classified as {risk_level} risk. The child has been observed regularly at the Anganwadi Center, and this referral is made in accordance with the national ECCE developmental framework under NEP 2020.

We request a specialist assessment and recommend exploring the following applicable government schemes: {schemes_text}. These schemes provide free assessment and therapeutic services that could significantly support this child's developmental trajectory.

Please contact the Anganwadi Worker for the child's complete developmental record and observation history. We appreciate your support in ensuring this child receives timely intervention.

Respectfully,
Anganwadi Worker
{awc_name}
Aarambh AI Platform
"""
    return letter


def create_referral(child_id: UUID, generated_by: UUID, db: Session) -> dict:
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child {child_id} not found")

    latest_pdrs = get_latest_pdrs(child_id, db)
    pdrs_score = latest_pdrs.overall_score if latest_pdrs else 50
    risk_level = latest_pdrs.risk_level.value if latest_pdrs else "AMBER"
    domain_scores = latest_pdrs.domain_scores if latest_pdrs else {}

    district_id = child.awc.block.district.id if child.awc and child.awc.block else None
    facility = get_nearest_facility(district_id, db)
    applicable_schemes = get_applicable_schemes(domain_scores, db)
    scheme_names = [s.name for s in applicable_schemes]
    scheme_codes = [s.code for s in applicable_schemes]

    awc_name = child.awc.name if child.awc else "Anganwadi Center"
    facility_name = facility.name if facility else "District Hospital RBSK Clinic"
    age_months = get_age_months(child.date_of_birth)

    letter_text = generate_referral_letter(
        child.full_name, age_months, awc_name, facility_name,
        pdrs_score, risk_level, domain_scores, scheme_names,
    )

    flagged_domains = [d for d, s in domain_scores.items() if s >= 60]

    whatsapp_message = (
        f"Dear Parent/Guardian, {child.full_name} has been referred for a developmental assessment at "
        f"{facility_name}. This assessment is FREE under government schemes ({', '.join(scheme_codes)}). "
        f"Please contact your Anganwadi Worker for the appointment details and referral letter."
    )

    referral = Referral(
        child_id=child_id,
        generated_by=generated_by,
        facility_id=facility.id if facility else None,
        letter_text=letter_text,
        pdrs_at_referral=pdrs_score,
        domains_flagged=flagged_domains,
    )
    referral.schemes = applicable_schemes
    db.add(referral)
    db.commit()
    db.refresh(referral)

    return {
        "referral": referral,
        "facility": facility,
        "scheme_codes": scheme_codes,
        "letter_text": letter_text,
        "whatsapp_message": whatsapp_message,
    }
