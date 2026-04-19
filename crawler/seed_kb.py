"""
Curated Pega Knowledge Base Seeder
Pre-built debugging knowledge from Pega documentation, method references,
and common troubleshooting patterns.

Run: python -m crawler.seed_kb
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Curated Knowledge Base ─────────────────────────────────────────────
# Each entry: { "url": source, "title": title, "content": full text }

CURATED_DOCS = [
    # ═══════════════════════════════════════════════════════════════════
    # METHOD REFERENCES — Obj-* Methods
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/pxref/objsave-method.html",
        "title": "Obj-Save Method Reference",
        "content": """# Obj-Save Method Reference

## Overview
The Obj-Save method saves the contents of a clipboard page to the PegaRULES database. It writes data from the clipboard page to the corresponding database table row.

## Syntax
Obj-Save writes the top-level page and all embedded pages to the database. It performs an INSERT if the row does not exist, or an UPDATE if it does.

## Key Parameters
- **PageName**: The clipboard page to save. Must be a top-level page.
- **WriteNow**: If true, writes immediately without waiting for Commit. Default is false.
- **IfNotLocked**: If true, saves only if the current requestor holds a lock on the object.

## Common Errors

### "You cannot save a page that your session does not hold a lock on"
**Root Cause**: The work object was opened without acquiring a lock (Obj-Open with Lock=False or default), but Obj-Save requires a lock for lockable classes.
**Fix**:
1. In Obj-Open step, set Lock = True
2. Set ReleaseOnCommit = True to release after Commit
3. Ensure no downstream Obj-Open re-reads the same page without locking

### "Attempt to save an object that has been modified by another session"
**Root Cause**: Optimistic locking conflict. Another user or process modified the same work object between your Obj-Open and Obj-Save.
**Fix**:
1. Refresh the page with Obj-Refresh-And-Lock before saving
2. Implement retry logic in Queue Processor activities
3. Consider using pessimistic locking for high-contention objects

### "Obj-Save failed: primary page is not connected to a database table"
**Root Cause**: The class of the page being saved does not have a database table mapping.
**Fix**:
1. Check class mapping in Records > SysAdmin > Database Table
2. Ensure the class extends from a mapped class (e.g., Work-, Data-)
3. Run the Column Populator if columns are missing

## Best Practices
- Always acquire a lock before saving lockable objects
- Use WriteNow=True only when immediate persistence is required (e.g., in QP activities)
- Wrap Obj-Save in a try-catch to handle database exceptions
- Use Commit after Obj-Save to finalize the transaction
- In Queue Processor context, always use Lock=True on Obj-Open before Obj-Save
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/pxref/objopen-method.html",
        "title": "Obj-Open Method Reference",
        "content": """# Obj-Open Method Reference

## Overview
Obj-Open reads a single row from the PegaRULES database into a clipboard page. It is the primary method for loading work objects, data objects, and rule instances from the database.

## Key Parameters
- **PageName**: Name of the clipboard page to populate
- **ObjClass**: The class of the object to open
- **Lock**: Whether to acquire a lock on the object. Default is false.
- **ReleaseOnCommit**: Release the lock when Commit is called. Default is false.
- **pxObjClass**: Set automatically based on the class

## Locking Behavior
- Lock=True: Acquires a pessimistic lock. Required before Obj-Save on lockable classes.
- Lock=False (default): Opens in read-only mode. Obj-Save will fail on lockable classes.
- ReleaseOnCommit=True: Releases the lock when Commit executes.

## Common Errors

### "Object not found"
**Root Cause**: The specified pzInsKey or primary key does not match any row in the database.
**Fix**:
1. Verify the pzInsKey format matches the class key pattern
2. Check the database table directly to confirm the record exists
3. Ensure you're querying the correct database (dev/staging/prod)

### "Deadlock detected"
**Root Cause**: Two or more sessions are waiting for each other's locks.
**Fix**:
1. Reduce lock hold time — move Obj-Open(Lock=True) closer to Obj-Save
2. Ensure consistent ordering when locking multiple objects
3. Add retry logic with exponential backoff

### "Lock is held by another requestor"
**Root Cause**: Another session already holds a lock on this object.
**Fix**:
1. Check SysAdmin > Lock Management for stale locks
2. Increase lock timeout in prconfig.xml
3. Use Obj-Open with TryLock=True to handle gracefully

## Queue Processor Context
In Queue Processors, ALWAYS use Lock=True when opening objects you intend to modify. QP items may process in parallel, and without locking, you will get intermittent Obj-Save failures.

## Best Practices
- Only lock when you intend to modify and save
- Use ReleaseOnCommit=True to avoid lock leaks
- In flows, the system manages locking automatically
- In activities called from QPs or agents, manage locking explicitly
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/pxref/objdelete-method.html",
        "title": "Obj-Delete Method Reference",
        "content": """# Obj-Delete Method Reference

## Overview
Obj-Delete removes a row from the PegaRULES database corresponding to a clipboard page.

## Key Parameters
- **PageName**: The clipboard page whose database row should be deleted
- **Immediate**: If true, executes immediately without waiting for Commit

## Common Errors

### "Cannot delete: lock not held"
**Root Cause**: Attempting to delete a lockable object without first acquiring a lock.
**Fix**: Use Obj-Open with Lock=True before calling Obj-Delete.

### "Referential integrity violation"
**Root Cause**: Other records in the database reference the object being deleted (foreign key constraint).
**Fix**:
1. Delete dependent records first
2. Check for references in assignment, history, and attachment tables
3. Consider using a status-based soft delete instead

## Best Practices
- Always lock before deleting lockable objects
- Delete child/embedded objects before parent objects
- Use Obj-Delete-By-Handle for batch deletions
- Wrap in try-catch for production robustness
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/pxref/objlist-method.html",
        "title": "Obj-List Method Reference",
        "content": """# Obj-List Method Reference

## Overview
Obj-List retrieves multiple rows from the database into a clipboard page list. It generates a SQL SELECT statement based on the parameters provided.

## Key Parameters
- **PageName**: The clipboard page to hold the results
- **ObjClass**: The class to query
- **PageListProperty**: The property that holds the list of results
- **Select**: Columns to select (default: all mapped columns)
- **Where**: SQL WHERE clause filter
- **OrderBy**: ORDER BY clause

## Common Errors

### "SQL syntax error in Obj-List"
**Root Cause**: Invalid WHERE clause or unmapped property used in filter.
**Fix**:
1. Check that all properties in WHERE clause are mapped to database columns
2. Use the Column Populator to add missing column mappings
3. Verify SQL syntax — Pega generates the SQL from your parameters

### "Result set too large / Out of memory"
**Root Cause**: Obj-List returned too many rows, exhausting clipboard memory.
**Fix**:
1. Add a MaxRecords parameter to limit results
2. Use more specific WHERE clause filters
3. Consider using Report Definition instead for large datasets
4. Use Obj-Browse for read-only scenarios (more memory efficient)

### Performance Issues
- Use Obj-Browse instead of Obj-List when you don't need full page objects
- Add database indexes for frequently filtered columns
- Avoid SELECT * — specify only needed columns
- Use parameterized queries to leverage SQL plan caching
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # TRACER & DEBUGGING
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/tracer/tracer-overview.html",
        "title": "Pega Tracer — Overview and Usage Guide",
        "content": """# Pega Tracer — Complete Debugging Guide

## Overview
Tracer is the primary debugging tool in Pega. It captures real-time execution details of activities, flows, data transforms, declare expressions, and other rule executions for a specific requestor session.

## Launching Tracer
1. Open Designer Studio > System > Debugging > Tracer
2. Or use the keyboard shortcut: Ctrl+Shift+T in Dev Studio
3. Select the requestor to trace (your session or another user's)

## Tracer Event Types
- **Activity Steps**: Shows each step execution with status and elapsed time
- **Flow Processing**: Connector and shape evaluations in flows
- **Data Transforms**: Property set/remove operations
- **When Rules**: Condition evaluation results (true/false)
- **Declare Expressions**: Forward and backward chaining evaluations
- **SQL**: Generated SQL queries with bind variables
- **Exceptions**: Java exceptions and Pega error messages
- **PegaRULES Log**: Log messages from the PRLogging framework

## Key Tracer Settings
- **Break on**: Pause execution at specific events (useful for step debugging)
- **Watch**: Monitor specific properties and their values in real time
- **Event Types**: Filter which events appear (reduce noise)
- **Remote Tracer**: Trace another user's session (requires SysAdmin access)

## Common Debugging Patterns

### Finding Root Cause of Activity Failures
1. Enable Activity Steps + Exceptions event types
2. Reproduce the error
3. Look for the LAST successful step before the exception
4. Check property values at that step using Watch

### Debugging Data Transform Issues
1. Enable Data Transform + Property Set events
2. Run the flow or activity that triggers the DT
3. Check each property value after it's set
4. Look for empty sources or incorrect .pyNote references

### Debugging SQL/Database Issues
1. Enable SQL event type
2. Reproduce the database operation
3. Copy the generated SQL and run it directly in the database
4. Check bind variable values for correctness

### Performance Debugging
1. Enable all event types with elapsed time display
2. Run the slow process
3. Sort by elapsed time to find the bottleneck
4. Common culprits: large Obj-List, unoptimized Declare Expressions, unnecessary database calls

## Tracer Tips
- Use Ctrl+F in Tracer to search through captured events
- Export Tracer XML for sharing with support teams
- Use Remote Tracer to debug issues that only happen for specific users
- Clear Tracer output frequently to keep it manageable
- Set Max Events to prevent memory issues in long traces
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # QUEUE PROCESSORS
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/queueprocessor/queue-processor-landing-page.html",
        "title": "Queue Processor — Complete Guide and Troubleshooting",
        "content": """# Queue Processor — Complete Guide

## Overview
Queue Processors (QPs) process items from a queue table asynchronously. They are used for high-volume batch processing, background tasks, and decoupling real-time user actions from heavy backend processing.

## How Queue Processors Work
1. Items are enqueued to a queue table (pxQueueClass or custom)
2. QP nodes pick up items based on thread count and node configuration
3. Each item runs the configured activity in its own thread
4. Items are marked as completed, failed, or retried

## Key Configuration
- **Queue Class**: The rule that defines the queue table and processing activity
- **Thread Count**: Number of concurrent processing threads per node
- **Retry Count**: How many times to retry failed items
- **Activity**: The activity executed for each queue item
- **Node Selection**: Which nodes process this queue

## Common Errors

### "You cannot save a page that your session does not hold a lock on" (~1% of items)
**Root Cause**: Intermittent locking issue. Multiple QP threads may process items that touch the same work object. Without explicit locking, save operations fail.
**Fix**:
1. In your QP activity's Obj-Open step, set Lock=True
2. Set ReleaseOnCommit=True
3. Ensure no downstream step re-opens the same object without locking
4. Add retry logic for transient locking conflicts

### "Queue item stuck in PROCESSING status"
**Root Cause**: The QP thread crashed or the node went down during processing. The item's status was never updated.
**Fix**:
1. Check the queue table directly: SELECT * FROM {queue_table} WHERE pxQueueStatus='PROCESSING'
2. Manually reset stuck items: UPDATE {queue_table} SET pxQueueStatus='NEW' WHERE pxQueueStatus='PROCESSING' AND pxUpdateDateTime < (NOW() - INTERVAL 1 HOUR)
3. Investigate why the thread crashed (check PegaRULES log)

### "Queue Processor not picking up items"
**Root Cause**: Multiple possible causes.
**Diagnosis**:
1. Check if the QP is enabled: SysAdmin > Queue Processors
2. Verify the node is configured to run this QP
3. Check if all threads are busy: Monitor > Queue Processor Status
4. Look for errors in PegaRULES log for the QP ruleset
5. Verify items have status 'NEW' in the queue table

### "OutOfMemoryError during QP processing"
**Root Cause**: QP activity creates too many clipboard pages without cleanup.
**Fix**:
1. Use Page-Remove to clean up temporary pages after processing
2. Reduce thread count to lower concurrent memory usage
3. Use Obj-Browse instead of Obj-List for read-only queries
4. Ensure embedded pages are not growing unbounded

## Performance Tuning
- Set thread count based on CPU cores (start with cores/2)
- Use batch size to process multiple items per activity invocation
- Index the queue table on pxQueueStatus for fast polling
- Monitor queue depth and processing rate in the Pega monitoring dashboard
- Use dedicated nodes for heavy QP processing

## Best Practices
- Always use explicit locking in QP activities
- Implement idempotent processing (same item processed twice = same result)
- Use try-catch around critical operations
- Log enough context to diagnose failures without Tracer
- Set appropriate retry counts (3 for transient, 0 for permanent errors)
- Use Page-Remove in finally blocks to prevent memory leaks
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # LOCKING & TRANSACTIONS
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/datamanagement/locking-overview.html",
        "title": "Pega Locking Mechanisms — Optimistic and Pessimistic",
        "content": """# Pega Locking Mechanisms

## Overview
Pega supports two types of database-level locking to prevent concurrent modification conflicts: optimistic locking and pessimistic locking.

## Pessimistic Locking
Acquires an exclusive lock when an object is opened. No other session can modify the object until the lock is released.

### How It Works
1. Obj-Open with Lock=True acquires the lock (row in pc_locks table)
2. Other sessions attempting to lock the same object will wait or fail
3. Lock is released by Commit (if ReleaseOnCommit=True) or explicit unlock

### When to Use
- Queue Processor activities modifying shared objects
- Agent activities with concurrent execution risk
- High-contention scenarios where conflicts are frequent (>5%)

### Common Issues
- **Lock not released**: Forgetting ReleaseOnCommit=True causes locks to persist until session ends
- **Deadlocks**: Two sessions each holding a lock the other needs
- **Stale locks**: Locks from crashed sessions remain in pc_locks table

### Diagnosing Lock Issues
1. Query pc_locks table: SELECT * FROM pc_locks WHERE ...
2. Use SysAdmin > Lock Management tool
3. Check PegaRULES log for "lock" related warnings

## Optimistic Locking
Does not acquire a lock on open. Instead, checks at save time whether the object was modified by another session.

### How It Works
1. Obj-Open (no lock) reads the object and notes the pzUpdateDateTime
2. On Obj-Save, Pega checks if pzUpdateDateTime changed
3. If changed → conflict error; if unchanged → save succeeds

### When to Use
- Low-contention scenarios (<5% conflict rate)
- Interactive user forms (lock would block other users)
- Read-heavy, write-rare data

### Common Issues
- **"Object has been modified by another session"**: Expected in concurrent scenarios. Handle with refresh+retry.
- **Lost updates**: Two users edit the same object; last save wins without optimistic locking enabled.

## Locking in Different Contexts

| Context | Recommended Locking | Notes |
|---------|-------------------|-------|
| Flow (interactive) | Automatic (system-managed) | Pega handles locking in flows |
| Activity (standalone) | Pessimistic (Lock=True) | Must manage explicitly |
| Queue Processor | Pessimistic (Lock=True) | Always lock in QP |
| Agent | Pessimistic (Lock=True) | Always lock in agents |
| Report/Dashboard | None needed | Read-only operations |
| Data Transform | Depends on caller | Inherits from calling context |

## Best Practices
- In QP/Agent activities: ALWAYS use Lock=True + ReleaseOnCommit=True
- Minimize lock duration: open+lock → modify → save → commit in quick succession
- Use consistent lock ordering to prevent deadlocks
- Monitor pc_locks table for stale locks in production
- Set lock timeout in prconfig.xml for your expected processing duration
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # COMMIT AND ROLLBACK
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/datamanagement/commit-and-rollback.html",
        "title": "Commit and Rollback — Transaction Management",
        "content": """# Commit and Rollback in Pega

## Overview
Commit finalizes all pending database operations (saves, deletes) as a single transaction. Rollback undoes all pending operations since the last Commit.

## Commit Behavior
- Groups all Obj-Save and Obj-Delete operations since the last Commit
- Executes as a single database transaction (all-or-nothing)
- Releases locks acquired with ReleaseOnCommit=True
- Triggers any post-commit processing (e.g., queue items)

## Rollback Behavior
- Undoes all database operations since the last Commit
- Clipboard pages remain modified (only database is rolled back)
- Does NOT release locks (locks persist until Commit or session end)

## Common Errors

### "Commit failed: database connection lost"
**Root Cause**: Database connection dropped during commit.
**Fix**:
1. Check database server health and connection pool settings
2. Reduce transaction size (fewer Obj-Save calls per Commit)
3. Implement retry logic for transient connection issues

### "Commit failed: constraint violation"
**Root Cause**: Data being saved violates a database constraint (unique key, not null, foreign key).
**Fix**:
1. Check the error details for which constraint failed
2. Validate data before Obj-Save
3. Use Obj-Validate to check data integrity before saving
4. Check for duplicate key generation issues

### "Partial commit — some operations succeeded, others failed"
**Root Cause**: This should NOT happen if using Commit correctly. If it does, check for nested Commits or auto-commit settings.
**Fix**:
1. Ensure only one Commit call per logical transaction
2. Check prconfig.xml for auto-commit settings
3. Review activity flow for unexpected Commit calls

## Best Practices
- One Commit per logical unit of work
- Use Rollback in error handling to clean up partial operations
- Always pair Lock+ReleaseOnCommit with a Commit call
- Keep transactions small to reduce lock duration
- In QP activities: Commit after each item, not after the entire batch
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # CONNECTORS — REST & SOAP
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/connectors/rest-connector.html",
        "title": "REST Connector — Configuration and Troubleshooting",
        "content": """# REST Connector — Troubleshooting Guide

## Overview
Connect-REST sends HTTP requests to external REST APIs. It maps clipboard data to request body/headers and maps the response back to clipboard pages.

## Common Errors

### HTTP 401 — Unauthorized
**Root Cause**: Authentication credentials are missing, expired, or invalid.
**Fix**:
1. Check Authentication Profile configuration
2. Verify OAuth2 token is not expired — check token refresh logic
3. Ensure credentials are correct in the authentication data instance
4. For Basic Auth: verify username/password are correctly base64 encoded
5. Check if the API key or token needs rotation

### HTTP 403 — Forbidden
**Root Cause**: Authenticated but not authorized for the requested resource.
**Fix**:
1. Verify the service account has required permissions
2. Check if IP whitelisting is required by the external service
3. Review API scopes in OAuth2 configuration

### HTTP 500 — Internal Server Error (from external system)
**Root Cause**: The external system encountered an error processing the request.
**Fix**:
1. Check the request payload for invalid data
2. Review the external system's logs
3. Verify the endpoint URL is correct (not hitting wrong environment)
4. Test the same request using Postman/curl

### "Connect-REST timeout"
**Root Cause**: External service did not respond within the configured timeout.
**Fix**:
1. Increase timeout in the connector rule (default may be too low)
2. Check network connectivity to the external service
3. Verify firewall rules allow outbound connections
4. Check if the external service is under load

### "SSL/TLS handshake failed"
**Root Cause**: Certificate trust issue between Pega and the external service.
**Fix**:
1. Import the external service's SSL certificate into Pega's keystore
2. Check certificate chain — intermediate certs may be missing
3. Verify TLS version compatibility (some services require TLS 1.2+)
4. Check prconfig.xml for SSL/TLS configuration

### Response Mapping Errors
**Root Cause**: Response JSON/XML structure doesn't match the expected data mapping.
**Fix**:
1. Enable Tracer with SQL events to see the raw response
2. Test with a REST client to see actual response format
3. Update the response data transform to match actual structure
4. Check for null/empty fields that your mapping doesn't handle

## Debugging REST Connectors
1. Enable Tracer > Service (REST) events
2. Use the Connector simulator (right-click connector rule > Run)
3. Check the clipboard after execution for pyStatusValue and pyStatusMessage
4. Review PegaRULES log for detailed HTTP exchange info
5. Set log level to DEBUG for com.pega.pegarules.integration
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/connectors/soap-connector.html",
        "title": "SOAP Connector — Troubleshooting Guide",
        "content": """# SOAP Connector — Troubleshooting Guide

## Common Errors

### "SOAP Fault: Invalid XML"
**Root Cause**: Request XML is malformed or doesn't match the WSDL schema.
**Fix**:
1. Validate request XML against the WSDL using an XML validator
2. Check data transforms that build the SOAP request
3. Look for special characters that need XML encoding
4. Ensure namespaces match what the service expects

### "WSDL import failed"
**Root Cause**: Cannot fetch or parse the WSDL document.
**Fix**:
1. Verify WSDL URL is accessible from the Pega server
2. Check for authentication requirements on the WSDL endpoint
3. Download WSDL manually and import as a file
4. Check for circular imports in the WSDL

### "Connection refused"
**Root Cause**: Network connectivity issue to the SOAP service.
**Fix**:
1. Verify endpoint URL and port
2. Check firewall rules between Pega server and service
3. Ensure DNS resolution works for the service hostname
4. Check if the service requires VPN access

## Debugging Tips
- Enable Tracer > Service events to see full SOAP request/response XML
- Use SoapUI to test the same request outside of Pega
- Check the XML tab in the connector simulator for the generated envelope
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # DECLARE EXPRESSIONS
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/declaratives/declare-expression-overview.html",
        "title": "Declare Expressions — Troubleshooting Guide",
        "content": """# Declare Expressions — Troubleshooting Guide

## Overview
Declare Expressions automatically compute property values using forward chaining or backward chaining. They fire when input properties change (forward) or when the target property is referenced (backward).

## Common Errors

### "Circular reference detected in Declare Expression"
**Root Cause**: Two or more Declare Expressions reference each other's target properties, creating an infinite loop.
**Fix**:
1. Map out all Declare Expressions and their inputs/outputs
2. Identify the circular dependency chain
3. Break the cycle by converting one expression to an activity-based calculation
4. Use the Declare Expression dependency viewer in Dev Studio

### "Declare Expression not firing"
**Root Cause**: Multiple possible causes.
**Diagnosis**:
1. Check if the expression is in the correct ruleset and version
2. Verify the input property names match exactly (case-sensitive)
3. Check if the expression's class matches where the property is used
4. Enable Tracer > Declare Expression events to see if it triggers
5. Check for circumstance-qualified expressions that might take priority

### "Performance degradation from Declare Expressions"
**Root Cause**: Too many or poorly designed Declare Expressions causing excessive recalculations.
**Fix**:
1. Check for cascading expressions (A triggers B triggers C...)
2. Minimize the number of input properties per expression
3. Use backward chaining for properties that are rarely accessed
4. Profile with Tracer to identify the expensive expressions
5. Consider converting hot-path expressions to explicit calculations

### "Declare Expression returns wrong value"
**Root Cause**: Expression logic error or unexpected input state.
**Fix**:
1. Enable Tracer to see input values when the expression fires
2. Test the expression logic manually with the same inputs
3. Check for page context issues (expression running on wrong page)
4. Verify property types match (String vs Integer vs Date)

## Best Practices
- Use forward chaining for properties that change rarely but are read often
- Use backward chaining for properties that change often but are read rarely
- Keep expression logic simple — complex calculations belong in activities
- Document dependencies between expressions
- Avoid Declare Expressions on high-volume page lists
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # SECURITY & AUTHENTICATION
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/security/authentication-overview.html",
        "title": "Pega Authentication & SSO Troubleshooting",
        "content": """# Pega Authentication & SSO Troubleshooting

## Common Authentication Errors

### "Invalid credentials" / Login failure
**Root Cause**: Username or password mismatch.
**Fix**:
1. Verify the operator ID exists and is not disabled
2. Check password policy — the password may have expired
3. Verify the authentication service configuration
4. Check for LDAP connectivity if using directory authentication
5. Review the PegaRULES log for detailed auth failure reasons

### "SSO authentication failed"
**Root Cause**: SAML/OIDC token validation failed.
**Fix**:
1. Check SAML assertion — verify issuer, audience, and timestamps
2. Ensure clock synchronization between Pega server and IdP (< 5 min skew)
3. Verify the IdP certificate is imported into Pega's keystore
4. Check the Assertion Consumer Service URL matches IdP configuration
5. Review SAML response in browser dev tools (Network tab)

### "OAuth2 token expired / refresh failed"
**Root Cause**: Access token expired and refresh token is invalid or expired.
**Fix**:
1. Check token expiry duration in the OAuth2 provider configuration
2. Verify the refresh token grant is enabled
3. Ensure the token endpoint URL is correct and accessible
4. Check client ID and client secret are valid
5. Review OAuth2 error response for specific error codes

### "LDAP connection failed"
**Root Cause**: Cannot connect to the LDAP/Active Directory server.
**Fix**:
1. Verify LDAP server hostname and port (389 for LDAP, 636 for LDAPS)
2. Check firewall rules between Pega server and LDAP server
3. Verify bind DN and password for the service account
4. Test LDAP connection using ldapsearch command
5. Check SSL certificate if using LDAPS

### "Access denied" after successful login
**Root Cause**: User authenticated but lacks required access roles.
**Fix**:
1. Check the operator's access group assignment
2. Verify the access group has the required roles
3. Check for privilege-based restrictions on the attempted action
4. Review access-when rules that may be blocking

## Debugging Authentication Issues
1. Set log level to DEBUG for com.pega.pegarules.session.security
2. Check PegaRULES log for the full authentication flow
3. Use browser developer tools to inspect SAML/OIDC redirects
4. Test with a known-working account to isolate the issue
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # AGENTS & JOB SCHEDULER
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/agents/agent-schedule-landing.html",
        "title": "Pega Agents — Configuration and Troubleshooting",
        "content": """# Pega Agents — Troubleshooting Guide

## Overview
Agents are scheduled background processes that run activities at configured intervals. They run on specific nodes and can be enabled/disabled per node.

## Common Issues

### "Agent not running / not picking up work"
**Diagnosis**:
1. Check Agent Management: SysAdmin > Agents & Daemon Management
2. Verify the agent is enabled and running on the correct node
3. Check the agent schedule — it may be configured for specific hours only
4. Review PegaRULES log for agent errors
5. Check if the agent's ruleset version is available on the node

### "Agent running but processing slowly"
**Fix**:
1. Check the agent activity for performance bottlenecks (use Tracer)
2. Verify database query performance in the agent's activity
3. Check for lock contention with other agents or QPs
4. Reduce the scope of work per agent cycle
5. Consider migrating heavy processing to Queue Processors

### "Agent causing high CPU / memory usage"
**Fix**:
1. Profile the agent activity with Tracer
2. Check for unbounded clipboard page growth
3. Add Page-Remove calls to clean up temporary pages
4. Reduce agent frequency if running too often
5. Check for infinite loops in the agent activity

### "Duplicate processing — agent processes same items twice"
**Root Cause**: Agent cycle overlaps — previous cycle hasn't finished when the next one starts.
**Fix**:
1. Increase the agent interval to exceed processing time
2. Add a flag/status check to skip already-processed items
3. Use pessimistic locking to prevent concurrent processing
4. Consider switching to Queue Processor for better concurrency control

## Agent vs Queue Processor — When to Use Which

| Scenario | Use Agent | Use Queue Processor |
|----------|-----------|-------------------|
| Scheduled batch job (nightly) | Yes | No |
| Process items as they arrive | No | Yes |
| High volume (>1000 items/min) | No | Yes |
| Simple periodic check | Yes | No |
| Needs parallel processing | No | Yes |
| Needs retry logic | Maybe | Yes (built-in) |

## Best Practices
- Set agent interval based on expected processing time + buffer
- Implement idempotent processing logic
- Use locking for shared resources
- Log enough context for debugging without Tracer
- Monitor agent health via SysAdmin dashboards
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # GUARDRAILS
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/guardrails/guardrails-landing-page.html",
        "title": "Pega Guardrails — Best Practices and Compliance",
        "content": """# Pega Guardrails — Best Practices

## Overview
Guardrails are Pega's built-in best practices that help maintain application quality, performance, and maintainability. Guardrails compliance is measured as a score (0-100) in the Application Guardrails landing page.

## Critical Guardrails Violations

### "Avoid Java in activities"
**Why**: Java steps bypass Pega's declarative processing and make upgrades harder.
**Fix**: Replace Java steps with built-in method steps, data transforms, or library functions.

### "Avoid large clipboard pages"
**Why**: Large pages consume memory and slow processing.
**Fix**: Limit page list sizes, use pagination, clean up temporary pages with Page-Remove.

### "Use data transforms instead of activities for data manipulation"
**Why**: Data transforms are declarative, traceable, and easier to maintain.
**Fix**: Convert activity-based property setting to data transforms.

### "Avoid deeply nested page structures"
**Why**: Deep nesting increases memory usage and makes debugging difficult.
**Fix**: Flatten data structures where possible, use references instead of embedded pages.

### "Use Report Definition instead of Obj-List for reporting"
**Why**: Report Definitions are optimized, cached, and support the Pega reporting framework.
**Fix**: Replace Obj-List calls used for reporting with Report Definition rules.

## Checking Guardrails Compliance
1. Open Application > Quality > Guardrails
2. Review the overall score and individual violations
3. Click each violation to see the affected rules
4. Prioritize Critical and High severity violations
5. Run the Guardrails report periodically during development

## Impact of Low Guardrails Score
- Poor application performance
- Difficult upgrades to newer Pega versions
- Harder maintenance and debugging
- Higher risk of production issues
- Pega support may require guardrails compliance for SRs
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # PERFORMANCE & CACHING
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/performance/pega-performance-overview.html",
        "title": "Pega Performance Tuning Guide",
        "content": """# Pega Performance Tuning Guide

## Common Performance Issues

### Slow Case Processing
**Diagnosis**:
1. Enable Tracer and reproduce the slow operation
2. Sort events by elapsed time to find bottlenecks
3. Common culprits:
   - Large Obj-List queries without proper filters
   - Excessive Declare Expression cascading
   - Unoptimized data transforms on large page lists
   - External connector timeouts

**Fix by category**:
- **Database**: Add indexes, optimize WHERE clauses, use Report Definition
- **Clipboard**: Reduce page sizes, use pagination, clean up with Page-Remove
- **Rules**: Simplify Declare Expressions, cache When rules, reduce activity steps
- **Connectors**: Add timeouts, implement caching, use async processing

### High Database CPU
**Fix**:
1. Identify slow queries via database monitoring tools
2. Add missing indexes (use Pega's Index Suggestions)
3. Optimize Obj-List WHERE clauses
4. Use Obj-Browse for read-only queries
5. Review Declare Index rules for unnecessary indexes

### High Memory Usage (JVM Heap)
**Fix**:
1. Check for large clipboard pages (SysAdmin > Clipboard Viewer)
2. Look for memory leaks in custom Java code
3. Reduce QP/Agent thread counts
4. Increase JVM heap size if hardware allows
5. Enable garbage collection logging for analysis

### Slow UI Rendering
**Fix**:
1. Reduce the number of sections per screen
2. Use lazy loading for tabs and hidden sections
3. Optimize client-side scripts
4. Reduce the number of repeat grids on a single screen
5. Use server-side pagination for lists

## Performance Monitoring Tools
- **PAL (Performance Analyzer)**: Real-time performance metrics
- **SMA (System Management Application)**: System-level monitoring
- **Tracer**: Detailed execution tracing
- **Database Query Inspector**: SQL analysis
- **Clipboard Viewer**: Memory usage per requestor

## Caching
Pega caches rules, data pages, and lookup tables to reduce database queries.

### Data Page Caching Issues
- **Stale data**: Data page not refreshing when source data changes
  - Fix: Set appropriate cache expiration or use scope-based invalidation
- **Memory bloat from cached pages**: Too many data pages cached globally
  - Fix: Use requestor-scoped pages where possible, set MaxAge
- **Cache miss storms**: All nodes re-fetch simultaneously after cache expires
  - Fix: Stagger cache expiration times across nodes

### Rule Cache Issues
- **Rule changes not taking effect**: The rule cache may be stale
  - Fix: Clear rules cache via SysAdmin > Caching > Clear Caches
- **High cache miss rate**: Rules not being cached effectively
  - Fix: Review ruleset configuration, check for unnecessary circumstancing
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # DATABASE MAPPING & CLASS TABLE MAPPING
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/datamanagement/database-mapping-overview.html",
        "title": "Database Mapping & Class-Table Errors",
        "content": """# Database Mapping Troubleshooting

## Common Errors

### "Property not mapped to a column"
**Root Cause**: A property used in Obj-List WHERE/ORDER BY is not mapped to a database column.
**Fix**:
1. Open the class > Database tab
2. Click "Map columns" or use the Column Populator tool
3. Run Column Populator: Records > SysAdmin > Column Populator
4. Add the property to the database table using ALTER TABLE if needed

### "Class not mapped to any table"
**Root Cause**: The class doesn't have a Database Table mapping.
**Fix**:
1. Create a Database Table record for the class
2. Or ensure the class inherits from a mapped parent class
3. Check the class hierarchy: class > Pattern Inheritance

### "Column type mismatch"
**Root Cause**: The Pega property type doesn't match the database column type.
**Fix**:
1. Check the property type (String, Integer, DateTime, etc.)
2. Compare with the database column type
3. Alter the column type if possible, or change the property type
4. For date/time mismatches, check the database-specific format

### "Duplicate key violation on save"
**Root Cause**: Attempting to insert a record with a primary key that already exists.
**Fix**:
1. Check the key generation strategy (auto-generated vs manual)
2. Look for race conditions in concurrent key generation
3. Use Obj-Open to check existence before Obj-Save (INSERT)
4. Consider using Obj-Save-Cancel and retry with new key

## Column Populator
The Column Populator automatically maps Pega properties to database columns.
1. Navigate to Records > SysAdmin > Column Populator
2. Select the target class
3. Run the populator — it adds columns for unmapped properties
4. Verify the new columns in the database table

## Best Practices
- Run Column Populator after adding new properties to mapped classes
- Test database operations in dev before promoting to higher environments
- Keep class-table mappings documented
- Use Pega's automatic schema management when possible
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # SLA & URGENCY
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/sla/service-level-agreement-overview.html",
        "title": "SLA & Urgency — Troubleshooting",
        "content": """# SLA & Urgency Troubleshooting

## Common Issues

### "SLA not firing / deadlines not triggered"
**Root Cause**: SLA agent may not be running, or SLA configuration is incorrect.
**Diagnosis**:
1. Check if the SLAEvaluate agent is running: SysAdmin > Agents
2. Verify the SLA rule is attached to the correct assignment/flow
3. Check if the case has the correct status for SLA evaluation
4. Look at the case's pxUrgencyWork and SLA-related properties

### "Urgency not increasing as expected"
**Root Cause**: SLA urgency calculation may be misconfigured.
**Fix**:
1. Review the SLA rule's urgency increment settings
2. Check the goal, deadline, and passed-deadline intervals
3. Verify the SLA evaluation frequency in the agent schedule
4. Test with a short SLA interval to verify the mechanism works

### "SLA triggered on wrong assignment"
**Root Cause**: SLA scope is broader than intended.
**Fix**:
1. Check which flow shape the SLA is attached to
2. Verify the SLA applies to the correct step/assignment
3. Review circumstanced SLA rules that may override the default

## Best Practices
- Test SLA behavior with compressed timeframes during development
- Monitor the SLAEvaluate agent's health
- Use urgency-based routing to prioritize SLA-critical cases
- Document SLA rules and their business requirements
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # EXCEPTION HANDLING & FLOW ERRORS
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/flowprocessing/exception-handling-overview.html",
        "title": "Exception Handling in Pega — Flow and Activity Errors",
        "content": """# Exception Handling in Pega

## Flow-Level Exception Handling
Flows support exception handling through:
- **Ticket/Flag**: Raise a ticket to jump to a specific flow shape
- **Flow Exception Handler**: Configured at the case type level
- **Spin-off flows**: Run exception logic in parallel

## Activity-Level Exception Handling
Activities support try-catch-finally blocks:
- **Try**: Wrap steps that may fail
- **Catch**: Handle specific exception types
- **Finally**: Clean up resources (release locks, remove pages)

## Common Patterns

### Handling Database Exceptions in Activities
```
Step 1: Obj-Open (Lock=True)          [try]
Step 2: Property-Set                   [try]
Step 3: Obj-Save                       [try]
Step 4: Commit                         [try]
Step 5: Log error, set status flag     [catch]
Step 6: Page-Remove, Rollback          [finally]
```

### Handling Connector Failures
```
Step 1: Connect-REST                   [try]
Step 2: Check pyStatusValue            [try]
Step 3: If error, retry with backoff   [catch]
Step 4: If max retries, escalate       [catch]
```

### Handling Flow Action Validation Errors
- Use Validate rules to check data before submission
- Display pyMessageLabel to the user with actionable error messages
- Use client-side validation for immediate feedback

## Common Errors

### "Unhandled exception in flow"
**Root Cause**: An activity or connector threw an exception with no try-catch.
**Fix**:
1. Add try-catch blocks around all database and connector operations
2. Configure a flow-level exception handler as a safety net
3. Log the exception details for debugging

### "Flow stuck at assignment — no connector evaluates to true"
**Root Cause**: All connectors from a decision shape or router evaluate to false.
**Fix**:
1. Add an "Otherwise" connector as a fallback
2. Review connector conditions with Tracer
3. Check for null/empty values in the condition properties

### "Duplicate assignment created"
**Root Cause**: Flow processing error caused a retry that re-created the assignment.
**Fix**:
1. Check for flow action resubmission (double-click prevention)
2. Implement idempotency checks in flow actions
3. Review the flow for unintended loops

## Best Practices
- Always add try-catch in activities that call connectors or database operations
- Use finally blocks to clean up locks and temporary pages
- Log enough context in catch blocks for troubleshooting
- Configure flow-level exception handlers for all production case types
- Use pyMessageLabel for user-friendly error messages
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # REPORT DEFINITIONS
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/reporting/troubleshooting-reports.html",
        "title": "Report Definition — Troubleshooting",
        "content": """# Report Definition Troubleshooting

## Common Errors

### "Report returns no results"
**Diagnosis**:
1. Check the report's filter conditions
2. Verify the class and applies-to configuration
3. Run the generated SQL directly in the database
4. Check access controls — user may lack visibility to the data
5. Verify the database table has data for the specified class

### "Report is slow"
**Fix**:
1. Check the generated SQL for missing indexes
2. Reduce the number of columns selected
3. Add appropriate filters to reduce the result set
4. Avoid using LIKE with leading wildcards
5. Use Aggregate functions instead of loading all rows
6. Check for cross-join issues in multi-table reports

### "Property not available in report"
**Root Cause**: Property is not mapped to a database column.
**Fix**:
1. Map the property using Column Populator
2. Check if the property exists in a different class than the report's applies-to
3. For calculated values, use Report Definition expressions instead

### "Access control blocks report results"
**Root Cause**: Row-level security or access when rules filter out data.
**Fix**:
1. Review access-when rules on the report's class
2. Check the user's access group for report-related privileges
3. Test with an admin account to confirm data exists
4. Check for class-level access controls
"""
    },
]


def seed_knowledge_base(output_dir: Path = RAW_DOCS_DIR) -> int:
    """Write all curated docs to the raw_docs directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS:
        doc["content_length"] = len(doc["content"])
        filename = f"curated_{count:03d}.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        logger.info(f"  Saved: {doc['title'][:60]} ({doc['content_length']} chars)")
        count += 1
    logger.info(f"\nSeeded {count} curated documents to {output_dir}")
    return count


if __name__ == "__main__":
    count = seed_knowledge_base()
    print(f"\nDone! {count} curated documents written.")
    print("Now run: python -m indexer.index_docs")
