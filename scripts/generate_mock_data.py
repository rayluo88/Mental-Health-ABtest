"""
Mock Data Generator for Mind-Log Experimentation Lab.

Generates realistic synthetic data to demonstrate analytics dashboard.
Implements intentional bias to show statistically significant A/B test results.

Key design decisions:
- Variant B (Empathetic) has higher conversion, especially for severe cases
- Sentiment follows realistic distribution (slightly negative skew for mental health)
- Time to decision varies by severity (more severe = longer decision time)
- UTM sources simulate realistic marketing channels
"""

import random
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "experiment.db"

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# =============================================================================
# CONFIGURATION
# =============================================================================

NUM_RECORDS = 500
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 1, 16)

# Variant distribution (50/50 split)
VARIANTS = ["A_CLINICAL", "B_EMPATHETIC"]

# Severity distribution (weighted towards moderate - realistic for mental health platform)
SEVERITY_WEIGHTS = {
    "mild": 0.30,
    "moderate": 0.45,
    "severe": 0.25,
}

# Base conversion rates by variant and severity
# Key insight: Empathetic performs better, especially for severe cases
CONVERSION_RATES = {
    "A_CLINICAL": {
        "mild": 0.12,
        "moderate": 0.18,
        "severe": 0.22,
    },
    "B_EMPATHETIC": {
        "mild": 0.15,
        "moderate": 0.25,
        "severe": 0.35,  # Big lift for severe cases
    },
}

# UTM sources with weights
UTM_SOURCES = [
    ("google_search", 0.30),
    ("facebook_ads", 0.20),
    ("instagram_ads", 0.15),
    ("direct", 0.15),
    ("referral", 0.10),
    ("email_campaign", 0.05),
    ("tiktok_ads", 0.05),
]

# Sample input texts by severity (for realistic logging)
SAMPLE_INPUTS = {
    "mild": [
        "I've been feeling a bit off lately",
        "Just wanted to check in on my mental health",
        "Feeling okay but could be better",
        "Sometimes I feel a little anxious",
        "Work has been stressful but manageable",
        "I'm doing alright, just curious about resources",
        "Feeling tired more than usual",
        "Just going through some minor stress",
    ],
    "moderate": [
        "I've been really stressed and can't seem to relax",
        "Anxiety has been keeping me up at night",
        "I feel overwhelmed with everything going on",
        "My mood has been really low lately",
        "I'm struggling to find motivation",
        "Feeling disconnected from people around me",
        "Can't shake this feeling of sadness",
        "Everything feels harder than it should be",
        "I don't feel like myself anymore",
        "Constantly worrying about things",
    ],
    "severe": [
        "I feel completely hopeless about the future",
        "Nothing brings me joy anymore",
        "I can't stop crying and don't know why",
        "The darkness feels overwhelming",
        "I feel like a burden to everyone",
        "I don't see the point in anything",
        "Every day feels like a struggle to get through",
        "I feel trapped and don't know what to do",
    ],
}

# Crisis rate (small percentage - these bypass experiment)
CRISIS_RATE = 0.02  # 2% of sessions trigger crisis protocol


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def weighted_choice(choices_with_weights):
    """Select from choices based on weights."""
    choices, weights = zip(*choices_with_weights)
    return random.choices(choices, weights=weights, k=1)[0]


def generate_sentiment_score(severity: str) -> float:
    """
    Generate realistic sentiment score based on severity.

    Uses truncated normal distribution:
    - Mild: centered around 0.1 (slightly positive)
    - Moderate: centered around -0.3
    - Severe: centered around -0.6
    """
    params = {
        "mild": (0.1, 0.25),      # mean, std
        "moderate": (-0.3, 0.2),
        "severe": (-0.6, 0.15),
    }
    mean, std = params[severity]
    score = np.random.normal(mean, std)
    return max(-1.0, min(1.0, score))  # Clamp to [-1, 1]


def generate_time_to_decision(severity: str, converted: bool) -> int:
    """
    Generate realistic time_to_decision_ms.

    - More severe = longer decision time
    - Conversions typically take longer (more deliberate)
    - Non-conversions can be quick (bounce) or long (deliberation then exit)
    """
    base_times = {
        "mild": (3000, 8000),      # 3-8 seconds
        "moderate": (5000, 15000),  # 5-15 seconds
        "severe": (8000, 25000),    # 8-25 seconds
    }

    min_time, max_time = base_times[severity]

    if converted:
        # Conversions cluster in middle-to-high range
        return int(np.random.triangular(min_time, max_time * 0.7, max_time))
    else:
        # Non-conversions: bimodal (quick bounce or long deliberation)
        if random.random() < 0.4:
            # Quick bounce
            return int(np.random.uniform(1000, min_time))
        else:
            # Long deliberation then exit
            return int(np.random.uniform(min_time, max_time * 1.2))


def generate_response_time() -> int:
    """Generate realistic response_time_ms (system latency)."""
    # Most responses are fast, occasional slow ones
    if random.random() < 0.95:
        return int(np.random.uniform(50, 200))
    else:
        return int(np.random.uniform(200, 500))


def generate_timestamp(start: datetime, end: datetime) -> str:
    """Generate random timestamp between start and end."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    timestamp = start + timedelta(seconds=random_seconds)
    return timestamp.isoformat()


# =============================================================================
# MAIN GENERATOR
# =============================================================================

def generate_mock_data(num_records: int = NUM_RECORDS, clear_existing: bool = True):
    """
    Generate mock interaction data and insert into database.

    Args:
        num_records: Number of records to generate
        clear_existing: If True, clear existing data before inserting
    """
    print(f"🔧 Generating {num_records} mock interactions...")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists
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

    if clear_existing:
        cursor.execute("DELETE FROM interactions")
        print("   Cleared existing data.")

    # Generate records
    records = []
    crisis_count = 0
    conversion_counts = {"A_CLINICAL": 0, "B_EMPATHETIC": 0}
    total_counts = {"A_CLINICAL": 0, "B_EMPATHETIC": 0}

    for i in range(num_records):
        session_id = str(uuid.uuid4())
        timestamp = generate_timestamp(START_DATE, END_DATE)

        # Check for crisis (bypasses experiment)
        is_crisis = random.random() < CRISIS_RATE

        if is_crisis:
            crisis_count += 1
            severity = "severe"
            sentiment_score = generate_sentiment_score(severity) - 0.3  # Extra negative
            sentiment_score = max(-1.0, sentiment_score)

            records.append((
                session_id,
                timestamp,
                "I want to hurt myself",  # Crisis input
                sentiment_score,
                severity,
                None,  # No variant assigned
                generate_response_time(),
                None,  # No decision time
                1,
                None,  # No conversion
                "crisis_protocol",
                weighted_choice(UTM_SOURCES),
            ))
        else:
            # Normal experiment flow
            severity = weighted_choice(list(SEVERITY_WEIGHTS.items()))
            variant = random.choice(VARIANTS)
            sentiment_score = generate_sentiment_score(severity)

            # Determine conversion based on rates
            conversion_rate = CONVERSION_RATES[variant][severity]
            converted = 1 if random.random() < conversion_rate else 0

            # Track for summary
            total_counts[variant] += 1
            if converted:
                conversion_counts[variant] += 1

            # Generate other fields
            input_text = random.choice(SAMPLE_INPUTS[severity])
            time_to_decision = generate_time_to_decision(severity, bool(converted))

            records.append((
                session_id,
                timestamp,
                input_text,
                sentiment_score,
                severity,
                variant,
                generate_response_time(),
                time_to_decision,
                1,
                converted,
                None,
                weighted_choice(UTM_SOURCES),
            ))

    # Insert all records
    cursor.executemany("""
        INSERT INTO interactions (
            session_id, timestamp, input_text, sentiment_score, severity_bucket,
            assigned_variant, response_time_ms, time_to_decision_ms, session_depth,
            converted, experiment_excluded, referral_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()

    # Print summary
    print(f"\n✅ Generated {num_records} records")
    print(f"\n📊 Summary:")
    print(f"   Crisis protocol triggered: {crisis_count}")
    print(f"\n   Variant A (Clinical):")
    print(f"      Sessions: {total_counts['A_CLINICAL']}")
    print(f"      Conversions: {conversion_counts['A_CLINICAL']}")
    if total_counts['A_CLINICAL'] > 0:
        rate_a = conversion_counts['A_CLINICAL'] / total_counts['A_CLINICAL'] * 100
        print(f"      Conversion Rate: {rate_a:.1f}%")

    print(f"\n   Variant B (Empathetic):")
    print(f"      Sessions: {total_counts['B_EMPATHETIC']}")
    print(f"      Conversions: {conversion_counts['B_EMPATHETIC']}")
    if total_counts['B_EMPATHETIC'] > 0:
        rate_b = conversion_counts['B_EMPATHETIC'] / total_counts['B_EMPATHETIC'] * 100
        print(f"      Conversion Rate: {rate_b:.1f}%")

    if total_counts['A_CLINICAL'] > 0 and total_counts['B_EMPATHETIC'] > 0:
        lift = (rate_b - rate_a) / rate_a * 100
        print(f"\n   📈 Relative Lift (B vs A): {lift:+.1f}%")

    print(f"\n   Database: {DB_PATH}")


if __name__ == "__main__":
    generate_mock_data()
