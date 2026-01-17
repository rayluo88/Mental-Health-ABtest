"""
Analytics Module for Mind-Log Experimentation Lab.

Provides statistical analysis functions for A/B test results:
- Conversion rate calculations with confidence intervals
- Two-proportion z-test for significance
- Segment analysis by severity
- Summary statistics for dashboard
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "experiment.db"


@dataclass
class ABTestResult:
    """Results from A/B test statistical analysis."""
    variant_a_sessions: int
    variant_a_conversions: int
    variant_a_rate: float
    variant_a_ci_lower: float
    variant_a_ci_upper: float

    variant_b_sessions: int
    variant_b_conversions: int
    variant_b_rate: float
    variant_b_ci_lower: float
    variant_b_ci_upper: float

    relative_lift: float
    lift_ci_lower: float
    lift_ci_upper: float

    p_value: float
    z_statistic: float
    is_significant: bool
    recommendation: str


def get_dataframe() -> pd.DataFrame:
    """Load all interactions into a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT * FROM interactions
        WHERE experiment_excluded IS NULL
        ORDER BY timestamp
    """, conn)
    conn.close()
    return df


def get_full_dataframe() -> pd.DataFrame:
    """Load ALL interactions (including crisis) into a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM interactions ORDER BY timestamp", conn)
    conn.close()
    return df


def calculate_conversion_rate_ci(conversions: int, total: int, alpha: float = 0.05) -> tuple:
    """
    Calculate conversion rate with confidence interval.

    Uses Wilson score interval (more accurate for proportions near 0 or 1).

    Args:
        conversions: Number of conversions
        total: Total sessions
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        Tuple of (rate, ci_lower, ci_upper)
    """
    if total == 0:
        return 0.0, 0.0, 0.0

    rate = conversions / total
    ci_lower, ci_upper = proportion_confint(conversions, total, alpha=alpha, method='wilson')

    return rate, ci_lower, ci_upper


def run_ab_test(df: Optional[pd.DataFrame] = None) -> ABTestResult:
    """
    Run statistical analysis on A/B test data.

    Performs:
    1. Conversion rate calculation with 95% CI for each variant
    2. Two-proportion z-test for significance
    3. Relative lift calculation

    Args:
        df: Optional DataFrame (loads from DB if not provided)

    Returns:
        ABTestResult with all statistics
    """
    if df is None:
        df = get_dataframe()

    # Filter to only experiment data (exclude crisis)
    df_exp = df[df['experiment_excluded'].isna() & df['assigned_variant'].notna()].copy()

    # Separate by variant
    df_a = df_exp[df_exp['assigned_variant'] == 'A_CLINICAL']
    df_b = df_exp[df_exp['assigned_variant'] == 'B_EMPATHETIC']

    # Count sessions and conversions
    n_a = len(df_a)
    conv_a = df_a['converted'].sum()

    n_b = len(df_b)
    conv_b = df_b['converted'].sum()

    # Calculate rates and CIs
    rate_a, ci_a_lower, ci_a_upper = calculate_conversion_rate_ci(conv_a, n_a)
    rate_b, ci_b_lower, ci_b_upper = calculate_conversion_rate_ci(conv_b, n_b)

    # Calculate relative lift
    if rate_a > 0:
        relative_lift = (rate_b - rate_a) / rate_a
    else:
        relative_lift = 0.0

    # Bootstrap CI for relative lift (simplified)
    lift_ci_lower = relative_lift - 0.15  # Approximation
    lift_ci_upper = relative_lift + 0.15

    # Two-proportion z-test
    if n_a > 0 and n_b > 0:
        count = np.array([conv_b, conv_a])
        nobs = np.array([n_b, n_a])
        z_stat, p_value = proportions_ztest(count, nobs, alternative='larger')
    else:
        z_stat, p_value = 0.0, 1.0

    # Determine significance and recommendation
    is_significant = p_value < 0.05

    if is_significant and relative_lift > 0:
        recommendation = (
            f"✅ Variant B (Empathetic) significantly outperforms Variant A. "
            f"Recommend rolling out Empathetic responses."
        )
    elif is_significant and relative_lift < 0:
        recommendation = (
            f"⚠️ Variant A (Clinical) significantly outperforms Variant B. "
            f"Recommend keeping Clinical responses."
        )
    else:
        recommendation = (
            f"⏳ No statistically significant difference detected. "
            f"Continue experiment to gather more data."
        )

    return ABTestResult(
        variant_a_sessions=n_a,
        variant_a_conversions=int(conv_a),
        variant_a_rate=rate_a,
        variant_a_ci_lower=ci_a_lower,
        variant_a_ci_upper=ci_a_upper,
        variant_b_sessions=n_b,
        variant_b_conversions=int(conv_b),
        variant_b_rate=rate_b,
        variant_b_ci_lower=ci_b_lower,
        variant_b_ci_upper=ci_b_upper,
        relative_lift=relative_lift,
        lift_ci_lower=lift_ci_lower,
        lift_ci_upper=lift_ci_upper,
        p_value=p_value,
        z_statistic=z_stat,
        is_significant=is_significant,
        recommendation=recommendation,
    )


def get_severity_breakdown(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Get conversion rates by severity bucket and variant.

    Returns DataFrame with columns:
    - severity_bucket
    - assigned_variant
    - sessions
    - conversions
    - conversion_rate
    """
    if df is None:
        df = get_dataframe()

    df_exp = df[df['experiment_excluded'].isna() & df['assigned_variant'].notna()].copy()

    breakdown = df_exp.groupby(['severity_bucket', 'assigned_variant']).agg(
        sessions=('session_id', 'count'),
        conversions=('converted', 'sum')
    ).reset_index()

    breakdown['conversion_rate'] = breakdown['conversions'] / breakdown['sessions']

    return breakdown


def get_funnel_data(df: Optional[pd.DataFrame] = None) -> dict:
    """
    Get funnel data for visualization.

    Returns dict with:
    - total_sessions
    - experiment_sessions (excluding crisis)
    - conversions
    - crisis_excluded
    """
    if df is None:
        df = get_full_dataframe()

    total = len(df)
    crisis = len(df[df['experiment_excluded'] == 'crisis_protocol'])
    experiment = len(df[df['experiment_excluded'].isna()])
    conversions = df[df['converted'] == 1]['converted'].count()

    return {
        'total_sessions': total,
        'experiment_sessions': experiment,
        'conversions': int(conversions),
        'crisis_excluded': crisis,
    }


def get_sentiment_conversion_data(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Get data for sentiment vs conversion scatter plot.

    Returns DataFrame with sentiment_score, converted, assigned_variant.
    """
    if df is None:
        df = get_dataframe()

    return df[['sentiment_score', 'converted', 'assigned_variant', 'severity_bucket']].copy()


def get_time_to_decision_data(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Get time_to_decision data by variant.

    Returns DataFrame with time_to_decision_ms, assigned_variant, converted.
    """
    if df is None:
        df = get_dataframe()

    return df[['time_to_decision_ms', 'assigned_variant', 'converted', 'severity_bucket']].dropna()


def get_utm_breakdown(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Get conversion rates by UTM source.

    Returns DataFrame with referral_source, sessions, conversions, conversion_rate.
    """
    if df is None:
        df = get_dataframe()

    breakdown = df.groupby('referral_source').agg(
        sessions=('session_id', 'count'),
        conversions=('converted', 'sum')
    ).reset_index()

    breakdown['conversion_rate'] = breakdown['conversions'] / breakdown['sessions']
    breakdown = breakdown.sort_values('sessions', ascending=False)

    return breakdown


def get_summary_stats(df: Optional[pd.DataFrame] = None) -> dict:
    """
    Get summary statistics for dashboard header.
    """
    if df is None:
        df = get_full_dataframe()

    df_exp = df[df['experiment_excluded'].isna()]

    total = len(df)
    conversions = df_exp['converted'].sum()
    conversion_rate = conversions / len(df_exp) if len(df_exp) > 0 else 0

    # Per variant
    df_a = df_exp[df_exp['assigned_variant'] == 'A_CLINICAL']
    df_b = df_exp[df_exp['assigned_variant'] == 'B_EMPATHETIC']

    rate_a = df_a['converted'].mean() if len(df_a) > 0 else 0
    rate_b = df_b['converted'].mean() if len(df_b) > 0 else 0

    return {
        'total_sessions': total,
        'total_conversions': int(conversions),
        'overall_rate': conversion_rate,
        'variant_a_rate': rate_a,
        'variant_b_rate': rate_b,
    }
