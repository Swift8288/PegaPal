"""
Curated Pega Knowledge Base — Phase 16 (Platform Internals — Requestors, Passivation, Queues, Class Mapping)
Run: python -m crawler.seed_kb_phase16
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE16 = [
    {
        "title": "Requestor Types — Browser, Batch, API, Service",
        "url": "https://pega.docs/platform/requestor-types",
        "content": """
# Requestor Types in Pega — Browser, Batch, API, Service

## What is a Requestor?

A **requestor** is a thread of execution in Pega that represents a user session, background agent, or service call. Each requestor maintains its own context, clipboard, work history, and security credentials. Pega allocates system resources per requestor and tracks its lifecycle from creation to termination.

## Browser Requestor (Interactive)

**Browser requestors** handle interactive user sessions from the web UI:
- Created when a user logs in; destroyed on logout or timeout
- Maintains session state, user context, and case data
- Single-threaded per user (one requestor per browser tab per user)
- Default timeout: 30 minutes of inactivity (configurable in System Settings)
- Resource-intensive due to UI rendering and clipboard state

**Configuration:**
- **Max Active Browser Requestors**: System Settings → Requestor Management
- **Requestor Timeout**: Set in the Application section
- Monitor in **System Management Application (SMA) → Cluster → Requestors**

**Common Issues:**
- **"Too Many Active Requestors"**: Browser tabs left open without logout; implement auto-logout or session management
- **Memory Leak**: Users not logging out; enable auto-session termination
- **Orphaned Requestors**: Network disconnects; clean up via SMA

---

## Batch Requestor (Background Processing)

**Batch requestors** run background agents, scheduled jobs, and deferred processing:
- Created by the scheduler or triggered manually
- No UI state; minimal clipboard overhead
- Can run for seconds to hours depending on job complexity
- Share a pool of threads in the application server

**Batch Job Configuration:**
- **Start Time**: One-time, daily, weekly, or monthly schedules
- **Requestor Pool Size**: System Settings → Batch Requestor Pool (default: 5)
- **Timeout**: Usually longer than browser requestors (300+ seconds)

**Monitoring:**
- **SMA → Batch Administration → Batch Status** — View running jobs
- **SMA → Requestor Diagnostics** — Track batch execution time

**Common Issues:**
- **Job Hangs**: Deadlock in agent logic; add timeout monitoring
- **"No Available Batch Requestor"**: Pool too small; increase batch pool size
- **Memory Spike**: Agent processes large datasets without pagination

---

## Service Requestor (API/Service Calls)

**Service requestors** handle REST/SOAP API calls and service integrations:
- Created per API request; short-lived (typically <5 seconds)
- Minimal session state; focused on request/response mapping
- Can be reused via connection pooling
- Often stateless (no clipboard retention post-request)

**Configuration:**
- **Service Requestor Pool**: System Settings → Service Requestor Pool (default: 10)
- **Request Timeout**: Configurable per service rule (REST Connector, Service rules)
- **Max Concurrent Services**: Limits concurrent API requests

**Best Practices:**
- Use connection pooling to reuse requestors across API calls
- Set appropriate timeouts to prevent resource exhaustion
- Monitor service latency in **SMA → Service Health**

---

## Requestor Pooling for Services

Pega reuses requestor threads via pooling to reduce overhead:

**How It Works:**
1. Request arrives (API call, batch job, browser login)
2. Pega acquires a requestor from the pool (or creates a new one if pool exhausted)
3. Requestor executes the work (rule invocation, database query)
4. Requestor returns to the pool for reuse

**Tuning Requestor Pools:**
- Monitor **SMA → Performance → Requestor Utilization**
- Increase pool size if "Waiting for Requestor" errors appear
- Too many requestors = higher memory; too few = queued requests

---

## Requestor Timeout Configuration

**In System Settings:**
```
Application → Timeout Settings
  - Interactive Requestor Timeout: 1800 seconds (30 min)
  - Batch Requestor Timeout: 3600 seconds (1 hour)
  - Service Requestor Timeout: 300 seconds (5 min)
```

**Per-Rule Configuration:**
- **Activity**: Timeout in activity properties
- **Service Rule**: Timeout in the REST/SOAP connector
- **Agent**: Timeout in the batch job schedule

**Impact:**
- Too short: Legitimate requests aborted prematurely
- Too long: Orphaned requestors consume memory
- Stale sessions not cleaned up quickly

---

## Monitoring Active Requestors in SMA

**SMA → Cluster → Requestors Dashboard:**
- List of all active requestors (browser, batch, service)
- Requestor ID, User, Status, Start Time, Elapsed Time
- Memory per requestor
- Lock/Unlock requestors for debugging

**Key Metrics:**
- **Total Active**: Compare against pool size
- **Waiting for Requestor**: Indicates pool exhaustion
- **Memory per Requestor**: Baseline for memory leaks

**Action Items:**
- Terminate stuck requestors manually
- Review requestor history for patterns
- Correlate spikes with user login/logout events

---

## Debugging Requestor Issues

### Issue: Too Many Open Requestors
**Symptoms:** "No available requestor" errors; high memory usage
**Root Causes:**
- Users not logging out (browser requestors accumulating)
- Batch jobs hanging without timeout
- Connection leaks in service code

**Fixes:**
1. Check **SMA → Requestors** for idle sessions
2. Implement auto-logout (System Settings)
3. Increase pool sizes temporarily
4. Restart application if all else fails

### Issue: Memory Leak (Requestor Memory Growing)
**Symptoms:** Requestor memory grows over time; not returned to pool
**Root Causes:**
- Unbounded collection in clipboard (list growing infinitely)
- Cached references in static objects
- Passivation not clearing session data

**Debugging Steps:**
1. Enable requestor memory profiling in SMA
2. Check clipboard size during execution
3. Review rules that manipulate global data

### Issue: Orphaned Requestors
**Symptoms:** Requestors stuck in "processing" state; cannot terminate
**Root Causes:**
- Network disconnect (browser tab closed)
- Deadlock in rule code
- Service timeout without cleanup

**Resolution:**
1. Terminate via **SMA → Requestors → Terminate** button
2. Monitor network stability
3. Add error handling in rules

---

## DSS Settings for Requestor Management

**Decision Service Settings (for Service requestors):**
```
Requestor Management (in service/API configuration)
  - Reuse Requestor: Yes/No (default: Yes for pooling)
  - Requestor Lifetime: Specify max operations per requestor
  - Cleanup Policy: Immediate vs Deferred
```

**Tuning:**
- Reuse = Better performance; No reuse = Cleaner state
- For stateless APIs, enable reuse
- For stateful services, disable to prevent state bleed

---

## Summary & Checklist

- **Browser Requestors**: UI sessions; timeout on inactivity
- **Batch Requestors**: Background jobs; reusable pool
- **Service Requestors**: API calls; short-lived, pooled
- Monitor **SMA → Requestors** regularly
- Configure appropriate timeouts
- Clean up orphaned requestors
- Scale pools based on workload
"""
    },
    {
        "title": "Passivation & Activation — Session Management Deep Dive",
        "url": "https://pega.docs/platform/passivation-activation",
        "content": """
# Passivation & Activation — Session Management Deep Dive

## What is Passivation?

**Passivation** is the process of serializing and saving a requestor's session state to the database when it becomes idle, freeing up memory in the application server. When the user resumes activity, **activation** restores the session state from the database back into memory.

### Why Pega Passivates

- **Memory Management**: Browser sessions can sit idle for hours; passivation frees memory
- **Scalability**: Allows more concurrent users with finite server memory
- **Fault Tolerance**: Session survives application restarts
- **Cluster Support**: Passivated sessions can be re-activated on any node

---

## How Passivation Works (Technical Flow)

1. **Idle Detection**: Requestor has no activity for N seconds (configurable)
2. **Serialization**: Requestor's clipboard, work history, and context are serialized
3. **Database Write**: Serialized data written to `pr_other` table with requestor ID
4. **Memory Release**: Requestor object released from heap
5. **Reactivation**: Next user action looks up passivated state and reconstructs requestor

**Performance Impact:**
- Passivation: 50-500 ms (DB write + serialization)
- Activation: 100-1000 ms (DB read + deserialization)
- User may see slight delay on first action after idle period

---

## Passivation Timeout Settings

**In System Settings:**
```
Application → Session Management
  - Passivation Timeout: 900 seconds (15 min, default)
  - Session Timeout: 1800 seconds (30 min, default)
```

**How They Interact:**
- **Passivation Timeout (900s)**: Idle time before passivation triggered
- **Session Timeout (1800s)**: Idle time before session killed entirely
- Typical flow: Active → Passivated (900s) → Terminated (1800s)

**Tuning Guidelines:**
- **High Traffic**: Lower passivation timeout (300s) to free memory sooner
- **Long Tasks**: Increase passivation timeout to avoid unnecessary save/restore
- **Mobile Users**: Consider network lag; longer passivation timeout

---

## Passivation Storage — pr_other Table

**Storage Location:** `pr_other` table in Pega database

**Table Structure:**
```
PZINSKEY (Instance Key) — Unique requestor ID
PZSOBJKEY (Object Key) — Requestor state blob (serialized)
PZCREATED — When state was last saved
PZPPASSPORTDATA — User/security context
PZPCLIPBOARD — Work item and context data
```

**Query Example:**
```sql
SELECT PZINSKEY, PZCREATED, length(PZSOBJKEY) as SIZE_BYTES
FROM pr_other
WHERE PZINSKEY LIKE 'REQUESTOR%'
ORDER BY PZCREATED DESC;
```

**Maintenance:**
- Old passivated sessions accumulate; implement cleanup job
- Monitor `pr_other` table size growth
- Purge sessions older than 30 days (batch job)

---

## Passivation Impact on Performance

### Benefits:
- Frees 2-5 MB per browser session
- Allows 500+ concurrent users on moderate hardware
- Enables long user think-time without server impact

### Costs:
- **Database I/O**: Write/read serialized state
- **CPU**: Serialization/deserialization overhead
- **Latency**: User sees delay on first action after idle

### Real-World Example:
```
- 100 concurrent browser sessions, 8 GB server RAM
- Without passivation: Each session = 2 MB → 200 MB used
- With passivation (15 min): 10-15 active sessions in memory = 30 MB
- Freed memory allows more users without hardware upgrade
```

---

## Debugging Passivation Errors

### Error: "Requestor No Longer Exists"
**Symptom:** User clicks button after idle period; error message appears
**Root Causes:**
1. Session timed out before reactivation
2. Passivated state corrupted in database
3. Application restart cleared in-memory requestor

**Fix:**
1. Check if Session Timeout < Passivation Timeout (should be opposite)
2. Verify `pr_other` table integrity (corrupted blob)
3. Increase passivation timeout; user is inactive too long

### Error: "Lost Session Data"
**Symptom:** User's work item, case data, or form values disappeared after passivation
**Root Causes:**
1. Transient data not saved to clipboard properly
2. Rule creates non-serializable object (connection, file handle)
3. Clipboard truncated due to size limits

**Debugging:**
```
- Enable logging: System Settings → Debug → Passivation Logging
- Check logs for serialization errors
- Review rule code: avoid non-serializable objects in clipboard
- Monitor clipboard size: Settings → Application → Clipboard Size Limits
```

### Error: "Passivation Failed — pr_other Table Full"
**Symptom:** Passivation stops working; "no space on device" or quota exceeded
**Fix:**
1. Run cleanup job: **SMA → Batch Administration → Purge Passivated Sessions**
2. Increase database tablespace
3. Archive old `pr_other` rows to offline storage

---

## Passivation vs Session Timeout

| Feature | Passivation | Session Timeout |
|---------|-------------|-----------------|
| **Purpose** | Free memory; preserve state | Terminate idle session |
| **Timing** | N minutes (900s default) | M minutes (1800s default) |
| **Recovery** | State restored on next action | Session lost; user must re-login |
| **Database** | Writes serialized state | Deletes session record |
| **User Experience** | Slight delay on first action | Must re-authenticate |

**Best Practice:** Session Timeout > Passivation Timeout
- User gets passivation benefit (free memory) without losing work
- If truly idle for full session timeout, session is cleaned up

---

## Best Practices for Reducing Passivation Overhead

1. **Optimize Clipboard Size**
   - Don't store large objects in clipboard (use page objects or database)
   - Clear unnecessary data periodically
   - Use `Obj-Set-Property(Clipboard, "propertyToDelete", )` to remove items

2. **Increase Passivation Timeout Selectively**
   - For knowledge workers: 1800s (allow longer think-time)
   - For call center: 300s (churn sessions faster)
   - Configure per application role

3. **Disable Passivation for Specific Sessions**
   - Service API calls: No need to passivate (stateless)
   - Batch jobs: Run to completion; no passivation
   - Configuration: Service Settings → "Do not passivate"

4. **Monitor & Alert**
   - Track passivation count and average activation time
   - Alert if activation time > 2000 ms (slow database)
   - Review spike in passivation errors

5. **Database Tuning**
   - Index `pr_other` table by PZINSKEY (speeds lookup)
   - Schedule `pr_other` cleanup during low-traffic periods
   - Monitor disk I/O during passivation peaks (morning login rush)

---

## Summary Checklist

- Passivation saves memory; activation restores state
- Configure passivation timeout (15 min default) vs session timeout (30 min default)
- Passivated state stored in `pr_other` table
- Monitor pr_other size; clean up old sessions
- Expect 100-1000 ms activation latency
- Optimize clipboard to reduce serialization cost
- Disable passivation for stateless services
- Enable passivation logging for troubleshooting
"""
    },
    {
        "title": "Queue Processors — Asynchronous Processing Engine",
        "url": "https://pega.docs/platform/queue-processors",
        "content": """
# Queue Processors — Asynchronous Processing Engine

## What Are Queue Processors?

**Queue processors** are background threads that asynchronously process work items stored in a work queue. Instead of blocking a browser requestor, work is enqueued and processed when resources are available, enabling scalable asynchronous workflows.

### Work Queue Model:
1. **Enqueue**: User triggers work → item stored in work queue table
2. **Processing**: Queue processor picks up work → executes rule/agent
3. **Complete**: Work finished → marked complete or moved to error queue
4. **Retry**: Failed items may be retried per configuration

---

## Creating Queue Processors

**In Pega Designer:**

1. **Define Queue**: Create a Queue object
   - **Type**: Standard (shared) or Dedicated (exclusive)
   - **Priority**: High, Normal, Low (affects processing order)
   - **Dedicated Requestor Pool**: Queue processor thread pool size

2. **Configure Queue Processor**: Add to System Settings
   ```
   Queue Processors (System Settings)
     - Queue: [SelectQueue]
     - Number of Processors: 3-5 (threads)
     - Requestor Timeout: 300 seconds
     - Failure Handling: Retry or Error Queue
   ```

3. **Enqueue Work**: In activity/rule
   ```
   Call Obj-Queue-Work(WorkPage, ActivityName, Queue, Priority)
   - WorkPage: Data to process
   - ActivityName: What to execute
   - Queue: Target queue
   - Priority: Relative priority
   ```

---

## Standard vs Dedicated Queues

| Feature | Standard Queue | Dedicated Queue |
|---------|----------------|-----------------|
| **Purpose** | General async work | Critical processes |
| **Processor Pool** | Shared (5 default) | Exclusive (2-3) |
| **Performance** | Lower latency; resource contention | Higher latency; guaranteed resource |
| **Use Case** | Email, notifications, reports | Payment processing, order submission |
| **Priority Starvation** | High-priority items may dominate | No starvation; dedicated threads |

**Example:**
```
- Standard Queue: Batch email send (1000 items)
- Dedicated Queue: Payment authorization (critical, 10 items/sec)
→ Payment queue not blocked by email queue
```

---

## Queue Item Lifecycle

### State Transitions:

```
PENDING (initial)
  ↓ [processor picks up]
PROCESSING (active)
  ↓ [on success]
COMPLETE

  ↓ [on failure]
ERROR
  ↓ [retry configured]
PENDING (retry)
  ↓
PROCESSING
  ↓
COMPLETE / FINAL_ERROR (exhausted retries)
```

### Timestamps Tracked:
- **Enqueue Time**: When work added to queue
- **Start Time**: When processor began
- **Complete Time**: When finished
- **Duration**: Elapsed time

---

## Broken Queue Items

**Broken Item**: Work that failed and cannot be retried (max retries exceeded, unrecoverable error)

### Common Causes:
1. **Rule Not Found**: Activity deleted; queue item references old rule
2. **Data Validation Error**: Invalid input data that will always fail
3. **External System Timeout**: Third-party API down permanently
4. **Code Exception**: Runtime error in rule logic

### Finding Broken Items:

**In SMA:**
```
System Management → Requestor Management → Queue Items
  - Filter: Status = ERROR
  - View: Enqueue Time, Start Time, Error Message
```

**Database Query:**
```sql
SELECT PZINSKEY, PZQUEUENAME, PZSTATUS, PZERRORTEXT, PZLASTUPDATED
FROM pr_queue
WHERE PZSTATUS = 'ERROR'
ORDER BY PZLASTUPDATED DESC;
```

### Fixing Broken Items:

1. **Review Error Message**: Understand why it failed
2. **Fix Root Cause**: Update rule, fix data, restore service
3. **Manually Requeue**:
   - Edit queue item in SMA
   - Change status to PENDING
   - Update data if necessary
   - Release back to queue

4. **Purge Old Errors**: Delete unrecoverable items >30 days
   ```sql
   DELETE FROM pr_queue
   WHERE PZSTATUS = 'ERROR'
   AND PZLASTUPDATED < (SYSDATE - 30);
   ```

---

## Retry Configuration

**In Queue Configuration:**
```
Queue Settings
  - Max Retries: 3 (default)
  - Retry Delay: 60 seconds
  - Backoff Strategy: None, Linear, Exponential
```

**Retry Backoff Example (Exponential):**
```
Retry 1: Delay 60s (60 × 1)
Retry 2: Delay 120s (60 × 2)
Retry 3: Delay 240s (60 × 4)
After 3 retries: Move to ERROR queue
```

**Best Practices:**
- Transient errors (timeout, DB lock): Higher retry count (5)
- Data validation error: Lower retry count (1)
- Payment processing: Exponential backoff to avoid duplicate charges

---

## Scaling Queue Processors Across Nodes

**Cluster Deployment:**

In a 3-node cluster:
```
Node A: Queue Processor Pool (3 threads) → Process Queue Q1
Node B: Queue Processor Pool (3 threads) → Process Queue Q1
Node C: Queue Processor Pool (3 threads) → Process Queue Q1
Total: 9 concurrent workers on queue Q1
```

**How Pega Distributes Work:**
- Shared queue table read by all nodes
- Database lock prevents duplicate processing
- Processor grabs next item, acquires lock, processes
- Other processors skip locked items

**Scaling Formula:**
```
Max Throughput = (Processors per Node) × (Number of Nodes) × (1 / Item Duration)
Example: 3 procs × 3 nodes × (1 / 2 sec per item) = 4.5 items/sec
```

**Tuning Across Cluster:**
- Increase processors if queue depth grows
- Add nodes if single-node queue processors saturated
- Monitor queue latency: (Current Time - Enqueue Time)

---

## Monitoring Queue Depth in SMA

**SMA → Requestor Management → Queue Monitoring:**
- Queue Name
- Total Items: PENDING + PROCESSING + ERROR
- Processing: Currently being worked on
- Error: Failed items awaiting manual intervention
- Avg Processing Time: Item duration
- Queue Depth Growth Rate: Enqueue rate vs processing rate

**Alert Thresholds:**
- Queue Depth > 1000 items: Processor pool too small
- Avg Processing Time > 5 min: Slow rule logic or I/O
- Error Rate > 5%: Data quality or integration issues

---

## Debugging Stuck/Broken Queue Items

### Issue: Queue Items Stay in PROCESSING Forever
**Symptoms:** Item stuck for hours; processor crashed or deadlocked
**Root Causes:**
1. Processor thread crashed; work never completed
2. Deadlock in rule (waiting for resource held by another thread)
3. External service hang (API not responding)

**Debug Steps:**
1. Check processor status: **SMA → Batch Administration**
2. Review rule logs for exceptions during item processing
3. Check database locks: `SELECT * FROM pr_queue WHERE PZSTATUS='PROCESSING'`
4. Manually fail item or extend timeout

### Issue: Items Processed Twice (Duplicate Processing)
**Symptoms:** Work executed multiple times; data duplicated
**Root Causes:**
1. Processor retried item; rule not idempotent
2. Manual requeue without checking completion
3. Multiple queue processors grabbing same item (lock race)

**Prevention:**
- Make rules idempotent (safe to run multiple times)
- Check item status before re-queuing
- Ensure database row-locking works (check DB logs)

### Issue: Queue Items Lost After Application Restart
**Symptoms:** PENDING items disappear; work not processed
**Root Cause:** In-memory queue; items not persisted to database
**Fix:** Verify queue configuration saves to pr_queue table (not memory-only)

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Queue not found" | Queue deleted or misspelled | Recreate queue; update references |
| "Max retries exceeded" | Item failed 5+ times | Review error message; fix root cause |
| "Processor pool exhausted" | Too many items; too few workers | Increase processor count; add nodes |
| "Enqueue timeout" | Queue table locked | Check for deadlocks; optimize DB |

---

## Summary & Checklist

- Queue processors enable asynchronous work processing
- Items flow: PENDING → PROCESSING → COMPLETE or ERROR
- Configure queue type (standard vs dedicated) by workload
- Set retry policy (count, delay, backoff)
- Scale processors per node; add nodes for throughput
- Monitor queue depth and error rate in SMA
- Clean up broken items; review error logs
- Ensure rules are idempotent (safe to retry)
- Use dedicated queues for critical work (payment, order)
"""
    },
    {
        "title": "Class-to-Table Mapping — Database Schema Design",
        "url": "https://pega.docs/platform/class-table-mapping",
        "content": """
# Class-to-Table Mapping — Database Schema Design

## How Pega Maps Classes to Database Tables

Every Pega class is mapped to a database table. When you save an object, Pega serializes its properties and stores them in the mapped table. The mapping defines schema, performance, and reporting capabilities.

### Basic Mapping Rule:
- **Pega Class** (e.g., `MyApp-Work-Order`) → **Database Table** (e.g., `pc_work_order`)
- **Class Property** (e.g., `OrderID`) → **Column** (e.g., `PZPORDERID`)
- **Object Instance** → **Row** in table

---

## Default Table Mapping

Pega provides default table mappings for standard class hierarchies:

| Class Type | Default Table | Purpose |
|-----------|---------------|---------|
| **Work** (extends Work-) | `pc_work` | Case/work item storage |
| **Data** (extends Data-) | `pr_other` | Generic data objects, passivated sessions |
| **Decision** (extends Rule-) | `pr_obj_decisionrules` | Decision tree rules |
| **System** (extends System-) | (internal tables) | Pega system objects |

### Example:
```
Class: MyApp-Work-Order (extends Work-)
Mapped to: pc_work_order (dedicated table)

Class: MyApp-Data-Address (extends Data-)
Mapped to: pr_other (shared table)
```

---

## Creating Custom Database Tables

### Why Create Custom Tables?

- **Performance**: Dedicated table indexes; faster queries
- **Reporting**: Easier for SQL reporting tools
- **Compliance**: Schema isolation; data governance
- **Scale**: Handle millions of rows per class

### Steps to Create Custom Table:

1. **In Designer:**
   ```
   Build → Database → Tables → New Table
   Name: pc_custom_mytable
   Class: MyApp-Work-Custom
   Storage: Full (all properties) or Partial (key properties only)
   ```

2. **Define Columns:**
   - **Primary Key**: PZINSKEY (auto-generated)
   - **Parent Key**: PZPKEY (for embedded pages)
   - **Property Mappings**: Map class properties to columns
   ```
   Property: OrderID → Column: PZPORDERID (VARCHAR2(32))
   Property: OrderDate → Column: PZPORDERDATE (DATE)
   Property: Status → Column: PZPSTATUS (VARCHAR2(20))
   ```

3. **Create Indexes:**
   ```
   Index 1: PZPORDERID (fast lookup by order)
   Index 2: PZPSTATUS (fast filtering by status)
   ```

4. **Generate Schema:**
   - Click "Create Table" in Designer
   - Pega generates SQL and executes against database
   - Verify table created: `DESC pc_custom_mytable`

---

## Class Group Table Inheritance

**Class Group** is a set of classes sharing one table (space-saving design).

### Example:
```
Class Hierarchy:
  Data- (root)
    └─ Data-Address
       ├─ Data-Address-Billing
       └─ Data-Address-Shipping

All three classes → Shared table: pr_data_address

Discriminator Column: PZCLASSNAME
  Row 1: {PZCLASSNAME: 'Data-Address', Street: '123 Main', ...}
  Row 2: {PZCLASSNAME: 'Data-Address-Billing', Street: '456 Oak', ...}
```

### Benefits:
- Single table for related classes
- Fewer tables = simpler schema
- Shared parent indexes

### Drawbacks:
- NULL columns for class-specific properties
- Schema less normalized
- Harder to enforce constraints

---

## Dedicated vs Shared Tables

| Aspect | Dedicated Table | Shared (Group) Table |
|--------|-----------------|----------------------|
| **Classes** | One class | Multiple related classes |
| **Columns** | Only needed properties | All properties from hierarchy |
| **Indexes** | Class-specific | Shared by group |
| **Row Size** | Smaller | Larger (NULL padding) |
| **Query Performance** | Faster | Slower (more NULLs) |
| **Reporting** | Easier (no discriminator) | Harder (filter by class) |

**Choose Dedicated Table If:**
- High query volume on class
- Reporting needs
- Large objects (many properties)
- Performance critical

**Choose Shared Table If:**
- Infrequent queries
- Few properties per class
- Simple schema preferred

---

## When to Create a Dedicated Table

### Performance Thresholds:

```
Estimated Row Count: > 100,000
  → Create dedicated table; add indexes

Query Frequency: > 1000 queries/sec
  → Dedicated table with optimal indexes

Property Count: > 30
  → Dedicated table to reduce NULL columns

Reporting Load: Significant SQL-based reporting
  → Dedicated table for cleaner schema
```

### Real-World Example:

```
MyApp-Work-Order: Expected 5 million rows/year
  → Create dedicated table (pc_work_order)
  → Index on OrderDate, CustomerID, Status

MyApp-Data-Comment: Expected 10,000 rows
  → Share pr_other (generic data table)
  → No performance impact; simpler maintenance
```

---

## Schema Generation

### In Designer Workflow:

1. **Define Mapping**: Class → Table, Properties → Columns
2. **Set Storage**: Full vs Partial
3. **Generate Schema**: Click "Generate" button
   ```
   Generated SQL:
   CREATE TABLE pc_work_order (
     PZINSKEY VARCHAR2(32) PRIMARY KEY,
     PZPORDERID VARCHAR2(32),
     PZPCUSTOMERID VARCHAR2(32),
     PZPSTATUS VARCHAR2(20),
     PZPCREATEDDATE DATE,
     PZPUPDATEDDATE DATE,
     INDEX idx_orderid (PZPORDERID),
     INDEX idx_status (PZPSTATUS)
   );
   ```
4. **Review & Execute**: DBA reviews; SQL executed in target database

### Modifying Existing Table:

```
Add Column: New property added; Pega generates ALTER TABLE
Drop Column: Remove property; Pega marks column inactive (not dropped)
Rename Column: Not supported; create new column, migrate data
```

---

## Debugging "Table Not Found" Errors

### Error: "Table Does Not Exist"
**Symptom:** Save/query fails with "Table pc_custom_order not found"
**Root Causes:**
1. Table not created in database (designer table created but SQL not executed)
2. Class mapped to wrong table name
3. Database schema out of sync with Pega definition

**Debug Steps:**
```sql
-- Check if table exists
SELECT TABLE_NAME FROM USER_TABLES
WHERE TABLE_NAME = 'PC_CUSTOM_ORDER';

-- If missing, regenerate in Designer
-- Check Pega logs for creation errors
-- Verify database credentials for DDL execution
```

### Error: "Class Not Mapped"
**Symptom:** New class created; trying to save throws error
**Fix:** Map class to table in Designer
```
Application Explorer → Class → [Click Class]
→ Storage tab → Select "Table Mapping"
→ Choose or create table → Save
```

### Error: "Column Not Found"
**Symptom:** Property value cannot be saved; "column PZPFIELD not found"
**Root Causes:**
1. Property added to class; table not updated
2. Property name typo in mapping
3. Table schema out of sync

**Fix:**
1. Verify mapping in Designer (correct column name)
2. Regenerate table schema
3. Manually add column if schema out of sync:
   ```sql
   ALTER TABLE pc_custom_order ADD PZPFIELD VARCHAR2(100);
   ```

---

## Impact on Reporting and Search

### Reporting:
- **Dedicated Table**: Clean SQL queries; no discriminator filter
  ```sql
  SELECT COUNT(*) FROM pc_work_order WHERE PZPSTATUS='COMPLETED';
  ```
- **Shared Table**: Must filter by class
  ```sql
  SELECT COUNT(*) FROM pr_other
  WHERE PZCLASSNAME='Data-Address' AND PZPSTATUS='Active';
  ```

### Full Text Search:
- Index on `PZPCONTENT` column for keyword search
- Dedicated tables support more aggressive indexing
- Shared tables have larger indexes (all classes)

### Analytics:
- Dedicated tables: Data warehouse easily exports; no schema ambiguity
- Shared tables: Need ETL transformation to normalize

---

## Summary & Checklist

- Every class maps to a table; every property to a column
- Default mapping: Work- → pc_work, Data- → pr_other
- Create dedicated tables for high-performance, high-volume classes
- Use shared tables for low-volume, simple data
- Generate schema in Designer; DBA executes in production
- Monitor table size; add indexes as row count grows
- Debug "table not found" by checking database existence and class mapping
- Dedicated tables enable better reporting and SQL queries
- Avoid modifying schema after deployment; plan table mapping carefully
"""
    },
    {
        "title": "Situational Layer Cake — Enterprise Application Architecture",
        "url": "https://pega.docs/platform/layer-cake-architecture",
        "content": """
# Situational Layer Cake — Enterprise Application Architecture

## Pega's Layered Architecture Concept

The **Situational Layer Cake** is Pega's multi-tenant application architecture that enables organizations to build scalable, reusable, multi-implementation systems. Work, decisions, data, and integrations are organized into distinct layers, each with clear responsibilities.

### Layers from Bottom to Top:

```
┌─────────────────────────────────────────┐
│ Implementation Layer (Top)              │
│ Customer-specific rules, workflows      │
├─────────────────────────────────────────┤
│ Industry/Division Layer (Middle)        │
│ Business rules, processes, policies     │
├─────────────────────────────────────────┤
│ Organization Layer (Core)               │
│ Platform, connectors, infrastructure    │
└─────────────────────────────────────────┘
```

---

## Layer Types & Responsibilities

### Organization Layer (Foundation)

**Purpose:** Platform-wide, shared across all implementations
- System configuration, connectors (Salesforce, SAP, etc.)
- Common services, utilities, base classes
- Enterprise integrations, governance
- Example package: `Organization-Core`

**What Lives Here:**
```
Rule Type: Connect-REST for external APIs
Class: Data-SystemUser (shared across implementations)
Activity: Utility-LogEvent (logging framework)
```

### Division/Framework Layer (Mid-Tier)

**Purpose:** Industry or framework-specific rules and processes
- Business object definitions (Work class, Data classes)
- Standard workflows and decisions
- Industry best practices
- Example package: `IndustryX-Framework`

**What Lives Here:**
```
Work Class: Work-Claim (claims processing)
Decision: Claim-Eligibility (business rules)
Activity: Workflow-ClaimReview (standard process)
```

### Implementation Layer (Top)

**Purpose:** Customer-specific customizations and workflows
- Custom validations, business logic
- Integration with customer systems
- Local compliance, branding
- Example package: `CustomerY-Implementation`

**What Lives Here:**
```
Activity: CustomValidation-Order (customer-specific rules)
Work Class: Work-Order-CustomY (extends Work-Claim from Framework)
Data: CustomerY-Settings (local configuration)
```

---

## Rule Resolution Across Layers

When Pega executes a rule, it searches through layers in precedence order:

```
User triggers action: Process Work Item
↓
Pega searches for rule in order:
1. Implementation Layer (CustomerY-Implementation)
   └─ Found? USE IT. Done.
2. Division Layer (IndustryX-Framework)
   └─ Not found; try next
3. Organization Layer (Organization-Core)
   └─ Found? USE IT.
4. Pega Base Classes
   └─ Still nothing? Use default Pega behavior
```

### Example Resolution:

```
Activity: CheckOrder (which implementation to use?)

Search Path:
  CustomerY-Implementation.CheckOrder → FOUND → Execute
  (IndustryX-Framework.CheckOrder skipped)
  (Organization-Core.CheckOrder skipped)

Activity: LogEvent (not in implementation layer)
  CustomerY-Implementation.LogEvent → NOT FOUND
  IndustryX-Framework.LogEvent → NOT FOUND
  Organization-Core.LogEvent → FOUND → Execute
```

---

## How Inheritance Works Across Layers

### Class Inheritance:

```
Pega Base: Work-
  ↓ (extended by Organization)
Organization: Work-Task
  ↓ (extended by Division)
Division: Work-Claim (extends Work-Task)
  ↓ (extended by Implementation)
Implementation: Work-Claim-Premium (extends Work-Claim)
```

### Property & Method Inheritance:

```
Work- (Pega) → Properties: WorkID, Status, Assignee, CreatedDate
  ↓
Work-Claim (Framework) → Adds: ClaimType, Severity, Claimant
  ↓
Work-Claim-Premium (Implementation) → Adds: PremiumOption, DiscountCode
```

**Resolution:** Premium order retrieves ClaimType from Framework, Severity from Framework, PremiumOption from Implementation.

---

## Reusability Benefits

### 1. Leverage Across Customers

```
Organization Layer: API integrations (Salesforce, ServiceNow)
  → Reused by 50 customers

Division Layer: Claim processing workflow
  → Reused by 10 auto-insurance companies

Implementation Layer: Specific customer rules
  → Unique to one company
```

**Cost Saving:** Build once in Organization/Division; reuse in 10+ implementations.

### 2. Maintenance & Updates

```
Framework releases ClaimEligibility v2 (improved rules)
  → All implementations automatically inherit (if not overridden)
  → No need to update 50 customer packages

Customer needs custom logic
  → Override in Implementation layer only
  → Framework updates still inherited for non-overridden rules
```

### 3. Faster Implementation Delivery

```
Baseline: Use existing Framework
  → 20% dev time (customize + test)

Versus building from scratch
  → 100% dev time

ROI: 80% faster time to market
```

---

## Building Enterprise Frameworks

### Step 1: Design Layer Structure

```
Organization-Core (foundation)
  - System connectors
  - Utilities, logging, auditing
  - Base classes, data models

Banking-Framework (industry)
  - Account, Customer, Transaction classes
  - Core banking processes (Deposit, Withdrawal, Transfer)
  - Compliance rules (AML, KYC)

Bank-Acme-Impl (customer)
  - Acme-specific workflows
  - Acme integrations (core banking system)
  - Acme branding, local rules
```

### Step 2: Define Classes Hierarchy

```
Organization:
  Data-Customer (first name, last name, email)

Framework:
  Data-Customer → Data-BankCustomer (account, risk rating)

Implementation:
  Data-BankCustomer → Data-BankAcmeCustomer (legacy ID, office location)
```

### Step 3: Build Reusable Workflows

```
Framework:
  Activity: Workflow-OpenAccount
    1. Validate customer
    2. Create account record
    3. Notify core banking system
    4. Return account number

Implementation:
  Override Step 4: Notify Acme-specific handler
  Add Step 5: Log in Acme audit system
```

### Step 4: Configuration & Customization

```
Use Data Objects for configuration (not hard-coded rules):
  Data-AccountLimits
    OrganizationName, TransactionLimit, DailyLimit

Implementation layer creates:
  Data-AccountLimits-BankAcme {TransactionLimit: 50000, DailyLimit: 500000}
```

---

## Layer Cake Best Practices

### 1. Clear Ownership & Governance

```
Organization Layer:
  Owner: Platform Engineering
  Review: Change Control Board
  Release: Quarterly

Division Layer:
  Owner: Business Analysts
  Review: Product Owner
  Release: Monthly (per division)

Implementation Layer:
  Owner: Customer Team
  Review: Customer CTO
  Release: As-needed
```

### 2. Minimize Implementation Overrides

**Anti-Pattern:** Overriding 80% of framework rules → code duplication
**Better:** Design flexible framework with configuration hooks

```
Bad:
  Framework: Activity-ClaimApproval (hardcoded rules)
  Implementation: Override 5/7 steps

Better:
  Framework: Activity-ClaimApproval (calls Decision: GetApprovalRules)
  Implementation: Custom Decision-GetApprovalRules (no override)
```

### 3. Document & Communicate

- Maintain layer responsibility matrix
- Document which rules are "extension points" (meant to be overridden)
- Version framework layer separately from organization layer

### 4. Version Management

```
Version Format: [Org].[Division].[Impl]
  Organization-Core: v2.1.0
  Banking-Framework: v1.0.0
  Bank-Acme-Impl: v1.0.2

Implementation can depend on Framework v1.x
  (compatible with Framework 1.0, 1.1, 1.2, etc.)
```

---

## Debugging Rule Resolution in Multi-Layer Applications

### Issue: Wrong Rule Executing

**Symptom:** Business logic not matching implementation requirements

**Debug Steps:**
1. Check rule execution trace:
   ```
   SMA → System → Debug → Execution Trace
     Activity: Which rule executed?
     Package: Which layer (Organization, Division, Implementation)?
   ```

2. Verify rule precedence:
   ```
   Application Explorer → Activity CheckOrder
     Check "Available in" (which packages)
     Check inheritance (extends from which layer)
   ```

3. Confirm search path:
   ```
   System Settings → Layer Configuration
     Implementation layer listed first? (highest priority)
   ```

### Issue: Framework Update Not Inherited

**Symptom:** Framework improved rule; implementation still using old version

**Cause:** Implementation layer has override

**Fix:**
1. Compare framework rule vs implementation rule
2. If override not needed, delete implementation rule
3. Implementation will then inherit framework version

---

## Summary & Checklist

- Layer Cake: Organization (foundation) → Division (framework) → Implementation (customer)
- Rule resolution: Check Implementation first; fall back to Division, then Organization
- Each layer has clear ownership and deployment cycle
- Reuse across customers saves 80% development time
- Design frameworks with extension points, not overrides
- Document which rules are meant to be customized
- Monitor layer configurations; prevent accidental overrides
- Version dependencies; track compatibility
- Use configuration objects instead of hard-coded rules
"""
    },
    {
        "title": "Connect Rules Deep Dive — REST, SOAP, CMIS, SAP, JMS",
        "url": "https://pega.docs/platform/connect-rules",
        "content": """
# Connect Rules Deep Dive — REST, SOAP, CMIS, SAP, JMS

## Overview: What Are Connect Rules?

**Connect Rules** (also called Connectors) are Pega's integration framework for calling external systems. They handle authentication, request/response mapping, error handling, and retry logic—removing the need to write custom integration code.

### Supported Connector Types:

- **Connect-REST**: HTTP/HTTPS REST APIs
- **Connect-SOAP**: XML-based SOAP web services
- **Connect-CMIS**: Document management (Alfresco, SharePoint)
- **Connect-JMS**: Message queues (IBM MQ, RabbitMQ)
- **Connect-SAP**: SAP BAPI calls (synchronous)
- **Connect-File**: File I/O (read/write local/network)
- **Connect-Database**: Stored procedures, SQL

---

## Connect-REST Configuration

### Basic Setup:

1. **Create Connector** in Designer
   ```
   Build → Integration → Connectors → New → Connect-REST
   Name: ServiceName-GetCustomer
   Endpoint: https://api.example.com/v1/customers/{customerID}
   ```

2. **Define Request:**
   ```
   Method: GET (or POST, PUT, DELETE)
   Headers:
     Content-Type: application/json
     Authorization: Bearer {AuthToken}
   Timeout: 30 seconds (default)
   Retry: 3 attempts, 5 second backoff
   ```

3. **Map Request Parameters:**
   ```
   URL Path: /customers/{customerID} → FROM: WorkObject.CustomerID
   Query String: ?status=active&limit=100
   Request Body: (For POST/PUT)
     {
       "firstName": "{Customer.FirstName}",
       "lastName": "{Customer.LastName}",
       "email": "{Customer.Email}"
     }
   ```

4. **Map Response:**
   ```
   Success Response (200 OK):
     {
       "id": "C12345",
       "name": "John Doe",
       "status": "active",
       "createdDate": "2024-01-01T10:00:00Z"
     }
     Map to:
       WorkObject.CustomerID = response.id
       WorkObject.CustomerName = response.name
       WorkObject.Status = response.status
   ```

### Authentication Options:

| Type | Use Case | Config |
|------|----------|--------|
| **None** | Public API | No auth header |
| **Basic Auth** | Username/password | Base64 encode in header |
| **Bearer Token** | OAuth, API keys | Header: `Authorization: Bearer {token}` |
| **API Key** | Query or header param | Custom header with key |
| **OAuth 2.0** | Delegated access | Token endpoint, refresh token |

**Example: Bearer Token**
```
In Connector:
  Header: Authorization = Bearer {.APIKey}
In Activity:
  .APIKey = GetOAuthToken()  // Fetch token
  Call ServiceName-GetCustomer
```

---

## Connect-SOAP Configuration

### WSDL Import Workflow:

1. **Import WSDL:**
   ```
   Build → Integration → Connectors → New → Connect-SOAP
   WSDL URL: https://service.example.com/soap?wsdl
   Click "Import"
   ```
   Pega parses WSDL and auto-generates:
   - Service operations (methods)
   - Request/response message structures
   - Data type mappings

2. **Select Operation:**
   ```
   Available Operations:
     - GetCustomer
     - UpdateCustomer
     - CreateOrder
   Select: GetCustomer
   ```

3. **Map Parameters:**
   ```
   SOAP Request:
     <soap:Body>
       <GetCustomer>
         <customerID>{WorkObject.CustomerID}</customerID>
         <includeHistory>true</includeHistory>
       </GetCustomer>
     </soap:Body>

   Map Response:
     response.customer.name → WorkObject.CustomerName
     response.customer.status → WorkObject.Status
   ```

### SOAP-Specific Options:

- **SOAP Version**: 1.1 or 1.2
- **WS-Security**: Encrypt request/response
- **SOAP Attachments**: Include binary files
- **Namespace Handling**: Auto-map or custom

---

## Connect-CMIS Configuration

**CMIS** (Content Management Interoperability Services) is a standard for document management integration.

### Setup for SharePoint/Alfresco:

```
Connector: Document-Repository-Upload
Type: Connect-CMIS
Repository URL: https://sharepoint.example.com/alfresco/cmis
Operation: CreateDocument
Authentication: OAuth (SharePoint) or Basic (Alfresco)

Parameters:
  FolderPath: /Claims/{CaseID}/
  DocumentName: {ClaimID}_Attachment
  Content: {BinaryDocument}  // File content
  Properties:
    ClaimType: {Claim.Type}
    ClaimID: {Claim.ID}
```

### Common Operations:

- **Create Document**: Upload file to repository
- **Update Document**: Modify file/properties
- **Delete Document**: Remove from repository
- **Query Documents**: Search by metadata
- **Get Document**: Download file

---

## Connect-JMS Configuration

**JMS** (Java Message Service) enables asynchronous messaging with queues/topics.

### Setup for IBM MQ or RabbitMQ:

```
Connector: OrderQueue-Send
Type: Connect-JMS
Broker URL: tcp://mq.example.com:61616  // IBM MQ
Or: amqp://rabbitmq.example.com:5672  // RabbitMQ

Queue/Topic: ORDER_REQUESTS
Message Type: Text (or Bytes)
Correlation ID: {Order.OrderID}  // Track message

Request Mapping:
  {
    "orderID": "{Order.OrderID}",
    "customerID": "{Order.CustomerID}",
    "amount": {Order.TotalAmount},
    "items": [{Order.Items[]}]
  }
```

### Features:

- **Async Processing**: Fire-and-forget; no response wait
- **Persistence**: Messages survive broker restart
- **Dead Letter Queue**: Failed messages routed here
- **TTL (Time to Live)**: Auto-expire old messages

---

## Connect-SAP Configuration

**SAP BAPI** (Business Application Programming Interface) calls are synchronous RPC-style integrations.

### Setup for SAP ERP:

```
Connector: SAP-CreateSalesOrder
Type: Connect-SAP (via RFC or webservice)
BAPI Name: BAPI_SALESORDER_CREATE
Authentication: SAP user + password (or SSO)

Import Parameters:
  HEADER: {
    DOC_TYPE: "TA",           // Sales Order
    SALES_ORG: "1000",
    DIST_CHANNEL: "10"
  }
  ITEMS: [{
    MATERIAL: "{Order.PartNumber}",
    ORDER_QUANTITY: {Order.Qty},
    NET_PRICE: {Order.UnitPrice}
  }]
  PARTNER: [{
    PARTN_ROLE: "AG",         // Bill-to party
    PARTN_NUMB: "{Customer.SAPVendorID}"
  }]

Return Parameters (mapped to Work object):
  SALESDOCUMENT → Order.SAPOrderNumber
  RETURN (error messages) → Order.SAPErrorText
```

### BAPI Best Practices:

- **Commit BAPI**: Call BAPI_TRANSACTION_COMMIT after creation
- **Idempotency**: Use unique external ID to prevent duplicates
- **Error Mapping**: Map RFC errors to user-friendly messages

---

## Request/Response Mapping

### Complex Data Transformation:

```
REST API Response (nested JSON):
{
  "data": {
    "customer": {
      "id": 123,
      "contact": {
        "name": "John",
        "email": "john@example.com"
      }
    }
  }
}

Pega Mapping (using JSONPath):
  response.data.customer.id → .CustomerID
  response.data.customer.contact.name → .CustomerName
  response.data.customer.contact.email → .CustomerEmail

SOAP Response (XML):
<soap:Body>
  <GetCustomerResponse>
    <Customer>
      <ID>123</ID>
      <Name>John</Name>
    </Customer>
  </GetCustomerResponse>
</soap:Body>

Pega Mapping (using XPath):
  //Customer/ID → .CustomerID
  //Customer/Name → .CustomerName
```

---

## Error Handling in Connect Rules

### Response Status Codes:

```
200-299: Success
  → Execute success mapping
  → Continue flow

3xx: Redirection
  → Follow redirect (automatic in HTTP client)

4xx: Client Error (Bad Request)
  → Unrecoverable; go to error handler
  → Example: 400 (invalid input), 401 (auth failed), 404 (not found)

5xx: Server Error (Temporary)
  → Potentially recoverable; retry
  → Example: 500 (internal error), 503 (service unavailable)
```

### Error Handling Strategy:

```
In Connector:
  Success Path: HTTP 200-299 → Map response
  Error Path 1: HTTP 4xx → Log and fail (no retry)
  Error Path 2: HTTP 5xx → Retry with backoff
  Timeout: 30s → Retry 3 times, then fail

In Activity:
  Try:
    Call Connect-REST
  Catch HTTP_ERROR:
    Log error message
    Notify user
    Rollback transaction
```

---

## Timeout Configuration

### Setting Timeout:

```
In Connector:
  Read Timeout: 30 seconds (wait for response)
  Connection Timeout: 10 seconds (establish connection)
  Total Timeout: 60 seconds (end-to-end)

Rule of Thumb:
  Fast API (lookup) → 5-10 seconds
  Medium API (processing) → 15-30 seconds
  Slow API (heavy processing) → 45-120 seconds
```

### Handling Timeout:

```
If timeout occurs:
  → No response received
  → Treat as transient error
  → Retry with exponential backoff

After max retries:
  → Fail and log
  → Return error to user
  → Consider fallback (cached value, default behavior)
```

---

## Connection Pool Settings

### HTTP Connection Pooling:

```
System Settings → Connectivity → HTTP Connection Pool
  Max Connections: 100 (total)
  Max Per Host: 10 (per domain)
  Timeout: 30 seconds (reuse idle connection)

Impact:
  Pool exhausted → New connections queued; latency increases
  Idle connections → Recycled every 30s; reduces memory
```

---

## Debugging Connector Failures

### Issue: Timeout Errors

**Symptom:** "HTTP request timed out after 30 seconds"
**Root Causes:**
1. External service is slow (database query taking 2+ min)
2. Network latency or routing issue
3. Firewall blocking connection

**Debug:**
```
curl -v -m 30 https://api.example.com/endpoint
  → Check response time
  → Verify network latency (ping)
  → Test from Pega server directly
```

### Issue: Authentication Failure (401)

**Symptom:** "Unauthorized — Invalid credentials"
**Root Causes:**
1. Bearer token expired
2. API key incorrect or revoked
3. User account permissions insufficient

**Debug:**
1. Verify token in connector (SMA → Connector logs)
2. Test auth with curl:
   ```
   curl -H "Authorization: Bearer {TOKEN}" https://api.example.com
   ```
3. Refresh token if using OAuth

### Issue: Response Mapping Error

**Symptom:** "Unable to map response: Field not found"
**Root Causes:**
1. API response structure changed (API versioning)
2. JSONPath/XPath selector incorrect
3. Field name typo

**Debug:**
1. Log raw response:
   ```
   In Connector: Enable "Log Full Response"
   ```
2. Verify JSONPath selector online (jsonpath.com)
3. Check API documentation for latest schema

### Issue: Connector Hangs

**Symptom:** Activity blocked indefinitely; connector never returns
**Root Causes:**
1. External system deadlock
2. Missing timeout configuration
3. Thread exhaustion in pool

**Fix:**
1. Add timeout to connector (max 60 sec)
2. Monitor thread pool: SMA → Performance → Thread Pool
3. Restart application if threads exhausted

---

## Summary & Checklist

- Connect Rules automate external integrations (REST, SOAP, CMIS, JMS, SAP)
- Configure endpoint, auth, timeout, request/response mapping
- Use appropriate auth (Bearer token, OAuth, API key)
- Map request/response using JSONPath, XPath, or XML
- Handle errors: 4xx (no retry), 5xx (retry), timeout (retry)
- Set timeouts based on expected service latency
- Monitor connection pool; increase if exhausted
- Enable logging for troubleshooting connector failures
- Implement retry strategy with exponential backoff
"""
    },
    {
        "title": "Pega System Pulse & Inter-Node Communication",
        "url": "https://pega.docs/platform/system-pulse-cluster",
        "content": """
# Pega System Pulse & Inter-Node Communication

## What is System Pulse?

**System Pulse** is Pega's real-time message bus that enables inter-node communication in a clustered environment. It ensures cache consistency, distributes rule updates, and synchronizes system state across all application servers.

### Core Functions:

1. **Cache Invalidation**: When rule updated on Node A, pulse notifies Node B, C, D to clear cache
2. **System State Sync**: Rule version, user session, application state consistent across cluster
3. **Rule Distribution**: New rule deployed; pulse broadcasts to all nodes immediately
4. **Heartbeat & Health**: Nodes announce "I'm alive" periodically; dead nodes detected

---

## How Nodes Communicate in a Cluster

### Cluster Architecture:

```
Load Balancer
  ↓
┌─────────────┬──────────────┬──────────────┐
│   Node 1    │   Node 2     │   Node 3     │
│ (Tomcat)    │ (Tomcat)     │ (Tomcat)     │
└──────┬──────┴────────┬──────┴──────┬──────┘
       │               │             │
       └───────────────┼─────────────┘
                Pulse Bus
         (Hazelcast or Ignite)
```

### Communication Flow:

```
User Action on Node 1: Create new Activity "CheckOrder"
  ↓
Node 1 saves to database & notifies Pulse
  ↓
Pulse broadcasts: "NEW_RULE: Activity/CheckOrder" to Node 2, 3
  ↓
Node 2 & 3 receive notification:
  - Invalidate local rule cache
  - Reload rule from database on next reference
  ↓
Next user on Node 2 calls CheckOrder:
  - Cache miss → Fetch from database
  - New version loaded; executed
```

---

## Pulse Messages for Cache Invalidation

### Message Types:

| Message Type | Triggered By | Action |
|--------------|--------------|--------|
| **RULE_CREATE** | New rule created | Clear rule cache globally |
| **RULE_UPDATE** | Rule modified | Clear cache, reload on next use |
| **RULE_DELETE** | Rule deleted | Remove from cache, use fallback |
| **CLASS_UPDATE** | Class properties changed | Update schema cache |
| **DATA_CHANGE** | Data object modified | Notify dependent caches |
| **NODE_JOIN** | New node starts | Sync state; distribute load |
| **NODE_LEAVE** | Node stops/crashes | Rebalance work; notify users |

### Example: Rule Update Broadcast

```
Scenario: Developer updates Activity "ProcessOrder" on Node 1

1. Dev saves rule in Designer (Node 1)
   → Database row updated
   → Pulse message: {Type: RULE_UPDATE, RuleType: Activity, Name: ProcessOrder}

2. Pulse broadcasts to Node 2, 3, 4
   → Each node receives notification

3. Each Node Action:
   Node 2: If cached, invalidate
           Next call to ProcessOrder → Fetch from database (new version)
   Node 3: Same as Node 2
   Node 4: Cache already expired; reload on demand

4. All users globally now see new version (within milliseconds)
```

---

## Pulse for Rule Updates Across Nodes

### Deployment Flow (Zero-Downtime):

```
Scenario: Deploy new version of service to all 5 nodes

Traditional (no cluster):
  1. Stop Node 1 → Deploy → Start Node 1
  2. Stop Node 2 → Deploy → Start Node 2
  3. Stop Node 3 → Deploy → Start Node 3
  (Users unavailable during each node restart)

With Cluster + Pulse:
  1. Deploy to database (all rules updated)
  2. Pulse broadcasts RULE_UPDATE to all nodes
  3. All nodes invalidate cache simultaneously
  4. No restart required; no downtime
  5. Users continue working seamlessly
```

### Cache Invalidation Across Nodes:

```
Node 1 Local Cache (In-Memory):
  Activity.ProcessOrder (v1) → expires on RULE_UPDATE message

Node 2 Local Cache:
  Activity.ProcessOrder (v1) → expires on RULE_UPDATE message

Node 3 Local Cache:
  Activity.ProcessOrder (v1) → expires on RULE_UPDATE message

All nodes simultaneously:
  Next reference → Cache miss
  → Fetch from database (v2)
  → Rebuild local cache with new rule
```

---

## Hazelcast/Ignite Cluster Communication

### Hazelcast (Default Distributed Cache):

Pega uses **Hazelcast** as the underlying distributed cache and messaging layer.

**Features:**
- **In-Memory Data Grid**: Shared cache across cluster
- **Map-Reduce**: Distributed computation
- **Pub-Sub**: Messaging between nodes
- **Cluster Topology**: Discovery, failover, rebalancing

**Configuration (System Settings):**
```
Cluster Manager: Hazelcast
Network:
  Multicast Discovery: Enabled (auto-detect nodes)
  Or Static Members: node1:5701, node2:5701, node3:5701

Cache Partitioning:
  Partition Count: 271 (default; distribute data)
  Backup Count: 1 (each partition has 1 replica)
```

### Apache Ignite (Alternative):

**Ignite** is an alternative to Hazelcast with SQL support.

**Features:**
- **Distributed SQL**: Query across cluster
- **Persistence**: Data survives cluster shutdown
- **Compute Grid**: Distributed Java jobs
- **Streaming**: Real-time data ingestion

**Configuration:**
```
Cluster Manager: Apache Ignite
Data Nodes: 3
Backup Copies: 1

Impact:
  - More powerful than Hazelcast
  - Heavier resource usage (CPU, memory)
  - Better for data-intensive applications
```

---

## Debugging Cluster Sync Issues

### Issue: Stale Cache (Old Rule Executing)

**Symptom:** New rule deployed; some nodes still using old version
**Root Causes:**
1. Pulse message not received by node
2. Node not restarted; cache not cleared
3. Network partition between nodes

**Debug Steps:**

1. Check Cluster Status: **SMA → Cluster → Nodes**
   ```
   Node 1: Connected, Cache Size: 12MB
   Node 2: Connected, Cache Size: 11MB
   Node 3: DISCONNECTED ← Problematic

   Action: Restart Node 3 to re-join cluster
   ```

2. Verify Pulse Health:
   ```
   SMA → Cluster → Pulse Health
   Message Rate: 100 msg/sec (normal)
   Failed Messages: 0 (good)
   Node 3: Last Heartbeat: 30 min ago (STALE)

   Action: Network issue or Node 3 hung; restart required
   ```

3. Check Network Connectivity:
   ```
   From Node 1 to Node 3:
   telnet node3.example.com 5701  ← Hazelcast port
   [Connection refused] → Network blocked or service down

   Fix: Check firewall rules; restart Hazelcast service on Node 3
   ```

4. Clear Local Cache Manually:
   ```
   In Designer on affected node:
   Administration → System → Caches → Flush All
   OR via SMA → Diagnostics → Clear Caches
   ```

### Issue: Nodes Not Receiving Updates

**Symptom:** Rule updated on Node 1; Node 2 still has old version
**Root Causes:**
1. Network partition (nodes cannot communicate)
2. Pulse bus stopped or crashed
3. Node has crashed; cluster thinks it's dead

**Debug:**

```
1. Verify cluster membership:
   SMA → Cluster → Nodes
     All nodes showing "Connected"?
     All nodes same cluster ID?

2. Check Pulse messages in logs:
   Application logs → Filter: "PULSE"
   Look for: [PULSE] Message received from Node X

3. Force cluster resync:
   SMA → Cluster → Force Sync
   → All nodes rebuild distributed cache
   → May cause brief I/O spike (DB read)

4. Monitor cache hit rate:
   SMA → Performance → Cache Statistics
   Hit Rate: 95%+ (good)
   Hit Rate: <50% (stale cache; rebuild needed)
```

---

## Configuring Pulse Frequency

**Pulse Configuration (System Settings):**

```
Cluster Settings → Pulse
  Heartbeat Interval: 5000 ms (5 sec)
    → Nodes announce "I'm alive" every 5 sec
    → Lower = faster failure detection; higher CPU

  Failure Detection Timeout: 30000 ms (30 sec)
    → If no heartbeat for 30 sec, node marked dead
    → Lower = faster failure response; false positives risk

  Cache Expiration: 3600 sec (1 hour)
    → Cached rules auto-expire after 1 hour
    → Ensures rule version consistency even without pulse
```

**Tuning Guidelines:**

```
High-Frequency Trading / Real-Time Systems:
  Heartbeat: 1000 ms (faster detection)
  Failure Detection: 10000 ms
  → Quick failover; higher CPU cost

Stable Internal Applications:
  Heartbeat: 10000 ms (default 5000)
  Failure Detection: 60000 ms
  → Lower CPU; slower failover acceptable
```

---

## Monitoring Pulse Health

**In SMA → Cluster → Pulse Dashboard:**

```
Metrics:
  Total Messages: 50,000 (lifetime)
  Messages/Sec: 125 (current throughput)
  Failed Messages: 0 (successful delivery)
  Retry Count: 5 (across cluster)

Per-Node Metrics:
  Node 1: 45 messages sent, 1200 ms latency
  Node 2: 42 messages sent, 800 ms latency
  Node 3: 38 messages sent, 2500 ms latency ← Slow network?

Network Health:
  Packet Loss: 0% (no loss)
  Latency P99: 500 ms (99th percentile)
```

**Alert Thresholds:**

```
CRITICAL:
  - Node unreachable (no heartbeat > 60s)
  - Failed messages > 10/sec (delivery issues)

WARNING:
  - Latency > 2000 ms (slow network)
  - Messages/sec < baseline (bottleneck)
```

---

## Best Practices for Cluster Communication

1. **Network Configuration**
   - Dedicated network for Pulse (lower latency)
   - 1 Gbps or higher network speed
   - Low packet loss (< 0.1%)
   - Firewall allows Hazelcast ports (5701+)

2. **Cluster Sizing**
   - 2-3 nodes: High availability + load distribution
   - 5+ nodes: Scale-out for throughput
   - Odd number of nodes (quorum for split-brain)

3. **Monitoring & Alerting**
   - Alert on node disconnect
   - Track pulse latency; alert if > 5 sec
   - Monitor failed message count

4. **Graceful Shutdown**
   ```
   To remove node from cluster:
     1. Drain connections (stop accepting new requests)
     2. Notify cluster: SMA → Cluster → Decommission Node
     3. Wait for in-flight work to complete
     4. Shutdown Pulse service
     5. Shutdown application server
   ```

---

## Summary & Checklist

- System Pulse enables cache invalidation and rule distribution
- Nodes communicate via Hazelcast (or Ignite) cluster bus
- Rule updates broadcast to all nodes; cache invalidated automatically
- Configure heartbeat interval and failure detection timeout
- Monitor pulse health: message rate, latency, failed messages
- Troubleshoot stale cache by checking cluster membership
- Network connectivity critical: test firewall ports, latency
- Force cluster resync if nodes out of sync
- Scale cluster: 2+ nodes for HA, 5+ for throughput
"""
    }
]

def seed_phase16():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE16:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase16_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(__import__('json').dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE16)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 16 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase16()
