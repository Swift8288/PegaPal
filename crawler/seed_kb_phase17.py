"""
Curated Pega Knowledge Base — Phase 17 (Industry Frameworks, Methodology, Versioning & Multi-Tenancy)
Run: python -m crawler.seed_kb_phase17
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE17 = [
    {
        "title": "Pega Express Methodology — Low-Code Development Approach",
        "url": "https://docs.pega.com/bundle/pega_express",
        "content": """
# Pega Express Methodology — Low-Code Development Approach

## What is Pega Express?

Pega Express is a rapid, low-code delivery methodology that emphasizes speed, collaboration, and iterative delivery. Designed for organizations seeking to launch Pega applications faster than traditional waterfall approaches, Express combines agile principles with Pega's low-code capabilities.

**Key Characteristics:**
- Delivers working software in 2-4 week iterations
- Reduces development overhead through model-driven design
- Empowers business analysts to participate in development
- Minimizes custom Java code (targets <10% of implementation)
- Focuses on re-use of Pega frameworks and out-of-box features

## Directly Capture Objectives (DCO)

DCO is the Express cornerstone—capturing business requirements directly into executable Pega models without lengthy documentation phases.

**DCO Process:**
1. Stakeholder workshops define business objectives
2. Business analysts capture objectives in Pega Designer Studio
3. Objectives map to case types, stages, and decision flows
4. Immediate feedback loop validates assumptions
5. Executable requirements eliminate translation gaps

**Debugging DCO Issues:**
- If objectives don't translate to case logic, review stage conditions and guardrails
- Verify decision trees map correctly to case routing
- Check for orphaned objectives (defined but unused in case design)

## Microjourney-Based Design

Express decomposes applications into "microjourneys"—small, focused user interactions that map to specific business outcomes.

**Microjourney Structure:**
- One microjourney = one case or sub-case
- Each journey has clear entry/exit points
- Bounded scope prevents scope creep
- Easier to test, debug, and enhance incrementally

**Example:** A "Quick Quote" microjourney in insurance handles: customer input → risk assessment → quote generation → decision. This completes in one iteration.

## Pega Express Guardrails

Guardrails are best-practice constraints enforced to keep projects lean and predictable:

1. **Scope guardrails** – No custom frameworks; use Pega Foundation
2. **Complexity guardrails** – Limit decision tree depth; use decision tables for >5 branches
3. **Integration guardrails** – Leverage REST/JSON; avoid custom adapters
4. **Code guardrails** – Max 10% custom Java; prefer rules-based logic
5. **Team guardrails** – Max 4-6 core delivery team members; minimize dependencies

**Violating guardrails increases risk:** Projects that ignore these controls experience scope creep, extended timelines, and unpredictable costs.

## When to Use Express vs. Traditional

| Aspect | Express | Traditional |
|--------|---------|-------------|
| Timeline | 2-4 week sprints | 6+ month phases |
| Change tolerance | High (iterate frequently) | Low (costly changes) |
| Stakeholder involvement | Continuous | Milestone-based |
| Custom code | <10% | Often >30% |
| Best for | Greenfield, moderate complexity | Complex, highly regulated, high custom needs |

## Express Delivery Lifecycle

1. **Assess (Week 1):** Workshops, objective capture, architecture review
2. **Construct (Weeks 2-4):** Build case types, rules, integrations; demo weekly
3. **Validate (Week 5):** User testing, refinement
4. **Release (Week 6):** Production deployment, monitoring

Each iteration repeats this cycle, adding features incrementally.

## Common Mistakes with Express Methodology

**Mistake 1: Treating Express like traditional waterfall**
- Wrong: Define all requirements upfront; build for 3 months
- Right: Iterate, gather feedback, adjust course

**Mistake 2: Ignoring guardrails as "guidelines"**
- Creates technical debt; later iterations stall
- Solution: Enforce guardrails in reviews; escalate violations

**Mistake 3: Insufficient stakeholder engagement**
- Leads to rework and scope creep
- Solution: Schedule weekly demos; engage decision makers, not proxies

**Mistake 4: Attempting custom frameworks**
- Pega Foundation is purpose-built for Express; reinventing it adds weeks
- Solution: Use Foundation; customize at the feature level, not foundation level

## Express vs. Scrum/Agile Comparison

Express is **not** Scrum—it's Pega-specific methodology layered on agile ceremonies:

**Similarities:** Sprints, user stories, retrospectives, iterative delivery
**Differences:**
- Express uses Pega's case management model (not story points)
- Emphasis on reusable rules, not custom code
- Structured decision flows (not ad-hoc user story splitting)
- Guardrail enforcement (not arbitrary team decisions)

**Integration:** Many teams run Scrum ceremonies around Express iterations. Use Express for **what** to build, Scrum for **how** to organize the team.

## Debugging Tips

**Symptom:** Application feels "too custom" for Express
- Review decision trees for unnecessary complexity
- Consolidate similar case types; avoid one-off variants
- Check if rules are parameterized (configurable vs. hardcoded)

**Symptom:** Iterations extend beyond 4 weeks
- Reassess scope—microjourneys should be smaller
- Identify blockers (unclear requirements, external dependencies, team skill gaps)
- Consider parallel workstreams if feasible

**Symptom:** Stakeholder engagement drops after first iteration
- Schedule demos at executive level, not just team level
- Show tangible progress (working features, not just architecture)
- Adjust sprints based on feedback; ignore feedback = disengagement
"""
    },
    {
        "title": "Pega Infinity Version Comparison — 7.x vs 8.x vs 23.x vs 24.x",
        "url": "https://docs.pega.com/bundle/pega_infinity_roadmap",
        "content": """
# Pega Infinity Version Comparison — 7.x vs 8.x vs 23.x vs 24.x

## Pega Version Evolution Timeline

| Version | Release | Key Theme | Support Status |
|---------|---------|-----------|-----------------|
| Pega 7.x | 2013–2021 | Foundation/Stability | Maintenance only |
| Pega 8.x | 2021–2022 | Modernization | Extended support |
| Pega 23 (Infinity) | 2023 | Cloud-native, GenAI | Active |
| Pega 24 | 2024 | AI/ML, Performance | Current |

## Pega 7.x Features & Limitations

**Strengths:**
- Battle-tested for 8+ years; predictable behavior
- Extensive documentation and community knowledge base
- Works with legacy integrations (SOAP, old adapters)
- Lower resource requirements than modern versions

**Limitations:**
- No GenAI capabilities; rule-based decision only
- Tomcat bundled separately (complex installation)
- Limited cloud-native features; not containerized by default
- Slower rule engine; performance degrades at scale (>500K cases/day)

**When to stay on Pega 7:** Legacy systems; organizations without AI/ML roadmaps; deeply customized implementations where migration cost exceeds benefit.

## Pega 8 Changes — Modernization Push

**Major Improvements:**

1. **Constellation Introduction** – New responsive UI framework (but not default; 7.x UI still available)
2. **Embedded Tomcat** – Simplified installation; no external app server needed
3. **Decision Engine Overhaul** – Faster rule evaluation; reduced latency
4. **Improved Containerization** – Better Docker/Kubernetes support (foundation for cloud)
5. **Enhanced Logging** – Structured logs; easier integration with observability tools

**Breaking Changes:**
- Some custom UI extensions require Constellation rewrite
- SOAP adapters deprecated; REST now standard
- Rule caching behavior changed; old optimization patterns no longer work

**Performance Gains:** 20-30% improvement in rule evaluation on typical workloads.

## Pega 23 (Infinity) — Cloud-Native, GenAI Launch

**Transformational Features:**

1. **Constellation GA (General Availability)** – Default UI; fully responsive; accessibility built-in
2. **GenAI Integration** – Native LLM connectors; prompt management; AI-assisted case routing
3. **Cloud-First Architecture** – Designed for multi-cloud (AWS, Azure, GCP); minimal on-prem friction
4. **Embedded Analytics** – Real-time dashboards; Pega's own analytics engine (not external BI)
5. **Process Optimization** – Automated process mining; bottleneck detection

**Breaking Changes:**
- Pega 7-style custom CSS no longer compatible with Constellation
- Classic UI deprecated (available in compatibility mode, not recommended)
- Some rule types redesigned for performance (backward-compatible but behavior may differ)

**Performance:** 40-50% faster than Pega 8; handles 2M+ cases/day at scale.

## Pega 24 — Latest, Production-Ready

**New Capabilities:**

1. **Advanced GenAI** – RAG (Retrieval-Augmented Generation) for case-specific AI context; fine-tuning support
2. **Expanded AI Services** – Native integrations: OpenAI, Azure OpenAI, Anthropic Claude, open-source LLMs
3. **Native Graph Database** – Knowledge graphs for entity relationships; improves decision accuracy
4. **Enhanced RPA** – Robotic Process Automation tightly integrated; lower code for automation
5. **Predictive Decisioning** – ML models for propensity scoring, churn prevention, next-best-action

**Performance Enhancements:**
- 15-20% latency improvement over Pega 23
- Horizontal scaling simplified; distributed decision engine
- Memory optimization; smaller footprint for edge deployments

**Recommended for:** New greenfield projects; organizations with AI/ML roadmaps; SaaS/cloud-first strategies.

## Deprecated Features by Version

**Pega 7 → 8:**
- Custom JSF faces (use Constellation)
- SOAP adapters (use REST)
- Deprecated rule types: `Activity`, `HTML`, `Form` (use modern alternatives)

**Pega 8 → 23:**
- Classic UI (use Constellation)
- Offline processing (no longer supported)
- Some deprecated rule optimization techniques

**Pega 23 → 24:**
- Legacy analytics dashboards (use embedded analytics)
- Some older LLM provider SDKs (standardized on OpenAI-compatible APIs)

## Migration Considerations

**Pega 7 → 8:** 4-6 month effort for mid-sized applications; Constellation migration is 80% of cost
**Pega 8 → 23:** 2-3 months; most code compatible; focus on UI/GenAI integration testing
**Pega 23 → 24:** 1-2 months; mostly patch-level upgrade path; new features are additive

**Strategy:** Plan for version hops (skip 8, go to 23 directly if greenfield). Migration between adjacent versions smoother.

## Version-Specific Debugging Tips

**Pega 7:**
- Use older Activity rules with caution; many have O(n²) performance issues
- Monitor deprecated rule types in rule integrity checkers
- Classic SOAP adapters leak connections under load; migrate to REST

**Pega 8:**
- Constellation UI issues often stem from missing CSS customizations; validate CSS compat
- Decision engine changes may affect rule ordering; verify unit tests
- Tomcat configuration issues: check context.xml for memory settings

**Pega 23:**
- GenAI failures often due to API misconfiguration; validate LLM endpoint credentials
- Analytics loading slow? Check embedded analytics engine indexing status
- Constellation accessibility issues: use browser dev tools to validate ARIA attributes

**Pega 24:**
- Graph database queries slow? Check entity indexing strategy
- RPA integration timeouts? Verify process mining service availability
- Predictive model drift? Monitor accuracy metrics; retrain periodically

## Version-Specific Performance Tuning

| Aspect | Pega 7 | Pega 8 | Pega 23 | Pega 24 |
|--------|--------|--------|---------|---------|
| Rule evaluation | Baseline | +20% | +40-50% | +55-60% |
| UI responsiveness | Slow | Better | Excellent | Excellent |
| GenAI latency | N/A | N/A | 2-5s | 1-3s |
| Max daily cases | 500K | 1M | 2M | 5M+ |
"""
    },
    {
        "title": "Multi-Tenancy in Pega — Building SaaS Applications",
        "url": "https://docs.pega.com/bundle/pega_multitenancy",
        "content": """
# Multi-Tenancy in Pega — Building SaaS Applications

## What is Multi-Tenancy?

Multi-tenancy allows a single Pega application instance to serve multiple independent organizations (tenants) with complete data and configuration isolation. Each tenant operates as a separate logical business entity, unaware of others' data.

**Models:**
- **Single Database, Multiple Schemas** – One DB; separate schema per tenant; simplest for Pega
- **Single Database, Row-Level Isolation** – One schema; row-level security; higher complexity
- **Multiple Databases** – Separate DB per tenant; most isolation; operational overhead

**Pega Native Model:** Single database with row-level security and tenant-scoped rulesets.

## Tenant-Level Access Control

Pega enforces tenancy through **Access Groups** tied to tenants:

**Architecture:**
```
Organization Tenant (e.g., "Acme Corp")
├── Access Group: "AcmeSalesTeam"
├── Access Group: "AcmeAdminTeam"
└── Access Group: "AcmeReportingTeam"
```

Each access group controls:
- Rule visibility (only rules for that tenant visible to users)
- Case visibility (only that tenant's cases visible)
- Report access (dashboards show only tenant data)
- Data access (no cross-tenant data leakage)

**Implementation:**
- Assign users to tenant-scoped access groups in Pega Admin
- Use `@CurrentOrganization` context variable to enforce tenant filtering
- Design rulesets with tenant prefix: `Acme-Sales`, `Acme-Admin`, etc.

## Tenant-Specific Rulesets

All rules must be prefixed or namespaced by tenant to prevent conflicts:

**Good Pattern:**
```
Ruleset: Acme-Sales-01-01-01
Rules: Acme-Sales-ProcessLoan, Acme-Sales-CheckCredit, etc.

Ruleset: Zenith-Claims-01-01-01
Rules: Zenith-Claims-ProcessClaim, Zenith-Claims-ValidateProof, etc.
```

**Anti-Pattern:**
```
Ruleset: Shared-Common-01-01-01  (shared by all tenants)
→ Causes rule conflicts; hard to debug which tenant modified what
```

**Best Practice:** Each tenant has dedicated rulesets; shared utilities in a `Common` ruleset that both call.

## Data Isolation Between Tenants

**Row-Level Security (RLS):** Pega's primary isolation mechanism.

**How it works:**
- Every case has an `Organization` field
- Queries automatically filter: `WHERE Organization = @CurrentOrganization`
- UI components inherit tenant context; no manual filtering needed
- Reports scoped to current organization

**Debugging Data Leakage:**
1. Check if case type has `Organization` field
2. Verify queries use `Organization` in WHERE clause
3. Check access groups—misconfigured groups bypass security
4. Review case lifecycle rules; ensure they preserve `Organization` field
5. Check reports; confirm they filter by `@CurrentOrganization`

**Common Mistake:** Developers hardcoding organization values instead of using `@CurrentOrganization` context variable.

## Tenant Provisioning

**Self-Service Provisioning (for SaaS):**

1. **Tenant Registration** – New customer signs up; provides company name, admin email
2. **Workspace Creation** – System creates:
   - Unique tenant ID (e.g., `TENANT-00012345`)
   - Access group: `TENANT-00012345-Admins`
   - Admin user with that access group
3. **Ruleset Initialization** – Deploy tenant-specific rules from template
4. **Configuration** – Admin customizes tenant-specific settings (branding, workflows)

**Implementation in Pega:**
- Create automation rule that calls provisioning API
- API creates access group, user, initializes ruleset
- Send onboarding email with admin credentials
- Monitor provisioning failures (API timeouts, quota limits)

## Tenant-Specific Configuration (DSS Per Tenant)

**Dynamic System Settings (DSS)** enable per-tenant configuration without code changes:

**Example:**
```
DSS Property: Acme-LoanApprovalThreshold
Value: 50000

DSS Property: Zenith-LoanApprovalThreshold
Value: 150000
```

Decision rules use these values; no hardcoding:
```
@"Pega-RULES(Acme).DSS-LoanApprovalThreshold"  → applies to Acme tenant only
```

**Benefits:**
- Update thresholds without rebuilding
- Multi-tenant instances support divergent business logic
- Easy rollback if configuration breaks workflow

**Gotcha:** DSS changes take ~2 minutes to propagate; plan rollout accordingly.

## Performance Considerations

**Single-Instance Multi-Tenancy:**
- Cache efficiency suffers (more rules, more memory)
- Query performance degrades with many tenants
- Database I/O increases with row-level filtering

**Optimization:**
1. **Tenant-Specific Caching** – Cache rules per tenant; don't mix
2. **Database Partitioning** – Partition case tables by tenant; faster scans
3. **Index Strategy** – Index `(Organization, CaseID)` for fast queries
4. **Connection Pooling** – Separate pool per high-volume tenant if needed

**Typical Limits:**
- Single instance: 100-500 active tenants (depends on case volume)
- Beyond 500: consider sharding or separate instances per tenant

## Debugging Tenant Isolation Issues

**Symptom: Data leakage (seeing other tenant's cases)**
1. Check user's access group → must be tenant-scoped
2. Run query: `SELECT * FROM Case WHERE Organization != @CurrentOrganization`
3. Review case type lifecycle; verify `Organization` preserved in all rule transitions
4. Check custom Java; verify it filters by Organization

**Symptom: User can't see their own cases**
1. Verify organization assignment in access group
2. Check case `Organization` value matches user's organization
3. Review report filters; ensure they use `@CurrentOrganization`
4. Check for typos in organization names

**Symptom: One tenant's rule changes affect another tenant**
1. Verify rulesets are not shared across tenants
2. Check for hardcoded organization values in rules
3. Review ruleset application rules; ensure tenant-specific rulesets listed

**Symptom: Performance degradation with new tenant**
1. Run database analyze/reindex
2. Check connection pool exhaustion
3. Monitor memory; tenant caching may exceed limits
4. Consider separating tenant to different instance

## Pega Cloud for SaaS

**Pega Cloud** is Pega's managed multi-tenant SaaS platform:

**Features:**
- Pre-configured multi-tenancy
- Automatic scaling per tenant
- Built-in compliance (SOC2, HIPAA, GDPR)
- No ops overhead; Pega manages infrastructure

**When to use Pega Cloud:**
- SaaS ISVs (software vendors)
- Low IT infrastructure budget
- Need rapid multi-tenant deployment
- Compliance certifications critical

**Debugging Pega Cloud apps:** Use Pega Cloud Admin Portal for tenant logs; standard debugging tools apply.
"""
    },
    {
        "title": "Pega Healthcare — Claims, Prior Auth, Care Management",
        "url": "https://docs.pega.com/bundle/pega_healthcare",
        "content": """
# Pega Healthcare — Claims, Prior Auth, Care Management

## Pega Healthcare Framework Overview

Pega HealthCare is a purpose-built industry framework addressing end-to-end healthcare workflows: member enrollment, claims, prior authorization, care management, and provider network management.

**Core Case Types:**
- **Member Case** – Enrollment, eligibility, coverage maintenance
- **Claim Case** – Submission, adjudication, payment, appeals
- **Prior Auth Case** – Pre-authorization for treatments
- **Care Management Case** – Disease management, care coordination
- **Provider Network Case** – Contract management, credentialing

**Integration Points:**
- Electronic Data Interchange (EDI/X12) for claims
- HL7/FHIR for clinical data interchange
- Pharmacy networks (NCPDP)
- Employer/benefit administration systems

## Claims Processing Case Type

**Claims workflow:**
```
Claim Submission → Eligibility Check → Coverage Validation →
Benefit Calculation → Adjudication → Payment Processing → Explanation of Benefits
```

**Key Rules:**
1. **Benefit Rules** – Define coverage limits, deductibles, coinsurance
2. **Editing Rules** – Validate claim data against policy rules
3. **Pricing Rules** – Calculate allowed amounts, member liability
4. **Adjudication Rules** – Determine payment (approve, deny, pend)

**Common Debugging Issues:**

**Issue: Claim denied unexpectedly**
- Check eligibility lookup; member may be terminated mid-claim
- Verify benefit rules matched correct policy; coverage may have changed
- Review editing rules; claim may fail validation (e.g., wrong provider type)
- Check pricing data; contracted rates may be out of date

**Issue: Payment calculation wrong**
- Verify coinsurance percentage in benefit rule (e.g., 80% coverage = 20% member out-of-pocket)
- Check if deductible applied correctly (some claims exempt deductible)
- Confirm out-of-pocket limits; once met, member owes $0

**Issue: Claim stuck in pending**
- Check if waiting for prior authorization approval
- Verify external referential integrity (eligibility data available)
- Check for missing documentation (diagnosis codes, provider credentials)

## Prior Authorization Workflows

Prior Auth (Pre-Auth) is pre-approval for high-cost treatments.

**Workflow:**
```
Provider Request → Clinical Review → Medical Policy Check →
Approval Decision (Approve/Deny/Modify) → Notification → Claim Submission
```

**Key Processes:**
1. **Intake & Triage** – Capture request; validate completeness
2. **Clinical Review** – RN/MD reviews medical necessity against guidelines
3. **Policy Application** – Check against medical necessity algorithms
4. **Approval Decision** – Auto-approve routine cases; escalate complex
5. **Notification** – Inform provider and member of decision

**Debugging Prior Auth Issues:**

**Issue: Prior Auth auto-approval not working**
- Verify medical policy rules loaded and in effect
- Check diagnosis/procedure code in request matches policy rules
- Review escalation criteria; complex cases should route to nurse
- Confirm clinical data available (member age, conditions)

**Issue: Prior Auth approval takes too long**
- Check if stuck waiting for clinical data (missing labs, imaging)
- Verify routing rules; ensure going to qualified clinicians
- Monitor SLA timers; escalate if approaching limits
- Check for process blockers (missing information requests)

**Issue: Prior Auth denials being appealed frequently**
- Review denial reason clarity; vague denials invite appeals
- Check if medical policy rules too strict (not matching clinical practice)
- Verify appeals process responsive; delayed appeals demoralize members
- Monitor denial rates by provider; identify training opportunities

## Care Management Case Type

Care management identifies high-risk members and coordinates interventions (disease management, case management, wellness programs).

**Workflow:**
```
Member Identification → Risk Stratification → Care Plan Development →
Intervention Delivery → Outcome Tracking → Re-enrollment
```

**Key Components:**
1. **Risk Scoring** – Predictive model identifies high-risk members (readmission risk, chronic disease progression)
2. **Care Planning** – RN develops individualized care plan
3. **Outreach** – Phone calls, home visits, educational materials
4. **Coordination** – Work with providers, social services, behavioral health
5. **Metrics** – Track readmission reduction, cost savings, member satisfaction

**Debugging Care Management Issues:**

**Issue: Wrong members identified for care management**
- Verify risk model; check input data (claims, diagnoses, medication)
- Review scoring thresholds; may be too lenient/strict
- Check eligibility; excluded members (e.g., Medicaid with limits) should filter
- Monitor demographic bias in risk model

**Issue: Care coordinators overwhelmed (too many assignments)**
- Check workload distribution; ensure balanced across team
- Verify case closure rules; complex cases should remain open longer
- Review SLA configuration; adjust based on actual closure rates
- Implement skill-based routing (disease-specific specialists)

**Issue: Low member engagement in care plans**
- Check outreach method effectiveness (phone vs. text vs. mail)
- Verify member contact preferences; respect communication choices
- Review care plan relevance; members disengaged if not addressing their needs
- Monitor incentive programs; financial incentives improve compliance

## Healthcare-Specific Integrations

### HL7/FHIR
**HL7 v2.x** – Legacy standard; clinical data exchange (lab results, admit/discharge/transfer)
**FHIR** – RESTful, JSON-based successor to HL7; modern healthcare APIs

**In Pega:**
- Consume HL7 via REST adapters
- Parse FHIR JSON; map to Pega pages
- Support bidirectional sync (read and write clinical data)

**Debugging HL7/FHIR Issues:**
- Validate message format; use HL7 message validator tools
- Check encoding; UTF-8 vs. EBCDIC can cause parse failures
- Verify segment mapping; ORC (order) vs. OBR (observation request) confusion common
- Check timestamp formats; HL7 date format strict (YYYYMMDD)

### EDI/X12 Claims
**EDI 837** – Healthcare claim submission standard (Healthcare Provider, Institutional, Dental)
**EDI 835** – Remittance advice (payment explanation)

**In Pega:**
- Parse incoming 837 claims via EDI connector
- Validate ISA (interchange), GS (functional group), ST (transaction) segments
- Map segments to Pega claim page structure
- Generate 997 functional acknowledgments

**Debugging EDI Issues:**
- Check EDI validation rules; segment count/format errors common
- Verify NM1 (name) segment parsing; hierarchical identifier nesting complex
- Monitor transaction set numbers (ST01); duplicates rejected
- Check envelope (ISA/GS) dates; time-zone aware parsing needed

### NCPDP Pharmacy Integration
**NCPDP D0** – Pharmacy claims standard (prescription transactions)

**Debugging Pharmacy Issues:**
- Verify pharmacy network lookup; wrong network = no coverage
- Check prior authorization lookup for controlled drugs
- Monitor refill frequency violations (e.g., too early, exceeds quantity)
- Review drug interaction checks; allergy/drug conflicts flagged

## HIPAA Compliance in Pega

**Requirements:**
1. **Access Controls** – Role-based; audit all data access
2. **Encryption** – In transit (TLS 1.2+) and at rest (AES-256)
3. **Audit Logging** – Track who accessed what, when, why
4. **Data Minimization** – Only collect needed data; retention policies
5. **Breach Notification** – Investigate and notify within 60 days

**In Pega:**
- Enable encrypted connections; disable unencrypted HTTP
- Configure audit rules; log all healthcare data access
- Implement access groups per job role; limit by-need-to-know
- Encrypt database columns (PII: SSN, DOB, medical info)
- Configure data retention/purging policies

**Debugging HIPAA Audit Issues:**
- Verify audit trail logs all access to sensitive fields
- Check for data exfiltration (bulk exports without audit)
- Monitor for privilege escalation (users gaining unauthorized access)
- Review retention policies; old data properly purged

## Common Healthcare App Debugging

**Issue: Claim rejection due to eligibility**
1. Check member eligibility lookup; verify effective dates
2. Confirm benefit rules match plan type
3. Validate provider contract status; out-of-network = denial
4. Check plan change dates; coverage gaps common during transitions

**Issue: Prior Auth timeout**
1. Verify external clinical data service responding
2. Check request completeness; missing data delays review
3. Monitor queue depth; too many requests = slow processing
4. Check clinical staff availability; afternoon delays common

**Issue: Care management low engagement**
1. Verify member contact info current; bad phone = no outreach
2. Check outreach frequency; too many contacts = fatigue
3. Review member preference settings; respect opt-outs
4. Monitor language/accessibility; non-English members may need support
"""
    },
    {
        "title": "Pega Insurance — Policy, Claims, Underwriting",
        "url": "https://docs.pega.com/bundle/pega_insurance",
        "content": """
# Pega Insurance — Policy, Claims, Underwriting

## Pega Insurance Framework Overview

Pega Insurance is a comprehensive industry solution addressing the full insurance value chain: policy administration, claims handling, underwriting, renewal, and customer service.

**Core Case Types:**
- **Policy Case** – New business, endorsements, renewals, cancellations
- **Claim Case** – First notice of loss, investigation, settlement, payment
- **Underwriting Case** – Risk assessment, quote, declination, approval
- **Customer Service Case** – Changes, inquiries, complaints, retention

**Lines of Business Supported:**
- Property & Casualty (Auto, Homeowners, General Liability)
- Life & Annuities
- Travel Insurance
- Workers Compensation

## Policy Administration

**Policy Lifecycle:**
```
Quote → Bind (Issue Policy) → Coverage Period → Endorsements/Changes →
Renewal → Cancellation/Non-Renewal
```

**Key Rules:**
1. **Rating Rules** – Calculate premium based on risk factors (age, location, coverage limits)
2. **Underwriting Rules** – Approve/decline based on risk appetite
3. **Policy Issuance** – Generate documents, collect payment, activate coverage
4. **Endorsement Rules** – Allow mid-term changes; recalculate premium for changes

**Debugging Policy Issues:**

**Issue: Premium calculation incorrect**
1. Verify rating rules applied correct risk factors (age, location, claims history)
2. Check discounts applied (multi-policy, safety features, good driver)
3. Confirm taxes/fees included (state insurance tax, administrative fees)
4. Review effective dates; premium changes on coverage start date

**Issue: Policy not binding/issuing**
1. Check underwriting approval received; policy can't bind without approval
2. Verify payment received; some policies require prepayment
3. Check for data validation failures (missing address, wrong birthdate)
4. Review regulatory requirements; some states require additional disclosures

**Issue: Endorsements not processing**
1. Verify effective date in future or current; backdated endorsements restricted
2. Check if endorsement triggers re-underwriting (some changes require approval)
3. Confirm premium recalculation triggered; manually approve if needed
4. Monitor endorsement routing; ensure reaching correct team

## Claims Processing

**Claims workflow:**
```
First Notice of Loss → Investigation → Damage Assessment →
Coverage Review → Reserve → Settlement → Payment → Close
```

**Key Processes:**

1. **Intake & Validation**
   - Log claim; assign claim number
   - Validate policy active; coverage in force
   - Capture loss date, description, amount

2. **Investigation**
   - Assign adjuster
   - Request documentation (photos, repair estimates, police report)
   - Fraud screening (SIU alert if suspicious pattern)

3. **Coverage Assessment**
   - Verify coverage applies to loss type
   - Check deductible, limits, exclusions
   - Confirm no policy violations (e.g., lapsed maintenance)

4. **Settlement**
   - Calculate indemnity (what insurance pays)
   - Apply deductible
   - Issue check or direct repair authorization

**Debugging Claims Issues:**

**Issue: Claim incorrectly denied**
1. Verify policy active on loss date (coverage effective/expiration)
2. Check coverage type; may be excluded (e.g., normal wear-and-tear)
3. Review deductible application; some claims waive deductible
4. Check for policy lapses; lapsed payment = coverage void

**Issue: Claim payment incorrect**
1. Verify indemnity calculation: `(Damage Amount - Deductible) = Claim Amount`
2. Check policy limits applied (e.g., max repair = $50K, limit exceeded)
3. Confirm depreciation applied (for auto: reduce value by age/mileage)
4. Review subrogation; third-party liability may reduce payment

**Issue: Fraud detection too aggressive (too many SIU alerts)**
1. Review fraud rule scoring; may be oversensitive
2. Check for pattern overlap (e.g., claims in same area = normal for disaster)
3. Adjust thresholds; false positives tie up SIU resources
4. Monitor SIU capacity; staffing constraints may cause delays

## Underwriting Workflows

Underwriting assesses risk and determines if/how to offer coverage.

**Workflow:**
```
Application Intake → Risk Assessment → Underwriting Decision →
Quote Generation → Declination/Approval → Bind
```

**Key Components:**

1. **Application Intake**
   - Collect applicant info, loss history, property details
   - Validate data completeness

2. **Risk Assessment**
   - Credit score lookup (correlated with claims likelihood)
   - Driving record check (for auto)
   - Property inspection (for high-value homes)
   - Loss history query

3. **Underwriting Decision Rules**
   - Rule-based: Age <16 or >90 = decline
   - Predictive: LTV (loan-to-value) > 120% = decline
   - Manual: Complex cases escalate to underwriter

4. **Quote Generation**
   - Calculate premium
   - Apply underwriting adjustments
   - Present options (coverage levels, limits)

**Debugging Underwriting Issues:**

**Issue: Excessive declinations**
1. Review decline rules; may be too strict vs. market
2. Check data accuracy; old loss history, wrong bureau data
3. Verify credit score source; some agencies inaccurate
4. Monitor competitive analysis; compare decline rate to market

**Issue: Underwriting SLA not met**
1. Check application completeness; requests for info cause delays
2. Verify external lookups responsive (bureau data, MIB for life insurance)
3. Monitor underwriter workload; manually escalate if backed up
4. Review escalation criteria; complex cases queue differently

## Insurance-Specific Data Models

**Key Entities:**

1. **Policy**
   - Policy Number (unique ID)
   - Insured (policyholder)
   - Coverage Period (effective–expiration)
   - Premium, Deductible, Limits
   - Status (Active, Cancelled, Expired)

2. **Coverage**
   - Line of Business (Auto, Home, Life)
   - Coverage Type (Comprehensive, Collision, Liability)
   - Limits (e.g., $500K liability limit)
   - Deductible

3. **Claim**
   - Loss Date
   - Claim Amount (total incurred)
   - Indemnity (what we pay)
   - Status (Reported, Investigating, Settled, Closed, Denied)

4. **Insured/Risk Unit**
   - For auto: VIN, year, make, model, usage
   - For home: property address, age, construction, square footage
   - For life: age, health, occupation, beneficiary

**Debugging Data Issues:**
- Verify policy-claim link; orphaned claims (no matching policy) = data quality issue
- Check coverage hierarchy; claim must match coverage type on policy
- Monitor data freshness; outdated vehicle/property info leads to incorrect rating

## Integration with Actuarial Systems

Insurance companies use actuarial software to model future claims, set reserves, and analyze profitability.

**Integration Points:**
- Export claims data to actuarial systems (frequency, severity, reserves)
- Import reserve recommendations back to Pega
- Share loss triangles (development of claims over time)

**In Pega:**
- REST API exports claim-level data periodically
- Actuarial system runs models; returns reserve amounts
- Pega updates claim reserves; impacts financial reporting
- Monitor API reliability; failed exports = data lag

## Regulatory Compliance

**Key Regulations:**
- **State Insurance Codes** – Rate filing, approval required before use
- **NAIC** (National Association of Insurance Commissioners) – Uniform standards
- **Sarbanes-Oxley (SOX)** – Financial controls, audit trails
- **Fair Credit Reporting Act (FCRA)** – Adverse action notices if declined

**In Pega:**
- Document rating rules; file with state regulators
- Track rating changes; maintain audit trail of approvals
- Generate adverse action notices automatically (decline letters)
- Implement access controls; prevent unauthorized rate changes

**Debugging Compliance Issues:**
- Verify rate approval dates match usage dates; unapproved rates = violation
- Check adverse action notices sent; FCRA requires notification within 30 days
- Audit SOX controls; who changed rates, when, why
- Monitor state filings; missed deadlines = penalties

## Common Insurance App Debugging

**Issue: Premium quote varies between quote and bind**
1. Verify rating factors consistent (age, location, coverage)
2. Check if policy bound with different selections than quoted
3. Confirm no rating rule changes between quote and bind
4. Review effective date; rates may change daily or seasonally

**Issue: Claim reserve inadequate**
1. Review claim facts; reserve set based on reported amount
2. Check estimate accuracy; contractor estimates may underestimate
3. Monitor claim progression; adjust reserve as information gathered
4. Verify catastrophe adjustment (major events may have development factors)

**Issue: Renewal premium shock (too high)**
1. Verify loss history update; claims may have increased premium
2. Check market rating changes; insurer may have filed rate increase
3. Confirm coverage still appropriate (limits may be too low, customer adds coverage)
4. Monitor competitor offers; customer may switch if price uncompetitive

**Issue: Underwriting capacity constraint**
1. Check underwriter workload; spike in applications = backlog
2. Verify automation working; rule-based approvals should reduce manual load
3. Monitor quality metrics; rushing leads to wrong decisions
4. Consider temporary staff or outsourcing for overflow
"""
    },
    {
        "title": "Pega Financial Services & Government — Regulated Industry Solutions",
        "url": "https://docs.pega.com/bundle/pega_financial_government",
        "content": """
# Pega Financial Services & Government — Regulated Industry Solutions

## Pega for Banking — KYC, AML, Loan Origination

### Know Your Customer (KYC)

KYC is the regulatory requirement to verify customer identity and assess risk before opening accounts or providing services.

**KYC Process:**
```
Customer Application → Identity Verification → Risk Assessment →
Document Collection → Sanctions Screening → Approval/Rejection
```

**Key Steps:**

1. **Identity Verification**
   - Government ID scan/upload (driver's license, passport)
   - Document verification service (Experian, IDology)
   - Liveness check (selfie matching ID photo)
   - Address verification

2. **Risk Assessment**
   - Politically Exposed Persons (PEP) check
   - Sanction list screening (OFAC, EU sanctions)
   - Adverse media check (news databases for criminal links)
   - Country risk assessment (higher scrutiny for higher-risk countries)

3. **Enhanced Due Diligence (EDD)**
   - For high-risk customers: additional verification
   - Source of funds confirmation
   - Beneficial ownership verification

**Debugging KYC Issues:**

**Issue: Customer KYC rejected incorrectly**
1. Verify sanctions screening against current lists (OFAC updated daily)
2. Check name matching rules; slight variations (Jr., Sr.) may cause false positives
3. Review PEP check; some systems overly broad (common names in government)
4. Confirm document expiration; may reject expired ID prematurely

**Issue: KYC approval taking weeks**
1. Check document quality; blurry scans may fail OCR (Optical Character Recognition)
2. Verify manual review queue; backed-up due to volume spike
3. Confirm external verification service responding (API timeouts)
4. Monitor business hours; some verifications async, process during business hours

### Anti-Money Laundering (AML)

AML detects and prevents illicit financial activity.

**AML Monitoring:**
```
Transaction Stream → Pattern Detection → Alert Generation →
Investigation → Filing (SAR) → Law Enforcement Reporting
```

**Key Rules:**
1. **Structuring Detection** – Multiple small deposits to avoid reporting thresholds
2. **Unusual Activity** – Transactions inconsistent with customer profile
3. **Sanctions Screening** – Ongoing monitoring (not just KYC)
4. **Geographic Risk** – Activity in higher-risk countries flagged

**Suspicious Activity Report (SAR):** Filed with FinCEN within 30 days of detecting suspicious activity.

**Debugging AML Issues:**

**Issue: Too many AML alerts (alert fatigue)**
1. Review alert rule thresholds; may be too sensitive
2. Check customer segmentation; adjust thresholds by risk tier
3. Monitor false positive rate; high rates = rule ineffective
4. Consider machine learning models; better pattern detection than rules

**Issue: SAR filed late or incorrectly**
1. Verify alert triage process; alerts reaching investigator promptly
2. Check SAR form completeness; all required fields filled
3. Monitor filing timeline; document investigation start, SAR filing date
4. Verify FinCEN submission; system should log submission confirmation

### Loan Origination

Loan origination is the process of issuing loans (mortgages, auto loans, personal loans).

**Workflow:**
```
Application → Pre-Qualification → Full Application → Underwriting →
Appraisal → Verification of Employment/Assets → Final Approval → Funding
```

**Key Decision Points:**
1. **Pre-Qualification** – Soft credit pull; estimate borrower capacity
2. **Underwriting** – Credit analysis, debt-to-income ratio, property valuation
3. **Appraisal** – Home value assessment (for mortgages)
4. **Conditions** – Additional docs needed before approval (pay stubs, bank statements)
5. **Clear to Close** – All conditions met; ready to fund

**Debugging Loan Issues:**

**Issue: Loan stuck in underwriting**
1. Check conditions outstanding; missing documentation = bottleneck
2. Verify credit report obtained; some pulls require manual review
3. Confirm appraisal ordered and received (appraisals take 5-10 days)
4. Monitor underwriter capacity; complex loans take longer

**Issue: Loan declined unfairly**
1. Review underwriting rules; may have policy conflicts
2. Check credit score; may be borderline; reconsider with compensating factors
3. Verify debt-to-income calculation; may be calculated incorrectly
4. Check if loan type fits customer profile; high-risk product for low-income customer

## Pega for Government — Case Management, Citizen Services, Eligibility

### Government Case Management

Government agencies manage cases: social services, licenses, permits, investigations.

**Case Types:**
- **Social Services** – Benefits eligibility (SNAP, Medicaid, housing assistance)
- **Permitting** – License, permit, certification requests (business license, construction permit)
- **Investigation** – Complaint investigation, fraud investigation
- **Enforcement** – Violation enforcement, license suspension

**Workflow Example (Benefits Case):**
```
Application → Eligibility Assessment → Documentation Collection →
Verification → Approval/Denial → Enrollment → Ongoing Compliance
```

**Key Challenges:**
1. **Complex Eligibility Rules** – Multiple benefit programs; overlapping rules
2. **Integration with Legacy Systems** – Often 20+ year old mainframe systems
3. **Multi-Channel Application** – Online, paper, in-person applications
4. **Compliance Reporting** – Regular audits; detailed audit trails required

**Debugging Government Case Issues:**

**Issue: Incorrect eligibility determination**
1. Verify all household members captured (often overlooked)
2. Check income calculation; include all sources (wages, benefits, SSI)
3. Confirm asset limits applied correctly; some programs asset-tested
4. Review recent rule changes; regulations update annually

**Issue: Case processing exceeding SLA**
1. Check documentation completeness; requests for info cause delays
2. Verify verifications completed (income, employment, residency)
3. Monitor queue backlog; spike in applications = extended SLA
4. Check if supervisory approval required; approval bottleneck

### Citizen Services Portal

Modern governments offer online portals for citizens to check status, apply, pay fees, etc.

**Portal Functions:**
- Check application/case status
- Upload documents
- Pay bills/fees
- Schedule appointments
- Request certificates/copies

**Debugging Portal Issues:**

**Issue: Document upload failing**
1. Check file size limits; large PDFs rejected
2. Verify file type allowed (PDF, JPEG, PNG typically)
3. Confirm virus scanning not blocking uploads
4. Check network latency; timeouts on slow connections

**Issue: Status lookup not showing cases**
1. Verify authentication; user logged into correct account
2. Check case assignment; case may not be assigned to current user
3. Confirm data integration; portal pulls from backend system
4. Monitor for sync lag; real-time updates may have delay

### Eligibility Verification

Government benefits require ongoing eligibility verification (not just initial approval).

**Verification Methods:**
1. **Wage Verification** – Query Social Security Administration (SSA)
2. **Residency Verification** – Address confirmation
3. **Citizenship Verification** – E-Verify system (employment eligibility)
4. **Benefit Cross-Check** – Prevent double-dipping across programs

**Debugging Verification Issues:**

**Issue: Wage verification failing**
1. Check SSA connectivity; system may be down
2. Verify social security number; typos cause mismatches
3. Confirm wage data timely (SSA updates quarterly; lag possible)
4. Check for name mismatches; surname changes not always updated

**Issue: Duplicate benefits detected**
1. Cross-check application database; applicant in multiple programs at once
2. Verify data quality; same person entered twice (different names)
3. Monitor benefit rules; some allow stacking (legitimate), some don't
4. Review approval process; should have caught duplicates before approval

## Compliance Requirements

### Sarbanes-Oxley (SOX) — Financial Controls

**For financial institutions:**
- Audit trails (who changed what, when, why)
- Segregation of duties (no one person approves and funds a transaction)
- Change management (all system changes documented, approved)
- Risk assessments

**In Pega:**
- Enable rule auditing; track all rule modifications
- Require approval workflows for high-risk changes (rate changes, rule changes)
- Document system changes; maintain change log
- Periodic risk assessment; review controls effectiveness

**Debugging SOX Compliance:**

**Issue: Missing audit trail for rule change**
1. Verify audit rules enabled in system settings
2. Check if rule change exempted from audit (some rule types not audited)
3. Review rule history; use rule comparison tools
4. Monitor for unauthorized changes; implement alerts

**Issue: Segregation of duties violation**
1. Review access group assignments; same user may have too much power
2. Separate approval authority; who approves vs. who executes
3. Implement approval workflows; 4-eyes principle on high-risk actions
4. Monitor access logs; detect privilege escalation

### GDPR — European Data Protection

**Key Requirements:**
- Right to be forgotten (data deletion on request)
- Data portability (export personal data)
- Explicit consent (for data collection)
- Data Protection Impact Assessment (DPIA) for new systems

**In Pega:**
- Implement data retention policies (automatic purging)
- Provide data export capability
- Maintain consent records (explicitly opt-in)
- Document DPIA results

**Debugging GDPR Issues:**

**Issue: Data not deleted on deletion request**
1. Check data retention rules; may not be configured for deletion
2. Verify all copies deleted (production, backups, logs)
3. Monitor third-party data sharing; vendors also required to delete
4. Document deletion; maintain deletion audit trail (proof for regulators)

## Industry-Specific Patterns

### Approval Workflows
Standard pattern for regulated industries: request → approval → execution

**Implementation:**
```
Rule Proposal → Manager Approval → Compliance Review → Deployment
```

**Best Practice:** Separate teams for each role (no one person does all).

### Data Retention Policies
Regulatory requirements dictate how long to keep records.

**Example:**
- Financial records: 7 years (SOX)
- Tax records: 5 years (IRS)
- HIPAA records: 6 years

**In Pega:** Use purge rules; automatic deletion after retention period.

### Audit Logging
Every sensitive action must be logged and auditable.

**What to log:**
- Data access (who read sensitive data)
- Data modification (who changed what)
- Approvals (who approved what)
- System changes (who modified rules/configuration)

**Debugging audit issues:**
- Verify audit trails queryable (not buried in application logs)
- Check timestamp accuracy; clock skew causes confusion
- Monitor audit log growth; may fill disk if not archived
- Implement alerting; unauthorized access detected in real-time

## Common Debugging in Regulated Industries

**Issue: Compliance failure detected in audit**
1. Identify control failure (what was missed)
2. Root cause analysis (why did it happen)
3. Remediation (fix the control)
4. Documentation (document for regulators)

**Issue: Regulatory change requires rapid deployment**
1. Assess impact; which rules/processes affected
2. Update rules; test thoroughly (no rolling back mid-quarter in regulated industries)
3. Communicate to impacted teams
4. Verify deployment; confirm rules active

**Issue: Audit finding (regulator identified issue)**
1. Take seriously; auditors have enforcement authority
2. Develop response plan; regulator will ask for remediation timeline
3. Implement corrective actions; often required within 30 days
4. Follow up; regulator may reinspect to verify remediation

**Issue: Customer complaint regarding regulatory violation**
1. Investigate promptly; escalate to compliance team
2. Determine actual breach; customer perception may differ from reality
3. Provide transparency; explain to customer what happened, why
4. Report to regulator if required (e.g., data breach >500 individuals)
"""
    }
]

def seed_phase17():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE17:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase17_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE17)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 17 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase17()
