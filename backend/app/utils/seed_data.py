"""
Seeds the database with:
1. Developmental domains (6 NEP 2020 domains)
2. Milestone library (WHO + ASQ-3 based, 35+ milestones)
3. Government schemes (RBSK, NPPCD, Divyangjan)
4. Referral facilities (demo data)
5. Demo geography (Karnataka — Gulbarga district)
"""
import logging

logger = logging.getLogger(__name__)

DEVELOPMENTAL_DOMAINS = [
    {"code": "PHYSICAL_MOTOR",     "name": "Physical & Motor",         "name_hi": "शारीरिक एवं मोटर",                    "display_order": 1, "color_hex": "#FF6B6B"},
    {"code": "LANGUAGE_LITERACY",  "name": "Language & Literacy",      "name_hi": "भाषा एवं साक्षरता",                     "display_order": 2, "color_hex": "#4ECDC4"},
    {"code": "COGNITIVE",          "name": "Cognitive",                "name_hi": "संज्ञानात्मक",                           "display_order": 3, "color_hex": "#45B7D1"},
    {"code": "SOCIAL_EMOTIONAL",   "name": "Social-Emotional",         "name_hi": "सामाजिक-भावनात्मक",                     "display_order": 4, "color_hex": "#96CEB4"},
    {"code": "AESTHETIC_CULTURAL", "name": "Aesthetic & Cultural",     "name_hi": "सौंदर्यात्मक एवं सांस्कृतिक",            "display_order": 5, "color_hex": "#FFEAA7"},
    {"code": "LEARNING_HABITS",    "name": "Positive Learning Habits", "name_hi": "सीखने की आदतें",                         "display_order": 6, "color_hex": "#DDA0DD"},
]

MILESTONE_LIBRARY = [
    # PHYSICAL_MOTOR — Fine Motor
    {"domain": "PHYSICAL_MOTOR", "text": "Uses pincer grasp (thumb + finger) to pick up small objects",   "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "PHYSICAL_MOTOR", "text": "Copies a circle when shown by adult",                            "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "PHYSICAL_MOTOR", "text": "Holds crayon/pencil with fingers (not fist)",                    "age_min": 42, "age_max": 54, "is_critical": False, "source": "WHO"},
    {"domain": "PHYSICAL_MOTOR", "text": "Cuts paper with scissors (with help)",                           "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    {"domain": "PHYSICAL_MOTOR", "text": "Draws a person with at least 3 body parts",                     "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    # PHYSICAL_MOTOR — Gross Motor
    {"domain": "PHYSICAL_MOTOR", "text": "Runs without falling on flat surface",                           "age_min": 36, "age_max": 42, "is_critical": True,  "source": "WHO"},
    {"domain": "PHYSICAL_MOTOR", "text": "Jumps with both feet together",                                  "age_min": 36, "age_max": 48, "is_critical": False, "source": "WHO"},
    {"domain": "PHYSICAL_MOTOR", "text": "Kicks a ball with coordination",                                 "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "PHYSICAL_MOTOR", "text": "Stands on one foot for 2+ seconds",                              "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    {"domain": "PHYSICAL_MOTOR", "text": "Hops on one foot 3+ times",                                     "age_min": 54, "age_max": 72, "is_critical": False, "source": "ASQ-3"},
    # LANGUAGE_LITERACY
    {"domain": "LANGUAGE_LITERACY", "text": "Uses at least 50 different words in speech",                  "age_min": 24, "age_max": 36, "is_critical": True,  "source": "WHO"},
    {"domain": "LANGUAGE_LITERACY", "text": "Combines 2 or more words in sentences",                      "age_min": 24, "age_max": 36, "is_critical": True,  "source": "WHO"},
    {"domain": "LANGUAGE_LITERACY", "text": "Responds when name is called",                               "age_min": 12, "age_max": 24, "is_critical": True,  "source": "M-CHAT"},
    {"domain": "LANGUAGE_LITERACY", "text": "Follows 2-step instructions",                                "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "LANGUAGE_LITERACY", "text": "Speech understood by strangers most of the time",            "age_min": 36, "age_max": 48, "is_critical": True,  "source": "WHO"},
    {"domain": "LANGUAGE_LITERACY", "text": "Names at least 6 body parts",                                "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "LANGUAGE_LITERACY", "text": "Tells a simple 2-event story",                               "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    {"domain": "LANGUAGE_LITERACY", "text": "Recognizes and names 4+ colors",                             "age_min": 48, "age_max": 60, "is_critical": False, "source": "NCERT"},
    # COGNITIVE
    {"domain": "COGNITIVE", "text": "Sorts objects by color or shape when asked",                          "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "COGNITIVE", "text": "Understands concepts: big/small, same/different",                    "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "COGNITIVE", "text": "Counts 3 or more objects correctly",                                 "age_min": 42, "age_max": 54, "is_critical": False, "source": "NCERT"},
    {"domain": "COGNITIVE", "text": "Completes a 4-piece puzzle independently",                           "age_min": 42, "age_max": 54, "is_critical": False, "source": "ASQ-3"},
    {"domain": "COGNITIVE", "text": "Understands past and future (yesterday, tomorrow)",                  "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    {"domain": "COGNITIVE", "text": "Follows 3-step instructions correctly",                              "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    # SOCIAL_EMOTIONAL
    {"domain": "SOCIAL_EMOTIONAL", "text": "Engages in play with other children (not just parallel play)", "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "SOCIAL_EMOTIONAL", "text": "Shows affection to familiar people",                          "age_min": 24, "age_max": 36, "is_critical": True,  "source": "M-CHAT"},
    {"domain": "SOCIAL_EMOTIONAL", "text": "Separates from parent without extreme distress (at AWC)",     "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "SOCIAL_EMOTIONAL", "text": "Takes turns in games with prompting",                         "age_min": 42, "age_max": 54, "is_critical": False, "source": "ASQ-3"},
    {"domain": "SOCIAL_EMOTIONAL", "text": "Shows empathy (comforts others who are sad)",                 "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    {"domain": "SOCIAL_EMOTIONAL", "text": "Can regulate emotions (calms down within 10 min)",            "age_min": 48, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    # AESTHETIC_CULTURAL
    {"domain": "AESTHETIC_CULTURAL", "text": "Engages in pretend/imaginative play",                       "age_min": 36, "age_max": 48, "is_critical": False, "source": "ASQ-3"},
    {"domain": "AESTHETIC_CULTURAL", "text": "Sings simple songs or rhymes",                              "age_min": 36, "age_max": 48, "is_critical": False, "source": "NCERT"},
    {"domain": "AESTHETIC_CULTURAL", "text": "Shows interest in drawing or painting",                     "age_min": 36, "age_max": 60, "is_critical": False, "source": "NCERT"},
    # LEARNING_HABITS
    {"domain": "LEARNING_HABITS", "text": "Can focus on a single activity for 5+ minutes",                "age_min": 42, "age_max": 60, "is_critical": False, "source": "ASQ-3"},
    {"domain": "LEARNING_HABITS", "text": "Shows curiosity by asking 'why' or 'what' questions",          "age_min": 42, "age_max": 60, "is_critical": False, "source": "NCERT"},
    {"domain": "LEARNING_HABITS", "text": "Completes a started task before moving on",                    "age_min": 54, "age_max": 72, "is_critical": False, "source": "NCERT"},
]

GOVERNMENT_SCHEMES = [
    {
        "name": "Rashtriya Bal Swasthya Karyakram (RBSK)",
        "code": "RBSK",
        "description": "Free health screening and treatment for children 0-18 years. Covers developmental delays, disabilities, diseases, and deficiencies.",
        "description_hi": "0-18 वर्ष के बच्चों के लिए निःशुल्क स्वास्थ्य जांच और उपचार।",
        "eligibility_criteria": "All children 0-18 years in India",
        "department": "Ministry of Health and Family Welfare",
    },
    {
        "name": "National Programme for Prevention and Control of Deafness (NPPCD)",
        "code": "NPPCD",
        "description": "Free hearing assessment and hearing aids for children with hearing impairment.",
        "eligibility_criteria": "Children with diagnosed or suspected hearing impairment",
        "department": "Ministry of Health and Family Welfare",
    },
    {
        "name": "Divyangjan Schemes (RPWD Act 2016)",
        "code": "DIVYANGJAN",
        "description": "Comprehensive disability support including assistive devices, therapy, education support, and financial assistance.",
        "description_hi": "दिव्यांग बच्चों के लिए उपकरण, चिकित्सा, शिक्षा सहायता।",
        "eligibility_criteria": "Children with certified disability (40% or above)",
        "department": "Ministry of Social Justice and Empowerment",
    },
    {
        "name": "PM POSHAN (Mid-Day Meal Scheme)",
        "code": "PM_POSHAN",
        "description": "Free nutritious meals for children in government schools and AWCs to support physical development.",
        "eligibility_criteria": "All children enrolled in government AWCs and schools",
        "department": "Ministry of Education",
    },
    {
        "name": "Integrated Child Development Services (ICDS)",
        "code": "ICDS",
        "description": "Comprehensive early childhood development services including nutrition, immunization, health check-up, and pre-school education.",
        "eligibility_criteria": "Children 0-6 years enrolled in Anganwadi Centers",
        "department": "Ministry of Women and Child Development",
    },
]

REFERRAL_FACILITIES = [
    {
        "name": "Gulbarga District Hospital — RBSK Clinic",
        "facility_type": "DISTRICT_HOSPITAL",
        "address": "Sedam Road, Kalaburagi, Karnataka 585102",
        "phone": "08472-235678",
        "available_days": "Every Tuesday and Friday",
        "available_time": "9:00 AM – 1:00 PM",
        "specialties": ["developmental_assessment", "speech_therapy", "physiotherapy"],
        "district_code": "KA_GULBARGA",
    },
    {
        "name": "Bidar PHC — Child Development Unit",
        "facility_type": "PHC",
        "address": "Udgir Road, Bidar, Karnataka 585401",
        "phone": "08482-226789",
        "available_days": "3rd Tuesday of every month",
        "available_time": "10:00 AM – 2:00 PM",
        "specialties": ["developmental_assessment", "hearing_test"],
        "district_code": "KA_BIDAR",
    },
    {
        "name": "Raichur District RBSK Mobile Team",
        "facility_type": "RBSK",
        "address": "District Hospital Campus, Raichur, Karnataka 584101",
        "phone": "08532-227890",
        "available_days": "Visits AWCs on rotation (contact CDPO for schedule)",
        "available_time": "9:00 AM – 5:00 PM",
        "specialties": ["developmental_assessment", "vision_screening", "hearing_test"],
        "district_code": "KA_RAICHUR",
    },
]

DEMO_GEOGRAPHY = {
    "state": {"name": "Karnataka", "code": "KA"},
    "districts": [
        {"name": "Kalaburagi (Gulbarga)", "code": "KA_GULBARGA"},
        {"name": "Bidar", "code": "KA_BIDAR"},
        {"name": "Raichur", "code": "KA_RAICHUR"},
    ],
    "blocks": [
        {"name": "Sedam Block", "district_code": "KA_GULBARGA"},
        {"name": "Aland Block", "district_code": "KA_GULBARGA"},
        {"name": "Bidar Urban Block", "district_code": "KA_BIDAR"},
    ],
    "awcs": [
        {"center_number": "AWC-KA-GUL-001", "name": "AWC Sedam #1",   "village": "Sedam",    "block": "Sedam Block",       "lat": 17.1865, "lon": 77.2847},
        {"center_number": "AWC-KA-GUL-002", "name": "AWC Sedam #2",   "village": "Sedam",    "block": "Sedam Block",       "lat": 17.1890, "lon": 77.2830},
        {"center_number": "AWC-KA-GUL-047", "name": "AWC Sedam #47",  "village": "Gadwal",   "block": "Sedam Block",       "lat": 17.1950, "lon": 77.2920},
        {"center_number": "AWC-KA-GUL-103", "name": "AWC Aland #3",   "village": "Aland",    "block": "Aland Block",       "lat": 17.5563, "lon": 76.5693},
        {"center_number": "AWC-KA-BID-022", "name": "AWC Bidar #22",  "village": "Bidar",    "block": "Bidar Urban Block",  "lat": 17.9104, "lon": 77.5199},
    ],
}


def seed_all():
    """Run all seeders. Safe to run multiple times (idempotent)."""
    from app.database import SessionLocal
    from app.models.milestone import DevelopmentalDomain, MilestoneLibrary
    from app.models.referral import GovernmentScheme, ReferralFacility
    from app.models.geography import State, District, Block, AnganwadiCenter

    db = SessionLocal()
    try:
        _seed_domains(db)
        _seed_milestones(db)
        _seed_schemes(db)
        _seed_demo_geography(db)
        _seed_referral_facilities(db)
        db.commit()
        print("✅ Seed data loaded successfully")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Seed error (may already exist): {e}")
    finally:
        db.close()


def _seed_domains(db):
    from app.models.milestone import DevelopmentalDomain
    for d in DEVELOPMENTAL_DOMAINS:
        existing = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == d["code"]).first()
        if not existing:
            domain = DevelopmentalDomain(**d)
            db.add(domain)
    db.flush()
    logger.info("Domains seeded")


def _seed_milestones(db):
    from app.models.milestone import DevelopmentalDomain, MilestoneLibrary
    for m in MILESTONE_LIBRARY:
        domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == m["domain"]).first()
        if not domain:
            continue
        existing = db.query(MilestoneLibrary).filter(
            MilestoneLibrary.text == m["text"],
            MilestoneLibrary.domain_id == domain.id,
        ).first()
        if not existing:
            milestone = MilestoneLibrary(
                domain_id=domain.id,
                text=m["text"],
                age_min_months=m["age_min"],
                age_max_months=m["age_max"],
                is_critical=m["is_critical"],
                source=m["source"],
            )
            db.add(milestone)
    db.flush()
    logger.info("Milestones seeded")


def _seed_schemes(db):
    from app.models.referral import GovernmentScheme
    for s in GOVERNMENT_SCHEMES:
        existing = db.query(GovernmentScheme).filter(GovernmentScheme.code == s["code"]).first()
        if not existing:
            scheme = GovernmentScheme(**s)
            db.add(scheme)
    db.flush()
    logger.info("Government schemes seeded")


def _seed_demo_geography(db):
    from app.models.geography import State, District, Block, AnganwadiCenter
    geo = DEMO_GEOGRAPHY

    state = db.query(State).filter(State.code == geo["state"]["code"]).first()
    if not state:
        state = State(name=geo["state"]["name"], code=geo["state"]["code"])
        db.add(state)
        db.flush()

    district_map = {}
    for d in geo["districts"]:
        district = db.query(District).filter(District.name == d["name"]).first()
        if not district:
            district = District(name=d["name"], state_id=state.id)
            db.add(district)
            db.flush()
        district_map[d["code"]] = district

    block_map = {}
    for b in geo["blocks"]:
        district = district_map.get(b["district_code"])
        if not district:
            continue
        block = db.query(Block).filter(Block.name == b["name"], Block.district_id == district.id).first()
        if not block:
            block = Block(name=b["name"], district_id=district.id)
            db.add(block)
            db.flush()
        block_map[b["name"]] = block

    for a in geo["awcs"]:
        block = block_map.get(a["block"])
        if not block:
            continue
        existing = db.query(AnganwadiCenter).filter(AnganwadiCenter.center_number == a["center_number"]).first()
        if not existing:
            awc = AnganwadiCenter(
                center_number=a["center_number"],
                name=a["name"],
                village=a["village"],
                block_id=block.id,
                latitude=a.get("lat"),
                longitude=a.get("lon"),
            )
            db.add(awc)
    db.flush()
    logger.info("Demo geography seeded")


def _seed_referral_facilities(db):
    from app.models.geography import District
    from app.models.referral import ReferralFacility

    for f in REFERRAL_FACILITIES:
        existing = db.query(ReferralFacility).filter(ReferralFacility.name == f["name"]).first()
        if not existing:
            district = db.query(District).filter(District.name.ilike(f"%{f['district_code'].split('_')[-1].title()}%")).first()
            facility = ReferralFacility(
                name=f["name"],
                facility_type=f["facility_type"],
                address=f["address"],
                phone=f["phone"],
                available_days=f["available_days"],
                available_time=f["available_time"],
                specialties=f["specialties"],
                district_id=district.id if district else None,
            )
            db.add(facility)
    db.flush()
    logger.info("Referral facilities seeded")
