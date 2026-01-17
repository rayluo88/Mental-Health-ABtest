# Mind-Log Experimentation Lab

**A/B Testing for Mental Health Triage Optimization**

🚀 **Live Demo:** [https://mhabtest.streamlit.app](https://mhabtest.streamlit.app)

A full-stack analytics prototype demonstrating how data-driven experimentation can optimize help-seeking behavior on digital mental health platforms like [mindline.sg](https://mindline.sg).

---

## Why This Project?

Digital mental health platforms face a critical challenge: **how do we encourage users to seek help when they need it?** This prototype explores whether conversational tone impacts conversion rates in a mental health triage flow.

**The Hypothesis:** Users in distress may respond better to empathetic, validating language than clinical, symptom-focused language when deciding whether to connect with a counselor.

This directly relates to mindline.sg's mission of destigmatizing help-seeking and directing individuals to appropriate mental health support.

---

## Skills Demonstrated

| Skill Area | Implementation |
|------------|----------------|
| **A/B Testing & Experimentation** | Designed and implemented controlled experiment with 50/50 randomization, crisis exclusion protocol, and statistical significance testing |
| **Statistical Analysis** | Two-proportion z-test, 95% confidence intervals (Wilson score), power analysis for sample size determination |
| **User Behavior Analytics** | Conversion funnel analysis, time-to-decision tracking, segment analysis by severity |
| **Data Engineering** | SQLite event schema with 12 fields, efficient logging pipeline, data validation |
| **NLP & Sentiment Analysis** | VADER sentiment scoring, severity classification, crisis keyword detection |
| **Data Visualization** | Interactive Plotly dashboards with KPIs, confidence interval charts, funnels, scatter plots |
| **Marketing Analytics** | UTM parameter tracking, referral source attribution, channel performance analysis |
| **Python & SQL** | Clean modular code, parameterized queries, comprehensive test suite |
| **Mental Health Domain Awareness** | Safety-first crisis protocol, ethical experiment design, Singapore-specific resources |
| **Research Methodology** | Experimental design, power analysis, effect size interpretation, actionable recommendations |

---

## Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate mock data (500 interactions)
python scripts/generate_mock_data.py

# Run the app
streamlit run app.py
```

Open http://localhost:8501

---

## The Experiment

### Research Question

> Does an empathetic conversational tone lead to higher conversion rates (connecting with a counselor) compared to a clinical tone, particularly among users with moderate-to-severe distress?

### Experimental Design

| Component | Details |
|-----------|---------|
| **Variants** | A (Clinical) vs B (Empathetic) |
| **Randomization** | 50/50 split at session level |
| **Primary Metric** | Conversion rate (click "Connect with Counselor") |
| **Secondary Metrics** | Time-to-decision, segment performance by severity |
| **Exclusion Criteria** | Crisis-flagged users bypass experiment for safety |

### Variant Examples

**Variant A (Clinical):**
> "Symptom assessment: Moderate anxiety indicators detected. Recommendation: Schedule consultation with mental health professional."

**Variant B (Empathetic):**
> "It sounds like you're carrying a heavy load right now. These feelings are valid, and it takes courage to acknowledge them. Would you be open to speaking with someone who can help?"

### Sample Size Calculation

With a baseline conversion rate of 15% and a minimum detectable effect of 5 percentage points:
- **Power:** 80%
- **Significance level:** α = 0.05
- **Required sample:** ~550 users per variant (1,100 total)

---

## Features

### 💬 Triage Chat Interface

The chat interface collects user input, analyzes sentiment, assigns variants, and displays appropriate responses.

**Key components:**
- **VADER Sentiment Analysis:** Calibrated for informal, emotional text common in mental health contexts
- **Severity Classification:** Maps sentiment scores to mild/moderate/severe buckets
- **A/B Variant Assignment:** Random assignment with session persistence
- **Response Generation:** Tone-appropriate responses based on variant and severity

### 📊 Analytics Dashboard

Interactive dashboard for monitoring experiment performance and deriving insights.

**Visualizations include:**

1. **KPI Header:** Total sessions, overall conversion rate, per-variant rates, lift calculation
2. **A/B Test Results Panel:**
   - Statistical significance indicator (p-value < 0.05)
   - 95% confidence intervals for each variant
   - Clear recommendation based on results
3. **Conversion Funnel:** Sessions → Experiment-eligible → Converted
4. **Segment Analysis:** Conversion by severity bucket (grouped bar chart)
5. **Sentiment vs Conversion:** Scatter plot exploring sentiment-conversion relationship
6. **Time to Decision:** Box plots comparing decision latency between variants
7. **Marketing Attribution:** Conversion rates by UTM source/channel

### 🛡️ Safety & Ethics

Mental health applications require special consideration. This prototype implements:

**Crisis Detection Protocol:**
- Keyword matching for self-harm/suicide-related phrases
- Extreme negative sentiment threshold (< -0.8)
- Immediate display of crisis resources (bypasses experiment)
- Singapore-specific hotlines: SOS (1-767), IMH (6389-2222)

**Ethical Experimentation:**
- Both variants provide valid pathways to support (no harmful control)
- Auto-stop capability if one variant shows significantly worse outcomes
- Transparent about experiment participation
- Data minimization: only store what's necessary for analysis

---

## Technical Architecture

### Event Schema

Every interaction is logged with 12 fields for comprehensive analysis:

| Field | Type | Purpose |
|-------|------|---------|
| `session_id` | TEXT | Unique session identifier |
| `timestamp` | DATETIME | Event timing |
| `input_text` | TEXT | User's message |
| `sentiment_score` | REAL | VADER compound score (-1 to 1) |
| `severity_bucket` | TEXT | mild/moderate/severe |
| `assigned_variant` | TEXT | A_CLINICAL or B_EMPATHETIC |
| `response_time_ms` | INTEGER | System response latency |
| `time_to_decision_ms` | INTEGER | User's decision latency |
| `session_depth` | INTEGER | Interaction count |
| `converted` | BOOLEAN | Clicked "Connect with Counselor" |
| `experiment_excluded` | BOOLEAN | Crisis protocol triggered |
| `referral_source` | TEXT | UTM source attribution |

### Project Structure

```
├── app.py                    # Streamlit entry point (3 pages)
├── src/
│   ├── database.py           # SQLite schema, logging, queries
│   ├── experiment.py         # NLP, variants, crisis detection
│   └── analytics.py          # Statistical calculations
├── scripts/
│   └── generate_mock_data.py # Realistic data simulation
├── tests/
│   └── test_experiment.py    # 8 unit tests
└── data/
    └── experiment.db         # SQLite database
```

### Statistical Methods

| Analysis | Method | Implementation |
|----------|--------|----------------|
| Significance testing | Two-proportion z-test | `statsmodels.stats.proportion.proportions_ztest` |
| Confidence intervals | Wilson score interval | `statsmodels.stats.proportion.proportion_confint` |
| Sample size calculation | Power analysis | Pre-computed based on baseline conversion |

**Why Wilson score intervals?** Traditional normal approximation intervals can give nonsensical results (< 0 or > 1) when proportions are near 0 or 1. Wilson score intervals remain valid across the entire [0, 1] range.

---

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | Streamlit | Rapid prototyping, native Python, built-in state management |
| **NLP** | VADER Sentiment | Optimized for social media/informal text, handles emoticons and emphasis |
| **Database** | SQLite | Portable, allows SQL query demonstrations, zero setup |
| **Statistics** | scipy, statsmodels | Industry-standard, peer-reviewed implementations |
| **Visualization** | Plotly | Interactive, publication-quality charts |

---

## Testing

The test suite validates core experiment logic:

```bash
python tests/test_experiment.py
```

**Test coverage:**
- Sentiment analysis (positive/negative/neutral)
- Severity bucketing (boundary conditions)
- Crisis detection (keyword matching + sentiment threshold)
- Variant assignment (randomization distribution)
- Full input analysis (normal and crisis flows)
- Response template completeness

---

## Insights from Mock Data

The generated dataset simulates 500 interactions with realistic patterns:

**Key findings:**
- Variant B (Empathetic) shows **+46% lift** in conversion rate
- Effect is **strongest among severe cases** (~60% improvement)
- Results are statistically significant (p < 0.05)
- 95% CIs: Variant A [14%, 22%], Variant B [21%, 33%] — no overlap

**Recommended action:** Roll out empathetic responses, with priority for moderate-to-severe users.

---

## Future Enhancements

For production deployment, consider:

- **Database:** PostgreSQL for scalability
- **Event tracking:** Segment or Amplitude for rich user journeys
- **Guardrail metrics:** Automated experiment stopping rules
- **Multi-arm bandits:** Dynamic traffic allocation as results emerge
- **Cohort analysis:** Long-term retention impact of variants
- **Qualitative feedback:** Post-conversion surveys

---

## Author

Built by Raymond Luo as a demonstration of data analytics capabilities for digital mental health product optimization.

**Contact:** [Your contact method]

---

*This prototype demonstrates the intersection of product analytics, statistical rigor, and domain-specific safety considerations essential for effective digital health platforms.*
