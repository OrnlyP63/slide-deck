# Zero-Downtime Migration from Monolith to Microservices: 18-Month Roadmap
<!-- author: Platform Engineering Team -->
<!-- theme: tech -->

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

## 3. Expected Outcomes

### Migration delivers daily deployments per team and 95% reduction in incident blast radius
- Deployment frequency: 1× per quarter → daily per team (12 independent pipelines)
- Lead time for changes: 14 days → 2 days (target: same-day for minor features)
- MTTR: 4 hours → 12 minutes (isolated failure domains, faster rollback)
- Change failure rate: 8.3% → target <1% (smaller blast radius per deploy)
> Source: DORA metrics baseline 2025; Target based on comparable migrations at Shopify, Monzo

### 18-month investment of 4 dedicated engineers delivers $12M NPV through velocity gains
- 4 dedicated platform engineers for 18 months ($1.8M fully loaded cost)
- $4.2M value: 40% faster feature delivery, measured against delayed roadmap items
- $5.1M value: avoided downtime cost at $85K/hour × projected outage reduction
- $2.7M value: senior engineer retention premium (3 likely departures avoided at $900K each)
> Source: Internal financial model; Engineering productivity benchmarks; Retention cost analysis
<!-- notes: CTO worried about team distraction during migration — emphasise 4 dedicated engineers don't pull from product teams -->
