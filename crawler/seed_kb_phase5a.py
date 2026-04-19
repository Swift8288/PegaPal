"""
Curated Pega Knowledge Base — Phase 5A (High Priority)
Covers: REST Services, OAuth 2.0, CI/CD, Database Tuning, Upgrade Assessment,
        Data Flows, Branch & Merge

Run: python -m crawler.seed_kb_phase5a
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE5A = [
    {
        "url": "curated://pega-rest-service-exposure",
        "title": "REST Service — Exposing Pega APIs, Service Packages, and Troubleshooting",
        "content": """# REST Service — Exposing Pega as a REST API

## Overview
Service REST rules expose Pega functionality as RESTful API endpoints for external systems to consume. This is the reverse of a REST Connector — instead of Pega calling out, external systems call INTO Pega.

## Architecture
- **Service Package**: Groups service rules, defines base URL path, authentication method
- **Service REST rule**: Defines HTTP method, path, request/response mapping
- **Service Activity**: Processes the incoming request (business logic)
- **Authentication**: Basic, OAuth 2.0, or custom authentication on the service package

## Configuration Steps
1. Create a Service Package (Records → Integration → Service Package)
2. Set authentication method (Basic, OAuth 2.0, Anonymous)
3. Create Service REST rule inside the package
4. Define HTTP methods (GET, POST, PUT, DELETE)
5. Map request parameters/body to Pega properties
6. Configure response mapping (JSON/XML output)
7. Deploy and test

## Common REST Service Issues

### 1. External System Gets 404 — Endpoint Not Found
**Root Causes**:
- Service Package not running or not deployed to this node
- URL path doesn't match the service rule configuration (case-sensitive!)
- Service Package context root mismatch
- Node type doesn't include service processing

**Fix**:
1. Check SMA/Admin Studio → Services → Service Packages → is it running?
2. Verify URL: `<server>/prweb/PRRestService/<ServicePackageName>/<path>`
3. Check service rule's HTTP method and path match what the caller is using
4. Verify node type includes service processing in prconfig.xml

### 2. 401 Unauthorized / 403 Forbidden
**Root Causes**:
- Wrong authentication credentials
- OAuth token expired or invalid scope
- Service Package authentication method doesn't match what caller is sending
- Operator tied to the service credentials lacks required access

**Fix**:
1. Check Service Package → Authentication tab → what method is configured?
2. For OAuth: verify client ID, secret, token endpoint, and scopes
3. For Basic: verify the operator ID/password used in the Authorization header
4. Check the service operator's access group has required privileges

### 3. 500 Internal Server Error on Service Call
**Root Causes**:
- Service Activity throws an unhandled exception
- Request body doesn't match expected schema
- Property mapping fails (wrong type, missing required field)
- Database error during processing

**Fix**:
1. Check PegaRULES log for the specific error (search for the service name)
2. Use Tracer on the service operator to trace the processing
3. Validate request body matches the expected schema
4. Test the service activity independently with sample data

### 4. Request Body Not Mapping to Properties
**Root Causes**:
- JSON field names don't match Pega property names (case-sensitive!)
- Nested JSON not mapped correctly (need page/page list mapping)
- Content-Type header missing or wrong (must be application/json)
- Request parsing rule misconfigured

**Fix**:
1. Check the service rule's Request tab → property mapping
2. Ensure caller sends `Content-Type: application/json` header
3. Verify JSON field names match property names exactly
4. For nested objects: configure page-level mapping in the service rule
5. Test with a simple flat JSON first, then add complexity

### 5. Response Missing Fields or Wrong Format
**Root Causes**:
- Response mapping not including all required properties
- Property is null/empty so it's excluded from JSON output
- Wrong response content type configured
- Custom response activity not formatting output correctly

**Fix**:
1. Check service rule → Response tab → verify all properties are mapped
2. Set default values for properties that might be null
3. Verify Content-Type in response configuration
4. Test response using a REST client (Postman, curl)

### 6. Service Performance Issues
**Symptoms**: Slow API response, timeouts, high latency
**Root Causes**:
- Service activity has expensive database queries
- No connection pooling for the service
- Synchronous processing of long-running operations
- Too many concurrent requests overwhelming the service thread pool

**Fix**:
1. Optimize the service activity — minimize database calls
2. Use asynchronous processing for long operations (return 202 Accepted, process in background)
3. Implement caching for frequently-requested data
4. Monitor service performance with PAL and PDC alerts
5. Scale service thread pool or add nodes for high-volume APIs

## REST Service Best Practices
1. Version your APIs: use `/v1/`, `/v2/` in the URL path
2. Use proper HTTP status codes (200, 201, 400, 404, 500)
3. Implement rate limiting to protect the system
4. Always use OAuth 2.0 in production (never Basic Auth)
5. Log all incoming requests for audit and debugging
6. Return meaningful error messages in the response body
7. Document your API with OpenAPI/Swagger
"""
    },
    {
        "url": "curated://pega-oauth2-oidc-deep-dive",
        "title": "OAuth 2.0 and OIDC — Configuration, Grant Types, and Troubleshooting",
        "content": """# OAuth 2.0 and OIDC in Pega — Deep Dive

## Overview
OAuth 2.0 is the standard authentication/authorization protocol for Pega APIs and SSO. Pega supports OAuth 2.0 both as a **provider** (issuing tokens) and as a **client** (consuming tokens from external identity providers).

## Grant Types Supported
1. **Client Credentials**: Machine-to-machine (no user involved). Most common for service-to-service calls.
2. **Authorization Code**: User-facing SSO. Redirects user to login page, returns auth code, exchanges for token.
3. **Authorization Code + PKCE**: Secure version for public clients (mobile/SPA). No client secret needed.
4. **Resource Owner Password (ROPC)**: Direct username/password exchange. DEPRECATED — avoid in new implementations.
5. **Implicit**: DEPRECATED — use Authorization Code + PKCE instead.

## Pega as OAuth Provider (Issuing Tokens)

### Configuration
1. Security → OAuth 2.0 → Create Client Registration
2. Set Grant Types allowed (Client Credentials, Auth Code, etc.)
3. Configure Client ID and Client Secret
4. Set Token Expiration time (default: 3600 seconds / 1 hour)
5. Configure Redirect URIs (for Auth Code flow)
6. Define Scopes (optional — maps to Pega access groups)

### Token Endpoints
- **Token**: `POST <server>/prweb/PRRestService/oauth2/v1/token`
- **Authorize**: `GET <server>/prweb/PRRestService/oauth2/v1/authorize`
- **Token Info**: `GET <server>/prweb/PRRestService/oauth2/v1/token/info`
- **Revoke**: `POST <server>/prweb/PRRestService/oauth2/v1/revoke`

## Common OAuth Issues

### 1. "Invalid client" Error on Token Request
**Root Causes**:
- Client ID or Client Secret wrong
- Client Registration rule not saved or not in active ruleset
- Encoding issue — client_id/secret must be URL-encoded if sent in body, or Base64 in header
- Client Registration disabled or expired

**Fix**:
1. Verify Client ID and Secret in the Client Registration rule
2. Check if sending via header: `Authorization: Basic base64(client_id:client_secret)`
3. Or via body: `grant_type=client_credentials&client_id=xxx&client_secret=xxx`
4. Verify the Client Registration rule is active and in the ruleset stack

### 2. "Invalid grant" Error
**Root Causes**:
- Authorization code already used (codes are single-use!)
- Authorization code expired (default: 5 minutes)
- Redirect URI mismatch between authorize and token requests
- PKCE code_verifier doesn't match the code_challenge

**Fix**:
1. Request a new authorization code — don't reuse
2. Exchange the code for a token within 5 minutes
3. Ensure redirect_uri is EXACTLY the same in both requests (including trailing slashes)
4. For PKCE: verify code_challenge_method and code_verifier generation

### 3. Token Expired / "Invalid token"
**Root Causes**:
- Access token expired (check exp claim)
- Token was revoked
- Token issued by a different Pega environment (dev token on prod)
- Clock skew between systems

**Fix**:
1. Implement token refresh: use refresh_token grant to get a new access token
2. Cache tokens and refresh proactively before expiry (e.g., refresh at 80% of lifetime)
3. Check token expiration: decode JWT and check `exp` timestamp
4. Sync clocks between systems (NTP)

### 4. Scope / Permission Issues
**Root Causes**:
- Token doesn't have the required scope for the API endpoint
- Scope maps to wrong access group in Pega
- Client Registration doesn't include the required scope

**Fix**:
1. Check what scopes the token has (decode JWT or use token info endpoint)
2. Verify scope-to-access-group mapping in Pega OAuth configuration
3. Add required scopes to the Client Registration
4. Request the correct scopes when requesting the token

### 5. CORS Errors on Browser-Based OAuth
**Symptoms**: Browser console shows CORS errors during OAuth redirect
**Root Causes**:
- Pega CORS policy doesn't allow the frontend origin
- Preflight OPTIONS request blocked
- Token endpoint doesn't support CORS headers

**Fix**:
1. Configure CORS in Pega: Security → CORS Policy → add frontend origin
2. Ensure preflight (OPTIONS) requests are handled
3. For SPA apps: use Authorization Code + PKCE (not Implicit)

## OAuth Best Practices
1. Use Client Credentials for service-to-service, Authorization Code + PKCE for user-facing
2. Never expose client secrets in frontend code
3. Implement token refresh — don't force re-authentication
4. Set appropriate token lifetimes (short for access tokens, longer for refresh tokens)
5. Use scopes to implement least-privilege access
6. Rotate client secrets periodically
7. Log all token issuance and revocation for audit
"""
    },
    {
        "url": "curated://pega-cicd-pipeline",
        "title": "CI/CD Pipeline — Deployment Manager, Jenkins, and Automation",
        "content": """# CI/CD Pipeline — Deployment Manager and Automation

## Overview
Pega supports automated CI/CD through Deployment Manager (built-in) and integration with external tools (Jenkins, GitHub Actions, Azure DevOps). The goal: automate the promotion of applications from Dev → QA → Staging → Production.

## Deployment Manager
Pega's built-in deployment tool manages the full pipeline:
1. **Pipeline definition**: Define environments and promotion stages
2. **Application packaging**: Export application as RAP (Rules Application Package)
3. **Automated testing**: Run PegaUnit tests before promotion
4. **Approval gates**: Require manual approval before production deployment
5. **Rollback**: Revert to previous version if deployment fails

## Pipeline Architecture
```
Dev → Build/Export RAP → Run Tests → QA Deploy → QA Tests →
Staging Deploy → Smoke Tests → Approval Gate → Prod Deploy → Validation
```

## Common CI/CD Issues

### 1. RAP Export Fails
**Root Causes**:
- Uncommitted rules in the ruleset (rules checked out but not saved)
- Ruleset version conflicts (overlapping versions)
- Missing dependencies (built-on application not included)
- Database lock during export

**Fix**:
1. Check for uncommitted/checked-out rules in the ruleset version
2. Verify all dependent rulesets are included in the export
3. Lock the ruleset version before export to prevent concurrent changes
4. Resolve any compilation errors in the ruleset

### 2. RAP Import Fails in Target Environment
**Error**: "Import failed" or "Conflict detected during import"
**Root Causes**:
- Schema differences between source and target database
- Conflicting rules already exist in target (higher version)
- Missing prerequisite application or ruleset in target
- Product version mismatch (e.g., RAP from 8.7 imported into 8.6)

**Fix**:
1. Check import log for specific error details
2. Verify target environment has all prerequisite applications
3. Run schema update in target before import if schema changed
4. Ensure Pega product version in target >= source
5. Use "Import with overwrite" cautiously — understand what will be replaced

### 3. Automated Tests Fail in Pipeline
**Root Causes**:
- Tests depend on environment-specific data (operator IDs, reference data)
- Test mocks not applied in the pipeline environment
- Ruleset stack differs between dev and pipeline environment
- Timing issues — tests run before import is fully complete

**Fix**:
1. Make tests self-contained — set up test data in the test itself
2. Mock all external dependencies
3. Add wait/verification step between import and test execution
4. Use environment-agnostic test data

### 4. Deployment Manager Pipeline Stuck
**Root Causes**:
- Approval gate waiting for approver who hasn't acted
- Target environment is unreachable (network issue)
- Previous deployment still in progress
- Pipeline configuration error

**Fix**:
1. Check Deployment Manager dashboard for the stuck stage
2. If approval gate: notify the approver or configure auto-approval for non-prod
3. Verify network connectivity between Deployment Manager and target
4. Cancel stuck deployment and retry

### 5. Rollback Doesn't Work as Expected
**Root Causes**:
- Database schema changes are not automatically rolled back
- Data created by the new version persists after rollback
- Dependent applications not rolled back together

**Fix**:
1. Always backup database before production deployment
2. Plan rollback for schema changes separately (DDL scripts)
3. Test rollback procedure in staging before production
4. Document manual rollback steps for each deployment

## Jenkins Integration
```
Pipeline Steps:
1. Trigger: Git push or schedule
2. Export: Call Pega export API → download RAP file
3. Test: Trigger PegaUnit test suite via Pega API
4. Deploy: Call Pega import API with RAP file
5. Validate: Run smoke tests against target environment
6. Notify: Send results to Slack/email
```

## CI/CD Best Practices
1. Automate everything — manual deployments cause errors
2. Run tests at every stage (dev, QA, staging, prod)
3. Use feature branches and merge to main only when ready
4. Keep RAP files small — deploy frequently in small increments
5. Always have a rollback plan before production deployment
6. Monitor the target environment after deployment (alerts, errors, performance)
7. Version everything — rulesets, applications, pipelines
"""
    },
    {
        "url": "curated://pega-database-tuning",
        "title": "Database Tuning for Pega — Indexes, Query Optimization, and Troubleshooting",
        "content": """# Database Tuning for Pega — Indexes, Query Optimization

## Overview
Pega's performance is heavily dependent on the underlying database. The main tables (pc_work, pc_history, pc_data_*, pr_other) can grow to millions of rows. Proper indexing, statistics, and query optimization are critical.

## Key Pega Tables
- **pc_work**: Active work items (cases). Most queried table.
- **pc_history**: Resolved/closed work items. Archive table.
- **pc_data_***: Data class instances (one table per class group).
- **pr_other**: Rules and system data.
- **pc_assign_worklist**: Active assignments.
- **pc_assign_workbasket**: Workbasket assignments.

## Common Performance Issues

### 1. Slow Queries on pc_work
**Symptoms**: Report definitions, search, or case list screens are slow
**Root Causes**:
- Missing indexes on commonly filtered columns
- Table statistics out of date
- Full table scan due to non-indexed WHERE clause
- Too many rows in pc_work (no archival strategy)

**Essential Indexes for pc_work**:
```sql
CREATE INDEX idx_pcwork_status ON pc_work (pystatuswork);
CREATE INDEX idx_pcwork_createdt ON pc_work (pxcreatedatetime);
CREATE INDEX idx_pcwork_updatedt ON pc_work (pxupdatedatetime);
CREATE INDEX idx_pcwork_assignee ON pc_work (pyassignedoperatorid);
CREATE INDEX idx_pcwork_casetype ON pc_work (pxobjclass);
CREATE INDEX idx_pcwork_id ON pc_work (pyid);
-- Composite index for common query patterns:
CREATE INDEX idx_pcwork_status_class ON pc_work (pystatuswork, pxobjclass);
CREATE INDEX idx_pcwork_class_createdt ON pc_work (pxobjclass, pxcreatedatetime);
```

### 2. Slow Assignment Queries
**Symptoms**: Worklist/workbasket screens slow, "Get Next Work" slow
**Essential Indexes**:
```sql
CREATE INDEX idx_assign_wl_operator ON pc_assign_worklist (pxassignedoperatorid);
CREATE INDEX idx_assign_wl_urgency ON pc_assign_worklist (pxurgencyassign DESC);
CREATE INDEX idx_assign_wb_name ON pc_assign_workbasket (pxworkbasketname);
```

### 3. Table Statistics Out of Date
**Symptoms**: Sudden performance degradation, query plans change for the worse
**Root Cause**: Database optimizer uses stale statistics to choose query plans

**Fix by database**:
- **PostgreSQL**: `ANALYZE pc_work; ANALYZE pc_assign_worklist;`
- **Oracle**: `EXEC DBMS_STATS.GATHER_TABLE_STATS('schema', 'PC_WORK');`
- **SQL Server**: `UPDATE STATISTICS pc_work;`
- **Schedule**: Run statistics update daily or after large data changes
- **In Pega**: Admin Studio → Database → Update Statistics

### 4. Large Table Growth — Archival Strategy
**Symptoms**: pc_work has millions of rows, all queries slow
**Fix**:
1. Move resolved cases to pc_history (Pega's built-in archival)
2. Configure archival rules: Dev Studio → SysAdmin → Archive rules
3. Set retention period (e.g., archive after 90 days of resolution)
4. For very old data: consider moving to a data warehouse
5. Partition pc_work by date or status for very large installations

### 5. Database Connection Pool Exhaustion
**Symptoms**: "Connection pool exhausted" errors, requests queuing
**Root Causes**:
- Pool too small for concurrent users
- Long-running queries hogging connections
- Transaction leaks (Commit/Rollback not called)
- Connection validation overhead

**Fix**:
1. Increase pool size in app server config (context.xml for Tomcat)
2. Identify and optimize long-running queries (check PAL/alerts)
3. Check for missing Commit/Rollback in activities
4. Set connection pool validation query and timeout
5. Monitor active connections: `SELECT count(*) FROM pg_stat_activity` (PostgreSQL)

### 6. Query Plan Issues
**Symptoms**: Same query sometimes fast, sometimes slow
**Root Causes**:
- Parameter sniffing (cached plan optimal for different parameters)
- Statistics drift between updates
- Index not used due to type mismatch or function on column

**Fix**:
1. Check query plan: `EXPLAIN ANALYZE <query>` (PostgreSQL) or `EXPLAIN PLAN FOR` (Oracle)
2. Look for Sequential Scan (PostgreSQL) / TABLE ACCESS FULL (Oracle) — indicates missing index
3. Update statistics
4. Check for implicit type conversions in WHERE clauses
5. Consider query hints only as last resort

## Database Best Practices
1. Update statistics at least daily in production
2. Add indexes for all commonly-used report filters
3. Implement archival strategy — don't let pc_work grow unbounded
4. Monitor slow query log and address top offenders
5. Size connection pool based on concurrent user count + background threads
6. Run EXPLAIN on slow queries to understand the query plan
7. Partition large tables if they exceed 10M+ rows
"""
    },
    {
        "url": "curated://pega-upgrade-assessment",
        "title": "Pre-Upgrade and Post-Upgrade — Assessment, Validation, and Troubleshooting",
        "content": """# Pega Upgrade — Pre and Post Assessment Guide

## Pre-Upgrade Assessment

### Step 1: Run Pega Pre-Upgrade Tool
- Available in Dev Studio → Configure → Application → Upgrade Assessment
- Identifies: deprecated APIs, removed features, incompatible rules, Java changes
- Run this FIRST — it provides the definitive list of what needs attention

### Step 2: Review Custom Java Code
**What to check**:
- Search for deprecated Java API calls (PublicAPI changes)
- Check custom Java steps in Activities for removed methods
- Verify JAR file compatibility with target Pega version
- Check for direct JDBC usage (should use Connect SQL instead)

**How**: `grep -r "import com.pega" --include="*.java" custom/`

### Step 3: Review Custom SQL
**What to check**:
- Direct SQL queries against Pega system tables (schema may change)
- Connect SQL rules with hardcoded table/column names
- Custom database views built on Pega tables
- Report Definitions with SQL overrides

### Step 4: Review Integrations
**Checklist**:
- [ ] REST/SOAP Connectors — do target systems accept calls from new Pega version?
- [ ] Service REST/SOAP rules — will callers work with any response format changes?
- [ ] JMS/MQ listeners — verify message format compatibility
- [ ] File listeners — verify directory paths and file patterns
- [ ] Email accounts — verify OAuth tokens and SMTP config

### Step 5: Review UI Components
**Checklist**:
- [ ] Custom JavaScript in sections — may break in Constellation
- [ ] CSS overrides — may not apply in new UI framework
- [ ] Custom harness/portal rules — check compatibility
- [ ] Third-party JavaScript libraries — check version compatibility

### Step 6: Backup Everything
- Full database backup (PegaRULES + PegaDATA)
- Application export (RAP) of all applications
- Document current configuration (prconfig.xml, DSS values, security settings)
- Export operator and access group configurations

## Post-Upgrade Validation

### Immediate Checks (First 30 minutes)
1. **System starts**: All nodes come up without errors
2. **Login works**: Admin can log in, regular users can log in
3. **Portal loads**: Default portal renders without JavaScript errors
4. **Database connectivity**: No connection errors in logs
5. **Search works**: Full-text search returns results

### Functional Smoke Tests (First 2 hours)
1. **Create a case**: Can you create a new case of each type?
2. **Complete an assignment**: Can you fill out forms and submit?
3. **Run a report**: Do key reports return data?
4. **Test integrations**: Do REST connectors reach external systems?
5. **Test background jobs**: Are agents and queue processors running?
6. **Test search**: Do new and existing cases appear in search?

### Regression Testing (First 1-2 days)
1. Run full PegaUnit test suite
2. Execute critical business process end-to-end tests
3. Test all integration points with external systems
4. Verify all reports and dashboards
5. Check performance baselines (compare response times to pre-upgrade)
6. Test SSO/authentication flows
7. Verify email/correspondence functionality
8. Test batch processing and agents

### What to Watch For (First Week)
1. **Error spike**: Monitor PegaRULES log and ALERT log for new errors
2. **Performance degradation**: Compare PAL metrics to pre-upgrade baseline
3. **User complaints**: Set up feedback channel for users to report issues
4. **Memory usage**: Monitor JVM heap — new version may have different memory profile
5. **Database performance**: Monitor slow queries — schema changes may invalidate query plans

## Common Post-Upgrade Issues

### 1. Rules Behaving Differently
**Cause**: Rule resolution algorithm changes between versions
**Fix**: Use Rule Resolution inspector to compare which rule version is picked up

### 2. Performance Regression
**Cause**: Database statistics outdated after schema changes, or new features enabled by default
**Fix**: Update all database statistics immediately after upgrade. Disable new features that aren't needed.

### 3. Authentication Failures
**Cause**: Security policy defaults changed in new version
**Fix**: Review authentication policies and reset to required configuration

### 4. Missing Customizations
**Cause**: Custom rules overwritten by upgrade if they share the same ruleset version
**Fix**: Always keep customizations in application-specific rulesets, not in Pega base rulesets

## Upgrade Best Practices
1. Never upgrade production first — upgrade Dev → QA → Staging → Prod
2. Run the Pre-Upgrade Assessment tool before starting
3. Allocate 2-3x the expected time — upgrades always take longer
4. Keep the old environment running until new environment is validated
5. Document every manual step during upgrade for repeatability
6. Plan for rollback — have a tested rollback procedure ready
7. Communicate downtime window to all stakeholders
"""
    },
    {
        "url": "curated://pega-data-flows-pipeline",
        "title": "Data Flows and Data Pipeline — Event Processing and Troubleshooting",
        "content": """# Data Flows and Data Pipeline — Troubleshooting

## Overview
Data Flows in Pega enable high-throughput, event-driven data processing. They read from data sources (database, Kafka, file), process records in parallel, and write to destinations. Used for: data migration, real-time event processing, batch ETL, and analytics.

## Architecture
- **Data Set (Source)**: Where data comes from — Database, Kafka, File, REST endpoint
- **Data Flow rule**: Defines the processing logic — read, transform, filter, write
- **Data Set (Destination)**: Where processed data goes — Database, Kafka, case creation
- **Strategy**: Optional decision logic (Next-Best-Action) applied during processing

## Data Flow Types
- **Batch**: Process a fixed set of records (e.g., nightly data migration)
- **Real-time**: Continuously process incoming events (e.g., Kafka stream)
- **On-demand**: Triggered by user action or API call

## Common Data Flow Issues

### 1. Data Flow Not Starting
**Root Causes**:
- Data Flow rule disabled or not deployed
- Source data set not configured or not accessible
- Node classification doesn't include data flow processing
- Insufficient permissions to run the data flow

**Fix**:
1. Check Data Flow rule → is it enabled?
2. Verify source data set is properly configured and accessible
3. Check node type includes "BackgroundProcessing" or data flow node type
4. Verify operator permissions for the data flow's class

### 2. Records Skipped or Lost
**Root Causes**:
- Error in processing logic causes records to fail silently
- Filter conditions accidentally excluding valid records
- Source query doesn't return expected records
- Destination write fails but error not surfaced

**Fix**:
1. Enable error handling on the data flow — configure error data set
2. Check filter conditions with sample data
3. Test the source data set independently
4. Monitor the error data set for failed records
5. Add logging at each processing step

### 3. Data Flow Performance — Too Slow
**Root Causes**:
- Not enough parallel threads configured
- Each record triggers expensive processing (database lookups, connector calls)
- Source query is slow (missing indexes)
- Destination is the bottleneck (slow database inserts)

**Fix**:
1. Increase thread count on the data flow (Concurrency setting)
2. Batch database operations instead of per-record
3. Optimize source query with indexes
4. Use bulk insert for destination if supported
5. Monitor with PAL to identify the bottleneck

### 4. Duplicate Processing
**Root Causes**:
- Data flow restarted without offset management
- Kafka consumer group reset causing reprocessing
- No idempotency check in the processing logic

**Fix**:
1. Implement idempotency: check if record already processed before processing again
2. Use Kafka consumer offsets properly (commit after successful processing)
3. Add unique constraint on destination to prevent duplicates
4. Use "exactly once" semantics where supported

### 5. Real-Time Data Flow Falling Behind
**Root Causes**:
- Processing can't keep up with incoming event rate
- Thread pool exhausted
- Downstream system (database/API) can't handle the throughput

**Fix**:
1. Scale horizontally — add more Pega nodes for data flow processing
2. Increase concurrency (thread count)
3. Optimize per-record processing time
4. Use batching for database writes
5. Monitor lag between event production and processing

## Data Flow Best Practices
1. Always configure an error data set to capture failed records
2. Implement idempotency for at-least-once processing
3. Monitor throughput and latency with PDC
4. Test with production-volume data before go-live
5. Set appropriate concurrency based on available resources
6. Use batch operations for database-heavy processing
"""
    },
    {
        "url": "curated://pega-branch-merge-conflicts",
        "title": "Branch and Merge — Strategies, Conflict Resolution, and Troubleshooting",
        "content": """# Branch and Merge — Conflict Resolution and Troubleshooting

## Overview
Pega uses **branches** for parallel development — multiple developers or teams work in isolated branch rulesets, then merge changes back to the main ruleset. Understanding merge conflicts and resolution strategies is critical for team development.

## How Branches Work
1. Developer creates a branch from the main ruleset version
2. Branch gets its own ruleset (e.g., `MyApp:01-01-01-branch-FEAT123`)
3. Developer makes changes in the branch (isolated from main)
4. When ready: merge branch back to main ruleset
5. Conflicts resolved during merge

## Branch Types
- **Feature branch**: One feature per branch (recommended)
- **Developer branch**: One branch per developer (less common)
- **Release branch**: Stabilization branch before production (common in large teams)

## Common Branch & Merge Issues

### 1. Merge Conflict — Same Rule Modified in Both Branch and Main
**Symptoms**: Merge wizard shows conflicts, can't auto-merge
**Root Causes**:
- Two developers modified the same rule (section, activity, data transform, etc.)
- Main ruleset had hotfixes while branch was in development
- Long-lived branch diverged significantly from main

**Resolution Steps**:
1. Open the merge conflict wizard → review each conflicting rule
2. For each conflict, choose: Take branch version, Take main version, or Manual merge
3. Manual merge: open both versions side-by-side, combine changes carefully
4. After resolving: test the merged version thoroughly
5. Run PegaUnit tests to verify nothing broke

### 2. Merge Fails — "Cannot merge, base version not found"
**Root Causes**:
- Branch was created from a different ruleset version than current main
- Base ruleset was re-versioned or reorganized since branch creation
- Intervening merges changed the ruleset structure

**Fix**:
1. Identify the common base version
2. If possible: rebase the branch onto current main before merging
3. If rebase not possible: manual migration of changes
4. For future: keep branches short-lived to minimize divergence

### 3. Merged Rule Doesn't Work as Expected
**Symptoms**: Merged successfully but behavior is wrong
**Root Causes**:
- Semantic conflict: both changes compile but have conflicting logic
- Missing context: one change depends on another change that wasn't merged
- Partial merge: some rules merged, others not yet

**Fix**:
1. Review the merged rule logic carefully (not just syntax)
2. Ensure ALL related rules from the branch were merged (not just some)
3. Run full regression test suite after merge
4. Compare behavior with both the branch and main pre-merge versions

### 4. Too Many Conflicts — Branch Too Old
**Root Causes**:
- Branch has been open for weeks/months
- Main has received many changes since branch was created

**Prevention**:
1. Keep branches short-lived (days, not weeks)
2. Regularly merge main INTO the branch (forward integration) to stay current
3. Small, focused branches are better than large, long-running ones
4. Communicate with team about which rules are being modified

### 5. Lock Conflicts During Merge
**Symptoms**: "Rule is locked by another user" during merge
**Root Causes**:
- Another developer has the rule checked out
- Branch lock conflicts with main lock
- System lock from a failed previous merge attempt

**Fix**:
1. Coordinate with the team — have the other developer check in their changes
2. If system lock: use Admin Studio to release stale locks
3. Schedule merges during low-activity periods

## Merge Best Practices
1. Keep branches short-lived (1-2 weeks max)
2. One feature per branch — don't mix unrelated changes
3. Forward-integrate regularly: merge main into branch weekly
4. Run all tests after merge before closing the branch
5. Use a code review/approval process before merging to main
6. Document what each branch contains and when it's planned to merge
7. Lock critical rules during merge to prevent concurrent modifications
"""
    },
]


def seed_phase5a():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE5A:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase5a_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE5A)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 5A complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase5a()
