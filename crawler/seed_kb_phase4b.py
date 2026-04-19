"""
Curated Pega Knowledge Base — Phase 4B (One Stop Pega style)
Covers: Parallel Processing, Security Policies, Localization, Delegation,
        Pulse Notifications, Report Performance, Mobile/DX API

Run: python -m crawler.seed_kb_phase4b
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE4B = [
    {
        "url": "https://onestoppega.com/parallel-processing-troubleshooting",
        "title": "Parallel Processing — Split-Join, Split-ForEach, and Troubleshooting",
        "content": """# Parallel Processing — Split-Join, Split-ForEach, and Troubleshooting

## Overview
Parallel processing in Pega allows multiple paths in a flow to execute simultaneously. Two main patterns:
- **Split-Join**: Fixed number of parallel branches, all must complete before joining
- **Split-ForEach**: Dynamic number of parallel branches based on a page list (e.g., process each line item in parallel)

## How It Works
1. Flow reaches a Split shape
2. Multiple branches execute simultaneously (on separate threads)
3. Join shape waits for all (or some) branches to complete
4. Flow continues after join

## Common Parallel Processing Issues

### 1. Split-Join Never Completes
**Symptoms**: Case stuck at the join point indefinitely
**Root Causes**:
- One branch has an error and doesn't reach the join
- Branch has an assignment waiting for human action
- Join configured for "All" but one branch took a different path
- Branch hits an infinite loop or deadlock

**Debug Steps**:
1. Check each branch — is any branch stuck or in error?
2. Look at the case's flow execution: Case → Process tab → view running flows
3. Use Tracer on each branch to identify where it's stuck
4. Check if join requires ALL branches or just SOME

### 2. Split-ForEach Skipping Items
**Symptoms**: Some page list items not processed
**Root Causes**:
- Source page list has fewer items than expected
- Error in one iteration causes remaining items to skip (depending on error handling)
- Thread pool exhaustion — not enough threads for all iterations
- Page list modified during iteration

**Fix**:
1. Verify page list item count before the split
2. Add error handling within each iteration branch
3. Check system thread pool configuration for parallel capacity
4. Avoid modifying the source page list during split-forEach processing

### 3. Data Conflicts Between Parallel Branches
**Symptoms**: Branches overwrite each other's data, wrong values after join
**Root Causes**:
- Branches modifying the same clipboard page (not thread-safe!)
- Shared data page (Node or Requestor scope) being modified concurrently
- No data isolation between parallel branches

**Fix**:
1. Each branch should only modify its own local data (thread-local pages)
2. Merge results AFTER the join, not during parallel execution
3. Use thread-scoped data pages within branches
4. Avoid Obj-Save on the same object from multiple branches

### 4. Performance Not Improving with Parallel Processing
**Symptoms**: Parallel processing is slower than or equal to sequential
**Root Causes**:
- Branches are too small (overhead of thread management exceeds the benefit)
- All branches hitting the same database/service (bottleneck is the target, not Pega)
- Thread pool too small — branches queued instead of running in parallel
- Serialized by database locks

**Fix**:
1. Only parallelize when branches have substantial work
2. Check if the external service/database can handle concurrent requests
3. Increase thread pool size in prconfig.xml
4. Monitor actual thread utilization during execution

## Best Practices
1. Use Split-Join for a fixed number of known branches
2. Use Split-ForEach for dynamic iterations over a page list
3. Keep parallel branches independent — no shared mutable state
4. Set timeouts on parallel branches to prevent indefinite waiting
5. Test with large page lists to verify scalability
6. Monitor thread pool utilization in production
"""
    },
    {
        "url": "https://onestoppega.com/security-policies-troubleshooting",
        "title": "Security Policies — Authentication, Password, Session, and Troubleshooting",
        "content": """# Security Policies — Authentication, Password, and Session Troubleshooting

## Overview
Security in Pega covers authentication (who are you?), authorization (what can you do?), and session management (how long can you stay?). Security issues are common after upgrades, new deployments, or policy changes.

## Authentication Methods
- **Basic**: Username + password against Pega's internal directory
- **LDAP/AD**: Authenticate against Active Directory or LDAP server
- **SAML 2.0**: Single Sign-On with identity provider (Okta, Azure AD, etc.)
- **OAuth 2.0 / OIDC**: Token-based authentication
- **Custom**: Pluggable authentication activity

## Common Security Issues

### 1. User Can't Log In — "Invalid credentials"
**Root Causes**:
- Wrong password (most common — check caps lock!)
- Account locked due to too many failed attempts
- Operator record disabled or expired
- LDAP/AD server unreachable
- Password expired (password expiration policy)

**Debug Steps**:
1. Check operator record: Records → Organization → Operator → is it active?
2. Check if account is locked: Operator → Security tab → lock status
3. Verify LDAP connectivity from Pega server (if using LDAP auth)
4. Check security policies: Configure → Security → Authentication Policies
5. Try resetting the password via admin tools

### 2. SSO (SAML/OAuth) Login Failing
**Error**: Redirect loop, "SAML response invalid", or blank screen after login
**Root Causes**:
- SAML assertion consumer URL mismatch (Pega URL vs IDP config)
- Clock skew between Pega server and Identity Provider (>5 minutes)
- Certificate mismatch (IDP signing cert not imported in Pega)
- Missing attribute mapping (IDP sends different attribute names)
- CORS/redirect URL not whitelisted

**Fix**:
1. Verify ACS URL in both Pega and IDP match exactly (protocol, port, path)
2. Sync server clocks (NTP)
3. Import IDP's signing certificate into Pega's authentication profile
4. Map IDP attributes to Pega operator properties (check attribute names)
5. Check Pega logs for detailed SAML error messages

### 3. User Logged Out Unexpectedly
**Root Causes**:
- Session timeout too short (default: 30 minutes of inactivity)
- Requestor timeout in prconfig.xml
- Load balancer session stickiness not configured
- Multiple tabs/windows causing session conflicts
- Security policy enforcing single-session-per-user

**Fix**:
1. Check session timeout: DSS → `Pega-RULES/requestor/timeoutMinutes`
2. Verify load balancer sticky session configuration
3. Check security policy for concurrent session limits
4. Increase timeout if appropriate for the use case

### 4. "Access Denied" After Login
**Symptoms**: Login succeeds but user sees "You don't have access" or blank portal
**Root Causes**:
- Operator not assigned to correct access group
- Access group doesn't have the application's role
- Portal rule missing from the access group
- Work pool not included in access group (can't see cases)

**Fix**:
1. Check operator → Access Group field — is it the correct one?
2. Open access group → Roles tab → does it have the required application role?
3. Check access group → Portal tab → is a portal assigned?
4. Verify access group → Work pools include the application's case type classes

### 5. Password Policy Issues
**Symptoms**: User can't set new password, "Password doesn't meet requirements"
**Root Causes**:
- Complexity requirements changed after upgrade (Infinity '23 defaults are stricter)
- Minimum length, special characters, or history requirements not met
- Password same as username (often blocked by default)

**Fix**:
1. Review policy: Configure → Security → Password Policy
2. Communicate requirements to users (min length, complexity, history)
3. Adjust policy if requirements are unnecessarily strict for the use case
4. For service accounts: ensure auto-generated passwords meet the policy

## Security Best Practices
1. Use SSO (SAML/OAuth) for production — avoid basic auth
2. Set reasonable session timeouts (too short = frustrating, too long = risk)
3. Enable audit logging for security events
4. Regularly review operator access and disable unused accounts
5. Use HTTPS everywhere — never allow HTTP in production
6. Test authentication flows after every upgrade
"""
    },
    {
        "url": "https://onestoppega.com/localization-troubleshooting",
        "title": "Localization and Internationalization — Field Values, UI, and Troubleshooting",
        "content": """# Localization and Internationalization (i18n) — Troubleshooting

## Overview
Pega supports multi-language applications through Field Values (translations), locale settings, and language-specific rulesets. Localization issues typically appear as missing translations, wrong date/number formats, or encoding problems.

## How Localization Works
1. **Base rule** has default language content (usually English)
2. **Field Value rules** provide translations for labels, messages, and text
3. **Operator locale** determines which translations to show
4. **Application locale** sets default locale for all users

## Common Localization Issues

### 1. Labels Showing in Wrong Language / Not Translated
**Symptoms**: UI shows English labels even though user locale is set to French/Spanish/etc.
**Root Causes**:
- Field Value rules don't exist for the target language
- Operator locale not set correctly
- Ruleset containing translations not in the application stack
- Labels hardcoded in sections instead of using Field Values

**Fix**:
1. Check operator record → Locale/Language setting
2. Verify Field Value rules exist for the language: Records → SysAdmin → Field Value
3. Ensure the localization ruleset is in the application's ruleset stack
4. Replace hardcoded text in sections with property references using Field Values

### 2. Date/Number Format Wrong for Locale
**Symptoms**: Dates show MM/DD/YYYY instead of DD/MM/YYYY, or decimal separator wrong
**Root Causes**:
- Locale format settings not configured
- Custom formatting overriding locale defaults
- JavaScript date formatting not locale-aware
- Integration sending dates in wrong format for the user's locale

**Fix**:
1. Check locale settings for date/time/number formats
2. Use Pega's locale-aware formatting functions instead of custom formatting
3. Verify that integrations handle locale-specific formats
4. Test with multiple locales to catch format issues

### 3. Character Encoding Issues (Garbled Text)
**Symptoms**: Special characters (ñ, ü, 中文) appear as ???? or garbled
**Root Causes**:
- Database not using UTF-8 encoding
- Browser sending wrong character set
- Integration receiving data in different encoding
- prconfig.xml or web server not configured for UTF-8

**Fix**:
1. Verify database uses UTF-8: check database character set configuration
2. Ensure HTML meta tag includes `charset=UTF-8`
3. Check Content-Type headers on integrations
4. Set JVM file.encoding to UTF-8 in startup parameters

## Localization Best Practices
1. Never hardcode text — always use Field Values for user-facing text
2. Set up localization rules early in development, not as an afterthought
3. Test with RTL (right-to-left) languages if applicable (Arabic, Hebrew)
4. Use locale-aware formatting for dates, numbers, and currency
5. Include locale in your testing matrix (test every screen in every supported language)
"""
    },
    {
        "url": "https://onestoppega.com/delegation-troubleshooting",
        "title": "Delegation — Business Rule Changes by Business Users and Troubleshooting",
        "content": """# Delegation — Troubleshooting

## Overview
Delegation in Pega allows business users (non-developers) to modify specific rules through App Studio without developer intervention. Delegatable rules include: Decision Tables, Decision Trees, When Rules, Map Values, Constraints, SLAs, Correspondence, and some UI elements.

## How Delegation Works
1. Developer marks a rule as "Allow delegation" in Dev Studio
2. Developer specifies which access groups can modify the rule
3. Business user opens App Studio → finds the delegated rule
4. Business user modifies values within the allowed parameters
5. Changes take effect immediately (no deployment needed)

## Common Delegation Issues

### 1. Business User Can't See Delegated Rule in App Studio
**Root Causes**:
- Rule not marked as delegatable (Allow delegation checkbox not set)
- User's access group not in the delegation list
- User doesn't have App Studio access
- Rule is in a locked ruleset version

**Fix**:
1. Open rule in Dev Studio → check "Allow delegation" checkbox
2. Check "Delegate to" field → add the correct access group
3. Verify user has App Studio access in their access group
4. Ensure ruleset is not locked (delegation creates a new version)

### 2. Delegated Changes Not Taking Effect
**Root Causes**:
- Rule cache not refreshed after delegation
- Circumstanced version overriding the delegated rule
- Delegated change saved to wrong ruleset version
- Another rule with higher priority overriding the delegated version

**Fix**:
1. Clear rule cache from Admin Studio → Cache
2. Check rule resolution — is another version overriding?
3. Verify the delegated version's ruleset is in the active stack
4. Wait for cache refresh or trigger explicit refresh

### 3. Delegation Breaks Application Logic
**Symptoms**: Application errors after business user modifies a rule
**Root Causes**:
- Business user changed a decision table condition to an invalid value
- Required row in decision table deleted
- When rule logic changed to always return true/false (breaking flow logic)
- SLA timers set to unrealistic values

**Fix**:
1. Review the delegated rule's change history (audit trail)
2. Revert to previous version if needed
3. Add guardrails: use allowed values lists, validation on delegated fields
4. Provide better guidance in the rule's description for business users

## Delegation Best Practices
1. Only delegate rules that business users actually need to change
2. Add clear descriptions and help text to delegated rules
3. Use constrained allowed values to prevent invalid changes
4. Set up notifications when delegated rules are modified
5. Review delegated changes periodically for correctness
6. Test delegated rules with edge case values
"""
    },
    {
        "url": "https://onestoppega.com/dx-api-mobile-troubleshooting",
        "title": "DX API and Mobile — Headless UI, API Errors, and Troubleshooting",
        "content": """# DX API and Mobile — Troubleshooting

## Overview
The **DX API** (Digital Experience API) is Pega's REST API for headless/decoupled UI applications. It powers Constellation UI, mobile apps, and custom React/Angular frontends. It exposes case management, assignment, and data operations as REST endpoints.

## DX API Architecture
- **Base URL**: `<pega-server>/prweb/api/application/v2/`
- **Authentication**: OAuth 2.0 or Basic Auth
- **Endpoints**: Cases, Assignments, Data pages, Views, Actions
- **Response format**: JSON (Pega's DX JSON schema)

## Common DX API Issues

### 1. DX API Returns 401 Unauthorized
**Root Causes**:
- OAuth token expired or invalid
- Client credentials wrong (client ID/secret)
- Token endpoint URL incorrect
- CORS blocking preflight requests from browser

**Fix**:
1. Regenerate OAuth token and retry
2. Verify client credentials in Security → OAuth2 configuration
3. Check token endpoint URL matches your Pega server
4. For browser apps: configure CORS in Pega (Security → CORS Policy)

### 2. DX API Returns 403 Forbidden
**Root Causes**:
- Operator doesn't have API access role
- Access group missing required privileges
- Case type not exposed via channel interface
- DX API not enabled for the application

**Fix**:
1. Check operator's access group has API access
2. Verify the channel interface includes the case type
3. Enable DX API in application settings
4. Check if the specific endpoint requires additional privileges

### 3. Case Creation via API Fails
**Error**: `500 Internal Server Error` or validation errors on create
**Root Causes**:
- Required fields not passed in the request body
- Field names don't match Pega property names (case-sensitive!)
- Data format wrong (date format, number format)
- Channel interface doesn't allow case creation

**Fix**:
1. Check the API docs for required fields on case creation
2. Verify property names match exactly (use the DX API metadata endpoint)
3. Use ISO 8601 date format for dates
4. Test with minimal required fields first, then add optional fields

### 4. Assignment Action via API Returns Error
**Error**: "Action not available" or "Cannot perform action"
**Root Causes**:
- Assignment not in the right status for the action
- Action name doesn't match the configured flow action
- Case is locked by another user/session
- Validation errors on the action's flow action

**Fix**:
1. GET the assignment first to check available actions
2. Use the exact action ID from the assignment response
3. Check if case is locked (GET case → check lock status)
4. Include all required fields for the flow action's validation

### 5. DX API Performance Issues
**Symptoms**: Slow API response times, timeouts
**Root Causes**:
- Large payload (too many embedded pages returned)
- No pagination on list endpoints
- Each API call triggers expensive rule execution
- No caching on frequently-accessed data

**Fix**:
1. Use `?fields=` parameter to request only needed properties
2. Implement pagination for list endpoints
3. Optimize the underlying rules (data pages, connectors)
4. Use ETags/conditional requests for caching
5. Consider GraphQL-style field selection in newer Pega versions

## Mobile-Specific Issues

### 6. Mobile App Offline Mode Not Syncing
**Symptoms**: Changes made offline don't sync when back online
**Root Causes**:
- Sync configuration not set up for the case type
- Conflicts between offline changes and server-side changes
- Large payload exceeding sync limits
- Mobile client version incompatible with server version

**Fix**:
1. Verify offline configuration in Application rule
2. Implement conflict resolution strategy
3. Reduce data sync scope to only necessary fields
4. Ensure mobile client and server versions are compatible

## DX API Best Practices
1. Always use OAuth 2.0, never Basic Auth in production
2. Implement proper error handling for all API responses
3. Use field-level selection to minimize payload size
4. Cache reference data on the client side
5. Implement retry with exponential backoff for transient failures
6. Monitor API usage and set rate limits to protect the server
"""
    },
    {
        "url": "https://onestoppega.com/common-real-world-debugging-scenarios",
        "title": "Common Real-World Debugging Scenarios — Step-by-Step Resolution Guide",
        "content": """# Common Real-World Debugging Scenarios

## Scenario 1: Case Stuck in Processing — Won't Move Forward
**Problem**: User clicks Submit but the case doesn't advance to the next step.

**Step-by-step resolution**:
1. Open the case → check pyStatusWork (is it still "Open"?)
2. Check Assignments tab → is there a pending assignment? Who's it assigned to?
3. Open Tracer → reproduce the issue → look for:
   - Red error entries (exceptions, validation failures)
   - Flow action completion — does it fire?
   - Connectors — does the transition condition evaluate correctly?
4. Check browser console for JavaScript errors (common in Constellation)
5. Check if the case is locked by another session
6. Common fix: Validation rule is silently failing — check pyValidationMessages on clipboard

## Scenario 2: Case Created But Data is Missing
**Problem**: Case is created (manually or by integration) but key fields are blank.

**Step-by-step resolution**:
1. If created manually: Check the Create stage data transform — does it set the fields?
2. If created by integration: Check the service rule mapping (request → case properties)
3. Use Clipboard viewer right after creation to see what's populated
4. Check if data propagation from parent case is configured (if sub-case)
5. Check if a Declare Expression should be computing the values — is it firing?
6. Common fix: Property names are case-sensitive — "customerId" ≠ "CustomerID"

## Scenario 3: Slow Performance on Specific Screen
**Problem**: One screen takes 10+ seconds to load while others are fast.

**Step-by-step resolution**:
1. Enable PAL (Performance Analyzer) → load the screen → review the PAL report
2. Look for: slow data pages, expensive Declare Expressions, heavy reports
3. Check if the screen has a data page that loads excessive data (check record count)
4. Check for N+1 query pattern: repeating grid loading related data per row
5. Use browser Network tab to check if specific API calls are slow
6. Common fix: Add a database index on the property used in the slow query, or paginate the data page

## Scenario 4: Integration Returning Wrong Data
**Problem**: REST connector returns data but the values are wrong or missing fields.

**Step-by-step resolution**:
1. Test the connector independently: Dev Studio → rule → Run
2. Check the raw HTTP response (not just the mapped data)
3. Compare response fields with the data transform mapping
4. Check if the external API changed its schema or field names
5. Verify request parameters are correct (check clipboard for parameter values)
6. Common fix: API response field name changed (e.g., "customer_id" → "customerId") — update mapping

## Scenario 5: Report Shows Duplicate Records
**Problem**: Report Definition shows the same case/record multiple times.

**Step-by-step resolution**:
1. Check the report's Join configuration — wrong join produces cartesian product
2. Look for one-to-many joins that multiply rows (case → multiple assignments)
3. Check if the report includes both current and history table
4. Verify filter conditions — are you excluding resolved/deleted cases?
5. Check if the report's class maps to a table shared by multiple classes (class group)
6. Common fix: Add DISTINCT, or fix the join condition to be one-to-one, or add a filter for pyStatusWork

## Scenario 6: Agent/Queue Processor Stops Working After Deployment
**Problem**: Background job that worked in Dev stops after deploying to QA/Prod.

**Step-by-step resolution**:
1. Check Admin Studio → Agent Management → is the agent running?
2. Check node type classification — does the node include "BackgroundProcessing"?
3. Check if the agent schedule is pinned to a specific node ID that doesn't exist in QA
4. Review the agent activity — does it depend on environment-specific data/config?
5. Check DSS settings that might differ between environments
6. Common fix: Agent schedule was configured for a specific Dev node. Remove the node restriction so it runs on any BackgroundProcessing node.

## Scenario 7: Users See Different Data on Different Nodes
**Problem**: In a clustered environment, users sometimes see stale or inconsistent data.

**Step-by-step resolution**:
1. Check if the issue is Node-scoped data page caching
2. Verify cache invalidation is working across the cluster
3. Check Hazelcast/Ignite cluster membership — are all nodes in the cluster?
4. Look for direct clipboard modification (instead of proper data page refresh)
5. Check if the load balancer is routing to the correct node
6. Common fix: Change data page scope from Node to Requestor or Thread, or implement proper cache invalidation

## General Debugging Toolkit
| Tool | When to Use |
|------|-------------|
| **Tracer** | Step-by-step rule execution, data flow, error tracking |
| **Clipboard** | View current in-memory data state |
| **PAL** | Performance profiling — which rules are slow |
| **Log files** | Background processing errors, system-level issues |
| **Rule Resolution** | Which version of a rule is being used |
| **Admin Studio** | System health, agents, queues, cluster status |
| **Browser DevTools** | JavaScript errors, network calls, UI issues |
"""
    },
]


def seed_phase4b():
    """Write Phase 4B curated docs to raw_docs directory."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc in CURATED_DOCS_PHASE4B:
        slug = (
            doc["title"]
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("—", "-")
            .replace("'", "")
            .replace(",", "")
            .replace(".", "")
        )[:80]
        filename = f"phase4b_{slug}.json"
        filepath = RAW_DOCS_DIR / filename

        payload = {
            "url": doc["url"],
            "title": doc["title"],
            "content": doc["content"].strip(),
        }
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE4B)}] Saved: {doc['title']}")

    logger.info(f"\nPhase 4B complete — {count} documents saved to {RAW_DOCS_DIR}")
    logger.info("Next: python -m indexer.index_docs")


if __name__ == "__main__":
    seed_phase4b()
