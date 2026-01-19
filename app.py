"""
Mind-Log Experimentation Lab
A/B Testing for Mental Health Triage Optimization

Main Streamlit application entry point.
"""

import time
import streamlit as st
import os

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Mind-Log Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules after page config
from src.database import init_db, generate_session_id, log_event, update_conversion, get_record_count
from src.experiment import analyze_input, Variant, Severity
from src.analytics import (
    run_ab_test, get_summary_stats, get_funnel_data,
    get_severity_breakdown, get_sentiment_conversion_data,
    get_time_to_decision_data, get_utm_breakdown, get_dataframe
)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

# Valid referral sources (whitelist to prevent injection)
VALID_REFERRAL_SOURCES = {
    "google_search", "facebook_ads", "instagram_ads", "direct",
    "referral", "email_campaign", "tiktok_ads", "organic", "other"
}

# Input validation
MAX_INPUT_LENGTH = 5000  # Characters
MIN_INPUT_LENGTH = 5

def validate_referral_source(source: str) -> str:
    """
    Validate and sanitize referral source.

    Args:
        source: Raw referral source string (e.g., from UTM parameter)

    Returns:
        Valid referral source string, or 'direct' if invalid
    """
    if not source or source.strip() not in VALID_REFERRAL_SOURCES:
        return "direct"
    return source.strip()


def anonymize_user_input(text: str) -> str:
    """
    Anonymize user input for storage.

    In production, this would:
    - Strip personally identifiable information (names, emails, phone numbers)
    - Hash or truncate sensitive data
    - For this demo, we hash the first 100 chars to prevent exact replay attacks

    Args:
        text: Raw user input

    Returns:
        Anonymized version for database logging
    """
    import hashlib
    # Production: Implement proper PII masking (e.g., with regex for email/phone)
    # For demo: Hash first 100 chars to preserve intent while protecting PII
    preview = text[:100]
    text_hash = hashlib.sha256(preview.encode()).hexdigest()[:16]
    return f"[anonymized:{text_hash}]"


# Initialize database
init_db()

# Auto-generate mock data if database is empty (for Streamlit Cloud deployment)
if get_record_count() == 0:
    from scripts.generate_mock_data import generate_mock_data
    generate_mock_data(num_records=500, clear_existing=False)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "response_shown_at" not in st.session_state:
    st.session_state.response_shown_at = None
if "interaction_logged" not in st.session_state:
    st.session_state.interaction_logged = False
if "converted" not in st.session_state:
    st.session_state.converted = False


def reset_session():
    """Reset session for new interaction."""
    st.session_state.session_id = generate_session_id()
    st.session_state.analysis_result = None
    st.session_state.response_shown_at = None
    st.session_state.interaction_logged = False
    st.session_state.converted = False


def main():
    """Main application entry point."""

    # Sidebar navigation
    st.sidebar.title("🧠 Mind-Log Lab")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        ["💬 Triage Chat", "📊 Analytics Dashboard", "ℹ️ About"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Session: `{st.session_state.session_id[:8]}...`")

    # Debug info (can be removed for production)
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        st.sidebar.markdown("---")
        st.sidebar.caption("**Debug Info**")
        st.sidebar.caption(f"Sentiment: {result.sentiment_score:.2f}")
        st.sidebar.caption(f"Severity: {result.severity.value}")
        if result.assigned_variant:
            st.sidebar.caption(f"Variant: {result.assigned_variant.value}")
        st.sidebar.caption(f"Crisis: {result.is_crisis}")

    # Route to selected page
    if page == "💬 Triage Chat":
        show_triage_chat()
    elif page == "📊 Analytics Dashboard":
        show_analytics_dashboard()
    else:
        show_about()


def show_triage_chat():
    """Triage chat interface - the A/B test happens here."""
    st.title("How are you feeling today?")
    st.markdown(
        "Share what's on your mind. This is a safe, anonymous space. "
        "Your response helps us connect you with the right support."
    )

    # Check if we already have a result to display
    if st.session_state.analysis_result and not st.session_state.converted:
        display_response()
        return

    # Show completion message if converted
    if st.session_state.converted:
        st.success("✅ Thank you for reaching out. A counselor will be in touch soon.")
        if st.button("Start New Session", type="secondary"):
            reset_session()
            st.rerun()
        return

    # Input form
    user_input = st.text_area(
        "Express yourself freely...",
        height=150,
        placeholder="I've been feeling...",
        key="chat_input"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit = st.button("Share", type="primary", use_container_width=True)

    if submit:
        # Validate input
        if not user_input.strip():
            st.warning("Please share how you're feeling before continuing.")
        elif len(user_input) < MIN_INPUT_LENGTH:
            st.warning(f"Please share at least {MIN_INPUT_LENGTH} characters.")
        elif len(user_input) > MAX_INPUT_LENGTH:
            st.error(f"Your message is too long (max {MAX_INPUT_LENGTH} characters). Please shorten it.")
        else:
            process_input(user_input.strip())
            st.rerun()

    st.markdown("---")
    st.caption("🔒 Your privacy is protected. No personal data is stored.")


def process_input(user_input: str):
    """
    Process user input through experiment logic.

    PII Handling Strategy:
    - Raw input is analyzed but NOT stored in database
    - Only anonymized/hashed version is logged
    - In production: Implement PII masking (email, phone, names) before hashing
    """
    # Record start time for response latency
    start_time = time.time()

    # Analyze input (analysis doesn't store the text, only metadata)
    result = analyze_input(user_input)

    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)

    # Store result in session state
    st.session_state.analysis_result = result
    st.session_state.response_shown_at = time.time()

    # Anonymize input before storage (GDPR/privacy best practice)
    anonymized_input = anonymize_user_input(user_input)

    # Get validated referral source
    utm_source = os.getenv("UTM_SOURCE", "direct")
    validated_source = validate_referral_source(utm_source)

    # Log interaction to database
    log_event(
        session_id=st.session_state.session_id,
        input_text=anonymized_input,  # Anonymized for privacy
        sentiment_score=result.sentiment_score,
        severity_bucket=result.severity.value,
        assigned_variant=result.assigned_variant.value if result.assigned_variant else None,
        response_time_ms=response_time_ms,
        experiment_excluded="crisis_protocol" if result.is_crisis else None,
        referral_source=validated_source,  # Validated against whitelist
    )
    st.session_state.interaction_logged = True


def display_response():
    """Display the response based on analysis result."""
    result = st.session_state.analysis_result

    if result.is_crisis:
        # Crisis path - show resources immediately
        st.error("🚨 **We're here for you.**")
        st.markdown(result.crisis_resources)

        st.markdown("---")
        if st.button("Start New Session", type="secondary"):
            reset_session()
            st.rerun()
    else:
        # Normal path - show variant response
        st.markdown("---")

        # Display response based on variant
        if result.assigned_variant == Variant.A_CLINICAL:
            st.markdown(result.response_text)
        else:
            st.markdown(result.response_text)

        st.markdown("---")

        # Conversion button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🤝 Connect with a Counselor",
                type="primary",
                use_container_width=True,
                key="convert_btn"
            ):
                handle_conversion()
                st.rerun()

        # Alternative action
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "Not right now",
                type="secondary",
                use_container_width=True,
                key="decline_btn"
            ):
                handle_decline()
                st.rerun()


def handle_conversion():
    """Handle user clicking the conversion button."""
    # Calculate time to decision
    time_to_decision_ms = int((time.time() - st.session_state.response_shown_at) * 1000)

    # Update database
    update_conversion(
        session_id=st.session_state.session_id,
        converted=1,
        time_to_decision_ms=time_to_decision_ms
    )

    st.session_state.converted = True


def handle_decline():
    """Handle user declining to connect."""
    # Calculate time to decision
    time_to_decision_ms = int((time.time() - st.session_state.response_shown_at) * 1000)

    # Update database with non-conversion
    update_conversion(
        session_id=st.session_state.session_id,
        converted=0,
        time_to_decision_ms=time_to_decision_ms
    )

    # Reset for new session
    reset_session()


def show_analytics_dashboard():
    """Analytics dashboard - displays A/B test results."""
    st.title("📊 Experiment Analytics")

    # Load data
    try:
        stats = get_summary_stats()
        ab_result = run_ab_test()
        funnel = get_funnel_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Run the mock data generator first: `python scripts/generate_mock_data.py`")
        return

    # ==========================================================================
    # KPI HEADER
    # ==========================================================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Sessions",
            f"{stats['total_sessions']:,}",
            help="Total experiment sessions"
        )
    with col2:
        st.metric(
            "Conversion Rate",
            f"{stats['overall_rate']:.1%}",
            help="Overall click-through rate"
        )
    with col3:
        delta_a = None
        st.metric(
            "Variant A (Clinical)",
            f"{stats['variant_a_rate']:.1%}",
            delta=delta_a,
            help="Clinical response conversion"
        )
    with col4:
        lift = (stats['variant_b_rate'] - stats['variant_a_rate']) / stats['variant_a_rate'] * 100 if stats['variant_a_rate'] > 0 else 0
        st.metric(
            "Variant B (Empathetic)",
            f"{stats['variant_b_rate']:.1%}",
            delta=f"+{lift:.1f}%",
            help="Empathetic response conversion"
        )

    st.markdown("---")

    # ==========================================================================
    # A/B TEST RESULTS PANEL
    # ==========================================================================
    st.subheader("🧪 A/B Test Results")

    # Significance indicator
    if ab_result.is_significant:
        st.success(f"**Statistically Significant** (p = {ab_result.p_value:.4f})")
    else:
        st.warning(f"**Not Significant** (p = {ab_result.p_value:.4f}) — Continue experiment")

    # Recommendation
    st.info(ab_result.recommendation)

    # Confidence interval visualization
    col1, col2 = st.columns(2)

    with col1:
        # Create CI chart
        fig_ci = go.Figure()

        # Variant A
        fig_ci.add_trace(go.Scatter(
            x=[ab_result.variant_a_rate * 100],
            y=['Variant A (Clinical)'],
            mode='markers',
            marker=dict(size=15, color='#636EFA'),
            error_x=dict(
                type='data',
                symmetric=False,
                array=[(ab_result.variant_a_ci_upper - ab_result.variant_a_rate) * 100],
                arrayminus=[(ab_result.variant_a_rate - ab_result.variant_a_ci_lower) * 100],
                color='#636EFA',
                thickness=2,
                width=10,
            ),
            name='Variant A',
            hovertemplate='%{x:.1f}%<extra>Variant A</extra>'
        ))

        # Variant B
        fig_ci.add_trace(go.Scatter(
            x=[ab_result.variant_b_rate * 100],
            y=['Variant B (Empathetic)'],
            mode='markers',
            marker=dict(size=15, color='#00CC96'),
            error_x=dict(
                type='data',
                symmetric=False,
                array=[(ab_result.variant_b_ci_upper - ab_result.variant_b_rate) * 100],
                arrayminus=[(ab_result.variant_b_rate - ab_result.variant_b_ci_lower) * 100],
                color='#00CC96',
                thickness=2,
                width=10,
            ),
            name='Variant B',
            hovertemplate='%{x:.1f}%<extra>Variant B</extra>'
        ))

        fig_ci.update_layout(
            title="Conversion Rates with 95% CI",
            xaxis_title="Conversion Rate (%)",
            showlegend=False,
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_ci, use_container_width=True)

    with col2:
        # Summary table
        summary_data = {
            'Metric': ['Sessions', 'Conversions', 'Rate', '95% CI'],
            'Variant A': [
                ab_result.variant_a_sessions,
                ab_result.variant_a_conversions,
                f"{ab_result.variant_a_rate:.1%}",
                f"[{ab_result.variant_a_ci_lower:.1%}, {ab_result.variant_a_ci_upper:.1%}]"
            ],
            'Variant B': [
                ab_result.variant_b_sessions,
                ab_result.variant_b_conversions,
                f"{ab_result.variant_b_rate:.1%}",
                f"[{ab_result.variant_b_ci_lower:.1%}, {ab_result.variant_b_ci_upper:.1%}]"
            ],
        }
        st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)

        st.caption(f"**Relative Lift:** {ab_result.relative_lift:+.1%} | **Z-stat:** {ab_result.z_statistic:.2f}")

    st.markdown("---")

    # ==========================================================================
    # FUNNEL & SEGMENT ANALYSIS
    # ==========================================================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Conversion Funnel")

        funnel_fig = go.Figure(go.Funnel(
            y=['Total Sessions', 'Experiment Sessions', 'Conversions'],
            x=[funnel['total_sessions'], funnel['experiment_sessions'], funnel['conversions']],
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(color=['#636EFA', '#EF553B', '#00CC96']),
        ))
        funnel_fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(funnel_fig, use_container_width=True)
        st.caption(f"*{funnel['crisis_excluded']} sessions excluded (crisis protocol)*")

    with col2:
        st.subheader("📈 Conversion by Severity")

        severity_df = get_severity_breakdown()
        fig_severity = px.bar(
            severity_df,
            x='severity_bucket',
            y='conversion_rate',
            color='assigned_variant',
            barmode='group',
            labels={
                'severity_bucket': 'Severity',
                'conversion_rate': 'Conversion Rate',
                'assigned_variant': 'Variant'
            },
            color_discrete_map={
                'A_CLINICAL': '#636EFA',
                'B_EMPATHETIC': '#00CC96'
            },
        )
        fig_severity.update_layout(
            yaxis_tickformat='.0%',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig_severity, use_container_width=True)

    st.markdown("---")

    # ==========================================================================
    # SENTIMENT & TIME ANALYSIS
    # ==========================================================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💭 Sentiment vs Conversion")

        sentiment_df = get_sentiment_conversion_data()
        sentiment_df['converted_label'] = sentiment_df['converted'].map({0: 'No', 1: 'Yes'})

        fig_sentiment = px.scatter(
            sentiment_df,
            x='sentiment_score',
            y='converted',
            color='assigned_variant',
            symbol='converted_label',
            labels={
                'sentiment_score': 'Sentiment Score',
                'converted': 'Converted',
                'assigned_variant': 'Variant'
            },
            color_discrete_map={
                'A_CLINICAL': '#636EFA',
                'B_EMPATHETIC': '#00CC96'
            },
            opacity=0.6,
        )
        fig_sentiment.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No', 'Yes']),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)

    with col2:
        st.subheader("⏱️ Time to Decision")

        time_df = get_time_to_decision_data()
        time_df['time_seconds'] = time_df['time_to_decision_ms'] / 1000

        fig_time = px.box(
            time_df,
            x='assigned_variant',
            y='time_seconds',
            color='assigned_variant',
            labels={
                'assigned_variant': 'Variant',
                'time_seconds': 'Time to Decision (seconds)'
            },
            color_discrete_map={
                'A_CLINICAL': '#636EFA',
                'B_EMPATHETIC': '#00CC96'
            },
        )
        fig_time.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    # ==========================================================================
    # MARKETING ATTRIBUTION
    # ==========================================================================
    st.subheader("📣 Marketing Attribution")

    utm_df = get_utm_breakdown()
    fig_utm = px.bar(
        utm_df,
        x='referral_source',
        y='sessions',
        color='conversion_rate',
        color_continuous_scale='Greens',
        labels={
            'referral_source': 'Source',
            'sessions': 'Sessions',
            'conversion_rate': 'Conv. Rate'
        },
    )
    fig_utm.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig_utm, use_container_width=True)


def show_about():
    """About page with project information."""
    st.title("ℹ️ About Mind-Log Lab")

    st.markdown("""
    ## Project Overview

    **Mind-Log Experimentation Lab** is a full-stack analytics prototype demonstrating:

    1. **Product Engineering**: Interactive triage chatbot
    2. **Data Engineering**: Event logging and data pipeline
    3. **Product Analytics**: A/B test analysis with statistical rigor

    ## The Experiment

    We're testing whether **conversational tone** impacts help-seeking behavior
    in mental health triage:

    | Variant | Style | Example Response |
    |---------|-------|------------------|
    | A | Clinical | "Symptom noted. Severity: Moderate. Recommended action: Consult a specialist." |
    | B | Empathetic | "It sounds like you're carrying a heavy load. Would you be open to speaking with someone who can help?" |

    ## Key Metrics

    - **Primary**: Conversion rate (click on "Connect with Counselor")
    - **Secondary**: Time to decision, sentiment correlation

    ## Safety First

    Crisis detection protocol bypasses the experiment for users in acute distress,
    immediately displaying crisis resources.

    ---

    *Built for MOHT Data Analyst interview demonstration.*
    """)


if __name__ == "__main__":
    main()
