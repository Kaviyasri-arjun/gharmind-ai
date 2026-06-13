"""Initial schema with pgvector

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-10-25

Creates all GHARMIND AI tables with pgvector extensions.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── PostgreSQL Extensions ─────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # ── households ────────────────────────────────────────────────
    op.create_table(
        "households",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("owner_user_id", sa.String(200), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("pincode", sa.String(10)),
        sa.Column("timezone", sa.String(50), server_default="'Asia/Kolkata'"),
        sa.Column("language_preference", sa.String(20), server_default="'hinglish'"),
        sa.Column("home_type", sa.String(50)),
        sa.Column("floors", sa.SmallInteger(), server_default="1"),
        sa.Column("total_rooms", sa.SmallInteger(), server_default="4"),
        sa.Column("tags", postgresql.ARRAY(sa.String())),
        sa.Column("onboarding_complete", sa.Boolean(), server_default="false"),
        sa.Column("twin_initialized", sa.Boolean(), server_default="false"),
        sa.Column("ai_persona_name", sa.String(100), server_default="'Gharji'"),
        sa.Column("subscription_tier", sa.String(50), server_default="'free'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_households_owner", "households", ["owner_user_id"])
    op.create_index("idx_households_city", "households", ["city", "state"])

    # ── family_members ────────────────────────────────────────────
    op.create_table(
        "family_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("nickname", sa.String(50)),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("age", sa.SmallInteger()),
        sa.Column("gender", sa.String(20)),
        sa.Column("work_schedule", postgresql.JSONB()),
        sa.Column("school_schedule", postgresql.JSONB()),
        sa.Column("typical_wake_time", sa.Time()),
        sa.Column("typical_sleep_time", sa.Time()),
        sa.Column("is_primary_contact", sa.Boolean(), server_default="false"),
        sa.Column("receives_alerts", sa.Boolean(), server_default="true"),
        sa.Column("phone_number", sa.String(20)),
        sa.Column("preferences", postgresql.JSONB()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("simulated_location", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_members_household", "family_members", ["household_id"])

    # ── rooms ─────────────────────────────────────────────────────
    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("room_type", sa.String(50), nullable=False),
        sa.Column("floor", sa.SmallInteger(), server_default="0"),
        sa.Column("area_sqft", sa.Numeric(6, 2)),
        sa.Column("position_x", sa.Numeric(5, 2)),
        sa.Column("position_y", sa.Numeric(5, 2)),
        sa.Column("is_occupied", sa.Boolean(), server_default="false"),
        sa.Column("occupants", postgresql.ARRAY(sa.String())),
        sa.Column("lighting_state", sa.String(20), server_default="'off'"),
        sa.Column("temperature_c", sa.Numeric(4, 1)),
        sa.Column("air_quality", sa.String(20)),
        sa.Column("noise_level", sa.String(20)),
        sa.Column("last_state_change", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_rooms_household", "rooms", ["household_id"])

    # ── appliances ────────────────────────────────────────────────
    op.create_table(
        "appliances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("room_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("rooms.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("appliance_type", sa.String(50), nullable=False),
        sa.Column("brand", sa.String(100)),
        sa.Column("power_state", sa.String(20), server_default="'off'"),
        sa.Column("power_watts", sa.SmallInteger()),
        sa.Column("is_critical", sa.Boolean(), server_default="false"),
        sa.Column("auto_schedule", postgresql.JSONB()),
        sa.Column("health_score", sa.SmallInteger(), server_default="100"),
        sa.Column("avg_daily_runtime_mins", sa.SmallInteger()),
        sa.Column("last_on_at", sa.DateTime(timezone=True)),
        sa.Column("last_off_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_appliances_household", "appliances", ["household_id"])

    # ── twin_state_snapshots (with pgvector) ──────────────────────
    op.create_table(
        "twin_state_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True),
                  server_default=sa.text("NOW()"), nullable=False),
        sa.Column("ist_time", sa.Time(), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("week_number", sa.SmallInteger()),
        sa.Column("month", sa.SmallInteger()),
        sa.Column("season", sa.String(20)),
        sa.Column("festival_context", postgresql.ARRAY(sa.String())),
        sa.Column("is_holiday", sa.Boolean(), server_default="false"),
        sa.Column("is_exam_period", sa.Boolean(), server_default="false"),
        sa.Column("rooms_state", postgresql.JSONB(), nullable=False),
        sa.Column("appliances_state", postgresql.JSONB(), nullable=False),
        sa.Column("members_state", postgresql.JSONB(), nullable=False),
        sa.Column("power_available", sa.Boolean(), server_default="true"),
        sa.Column("water_available", sa.Boolean(), server_default="true"),
        sa.Column("internet_available", sa.Boolean(), server_default="true"),
        sa.Column("context_summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    # pgvector column — added via raw SQL after table creation
    op.execute("ALTER TABLE twin_state_snapshots ADD COLUMN context_embedding vector(1536)")
    op.create_index("idx_snapshots_household_time", "twin_state_snapshots",
                    ["household_id", sa.text("snapshot_at DESC")])
    # IVFFlat index for vector similarity — created after data is loaded
    op.execute("""
        CREATE INDEX idx_snapshots_embedding
        ON twin_state_snapshots
        USING ivfflat (context_embedding vector_cosine_ops)
        WITH (lists = 10)
    """)

    # ── routines ──────────────────────────────────────────────────
    op.create_table(
        "routines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("routine_type", sa.String(50), nullable=False),
        sa.Column("recurrence", sa.String(50), nullable=False),
        sa.Column("schedule_expression", postgresql.JSONB()),
        sa.Column("conditional_trigger", sa.Text()),
        sa.Column("primary_member_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("family_members.id", ondelete="SET NULL")),
        sa.Column("participant_ids", postgresql.ARRAY(sa.String())),
        sa.Column("appliance_ids", postgresql.ARRAY(sa.String())),
        sa.Column("is_ai_detected", sa.Boolean(), server_default="false"),
        sa.Column("confidence_score", sa.Numeric(3, 2)),
        sa.Column("detection_method", sa.String(50)),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("last_executed_at", sa.DateTime(timezone=True)),
        sa.Column("next_expected_at", sa.DateTime(timezone=True)),
        sa.Column("execution_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.execute("ALTER TABLE routines ADD COLUMN pattern_embedding vector(1536)")
    op.create_index("idx_routines_household", "routines", ["household_id"])

    # ── routine_executions ────────────────────────────────────────
    op.create_table(
        "routine_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("routine_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("routines.id", ondelete="CASCADE"), nullable=False),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("duration_mins", sa.SmallInteger()),
        sa.Column("ist_time", sa.Time(), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("season", sa.String(20)),
        sa.Column("festival_context", postgresql.ARRAY(sa.String())),
        sa.Column("was_predicted", sa.Boolean(), server_default="false"),
        sa.Column("prediction_accuracy", sa.Numeric(3, 2)),
        sa.Column("was_on_schedule", sa.Boolean(), server_default="true"),
        sa.Column("deviation_mins", sa.SmallInteger(), server_default="0"),
        sa.Column("deviation_reason", sa.Text()),
        sa.Column("execution_type", sa.String(20), server_default="'real'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_executions_routine", "routine_executions",
                    ["routine_id", sa.text("executed_at DESC")])
    op.create_index("idx_executions_household", "routine_executions",
                    ["household_id", sa.text("executed_at DESC")])

    # ── predictions ───────────────────────────────────────────────
    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("prediction_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("action_suggestion", sa.Text()),
        sa.Column("predicted_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prediction_window_mins", sa.SmallInteger(), server_default="30"),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False),
        sa.Column("priority", sa.String(20), server_default="'normal'"),
        sa.Column("category", sa.String(50)),
        sa.Column("context_snapshot_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("twin_state_snapshots.id", ondelete="SET NULL")),
        sa.Column("reasoning", sa.Text()),
        sa.Column("evidence", postgresql.JSONB()),
        sa.Column("linked_routine_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("routines.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(30), server_default="'pending'"),
        sa.Column("was_accurate", sa.Boolean()),
        sa.Column("actual_occurred_at", sa.DateTime(timezone=True)),
        sa.Column("user_feedback", sa.String(20)),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_predictions_household", "predictions", ["household_id"])

    # ── household_memories (pgvector) ─────────────────────────────
    op.create_table(
        "household_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("structured_data", postgresql.JSONB()),
        sa.Column("observed_at", sa.DateTime(timezone=True)),
        sa.Column("valid_seasons", postgresql.ARRAY(sa.String())),
        sa.Column("valid_months", postgresql.ARRAY(sa.SmallInteger())),
        sa.Column("recurrence", sa.String(50)),
        sa.Column("confidence", sa.Numeric(3, 2), server_default="1.00"),
        sa.Column("importance_score", sa.SmallInteger(), server_default="50"),
        sa.Column("observation_count", sa.Integer(), server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.execute("ALTER TABLE household_memories ADD COLUMN embedding vector(1536)")
    op.create_index("idx_memories_household", "household_memories", ["household_id"])
    op.execute("""
        CREATE INDEX idx_memories_embedding
        ON household_memories
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10)
    """)

    # ── simulation_runs ───────────────────────────────────────────
    op.create_table(
        "simulation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_by_member_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("family_members.id", ondelete="SET NULL")),
        sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("scenario_name", sa.String(200), nullable=False),
        sa.Column("scenario_type", sa.String(50)),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("perturbations", postgresql.JSONB(), nullable=False),
        sa.Column("sim_start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sim_duration_hours", sa.SmallInteger(), server_default="24"),
        sa.Column("sim_resolution_mins", sa.SmallInteger(), server_default="15"),
        sa.Column("status", sa.String(30), server_default="'running'"),
        sa.Column("result_summary", sa.Text()),
        sa.Column("impact_analysis", postgresql.JSONB()),
        sa.Column("risk_flags", postgresql.JSONB()),
        sa.Column("recommendations", postgresql.JSONB()),
        sa.Column("confidence", sa.Numeric(3, 2)),
        sa.Column("timeline", postgresql.JSONB()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_simulations_household", "simulation_runs",
                    ["household_id", sa.text("run_at DESC")])

    # ── festival_calendar ─────────────────────────────────────────
    op.create_table(
        "festival_calendar",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("festival_name", sa.String(200), nullable=False),
        sa.Column("local_names", postgresql.JSONB()),
        sa.Column("festival_type", sa.String(50), nullable=False),
        sa.Column("region", postgresql.ARRAY(sa.String())),
        sa.Column("gregorian_date", sa.Date()),
        sa.Column("lunar_month", sa.String(30)),
        sa.Column("lunar_tithi", sa.String(50)),
        sa.Column("calculation_rule", sa.Text()),
        sa.Column("household_impact", postgresql.JSONB(), nullable=False),
        sa.Column("prep_days_before", sa.SmallInteger(), server_default="1"),
        sa.Column("celebration_days", sa.SmallInteger(), server_default="1"),
        sa.Column("recovery_days", sa.SmallInteger(), server_default="0"),
        sa.Column("is_public_holiday", sa.Boolean(), server_default="false"),
        sa.Column("is_school_holiday", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # ── household_calendar_events ─────────────────────────────────
    op.create_table(
        "household_calendar_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("family_members.id", ondelete="SET NULL")),
        sa.Column("event_name", sa.String(200), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True)),
        sa.Column("is_recurring", sa.Boolean(), server_default="false"),
        sa.Column("recurrence_rule", postgresql.JSONB()),
        sa.Column("impact_tags", postgresql.ARRAY(sa.String())),
        sa.Column("description", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_hh_events_household", "household_calendar_events",
                    ["household_id", "start_at"])

    # ── household_event_log (non-partitioned for simplicity) ──────
    op.create_table(
        "household_event_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_source", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("ist_timestamp", sa.DateTime(timezone=True),
                  server_default=sa.text("NOW()"), nullable=False),
        sa.Column("event_date", sa.Date(), server_default=sa.text("CURRENT_DATE")),
    )
    op.create_index("idx_event_log_household", "household_event_log",
                    ["household_id", sa.text("ist_timestamp DESC")])


def downgrade() -> None:
    """Drop all tables in reverse order."""
    tables = [
        "household_event_log",
        "household_calendar_events",
        "festival_calendar",
        "simulation_runs",
        "household_memories",
        "predictions",
        "routine_executions",
        "routines",
        "twin_state_snapshots",
        "appliances",
        "rooms",
        "family_members",
        "households",
    ]
    for table in tables:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
