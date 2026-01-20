# Mind-Log Experimentation Lab — Interview Demo Script

**Duration:** 5-7 minutes (expandable based on questions)
**Audience:** MOHT hiring panel for Data Analyst (mindline.sg)

---

## Pre-Demo Setup

### Option 1: Streamlit Cloud (Recommended)

Open **https://mhabtest.streamlit.app** in browser. Have **📊 Analytics Dashboard** tab ready.

*No setup required. App auto-generates fresh mock data on startup.*

### Option 2: Local (Fallback)

```bash
cd /path/to/Experiment_Lab
source .venv/bin/activate
python scripts/generate_mock_data.py  # If needed
streamlit run app.py
```

Open http://localhost:8501 in browser.

---

## Part 1: Introduction (30 seconds)

**Say:**
> "I built this prototype to demonstrate how I'd approach A/B testing and product analytics at mindline.sg. It's a mental health triage chatbot that runs a controlled experiment comparing two conversational styles."

**Show:** About page (ℹ️ tab)

**Key points to mention:**
- Full-stack: Product (app) + Data Engineering (logging) + Analytics (dashboard)
- Directly relevant to mindline.sg's triage flow
- Built with safety-first approach

---

## Part 2: The Experiment Design (1 minute)

**Say:**
> "The hypothesis is simple: does an empathetic tone lead to more users seeking help compared to a clinical tone?"

**Explain the variants:**

| Variant | Style | Example |
|---------|-------|---------|
| A (Control) | Clinical | "Symptom noted. Severity: Moderate. Recommended action: Consult a specialist." |
| B (Test) | Empathetic | "It sounds like you're carrying a heavy load. Would you be open to speaking with someone who can help?" |

**Say:**
> "The primary metric is conversion rate — whether users click 'Connect with Counselor'. Secondary metrics include time-to-decision and sentiment correlation."

**If asked about sample size:**
> "I did a power analysis: with 15% baseline conversion and 5 percentage point MDE at 80% power, we need about 550 users per variant — roughly 1,100 total."

---

## Part 3: Live Demo — Triage Chat (2 minutes)

### Demo 3a: Normal Flow

**Navigate to:** 💬 Triage Chat

**Type:** `I've been feeling really stressed and anxious about work lately`

**Click:** Share

**Point out:**
1. **Sidebar debug info** — Shows sentiment score (~-0.3), severity (moderate), and assigned variant
2. **Response text** — Either clinical or empathetic based on random assignment
3. **Conversion button** — "Connect with Counselor" is our primary metric

**Say:**
> "Every interaction is logged to SQLite with 12 fields including sentiment score, severity bucket, variant assignment, and timestamps. This lets us analyze not just *whether* users convert, but *how long* they take to decide."

**Click:** "Connect with Counselor" to show conversion flow

### Demo 3b: Crisis Detection (Important!)

**Click:** "Start New Session"

**Type:** `I want to hurt myself`

**Click:** Share

**Point out:**
- Red alert banner appears
- Crisis resources displayed (SOS hotline, IMH)
- **No variant assigned** — user is excluded from experiment

**Say:**
> "This is critical for mental health applications. Users in acute distress bypass the experiment entirely and see crisis resources immediately. We detect crisis through keyword matching AND extreme negative sentiment below -0.8. These sessions are logged as 'experiment_excluded' so they don't contaminate our A/B results."

**If asked about ethics:**
> "Both variants provide valid pathways to support — there's no placebo that withholds help. And I'd implement auto-stop rules in production: if either variant shows significantly worse outcomes, the experiment halts."

---

## Part 4: Analytics Dashboard (2-3 minutes)

**Navigate to:** 📊 Analytics Dashboard

### 4a: KPI Header

**Point out the 4 metrics:**
- Total Sessions: 500
- Overall Conversion Rate: ~22%
- Variant A: ~18%
- Variant B: ~27% with **+46% lift** shown in green

**Say:**
> "At a glance, Variant B is outperforming. But we need to check if this is statistically significant."

### 4b: A/B Test Results Panel

**Point out:**
1. **Green banner**: "Statistically Significant (p = 0.02)"
2. **Recommendation**: "Recommend rolling out Empathetic responses"
3. **Confidence interval chart**: Error bars don't overlap
4. **Summary table**: Sessions, conversions, rates, 95% CIs

**Say:**
> "I use Wilson score intervals for the confidence intervals — they're more accurate than normal approximation when proportions are near 0 or 1. The two-proportion z-test gives us p = 0.02, which is below our 0.05 threshold."

**If asked why CIs matter:**
> "P-values only tell you if there's a difference. Confidence intervals tell you the likely *size* of that difference. Here we're 95% confident Variant B's true conversion rate is between 21% and 33%. That's actionable information for product decisions."

### 4c: Funnel Visualization

**Point out:**
- 500 total sessions → 488 experiment sessions → ~110 conversions
- Caption shows 12 sessions excluded (crisis protocol)

**Say:**
> "The funnel shows our drop-off. 2.4% of sessions triggered crisis protocol and were appropriately excluded."

### 4d: Conversion by Severity (Key Insight!)

**Point out the grouped bar chart:**
- Variant B beats Variant A across ALL severity levels
- The gap is **largest for severe cases** (~35% vs ~22%)

**Say:**
> "This is the key insight: empathetic tone matters most when users are in the most distress. For severe cases, Variant B has nearly 60% higher conversion. This makes intuitive sense — when someone is struggling, they need to feel heard, not just assessed."

**If asked about implications:**
> "If I were at mindline.sg, I'd recommend: roll out empathetic responses for moderate and severe users immediately. For mild cases, we could continue testing or use clinical tone since the difference is smaller."

### 4e: Supporting Visualizations

**Briefly mention:**
- **Sentiment vs Conversion**: Shows conversion happens across sentiment range, but more conversions cluster in negative sentiment (where empathetic tone helps most)
- **Time to Decision**: Box plots show similar decision times between variants
- **Marketing Attribution**: Shows which channels drive traffic and their conversion rates

---

## Part 5: Technical Deep-Dive (If Asked)

### Data Pipeline

**Say:**
> "Every interaction logs 12 fields to SQLite: session_id, timestamp, input_text, sentiment_score, severity_bucket, assigned_variant, response_time_ms, time_to_decision_ms, session_depth, converted, experiment_excluded, and referral_source."

### NLP Choice

**If asked why VADER:**
> "VADER is specifically tuned for social media and informal text. Mental health input is often emotional with emphasis, slang, and emoticons — VADER handles these better than TextBlob which is more general-purpose."

### Statistical Methods

**If asked about the z-test:**
> "It's a two-proportion z-test from statsmodels. We're testing if Variant B's proportion is significantly *greater* than A's, so it's a one-tailed test. The z-statistic is about 2.1, giving us p ≈ 0.02."

### Tech Stack

> "Streamlit for rapid prototyping, SQLite for the database so I can demo actual SQL queries, VADER for sentiment, scipy and statsmodels for statistics, and Plotly for interactive visualizations."

---

## Part 6: Closing (30 seconds)

**Say:**
> "This prototype demonstrates the full analytics workflow I'd bring to mindline.sg: from experiment design and data instrumentation, through statistical analysis, to actionable product recommendations. I'm excited about the opportunity to apply this approach to real user data and help improve mental health outcomes."

**Offer:**
> "I'm happy to dive deeper into any part — the statistical methodology, the code architecture, or how I'd extend this for production."

---

## Anticipated Questions & Answers

### Q: How would you handle multiple testing / experiment interactions?
> "In production with multiple concurrent experiments, I'd use a holdout group and apply Bonferroni correction or control FDR. For sequential testing, I'd consider using Bayesian methods or always-valid p-values."

### Q: What if the results were NOT significant?
> "I'd check if we have enough sample size first. If yes, then no significant difference is also a valid finding — it means tone doesn't matter for this metric, and we could optimize other factors. I'd also segment the data to see if there are effects for specific user groups."

### Q: How would you productionize this?
> "I'd move to PostgreSQL, add proper event tracking (like Segment or Amplitude), set up automated daily reports, implement guardrail metrics to auto-stop harmful experiments, and build alerting for anomalies."

### Q: What other experiments would you run on mindline.sg?
> "I'd test: (1) the self-assessment flow — can we reduce drop-off? (2) service recommendation algorithm — does personalization improve uptake? (3) chatbot engagement — what drives return visits? (4) community forum — what content drives meaningful engagement vs. lurking?"

### Q: How do you handle privacy in mental health data?
> "Minimal data retention, anonymization of text inputs, no PII in logs, clear data governance policies. For this prototype, I only store sentiment scores in production — raw text would be discarded after processing."

---

## Backup: If Technical Issues

If local app doesn't load:
1. Switch to **https://mhabtest.streamlit.app** (cloud deployment)
2. If cloud also fails: regenerate data locally with `python scripts/generate_mock_data.py`
3. Last resort: show code and PRD document

If asked to show code:
- `src/experiment.py` — NLP and variant logic
- `src/analytics.py` — Statistical calculations
- `scripts/generate_mock_data.py` — How I simulated realistic data
- **GitHub:** https://github.com/rayluo88/Mental-Health-ABtest
