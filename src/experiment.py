"""
Experiment Logic Module for Mind-Log Lab.
Handles sentiment analysis, variant assignment, crisis detection, and responses.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class Variant(Enum):
    """A/B test variants."""
    A_CLINICAL = "A_CLINICAL"
    B_EMPATHETIC = "B_EMPATHETIC"


class Severity(Enum):
    """Severity buckets derived from sentiment."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass
class AnalysisResult:
    """Result of analyzing user input."""
    sentiment_score: float
    severity: Severity
    is_crisis: bool
    assigned_variant: Optional[Variant]
    response_text: str
    crisis_resources: Optional[str] = None


# ============================================================================
# CRISIS DETECTION
# ============================================================================

CRISIS_KEYWORDS = [
    "hurt myself",
    "end it",
    "end it all",
    "suicide",
    "suicidal",
    "kill myself",
    "killing myself",
    "don't want to live",
    "dont want to live",
    "no reason to live",
    "better off dead",
    "can't go on",
    "cant go on",
    "want to die",
    "wish i was dead",
    "take my life",
    "end my life",
]

CRISIS_SENTIMENT_THRESHOLD = -0.8

CRISIS_RESOURCES = """
## You're Not Alone

If you're having thoughts of self-harm, please reach out now:

🆘 **SOS 24-hour Hotline**: 1-767
📞 **IMH Mental Health Helpline**: 6389-2222
💬 **Samaritans of Singapore**: 1800-221-4444

These services are free, confidential, and available 24/7.

**You matter. Help is available.**
"""


def detect_crisis(text: str, sentiment_score: float) -> bool:
    """
    Detect if user input indicates a crisis situation.

    Crisis is triggered by:
    - Sentiment score below threshold (-0.8), OR
    - Presence of crisis keywords

    Args:
        text: User input text (lowercased for matching)
        sentiment_score: VADER compound score (-1 to 1)

    Returns:
        True if crisis detected, False otherwise
    """
    text_lower = text.lower()

    # Check sentiment threshold
    if sentiment_score < CRISIS_SENTIMENT_THRESHOLD:
        return True

    # Check keywords
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True

    return False


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

# Initialize VADER analyzer (singleton)
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of user input using VADER.

    VADER is specifically tuned for social media and informal text,
    making it suitable for mental health input which is often emotional.

    Args:
        text: User input text

    Returns:
        Compound sentiment score from -1.0 (negative) to 1.0 (positive)
    """
    scores = _analyzer.polarity_scores(text)
    return scores['compound']


def get_severity_bucket(sentiment_score: float) -> Severity:
    """
    Classify sentiment into severity buckets.

    Thresholds:
    - Severe: sentiment < -0.5
    - Moderate: -0.5 <= sentiment < 0
    - Mild: sentiment >= 0

    Args:
        sentiment_score: VADER compound score (-1 to 1)

    Returns:
        Severity enum (MILD, MODERATE, SEVERE)
    """
    if sentiment_score < -0.5:
        return Severity.SEVERE
    elif sentiment_score < 0:
        return Severity.MODERATE
    else:
        return Severity.MILD


# ============================================================================
# A/B VARIANT ASSIGNMENT
# ============================================================================

def assign_variant() -> Variant:
    """
    Randomly assign user to A/B test variant (50/50 split).

    Returns:
        Variant.A_CLINICAL or Variant.B_EMPATHETIC
    """
    return random.choice([Variant.A_CLINICAL, Variant.B_EMPATHETIC])


# ============================================================================
# RESPONSE TEMPLATES
# ============================================================================

RESPONSES = {
    Variant.A_CLINICAL: {
        Severity.MILD: (
            "**Assessment Complete**\n\n"
            "Symptom severity: **Mild**\n\n"
            "Your responses indicate low distress levels. "
            "Preventive self-care is recommended. "
            "Professional consultation available if desired."
        ),
        Severity.MODERATE: (
            "**Assessment Complete**\n\n"
            "Symptom severity: **Moderate**\n\n"
            "Your responses indicate moderate distress. "
            "Recommended action: Consultation with a mental health professional. "
            "Early intervention can prevent escalation."
        ),
        Severity.SEVERE: (
            "**Assessment Complete**\n\n"
            "Symptom severity: **High**\n\n"
            "Your responses indicate significant distress. "
            "Immediate professional support is strongly recommended. "
            "A counselor can help you navigate these feelings."
        ),
    },
    Variant.B_EMPATHETIC: {
        Severity.MILD: (
            "Thank you for sharing with me. 💙\n\n"
            "It sounds like you're managing, and that takes strength. "
            "Even when things feel okay, having someone to talk to can help maintain your wellbeing. "
            "Would you like to explore some self-care resources, or connect with a supportive listener?"
        ),
        Severity.MODERATE: (
            "I hear you, and I want you to know that what you're feeling matters. 💙\n\n"
            "It sounds like you're carrying quite a bit right now. "
            "You don't have to figure this out alone. "
            "Speaking with someone who understands can make a real difference. "
            "Would you be open to connecting with a counselor who can help?"
        ),
        Severity.SEVERE: (
            "I'm really glad you reached out. What you're going through sounds incredibly hard. 💙\n\n"
            "Please know that these feelings, as overwhelming as they are, can get better with support. "
            "You've taken an important step by sharing this. "
            "I'd really encourage you to speak with someone who can help you through this. "
            "Would you like to connect with a counselor now?"
        ),
    },
}


def get_response(variant: Variant, severity: Severity) -> str:
    """
    Get response text based on variant and severity.

    Args:
        variant: A_CLINICAL or B_EMPATHETIC
        severity: MILD, MODERATE, or SEVERE

    Returns:
        Response text string
    """
    return RESPONSES[variant][severity]


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_input(text: str) -> AnalysisResult:
    """
    Main function to analyze user input and generate appropriate response.

    This is the entry point for the experiment logic:
    1. Analyze sentiment using VADER
    2. Check for crisis indicators
    3. If crisis: bypass experiment, show resources
    4. If not crisis: assign variant, determine severity, get response

    Args:
        text: User input text

    Returns:
        AnalysisResult with all analysis data and response
    """
    # Step 1: Analyze sentiment
    sentiment_score = analyze_sentiment(text)

    # Step 2: Determine severity
    severity = get_severity_bucket(sentiment_score)

    # Step 3: Check for crisis
    is_crisis = detect_crisis(text, sentiment_score)

    if is_crisis:
        # Crisis path: bypass experiment, show resources immediately
        return AnalysisResult(
            sentiment_score=sentiment_score,
            severity=severity,
            is_crisis=True,
            assigned_variant=None,  # Not assigned during crisis
            response_text="",
            crisis_resources=CRISIS_RESOURCES,
        )

    # Step 4: Normal path - assign variant and generate response
    variant = assign_variant()
    response_text = get_response(variant, severity)

    return AnalysisResult(
        sentiment_score=sentiment_score,
        severity=severity,
        is_crisis=False,
        assigned_variant=variant,
        response_text=response_text,
    )
