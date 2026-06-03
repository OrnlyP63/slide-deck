# Zero-Downtime Migration from Monolith to Microservices: 18-Month Roadmap
<!-- author: Platform Engineering Team -->
<!-- theme: tech -->

### Today's agenda
<!-- agenda -->
1. Current state: the monolith problem
2. Migration strategy: strangler fig pattern
3. Expected outcomes and metrics
4. Investment case

## 1. Current State

### Ten-year-old monolith deploys once per quarter and blocks 12 teams from shipping independently
**Situation:** 2.4M LOC Django monolith powers core product; 180 engineers across 12 product teams all commit to single codebase and share one deployment pipeline
**Complication:** Mean time to deploy increased from 2h to 14h over 3 years; quarterly release cycle blocks feature velocity; single failure domain caused 3 P0 outages (total 18h downtime) in 2025
**Resolution:** Strangler fig pattern with domain-driven service extraction reduces deployment frequency to daily per team, MTTR from 4h to 12min, and enables independent scaling of high-load domains
> Source: Internal engineering metrics 2023–2025; DORA State of DevOps Report 2025

### Four compounding problems make the current architecture unsustainable at 2026 scale
- Database: single PostgreSQL instance at 94% capacity; 18-month runway before hard limit
- Build time: 47-minute CI pipeline blocks developers 6× per day average
- On-call burden: any failure pages all 180 engineers regardless of domain
- Hiring: senior engineers declining offers citing monolith as culture signal
> Source: Internal ops metrics; Engineering survey Q4 2025; Offer decline exit interviews

## 2. Migration Strategy

### Strangler fig pattern extracts services at domain boundaries without rewriting or downtime
![Architecture Diagram](Before/after: monolith with API gateway in front; after shows 6 extracted microservices — Auth, Payments, Notifications, Search, Recommendations, Analytics — with strangler fig routing layer; monolith shrinks as services extract)
> Source: Internal architecture proposal v4; Martin Fowler Strangler Fig Application pattern

### Six domains extracted in priority order by blast radius and team ownership clarity
#### Phase 1: Low Risk (Q1–Q2 2026)
- Auth service: clear boundary, stateless, team already owns it
- Notifications service: no shared database tables, event-driven
- Analytics pipeline: read-only, tolerates eventual consistency
#### Phase 2: High Value (Q3–Q4 2026)
- Payments service: highest regulatory and audit pressure
- Search service: highest load, needs independent scaling
- Recommendations: ML model serving, separate release cadence needed

## 3. Outcomes

### Migration delivers step-change improvement on all four DORA metrics
| DORA Metric | Current | Target | Change |
|---|---|---|---|
| Deployment frequency | 1×/quarter | Daily per team | 48× |
| Lead time for changes | 14 days | 2 days | 7× faster |
| MTTR | 4 hours | 12 minutes | 20× faster |
| Change failure rate | 8.3% | <1% | 8× improvement |
> Source: DORA metrics baseline 2025; Target based on Shopify, Monzo case studies

### The greatest risk is not migrating — it's continuing to build on a crumbling foundation
> "The most dangerous kind of waste is the waste we do not recognise."
> — Shigeo Shingo

### 18-month roadmap: three phases, four dedicated engineers, zero production incidents
1. Q1 2026: Team onboarding, tooling setup, Auth service extraction complete
2. Q2–Q3 2026: Notifications, Analytics, Payments extracted; CI time drops below 15 min
3. Q4 2026: Search and Recommendations complete; all 12 teams on independent pipelines
> Source: Internal project plan; Engineering leadership sign-off December 2025

### Invest $1.8M, recover $12M — questions welcome
<!-- closing -->
- platform-engineering@company.com
- https://github.com/OrnlyP63/slide-deck
<!-- notes: CTO worried about team distraction during migration — emphasise 4 dedicated engineers don't pull from product teams -->
