# Findings & Decisions

## Requirements
From PRD v1.1:
- Full-stack analytics prototype (App + Logging + Analytics)
- A/B test comparing Clinical (A) vs Empathetic (B) chatbot personas
- Measure conversion rate (click on "Connect with Counselor")
- Sentiment analysis using NLP (TextBlob/VADER)
- Severity bucketing (mild/moderate/severe)
- Crisis detection bypass for high-risk users
- Dashboard with funnel, CI-based A/B results, segment analysis
- 500 simulated interactions for demo

## Research Findings

### Sentiment Analysis Libraries
- **VADER (Valence Aware Dictionary and sEntiment Reasoner)**
  - Specifically tuned for social media and informal text
  - Handles emoticons, slang, emphasis (ALL CAPS)
  - Returns compound score (-1 to +1)
  - `pip install vaderSentiment`
- **TextBlob**
  - More general-purpose
  - Returns polarity (-1 to +1) and subjectivity (0 to 1)
  - Better for formal text
- **Decision:** Use VADER—mental health input is often informal/emotional

### Statistical Testing for A/B
- **Two-proportion z-test** for comparing conversion rates
- `scipy.stats.proportions_ztest` for p-value
- `statsmodels.stats.proportion.proportion_confint` for CIs
- Power analysis: `statsmodels.stats.power.NormalIndPower`

### Streamlit Patterns
- `st.session_state` for maintaining state across reruns
- `st.tabs()` for app/dashboard separation
- `st.metric()` for KPI display with delta
- `st.plotly_chart()` for interactive visualizations

### Crisis Keywords (Mental Health)
Based on industry standards:
- "hurt myself", "end it", "suicide", "kill myself"
- "don't want to live", "no reason to live", "better off dead"
- "can't go on", "want to die"

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| VADER over TextBlob | Better for informal emotional text |
| SQLite for storage | Can demo SQL queries; more impressive than CSV |
| Plotly for viz | Interactive, native Streamlit support |
| UUID4 for session_id | No collision risk, industry standard |
| statsmodels for stats | Mature library, proper CI implementation |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
- VADER docs: https://github.com/cjhutto/vaderSentiment
- Streamlit docs: https://docs.streamlit.io/
- statsmodels proportion test: https://www.statsmodels.org/stable/stats.html
- mindline.sg (reference): https://mindline.sg/

## Visual/Browser Findings
- [To be updated after researching mindline.sg interface]

---
*Update this file after every 2 view/browser/search operations*
