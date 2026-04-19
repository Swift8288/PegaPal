"""
Curated Pega Knowledge Base — Phase 10 (Advanced Case Management & Processing)
Run: python -m crawler.seed_kb_phase10
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE10 = [
    {
        "title": "Case Locking & Optimistic Locking",
        "url": "https://pega.example.com/case-locking-guide",
        "content": """
# Case Locking & Optimistic Locking in Pega

## Overview
Case locking prevents concurrent modifications from overwriting each other. Pega supports **optimistic** and **pessimistic** locking strategies.

### Optimistic vs Pessimistic Locking
- **Optimistic**: No lock acquired; assumes conflicts are rare. Checks version/timestamp before commit. Fails if another user changed data.
- **Pessimistic**: Lock acquired immediately when case opened. Only one user can edit at a time.

## Lock Mechanism
- **Lock Conflict**: "Case is being modified by another user" error occurs when optimistic lock detects version mismatch.
- **Lock Timeout**: Controlled by DSS property `Lock Timeout (seconds)`. Default 300s (5 min). Orphaned locks auto-release.
- **Lock Mode**: Set via flow or case configuration. Pessimistic = safer but slower. Optimistic = faster but requires conflict handling.

## Common Issues & Debugging

### Error: "Case is being modified by another user"
```
Root causes:
1. Optimistic lock conflict—version changed between read and write
2. Previous user didn't release lock (network disconnect)
3. Lock timeout too short for long operations
4. Concurrent batch updates on same case
```

**Debug Steps**:
1. Check `pr_case_locks` table: `SELECT * FROM pr_case_locks WHERE pzinskey = 'CASE_ID'`
2. Verify lock timeout setting: Admin > System > Advanced Settings > Lock Timeout
3. Review database connection timeouts
4. Check for orphaned locks: `SELECT * FROM pr_case_locks WHERE created < NOW() - INTERVAL 5 MINUTE`

### Performance: Lock Contention
- High lock conflicts slow UI (retry loops, user frustration)
- Monitor: Reports > Performance > Case Lock Contention
- Solution: Use optimistic locking for read-heavy workloads; pessimistic for critical sections

## DSS Configuration
- **Property**: `Lock Wait Timeout`—how long system waits before failing lock attempt
- **Property**: `Lock Heartbeat Interval`—how often lock holder signals "still alive"
- **Enable Lock Logging**: System > Diagnostics > Trace Database Locks

## Best Practices
1. Keep case-open duration short to minimize lock hold time
2. Use optimistic locking for high-traffic cases
3. Implement pessimistic locking only in serial workflows (approval chains)
4. Monitor lock metrics in prod; alert on conflicts > 5%
5. Educate users: closing cases releases locks promptly

## Monitoring & Troubleshooting
- Query `pr_case_locks` to find locked cases
- Use Pega diagnostic tool: System > Diagnostics > Case Locks
- Check database log for lock timeout errors
- Review operator activity: Admin > Operator Activity Monitoring > Lock Events
"""
    },
    {
        "title": "Case Archival & Purging",
        "url": "https://pega.example.com/archival-purging-guide",
        "content": """
# Case Archival & Purging in Pega

## Archival Strategy
Archival moves completed cases to reduce database size while retaining audit trail.

### Archive Targets
1. **Database Table**: Default archive to separate `_archived` table in same DB
2. **External Database**: Archive to historical DB; reduces prod DB load
3. **Cloud Storage**: Archive to AWS S3 or Azure Blob; cheapest long-term option
4. **File System**: Archive to network share (not recommended for performance)

## Archival Process
- **Trigger**: Completed cases auto-archive after configurable retention period (default: 90 days)
- **Selective Archival**: Archive by status, class, creation date using archival criteria
- **Batch Job**: Admin > Data Management > Archive Cases (runs nightly)

### Archive Impact
- **Reporting**: Archived cases excluded from default queries; use archival views or restore if needed
- **Case Search**: Search across active cases only (unless configured to search archive)
- **Performance**: Reduces main table size; improves query speed by 10-40%

## Purging Strategy
Purging **permanently deletes** cases—use only after compliance retention period expires.

### Purge Configuration
- **Retention Policy**: Define in case type > Case Archival rules
- **Purge Frequency**: Weekly/monthly batch purge (System > Rules > Purge Utility)
- **Dependency Check**: System checks for linked cases, workflows, attachments before purge

### Common Purge Errors
```
Error: "Cannot purge case—linked cases exist"
→ Purge parent/child in dependency order
→ Use cascading purge (if configured)

Error: "Purge job timeout after 5 hours"
→ Batch size too large; reduce from 10K to 5K cases/batch
→ Schedule during low-traffic window (2 AM)
```

## Restoring Archived Cases
1. Query archival table or restore from backup
2. Use Import Tool to reload into `pxcase`
3. Re-index case and reattach documents
4. Validate case status and history

## Data Retention Compliance
- **GDPR**: Purge PII after 3 years (or per policy)
- **Audit**: Maintain case history before purge; export to compliance warehouse
- **Regulatory**: Some industries require 7-year retention—adjust policy accordingly

## Debugging Archival Issues

**Archived Case Not Found**:
- Check: Admin > Data Management > Archival Logs
- Query: `SELECT COUNT(*) FROM case_archived WHERE case_id = 'X'`
- Verify archival job ran: System > Job Scheduler > Archive Cases

**Purge Job Stalled**:
- Check database locks on purge table
- Verify disk space available
- Monitor CPU/memory; reduce batch size if spikes

## Best Practices
1. Archive cases automatically on completion; don't require manual trigger
2. Test archive/restore in dev before prod rollout
3. Keep audit trail even after case purge (separate audit log)
4. Monitor archival job success rate; alert on failures
5. Schedule purge during maintenance windows only
"""
    },
    {
        "title": "Bulk Case Processing",
        "url": "https://pega.example.com/bulk-case-processing-guide",
        "content": """
# Bulk Case Processing in Pega

## Bulk Case Creation
Processing thousands of cases from batch data (CSV, API, queue).

### Data Flow Strategy
1. **Inbound Queue**: Store raw data in processing queue
2. **Batch Flow**: Trigger flow for each row; create/update case
3. **Async Processing**: Use request ID tracking to monitor progress
4. **Error Handling**: Log failed cases; retry or escalate

### Queue Processor Configuration
- **Processor Type**: Default queue processor (System > Advanced > Queue Processor)
- **Thread Count**: Scale to CPU cores; e.g., 8-core server = 8 threads
- **Batch Size**: Balance memory vs throughput; default 100 cases/batch
- **Retry Logic**: Retry failed entries 3 times before moving to error queue

## Performance Considerations

### Bulk Update Strategies
- **Single-Step Update**: Update one field per case (fast, 1000 cases/min)
- **Multi-Step Update**: Update multiple fields per case (slower, 100 cases/min)
- **Mass Reassignment**: Reassign cases to different operator (moderate, 500 cases/min)

### Optimization Tips
```
1. Disable triggers during bulk load (DB constraint checks slow updates)
   → Re-enable after load complete
2. Batch commit every 100 cases; don't commit each row (SQL overhead)
3. Pre-validate data before processing; reject bad rows upfront
4. Use data transform (pzInsKey local) for field mapping
5. Index case search properties (status, create_date) for filter speed
```

### Monitoring Bulk Operations
- **Job Monitor**: Admin > Operations > Job Monitor > Watch Batch Job
- **Metrics**:
  - Cases processed/sec
  - Error rate (target < 1%)
  - Memory usage (alert if > 80%)
  - Processing time (ETA)
- **Database Load**: Monitor INSERT/UPDATE throughput; avoid peak hours

## Common Issues

**Issue: Bulk Job Runs Out of Memory**
```
Symptom: Job crashes after 5K cases; OutOfMemoryError
Solution:
1. Reduce batch size from 500 to 100
2. Increase JVM heap: -Xmx4g (4GB)
3. Clear cache between batches: Pega.clear()
4. Split 100K case job into 10x 10K sub-jobs
```

**Issue: Duplicate Cases Created**
```
Symptom: 10% of cases created twice
Root Cause: Batch job restarted; didn't track processed records
Solution:
1. Add request ID to track batch; skip already-processed
2. Use database transaction log to find last successful commit
3. Query: SELECT COUNT(DISTINCT case_id) to verify uniqueness
```

## Best Practices
1. Dry-run bulk job on sample data (100 cases) before full load
2. Implement idempotent case creation (safe to retry)
3. Log all failures with root cause; don't silently skip
4. Monitor system resources during bulk processing
5. Schedule bulk jobs during maintenance windows (off-peak)
6. Validate data quality before and after bulk load
7. Keep detailed audit trail for compliance
"""
    },
    {
        "title": "Case Attachments & Document Management",
        "url": "https://pega.example.com/attachments-document-guide",
        "content": """
# Case Attachments & Document Management in Pega

## Attachment Storage Options

### Database BLOB Storage
- **Default**: Attachments stored in `prpc_case_attach` table as BLOB
- **Pros**: Simple; backed up with database; transactional consistency
- **Cons**: Inflates DB size; slower; backup overhead
- **Use Case**: Small files (<10MB), high-security requirements

### File Repository Storage
- **Network Share**: Attachments on NAS/SMB share; DB stores path reference
- **Pros**: Reduces DB size; faster I/O; external backup
- **Cons**: Network dependency; requires permissions management; external backup
- **Use Case**: Medium files (10-500MB), moderate security

### Cloud Storage (S3/Azure Blob)
- **AWS S3**: Most flexible; scales infinitely; CDN-compatible
- **Azure Blob**: Native to Microsoft environments; integrates with Teams
- **Pros**: Lowest cost; highest scalability; managed backups
- **Cons**: Network latency; requires cloud credentials; compliance considerations
- **Use Case**: Large files (>500MB), scalable, cost-optimized systems

## Attachment Categories & Metadata
- **Category**: Define in Case Type; e.g., "Supporting Docs", "Approval Signatures"
- **Metadata**: Attachment name, size, upload date, operator, MIME type
- **Encryption**: Optional; encrypt at-rest for PII documents
- **Retention**: Auto-delete attachments after case archive (configurable)

## Size Limits & Virus Scanning

### Size Configuration
- **Max Upload**: Default 50MB; configure in Application Settings
- **Max Case Attachments**: Default 100 files/case
- **Storage Quota**: Monitor per-case attachment size; alert at 500MB+

### Virus Scanning
- **Scanner Integration**: ClamAV, Kaspersky, Windows Defender API
- **Scan on Upload**: Synchronous (blocks upload until scan done) or async
- **Quarantine**: Infected files blocked; operator notified; case flagged

## Common Attachment Errors

**Error: "Attachment upload failed—file too large"**
```
Solution:
1. Verify max upload size: Application Settings > Attachments > Max Size
2. Check server disk space: > 10% free required
3. Verify file repository permissions (if using external storage)
4. Browser upload timeout: increase from 30s to 300s
```

**Error: "Virus detected in attachment"**
```
Solution:
1. Verify scanner is running: System > Diagnostics > Antivirus Service
2. Quarantine logs: System > Logs > Antivirus Scan Results
3. Whitelist safe file types: .pdf, .docx (if needed for compliance)
4. Operator education: some files inherently flagged (executables, macros)
```

**Error: "Attachment not found—file deleted"**
```
Solution:
1. Check file repository: verify file exists on NAS
2. Query metadata: SELECT * FROM prpc_case_attach WHERE attach_id = 'X'
3. Restore from backup if recent deletion
4. Re-upload if necessary; maintain audit trail
```

## Viewing & Downloading Attachments
- **UI**: Case > Attachments tab > Download or inline view
- **API**: GET `/api/v1/cases/{caseId}/attachments/{attachmentId}/content`
- **Inline Preview**: PDF, images, text (supported); Office docs require Office365 integration
- **Virus Rescan**: Option to re-scan before download (audit trail)

## Best Practices
1. Default to cloud storage (S3/Azure) for new systems—cheaper, scalable
2. Enable virus scanning for all attachments
3. Set size limits reasonably (50-100MB per file)
4. Auto-purge attachments with archived cases
5. Encrypt sensitive documents at-rest
6. Monitor attachment storage growth; alert at 80% quota
7. Test disaster recovery for attachment restore
8. Document retention policy in case type metadata
"""
    },
    {
        "title": "Parallel Processing & Split-Join in Flows",
        "url": "https://pega.example.com/parallel-flows-guide",
        "content": """
# Parallel Processing & Split-Join in Flows

## Parallel vs Sequential Flows

### Sequential Execution
- Steps run one at a time; next step waits for previous to complete
- **Predictable**: Clear execution order; debugging easier
- **Slow**: Total time = sum of all steps; no concurrency

### Parallel Execution (Split-Join)
- Multiple paths execute simultaneously; main flow waits for all to complete
- **Fast**: Total time = longest step (not sum); higher throughput
- **Complex**: Timing issues, race conditions, deadlock risk

## Split-Join Shape Details

### Split (Fork) Configuration
- **Split Type**:
  - **Parallel**: All branches execute simultaneously
  - **Exclusive**: Only one branch executes (based on condition)
- **Synchronization Point**: Join waits for all parallel branches before proceeding
- **Timeout**: Optional; join continues if any branch exceeds time limit

### Join (Synchronization) Options
1. **Wait for All**: Standard; continue only when all branches complete
2. **Wait for Any**: Continue when first branch completes
3. **Wait with Timeout**: Abandon unfinished branches after timeout
4. **Conditional Join**: Continue only if branches meet condition (majority vote)

## When to Use Parallel Processing

### Good Use Cases
1. **Service Calls**: Call multiple external APIs in parallel (credit check, background check, address validation)
2. **Document Generation**: Create PDF, Excel, HTML versions simultaneously
3. **Case Creation**: Create multiple linked child cases in parallel
4. **Notifications**: Send email, SMS, Teams message at same time
5. **Audit Logging**: Log case change to multiple audit systems

### Avoid Parallel For
- **Dependent Steps**: If Branch B depends on Branch A output, must be sequential
- **Database Consistency**: Concurrent updates to same table risk corruption
- **Resource Limits**: If system CPU/memory limited, parallelism adds overhead
- **Debug/Testing**: Hard to reproduce race conditions

## Spin-Off Cases vs Parallel Paths

### Parallel Paths (Split-Join)
- Same case instance; sub-flows run in parallel
- Case remains open; blocked on join
- **Use For**: Fast, synchronous operations within same case

### Spin-Off Cases
- Create child case; parent continues (no wait)
- Parent case closes before children complete
- **Use For**: Asynchronous work; decoupling parent/child processes
- **Setup**: Create case in one branch; parent doesn't wait

## Debugging Parallel Flow Issues

**Issue: Join Never Completes (Hangs)**
```
Root Causes:
1. Deadlock—Branch A waits for Branch B; Branch B waits for A
2. Infinite loop in one branch
3. External service timeout (API unreachable)
4. Database lock on shared resource

Debug Steps:
1. Check flow tracer: Process > Show Tracer
   - See which branch is stuck
   - Timestamp shows how long each branch ran
2. Enable diagnostics: System > Diagnostics > Flow Execution
3. Query: SELECT * FROM flow_exec_log WHERE case_id='X' ORDER BY timestamp
4. Look for timeouts: API call exceeded 60s threshold
5. Monitor: Admin > System > Database Locks (check for deadlock)
```

**Issue: Race Condition—Data Corruption**
```
Symptom: Parallel branches both update same property; one value lost
Solution:
1. Use pessimistic locking: Flow > Case Options > Lock Case While Running
2. Add sync point: Use Utility shape to serialize critical section
3. Redesign: Avoid shared state; pass data via return values
4. Test: Run same case 100x in parallel; verify data consistency
```

**Issue: Performance Not Improved**
```
Symptom: Parallel doesn't run faster than sequential
Root Causes:
1. Branches have minimal work; fork/join overhead exceeds speedup
2. CPU bound; system can't run multiple threads
3. I/O wait on same database; contention
4. Network serialization; system waits for response

Optimization:
1. Profile branch duration: each > 1s for parallelism worth it
2. Increase CPU cores/threads available
3. Distribute database load across instances
4. Use async processing where possible (no join needed)
```

## Best Practices
1. Keep parallel branches independent (no data sharing)
2. Set timeout on join (don't wait indefinitely)
3. Test parallel flows under load (concurrent cases)
4. Log join/split points for monitoring
5. Use error handling to catch failed branches
6. Document why parallelism chosen (performance goal)
7. Monitor system resources during parallel execution
8. Prefer spin-off cases for truly async work
"""
    },
    {
        "title": "Case History & Audit Trail Deep Dive",
        "url": "https://pega.example.com/case-history-audit-guide",
        "content": """
# Case History & Audit Trail Deep Dive

## What Gets Logged in Case History

### Automatic History Entries
- **Case Status Change**: When case moves between lifecycle stages
- **Property Changes**: Each field update (old value → new value; timestamp; operator)
- **Assignment Change**: Case reassigned to different operator or queue
- **Action/Task Execution**: When work action completed (with timestamp)
- **Note Addition**: Case notes; who added; when
- **Approval**: Approval action (approved/rejected; comments)

### What Is NOT Logged
- Read-only views (viewing case doesn't create history entry)
- Internal housekeeping (cache refresh, reindex)
- Draft saves (only final commit logged)
- System updates (background maintenance)
- Certain metadata (like last accessed time)

## Custom History Entries

### Adding Custom History Programmatically
```
// Activity Trigger or Flow
obj_case.pxActivity.SetHistoryEntry("Manual Override: Status changed due to exception handling");

// Data Transform
.Set-Attribute("pxActivity", "Custom entry: Emergency escalation");
```

### Custom Entry Use Cases
1. **Manual Interventions**: Operator override reason
2. **System Actions**: Batch job updated case; which batch; ID
3. **External Events**: Received external notification; source
4. **Policy Changes**: Applied new business rule; justification
5. **Compliance Actions**: Audit action taken; signed off by

## History Search & Retrieval

### Search History UI
- Case > History tab > Filter by date range, operator, action type
- Full-text search in history content
- Export history to CSV for reporting

### Programmatic Access
```sql
SELECT * FROM case_history
WHERE case_id = 'X'
AND created_date > CURRENT_DATE - INTERVAL 30 DAY
ORDER BY created_date DESC;
```

### History Search Performance
- Index on case_id, created_date (automatic)
- Full-text search on comments slower (~500ms for large cases)
- Archive old history to separate table (> 1 year) for speed

## Compliance & Regulatory Requirements

### What Auditors Expect
1. **Tamper-Proof**: History cannot be edited/deleted (append-only)
2. **Complete**: Every case change logged with operator ID, timestamp
3. **Accessible**: Can produce history report on demand (GDPR, SOX)
4. **Retention**: Keep per policy (7 years for finance; 3 years for GDPR)
5. **Segregation**: Sensitive cases (HR, legal) logged separately with access controls

### GDPR Compliance
- Right to be forgotten: Purge history for subject (challenging—append-only design)
- Data minimization: Log only necessary fields (not full change details if PII)
- Audit trail: Prove who accessed/modified case

### SOX Compliance (Finance)
- Cannot modify history after creation (Pega enforces append-only)
- Segregation of duties: Different operators create vs approve
- Electronic signature on history entries for high-value transactions

## History Performance Impact

### Storage Overhead
- 1 case with 100 updates = ~50KB history data
- 1M cases * 100 updates * 50KB = **5TB** history storage
- Backup overhead; slower case queries if history joins

### Query Performance
- `SELECT * FROM pxcase` with large history = slow (avoid SELECT *)
- Index case lookup by ID; filter by date range
- Monitor: Reporting > Case History Query Performance

### Optimization
1. Archive history > 1 year to separate table
2. Compress old history (GZIP); maintain index on compressed dates
3. Use materialized views for reporting (don't query raw history)
4. Purge non-essential history (e.g., interim system updates)

## Reducing History Bloat

### What Causes Bloat
1. **Too Many Property Updates**: Changing same field 5 times per case
2. **Fine-Grained Logging**: Every micro-change logged
3. **System Auto-Updates**: Background jobs generating noise entries
4. **Copy Operations**: Copying case creates duplicate history entries

### Strategies to Reduce Bloat
1. **Batch Updates**: Combine 5 property changes into 1 data transform (1 entry instead of 5)
2. **Selective Logging**: Only log user-facing changes; skip internal housekeeping
3. **Summary Entries**: "Batch processing completed 500 updates" instead of 500 entries
4. **Archive Threshold**: Auto-archive history entries > 2 years old
5. **Retention Policy**: Delete low-value entries (e.g., draft saves) after 90 days

## Debugging Missing History Entries

**Issue: Property change not logged**
```
Root Causes:
1. Field not marked for history tracking (case type > Properties > History)
2. Operator permission missing (Case History view restricted)
3. History clearing: history purge job ran
4. Custom code bypassed history: direct database update

Debug Steps:
1. Verify property tracked: Case Type > Properties > select field > Check History flag
2. Check operator permissions: User Profile > Case History > View Permission
3. Query history: SELECT COUNT(*) FROM case_history WHERE case_id='X'
4. Review database audit log: Did history get deleted?
5. Check data transform: Did it use DB update vs Pega object update?
```

**Issue: History Search Returns No Results**
```
Solution:
1. Verify date range (default: last 30 days)
2. Check case_id spelling/format
3. Confirm search term in history content (case-sensitive)
4. Query: SELECT DISTINCT action_type FROM case_history WHERE case_id='X'
   - Verify expected actions exist
5. Check if case is archived (history moved to archive table)
```

## Best Practices
1. Enable history for all business-critical fields
2. Log custom entries for manual interventions
3. Archive history > 1 year to improve query speed
4. Monitor history table size (alert at > 1GB)
5. Test history retention/compliance policy annually
6. Document what is logged and why (for auditors)
7. Use history search for case audit trail and compliance reports
8. Regularly test history archive/restore process
"""
    }
]

def seed_phase10():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE10:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase10_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE10)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 10 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase10()
