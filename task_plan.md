# Task Plan: Mind-Log Experimentation Lab

## Goal
Build a full-stack analytics prototype demonstrating A/B testing, NLP sentiment analysis, and product analytics dashboards for mental health triage optimization—to showcase senior-level data analyst capabilities for the MOHT interview.

## Current Phase
**PROJECT COMPLETE** ✓

### Deliverables
- **Live Demo:** https://mhabtest.streamlit.app
- **GitHub Repo:** https://github.com/rayluo88/Mental-Health-ABtest
- **Local App:** `streamlit run app.py`

## Phases

### Phase 1: Project Setup & Core Infrastructure
- [x] Initialize project structure (directories, requirements.txt)
- [x] Set up Streamlit app skeleton with basic routing
- [x] Create SQLite database schema matching event schema in PRD
- [x] Implement `log_event()` function for data capture
- **Status:** complete
- **Est. Time:** 1-2 hours
- **Actual Time:** ~30 mins

### Phase 2: NLP & Experiment Logic
- [x] Implement sentiment analysis (VADER)
- [x] Build severity bucket classifier (mild/moderate/severe)
- [x] Create A/B variant randomizer (50/50 split)
- [x] Implement crisis detection protocol (bypass experiment for high-risk users)
- [x] Write variant response templates (Clinical vs Empathetic)
- [x] Integrate experiment logic into Streamlit app
- **Status:** complete
- **Est. Time:** 2-3 hours
- **Actual Time:** ~20 mins

### Phase 3: User Interface (Streamlit)
- [x] Build landing page with text input
- [x] Display appropriate variant response based on assignment
- [x] Add [Connect with Counselor] conversion button
- [x] Implement crisis resource display for flagged users
- [x] Track `time_to_decision_ms` for user actions
- **Status:** complete (merged with Phase 2)
- **Est. Time:** 2 hours
- **Actual Time:** included in Phase 2

### Phase 4: Data Generation Script
- [x] Create `generate_mock_data.py` to simulate 500 interactions
- [x] Inject realistic bias (higher conversion for Variant B in severe cases)
- [x] Include varied sentiment distributions
- [x] Add UTM parameter simulation for referral_source
- [x] Validate generated data matches schema
- **Status:** complete
- **Est. Time:** 1-2 hours
- **Actual Time:** ~15 mins

### Phase 5: Analytics Dashboard
- [x] Build funnel visualization (Sessions → Valid Inputs → Conversions)
- [x] Create A/B test results panel with 95% confidence intervals
- [x] Implement p-value calculation with decision logic
- [x] Add sentiment correlation scatter plot
- [x] Build segment analysis by severity bucket
- [x] Add time-to-decision distribution plot
- [x] Add marketing attribution chart
- **Status:** complete
- **Est. Time:** 3-4 hours
- **Actual Time:** ~30 mins

### Phase 6: Testing & Polish
- [x] Test full user flow end-to-end
- [x] Verify crisis detection works correctly (8 unit tests)
- [x] Validate statistical calculations
- [x] Add error handling
- [x] Write README with setup instructions
- **Status:** complete
- **Est. Time:** 1-2 hours
- **Actual Time:** ~10 mins

### Phase 7: Demo Preparation
- [x] Prepare talking points for interview demo
- [x] Document key decisions and trade-offs
- [x] Create 2-minute demo script
- [x] Test deployment (local)
- **Status:** complete
- **Est. Time:** 1 hour
- **Actual Time:** ~5 mins

### Phase 8: GitHub & Cloud Deployment
- [x] Initialize git repository
- [x] Push to GitHub
- [x] Add auto-data-generation for cloud deployment
- [x] Create .streamlit/config.toml
- [x] Deploy to Streamlit Cloud
- [x] Configure custom subdomain (mhabtest.streamlit.app)
- [x] Enhance README for interviewers
- **Status:** complete
- **Completed:** 2026-01-17

## Key Questions
1. Use VADER or TextBlob for sentiment? (VADER better for social media text)
2. SQLite or CSV for MVP storage? (SQLite for SQL demo capability)
3. Deploy to Streamlit Cloud or run locally? (Local safer, but Cloud more impressive)
4. How to handle session persistence across page reloads?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Streamlit for UI | Rapid prototyping, native Python, built-in Plotly support |
| SQLite over CSV | Can demo actual SQL queries in interview |
| VADER for sentiment | Better for informal/emotional text than TextBlob |
| 95% CI over just p-value | Shows statistical maturity beyond basic hypothesis testing |
| Crisis bypass protocol | Domain awareness—mental health safety is non-negotiable |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- Total estimated time: 12-16 hours across all phases
- Priority: Phases 1-5 are MVP; Phases 6-7 are polish
- Interview is next week—Phase 5 (Dashboard) is most important for demo
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions
