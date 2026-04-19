"""
Curated Pega Knowledge Base — Phase 5B (Medium Priority)
Covers: Declare OnChange/Trigger, Pulse/Notifications, JSON/XML Parsing,
        Application Versioning, JVM Tuning, Dynamic Layouts, CORS/CSRF,
        Prediction Studio/NBA

Run: python -m crawler.seed_kb_phase5b
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE5B = [
    {
        "url": "curated://pega-declare-onchange-trigger",
        "title": "Declare OnChange and Declare Trigger — Event-Driven Rules and Troubleshooting",
        "content": """# Declare OnChange and Declare Trigger — Troubleshooting

## Declare OnChange
Fires an activity when a specified property value changes. Common uses: audit logging, triggering notifications, updating related data.

### How It Works
1. You define which property to watch (e.g., pyStatusWork)
2. When that property changes, Pega runs the configured activity
3. Activity runs in the same transaction as the property change

### Common Issues

#### 1. Declare OnChange Not Firing
**Root Causes**:
- Property changed by direct database update (bypasses Pega change detection)
- Property set to the SAME value (no actual change detected)
- Declare OnChange rule not on the correct class in the hierarchy
- Rule is in a ruleset not in the application stack

**Fix**:
1. Verify the property is being changed through Pega (not direct SQL)
2. Check that the value actually changes (old != new)
3. Verify the rule is on the correct class (or a parent class)
4. Check ruleset stack includes the rule's ruleset

#### 2. Infinite Loop / Cascading Triggers
**Symptoms**: Stack overflow, performance hang, repeated activity execution
**Root Cause**: Declare OnChange activity modifies a property that triggers another Declare OnChange, creating a loop.
**Fix**: Add a guard condition in the activity (check a flag before processing). Never modify the watched property within the OnChange activity.

#### 3. Performance Impact
**Symptoms**: Slow saves, high CPU during case updates
**Root Cause**: Too many Declare OnChange rules firing on common properties
**Fix**: Minimize Declare OnChange rules. Use them only when necessary. Consider batch processing instead of per-change triggers.

## Declare Trigger
Fires an activity based on a case lifecycle event (case creation, case resolution, assignment creation, etc.). More structured than OnChange.

### Trigger Events
- **Case created**: Fires when a new case is instantiated
- **Case resolved**: Fires when case status changes to resolved
- **Assignment created**: Fires when a new assignment is created
- **Assignment completed**: Fires when an assignment is finished
- **Case status changed**: Fires on any status transition

### Common Issues

#### 1. Trigger Activity Not Running
**Root Causes**:
- Trigger event doesn't match the actual lifecycle event
- Activity has an error (check PegaRULES log)
- Trigger rule on wrong class
- Event fired but activity conditionally exits early

**Fix**: Use Tracer with "Declare" events enabled to see if the trigger fires. Verify the activity independently.

#### 2. Trigger Fires Multiple Times
**Root Cause**: Multiple saves on the case cause the event to fire repeatedly.
**Fix**: Add idempotency check in the activity. Use a flag property to track if trigger already processed for this event.

## Best Practices
1. Keep OnChange/Trigger activities lightweight — defer heavy work to queue processors
2. Always add guard conditions to prevent cascading triggers
3. Document all Declare rules — they are "invisible" in flows, making them hard to debug
4. Test with Tracer's Declare event filter to verify trigger behavior
5. Prefer Declare Trigger over OnChange when the event maps to a lifecycle event
"""
    },
    {
        "url": "curated://pega-pulse-notifications",
        "title": "Pulse Messages and Notifications — Configuration and Troubleshooting",
        "content": """# Pulse Messages and Notifications — Troubleshooting

## Overview
Pega has multiple notification mechanisms:
- **Pulse**: In-app messaging system for collaboration on cases (like comments/chat)
- **Notifications**: System alerts shown in the portal header bell icon
- **Correspondence**: Formal email communications (covered separately)
- **Push Notifications**: Mobile app notifications (Pega Mobile)

## Pulse Messages
Pulse allows users to post messages, mention other users (@mentions), and attach files within the context of a case.

### Common Pulse Issues

#### 1. Pulse Tab Not Visible on Case
**Root Causes**:
- Pulse not enabled for the case type
- UI template/harness doesn't include the Pulse widget
- User's access group doesn't have Pulse privileges

**Fix**:
1. Enable Pulse: Case Type → Settings → Collaboration → Enable Pulse
2. Check harness/portal includes the Pulse gadget
3. Verify user access group has Pulse-related privileges

#### 2. @Mentions Not Sending Notifications
**Root Causes**:
- Notification channel not configured for the mentioned operator
- Email delivery failing (SMTP issues)
- Mentioned user doesn't exist or ID is wrong

**Fix**:
1. Check operator's notification preferences
2. Verify email account configuration for notifications
3. Test with a known-good operator first

#### 3. Pulse Messages Not Persisting
**Root Causes**: Case not saved after posting Pulse message (if in deferred save mode)
**Fix**: Pulse messages are typically saved immediately. Check if custom logic is interfering.

## Notification Rules
Notification rules send lightweight alerts to users (in-app, email, or push).

### Configuration
1. Create Notification rule (Records → Process → Notification)
2. Define channel: In-app, Email, Push, or SMS
3. Set recipients: specific operator, work party role, or expression
4. Define message template with property substitution
5. Trigger from a flow step or activity

### Common Notification Issues

#### 1. In-App Notifications Not Appearing
**Root Causes**:
- Bell icon widget not in the portal harness
- Notification rule not triggered (check flow)
- WebSocket connection for real-time notifications not established

**Fix**:
1. Verify portal harness includes the notification widget
2. Use Tracer to confirm notification rule fires
3. Check browser console for WebSocket connection errors

#### 2. Notification Emails Not Sent
**Same causes as Correspondence email issues**: SMTP config, email account, agent not running.
**Fix**: Check email account, SMTP connectivity, and email agent status.

## Best Practices
1. Use Pulse for informal collaboration, Notifications for system alerts, Correspondence for formal communications
2. Don't over-notify — notification fatigue causes users to ignore all alerts
3. Allow users to configure notification preferences
4. Test notifications in non-production first
"""
    },
    {
        "url": "curated://pega-json-xml-parsing",
        "title": "JSON and XML Parsing — Parse Rules, Transforms, and Troubleshooting",
        "content": """# JSON and XML Parsing in Pega — Troubleshooting

## Overview
Pega processes JSON and XML data from integrations (REST/SOAP connectors), file imports, and service rules. Parse rules and data transforms handle the mapping between external formats and Pega's clipboard.

## JSON Handling

### Parse JSON (Connector Response)
- REST Connector → Response tab → Map to Clipboard
- Automatic mapping: JSON field names → Pega property names
- Nested objects → Page properties
- Arrays → Page List properties

### Common JSON Issues

#### 1. JSON Fields Not Mapping to Properties
**Root Causes**:
- Field name mismatch (case-sensitive!): `customerId` vs `CustomerID`
- Nested JSON not handled: `{"address": {"city": "NYC"}}` needs a Page property for "address"
- Array field mapped as single value instead of Page List
- Null values in JSON treated as missing (property not set)

**Fix**:
1. Check connector response mapping — verify field-to-property name matching
2. For nested objects: create a Page property and map the child object to it
3. For arrays: use Page List property and map array elements
4. Handle nulls explicitly in data transform post-processing

#### 2. JSON Parse Error / "Invalid JSON"
**Root Causes**:
- Response is not valid JSON (HTML error page, empty response, truncated)
- Character encoding mismatch (UTF-8 with BOM)
- Response is wrapped in extra characters (JSONP callback, XML wrapper)

**Fix**:
1. Log the raw response body to see what's actually returned
2. Validate response with a JSON validator
3. Strip BOM or wrapper characters before parsing
4. Handle non-JSON error responses gracefully

#### 3. Creating JSON for Connector Request
**How**: Use Data Transform to build the request page, or JSON Build/Parse activity
**Common error**: Property types don't match JSON types (sending string "123" instead of number 123)
**Fix**: Check property types match expected JSON schema

## XML Handling

### Parse XML (SOAP/File)
- SOAP Connector handles XML automatically via WSDL
- For custom XML: use XML Parse rules or XML Stream rules
- Map XML elements/attributes to Pega properties

### Common XML Issues

#### 1. XML Namespace Issues
**Error**: "Element not found" despite element existing in XML
**Root Cause**: XML namespaces not configured in parse rule
**Fix**: Add namespace mappings to the parse rule. Use namespace-aware XPath expressions.

#### 2. XML Attribute Values Not Captured
**Root Cause**: Parse rule maps elements but not attributes
**Fix**: Use `@attributeName` syntax in XPath to capture attribute values

#### 3. Large XML Causing Memory Issues
**Root Cause**: Entire XML loaded into memory (DOM parsing)
**Fix**: Use XML Stream rule for large documents — processes XML in chunks (SAX-style)

## Best Practices
1. Always validate incoming JSON/XML before processing
2. Handle missing/null fields gracefully (defaults, error messages)
3. Use XML Stream for files larger than 10MB
4. Log raw request/response during development for debugging
5. Test with edge cases: empty arrays, null values, special characters, large payloads
"""
    },
    {
        "url": "curated://pega-application-versioning",
        "title": "Application and Ruleset Versioning — Strategy, Lock/Unlock, and Troubleshooting",
        "content": """# Application and Ruleset Versioning — Troubleshooting

## Overview
Pega uses a three-part versioning scheme: **Major.Minor.Patch** (e.g., 01-01-01). Version management controls what's editable, what's deployed, and what's locked for production.

## Version States
- **Open**: Rules can be created and modified freely
- **Locked**: Rules are read-only. Used for production-deployed versions.
- **Archived**: Older versions kept for reference but not actively used

## Versioning Strategy
```
Development: MyApp:01-02-01 (open — developers work here)
QA:          MyApp:01-01-02 (locked — deployed to QA for testing)
Production:  MyApp:01-01-01 (locked — running in production)
```

### Common Versioning Issues

#### 1. "Ruleset version is locked, cannot modify"
**Root Causes**:
- Trying to edit a rule in a locked ruleset version
- Forgot to create a new version for development

**Fix**:
1. Create a new minor or patch version: MyApp:01-01-01 → MyApp:01-01-02
2. OR unlock the version (NOT recommended for production versions)
3. Check application rule → which version is "current" for development

#### 2. Wrong Version of Rule Executing
**Root Causes**:
- Multiple versions in the ruleset stack — higher version picked
- Application ruleset list has wrong version order
- Locked version has old rule, new version's rule not in the stack

**Fix**:
1. Check application definition → Rulesets tab → version list and order
2. Verify the active development version is in the stack
3. Use Rule Resolution to see which version is selected

#### 3. Patch vs Minor vs Major — When to Use
- **Patch** (01-01-01 → 01-01-02): Bug fixes, small changes. Production hotfixes.
- **Minor** (01-01-xx → 01-02-01): New features, enhancements. Sprint/release cycles.
- **Major** (01-xx-xx → 02-01-01): Major rework, breaking changes. Rare.

#### 4. Version Conflicts After Merge
**Root Cause**: Branch was based on version 01-01-01 but main is now 01-02-01
**Fix**: Re-merge with the current main version. Keep branches aligned with the target version.

## Best Practices
1. Lock every version that's deployed to QA or Production
2. Use patch versions for hotfixes, minor versions for feature work
3. Never unlock a production version — create a new patch instead
4. Keep a clear log of what changed in each version
5. Align team on versioning conventions at project start
"""
    },
    {
        "url": "curated://pega-jvm-tuning",
        "title": "JVM Tuning for Pega — Heap, GC, Thread Pools, and Troubleshooting",
        "content": """# JVM Tuning for Pega — Troubleshooting

## Overview
Pega runs on the JVM (Java Virtual Machine). JVM configuration directly impacts performance, stability, and scalability. Key areas: heap memory, garbage collection, and thread pools.

## Heap Memory

### Recommended Settings
- **Initial heap (-Xms)**: Set equal to max heap (avoids resize overhead)
- **Max heap (-Xmx)**: Depends on workload. Typical: 4GB-16GB per node.
- **Metaspace**: `-XX:MaxMetaspaceSize=512m` (for rule compilation cache)

### Sizing Guidelines
| User Count | Recommended Heap | Notes |
|-----------|-----------------|-------|
| < 100 concurrent | 4-6 GB | Small installation |
| 100-500 concurrent | 8-12 GB | Medium installation |
| 500+ concurrent | 12-16 GB | Large installation, consider multiple nodes |

### Common Heap Issues

#### OutOfMemoryError: Java heap space
**Root Causes**: Clipboard bloat, large data pages, memory leaks in custom Java
**Fix**: Increase heap as temporary measure. Profile with heap dump analysis. Fix root cause (see Clipboard Management doc).

#### OutOfMemoryError: Metaspace
**Root Causes**: Too many compiled rules, class loader leak
**Fix**: Increase MaxMetaspaceSize. Check for excessive rule compilation.

## Garbage Collection

### Recommended GC for Pega
- **G1GC** (recommended for Pega 8.x+): `-XX:+UseG1GC`
- Good balance of throughput and pause times
- Self-tuning for most workloads

### GC Tuning Parameters
```
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200        # Target max pause time
-XX:G1HeapRegionSize=16m        # Region size (auto-calculated if omitted)
-XX:+ParallelRefProcEnabled     # Parallel reference processing
-Xlog:gc*:file=gc.log:time      # GC logging (Java 11+)
```

### GC Issues
#### Long GC Pauses (> 1 second)
**Symptoms**: Application freezes, request timeouts
**Fix**: Enable GC logging, analyze pause causes. Common: heap too small, too many large objects, full GC triggered.

## Thread Pools

### Key Thread Pools
- **HTTP request threads**: Handle incoming user requests. Default varies by app server.
- **Background processing threads**: Agents, queue processors, data flows
- **Database connection pool**: Number of concurrent database connections

### Sizing
- HTTP threads: ~ 2x expected concurrent users (Tomcat default: 200)
- Background threads: Based on agent/QP count and data flow concurrency
- DB pool: ~ HTTP threads + background threads (don't over-provision)

## Monitoring
1. Enable GC logging in production (low overhead, invaluable for diagnosis)
2. Monitor heap usage via JMX, Admin Studio, or APM tools
3. Take thread dumps during performance issues (`jstack <pid>`)
4. Use heap dump analysis (Eclipse MAT, VisualVM) for memory leaks

## Best Practices
1. Set -Xms = -Xmx (avoid dynamic resizing)
2. Use G1GC for Pega 8.x+
3. Enable GC logging in all environments
4. Monitor heap usage trend — gradual increase indicates memory leak
5. Size heap based on actual usage, not guesswork — profile first
6. Don't over-allocate heap — leaves less memory for OS and file cache
"""
    },
    {
        "url": "curated://pega-cors-csrf-security",
        "title": "CORS, CSRF, and Web Security — Configuration and Troubleshooting",
        "content": """# CORS, CSRF, and Web Security in Pega — Troubleshooting

## CORS (Cross-Origin Resource Sharing)
Controls which external domains can call Pega APIs from a browser.

### Configuration
- Dev Studio → Security → CORS Policy
- Add allowed origins (e.g., `https://myapp.example.com`)
- Configure allowed methods (GET, POST, PUT, DELETE)
- Configure allowed headers (Authorization, Content-Type)

### Common CORS Issues

#### 1. "Access-Control-Allow-Origin" Error in Browser
**Symptom**: Browser blocks API call with CORS error
**Root Causes**:
- Frontend origin not in Pega's CORS whitelist
- Preflight OPTIONS request not handled
- CORS policy not applied to the service package

**Fix**:
1. Add the frontend URL to CORS allowed origins (exact match, including protocol and port)
2. Ensure OPTIONS method is allowed
3. Apply CORS policy to the specific service package

#### 2. Credentials Not Sent with CORS Request
**Root Cause**: `Access-Control-Allow-Credentials` not set, or origin is `*` (wildcard doesn't work with credentials)
**Fix**: Set specific origin (not `*`) and enable `Allow-Credentials` in CORS policy

## CSRF (Cross-Site Request Forgery)
Prevents unauthorized commands from a user's browser session.

### How Pega CSRF Works
- Pega generates a CSRF token for each session
- Token must be included in state-changing requests (POST, PUT, DELETE)
- Header: `X-CSRF-Token` or as a form field

### Common CSRF Issues

#### 1. "CSRF token validation failed" Error
**Root Causes**:
- Token not included in the request
- Token expired (session timeout)
- Token from a different session
- Custom integration not passing the CSRF token

**Fix**:
1. Get token: `GET <server>/prweb/api/v1/authenticate` returns token in response
2. Include token in subsequent requests: `X-CSRF-Token: <token>`
3. Refresh token if session is renewed
4. For testing: DSS `EnableCSRFProtection` can be disabled (NOT in production!)

## Security Headers
Recommended headers for Pega deployments:
```
X-Frame-Options: DENY (prevent clickjacking)
X-Content-Type-Options: nosniff (prevent MIME sniffing)
Strict-Transport-Security: max-age=31536000 (force HTTPS)
Content-Security-Policy: default-src 'self' (restrict content sources)
```
Configure in web server (Apache/Nginx) or application server settings.

## Best Practices
1. Never use `*` for CORS origins in production
2. Always enable CSRF protection in production
3. Set all recommended security headers
4. Use HTTPS everywhere — redirect HTTP to HTTPS
5. Regularly test security configuration with tools (OWASP ZAP, Burp Suite)
"""
    },
    {
        "url": "curated://pega-prediction-studio-nba",
        "title": "Prediction Studio and Next-Best-Action — Configuration and Troubleshooting",
        "content": """# Prediction Studio and Next-Best-Action (NBA) — Troubleshooting

## Overview
Pega's AI capabilities center around:
- **Prediction Studio**: Build, train, deploy, and monitor ML models
- **Next-Best-Action (NBA)**: Decision strategies that recommend the best action for each customer in real-time
- **Decision Strategies**: Visual flowchart of decision logic combining rules, models, and data

## Prediction Studio

### How It Works
1. Define a prediction (e.g., "Will customer churn?")
2. Upload training data or connect to data source
3. Pega auto-trains multiple models and selects the best performer
4. Deploy model to production
5. Monitor model performance over time (model decay detection)

### Common Prediction Issues

#### 1. Model Performance Declining
**Symptoms**: Prediction accuracy dropping over time
**Root Causes**: Data drift — real-world patterns changed since training
**Fix**: Retrain the model with recent data. Set up automatic retraining schedule. Monitor prediction vs actual outcomes.

#### 2. Model Not Available in Decision Strategy
**Root Causes**: Model not deployed, or deployed to wrong environment
**Fix**: Deploy from Prediction Studio. Verify the model ID matches what the strategy references.

#### 3. Scoring Errors in Production
**Root Causes**: Missing predictor properties at scoring time, model input format changed
**Fix**: Verify all predictor properties are populated before calling the model. Check data transform feeding the scorecard.

## Next-Best-Action (NBA)

### Architecture
1. **Triggers**: When to evaluate (case creation, customer interaction, scheduled)
2. **Eligibility**: Which actions are eligible for this customer
3. **Applicability**: Business rules filtering actions further
4. **Arbitration**: Rank eligible actions by priority, propensity, value
5. **Output**: Top N recommended actions

### Common NBA Issues

#### 1. No Actions Returned
**Root Causes**:
- Eligibility rules filter out all actions
- No actions defined for the customer segment
- Customer data incomplete (missing properties used in eligibility)
- Strategy has an error in a component

**Fix**:
1. Test the decision strategy in Prediction Studio → Run (with sample customer)
2. Check each stage: are actions making it past eligibility? applicability?
3. Verify customer data is complete
4. Check for errors in strategy components

#### 2. Wrong Action Prioritized
**Root Causes**: Arbitration weights not configured correctly, propensity model output unexpected
**Fix**: Review arbitration formula. Check propensity scores. Adjust weights (value, propensity, context).

#### 3. NBA Performance Issues
**Root Causes**: Strategy too complex, too many actions evaluated, expensive data lookups per action
**Fix**: Reduce action count, cache customer data, simplify eligibility rules, use pre-filtered action sets.

## Best Practices
1. Start with simple strategies — add complexity incrementally
2. Always have a fallback action (don't return empty results)
3. Monitor model performance weekly — set up decay alerts
4. A/B test strategy changes before full rollout
5. Log all NBA decisions for analysis and model retraining
"""
    },
    {
        "url": "curated://pega-dynamic-layouts-visibility",
        "title": "Dynamic Layouts and Visibility Conditions — Configuration and Troubleshooting",
        "content": """# Dynamic Layouts and Visibility Conditions — Troubleshooting

## Overview
Dynamic Layouts control which UI elements are visible, hidden, or disabled based on runtime conditions. They enable responsive, contextual user interfaces without multiple section variants.

## Visibility Types
- **Always visible**: Default — element always shown
- **Condition (expression)**: Show/hide based on property value (e.g., `.Status = "Open"`)
- **When rule**: Use a reusable When rule for complex conditions
- **Privilege**: Show only if user has a specific privilege
- **Never visible**: Hidden (useful for temporarily removing without deleting)

## Common Dynamic Layout Issues

### 1. Section Content Not Appearing
**Root Causes**:
- Visibility condition evaluates to false (property empty or wrong value)
- When rule has an error
- Nested dynamic layout — parent hidden, so children also hidden
- Refresh issue — condition changed but UI not refreshed

**Fix**:
1. Check the visibility condition — what property/expression does it use?
2. Use Clipboard viewer to check the property value at runtime
3. If When rule: test it independently (Dev Studio → rule → Run)
4. Add "Refresh When" on the section to trigger UI update when the condition property changes

### 2. "Refresh When" Not Working
**Root Causes**:
- Refresh-when property not matching what actually changes
- Property changes on a different page than what the section watches
- Refresh-when triggers too often (performance issue) or not at all

**Fix**:
1. Verify the refresh-when property path matches exactly
2. Ensure the property change happens on the same page context as the section
3. Test by changing the property value and checking if the section refreshes

### 3. Dynamic Layout Flickers / Jumps
**Symptoms**: UI elements appear/disappear causing layout shifts
**Root Causes**:
- Multiple rapid refreshes
- Visibility condition oscillates between true/false
- CSS not handling show/hide transitions smoothly

**Fix**:
1. Debounce the condition — don't toggle visibility on every keystroke
2. Use CSS transitions for smoother show/hide
3. Consider disabling instead of hiding (less jarring for users)

### 4. Repeating Grid + Dynamic Layout Issues
**Symptoms**: Visibility conditions don't work correctly inside repeating grids
**Root Causes**:
- Condition references wrong row context (.PropertyName vs .Row.PropertyName)
- Condition evaluates once for all rows instead of per-row
- Nested dynamic layouts in grids cause performance issues

**Fix**:
1. Ensure condition references properties within the row context
2. Use per-row expressions, not page-level conditions
3. Minimize dynamic layouts inside large grids (performance consideration)

## Best Practices
1. Use When rules for complex conditions (reusable, testable)
2. Always configure Refresh-When for conditions that change after page load
3. Test visibility with all possible data states (null, empty, various values)
4. Keep dynamic layouts simple — deeply nested conditions are hard to debug
5. Use privilege-based visibility for role-specific UI elements
"""
    },
]


def seed_phase5b():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE5B:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase5b_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE5B)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 5B complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase5b()
