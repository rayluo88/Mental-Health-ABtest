# Product Requirements Document (PRD)
## Project Name: Mind-Log Experimentation Lab
### "Optimizing Mental Health Triage via A/B Testing & NLP"

**Author:** Ray Luo
**Date:** January 2026
**Target Role:** Manager/Senior Manager, Data Analyst (MOHT)
**Version:** 1.1 (MVP)

---

## 1. Executive Summary
**Problem:** Digital mental health platforms often suffer from high drop-off rates during the triage process. Users in distress may disengage if the automated response feels too robotic or, conversely, too intrusive.
**Solution:** A "Full-Stack Analytics" prototype that serves as a triage bot while simultaneously running a controlled A/B test. It compares two distinct conversational styles (Clinical vs. Empathetic) to measure which leads to higher user conversion (click-through to services).
**Goal:** To demonstrate end-to-end data capability: **Product Engineering** (The App) + **Data Engineering** (The Logging) + **Product Analytics** (The Insight).

---

## 2. The Experiment Design (Hypothesis)
**Null Hypothesis ($H_0$):** There is no significant difference in conversion rates between Clinical and Empathetic responses.
**Alternative Hypothesis ($H_1$):** The Empathetic response (Variant B) will result in a higher conversion rate for users exhibiting "High Anxiety" sentiment.

### Variables
*   **Independent Variable:** Chatbot Persona (Variant A vs. Variant B).
*   **Dependent Variable:** Conversion Rate (Click on "Find a Professional").
*   **Covariates (for analysis):** User Sentiment Score, Severity Bucket, Message Length, Time of Day.

### Power Analysis (Sample Size Justification)
*   **Baseline Conversion Rate:** 15% (industry benchmark for mental health CTAs)
*   **Minimum Detectable Effect (MDE):** 5 percentage points (15% → 20%)
*   **Statistical Power:** 80%, Alpha (α): 0.05
*   **Required Sample Size:** ~550 users per variant (1,100 total)

```python
# Sample size calculation (scipy.stats)
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

effect_size = proportion_effectsize(0.20, 0.15)  # 20% vs 15%
analysis = NormalIndPower()
n = analysis.solve_power(effect_size, power=0.8, alpha=0.05, ratio=1)
# n ≈ 550 per group
```

*Note: MVP uses 500 simulated sessions to demonstrate methodology. Production deployment would require ~2 weeks of traffic at scale to reach statistical significance.*

---

## 3. Functional Requirements (The User Interface)

### 3.1 User Journey
1.  **Input:** User arrives at landing page and types their current mental state (e.g., "I feel overwhelmed").
2.  **Processing:**
    *   App calculates **Sentiment Score** (using TextBlob/Vader).
    *   App derives **Severity Bucket** (mild/moderate/severe) from sentiment.
    *   App assigns **Variant** (Randomized 50/50 split).
3.  **Response:**
    *   **Variant A (Clinical):** "Symptom noted. Severity: Moderate. Recommended action: Consult a specialist."
    *   **Variant B (Empathetic):** "It sounds like you are carrying a heavy load right now. It takes courage to share that. Would you be open to speaking with someone who can help?"
4.  **Conversion Point:** A specific button appears: **[Connect with Counselor]**.
5.  **Feedback:** User clicks (Conversion = 1) or leaves (Conversion = 0).

---

## 4. Data Instrumentation (The "Analyst" Core)
*Crucial Section: This demonstrates you plan for data capture before building.*

### 4.1 Event Schema (Database/Log Table)
The application will log every interaction into a structured format (CSV/SQLite for MVP).

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `session_id` | UUID | Unique identifier for the user session |
| `timestamp` | Datetime | Time of interaction (UTC) |
| `input_text` | String | Raw text (anonymized in production) |
| `sentiment_score` | Float | -1.0 (Negative) to 1.0 (Positive) |
| `severity_bucket` | String | 'mild', 'moderate', 'severe' (derived from sentiment) |
| `assigned_variant`| String | 'A_CLINICAL' or 'B_EMPATHETIC' |
| `response_time_ms`| Integer | System latency performance |
| `time_to_decision_ms` | Integer | Time between response shown and click/exit |
| `session_depth` | Integer | Number of messages in session |
| `converted` | Boolean | 1 if button clicked, 0 if not |
| `experiment_excluded` | String | Null, or reason for exclusion (e.g., 'crisis_protocol') |
| `referral_source` | String | UTM parameter for marketing attribution |

### 4.2 Data Pipeline (Mock)
*   Since real traffic requires time, a **Data Generator Script** will be built to simulate 500 historical interactions, incorporating bias (e.g., higher conversion for Variant B) to demonstrate analytical skills in the dashboard.

---

## 5. Analytics Dashboard Requirements (The "Director's View")
*This section defines what the interviewer will see.*

### 5.1 Key Performance Indicators (KPIs)
*   **Global Conversion Rate:** % of total users who clicked.
*   **Variant Performance:** Conversion Rate (A) vs. Conversion Rate (B).
*   **Sentiment Distribution:** Histogram of user input sentiment.
*   **Segment Analysis:** Conversion by severity bucket (mild/moderate/severe).

### 5.2 Visualizations
1.  **The Funnel:** Bar chart showing `Sessions` -> `Valid Inputs` -> `Conversions`.
2.  **A/B Test Results Panel:**
    *   Conversion rate per variant with **95% confidence intervals** (error bars)
    *   Relative lift with CI: e.g., "Variant B shows +33% lift (95% CI: +12% to +58%)"
    *   P-value display with practical significance assessment
    *   *Decision Logic:*
        *   If P < 0.05 AND lower CI bound > 0: "Statistically Significant Positive Result"
        *   If P < 0.05 but CI crosses 0: "Significant but inconclusive direction"
        *   If P >= 0.05: "No significant difference detected (continue experiment)"
3.  **Sentiment Correlation:** Scatter plot showing `Sentiment Score` vs. `Conversion`, colored by variant.
4.  **Time to Decision:** Distribution plot comparing decision latency between variants.

---

## 6. Technology Stack
*   **Frontend/App Logic:** Streamlit (Python).
*   **NLP Engine:** `TextBlob` or `NLTK` (Keep it lightweight for MVP).
*   **Data Storage:** Local `interaction_logs.csv` or SQLite.
*   **Visualization:** `Plotly` or `Altair` (Native to Streamlit).
*   **Statistics:** `scipy.stats` for hypothesis testing, `statsmodels` for confidence intervals.

---

## 7. Implementation Roadmap (Next 48 Hours)
*   **Phase 1 (Setup):** Initialize Repo, set up basic Streamlit text input.
*   **Phase 2 (Logic):** Implement Randomizer and simple IF/ELSE response logic.
*   **Phase 3 (Logging):** Build the `log_event()` function to save data to CSV.
*   **Phase 4 (Generation):** Run script to generate 500 "fake" user logs.
*   **Phase 5 (Dashboard):** Build the analytics tab to visualize the fake logs.

---

## 8. Ethical Considerations & Safety Rails
*Critical for mental health applications: safety must be designed in from the start.*

### 8.1 Crisis Detection Protocol
Users in acute distress must receive immediate support, not be subjected to experimentation.

*   **Trigger Conditions:**
    *   Sentiment score < -0.8, OR
    *   Input contains crisis keywords: `["hurt myself", "end it", "suicide", "kill myself", "don't want to live", "no reason to live"]`
*   **Action:** Bypass A/B test entirely → Display crisis resources immediately:
    *   Singapore: SOS 24-hour Hotline (1-767)
    *   IMH Mental Health Helpline (6389-2222)
*   **Logging:** Record as `experiment_excluded: 'crisis_protocol'` (no variant assignment)

### 8.2 Data Privacy
*   **No PII Storage:** `session_id` is ephemeral and not linked to user accounts
*   **Text Anonymization:** In production, only sentiment score is retained; raw text is discarded after processing
*   **Retention Policy:** Interaction logs purged after 90 days (configurable)

### 8.3 Experiment Ethics
*   **No Harmful Control:** Both variants provide valid pathways to support (no "placebo" that withholds help)
*   **Auto-Stop Rules:** Experiment halts automatically if either variant shows significantly *worse* outcomes (protective stopping)
*   **Informed Context:** Users are informed the platform uses AI to personalize responses (transparency)

---

## 9. Success Criteria
*   MVP deployed and functional with simulated data
*   Dashboard demonstrates statistical literacy (CIs, p-values, power analysis)
*   Safety rails implemented and testable
*   Code documented and shareable for interview discussion
