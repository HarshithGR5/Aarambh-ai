"""initial_schema

Revision ID: f701d63ba858
Revises: 
Create Date: 2026-05-31 16:07:33.028603

Full initial schema for Aarambh AI — Developmental Digital Twin Platform.
Tables: states, districts, blocks, anganwadi_centers, users, children,
        attendance, developmental_domains, milestone_library, milestone_assessments,
        observations, observation_markers, pdrs_scores, ddt_snapshots,
        drawings, drawing_analyses, government_schemes, referral_facilities,
        referrals, referral_schemes (assoc), activity_recommendations, parent_interactions
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f701d63ba858'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ENUMS ────────────────────────────────────────────────────────────────
    # CREATE TYPE IF NOT EXISTS is not valid PostgreSQL syntax;
    # use a DO block to catch duplicate_object errors instead.
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('AWW','CDPO','HEALTH_WORKER','STATE_OFFICER','ADMIN');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE gender_type AS ENUM ('MALE','FEMALE','OTHER');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE milestone_result AS ENUM ('YES','SOMETIMES','NOT_YET','NA');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE observation_type AS ENUM ('VOICE','TEXT','GUIDED_PLAY','PARENT_REPORT');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE marker_type AS ENUM ('POSITIVE','CONCERN','FLAG');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE marker_severity AS ENUM ('MILD','MODERATE','SIGNIFICANT');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE risk_level AS ENUM ('GREEN','AMBER','RED');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE referral_status AS ENUM ('GENERATED','SENT_TO_PARENT','APPOINTMENT_SCHEDULED','ASSESSED','FOLLOW_UP_NEEDED','CLOSED');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # ── GEOGRAPHY ────────────────────────────────────────────────────────────
    op.create_table(
        'states',
        sa.Column('id',         sa.Integer(),     primary_key=True),
        sa.Column('name',       sa.String(100),   nullable=False),
        sa.Column('code',       sa.String(5),     nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'districts',
        sa.Column('id',         sa.Integer(),   primary_key=True),
        sa.Column('name',       sa.String(100), nullable=False),
        sa.Column('state_id',   sa.Integer(),   sa.ForeignKey('states.id'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'blocks',
        sa.Column('id',          sa.Integer(),   primary_key=True),
        sa.Column('name',        sa.String(100), nullable=False),
        sa.Column('district_id', sa.Integer(),   sa.ForeignKey('districts.id'), nullable=False),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'anganwadi_centers',
        sa.Column('id',            sa.Integer(),      primary_key=True),
        sa.Column('center_number', sa.String(20),     nullable=False, unique=True),
        sa.Column('name',          sa.String(200),    nullable=False),
        sa.Column('village',       sa.String(100),    nullable=True),
        sa.Column('block_id',      sa.Integer(),      sa.ForeignKey('blocks.id'), nullable=False),
        sa.Column('latitude',      sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude',     sa.Numeric(11, 8), nullable=True),
        sa.Column('is_active',     sa.Boolean(),      server_default=sa.text('true')),
        sa.Column('created_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )

    # ── USERS ────────────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('phone',       sa.String(15),  nullable=False, unique=True),
        sa.Column('name',        sa.String(200), nullable=False),
        sa.Column('role',        sa.Text(),      nullable=False, server_default='AWW'),
        sa.Column('awc_id',      sa.Integer(),   sa.ForeignKey('anganwadi_centers.id'), nullable=True),
        sa.Column('district_id', sa.Integer(),   sa.ForeignKey('districts.id'),         nullable=True),
        sa.Column('language',    sa.String(10),  nullable=False, server_default='hi'),
        sa.Column('otp_hash',    sa.String(255), nullable=True),
        sa.Column('otp_expires', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('is_active',   sa.Boolean(),   server_default=sa.text('true')),
        sa.Column('last_login',  sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_users_phone', 'users', ['phone'])

    # ── CHILDREN ─────────────────────────────────────────────────────────────
    op.create_table(
        'children',
        sa.Column('id',                postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('full_name',         sa.String(200), nullable=False),
        sa.Column('date_of_birth',     sa.Date(),      nullable=False),
        sa.Column('gender',            sa.Text(),      nullable=False),
        sa.Column('awc_id',            sa.Integer(),   sa.ForeignKey('anganwadi_centers.id'), nullable=False),
        sa.Column('parent_name',       sa.String(200), nullable=True),
        sa.Column('parent_phone',      sa.String(15),  nullable=True),
        sa.Column('parent_language',   sa.String(10),  server_default='hi'),
        sa.Column('registration_date', sa.Date(),      server_default=sa.text('current_date')),
        sa.Column('registered_by',     postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('photo_url',         sa.Text(),      nullable=True),
        sa.Column('qr_code',           sa.String(255), nullable=True, unique=True),
        sa.Column('is_active',         sa.Boolean(),   server_default=sa.text('true')),
        sa.Column('school_entry_date', sa.Date(),      nullable=True),
        sa.Column('notes',             sa.Text(),      nullable=True),
        sa.Column('created_at',        sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at',        sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_children_date_of_birth', 'children', ['date_of_birth'])
    op.create_index('ix_children_awc_id',        'children', ['awc_id'])
    op.create_index('ix_children_parent_phone',  'children', ['parent_phone'])

    # ── ATTENDANCE ───────────────────────────────────────────────────────────
    op.create_table(
        'attendance',
        sa.Column('id',         sa.Integer(), primary_key=True),
        sa.Column('child_id',   postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('date',       sa.Date(),    nullable=False),
        sa.Column('present',    sa.Boolean(), nullable=False),
        sa.Column('marked_by',  postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('child_id', 'date', name='uq_attendance_child_date'),
    )

    # ── DEVELOPMENTAL DOMAINS & MILESTONES ───────────────────────────────────
    op.create_table(
        'developmental_domains',
        sa.Column('id',            sa.Integer(),   primary_key=True),
        sa.Column('code',          sa.String(30),  nullable=False, unique=True),
        sa.Column('name',          sa.String(100), nullable=False),
        sa.Column('name_hi',       sa.String(100), nullable=True),
        sa.Column('name_kn',       sa.String(100), nullable=True),
        sa.Column('description',   sa.Text(),      nullable=True),
        sa.Column('display_order', sa.Integer(),   nullable=False),
        sa.Column('color_hex',     sa.String(7),   nullable=True),
    )

    op.create_table(
        'milestone_library',
        sa.Column('id',             sa.Integer(), primary_key=True),
        sa.Column('domain_id',      sa.Integer(), sa.ForeignKey('developmental_domains.id'), nullable=False),
        sa.Column('text',           sa.Text(),    nullable=False),
        sa.Column('text_hi',        sa.Text(),    nullable=True),
        sa.Column('text_kn',        sa.Text(),    nullable=True),
        sa.Column('age_min_months', sa.Integer(), nullable=False),
        sa.Column('age_max_months', sa.Integer(), nullable=False),
        sa.Column('is_critical',    sa.Boolean(), server_default=sa.text('false')),
        sa.Column('source',         sa.String(100), nullable=True),
        sa.Column('display_order',  sa.Integer(), nullable=True),
        sa.Column('is_active',      sa.Boolean(), server_default=sa.text('true')),
    )
    op.create_index('ix_milestone_library_domain_id',      'milestone_library', ['domain_id'])
    op.create_index('ix_milestone_library_age_min_months', 'milestone_library', ['age_min_months'])
    op.create_index('ix_milestone_library_age_max_months', 'milestone_library', ['age_max_months'])

    op.create_table(
        'milestone_assessments',
        sa.Column('id',              sa.Integer(), primary_key=True),
        sa.Column('child_id',        postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('milestone_id',    sa.Integer(), sa.ForeignKey('milestone_library.id'), nullable=False),
        sa.Column('result',          sa.Text(),    nullable=False),
        sa.Column('assessed_by',     postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assessment_date', sa.Date(),    server_default=sa.text('current_date')),
        sa.Column('notes',           sa.Text(),    nullable=True),
        sa.Column('created_at',      sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('child_id', 'milestone_id', 'assessment_date', name='uq_assessment_child_milestone_date'),
    )
    op.create_index('ix_milestone_assessments_child_id', 'milestone_assessments', ['child_id'])

    # ── OBSERVATIONS ─────────────────────────────────────────────────────────
    op.create_table(
        'observations',
        sa.Column('id',                postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('child_id',          postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('observed_by',       postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'),    nullable=False),
        sa.Column('observation_type',  sa.Text(), nullable=False, server_default='VOICE'),
        sa.Column('raw_text',          sa.Text(), nullable=True),
        sa.Column('audio_url',         sa.Text(), nullable=True),
        sa.Column('transcript',        sa.Text(), nullable=True),
        sa.Column('transcript_lang',   sa.String(10), nullable=True),
        sa.Column('english_text',      sa.Text(), nullable=True),
        sa.Column('processing_status', sa.String(20), server_default='PENDING'),
        sa.Column('created_at',        sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_observations_child_id',   'observations', ['child_id'])
    op.create_index('ix_observations_created_at', 'observations', ['created_at'])

    op.create_table(
        'observation_markers',
        sa.Column('id',             sa.Integer(), primary_key=True),
        sa.Column('observation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('observations.id'), nullable=False),
        sa.Column('domain_id',      sa.Integer(), sa.ForeignKey('developmental_domains.id'), nullable=False),
        sa.Column('marker_type',    sa.Text(),    nullable=False),
        sa.Column('severity',       sa.Text(),    nullable=True),
        sa.Column('description',    sa.Text(),    nullable=False),
        sa.Column('description_hi', sa.Text(),    nullable=True),
        sa.Column('ai_extracted',   sa.Boolean(), server_default=sa.text('true')),
        sa.Column('confidence',     sa.Numeric(3, 2), nullable=True),
        sa.Column('created_at',     sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_observation_markers_observation_id', 'observation_markers', ['observation_id'])

    # ── PDRS & DDT ────────────────────────────────────────────────────────────
    op.create_table(
        'pdrs_scores',
        sa.Column('id',             sa.Integer(), primary_key=True),
        sa.Column('child_id',       postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('overall_score',  sa.Integer(), nullable=False),
        sa.Column('risk_level',     sa.Text(),    nullable=False),
        sa.Column('domain_scores',  postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('input_snapshot', postgresql.JSONB(), nullable=True),
        sa.Column('computed_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('computed_by',    sa.String(20), server_default='AUTO'),
    )
    op.create_index('ix_pdrs_scores_child_id',    'pdrs_scores', ['child_id'])
    op.create_index('ix_pdrs_scores_computed_at', 'pdrs_scores', ['computed_at'])

    op.create_table(
        'ddt_snapshots',
        sa.Column('id',                    sa.Integer(), primary_key=True),
        sa.Column('child_id',              postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('pdrs_score_id',         sa.Integer(), sa.ForeignKey('pdrs_scores.id'), nullable=True),
        sa.Column('portrait_text',         sa.Text(),    nullable=False),
        sa.Column('portrait_text_hi',      sa.Text(),    nullable=True),
        sa.Column('school_readiness_flag', sa.String(20), nullable=True),
        sa.Column('school_readiness_note', sa.Text(),    nullable=True),
        sa.Column('asd_flag',              sa.Boolean(), server_default=sa.text('false')),
        sa.Column('speech_delay_flag',     sa.Boolean(), server_default=sa.text('false')),
        sa.Column('motor_delay_flag',      sa.Boolean(), server_default=sa.text('false')),
        sa.Column('snapshot_data',         postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at',            sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_ddt_snapshots_child_id', 'ddt_snapshots', ['child_id'])

    # ── DRAWINGS ──────────────────────────────────────────────────────────────
    op.create_table(
        'drawings',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('child_id',    postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'), nullable=False),
        sa.Column('image_url',   sa.Text(),    nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('upload_date', sa.Date(),    server_default=sa.text('current_date')),
        sa.Column('context',     sa.String(100), nullable=True),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_drawings_child_id', 'drawings', ['child_id'])

    op.create_table(
        'drawing_analyses',
        sa.Column('id',                sa.Integer(), primary_key=True),
        sa.Column('drawing_id',        postgresql.UUID(as_uuid=True), sa.ForeignKey('drawings.id'), nullable=False, unique=True),
        sa.Column('fine_motor_score',  sa.Integer(), nullable=True),
        sa.Column('cognitive_score',   sa.Integer(), nullable=True),
        sa.Column('emotional_tone',    sa.String(50), nullable=True),
        sa.Column('spatial_org_score', sa.Integer(), nullable=True),
        sa.Column('figure_complexity', sa.Integer(), nullable=True),
        sa.Column('ai_summary',        sa.Text(),    nullable=False),
        sa.Column('ai_summary_hi',     sa.Text(),    nullable=True),
        sa.Column('domain_flags',      postgresql.JSONB(), server_default='{}'),
        sa.Column('analyzed_at',       sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('model_used',        sa.String(50), nullable=True),
    )

    # ── REFERRALS ─────────────────────────────────────────────────────────────
    op.create_table(
        'government_schemes',
        sa.Column('id',                   sa.Integer(),   primary_key=True),
        sa.Column('name',                 sa.String(200), nullable=False),
        sa.Column('code',                 sa.String(50),  nullable=False, unique=True),
        sa.Column('description',          sa.Text(),      nullable=False),
        sa.Column('description_hi',       sa.Text(),      nullable=True),
        sa.Column('eligibility_criteria', sa.Text(),      nullable=True),
        sa.Column('apply_url',            sa.Text(),      nullable=True),
        sa.Column('department',           sa.String(200), nullable=True),
        sa.Column('is_active',            sa.Boolean(),   server_default=sa.text('true')),
    )

    op.create_table(
        'referral_facilities',
        sa.Column('id',             sa.Integer(),   primary_key=True),
        sa.Column('name',           sa.String(200), nullable=False),
        sa.Column('facility_type',  sa.String(50),  nullable=True),
        sa.Column('address',        sa.Text(),      nullable=True),
        sa.Column('district_id',    sa.Integer(),   sa.ForeignKey('districts.id'), nullable=True),
        sa.Column('phone',          sa.String(20),  nullable=True),
        sa.Column('available_days', sa.Text(),      nullable=True),
        sa.Column('available_time', sa.String(50),  nullable=True),
        sa.Column('specialties',    postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('is_active',      sa.Boolean(),   server_default=sa.text('true')),
    )

    op.create_table(
        'referrals',
        sa.Column('id',               postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('child_id',         postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'),          nullable=False),
        sa.Column('generated_by',     postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'),             nullable=False),
        sa.Column('facility_id',      sa.Integer(),   sa.ForeignKey('referral_facilities.id'),              nullable=True),
        sa.Column('referral_date',    sa.Date(),      server_default=sa.text('current_date')),
        sa.Column('status',           sa.Text(),      nullable=False, server_default='GENERATED'),
        sa.Column('letter_text',      sa.Text(),      nullable=False),
        sa.Column('letter_text_kn',   sa.Text(),      nullable=True),
        sa.Column('letter_text_hi',   sa.Text(),      nullable=True),
        sa.Column('letter_pdf_url',   sa.Text(),      nullable=True),
        sa.Column('pdrs_at_referral', sa.Integer(),   nullable=True),
        sa.Column('domains_flagged',  postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('parent_notified_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('appointment_date', sa.Date(),      nullable=True),
        sa.Column('specialist_notes', sa.Text(),      nullable=True),
        sa.Column('resolved_at',      sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at',       sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at',       sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_referrals_child_id', 'referrals', ['child_id'])

    # Association table: referrals ↔ government_schemes (many-to-many)
    op.create_table(
        'referral_schemes',
        sa.Column('referral_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('referrals.id'),          primary_key=True),
        sa.Column('scheme_id',   sa.Integer(),                   sa.ForeignKey('government_schemes.id'), primary_key=True),
    )

    # ── RECOMMENDATIONS ───────────────────────────────────────────────────────
    op.create_table(
        'activity_recommendations',
        sa.Column('id',                   postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('child_id',             postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'),              nullable=False),
        sa.Column('domain_id',            sa.Integer(),   sa.ForeignKey('developmental_domains.id'), nullable=False),
        sa.Column('activity_title',       sa.Text(),      nullable=False),
        sa.Column('activity_title_hi',    sa.Text(),      nullable=True),
        sa.Column('activity_title_kn',    sa.Text(),      nullable=True),
        sa.Column('activity_description', sa.Text(),      nullable=False),
        sa.Column('activity_desc_hi',     sa.Text(),      nullable=True),
        sa.Column('activity_desc_kn',     sa.Text(),      nullable=True),
        sa.Column('age_min_months',       sa.Integer(),   nullable=True),
        sa.Column('age_max_months',       sa.Integer(),   nullable=True),
        sa.Column('duration_minutes',     sa.Integer(),   server_default='5'),
        sa.Column('generated_at',         sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('parent_sent',          sa.Boolean(),   server_default=sa.text('false')),
        sa.Column('parent_sent_at',       sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('ix_activity_recommendations_child_id', 'activity_recommendations', ['child_id'])

    op.create_table(
        'parent_interactions',
        sa.Column('id',                sa.Integer(), primary_key=True),
        sa.Column('child_id',          postgresql.UUID(as_uuid=True), sa.ForeignKey('children.id'),                nullable=False),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('activity_recommendations.id'), nullable=True),
        sa.Column('platform',          sa.String(20), nullable=False, server_default='WHATSAPP'),
        sa.Column('message_sent',      sa.Text(),     nullable=True),
        sa.Column('parent_response',   sa.Text(),     nullable=True),
        sa.Column('response_type',     sa.String(20), nullable=True),
        sa.Column('interaction_date',  sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_parent_interactions_child_id', 'parent_interactions', ['child_id'])


def downgrade() -> None:
    op.drop_table('parent_interactions')
    op.drop_table('activity_recommendations')
    op.drop_table('referral_schemes')
    op.drop_table('referrals')
    op.drop_table('referral_facilities')
    op.drop_table('government_schemes')
    op.drop_table('drawing_analyses')
    op.drop_table('drawings')
    op.drop_table('ddt_snapshots')
    op.drop_table('pdrs_scores')
    op.drop_table('observation_markers')
    op.drop_table('observations')
    op.drop_table('milestone_assessments')
    op.drop_table('milestone_library')
    op.drop_table('developmental_domains')
    op.drop_table('attendance')
    op.drop_table('children')
    op.drop_table('users')
    op.drop_table('anganwadi_centers')
    op.drop_table('blocks')
    op.drop_table('districts')
    op.drop_table('states')

    # DROP TYPE IF EXISTS is valid PostgreSQL — no DO block needed here
    op.execute("DROP TYPE IF EXISTS referral_status")
    op.execute("DROP TYPE IF EXISTS risk_level")
    op.execute("DROP TYPE IF EXISTS marker_severity")
    op.execute("DROP TYPE IF EXISTS marker_type")
    op.execute("DROP TYPE IF EXISTS observation_type")
    op.execute("DROP TYPE IF EXISTS milestone_result")
    op.execute("DROP TYPE IF EXISTS gender_type")
    op.execute("DROP TYPE IF EXISTS user_role")