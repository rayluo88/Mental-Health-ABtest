"""
Unit tests for Mind-Log Experimentation Lab.
Tests core experiment logic: sentiment analysis, crisis detection, variant assignment.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.experiment import (
    analyze_sentiment,
    get_severity_bucket,
    detect_crisis,
    assign_variant,
    analyze_input,
    Severity,
    Variant,
    CRISIS_KEYWORDS,
)


def test_sentiment_analysis():
    """Test VADER sentiment analysis returns expected ranges."""
    # Positive sentiment
    score = analyze_sentiment("I'm feeling great today!")
    assert score > 0, f"Expected positive score, got {score}"

    # Negative sentiment
    score = analyze_sentiment("I feel terrible and hopeless")
    assert score < 0, f"Expected negative score, got {score}"

    # Neutral sentiment
    score = analyze_sentiment("The weather is cloudy")
    assert -0.3 < score < 0.3, f"Expected neutral score, got {score}"

    print("✅ test_sentiment_analysis passed")


def test_severity_bucketing():
    """Test severity bucket classification."""
    # Mild (sentiment >= 0)
    assert get_severity_bucket(0.5) == Severity.MILD
    assert get_severity_bucket(0.0) == Severity.MILD

    # Moderate (-0.5 <= sentiment < 0)
    assert get_severity_bucket(-0.3) == Severity.MODERATE
    assert get_severity_bucket(-0.49) == Severity.MODERATE

    # Severe (sentiment < -0.5)
    assert get_severity_bucket(-0.6) == Severity.SEVERE
    assert get_severity_bucket(-1.0) == Severity.SEVERE

    print("✅ test_severity_bucketing passed")


def test_crisis_detection_keywords():
    """Test crisis detection with keywords."""
    # Should trigger crisis
    assert detect_crisis("I want to hurt myself", 0.0) == True
    assert detect_crisis("I want to end it all", 0.0) == True
    assert detect_crisis("thinking about suicide", 0.0) == True
    assert detect_crisis("I don't want to live anymore", 0.0) == True

    # Should NOT trigger crisis (no keywords, normal sentiment)
    assert detect_crisis("I'm feeling sad today", -0.3) == False
    assert detect_crisis("Work is stressful", -0.4) == False

    print("✅ test_crisis_detection_keywords passed")


def test_crisis_detection_sentiment():
    """Test crisis detection with extreme negative sentiment."""
    # Should trigger crisis (sentiment < -0.8)
    assert detect_crisis("anything", -0.85) == True
    assert detect_crisis("test", -0.9) == True

    # Should NOT trigger (sentiment >= -0.8)
    assert detect_crisis("test", -0.7) == False
    assert detect_crisis("test", -0.5) == False

    print("✅ test_crisis_detection_sentiment passed")


def test_variant_assignment():
    """Test variant assignment is random and valid."""
    variants = [assign_variant() for _ in range(100)]

    # Should only contain valid variants
    assert all(v in [Variant.A_CLINICAL, Variant.B_EMPATHETIC] for v in variants)

    # Should have roughly 50/50 split (with some tolerance)
    a_count = sum(1 for v in variants if v == Variant.A_CLINICAL)
    assert 30 < a_count < 70, f"Expected ~50% variant A, got {a_count}%"

    print("✅ test_variant_assignment passed")


def test_analyze_input_normal():
    """Test full input analysis for normal (non-crisis) cases."""
    result = analyze_input("I've been feeling stressed about work")

    assert result.is_crisis == False
    assert result.assigned_variant is not None
    assert result.response_text != ""
    assert result.crisis_resources is None
    assert -1 <= result.sentiment_score <= 1

    print("✅ test_analyze_input_normal passed")


def test_analyze_input_crisis():
    """Test full input analysis for crisis cases."""
    result = analyze_input("I want to hurt myself")

    assert result.is_crisis == True
    assert result.assigned_variant is None  # No variant for crisis
    assert result.crisis_resources is not None
    assert "SOS" in result.crisis_resources or "1-767" in result.crisis_resources

    print("✅ test_analyze_input_crisis passed")


def test_response_templates_exist():
    """Test that response templates exist for all variant/severity combinations."""
    from src.experiment import RESPONSES

    for variant in [Variant.A_CLINICAL, Variant.B_EMPATHETIC]:
        for severity in [Severity.MILD, Severity.MODERATE, Severity.SEVERE]:
            response = RESPONSES[variant][severity]
            assert len(response) > 50, f"Response too short for {variant}/{severity}"

    print("✅ test_response_templates_exist passed")


def run_all_tests():
    """Run all tests."""
    print("\n🧪 Running Mind-Log Experiment Tests\n")

    test_sentiment_analysis()
    test_severity_bucketing()
    test_crisis_detection_keywords()
    test_crisis_detection_sentiment()
    test_variant_assignment()
    test_analyze_input_normal()
    test_analyze_input_crisis()
    test_response_templates_exist()

    print("\n✅ All tests passed!\n")


if __name__ == "__main__":
    run_all_tests()
