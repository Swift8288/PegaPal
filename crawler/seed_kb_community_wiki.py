"""
Curated Pega Knowledge Base — Community Wiki
Covers real-world troubleshooting tips, best practices, and solutions
commonly shared on the Pega Community (collaborate.pega.com).

Topics:
  - Obj-Save/Obj-Open Locking & Concurrency
  - Queue Processor Deep Dive & Error Handling
  - Tracer Tips & Tricks
  - REST/SOAP Connector Troubleshooting
  - Declare Expression Circular References
  - Performance Tuning (Real-World)
  - Agent Troubleshooting
  - SSO / Authentication Errors
  - Data Page Caching Pitfalls
  - When Rules & Circumstancing
  - Clipboard Memory Issues
  - Pega Upgrade Gotchas
  - Deployment & RAP Issues
  - Search & Indexing (Elasticsearch/SRS)
  - Email (Send/Receive) Troubleshooting
  - Report Definition Performance
  - Decision Tables & Maps — Common Mistakes
  - Pega Unit Testing (PegaUnit) Best Practices
  - Branch & Merge Conflict Resolution
  - Constellation (DX) Migration Tips

Run: python -m crawler.seed_kb_community_wiki
"""

import json
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COMMUNITY_WIKI_DOCS = [
    # ─────────────────────────────────────────────────────────────
    # 1. Obj-Save Locking & Concurrency
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/obj-save-locking-concurrency",
        "title": "Community Wiki — Obj-Save Locking Issues & Concurrency in Pega",
        "content": """# Obj-Save Locking Issues & Concurrency — Community Solutions

## The Problem
One of the most frequently asked questions on Pega Community: "You cannot save a page that your session does not hold a lock on" or "Obj-Save failed: lock not held."

## Why This Happens
Pega uses optimistic locking to prevent two users (or two threads) from overwriting each other's changes on the same work object. When you open a case, Pega acquires a lock. If the lock is lost before you save, you get this error.

### Common Scenarios

#### 1. Lock Timeout
**Root Cause**: The default lock timeout is 30 minutes. If a user leaves a case open longer than that, the lock expires silently. On next save → error.
**Community Fix**:
- Increase `LockTimeout` DSS setting: Dev Studio → System → Settings → Dynamic System Settings → `Pega-Engine` / `locking/timeout` → set to 3600 (60 min) or higher
- Add a JavaScript heartbeat on the UI to refresh the lock periodically
- Warn users with an inactivity timer before the lock expires

#### 2. Multiple Tabs / Same Case
**Root Cause**: User opens the same case in two browser tabs. Only one tab holds the lock. Save from the other tab fails.
**Community Fix**:
- Enable the "case already open" warning: Application Settings → Case Management → Warn on duplicate case access
- Use `pxRequestor.pxReqLockInfo` to detect existing locks before opening

#### 3. Background Processing Conflicts
**Root Cause**: A queue processor or agent modifies the same case that a user has open. The background process steals the lock.
**Community Fix**:
- Use `Obj-Open` with the `pxObjClass` and lock=false for read-only background operations
- Use `Obj-Save-Cancel` to release locks explicitly in background activities
- Design flows so that background and user operations don't target the same case simultaneously

#### 4. Integration / Connector Lock Conflicts
**Root Cause**: An inbound service (REST/SOAP) creates or updates a case while a user also has it open.
**Community Fix**:
- Use `Obj-Refresh-and-Lock` in the service to acquire the lock before modifying
- Implement retry logic with exponential backoff in the service
- Consider a queue-based pattern: service writes to a queue, queue processor handles case updates serially

## Debugging Obj-Save Locking Issues

### Step 1: Identify the Lock Holder
```
Use Tracer or PAL to find:
- Who holds the lock (requestor ID)
- When the lock was acquired
- Whether the lock timed out
Check: SMA → System → Locking → Active Locks
```

### Step 2: Check Lock Timeout Settings
```
DSS: Pega-Engine / locking/timeout
Default: 1800 seconds (30 min)
Recommended for complex cases: 3600-7200 seconds
```

### Step 3: Check for Obj-Open-by-Handle
If code uses `Obj-Open-by-Handle` without proper lock parameters, the lock may not be acquired correctly. Always specify `pxObjClass` and set the lock parameter.

## Best Practices from the Community
1. **Always release locks explicitly** — Use `Obj-Save-Cancel` in error handlers and finally blocks
2. **Minimize lock duration** — Acquire late, release early
3. **Never hold locks across wait shapes** — Flow waits (assignments, timers) should release the lock
4. **Use Obj-Refresh-and-Lock** — Instead of separate Obj-Open + manual lock
5. **Monitor active locks** — Set up alerts for long-held locks (>1 hour)
6. **Test concurrent access** — Always test with multiple users accessing the same case"""
    },

    # ─────────────────────────────────────────────────────────────
    # 2. Queue Processor Deep Dive
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/queue-processor-deep-dive",
        "title": "Community Wiki — Queue Processor Deep Dive: Errors, Tuning & Best Practices",
        "content": """# Queue Processor Deep Dive — Community Knowledge

## What Are Queue Processors?
Queue processors handle asynchronous work in Pega. They run on agent nodes and pick up items from a queue table, processing them one at a time (or in parallel with multiple threads).

## Common Queue Processor Issues

### 1. Queue Processor Stuck / Not Processing
**Symptoms**: Items stay in "Pending-Processing" status, queue depth keeps growing.

**Debugging Steps (from community)**:
1. **Check if running**: SMA → System → Queue Processors → verify status is "Active"
2. **Check node assignment**: Queue processors run only on specific nodes. Verify the node is up and assigned: SMA → System → Nodes → check "Queue Processing" is enabled
3. **Check for broken items**: One bad item can block the queue. Query:
   ```sql
   SELECT * FROM {queue_table}
   WHERE pxStatus = 'Pending-Processing'
   ORDER BY pxCreateDateTime ASC
   LIMIT 10
   ```
4. **Check thread count**: SMA → Queue Processor → Thread Count. If threads = 0, the QP is paused
5. **Check logs**: Search for `QueueProcessor` or the specific queue name in PegaRULES log

**Common Fixes**:
- Restart the queue processor from SMA
- If a specific item is stuck, manually mark it as "Broken" using `pzQPBrokenStatus`
- Increase thread count for high-volume queues (but watch for DB connection pool exhaustion)
- Check for database locks — run `SELECT * FROM pg_locks` (PostgreSQL) or equivalent

### 2. Queue Items Failing Repeatedly
**Root Cause**: Item processing throws an exception, Pega retries, fails again → infinite loop.
**Community Fix**:
- Set `MaxRetries` on the queue processor (default is unlimited — dangerous!)
- Recommended: 3-5 retries with increasing delay
- Implement a dead-letter queue pattern: after max retries, move to a "failed" queue for manual review
- Add try-catch in the processing activity to log detailed errors before they bubble up

### 3. Performance — Queue Processing Too Slow
**Root Cause**: Single-threaded processing, or heavy processing per item.
**Community Tuning Tips**:
- **Increase threads**: Gradually increase from 1 → 4 → 8, monitor DB connections
- **Batch processing**: If items are independent, use the "batch size" setting (Pega 8.x+)
- **Dedicated node**: Assign queue processing to a dedicated background node, away from user traffic
- **Optimize the activity**: Profile with PAL — is it doing unnecessary Obj-Opens? Can you cache data page lookups?
- **Index the queue table**: Ensure proper indexes on pxStatus, pxCreateDateTime, and any custom columns used in selection criteria

### 4. Queue Items Created but Not Picked Up
**Root Cause**: Queue class mismatch or selection criteria filtering them out.
**Fix**:
- Verify the queue processor's "Class" matches the `pxObjClass` of enqueued items
- Check selection criteria — if you have custom WHERE clauses, ensure they match the item properties
- Verify the queue table exists and is accessible from the processing node

## Queue Processor vs Agent vs Job Scheduler
| Feature | Queue Processor | Agent | Job Scheduler |
|---------|----------------|-------|---------------|
| Trigger | Item in queue | Schedule/interval | Cron-like schedule |
| Ordering | FIFO (guaranteed) | No ordering | No ordering |
| Retry | Configurable | Manual | Manual |
| Scale | Multi-thread | Single per node | Single |
| Use for | Async case ops | Maintenance tasks | Batch jobs |

## Best Practices
1. **Always set MaxRetries** — unbounded retries are a production incident waiting to happen
2. **Monitor queue depth** — alert when depth > 1000 or items stay pending > 5 min
3. **Use dedicated nodes** — don't mix QP processing with interactive user nodes
4. **Log item IDs** — always log the pzInsKey being processed for traceability
5. **Test failure scenarios** — what happens when the database is down? When the item data is corrupt?
6. **Keep processing activities idempotent** — if an item is processed twice, it shouldn't cause data corruption"""
    },

    # ─────────────────────────────────────────────────────────────
    # 3. Tracer Tips & Tricks
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/tracer-tips-and-tricks",
        "title": "Community Wiki — Tracer Tips & Tricks for Efficient Debugging",
        "content": """# Tracer Tips & Tricks — Community Wisdom

## What Is the Tracer?
The Tracer is Pega's built-in debugging tool. It records step-by-step execution of activities, data transforms, when rules, and more. Think of it like a debugger's "step through" view.

## Accessing the Tracer
- **Dev Studio**: Dev Studio → Diagnostics → Tracer (or Ctrl+Shift+T in some versions)
- **Admin Studio**: Admin Studio → System → Monitoring → Tracer
- **URL shortcut**: Append `?pyActivity=pzTracer` to your Pega URL
- **Keyboard**: Press Ctrl+Alt+Shift+T on the case screen (browser-dependent)

## Essential Settings (Before You Start Tracing)

### Filter Wisely — Or Drown in Noise
The #1 community tip: **always set filters before starting the trace**. Unfiltered traces capture thousands of system events and make finding your issue nearly impossible.

**Recommended Filters**:
1. **RuleSet filter**: Only trace your application rulesets (exclude Pega-RULES, Pega-Engine, Pega-IntSvcs)
2. **Event type filter**:
   - For debugging activities: check "Activity Steps", "Property Sets", "DB Queries"
   - For debugging data transforms: check "Data Transform Steps"
   - For debugging when rules: check "When Evaluation"
   - Uncheck "Interaction Events" unless debugging UI rendering
3. **Thread filter**: If tracing a specific operation, filter to the specific requestor/thread

### Trace Settings That Save Time
- **Break on error**: Enable "Break" on `Exception` events — the tracer pauses when an error occurs so you can inspect the clipboard
- **Remote tracer**: Trace another user's session by entering their requestor ID (useful for reproducing issues another user reports)
- **Clipboard snapshots**: Enable "Show clipboard" at each step — slower but shows property values at each point
- **Max events**: Set a max (e.g., 10000) to prevent the tracer from consuming too much memory

## Advanced Tracer Techniques

### 1. Tracing Background Processes (Agents/Queue Processors)
**Challenge**: Agents and QPs don't have interactive sessions.
**Community Solution**:
1. Open Tracer and go to Settings → Requestor
2. Instead of your own session, enter the agent's requestor ID
3. Find it in SMA → System → Requestor Management → filter for "AGENT" or "BATCH"
4. Start tracing, then trigger the agent/QP — the tracer captures its execution

### 2. Tracing Services (REST/SOAP Inbound)
**Challenge**: Service calls are fast and you can't easily time the trace.
**Community Solution**:
1. Set up Tracer with filters for service rulesets
2. Enable "Auto-start on next service call" (Pega 8.3+)
3. Or: Add a `Log-Message` step at the top of the service activity with a known string → start tracer → send the request → search for that string in the trace

### 3. Comparing Before/After with Clipboard Diff
1. At step A, click "Save Clipboard" → saves a snapshot
2. Continue execution to step B
3. Click "Compare Clipboard" → shows a property-by-property diff
4. Useful for finding "where did this property get overwritten?"

### 4. Using Tracer XML Export for Deep Analysis
1. Export the trace as XML: Tracer → Actions → Export
2. Open in a text editor or XML viewer
3. Search for specific property names, class names, or error messages
4. Compare two trace exports to find differences between working/failing scenarios

## Common Tracer Issues

### 1. Tracer Shows Nothing
**Causes**: Wrong requestor selected, filters too restrictive, trace not started
**Fix**: Clear all filters, select "Current requestor", click Start, perform the action

### 2. Tracer Causes Performance Issues
**Causes**: Tracing with all events enabled, clipboard snapshots on, no max events
**Fix**: Use minimal filters, disable clipboard snapshots unless needed, set max events to 10000

### 3. Can't Trace Production
**Challenge**: Tracer adds overhead and may not be enabled in production.
**Alternative**: Use PAL (Performance Analyzer) for lightweight, always-on monitoring. PAL captures execution times and alert counts without the overhead of step-by-step tracing.

## Tracer vs PAL vs Log Files
| Tool | Overhead | Detail Level | Production Use | Best For |
|------|----------|-------------|---------------|----------|
| Tracer | HIGH | Step-by-step | Dev/QA only | Debugging specific issues |
| PAL | LOW | Summary stats | Yes | Performance monitoring |
| Log Files | LOW | Error/warn only | Yes | Error tracking |
| Clipboard Viewer | MEDIUM | Property state | Dev only | Inspecting runtime data |"""
    },

    # ─────────────────────────────────────────────────────────────
    # 4. REST Connector Troubleshooting
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/rest-connector-troubleshooting",
        "title": "Community Wiki — REST Connector Troubleshooting: Timeouts, Auth, Mapping",
        "content": """# REST Connector Troubleshooting — Community Solutions

## Overview
REST connectors are the primary way Pega integrates with external APIs. Community members report issues across authentication, timeouts, response mapping, and SSL.

## Top REST Connector Issues

### 1. Connection Timeout / Read Timeout
**Error**: "java.net.SocketTimeoutException: Read timed out" or "Connect timed out"
**Community Fixes**:
- **Connection timeout** (can't reach the server): Check network connectivity, firewall rules, proxy settings. Default is 30s.
  - DSS: `integration/rest/connectTimeout` — set to 10000 (10s) minimum
- **Read timeout** (server took too long to respond): External API is slow.
  - DSS: `integration/rest/readTimeout` — increase to 60000 (60s) for slow APIs
  - Better: Make the call async using a queue processor
- **Check proxy**: If Pega is behind a corporate proxy: Admin Studio → Integration → Connectors → Connection Settings → set HTTP/HTTPS proxy host/port
- **DNS resolution**: If the external URL uses a hostname, ensure DNS resolves from the Pega server. Test with `nslookup` from the app server.

### 2. Authentication Failures (401/403)
**Error**: "HTTP 401 Unauthorized" or "HTTP 403 Forbidden"

#### OAuth 2.0 Issues
- **Token expired**: Pega caches OAuth tokens. If the token TTL is shorter than Pega's cache, you get 401.
  - Fix: Set the `token.expiry.buffer` DSS to refresh tokens 60s before expiry
- **Wrong grant type**: Client Credentials vs Authorization Code — make sure you match the API's requirement
- **Scope missing**: Some APIs require specific scopes. Add them in the OAuth profile → Scopes field
- **Client ID/Secret wrong**: Double-check for trailing spaces (common copy-paste issue)

#### Basic Auth Issues
- **Base64 encoding**: Pega handles this automatically, but if you're using a custom header, encode `username:password` in Base64
- **Special characters in password**: URL-encode special chars, or use the Pega authentication profile instead of manual headers

#### API Key Issues
- **Header vs Query param**: Some APIs want the key in a header (`X-API-Key`), others as a query parameter (`?api_key=...`). Check the API docs.
- **Key rotation**: If the API rotated keys, update the DSS or authentication profile

### 3. Response Mapping Issues
**Problem**: Pega receives the response but properties are empty or wrong.

**Debugging Steps**:
1. Enable Tracer → filter for "Connect" events → inspect raw response body
2. Check the Data Transform that maps the response: is the JSON path correct?
3. Common JSON path mistakes:
   - API returns `{"data": {"items": [...]}}` but mapping starts at root → prefix with `.data.items`
   - Property names are case-sensitive: `firstName` ≠ `FirstName`
   - Arrays: Use `(1)` for first element in Pega (1-indexed), not `[0]`

**Community Tip**: Use the "Test Connectivity" button in the connector rule to see the raw response. Then use the "JSON to Clipboard" wizard to auto-generate mappings.

### 4. SSL/TLS Certificate Issues
**Error**: "sun.security.validator.ValidatorException: PKIX path building failed"
**Root Cause**: Pega's JVM doesn't trust the external API's SSL certificate.
**Fix**:
1. Download the server's certificate chain: `openssl s_client -connect api.example.com:443 -showcerts`
2. Import into Pega's JVM truststore:
   ```bash
   keytool -import -alias api-cert -keystore $JAVA_HOME/lib/security/cacerts -file api-cert.pem
   ```
3. Restart the Pega app server
4. For self-signed certs in dev/test: Add to the JVM truststore, never disable SSL verification in production

### 5. Large Response / Payload Issues
**Error**: OutOfMemoryError or very slow response processing
**Fix**:
- Enable streaming for large responses: Connector rule → Advanced → Enable Response Streaming
- Set `MaxResponseSize` DSS to a reasonable limit (default 10MB)
- Consider pagination: Request data in chunks instead of one large call
- For file downloads, use binary stream processing instead of loading into clipboard

## REST Connector Best Practices
1. **Always set timeouts** — never use defaults without thinking about the external API's SLA
2. **Use authentication profiles** — not hardcoded headers or DSS values
3. **Implement circuit breaker** — if the external API is down, fail fast instead of queueing retries
4. **Log request/response** — enable connector logging in non-production for debugging
5. **Externalize URLs** — use DSS or Application Settings, not hardcoded URLs in the connector rule
6. **Use Data Pages** — call REST connectors through data pages for built-in caching and scope management"""
    },

    # ─────────────────────────────────────────────────────────────
    # 5. Declare Expression Circular References
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/declare-expression-circular-reference",
        "title": "Community Wiki — Declare Expression Circular References: Detection & Resolution",
        "content": """# Declare Expression Circular References — Community Solutions

## What Is a Circular Reference?
A circular reference occurs when Declare Expressions form a dependency loop:
- Expression A depends on Property X
- Expression B depends on Property Y (which is set by Expression A)
- Expression A also depends on Property Y (which is set by Expression B)
→ Infinite calculation loop → StackOverflowError or Pega alert PEGA0026

## How to Detect Circular References

### Method 1: Pega's Built-In Detection
Dev Studio → Application → Integrity → Check Declare Expressions
- Pega shows a dependency graph and highlights circular chains
- Run this after any declare expression changes

### Method 2: Tracer Analysis
1. Start Tracer with "Declare Expression" events enabled
2. Trigger the calculation (open the case, change a property)
3. Look for repeating patterns: if the same expression fires more than 3 times in sequence, you likely have a circular reference

### Method 3: Clipboard Viewer
1. Open the case in question
2. Open Clipboard Viewer (Dev Studio → Diagnostics → Clipboard)
3. Check for properties with `pyCalculationStatus = "Calculating"` — indicates a stuck calculation

## Common Circular Reference Patterns

### Pattern 1: Direct A→B→A Loop
```
Declare Expression: TotalCost = ItemCost + Tax
Declare Expression: Tax = TotalCost * TaxRate
→ TotalCost depends on Tax, Tax depends on TotalCost
```
**Fix**: Break the loop — compute Tax from ItemCost directly:
```
Tax = ItemCost * TaxRate
TotalCost = ItemCost + Tax
```

### Pattern 2: Indirect Loop via Page Properties
```
Declare Expression on Parent: .SummaryAmount = SUM(.Items().Amount)
Declare Expression on Child: .Items().Amount = .Items().Qty * Parent.PriceMultiplier
Declare Expression on Parent: .PriceMultiplier = f(.SummaryAmount)
```
**Fix**: Remove the dependency from PriceMultiplier on SummaryAmount, or move PriceMultiplier calculation to an activity triggered on save.

### Pattern 3: Cross-Class Dependencies
```
Class A has Declare Expression: .Total = sum of Class B instances
Class B has Declare Expression: .AllocatedAmount = Class A .Total / count
```
**Fix**: Use a Data Transform triggered on save instead of Declare Expressions for one side of the dependency.

## Resolution Strategies

### Strategy 1: Replace One Declare with Data Transform
Convert one side of the circular dependency to a Data Transform invoked at a specific point (e.g., on case save). This breaks the automatic recalculation loop.

### Strategy 2: Use When Rules as Guards
Add a When rule condition to one Declare Expression so it only fires in specific circumstances, breaking the loop in the default case.

### Strategy 3: Flatten the Calculation
Combine multiple Declare Expressions into a single expression that computes the final result directly, without intermediate properties that create dependencies.

### Strategy 4: Use Declare OnChange Instead
Replace one Declare Expression with a Declare OnChange that triggers an activity. Activities don't participate in the declare network's dependency tracking, so they can't create circular references.

## Best Practices
1. **Draw the dependency graph** before creating declare expressions — arrows should form a DAG (directed acyclic graph), never a cycle
2. **Run integrity checks** after every declare expression change
3. **Avoid cross-page declare dependencies** — they're hard to reason about and prone to circularity
4. **Document declare dependencies** — add comments explaining what each expression depends on
5. **Prefer fewer, simpler expressions** over many interconnected ones"""
    },

    # ─────────────────────────────────────────────────────────────
    # 6. Performance Tuning (Real-World)
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/performance-tuning-real-world",
        "title": "Community Wiki — Real-World Pega Performance Tuning Tips",
        "content": """# Real-World Pega Performance Tuning — Community Tips

## Top Performance Killers (Community Consensus)

### 1. Clipboard Bloat
**Symptoms**: Slow page loads, high memory per requestor, OutOfMemoryError
**Root Causes**:
- Data pages loading too much data (no pagination, no filters)
- Page lists with thousands of entries kept in session scope
- Not removing temporary pages after use
**Community Fixes**:
- Use Thread scope for transient data, not Requestor scope
- Apply `When` conditions on data pages to filter at the source
- Use `Page-Remove` to clean up temporary pages after use
- Set `pxMaxRecords` on data page rules to cap result sizes
- Monitor clipboard size: SMA → Requestor Management → sort by clipboard size

### 2. Excessive Database Queries
**Symptoms**: Slow operations, high DB CPU, many similar queries in DB profiler
**Root Causes**:
- `Obj-Browse` or `RDB-List` without proper WHERE clauses
- Declare expressions triggering repeated DB lookups
- Data pages refreshing too often (wrong scope or short timeout)
**Community Fixes**:
- Use PAL: sort by "Database Time" → find the most expensive queries
- Add database indexes for frequently queried columns
- Use `RDB-List` with optimized SQL instead of `Obj-Browse` for bulk reads
- Cache data page results: use Node scope for reference data, Requestor scope for user-specific data
- Use `Obj-Open-by-Handle` instead of `Obj-Browse` when you know the exact key

### 3. Slow UI Rendering
**Symptoms**: Pages take 5+ seconds to render, browser freezes
**Root Causes**:
- Too many sections on a single screen (50+ visible sections)
- Auto-populate data pages loading synchronously on screen open
- Complex repeat grids with 100+ rows and embedded sections
**Community Fixes**:
- Use lazy loading for sections not visible on initial view
- Paginate repeat grids: show 20 rows max, add "Load More"
- Move data page population to background threads where possible
- Profile browser performance with browser DevTools → Performance tab
- Use Constellation DX API for better client-side rendering performance

### 4. JVM Garbage Collection Issues
**Symptoms**: Periodic freezes (1-5 seconds), sawtooth memory pattern, "GC overhead limit exceeded"
**Community Fixes**:
- Switch from `-XX:+UseParallelGC` to `-XX:+UseG1GC` (G1 is default in Java 11+)
- Set `-Xms` equal to `-Xmx` to avoid heap resizing: e.g., `-Xms8g -Xmx8g`
- Enable GC logging: `-Xlog:gc*:file=gc.log:time,uptime,level,tags`
- Analyze GC logs with GCViewer or Eclipse MAT
- Common tuning: `-XX:MaxGCPauseMillis=200 -XX:G1HeapRegionSize=16m`

### 5. Slow Report Definitions
**Symptoms**: Reports take minutes to generate, especially with large data sets
**Community Fixes**:
- Add database indexes for every column used in filters, sorts, and joins
- Limit report results: set max rows (10000 is a good cap)
- Use `Obj-List` or custom SQL instead of Report Definition for very complex queries
- Avoid `LIKE '%value%'` in report filters — not indexable, forces full table scan
- Pre-aggregate data with a nightly batch job for dashboard reports
- Consider Pega's Reporting DB (split reporting from transactional DB)

## Quick Wins — Community Favorites
1. **Enable static content caching**: Admin Studio → System → Performance → enable static content CDN or browser caching headers
2. **Compress responses**: Enable GZIP compression on the web server / load balancer
3. **Optimize rule resolution**: Keep the class hierarchy shallow (< 5 levels). Deep inheritance = slow rule resolution
4. **Connection pooling**: Tune DB connection pool: min=20, max=100, idle timeout=300s
5. **Prune clipboard on logout**: Use a cleanup activity on `pxLogout` to remove all session data
6. **Index PegaDATA tables**: Ensure `pc_work`, `pc_assign_worklist`, `pc_data_workattach` have proper indexes"""
    },

    # ─────────────────────────────────────────────────────────────
    # 7. Agent Troubleshooting
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/agent-troubleshooting",
        "title": "Community Wiki — Pega Agent Troubleshooting: Not Running, Errors, Scheduling",
        "content": """# Agent Troubleshooting — Community Knowledge

## What Are Agents?
Agents are scheduled background processes in Pega. They run activities at defined intervals (e.g., every 5 minutes) for maintenance tasks, data syncs, email processing, and SLA evaluations.

## Common Agent Issues

### 1. Agent Not Running
**Symptoms**: Agent shows "Disabled" or "Inactive" in SMA, scheduled work not happening.
**Debugging Steps**:
1. **Check SMA**: Admin Studio → System → Operations → Agents → find the agent → check status
2. **Check node assignment**: Agents run on specific nodes. Verify the agent is assigned to an active node: Agent rule → Agent Schedule → Node classification
3. **Check the schedule**: Agent rule → Schedule tab → verify interval is set and the agent is enabled
4. **Check RuleSet stack**: The agent rule's ruleset must be in the application stack on the running node
5. **Check logs**: Search for the agent's activity class/name in PegaRULES log

**Common Fixes**:
- Enable the agent: Agent rule → check "Enabled"
- Assign to correct node: Set the node classification (e.g., "BackgroundProcessing", "WebUser")
- Restart the agent from SMA: Agents → select → Restart
- If agent was disabled by a deployment, re-enable after deployment

### 2. Agent Running but Not Doing Anything
**Root Causes**:
- The agent's activity has no work to do (empty query result)
- The activity has an error early in execution (silently caught)
- The `Obj-Browse` or query in the activity returns no results due to a filter issue

**Debugging**:
1. Trace the agent's activity (see Tracer Tips for tracing agents)
2. Add `Log-Message` steps at key points in the activity
3. Check the query/browse conditions — is the WHERE clause correct?
4. Verify the activity runs successfully when executed manually (Dev Studio → Run)

### 3. Agent Running Too Frequently / Overlapping
**Symptoms**: Database contention, duplicate processing, high CPU
**Root Cause**: Agent interval is shorter than the time it takes to process all items. Previous run hasn't finished when the next one starts.
**Community Fixes**:
- Enable "Do not run if previous instance is still running" (enabled by default in Pega 8.x)
- Increase the interval to be longer than the worst-case processing time
- Move heavy processing to a queue processor instead — better suited for variable-length work
- Add a "last run time" check in the activity: skip if last run was < N minutes ago

### 4. Agent Errors Not Visible
**Root Cause**: Agent activities swallow exceptions without logging.
**Fix**:
- Add try-catch around all agent activity logic
- In the catch, use `Log-Message` to log the error details including stack trace
- Set up PEGA alert for agent failures: DSS `alerts/agents/failurethreshold`
- Use Pega's Alert mechanism: configure alerts for `PEGA0009` (agent execution failure)

## Standard Agents Every Admin Should Know
| Agent Name | Purpose | Default Interval |
|-----------|---------|-----------------|
| `Pega-IntSvcs-Queue` | Service request queue processing | 5 min |
| `Pega-ProCom-Work-SLA` | SLA deadline/goal evaluation | 5 min |
| `Pega-RULES-AdminCleanup` | Cleanup expired locks, sessions | 60 min |
| `Pega-RULES-IndexMaint` | Search index maintenance | 30 min |
| `Pega-ProCom-Work-Notify` | Send queued notifications | 5 min |

## Best Practices
1. **Never put heavy logic directly in agent activities** — agents should find work, then delegate to queue processors or activities
2. **Always log at the start and end** of agent execution with item counts
3. **Use node classification** — run agents on "background" nodes, not user-facing nodes
4. **Monitor with SMA dashboards** — set up agent health monitoring
5. **Test agent activities manually** before enabling the schedule"""
    },

    # ─────────────────────────────────────────────────────────────
    # 8. SSO / Authentication Errors
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/sso-authentication-errors",
        "title": "Community Wiki — SSO & Authentication Troubleshooting in Pega",
        "content": """# SSO & Authentication Troubleshooting — Community Solutions

## Common Authentication Architectures in Pega
1. **Basic Authentication** — username/password against Pega's internal directory
2. **LDAP/AD** — delegated to Active Directory or LDAP server
3. **SAML 2.0 SSO** — federated with identity providers (Okta, ADFS, Azure AD, Ping)
4. **OAuth 2.0** — token-based authentication for API access
5. **Kerberos / SPNEGO** — Windows integrated authentication (ticket-based)

## Top SSO Issues

### 1. SAML Assertion Errors
**Error**: "SAML assertion validation failed" or "Invalid signature"
**Community Debugging**:
1. Capture the SAML response: Browser DevTools → Network → find the POST to `/prweb/PRAuth/saml` → copy the `SAMLResponse` parameter
2. Decode it: Base64 decode the SAMLResponse → read the XML
3. Check: Is the certificate in the assertion matching Pega's configured IdP certificate?
4. Check: Is the `Audience` restriction matching Pega's entity ID?
5. Check: Is the assertion time-valid? Clock skew between IdP and Pega can cause "assertion expired"

**Common Fixes**:
- **Clock skew**: Sync NTP on both Pega and IdP servers. Add `clockSkewTolerance` DSS (default 300s, increase to 600s if needed)
- **Certificate mismatch**: Re-download the IdP signing certificate and upload to Pega's authentication service
- **Wrong NameID format**: Configure the IdP to send `emailAddress` or `unspecified` format matching Pega's expectations
- **Audience restriction**: Set Pega's entity ID to match exactly what the IdP is configured to send

### 2. LDAP Connection Failures
**Error**: "Unable to connect to LDAP server" or "Authentication failed: bind error"
**Community Debugging**:
1. Test LDAP connectivity from Pega server: `ldapsearch -h ldap.company.com -p 389 -D "bindDN" -w "password" -b "dc=company,dc=com"`
2. Check Pega's authentication service: Dev Studio → Integration → Authentication → find the LDAP service → verify host, port, bind DN
3. Check SSL/TLS: If using LDAPS (port 636), ensure the LDAP server's certificate is in Pega's JVM truststore

**Common Fixes**:
- **Port blocked**: Verify firewall allows Pega → LDAP on port 389 (LDAP) or 636 (LDAPS)
- **Bind DN wrong**: Use the full DN, not just the username. E.g., `CN=svc-pega,OU=ServiceAccounts,DC=company,DC=com`
- **Base DN wrong**: Verify the search base includes the OU where users are located
- **Password expired**: Service account passwords expire — set a reminder to rotate them
- **Referral chasing**: If LDAP returns referrals, configure Pega to follow them: DSS `authentication/ldap/referral` = `follow`

### 3. Users Can Log In but Have Wrong Access
**Root Cause**: Operator profile, access group, or role mapping is incorrect.
**Debugging**:
1. Check the operator record: Dev Studio → Records → Operator → search for the user
2. Verify the access group assignment in the operator record
3. For SSO: Check if the SAML assertion includes role/group attributes and if Pega's mapping is correct
4. Check the access group → application → role mapping

**Fix**:
- Update the operator provisioning map: Authentication Service → Mapping tab → map IdP groups to Pega access groups
- For automatic provisioning: Enable "Auto-create operators" and configure default access group, org, and work pool

### 4. Session Timeout / Unexpected Logout
**Root Cause**: Pega session timeout is shorter than IdP session timeout, or vice versa.
**Fix**:
- Align session timeouts: Pega's `requestor/timeout` DSS (default 1800s = 30 min) should roughly match the IdP's session timeout
- For SLO (Single Logout): Configure the SLO endpoint in both Pega and IdP
- Check if a load balancer is terminating sessions (sticky sessions may be required)

## Authentication Best Practices
1. **Use SAML 2.0 or OAuth 2.0** for production — not Basic Auth
2. **Rotate credentials regularly** — both service accounts and signing certificates
3. **Enable audit logging** for authentication events: DSS `audit/authentication` = true
4. **Test with multiple IdP accounts** — admin, regular user, and user with no access
5. **Document the SSO flow** — draw a sequence diagram showing browser → IdP → Pega"""
    },

    # ─────────────────────────────────────────────────────────────
    # 9. Data Page Caching Pitfalls
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/data-page-caching-pitfalls",
        "title": "Community Wiki — Data Page Caching Pitfalls: Stale Data, Scope, Refresh",
        "content": """# Data Page Caching Pitfalls — Community Lessons Learned

## Data Page Scopes — When to Use What

### Thread Scope
- Created per interaction (screen load), garbage collected when thread ends
- **Use for**: Temporary data needed only during a single operation
- **Pitfall**: Data is re-fetched on every screen load → performance hit if the data source is slow
- **Fix**: Move to Requestor scope if data is needed across multiple screens

### Requestor Scope
- Lives for the entire user session
- **Use for**: User-specific data that doesn't change during a session (e.g., user preferences, access rights)
- **Pitfall**: Data becomes stale if updated by another user or process during the session
- **Fix**: Set a refresh interval (e.g., 300 seconds) or call `pxRefreshOnNextAccess` when the data source changes

### Node Scope
- Shared across all requestors on a single JVM node
- **Use for**: Reference data shared by all users (e.g., country lists, product catalogs, config settings)
- **Pitfall #1**: On multi-node clusters, each node has its own copy — changes on one node don't propagate
- **Pitfall #2**: Large node-scope data pages consume JVM heap shared by all users
- **Fix**: Set a refresh interval (e.g., 600s). For immediate refresh, use `pxDataPageClearNode` agent

### Requestor scope with "Reload once per interaction"
- Hybrid: data is cached for the session but re-evaluated each time a new interaction starts
- **Use for**: Data that changes frequently but doesn't need to be 100% real-time (e.g., notification counts)

## Common Data Page Caching Mistakes

### Mistake 1: Using Node Scope for User-Specific Data
**Problem**: All users see the same data — security violation!
**Example**: Data page loads "my pending cases" with node scope → User A sees User B's cases
**Fix**: Always use Requestor or Thread scope for user-specific data. Add parameter keys (e.g., operator ID) if sharing a node-scope data page structure.

### Mistake 2: Not Setting Parameters as Keys
**Problem**: Data page `D_CustomerDetails` loaded with CustomerID=123, next access with CustomerID=456 → still returns data for 123 (cached!).
**Fix**: Mark `CustomerID` as a parameter key on the data page rule → Pega caches separate instances per parameter value.

### Mistake 3: Infinite Refresh Loop
**Problem**: Data page's data source triggers a property change → Declare OnChange fires → clears the data page → data page reloads → triggers property change → loop
**Fix**: Don't use Declare OnChange to clear the data page that triggers it. Use a different mechanism (e.g., timer-based refresh).

### Mistake 4: Data Page Loading Too Much Data
**Problem**: `D_AllCases` loads 50,000 cases into a node-scope data page → 500MB of heap consumed
**Fix**: Use report definition with pagination as the data source. Set `MaxRecords` parameter. Use parameterized filtering so only relevant data is loaded.

### Mistake 5: Not Handling Data Source Failures
**Problem**: Data page's REST connector times out → data page stores the error → all subsequent accesses return the error (cached!)
**Fix**: Enable "Reload on error" on the data page rule. Set a short refresh interval for error cases. Add an `onError` data transform to set a fallback value.

## Data Page Debugging Tips
1. **Clipboard Viewer**: Dev Studio → Diagnostics → Clipboard → search for `D_` to see all loaded data pages, their scope, and parameter values
2. **Data page inspector**: Click the data page in Clipboard Viewer → see refresh status, last load time, data source info
3. **Force refresh**: In a data transform or activity, use `@Default.pxRefreshOnNextAccess` = true to force reload
4. **Clear all**: SMA → Data Pages → "Clear all node-scope data pages" (use cautiously in production)"""
    },

    # ─────────────────────────────────────────────────────────────
    # 10. When Rules & Circumstancing
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/when-rules-circumstancing",
        "title": "Community Wiki — When Rules & Circumstancing: Common Mistakes and Best Practices",
        "content": """# When Rules & Circumstancing — Community Knowledge

## When Rules Overview
When rules evaluate a condition and return true/false. They're used everywhere: visibility conditions, validations, flow routing, declare expressions, access controls.

## Common When Rule Mistakes

### Mistake 1: When Rule Returns Unexpected Results
**Debugging Steps**:
1. Tracer → enable "When Evaluation" events
2. Execute the scenario → find the When rule in the trace
3. Inspect each condition row — which row evaluated to true/false?
4. Check property values in the clipboard at the time of evaluation

**Common Causes**:
- Property is empty/null (not the same as "" in Pega)
- Case sensitivity: "Active" ≠ "active" in string comparisons
- Date comparisons: comparing a date-time to a date (time portion causes mismatch)
- Embedded page reference wrong: `.Customer.Name` works, `Customer.Name` doesn't (missing leading dot)

### Mistake 2: When Rule Performance Issues
**Problem**: Complex when rules with database queries evaluated hundreds of times per screen.
**Fix**:
- Avoid database operations in when rules used for UI visibility — they fire on every render
- Cache the result: compute it once in a data transform, store in a property, reference the property
- Use simple property comparisons instead of complex expressions

### Mistake 3: Circumstanced When Rule Not Picked Up
**Problem**: You created a circumstanced version but Pega still uses the base rule.
**Root Causes**:
- Circumstance property value doesn't match exactly (trailing spaces, case mismatch)
- Circumstance template not configured on the base rule
- Rule resolution selects a different version (higher ruleset version overrides)

**Debugging**:
1. Dev Studio → Records → search for the When rule → view all versions
2. Check "Circumstance" column — is your circumstanced version listed?
3. Use the Rule Resolution inspector: Dev Studio → Rule Resolution → enter the rule name → see which version resolves

## Circumstancing Deep Dive

### What Is Circumstancing?
Circumstancing lets you create variant versions of a rule that apply in specific situations, without modifying the base rule. Think of it as conditional rule resolution.

### Types of Circumstancing
1. **Single property**: Rule varies by one property value (e.g., Country = "US" vs "UK")
2. **Multi-property**: Rule varies by combination of properties (e.g., Country + ProductType)
3. **Date-based**: Rule varies by date range (e.g., holiday pricing from Dec 20 to Jan 5)
4. **Template-based**: Define a circumstance template, then create instances (most flexible)

### Circumstancing Best Practices
1. **Use sparingly** — too many circumstanced rules make the application hard to understand and maintain
2. **Document the circumstance key** — add a description explaining when each variant applies
3. **Test all variants** — create test cases for each circumstance combination
4. **Prefer parameterized rules** over circumstancing when the variation is simple (e.g., a single threshold value)
5. **Use circumstance templates** for consistency — they enforce the same circumstance structure across rules

### When to Use Circumstancing vs Other Approaches
| Approach | Use When | Avoid When |
|----------|----------|------------|
| Circumstancing | Rule logic fundamentally different per variant | Simple value changes |
| When rule conditions | Logic is the same, just different thresholds | Completely different logic |
| Parameterized data pages | Data varies by input parameters | Logic varies, not just data |
| Application settings | Single configuration values | Complex logic changes |"""
    },

    # ─────────────────────────────────────────────────────────────
    # 11. Pega Upgrade Gotchas
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/pega-upgrade-gotchas",
        "title": "Community Wiki — Pega Upgrade Gotchas: What Breaks and How to Prepare",
        "content": """# Pega Upgrade Gotchas — Community Experience

## Pre-Upgrade Checklist (Community Consensus)

### 1. Run Application Guardrails
- Dev Studio → Application → Guardrails → run full scan
- Fix all Critical and High warnings before upgrading — they often become hard errors in newer versions
- Pay special attention to deprecated features and APIs

### 2. Run Database Integrity Checks
- SMA → System → Database → Integrity → run all checks
- Fix orphaned rules, broken references, and invalid rule configurations
- Back up the database before starting (obvious but often forgotten under time pressure)

### 3. Document Customizations
- List every OOTB (out-of-the-box) rule you've customized
- Pega upgrades may overwrite custom rules if they're in a Pega ruleset
- Move customizations to your application ruleset if they're currently in a Pega ruleset

### 4. Test Environment First
- Always upgrade a test/staging environment before production
- Run regression tests on the test environment
- Compare functionality before and after upgrade

## Common Things That Break During Upgrade

### 1. Custom Java Steps in Activities
**Problem**: Java methods or classes removed or renamed in newer Pega versions.
**Symptoms**: Compilation errors, ClassNotFoundException at runtime.
**Fix**: Review Pega's release notes for deprecated/removed Java APIs. Replace with supported alternatives. Common example: `HashStringUtils` methods moved between packages.

### 2. UI / Section Rendering Changes
**Problem**: Screens look different after upgrade — CSS changes, layout shifts.
**Symptoms**: Misaligned elements, missing styles, broken custom CSS.
**Fix**:
- Pega updates its UI framework periodically (especially in Constellation upgrades)
- Review custom CSS for references to Pega CSS classes that may have changed
- Use the "Skin" rule inspector to compare before/after styling

### 3. Security Policy Changes
**Problem**: Stricter default security settings in newer versions.
**Symptoms**: Features that worked before now blocked, CSRF errors, CORS rejections.
**Fix**: Review the upgrade guide's security section. Common: CSRF token enforcement tightened in 8.x, Content Security Policy headers added in 23.x.

### 4. Database Schema Changes
**Problem**: Pega adds/modifies tables and columns.
**Symptoms**: SQL errors in custom report definitions, broken RDB-List activities.
**Fix**: Re-generate report definitions after upgrade. Check custom SQL for hardcoded column names that may have changed.

### 5. Agent / Queue Processor Configuration Reset
**Problem**: Agent schedules or queue processor settings reset to defaults.
**Fix**: Document all custom agent/QP settings before upgrade. Re-apply them after upgrade. Use a configuration management script.

## Version-Specific Gotchas

### Upgrading to Pega 8.x (from 7.x)
- **Case Type structure changed**: Case types now use a different inheritance model
- **Skin → Theme migration**: Old skins need to be converted to the new Theme system
- **Admin Studio replaces SMA**: Learn the new admin interface
- **Java 11 required**: Ensure your JVM is updated

### Upgrading to Pega 23.x (from 8.x)
- **Constellation UI**: Consider migrating custom UI to Constellation components
- **DX API**: New API layer for headless/decoupled UI
- **Platform Security enhancements**: Review new default security settings
- **Cloud-native features**: New deployment model if moving to Pega Cloud

## Post-Upgrade Verification
1. Run smoke tests on all critical flows (case creation, assignment, routing, resolution)
2. Run PAL for 1 hour → compare performance metrics with pre-upgrade baseline
3. Check all agents and queue processors are running
4. Verify all integrations (REST/SOAP connectors) are working
5. Test SSO / authentication flows
6. Review Pega logs for new warnings or errors
7. Run guardrails scan again on the upgraded application"""
    },

    # ─────────────────────────────────────────────────────────────
    # 12. Deployment & RAP Issues
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/deployment-rap-issues",
        "title": "Community Wiki — Deployment & RAP Troubleshooting: Import Failures, Conflicts, Rollback",
        "content": """# Deployment & RAP Troubleshooting — Community Knowledge

## RAP (Rules Application Package) Basics
A RAP is a packaged set of rules exported from one environment and imported into another. It's Pega's primary deployment mechanism.

## Common RAP Issues

### 1. RAP Import Fails — "Rule already exists"
**Root Cause**: The target environment has a newer version of the rule, or a conflicting customization.
**Community Fixes**:
- **Check rule versions**: Compare the rule version in the RAP with the target. If target is newer, the import correctly skips it.
- **Force import**: Use "Import with overwrite" — but be careful, this replaces existing rules
- **Selective import**: Import only specific rulesets from the RAP, skip conflicting ones
- **Fix the conflict**: Open both versions, merge manually, then import

### 2. RAP Import Hangs / Very Slow
**Root Cause**: Large RAP with many rules, or database performance issue during import.
**Community Fixes**:
- Import during off-peak hours (fewer active users = less DB contention)
- Break the RAP into smaller packages (by ruleset or feature)
- Increase DB connection pool and transaction timeout for the import operation
- Check DB tablespace — imports need temporary disk space for staging

### 3. Missing Dependencies After Import
**Symptoms**: "Rule not found" errors after deployment, missing class definitions, broken references.
**Root Cause**: RAP was exported without including dependent rulesets.
**Fix**:
- Always include dependency rulesets in the RAP export
- Use Pega's dependency analyzer: Dev Studio → Application → Packaging → Include Dependencies
- Create a deployment checklist that lists all rulesets and their versions

### 4. Post-Import Issues — Features Not Working
**Common Causes**:
- **Cache not refreshed**: Rules are imported but the rule cache still has old versions
  - Fix: Clear rule cache from SMA → System → Caches → Clear All
- **Access group not updated**: New features require access group changes not included in the RAP
- **DSS not migrated**: Dynamic System Settings are often environment-specific and not included in RAPs
  - Fix: Maintain a DSS migration script per environment
- **Data types not generated**: After importing class definitions, regenerate database tables
  - Fix: SMA → Database → Table Utilities → Generate DDL and execute

## Deployment Manager (Pega 8.x+)

### Pipeline Setup Issues
**Problem**: Pipeline stages not progressing, deployments stuck in "Pending Approval".
**Fix**:
- Verify each stage has the correct application URL and credentials
- Check that the deployment manager operator has admin access on each target environment
- Review the pipeline configuration: merge target branch, approval requirements

### Merge Conflicts in Deployment Manager
**Problem**: "Merge conflict detected" when promoting from dev → test → prod.
**Community Approach**:
1. Pull the conflict details from Deployment Manager
2. Open the conflicting rules in Dev Studio on the target branch
3. Compare source and target versions side-by-side
4. Decide which version to keep (or manually merge)
5. Resolve in Dev Studio, then retry the promotion

## Deployment Best Practices
1. **Use Deployment Manager** (not manual RAP import/export) for Pega 8.x+
2. **Branch per feature**: Use Pega's branch/merge system, not one big development branch
3. **Always deploy to Test first**: Never deploy directly to Production
4. **Include a rollback plan**: Document how to revert each deployment
5. **Automate DSS migration**: Script environment-specific settings
6. **Tag your deployments**: Use meaningful names (e.g., "Release_2024Q1_v2.3")
7. **Smoke test immediately**: Run critical path tests right after deployment"""
    },

    # ─────────────────────────────────────────────────────────────
    # 13. Search & Indexing (Elasticsearch/SRS)
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/search-indexing-elasticsearch-srs",
        "title": "Community Wiki — Pega Search & Indexing (Elasticsearch/SRS) Troubleshooting",
        "content": """# Pega Search & Indexing Troubleshooting — Community Solutions

## Pega Search Architecture
Pega uses **Search and Reporting Service (SRS)** (Elasticsearch-based) for full-text search across cases, data instances, and rules. In older versions, it was embedded; in 23.x+, SRS is an external service.

## Common Search Issues

### 1. Search Returns No Results / Stale Results
**Root Cause**: Search index is out of sync with the database.
**Community Fixes**:
- **Rebuild the index**: SMA → Search & Reporting → Search Index → Rebuild for specific class or full rebuild
- **Check indexing queue**: SMA → Search & Reporting → Queue → verify items are being processed
- **Check SRS connectivity**: SMA → Search & Reporting → Health Check → verify SRS is reachable
- **Verify indexing is enabled**: DSS `search/indexing/enabled` must be `true`

### 2. Search Index Rebuild Takes Too Long
**Root Cause**: Large number of records (millions of cases), or SRS performance issues.
**Community Fixes**:
- Rebuild incrementally by class instead of full rebuild
- Run rebuild during off-peak hours
- Increase SRS resources (memory, CPU) — Elasticsearch is memory-hungry
- Increase batch size for indexing: DSS `search/indexing/batchsize` (default 200, increase to 500 for faster rebuild)
- Check SRS cluster health: `curl http://srs-host:9200/_cluster/health`

### 3. Search Performance — Slow Queries
**Root Cause**: Complex search queries, large index, or SRS under-resourced.
**Community Fixes**:
- Limit search scope: specify the class to search instead of searching all classes
- Use specific field searches instead of "all fields" wildcard
- Optimize SRS: increase JVM heap (`-Xms4g -Xmx4g` minimum), use SSD storage
- Check for too many search shards: `curl http://srs-host:9200/_cat/shards` — aim for < 1000 shards total
- Consider splitting the index by date (e.g., monthly indexes for case data)

### 4. SRS Connection Errors
**Error**: "Unable to connect to Search and Reporting Service"
**Fix**:
- Verify SRS is running: `curl http://srs-host:9200` should return version info
- Check network connectivity from Pega node to SRS (firewall, DNS)
- Verify the SRS URL in Pega: DSS `search/ElasticSearch/url` or Admin Studio → Search & Reporting → Connection
- If using TLS: ensure certificate trust is configured

### 5. Index Corruption
**Symptoms**: Search errors mentioning "shard failure", "index not found", or inconsistent results.
**Fix**:
1. Check index health: `curl http://srs-host:9200/_cat/indices?v` — look for RED/YELLOW status
2. If RED: identify the failing shard and try to recover: `curl -XPOST 'srs-host:9200/_cluster/reroute?retry_failed=true'`
3. If unrecoverable: delete the corrupt index and rebuild from Pega: SMA → Search → Rebuild Index

## Search Configuration Best Practices
1. **Separate SRS from Pega nodes** — SRS is resource-intensive, don't co-locate with Pega
2. **Allocate 50% of RAM to JVM heap** — but never more than 30GB (Elasticsearch limitation)
3. **Use SSD storage** — Elasticsearch is I/O intensive
4. **Monitor cluster health** — set up alerts for RED status and high JVM memory usage
5. **Back up the index configuration** — while data can be rebuilt, index templates and settings should be backed up"""
    },

    # ─────────────────────────────────────────────────────────────
    # 14. Email Troubleshooting
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/email-send-receive-troubleshooting",
        "title": "Community Wiki — Email (Send/Receive) Troubleshooting in Pega",
        "content": """# Email Troubleshooting in Pega — Community Knowledge

## Sending Email Issues

### 1. Emails Not Being Sent
**Debugging Steps**:
1. Check the email queue: SMA → Integration → Email → Outbound Queue → verify emails are queued
2. Check the email listener status: SMA → Integration → Email → Listener → verify it's running
3. Check SMTP settings: Admin Studio → Integration → Email → SMTP Configuration
4. Check Pega logs for SMTP connection errors

**Common Fixes**:
- **SMTP authentication**: Verify username/password. Many SMTP servers now require OAuth 2.0 instead of basic auth (e.g., Microsoft 365, Gmail)
- **Port blocked**: Common SMTP ports: 25 (unencrypted), 587 (STARTTLS), 465 (SSL). Verify firewall allows outbound to the SMTP server
- **TLS required**: Most modern SMTP servers require TLS. Enable it: Email Account → Use TLS → Yes
- **From address not authorized**: SMTP server may reject emails from unauthorized "From" addresses. Ensure the "From" address is authorized on the SMTP server

### 2. Emails Going to Spam
**Root Causes**: Missing SPF/DKIM/DMARC records, suspicious content, bulk sending.
**Fix**:
- Work with your email admin to add SPF, DKIM, and DMARC DNS records for the sending domain
- Use a consistent "From" address that matches the domain's SPF record
- Avoid spam trigger words in subject and body
- Implement throttling for bulk sends

### 3. Email Attachments Not Included
**Root Cause**: Correspondence rule doesn't reference attachments, or attachments exceed size limit.
**Fix**:
- In the correspondence rule, go to the Attachments section → add the attachment reference
- Check attachment size limits: DSS `correspondence/maxAttachmentSize` (default 10MB)
- For case attachments, use `pyAttachmentCategory` and `pyAttachmentName` properties to reference them

## Receiving Email (Email Listener)

### 1. Email Listener Not Processing Emails
**Debugging**:
1. SMA → Integration → Email → Listeners → check status
2. Verify IMAP/POP3 settings: host, port, credentials, folder name
3. Check network connectivity from Pega to the email server
4. Look for "EmailListener" in Pega logs

**Common Fixes**:
- **Wrong folder**: IMAP default folder is "INBOX" — must match exactly (case-sensitive on some servers)
- **OAuth required**: Microsoft 365 deprecated basic auth for IMAP in 2023. Use OAuth 2.0 authentication
- **SSL certificate**: Import the email server's SSL certificate into Pega's JVM truststore
- **Too many emails**: If inbox has thousands of emails, the listener may timeout. Process and archive older emails

### 2. Emails Received but Not Creating Cases
**Root Cause**: Email parsing rules not matching, or triage activity errors.
**Fix**:
- Check the email triage activity: Dev Studio → Integration → Email → Triage → verify the routing logic
- Verify the email-to-case mapping: which email fields map to which case properties?
- Test with a simple email first (plain text, no attachments) to rule out parsing issues

## Email Best Practices
1. **Use correspondence rules** — not hardcoded email logic in activities
2. **Template your emails** — use Pega's correspondence fragments for consistent branding
3. **Test in non-prod first** — configure a test SMTP server (e.g., Mailtrap) for development
4. **Monitor the outbound queue** — alert if queue depth > 100 or emails remain unsent > 30 min
5. **Log email events** — enable email audit logging for troubleshooting and compliance"""
    },

    # ─────────────────────────────────────────────────────────────
    # 15. Decision Tables & Maps
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/decision-tables-maps-mistakes",
        "title": "Community Wiki — Decision Tables & Decision Maps: Common Mistakes and Tips",
        "content": """# Decision Tables & Decision Maps — Community Tips

## Decision Tables

### What They Are
Decision tables evaluate conditions in a matrix (rows × columns) and return a result. Each row is a set of conditions; the first row that matches (top to bottom) returns its result.

### Common Mistakes

#### 1. Order of Rows Matters
**Problem**: A catch-all row at the top catches everything, specific rows below never evaluate.
**Example**:
```
Row 1: Status = * (any) → Result: "Default"
Row 2: Status = "Urgent" → Result: "Escalate"
→ Row 2 never fires because Row 1 matches everything
```
**Fix**: Put specific rows first, catch-all/default rows last.

#### 2. Missing "Otherwise" Row
**Problem**: No row matches → decision table returns empty → downstream logic fails silently.
**Fix**: Always add an "Otherwise" row at the bottom as a fallback. Log when it's hit — it indicates an unexpected input combination.

#### 3. Property Reference Errors
**Problem**: Decision table references a property that doesn't exist or is on the wrong page.
**Symptoms**: Evaluation returns unexpected results, no error reported.
**Fix**: Use the fully qualified property reference (e.g., `.pyStatusWork`, not just `Status`). Test with Tracer to see what values are being compared.

#### 4. Allowed List vs Free Text
**Problem**: Column uses "Allowed values" but the input doesn't match any allowed value exactly.
**Fix**: Check for case sensitivity, leading/trailing spaces, and ensure the property value matches the allowed list exactly.

### Decision Table Best Practices
1. **Test every row** — create test cases that trigger each row
2. **Use descriptive result columns** — not just "true/false" but meaningful action descriptions
3. **Keep tables small** — if > 20 rows, consider splitting into multiple tables or using a decision tree
4. **Version control** — decision tables are rules, so they benefit from proper versioning and branching

## Decision Maps (Pega 8.x+)

### What They Are
Decision maps are a visual alternative to decision tables. They use a flowchart-like interface where conditions branch to different outcomes.

### Common Mistakes

#### 1. Missing Branch
**Problem**: Decision map doesn't handle all cases — some inputs fall through without a result.
**Fix**: Add a default branch at every decision point. Use the "Otherwise" connector.

#### 2. Overlapping Conditions
**Problem**: Two branches have overlapping conditions — which one wins?
**Behavior**: Pega evaluates branches in order (left to right, top to bottom). The first match wins.
**Fix**: Ensure conditions are mutually exclusive, or order them by specificity (most specific first).

#### 3. Performance Issues with Complex Maps
**Problem**: Decision map with 50+ nodes and external data lookups takes seconds to evaluate.
**Fix**: Minimize external lookups within the map. Cache lookup results in data pages. Simplify by splitting into sub-maps.

## Decision Table vs Decision Tree vs Decision Map
| Feature | Decision Table | Decision Tree | Decision Map |
|---------|---------------|--------------|-------------|
| Visual | Matrix/grid | Tree diagram | Flowchart |
| Best for | Simple conditions, few variables | Hierarchical decisions | Complex flows |
| Performance | Fast | Fast | Medium |
| Maintainability | Easy for < 20 rows | Good for hierarchical | Good for complex |
| Delegation | Yes (business users) | No | Yes (Pega 8.x+) |"""
    },

    # ─────────────────────────────────────────────────────────────
    # 16. Branch & Merge Conflict Resolution
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/branch-merge-conflict-resolution",
        "title": "Community Wiki — Branch & Merge Conflict Resolution in Pega",
        "content": """# Branch & Merge Conflict Resolution — Community Guide

## Pega's Branch/Merge System
Pega uses a branching system similar to Git but for rules. Developers create branches, make rule changes on their branch, then merge back to the main application.

## Common Merge Conflicts

### 1. Same Rule Modified by Two Developers
**Scenario**: Dev A and Dev B both modified the same data transform on different branches.
**Detection**: Merge → conflict detected → Pega shows both versions.
**Resolution Options**:
1. **Keep source**: Use Dev A's version (discard Dev B's changes)
2. **Keep target**: Use Dev B's version (discard Dev A's changes)
3. **Manual merge**: Open both versions side-by-side, create a merged version that includes changes from both

**Community Tip**: Before merging, have both developers review the diff. Often one developer's changes are a subset of the other's.

### 2. Rule Deleted on One Branch, Modified on Another
**Scenario**: Dev A deleted a section. Dev B added a new field to the same section.
**Resolution**: Usually keep the modification (Dev B's version) and discuss with Dev A why it was deleted. If deletion is correct, the new field needs to go elsewhere.

### 3. Structural Conflicts (Class Changes)
**Scenario**: Dev A added properties to a class. Dev B reorganized the class hierarchy.
**Resolution**: This is the hardest conflict. Usually requires:
1. Merging the class hierarchy changes first
2. Then re-applying the property additions to the new structure
3. Testing both features together

## Branch Best Practices (Community Consensus)

### 1. Short-Lived Branches
**Rule**: Branches should live no longer than 1-2 sprints (2-4 weeks max).
**Why**: The longer a branch lives, the more it diverges from main, and the harder the merge.
**Tip**: If a feature takes longer, merge intermediate milestones back to main.

### 2. One Feature Per Branch
**Rule**: Each branch should contain ONE feature or user story.
**Why**: Mixing features makes merge review harder and makes it impossible to deploy one feature without the other.

### 3. Merge Main into Your Branch Regularly
**Rule**: At least weekly, merge main → your branch (forward integrate).
**Why**: Catches conflicts early when they're small and easy to resolve.

### 4. Review Before Merge
**Rule**: Have another developer review the merge before it's committed.
**Tooling**: Use Pega's built-in merge review UI, or export a rule diff report.

### 5. Lock Shared Rules
**Tip**: If a critical rule (e.g., main flow, core data transform) will be modified, communicate with the team. Consider locking the rule in the branch to prevent concurrent modifications.

## Merge Troubleshooting

### Merge Hangs / Takes Too Long
**Cause**: Branch has too many rules (500+), or database is slow.
**Fix**: Merge in smaller batches (by ruleset). Increase DB timeout for merge operations.

### Rules Missing After Merge
**Cause**: Rule was on the branch but not merged (skipped due to conflict resolution).
**Fix**: Check the merge log: Dev Studio → Application → Branches → Merge History → review each rule's merge status.

### Post-Merge Errors
**Cause**: Merged rules reference other rules that weren't included in the merge.
**Fix**: Run Application Guardrails after every merge. Test the merged application immediately."""
    },

    # ─────────────────────────────────────────────────────────────
    # 17. Constellation (DX) Migration Tips
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/constellation-dx-migration-tips",
        "title": "Community Wiki — Constellation (DX) Migration Tips & Common Issues",
        "content": """# Constellation (DX) Migration — Community Experience

## What Is Constellation?
Constellation is Pega's modern UI architecture (replacing the traditional "harness + section" model). It uses a component-based approach where the server provides data via the DX API and the client renders it using React-based components.

## Why Migrate to Constellation?
1. **Better performance**: Client-side rendering, less server round-trips
2. **Mobile-first**: Responsive design out of the box
3. **Consistent UX**: Standard component library ensures consistency
4. **Easier upgrades**: UI changes don't break custom sections (the component library handles rendering)
5. **Headless capability**: DX API can serve any frontend (React, Angular, mobile native)

## Migration Approach (Community-Recommended)

### Phase 1: Assessment
1. Inventory all custom sections, harnesses, and UI components
2. Identify which use standard Pega patterns (easy to convert) vs heavy customization (harder)
3. Check if your application's case types are "Constellation-ready": Dev Studio → Case Type → check "Constellation compatible"
4. Run the Constellation Readiness tool (Pega 23.x+): Dev Studio → Application → Constellation → Readiness Assessment

### Phase 2: Hybrid Mode
1. Enable Constellation for new case types while keeping existing ones on traditional UI
2. Configure hybrid mode: Application rule → UI tab → set "UI Architecture" to "Constellation" for specific portals
3. Test each converted case type thoroughly — especially custom UI actions, validations, and visibility conditions

### Phase 3: Component Customization
1. For standard UI patterns (forms, grids, tabs), Constellation handles them automatically
2. For custom UI components, create Constellation DX components (React-based)
3. Use Pega's Component Gallery for available OOTB components before building custom ones

## Common Migration Issues

### 1. Custom Sections Don't Render
**Root Cause**: Constellation doesn't use traditional sections/harnesses. They must be converted to Constellation views.
**Fix**: Re-create the section content as Constellation views. Use "Constellation-ready" layout types (Region, Card, Grid) instead of legacy layouts.

### 2. Custom JavaScript/CSS Not Working
**Root Cause**: Constellation uses a controlled rendering environment. Custom `<script>` tags and inline CSS from traditional sections are ignored.
**Fix**: Convert custom JavaScript to DX components or use Constellation's extension points. Move CSS to the Constellation theme configuration.

### 3. Custom Buttons / Actions Not Appearing
**Root Cause**: Traditional flow actions, local actions, and custom buttons have a different mechanism in Constellation.
**Fix**: Define actions in the Case Type → Actions → configure which actions appear in the Constellation action bar.

### 4. Performance Regression After Migration
**Root Cause**: DX API calls replacing server-rendered views — if data pages aren't optimized, each API call triggers multiple data fetches.
**Fix**: Optimize data pages (caching, scope). Minimize the number of data pages loaded per view. Use Constellation's lazy loading for complex views.

### 5. Print / PDF Rendering Different
**Root Cause**: Constellation's client-side rendering doesn't produce the same print output as server-rendered harnesses.
**Fix**: Use Pega's correspondence rules or PDF generation for print-quality output instead of browser print.

## Constellation Best Practices
1. **Start with new case types** — don't try to migrate everything at once
2. **Use OOTB components** wherever possible — custom components increase maintenance cost
3. **Test on mobile** — Constellation is mobile-first, verify mobile rendering early
4. **Leverage the DX API** — use it for integrations, testing, and automation
5. **Train the team** — Constellation is a paradigm shift; invest in training before migration"""
    },

    # ─────────────────────────────────────────────────────────────
    # 18. Clipboard Memory Issues
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/clipboard-memory-issues",
        "title": "Community Wiki — Clipboard Memory Issues: OutOfMemory, Bloat, Diagnostics",
        "content": """# Clipboard Memory Issues — Community Troubleshooting

## What Is the Clipboard?
The clipboard is Pega's in-memory data store for a user's session. Every case you open, every data page you load, every temporary page you create — it all lives on the clipboard. Too much data = OutOfMemoryError.

## Diagnosing Clipboard Bloat

### Method 1: SMA Requestor Management
SMA → System → Requestor Management → sort by "Clipboard Size" (descending)
- Normal: 1-10 MB per requestor
- Concern: 50+ MB per requestor
- Critical: 200+ MB per requestor

### Method 2: Clipboard Viewer
Dev Studio → Diagnostics → Clipboard
- Browse all pages on the clipboard
- Check page sizes (expand each page → check property count)
- Look for page lists with thousands of entries

### Method 3: PAL (Performance Analyzer)
PAL → Memory tab → shows clipboard memory over time
- Sawtooth pattern is normal (allocate → GC → allocate)
- Steadily increasing pattern indicates a memory leak

## Common Causes of Clipboard Bloat

### 1. Data Pages Loading Too Much Data
**Example**: `D_AllCases` loads 50,000 cases into memory.
**Fix**: Add pagination or filtering. Use `pxMaxRecords` to cap results. Use Thread scope so data is released after use.

### 2. Not Removing Temporary Pages
**Problem**: Activities create temporary pages (`Page-New`) but never remove them.
**Fix**: Always use `Page-Remove` in the finally/cleanup section of activities. Use try-finally blocks.

### 3. Large Case Attachments in Memory
**Problem**: Opening a case with large attachments (PDFs, images) pulls attachment data into memory.
**Fix**: Use streaming/download approach instead of loading into clipboard. Limit attachment preview sizes.

### 4. Embedded Pages with Deep Nesting
**Problem**: Case has deeply nested page structures (5+ levels) with lists at each level.
**Fix**: Flatten the data model where possible. Use references (keys) instead of embedded copies. Lazy-load nested data on demand.

### 5. Session Scope Data Page Accumulation
**Problem**: Over a long session, user opens many cases → each loads data pages → memory grows.
**Fix**: Implement a cleanup mechanism: remove data pages for cases the user is no longer viewing. Use Thread scope where possible.

## OutOfMemoryError — Emergency Response

### Step 1: Identify the Cause
1. Check Pega logs for `OutOfMemoryError` — note the thread and timestamp
2. Generate a heap dump: Add `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/` to JVM args
3. Analyze with Eclipse MAT (Memory Analyzer Tool): open the heap dump → Dominator Tree → find the largest objects

### Step 2: Immediate Fix
1. Restart the affected node (clears all clipboards)
2. If recurring: increase JVM heap as a temporary measure (`-Xmx`)
3. Identify the specific requestor causing the issue: SMA → Requestor Management

### Step 3: Root Cause Fix
- Fix the data page or activity that's loading too much data
- Add clipboard cleanup to the application's logout activity
- Add monitoring alerts for high clipboard sizes

## Prevention Best Practices
1. **Set `pxMaxRecords`** on all data pages (never load unbounded data)
2. **Use Thread scope** as default — only use Requestor/Node scope when you need persistence
3. **Clean up in activities** — always have a cleanup/finally step
4. **Monitor clipboard sizes** — set up weekly reports from SMA
5. **Load test with realistic data** — test with production-scale data volumes, not just 10 test cases
6. **Profile with PAL regularly** — catch memory issues before they reach production"""
    },

    # ─────────────────────────────────────────────────────────────
    # 19. PegaUnit Testing Best Practices
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/pegaunit-testing-best-practices",
        "title": "Community Wiki — PegaUnit Testing Best Practices & Common Pitfalls",
        "content": """# PegaUnit Testing Best Practices — Community Guide

## What Is PegaUnit?
PegaUnit is Pega's built-in unit testing framework. It lets you test individual rules (activities, data transforms, when rules, decision tables) in isolation with defined inputs and expected outputs.

## Setting Up PegaUnit Tests

### Creating a Test Case
1. Dev Studio → Testing → PegaUnit → Create Test Case
2. Select the rule to test (e.g., a data transform)
3. Define test data: set input properties on the clipboard
4. Define assertions: what properties should equal after the rule executes
5. Run the test → pass/fail result

### Test Naming Convention (Community Recommendation)
```
Test_<RuleName>_<Scenario>
Example: Test_SetCasePriority_HighValueCustomer
Example: Test_ValidateAddress_MissingZipCode
```

## Common PegaUnit Mistakes

### 1. Not Testing Edge Cases
**Problem**: Test only the happy path, miss failures.
**Fix**: For each rule, test:
- Happy path (valid input → expected output)
- Empty/null input → correct error handling
- Boundary values (max length, max value, zero, negative)
- Invalid input types (string where number expected)

### 2. Test Data Not Realistic
**Problem**: Test with trivial data ("Test123") → misses real-world issues like special characters, Unicode, long strings.
**Fix**: Use production-like test data. Include names with apostrophes (O'Brien), addresses with special characters, and multi-byte characters.

### 3. Tests Depend on External Systems
**Problem**: Test calls a REST connector → fails when the external service is down.
**Fix**: Use PegaUnit's mock capabilities. Mock the connector response with a fixed JSON payload. Test the integration separately with integration tests.

### 4. Not Cleaning Up Test Data
**Problem**: Tests create real cases or data records → pollute the database.
**Fix**: Use `Obj-Delete` in the test teardown section. Run tests on a dedicated test environment. Use the "Rollback on completion" option for database-modifying tests.

### 5. Testing Too Much at Once
**Problem**: One test case tests an entire flow (20 steps) → hard to identify which step failed.
**Fix**: Test individual rules in isolation. Use integration/scenario tests for end-to-end flow testing (separate from unit tests).

## What to Test (Community Priority List)
1. **Data transforms** — most common and most testable (inputs → outputs)
2. **Decision tables/trees** — each row should have a test case
3. **When rules** — test true and false scenarios
4. **Validation rules** — test valid and invalid inputs
5. **Activities with business logic** — not framework activities, just your custom logic
6. **Declare expressions** — verify calculation results

## What NOT to Unit Test
1. **OOTB Pega rules** — Pega already tests these
2. **UI rendering** — use functional/UI testing tools instead (Selenium, Pega's Scenario Testing)
3. **Simple property mappings** — data transforms that just copy properties aren't worth testing
4. **Framework plumbing** — Obj-Open, Obj-Save, Page-New — trust the platform

## Running Tests in CI/CD
1. **Export test cases** with the application RAP
2. **Run via API**: Pega provides REST endpoints to execute PegaUnit tests
3. **Parse results**: Test results come back as XML/JSON — parse with your CI tool (Jenkins, GitLab CI)
4. **Fail the build**: Configure CI to fail if any PegaUnit test fails
5. **Coverage reporting**: Track which rules have tests and which don't — aim for > 80% coverage on business logic rules

## PegaUnit vs Scenario Testing
| Feature | PegaUnit | Scenario Testing |
|---------|----------|-----------------|
| Scope | Single rule | End-to-end flow |
| Speed | Fast (seconds) | Slow (minutes) |
| Dependencies | Isolated (mocked) | Real system |
| Use for | Business logic | User journeys |
| Run in CI | Yes (easy) | Yes (harder) |"""
    },

    # ─────────────────────────────────────────────────────────────
    # 20. Report Definition Performance
    # ─────────────────────────────────────────────────────────────
    {
        "url": "wiki://pega-community/report-definition-performance",
        "title": "Community Wiki — Report Definition Performance Tuning & Optimization",
        "content": """# Report Definition Performance — Community Tips

## Common Report Performance Issues

### 1. Report Takes Minutes to Load
**Root Causes**:
- No database indexes on filtered/sorted columns
- Returning too many rows (no LIMIT/TOP clause)
- Complex joins across multiple tables
- Using `LIKE '%value%'` which forces full table scan

**Community Fixes**:
- **Add indexes**: Identify columns used in WHERE, ORDER BY, and JOIN clauses → create database indexes
  ```sql
  CREATE INDEX idx_work_status ON pc_work (pxcreatedatetime, pystatuswork);
  ```
- **Limit results**: Set "Maximum rows" on the report definition (1000-5000 for interactive reports)
- **Optimize filters**: Use `=` instead of `LIKE` where possible. If LIKE is needed, use `LIKE 'value%'` (prefix search, indexable) instead of `LIKE '%value%'` (full scan)
- **Paginate**: Display 20-50 rows per page with server-side pagination

### 2. Report Shows Incorrect Data
**Root Causes**:
- Wrong class mapping (reporting on the wrong table)
- Missing join conditions → Cartesian product (too many rows)
- Aggregate functions (SUM, COUNT) applied to wrong columns
- Date filters using wrong timezone

**Debugging**:
1. Enable SQL tracing: Tracer → filter for "Database" events → see the actual SQL query
2. Copy the SQL and run it directly against the database to verify results
3. Check the class-to-table mapping: Dev Studio → Records → Database Table → verify the class maps to the expected table

### 3. Report Causes Database Lock Contention
**Root Cause**: Report runs a long-running SELECT that blocks other operations.
**Fix**:
- Add `NOLOCK` hint (SQL Server) or read-committed snapshot isolation (PostgreSQL)
- Pega setting: DSS `database/readUncommitted` = true (use with caution — may read dirty data)
- Run heavy reports against a reporting database replica, not the transactional database
- Schedule heavy reports to run during off-peak hours

### 4. Exported Report Is Empty or Incomplete
**Root Cause**: Export timeout or memory limit reached.
**Fix**:
- Increase export timeout: DSS `reports/export/timeout` (default 300s, increase for large exports)
- Reduce data: add filters to narrow the result set before exporting
- For very large exports (100K+ rows), use a scheduled activity that generates a CSV file instead of the UI export

## Report Definition Best Practices
1. **Always index filtered columns** — this is the single biggest performance improvement
2. **Set reasonable maximums** — don't let users run unbounded queries
3. **Use optimized functions** — `Obj-List` with custom SQL for complex reports vs standard report definitions
4. **Separate reporting from OLTP** — use a reporting database or read replica for heavy analytics
5. **Cache report results** — for dashboards that show the same data to all users, cache the results in a Node-scope data page
6. **Test with production-scale data** — a report that runs in 1s with 100 records may take 10 minutes with 1M records"""
    },
]


def seed_community_wiki():
    """Save all community wiki docs to raw_docs directory."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    total = len(COMMUNITY_WIKI_DOCS)
    logger.info(f"Seeding {total} Pega Community Wiki documents...")

    output_file = RAW_DOCS_DIR / "community_wiki.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(COMMUNITY_WIKI_DOCS, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {total} community wiki docs to {output_file}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"  Pega Community Wiki — {total} documents seeded")
    print(f"{'='*60}")
    for i, doc in enumerate(COMMUNITY_WIKI_DOCS, 1):
        print(f"  {i:2d}. {doc['title'][:70]}")
    print(f"\nSaved to: {output_file}")
    print(f"Run indexer to add to ChromaDB: python -m indexer.index_docs")

    return total


if __name__ == "__main__":
    seed_community_wiki()
