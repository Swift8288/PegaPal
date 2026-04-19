"""
Curated Pega Knowledge Base — Phase 19 (PDC Alerts, PEGA Alert Codes & Exception Handling)
Comprehensive coverage of every major PEGA alert, PDC configuration, and exception debugging.

Run: python -m crawler.seed_kb_phase19
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE19 = [
    {
        "url": "curated://pega-pdc-complete-guide",
        "title": "PDC (Predictive Diagnostic Cloud) — Complete Setup and Monitoring Guide",
        "content": """# PDC (Predictive Diagnostic Cloud) — Complete Guide

## What is PDC?
PDC (Predictive Diagnostic Cloud) is Pega's cloud-based monitoring and diagnostic service. It collects alerts, performance metrics, and health data from your Pega environments and provides dashboards, trend analysis, and predictive insights to help you proactively identify and fix issues before they impact users.

## Key PDC Components

### 1. Alert Collection
- Pega nodes send alerts to PDC in real-time
- Alerts are categorized by severity: INFO, WARNING, ERROR, FATAL
- Each alert has a PEGA code (PEGA0001–PEGA0099) identifying the issue type
- Alerts include context: rule name, requestor, thread, timestamp, duration

### 2. Dashboards
- **Health Dashboard**: Overall system health across all nodes
- **Alert Dashboard**: Filterable view of all alerts by code, severity, time range, node
- **Performance Dashboard**: Trends for response times, throughput, resource usage
- **Prediction Dashboard**: AI-predicted issues based on alert patterns

### 3. Alert Subscriptions
- Configure email/SMS notifications for specific alert codes or severity levels
- Set up escalation rules (e.g., if PEGA0001 fires 10 times in 5 minutes, page oncall)
- Integrate with PagerDuty, ServiceNow, or custom webhooks

## PDC Configuration in Pega

### Enabling PDC
1. Navigate to **SMA → System → PDC settings** (or Dev Studio → System → Settings → PDC)
2. Enter PDC URL provided by Pega Cloud
3. Configure authentication (API key or OAuth)
4. Set alert forwarding: which alert codes to send to PDC
5. Test connection and verify alerts appear in PDC dashboard

### DSS Settings for PDC
| Setting | Description | Default |
|---------|-------------|---------|
| alerts/PDC/enabled | Enable/disable PDC forwarding | true |
| alerts/PDC/url | PDC endpoint URL | (provided by Pega) |
| alerts/PDC/batchSize | Number of alerts per batch | 50 |
| alerts/PDC/batchInterval | Seconds between batches | 30 |
| alerts/PDC/includeStackTrace | Send stack traces with alerts | false |

### Alert Threshold Configuration
Thresholds determine when alerts fire. Configure in **SMA → Alerts → Alert Thresholds**:
- **Interaction threshold**: How long an interaction runs before PEGA0001 fires (default: 20 seconds)
- **Query threshold**: How long a DB query runs before PEGA0002 fires (default: 5 seconds)
- **Clipboard threshold**: How large a clipboard page gets before PEGA0003 fires (default: 500KB)
- **Connect threshold**: How long a connector call takes before PEGA0004 fires (default: 10 seconds)

### Alert Destinations
Alerts can be sent to multiple destinations simultaneously:
1. **PegaALERT log file**: Local log file on each node (always enabled)
2. **PDC Cloud**: Centralized cloud dashboard
3. **Custom destination**: Custom Java class implementing AlertDestination interface
4. **Database**: Store alerts in pega_alert table for local reporting

## PDC Troubleshooting

### PDC Not Receiving Alerts
1. Check DSS: `alerts/PDC/enabled` must be `true`
2. Verify network: Pega node must be able to reach PDC URL (check firewall/proxy)
3. Check authentication: Expired API key or OAuth token
4. Check batch settings: If batchInterval is too high, alerts are delayed
5. Check PegaRULES log for PDC connection errors

### PDC Showing Stale Data
- Check node clock synchronization (NTP) — time skew causes stale-looking alerts
- Verify all nodes are forwarding (some nodes might have PDC disabled)
- Check PDC retention policy — old alerts may be purged

### Too Many Alerts (Alert Storm)
- Raise thresholds for non-critical alerts to reduce noise
- Use alert grouping in PDC to collapse repeated alerts
- Investigate root cause — alert storms usually indicate a real problem
- Temporarily suppress specific alert codes during known maintenance windows
"""
    },
    {
        "url": "curated://pega-alert-pega0001-long-interaction",
        "title": "PEGA0001 — Long-Running Interaction Alert — Causes and Fixes",
        "content": """# PEGA0001 — Long-Running Interaction

## What It Means
PEGA0001 fires when a user interaction (a single HTTP request/response cycle) exceeds the configured threshold. Default threshold: **20 seconds**. This means something in that request took too long — a slow activity, a heavy data page load, a bad query, or excessive rule resolution.

## Alert Details
- **Severity**: WARNING (can be configured to ERROR)
- **Threshold DSS**: `alerts/interaction/threshold` (default: 20000ms)
- **Log location**: PegaALERT.log
- **Context provided**: Requestor ID, interaction duration, rule being executed, thread name

## Common Causes

### 1. Slow Database Query
- A Report Definition or SQL query inside an activity is scanning too many rows
- Missing database index on a frequently queried column
- **Fix**: Check Tracer for DB operations. Add indexes. Optimize query filters.

### 2. Heavy Data Page Load
- A data page is loading a large dataset on first access (e.g., thousands of rows)
- Data page source (connector or activity) is slow
- **Fix**: Add pagination, use Node scope for shared data, set reload strategy.

### 3. Complex Rule Resolution
- Hundreds of When rules or Declare Expressions being evaluated during the interaction
- Deep class hierarchy causing excessive rule resolution
- **Fix**: Simplify rule structure. Use circumstancing instead of many When rules.

### 4. Large Clipboard
- Copying or iterating over large page lists (thousands of items)
- **Fix**: Reduce clipboard data. Use data pages instead of clipboard-heavy approaches.

### 5. External Connector Timeout
- REST/SOAP connector waiting for a slow external system
- **Fix**: Set appropriate timeouts on connectors. Use async pattern for slow integrations.

### 6. Excessive Logging/Tracing
- Tracer or verbose logging enabled in production
- **Fix**: Disable Tracer in production. Set log level to WARN/ERROR.

## Debugging Steps
1. **Open PegaALERT.log** — find the PEGA0001 entry, note the requestor ID and duration
2. **Run Tracer** on the same flow — reproduce the slow interaction
3. **Check PAL** (Performance Analyzer) — identify which step took the most time
4. **Check SQL logs** — look for slow queries during that timeframe
5. **Check clipboard size** — use Clipboard tool to measure page sizes
6. **Check external calls** — look for connector timeouts in the log

## Threshold Tuning
- **Development**: 30000ms (30 seconds) — more lenient for debugging
- **Test/QA**: 15000ms (15 seconds) — tighter to catch issues early
- **Production**: 10000ms (10 seconds) — strict to catch real problems
- Set via DSS: `alerts/interaction/threshold` = value in milliseconds
"""
    },
    {
        "url": "curated://pega-alert-pega0002-long-query",
        "title": "PEGA0002 — Long-Running Database Query Alert — Causes and Fixes",
        "content": """# PEGA0002 — Long-Running Database Query

## What It Means
PEGA0002 fires when a single database query exceeds the configured time threshold. Default: **5 seconds**. This indicates a query performance problem — either the query is poorly written, indexes are missing, or the database is under heavy load.

## Alert Details
- **Severity**: WARNING
- **Threshold DSS**: `alerts/query/threshold` (default: 5000ms)
- **Context**: SQL text (if enabled), query duration, table name, requestor ID

## Common Causes

### 1. Missing Database Index
- Query filtering on a column without an index causes full table scan
- Common with custom properties used in Access When or Report Definitions
- **Fix**: Create database index on the filtered column. Use Declare Index for embedded properties.

### 2. Large Table Scan
- Querying pc_work or pc_history without proper filters
- SELECT * without WHERE clause or with non-selective filters
- **Fix**: Add specific filters (date range, status, case type). Never scan entire pc_work.

### 3. BLOB Read for Large Cases
- Reading a case with a very large BLOB (lots of properties, page lists)
- **Fix**: Reduce case data. Move large data to separate data objects. Use Declare Index for reportable properties.

### 4. Report Definition Issues
- Complex report with many joins, sub-reports, or calculated columns
- Report running against large date ranges without proper indexing
- **Fix**: Optimize report. Add date range filters. Use summary reports instead of detailed.

### 5. Concurrent Database Load
- Multiple long-running reports or batch processes running simultaneously
- Database connection pool exhaustion
- **Fix**: Stagger batch jobs. Increase connection pool. Use read replicas for reporting.

## Debugging Steps
1. Find the PEGA0002 alert in PegaALERT.log — note the SQL and duration
2. Run EXPLAIN/EXPLAIN PLAN on the SQL to check query plan
3. Look for full table scans (TABLE ACCESS FULL in Oracle, Seq Scan in PostgreSQL)
4. Check if indexes exist on WHERE clause columns
5. Check database wait events during the query execution
6. Monitor connection pool usage in SMA

## Key DSS Settings
| DSS | Purpose | Default |
|-----|---------|---------|
| alerts/query/threshold | Query time alert threshold (ms) | 5000 |
| alerts/query/includeSQL | Include SQL text in alert | false |
| alerts/query/maxSQLLength | Max SQL text length in alert | 500 |
"""
    },
    {
        "url": "curated://pega-alert-pega0003-large-clipboard",
        "title": "PEGA0003 — Large Clipboard Page Alert — Causes and Fixes",
        "content": """# PEGA0003 — Large Clipboard Page

## What It Means
PEGA0003 fires when a clipboard page exceeds the configured size threshold. Default: **500KB** per page. Large clipboard pages consume server memory, slow down passivation/activation, and can cause OutOfMemoryError in extreme cases.

## Alert Details
- **Severity**: WARNING
- **Threshold DSS**: `alerts/clipboard/pagesize/threshold` (default: 500000 bytes)
- **Context**: Page name, page class, page size in bytes, requestor ID

## Common Causes

### 1. Unbounded Page Lists
- Loading ALL records from a data source into a page list without pagination
- Example: Loading all 50,000 customers into a single page list for a dropdown
- **Fix**: Use pagination. Load only visible records. Use autocomplete instead of dropdown for large lists.

### 2. Case Accumulating Data Over Time
- Long-running cases that accumulate history, notes, attachments metadata
- Each case interaction adds data but nothing is cleaned up
- **Fix**: Archive old data. Move completed sub-case data off clipboard. Clean up temporary pages.

### 3. Integration Response Stored on Clipboard
- Storing the full response from a connector (e.g., a 2MB XML response) on the clipboard
- **Fix**: Extract only the needed fields. Don't store raw response on clipboard.

### 4. Deeply Nested Page Structures
- Pages containing pages containing pages — deep nesting multiplies size
- **Fix**: Flatten data structure. Use data references instead of embedded copies.

### 5. Duplicate Data on Clipboard
- Same data loaded into multiple pages (e.g., customer data duplicated across case pages)
- **Fix**: Use data pages (single cached copy) instead of duplicating data.

## Debugging Steps
1. Open **Clipboard Viewer** (Dev Studio → Tools → Clipboard)
2. Sort pages by size — identify the largest pages
3. Expand large pages — find which properties or page lists are biggest
4. Check if page lists have excessive items
5. Check if any pages contain raw integration responses
6. Use the Clipboard tool API: `tools.getClipboard().getPageNames()` to enumerate programmatically

## Impact of Large Clipboards
- **Memory**: Each requestor's clipboard is held in JVM memory. 100 users × 5MB clipboard = 500MB
- **Passivation**: Large clipboards take longer to serialize to database during passivation
- **Performance**: Clipboard operations (copy, iterate) slow down with large pages
- **Network**: If using sticky sessions with failover, large clipboards increase failover time

## Best Practices
1. Set clipboard page size alerts to 200KB for early warning
2. Clean up temporary pages after use (Page-Remove)
3. Use Thread-scoped data pages for transient data (auto-cleanup)
4. Paginate all list views (max 50-100 items per page)
5. Never store BLOBs (files, images) on the clipboard — use attachment storage
"""
    },
    {
        "url": "curated://pega-alert-pega0004-long-connect",
        "title": "PEGA0004 — Long-Running Connector Alert — Causes and Fixes",
        "content": """# PEGA0004 — Long-Running Connector (Connect Rule Timeout)

## What It Means
PEGA0004 fires when a connector call (REST, SOAP, JMS, SAP, etc.) exceeds the configured threshold. Default: **10 seconds**. This means an external system is responding slowly or not at all.

## Alert Details
- **Severity**: WARNING
- **Threshold DSS**: `alerts/connect/threshold` (default: 10000ms)
- **Context**: Connector name, endpoint URL, duration, HTTP status, requestor ID

## Common Causes

### 1. External System Slow
- The target system is under load, processing complex requests, or experiencing issues
- **Fix**: Work with the external team to optimize their endpoint. Set realistic timeouts.

### 2. Network Latency
- High latency between Pega and the external system (different regions, VPN overhead)
- DNS resolution delays
- **Fix**: Check network path. Use connection pooling. Consider caching responses in data pages.

### 3. Large Payload
- Sending or receiving very large request/response bodies (multi-MB XML/JSON)
- **Fix**: Request only needed fields. Use pagination. Compress payloads.

### 4. SSL/TLS Handshake
- Certificate validation taking too long, CRL check timeout, SSL negotiation overhead
- **Fix**: Cache SSL sessions. Ensure CRL endpoints are accessible. Check certificate chain.

### 5. Connection Pool Exhaustion
- All connections to the external system are in use, new requests wait in queue
- **Fix**: Increase connection pool size. Reduce concurrent calls. Use async pattern.

### 6. Timeout Configuration Too Low
- Timeout set too aggressively for legitimately slow operations (e.g., report generation)
- **Fix**: Increase timeout for known slow operations. Use async pattern for long-running calls.

## Debugging Steps
1. Check PegaALERT.log for PEGA0004 — note connector name, URL, duration
2. Test the endpoint independently (Postman/curl) to verify it's responsive
3. Check Tracer — look at Connect step, see request/response details
4. Check PegaRULES log for HTTP errors (4xx, 5xx) from the connector
5. Check SMA → Integration → Connection Pool for pool utilization
6. Check network: `ping`, `traceroute`, `nslookup` from the Pega server

## Connector Timeout Settings
- **Connect timeout**: Time to establish the TCP connection (default: 10s)
- **Read timeout**: Time to receive the response after sending the request (default: 30s)
- **Total timeout**: Overall time limit for the entire connector call
- Configure per-connector in the connector rule's "Service" tab

## Best Practices
1. Always set explicit timeouts — never use defaults blindly
2. Implement circuit breaker pattern for unreliable services
3. Cache connector responses in data pages when appropriate
4. Use async connectors (Queue Processor) for non-urgent calls
5. Monitor connector performance in PDC — set alerts for degradation trends
"""
    },
    {
        "url": "curated://pega-alert-pega0005-pega0007-activity",
        "title": "PEGA0005 & PEGA0007 — Long-Running Activity and Activity Step Alerts",
        "content": """# PEGA0005 & PEGA0007 — Long-Running Activity Alerts

## PEGA0005 — Long-Running Activity Step
Fires when a single step within an activity exceeds the threshold.
- **Default threshold**: 5 seconds per step
- **DSS**: `alerts/activitystep/threshold`

## PEGA0007 — Long-Running Activity (Total)
Fires when the total execution time of an activity exceeds the threshold.
- **Default threshold**: 15 seconds total
- **DSS**: `alerts/activity/threshold`

## Alert Details
- **Severity**: WARNING
- **Context**: Activity name, step number (for 0005), class, total duration, method name

## Common Causes

### 1. Java Step with Heavy Processing
- Custom Java code doing complex calculations, string manipulation, or I/O
- **Fix**: Optimize Java code. Move heavy computation to batch processing.

### 2. obj-Browse/obj-Open on Large Datasets
- obj-Browse returning thousands of records without filters
- obj-Open loading a case with a huge BLOB
- **Fix**: Add filters. Limit result count. Use Report Definition instead of obj-Browse.

### 3. Looping Over Large Lists
- For-Each loop iterating over thousands of items with processing per item
- **Fix**: Use Data Flows for bulk processing. Reduce iteration count. Use batch commit.

### 4. obj-Save in a Loop
- Saving to the database inside a loop — each save is a DB round-trip
- **Fix**: Batch commits. Use Commit after the loop, not inside it.

### 5. Recursive Activity Calls
- Activity calling itself or circular activity chains
- **Fix**: Add depth limit. Refactor to iterative approach.

### 6. Property-Set with Complex Expressions
- Activity steps using Property-Set with expensive expressions or function calls
- **Fix**: Simplify expressions. Use Data Transform instead of Activity for data manipulation.

## Debugging Steps
1. Check PegaALERT.log — note activity name, step number, duration
2. Open the activity rule — go to the specific step number flagged
3. Run Tracer with "Activity Steps" enabled — see time per step
4. For Java steps: add timing instrumentation to isolate slow code
5. For obj-Browse: check the SQL generated — run EXPLAIN on it
6. For loops: check item count — is it higher than expected?

## Threshold Tuning
| Environment | PEGA0005 (Step) | PEGA0007 (Total) |
|-------------|-----------------|-------------------|
| Development | 10000ms | 30000ms |
| QA/Test | 5000ms | 15000ms |
| Production | 3000ms | 10000ms |

## When to Suppress vs Fix
- **Suppress temporarily**: Known batch activities that legitimately take long (configure a higher threshold for batch requestors)
- **Always fix**: User-facing activities that cause UI delays
- Configure per-requestor-type thresholds: `alerts/activity/threshold/batch` vs `alerts/activity/threshold/browser`
"""
    },
    {
        "url": "curated://pega-alert-pega0006-data-page-load",
        "title": "PEGA0006 — Long-Running Data Page Load Alert — Causes and Fixes",
        "content": """# PEGA0006 — Long-Running Data Page Load

## What It Means
PEGA0006 fires when a data page takes too long to load its data. This impacts the user who triggered the load and potentially other users if the data page scope is Requestor or Node (blocks concurrent access during loading).

## Alert Details
- **Severity**: WARNING
- **Threshold DSS**: `alerts/datapage/threshold` (default: 5000ms)
- **Context**: Data page name, class, scope, data source type, load duration

## Common Causes

### 1. Slow Data Source (Connector)
- Data page sourced from a REST/SOAP connector that's slow to respond
- **Fix**: Optimize external API. Set connector timeout. Cache with appropriate refresh.

### 2. Slow Data Source (Report Definition)
- Data page sourced from a complex Report Definition with expensive queries
- **Fix**: Optimize the report. Add indexes. Reduce result set size.

### 3. Slow Data Source (Activity)
- Data page sourced from an activity that does heavy processing
- **Fix**: Optimize the activity. Consider pre-computing results.

### 4. Large Result Set
- Data page loading thousands of records from any source
- **Fix**: Paginate. Filter. Load only what's needed for the current view.

### 5. First Load on Node-Scoped Data Page
- Node-scoped data pages load once and cache. The first user triggers the load — they wait.
- **Fix**: Pre-load Node-scoped data pages on startup (use a startup agent). Add a loading indicator.

### 6. Concurrent Load Blocking
- Multiple users hit a Requestor/Node-scoped data page simultaneously during first load. Second user blocks waiting for first user's load to complete.
- **Fix**: Pre-load. Use background load. Implement loading indicator.

## Debugging Steps
1. Find PEGA0006 in PegaALERT.log — note data page name and duration
2. Open the data page rule — check the data source type
3. If connector: test the connector independently, check endpoint performance
4. If report: run the underlying SQL with EXPLAIN, check for table scans
5. If activity: trace the activity, identify slow steps
6. Check data page scope — is it appropriate? (Thread-scoped pages load every time)

## Data Page Performance Optimization
1. **Right-size the scope**: Node for shared reference data, Requestor for user-specific, Thread only when necessary
2. **Set refresh strategy**: Don't reload Node-scoped pages on every access
3. **Paginate**: Use paging parameters to load data in chunks
4. **Pre-load**: Use startup activities to warm up critical data pages
5. **Monitor**: Set PEGA0006 threshold to 3000ms in production for early warning
"""
    },
    {
        "url": "curated://pega-alerts-pega0010-to-pega0019",
        "title": "PEGA0010–PEGA0019 — Resource and System Alert Codes Reference",
        "content": """# PEGA0010–PEGA0019 — Resource and System Alerts

## PEGA0010 — Database Query Returning Too Many Rows
- **What**: A query returned more rows than the configured threshold
- **Threshold DSS**: `alerts/query/maxrows` (default: 10000)
- **Common cause**: obj-Browse or Report Definition without proper filters
- **Fix**: Add WHERE clauses. Use Top/Limit. Paginate results. Never SELECT * from large tables.
- **Impact**: Memory consumption, slow processing, potential OutOfMemoryError

## PEGA0011 — Long-Running RDB Operation
- **What**: A relational database operation (insert, update, delete) took too long
- **Threshold DSS**: `alerts/rdb/threshold` (default: 5000ms)
- **Common cause**: Updating a large BLOB, lock contention, missing index on UPDATE WHERE clause
- **Fix**: Optimize BLOB size. Check for table locks. Add indexes. Batch updates.

## PEGA0012 — Too Many Requestors
- **What**: Number of active requestors exceeds the configured limit
- **Threshold DSS**: `alerts/requestor/count/threshold` (default: 500)
- **Common cause**: Session leak (requestors not being cleaned up), high concurrent users, long session timeouts
- **Fix**: Reduce session timeout. Implement proper session cleanup. Scale horizontally (add nodes).
- **Debugging**: SMA → Requestor Management → see active requestor count and idle times

## PEGA0013 — Too Many PRThreads
- **What**: Thread pool exhaustion — too many concurrent processing threads
- **Threshold DSS**: `alerts/prthread/count/threshold`
- **Common cause**: Long-running operations holding threads, deadlocks, blocking I/O
- **Fix**: Increase thread pool size. Fix long-running operations. Use async processing for heavy tasks.
- **Debugging**: Take a thread dump (`kill -3 <pid>` or `jstack`), look for blocked/waiting threads

## PEGA0014 — Frequent Garbage Collection
- **What**: JVM is spending too much time in garbage collection
- **Threshold**: GC pause > 5 seconds, or GC overhead > 30% of total time
- **Common cause**: Heap too small, memory leak, large object allocation
- **Fix**: Increase heap size. Tune GC parameters. Fix memory leaks (large clipboards, unclosed resources).
- **Debugging**: Enable GC logging. Analyze with GCViewer or GCEasy. Check for PEGA0003 (large clipboard) correlation.

## PEGA0015 — Memory Allocation Failure
- **What**: JVM failed to allocate memory — approaching or at OutOfMemoryError
- **Severity**: FATAL
- **Common cause**: Heap exhausted, large object allocation, memory leak
- **Fix**: Increase -Xmx. Analyze heap dump. Fix memory leaks. Reduce clipboard sizes.
- **Debugging**: Generate heap dump on OOM (`-XX:+HeapDumpOnOutOfMemoryError`). Analyze with Eclipse MAT.

## PEGA0016 — Queue Too Deep
- **What**: A queue processor queue has too many pending items
- **Threshold DSS**: `alerts/queue/depth/threshold` (default: 1000)
- **Common cause**: Queue processor not running, processing too slow, burst of incoming items
- **Fix**: Start/restart queue processors. Scale up. Increase processing threads. Check for broken items blocking the queue.

## PEGA0017 — Agent Exception
- **What**: An agent (background job) threw an exception during execution
- **Severity**: ERROR
- **Context**: Agent name, agent class, exception message, stack trace
- **Common cause**: Data error, null pointer, external system down, timeout
- **Fix**: Check the agent activity for the error. Fix the data issue. Add error handling.
- **Debugging**: Check PegaRULES log for the full stack trace. Reproduce by running the agent activity manually.

## PEGA0018 — Too Many Open File Handles
- **What**: The process has too many open file handles (approaching OS limit)
- **Threshold**: OS-dependent (typically 65536)
- **Common cause**: File resource leak, too many open connections, log file handles not closed
- **Fix**: Check `ulimit -n` on the server. Increase OS limit. Fix resource leaks. Check for unclosed streams in activities.

## PEGA0019 — Interaction Too Large
- **What**: The data sent in a single interaction (form submission) is too large
- **Threshold DSS**: `alerts/interaction/size/threshold` (default: 1MB)
- **Common cause**: Large file upload, huge form with many fields, page list with thousands of items
- **Fix**: Limit form data size. Use file attachment mechanism (not form fields) for uploads. Paginate large lists.
"""
    },
    {
        "url": "curated://pega-alerts-pega0020-to-pega0032",
        "title": "PEGA0020–PEGA0032 — Service, Rendering, and System Alert Codes Reference",
        "content": """# PEGA0020–PEGA0032 — Service, Rendering, and System Alerts

## PEGA0020 — Long-Running Service
- **What**: An inbound service (Service REST, Service SOAP, etc.) took too long to process
- **Threshold DSS**: `alerts/service/threshold` (default: 10000ms)
- **Common cause**: Heavy processing in service activity, slow data access, large response payload
- **Fix**: Optimize service logic. Cache data. Return only needed fields. Use async for heavy processing.
- **Debugging**: Trace the service activity. Check which step is slowest. Verify data page performance.

## PEGA0021 — Slow UI Rendering
- **What**: A section or harness took too long to render the HTML/JSON response
- **Threshold DSS**: `alerts/rendering/threshold` (default: 5000ms)
- **Common cause**: Complex sections with many visibility conditions, large repeating grids, excessive When rule evaluations during rendering
- **Fix**: Simplify UI layout. Reduce visibility conditions. Use lazy loading for tabs/sections. Paginate grids.
- **Debugging**: Use browser dev tools (Network tab) to measure render time. Use Tracer to check server-side rendering duration.

## PEGA0022 — Activity Timeout
- **What**: An activity was forcefully terminated because it exceeded the maximum allowed time
- **Severity**: ERROR (more severe than PEGA0007 warning)
- **Threshold DSS**: `alerts/activity/timeout` (default: 300000ms / 5 minutes)
- **Common cause**: Infinite loop, deadlock, extreme data processing
- **Fix**: Add loop limits. Fix deadlocks. Use batch processing for heavy workloads.

## PEGA0023 — Deprecated Method or Feature Used
- **What**: Code is using a deprecated Pega API, method, or feature
- **Severity**: INFO/WARNING
- **Common cause**: Old activities using deprecated Java methods, rules using removed features
- **Fix**: Update code to use recommended alternatives. Check Pega upgrade guide for replacement APIs.

## PEGA0024 — Rule Resolution Overhead
- **What**: Rule resolution (finding the correct rule to execute) is taking too long
- **Threshold DSS**: `alerts/ruleresolution/threshold` (default: 2000ms)
- **Common cause**: Deep class hierarchy, excessive circumstancing, many application layers
- **Fix**: Simplify class hierarchy. Reduce unnecessary circumstancing. Check rule cache effectiveness.

## PEGA0025 — Too Many Open Database Connections
- **What**: Connection pool utilization is above threshold
- **Threshold DSS**: `alerts/connection/pool/threshold` (default: 80%)
- **Common cause**: Connection leaks, too many concurrent requests, slow queries holding connections
- **Fix**: Increase pool size. Fix connection leaks (ensure connections are returned). Optimize slow queries.
- **Debugging**: SMA → Database → Connection Pool → check active/idle/waiting counts.

## PEGA0026 — Too Many Interactions
- **What**: A single requestor has too many concurrent or accumulated interactions
- **Threshold DSS**: `alerts/interaction/count/threshold` (default: 25)
- **Common cause**: User opening many tabs/windows, interaction leak (not properly closed)
- **Fix**: Limit concurrent interactions per user. Clean up stale interactions. Set interaction timeout.

## PEGA0027 — Service Timeout
- **What**: An inbound service call timed out before completing (different from PEGA0020 which is slow but completed)
- **Severity**: ERROR
- **Common cause**: Service processing exceeded the caller's timeout, deadlock during service execution
- **Fix**: Optimize service processing time. Increase caller timeout if appropriate. Use async pattern.

## PEGA0028 — Long-Running Commit
- **What**: A database commit operation took too long
- **Threshold DSS**: `alerts/commit/threshold` (default: 5000ms)
- **Common cause**: Large transaction (many rows), BLOB writes, database lock contention, slow storage I/O
- **Fix**: Reduce transaction size. Use deferred save to batch commits. Check database I/O performance.

## PEGA0029 — Alert Log Threshold Exceeded
- **What**: The rate of alerts being generated exceeds the threshold — potential alert storm
- **Threshold**: More than 100 alerts per minute
- **Common cause**: Cascading failure, systematic performance issue, misconfigured threshold
- **Fix**: Investigate the root cause of the alert storm. Temporarily raise thresholds. Fix the underlying issue.

## PEGA0030 — HTTP Request Too Large
- **What**: An incoming HTTP request body exceeds the size limit
- **Threshold DSS**: `alerts/http/request/maxsize` (default: 5MB)
- **Common cause**: Large file upload via form, bulk data submission, oversized API request
- **Fix**: Use streaming upload. Limit request size at load balancer. Validate input size.

## PEGA0031 — Excessive Declarative Rule Triggers
- **What**: Too many declarative rules (Declare Expressions, Constraints) triggered in a single interaction
- **Threshold DSS**: `alerts/declarative/threshold` (default: 1000 evaluations)
- **Common cause**: Circular dependencies, cascading declare expressions, large page list with declare expressions on each item
- **Fix**: Check for circular declare expressions. Reduce declarative rule count. Use targeted expressions (not on every property).

## PEGA0032 — Browser Request Timeout
- **What**: The browser-side request timed out waiting for a server response
- **Severity**: WARNING
- **Common cause**: Server processing exceeding browser timeout, network interruption
- **Fix**: Optimize server-side processing (check PEGA0001). Increase browser timeout if appropriate. Show loading indicator.
"""
    },
    {
        "url": "curated://pega-common-exceptions-reference",
        "title": "Common Pega Exceptions — Java Exceptions, Rule Errors, and Stack Traces",
        "content": """# Common Pega Exceptions — Complete Reference

## Java Exceptions in Pega

### NullPointerException (NPE)
- **Where**: Activity Java steps, Data Transforms, Declare Expressions
- **Common cause**: Accessing a property on a null/missing page, calling a method on a null object
- **How to debug**: Check the stack trace line number. Open the activity/Java step. Verify the page/property exists before accessing.
- **Fix**: Add null checks: `if (tools.findPage("MyPage") != null)`. Use `.pyIsPagePresent` before accessing pages.

### ClassNotFoundException
- **Where**: During rule assembly, custom Java compilation
- **Common cause**: Missing JAR file, deleted class, incorrect import
- **Fix**: Check JAR files in the classpath. Verify the class exists. Re-import the rule.

### PRRuntimeException
- **Where**: Anywhere in Pega execution
- **Common cause**: Pega's wrapper for internal errors — check the nested exception for the real cause
- **Fix**: Read the full stack trace. The nested cause (Caused by:) has the actual error.

### DatabaseException / SQLSyntaxErrorException
- **Where**: obj-Save, obj-Open, obj-Browse, Report Definitions
- **Common cause**: Invalid SQL generated, schema mismatch, missing column/table, data type mismatch
- **Fix**: Check the SQL in the log. Verify table schema matches the class definition. Run schema updates.

### OutOfMemoryError (OOM)
- **Where**: JVM-wide
- **Common cause**: Memory leak, clipboard bloat, large data processing, insufficient heap
- **Fix**: Increase -Xmx. Take heap dump and analyze. Fix clipboard bloat (PEGA0003). Check for resource leaks.

### StackOverflowError
- **Where**: Recursive activity calls, circular Declare Expressions, deeply nested rule resolution
- **Common cause**: Activity A calls Activity B calls Activity A (infinite recursion)
- **Fix**: Break the circular dependency. Add recursion depth limit. Refactor to iterative approach.

## Pega-Specific Exceptions

### InvalidRuleException
- **Where**: When trying to execute a rule that doesn't exist or can't be resolved
- **Common cause**: Missing rule, wrong ruleset version, rule checked out by another user
- **Fix**: Check if the rule exists. Verify ruleset version is in the access group. Check for locked rules.

### ConnectorException
- **Where**: REST/SOAP connector execution
- **Common cause**: External system unreachable, timeout, authentication failure, invalid response
- **Fix**: Check endpoint availability. Verify credentials. Check network connectivity. Test with Postman.

### WorkLockedException
- **Where**: Trying to open/modify a case that's locked by another user
- **Common cause**: Another user has the case open, background process holding a lock
- **Fix**: Wait for the other user to finish. Check SMA for lock holders. Force-release the lock if stale.

### AuthorizationException
- **Where**: Trying to access a rule, case, or feature without proper privileges
- **Common cause**: Missing role/privilege, Access When/Deny blocking access
- **Fix**: Check user's Access Group → Roles → Privileges. Check Access When/Deny rules for the class.

### FlowException
- **Where**: During flow execution
- **Common cause**: Missing assignment, invalid transition, SLA configuration error
- **Fix**: Check flow definition. Verify assignments are routing to valid operators/workbaskets. Check SLA rules.

## Reading Stack Traces

### Anatomy of a Pega Stack Trace
```
com.pega.pegarules.pub.runtime.PRRuntimeException: Error in activity MyOrg-App-Work.MyActivity
  at com.pega.pegarules.exec.internal.ActivityExecutor.doStep(ActivityExecutor.java:442)
  at com.pega.pegarules.exec.internal.ActivityExecutor.execute(ActivityExecutor.java:210)
Caused by: java.lang.NullPointerException
  at MyOrg_App_Work.MyActivity_step3(MyActivity.java:58)  ← THIS IS THE IMPORTANT LINE
```

### How to Read It
1. Start at **"Caused by:"** — this is the actual error
2. Find the line with **your rule name** (e.g., `MyActivity_step3`) — this is where the error occurred
3. The step number in the method name (`step3`) maps to the activity step number
4. Ignore Pega internal frames (ActivityExecutor, PRThread, etc.)

### Where to Find Stack Traces
1. **PegaRULES log**: Full stack traces for ERROR and FATAL entries
2. **Tracer**: Shows exceptions with stack traces during traced interactions
3. **Alerts**: Some alerts (PEGA0017) include stack traces
4. **Service responses**: Error responses from Service REST/SOAP may include stack trace details
"""
    },
    {
        "url": "curated://pega-alert-threshold-tuning-guide",
        "title": "Alert Threshold Tuning Guide — Best Practices for Dev, QA, and Production",
        "content": """# Alert Threshold Tuning Guide — Complete Reference

## Why Tune Alert Thresholds?
Default thresholds are designed to be broadly applicable but may not suit your specific application. Thresholds that are too low create alert noise (crying wolf). Thresholds too high miss real problems. The goal is to get alerts only for actionable issues.

## Complete Alert Threshold Reference

### Performance Alerts
| Alert Code | What It Measures | Dev | QA | Prod | DSS Key |
|-----------|-----------------|-----|-----|------|---------|
| PEGA0001 | Interaction time | 30s | 20s | 10s | alerts/interaction/threshold |
| PEGA0002 | DB query time | 10s | 5s | 3s | alerts/query/threshold |
| PEGA0004 | Connector time | 15s | 10s | 5s | alerts/connect/threshold |
| PEGA0005 | Activity step time | 10s | 5s | 3s | alerts/activitystep/threshold |
| PEGA0006 | Data page load time | 10s | 5s | 3s | alerts/datapage/threshold |
| PEGA0007 | Activity total time | 30s | 15s | 10s | alerts/activity/threshold |
| PEGA0011 | RDB operation time | 10s | 5s | 3s | alerts/rdb/threshold |
| PEGA0020 | Service processing | 15s | 10s | 5s | alerts/service/threshold |
| PEGA0021 | UI rendering time | 10s | 5s | 3s | alerts/rendering/threshold |
| PEGA0024 | Rule resolution time | 5s | 2s | 1s | alerts/ruleresolution/threshold |
| PEGA0028 | Commit time | 10s | 5s | 3s | alerts/commit/threshold |

### Resource Alerts
| Alert Code | What It Measures | Threshold | DSS Key |
|-----------|-----------------|-----------|---------|
| PEGA0003 | Clipboard page size | 500KB | alerts/clipboard/pagesize/threshold |
| PEGA0010 | Query row count | 10000 | alerts/query/maxrows |
| PEGA0012 | Active requestors | 500 | alerts/requestor/count/threshold |
| PEGA0016 | Queue depth | 1000 | alerts/queue/depth/threshold |
| PEGA0019 | Interaction size | 1MB | alerts/interaction/size/threshold |
| PEGA0025 | DB connection pool % | 80% | alerts/connection/pool/threshold |
| PEGA0026 | Interactions per requestor | 25 | alerts/interaction/count/threshold |
| PEGA0030 | HTTP request size | 5MB | alerts/http/request/maxsize |
| PEGA0031 | Declarative evaluations | 1000 | alerts/declarative/threshold |

## Setting Thresholds via DSS
1. Navigate to **Dev Studio → System → Settings → Dynamic System Settings**
2. Search for the DSS key (e.g., `alerts/interaction/threshold`)
3. If it doesn't exist, create it:
   - Owning Ruleset: Pega-Engine (or your application ruleset)
   - Setting Purpose: alerts/interaction/threshold
   - Setting Value: 10000 (milliseconds)
4. Save and the change takes effect immediately (no restart needed)

## Environment-Specific Threshold Strategy

### Development Environment
- **Lenient thresholds** — developers are debugging, running tracer, etc.
- Focus on catching critical issues (OOM, deadlocks) not minor slowness
- Disable non-critical alert codes to reduce log noise

### QA/Testing Environment
- **Moderate thresholds** — should catch performance regressions
- Enable all alert codes
- Run performance tests and baseline the alerts

### Production Environment
- **Strict thresholds** — every alert should be actionable
- Forward all alerts to PDC
- Set up alert subscriptions for ERROR/FATAL
- Review and tune monthly based on alert patterns

## Alert Suppression (When Needed)
- Suppress specific rules: `alerts/suppress/rulename=MySlowActivity`
- Suppress by requestor type: `alerts/suppress/requestortype=BATCH`
- Suppress during maintenance: Set a temporary DSS `alerts/suppress/all=true`
- **Always re-enable after maintenance!**

## Monthly Alert Review Process
1. Pull alert report from PDC for the past month
2. Identify top 10 most frequent alerts
3. For each: Is this a real problem? → Fix it. False positive? → Tune the threshold.
4. Check for new alert codes that appeared (new code path, regression)
5. Verify alert subscriptions are reaching the right people
"""
    },
    {
        "url": "curated://pega-exception-handling-patterns",
        "title": "Exception Handling Patterns in Pega — Try-Catch, Error Flows, and Recovery",
        "content": """# Exception Handling Patterns in Pega

## Overview
Pega provides multiple mechanisms for handling errors and exceptions. Proper error handling prevents cryptic error pages for users and ensures system resilience.

## 1. Activity Error Handling (Try-Catch Pattern)

### Jump-on-Failure
- Each activity step has a "Jump" field for error handling
- Set "Jump on failure" to a specific step number (error handler step)
- The error handler step can log the error, set a status, and continue or stop
- **Example**: Step 3 calls a connector. Jump on failure = Step 10 (error handler). Step 10 logs the error and returns gracefully.

### StatusValue Checking
After calling another activity or connector, check the status:
```
Step 4: Call-Activity MyConnectorActivity
Step 5: Property-Set .ErrorOccurred = @if(.pxStatuValue != "Good", true, false)
Step 6: Branch → if .ErrorOccurred = true → Jump to Step 10 (error handler)
```

### Java Try-Catch in Activities
```java
try {
    // risky operation
    tools.sendEmail(...);
} catch (Exception e) {
    oLog.error("Email failed: " + e.getMessage());
    tools.putParamValue("ErrorMessage", e.getMessage());
    // set status and let the next step handle it
}
```

## 2. Flow-Level Error Handling

### Error Handler Flows
- Each flow can have an **error handler flow** configured in the flow properties
- When an unhandled exception occurs during flow processing, Pega routes to the error handler
- The error handler flow can: log the error, notify administrators, set case status, create an incident case

### Ticket/Exception Flows
- **Tickets** are event-driven error handlers in flows
- Define a ticket for specific exception conditions
- When the ticket fires, it interrupts the normal flow and routes to the ticket handler
- Use for: business exceptions (not just technical errors)

### Flow Action Error Handling
- Configure validation on flow actions to catch data errors before processing
- Pre-processing and post-processing data transforms can validate state
- Set "Show errors on form" to display validation messages to users

## 3. Connector Error Handling

### HTTP Status Code Handling
Configure response handling for different HTTP status codes:
- **2xx**: Success — process the response normally
- **4xx**: Client error — log, show user-friendly message
- **5xx**: Server error — retry, fallback, or alert

### Retry Pattern
```
Connector Rule → Retry count: 3 → Retry interval: 5 seconds
On final failure → Route to error handler activity
```

### Circuit Breaker Pattern
1. Track consecutive connector failures (use a data page counter)
2. After N failures (e.g., 5), stop calling the external system for a cooldown period
3. After cooldown, try one request (half-open state)
4. If it succeeds, resume normal operations. If it fails, reset cooldown.

## 4. Service Error Handling (Inbound APIs)

### Service REST Error Responses
Configure error mapping in Service REST rules:
```json
{
    "errorCode": "PEGA_ERR_001",
    "message": "Case not found",
    "details": "No case exists with ID ABC-123"
}
```

### Error Status Codes
- Map Pega exceptions to appropriate HTTP status codes
- 400: Bad request (validation failure)
- 404: Not found (case/data not found)
- 500: Internal server error (unhandled exception)
- Configure in the Service REST rule's error handling tab

## 5. Declare OnChange Error Recovery
- If a Declare OnChange activity fails, it does NOT roll back the triggering change
- The change is committed but the side effect (the OnChange action) fails silently
- **Best practice**: Add error logging inside OnChange activities to catch failures

## 6. Global Error Handler

### Custom Error Pages
- Configure custom error pages instead of showing Pega stack traces
- **SMA → System → Error Pages** — map exception types to user-friendly pages
- Never show stack traces in production (security risk)

### Unhandled Exception Logger
- Configure a global exception handler activity to catch and log all unhandled exceptions
- DSS: `Pega-IntSvcs/ErrorHandler` — specify the activity to run on unhandled errors
- Log to a dedicated error table for monitoring and analysis

## Error Handling Best Practices
1. **Never swallow exceptions silently** — always log them at minimum
2. **Show user-friendly messages** — don't show stack traces or technical details to end users
3. **Log with context** — include case ID, user ID, operation being performed
4. **Use structured error codes** — consistent error codes make monitoring easier
5. **Test error paths** — include negative test cases in your test plan
6. **Monitor error rates** — set up PDC alerts for error rate spikes
7. **Graceful degradation** — if a non-critical feature fails, don't block the entire process
"""
    },
    {
        "url": "curated://pega-pegaalert-log-analysis",
        "title": "PegaALERT Log — Complete Guide to Reading, Analyzing, and Acting on Alerts",
        "content": """# PegaALERT Log — Complete Analysis Guide

## What is the PegaALERT Log?
The PegaALERT log (PegaALERT-YYYY-MM-DD.log or PegaALERT.log) is a dedicated log file that records all performance alerts generated by the Pega engine. It's separate from PegaRULES.log and focuses exclusively on performance/resource threshold violations.

## Log Location
- **Embedded Tomcat**: `<PEGA_HOME>/logs/PegaALERT.log`
- **WebSphere**: `<WAS_PROFILE>/logs/<SERVER>/PegaALERT.log`
- **WebLogic**: `<DOMAIN>/servers/<SERVER>/logs/PegaALERT.log`
- **Docker/K8s**: Mounted volume or stdout (configurable)

## Log Entry Format
```
2024-03-15 14:23:45,123 [ALERT] PEGA0001 Interaction exceeded threshold
  RequestorID: H12345678901234567
  Duration: 25034ms (threshold: 20000ms)
  RuleName: MyOrg-App-Work.CreateCase
  Thread: PRThread-1-1234
  Node: node1.example.com
  UserID: admin@myorg
  Details: Activity MyOrg-App-Work.CreateCase took 25034ms
```

## How to Analyze PegaALERT Logs

### Step 1: Identify Alert Patterns
```bash
# Count alerts by code (most frequent first)
grep "PEGA00" PegaALERT.log | awk '{print $4}' | sort | uniq -c | sort -rn

# Output example:
#  245 PEGA0001
#   89 PEGA0002
#   34 PEGA0004
#   12 PEGA0003
```

### Step 2: Analyze Top Offenders
```bash
# Find which rules trigger PEGA0001 most often
grep "PEGA0001" PegaALERT.log | grep "RuleName" | sort | uniq -c | sort -rn | head -10

# Find peak alert times (hourly distribution)
grep "PEGA0001" PegaALERT.log | awk '{print substr($2,1,2)}' | sort | uniq -c
```

### Step 3: Correlate Alerts
- PEGA0001 (slow interaction) often correlates with PEGA0002 (slow query) — the query is causing the slow interaction
- PEGA0003 (large clipboard) often precedes PEGA0015 (OOM) — clipboard bloat causing memory exhaustion
- PEGA0012 (too many requestors) + PEGA0014 (frequent GC) = memory pressure from session accumulation

### Step 4: Track Trends
- Compare alert counts week-over-week — increasing alerts indicate degradation
- Spike in PEGA0004 alerts often indicates external system problems
- New alert codes appearing after a deployment indicate regression

## Alert Severity Mapping
| Severity | Action Required | Response Time |
|----------|----------------|---------------|
| INFO | Review in next sprint | Days |
| WARNING | Investigate this week | Hours-Days |
| ERROR | Investigate today | Hours |
| FATAL | Investigate immediately | Minutes |

## Common Alert Combinations and Root Causes
| Alert Combination | Likely Root Cause |
|-------------------|-------------------|
| PEGA0001 + PEGA0002 | Slow DB query causing slow interaction |
| PEGA0001 + PEGA0004 | Slow connector causing slow interaction |
| PEGA0003 + PEGA0014 + PEGA0015 | Clipboard bloat → GC pressure → OOM |
| PEGA0012 + PEGA0025 | Too many sessions exhausting DB connections |
| PEGA0016 + PEGA0017 | Queue backup due to agent errors |
| PEGA0005 + PEGA0007 | One slow step making entire activity slow |
| PEGA0020 + PEGA0002 | Service slow due to DB query in service logic |
| PEGA0021 + PEGA0031 | Slow rendering due to excessive declare evaluations |

## Automated Alert Analysis Script
```python
# Quick Python script to analyze PegaALERT logs
import re
from collections import Counter

alerts = Counter()
rules = Counter()
with open("PegaALERT.log") as f:
    for line in f:
        match = re.search(r"(PEGA\\d{4})", line)
        if match:
            alerts[match.group(1)] += 1
        rule_match = re.search(r"RuleName: (.+)", line)
        if rule_match:
            rules[rule_match.group(1).strip()] += 1

print("=== Top Alerts ===")
for code, count in alerts.most_common(10):
    print(f"  {code}: {count}")

print("\\n=== Top Offending Rules ===")
for rule, count in rules.most_common(10):
    print(f"  {rule}: {count}")
```

## Best Practices
1. **Review PegaALERT daily in production** — it's the first signal of performance issues
2. **Automate analysis** — use scripts or PDC to aggregate and trend alerts
3. **Set up alert forwarding** to PDC or your monitoring system (Datadog, Splunk, etc.)
4. **Rotate log files** — PegaALERT can grow large; configure rotation in prlog4j2.xml
5. **Baseline your environment** — know what "normal" alert counts look like so you can detect anomalies
"""
    },
]


def seed_phase19():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE19:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase19_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE19)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 19 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase19()
