"""
Database module for Mind-Log Experimentation Lab.
Implements event schema from PRD v1.1 using SQLite.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "experiment.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory for dict-like access."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database with event schema from PRD."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            input_text TEXT,
            sentiment_score REAL,
            severity_bucket TEXT CHECK(severity_bucket IN ('mild', 'moderate', 'severe')),
            assigned_variant TEXT CHECK(assigned_variant IN ('A_CLINICAL', 'B_EMPATHETIC')),
            response_time_ms INTEGER,
            time_to_decision_ms INTEGER,
            session_depth INTEGER DEFAULT 1,
            converted INTEGER CHECK(converted IN (0, 1)),
            experiment_excluded TEXT,
            referral_source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_variant ON interactions(assigned_variant)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_converted ON interactions(converted)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_severity ON interactions(severity_bucket)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions(timestamp)")

    conn.commit()
    conn.close()


def log_event(
    session_id: str,
    input_text: Optional[str] = None,
    sentiment_score: Optional[float] = None,
    severity_bucket: Optional[str] = None,
    assigned_variant: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    time_to_decision_ms: Optional[int] = None,
    session_depth: int = 1,
    converted: Optional[int] = None,
    experiment_excluded: Optional[str] = None,
    referral_source: Optional[str] = None
) -> int:
    """
    Log an interaction event to the database.

    Args:
        session_id: Unique identifier for the user session (UUID)
        input_text: Raw user input (anonymized in production)
        sentiment_score: -1.0 (negative) to 1.0 (positive)
        severity_bucket: 'mild', 'moderate', or 'severe'
        assigned_variant: 'A_CLINICAL' or 'B_EMPATHETIC'
        response_time_ms: System latency in milliseconds
        time_to_decision_ms: Time from response shown to user action
        session_depth: Number of messages in session
        converted: 1 if clicked CTA, 0 if not
        experiment_excluded: Reason if excluded (e.g., 'crisis_protocol')
        referral_source: UTM parameter for marketing attribution

    Returns:
        The row ID of the inserted record
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interactions (
            session_id, timestamp, input_text, sentiment_score, severity_bucket,
            assigned_variant, response_time_ms, time_to_decision_ms, session_depth,
            converted, experiment_excluded, referral_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        datetime.utcnow().isoformat(),
        input_text,
        sentiment_score,
        severity_bucket,
        assigned_variant,
        response_time_ms,
        time_to_decision_ms,
        session_depth,
        converted,
        experiment_excluded,
        referral_source
    ))

    row_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return row_id


def update_conversion(session_id: str, converted: int, time_to_decision_ms: int) -> None:
    """Update conversion status for a session."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interactions
        SET converted = ?, time_to_decision_ms = ?
        WHERE session_id = ?
    """, (converted, time_to_decision_ms, session_id))

    conn.commit()
    conn.close()


def get_all_interactions() -> list[dict]:
    """Retrieve all interactions for analysis."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interactions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_experiment_stats() -> dict:
    """Get summary statistics for A/B test results."""
    conn = get_connection()
    cursor = conn.cursor()

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total_sessions,
            SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as total_conversions,
            AVG(CASE WHEN converted IS NOT NULL THEN converted ELSE 0 END) as overall_conversion_rate
        FROM interactions
        WHERE experiment_excluded IS NULL
    """)
    overall = dict(cursor.fetchone())

    # Per-variant stats
    cursor.execute("""
        SELECT
            assigned_variant,
            COUNT(*) as sessions,
            SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as conversions,
            AVG(CASE WHEN converted IS NOT NULL THEN converted ELSE 0 END) as conversion_rate,
            AVG(sentiment_score) as avg_sentiment,
            AVG(time_to_decision_ms) as avg_decision_time
        FROM interactions
        WHERE experiment_excluded IS NULL AND assigned_variant IS NOT NULL
        GROUP BY assigned_variant
    """)
    variants = {row['assigned_variant']: dict(row) for row in cursor.fetchall()}

    # Severity breakdown
    cursor.execute("""
        SELECT
            severity_bucket,
            assigned_variant,
            COUNT(*) as sessions,
            SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as conversions,
            AVG(CASE WHEN converted IS NOT NULL THEN converted ELSE 0 END) as conversion_rate
        FROM interactions
        WHERE experiment_excluded IS NULL AND severity_bucket IS NOT NULL
        GROUP BY severity_bucket, assigned_variant
    """)
    severity = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'overall': overall,
        'variants': variants,
        'by_severity': severity
    }


def generate_session_id() -> str:
    """Generate a new unique session ID."""
    return str(uuid.uuid4())


def get_record_count() -> int:
    """Get count of records in database (for checking if data exists)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM interactions")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# Initialize database on module import
init_db()
