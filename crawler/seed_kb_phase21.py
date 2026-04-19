"""
Curated Pega Knowledge Base — Phase 21 (PEGA0033–PEGA0099 Alert Codes + Security Alerts)
Complete coverage of all remaining alert codes, security event alerts, and security exceptions.

Run: python -m crawler.seed_kb_phase21
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE21 = [
    {
        "url": "curated://pega-alerts-pega0033-to-pega0045",
        "title": "PEGA0033–PEGA0045 — Advanced Performance and Processing Alert Codes",
        "content": """# PEGA0033–PEGA0045 — Advanced Performance and Processing Alerts

## PEGA0033 — Long-Running Flow Execution
- **What**: A flow (case lifecycle process) execution exceeded the threshold
- **Threshold DSS**: `alerts/flow/threshold` (default: 60000ms / 1 minute)
- **Common cause**: Complex flow with many shapes, multiple connector calls, heavy processing in flow actions
- **Fix**: Break complex flows into sub-flows. Move heavy processing to asynchronous queue processors. Optimize flow action pre/post processing.
- **Debugging**: Tracer → enable Flow tracking → identify the slowest shape

## PEGA0034 — Declare Expression Chain Too Long
- **What**: A chain of Declare Expressions triggered cascading recalculations beyond the allowed depth
- **Threshold DSS**: `alerts/declare/chain/maxdepth` (default: 20 levels)
- **Common cause**: Property A depends on B, B depends on C, C depends on D... creating a long evaluation chain
- **Fix**: Reduce chain depth. Use Data Transforms for initial calculation instead of declaring everything. Break circular or deep dependencies.
- **Debugging**: Tracer → enable Declare tracking → see the chain of evaluations

## PEGA0035 — Excessive Rule Cache Misses
- **What**: Too many rules not found in cache, causing repeated database lookups
- **Threshold DSS**: `alerts/rulecache/miss/threshold` (default: 100 misses per minute)
- **Common cause**: Cache too small, many circumstanced rules, frequent ruleset version changes
- **Fix**: Increase rule cache size in prconfig.xml. Check for unnecessary rule resolution patterns. Verify ruleset versions are stable.
- **Debugging**: SMA → System → Caches → Rule Cache hit/miss ratio

## PEGA0036 — Large Database Transaction
- **What**: A single database transaction involves too many rows or too much data
- **Threshold DSS**: `alerts/transaction/size/threshold` (default: 1000 rows)
- **Common cause**: Bulk case creation, large data import, mass property update
- **Fix**: Break into smaller batches. Use Data Flows for bulk operations. Implement batch commit pattern.

## PEGA0037 — Thread Pool Saturation
- **What**: Application thread pool is near capacity
- **Threshold DSS**: `alerts/threadpool/utilization/threshold` (default: 90%)
- **Common cause**: Too many concurrent requests, long-running synchronous operations, blocking I/O
- **Fix**: Increase thread pool size. Move blocking operations to async. Scale horizontally.
- **Debugging**: SMA → System → Thread Pools → active/max counts. Take thread dump to find blocked threads.

## PEGA0038 — Excessive Clipboard Copies
- **What**: Too many clipboard copy operations in a single interaction (property copying, page copying)
- **Threshold DSS**: `alerts/clipboard/copies/threshold` (default: 500 copy operations)
- **Common cause**: Data Transform copying large page structures repeatedly, loop doing page-level copy
- **Fix**: Copy only needed properties, not entire pages. Use references instead of copies where possible.

## PEGA0039 — Long-Running Commit with Many Objects
- **What**: A commit operation is writing too many work objects or data objects simultaneously
- **Threshold DSS**: `alerts/commit/objects/threshold` (default: 50 objects)
- **Common cause**: Bulk case processing committing all at once, case with many sub-cases saving together
- **Fix**: Use deferred save. Batch commits. Commit sub-cases independently.

## PEGA0040 — Excessive Database Connections Per Requestor
- **What**: A single requestor is holding too many database connections
- **Threshold DSS**: `alerts/requestor/connections/threshold` (default: 5)
- **Common cause**: Multiple simultaneous queries, nested database operations, connection leak in custom Java
- **Fix**: Close connections after use. Reduce concurrent DB operations. Check for connection leaks.

## PEGA0041 — Data Page Load Cascade
- **What**: Loading one data page triggers loading of multiple other data pages in a chain
- **Threshold DSS**: `alerts/datapage/cascade/threshold` (default: 10 loads in one interaction)
- **Common cause**: Data pages referencing other data pages in their sources, deeply nested data model
- **Fix**: Pre-load critical data pages. Flatten data model. Use eager loading for known dependencies.

## PEGA0042 — Long-Running Report Definition
- **What**: A Report Definition execution exceeded the threshold
- **Threshold DSS**: `alerts/report/threshold` (default: 15000ms)
- **Common cause**: Complex joins, large date ranges, missing indexes on filter columns
- **Fix**: Add indexes. Narrow date ranges. Optimize joins. Use summary reports instead of detailed.
- **Debugging**: Extract the SQL from Tracer and run EXPLAIN/EXPLAIN PLAN in the database.

## PEGA0043 — Excessive Page List Growth
- **What**: A page list grew beyond the expected size during processing
- **Threshold DSS**: `alerts/pagelist/growth/threshold` (default: 5000 items)
- **Common cause**: Loading unbounded query results into a page list, accumulating items without cleanup
- **Fix**: Paginate query results. Set MAX in obj-Browse. Clean up page lists after processing.

## PEGA0044 — Long-Running Parse Rule
- **What**: Parsing an XML or JSON response took too long
- **Threshold DSS**: `alerts/parse/threshold` (default: 5000ms)
- **Common cause**: Very large XML/JSON payload (multi-MB), complex parse rule with many mappings
- **Fix**: Request smaller payloads. Stream parsing for large documents. Simplify parse mappings.

## PEGA0045 — Agent Queue Backlog
- **What**: Agent queue has accumulated too many pending items waiting to be processed
- **Threshold DSS**: `alerts/agent/backlog/threshold` (default: 500 items)
- **Common cause**: Agent processing too slow, agent disabled, burst of incoming items
- **Fix**: Scale agent processing (more threads). Optimize agent activity. Clear stuck items. Enable agents on more nodes.
- **Debugging**: SMA → Agents → check agent status, last run time, queue depth
"""
    },
    {
        "url": "curated://pega-alerts-pega0046-to-pega0060",
        "title": "PEGA0046–PEGA0060 — Integration, Data, and Infrastructure Alert Codes",
        "content": """# PEGA0046–PEGA0060 — Integration, Data, and Infrastructure Alerts

## PEGA0046 — Connector Retry Exhausted
- **What**: A connector call failed and all retry attempts have been exhausted
- **Severity**: ERROR
- **Common cause**: External system persistently unavailable, authentication permanently failed
- **Fix**: Check external system status. Verify credentials haven't expired. Implement dead letter queue for failed messages.

## PEGA0047 — External Service Response Error
- **What**: External service returned an error response (4xx or 5xx HTTP status)
- **Context**: HTTP status code, error message from service, connector name
- **Common causes by status code**:
  - 400 Bad Request: Invalid request format, missing required fields
  - 401 Unauthorized: Authentication token expired, invalid credentials
  - 403 Forbidden: Insufficient permissions, IP not whitelisted
  - 404 Not Found: Endpoint URL wrong, resource doesn't exist
  - 500 Internal Server Error: External system crash
  - 502 Bad Gateway: Load balancer can't reach the backend
  - 503 Service Unavailable: External system overloaded or in maintenance
  - 504 Gateway Timeout: External system too slow to respond
- **Fix**: Map each status code to appropriate handling in the connector error mapping

## PEGA0048 — External Service Unavailable
- **What**: Cannot reach the external service at all (connection refused or DNS failure)
- **Severity**: ERROR
- **Common cause**: Service down, firewall blocking, DNS misconfigured, wrong hostname/port
- **Fix**: Verify service URL. Check network connectivity from Pega server. Check firewall rules. Implement circuit breaker.

## PEGA0049 — SSL/TLS Handshake Failure
- **What**: SSL/TLS connection to an external service failed
- **Common cause**: Certificate expired, untrusted CA, hostname mismatch, protocol version mismatch (TLS 1.0 disabled)
- **Fix**: Import the external service's certificate into Pega's truststore. Check certificate expiry. Ensure TLS 1.2+ is supported on both sides.
- **Debugging**: Enable SSL debug logging: `-Djavax.net.debug=ssl,handshake` in JVM args

## PEGA0050 — Database Connection Pool Exhausted
- **What**: All database connections in the pool are in use and new requests cannot get a connection
- **Severity**: ERROR
- **Common cause**: Slow queries holding connections, connection leaks, too many concurrent users for pool size
- **Fix**: Increase pool max size. Fix slow queries. Fix connection leaks. Monitor pool utilization.
- **Debugging**: SMA → Database → Connection Pool. Check for queries holding connections > 30 seconds.

## PEGA0051 — Database Deadlock Detected
- **What**: Two or more transactions are blocking each other, causing a deadlock
- **Severity**: ERROR
- **Common cause**: Concurrent updates to the same case/row, poorly ordered locking, batch + interactive conflicts
- **Fix**: Ensure consistent lock ordering. Use optimistic locking. Reduce transaction scope. Retry after deadlock.
- **Debugging**: Database logs show deadlock graph. Identify the two competing transactions.

## PEGA0052 — Disk Space Warning
- **What**: Server disk space is running low
- **Threshold**: Below 10% free or below 1GB free
- **Common cause**: Log file growth, temp files, large attachments, database growth
- **Fix**: Archive/rotate logs. Clean temp files. Move attachments to external storage. Add disk space.

## PEGA0053 — JVM Heap Usage Critical
- **What**: JVM heap usage exceeded 90% of maximum
- **Severity**: WARNING (ERROR at 95%)
- **Common cause**: Memory leak, large clipboard pages, insufficient heap allocation
- **Fix**: Increase -Xmx. Fix memory leaks. Reduce clipboard sizes. Add nodes for horizontal scaling.
- **Debugging**: Enable heap dump on OOM. Use JVisualVM or Eclipse MAT to analyze.

## PEGA0054 — Cluster Communication Failure
- **What**: A node in the cluster failed to communicate with other nodes
- **Severity**: ERROR
- **Common cause**: Network partition, node crash, Hazelcast/Ignite communication failure
- **Fix**: Check network between nodes. Restart failed nodes. Check cluster configuration.
- **Debugging**: Check Hazelcast/Ignite logs. Verify multicast or TCP-IP cluster discovery settings.

## PEGA0055 — Out of Memory Error
- **What**: JVM ran out of heap memory — OutOfMemoryError thrown
- **Severity**: FATAL
- **Immediate action**: Restart the node. Capture heap dump for analysis.
- **Common cause**: Memory leak, very large case data, too many active sessions, clipboard bloat
- **Fix**: Increase heap (-Xmx). Analyze heap dump with Eclipse MAT. Fix largest memory consumers.
- **Correlated alerts**: Often preceded by PEGA0003 (large clipboard) and PEGA0014 (frequent GC)

## PEGA0056 — Elasticsearch Index Corruption
- **What**: Elasticsearch index is corrupted or unavailable
- **Severity**: ERROR
- **Common cause**: Disk full during indexing, abrupt server shutdown, Elasticsearch node failure
- **Fix**: Re-index from the database. Repair or rebuild the Elasticsearch index. Check Elasticsearch cluster health.
- **Debugging**: Elasticsearch API: `GET /_cluster/health`, `GET /_cat/indices`

## PEGA0057 — Scheduled Agent Failure
- **What**: A scheduled agent threw an exception and failed to complete
- **Severity**: ERROR
- **Context**: Agent name, exception message, stack trace
- **Common cause**: Data error in the records being processed, external system unavailable, timeout
- **Fix**: Fix the root cause exception. Add error handling in the agent activity. Skip/quarantine problem records.

## PEGA0058 — Large BLOB Write
- **What**: Writing a very large BLOB to the database (case data exceeds threshold)
- **Threshold DSS**: `alerts/blob/size/threshold` (default: 1MB)
- **Common cause**: Case accumulated too much data, large embedded page lists, attachment data stored in BLOB
- **Fix**: Clean up unnecessary properties. Move large data to separate tables. Use Declare Index for reportable properties to avoid BLOB reads.

## PEGA0059 — Configuration Integrity Warning
- **What**: A system configuration inconsistency was detected
- **Severity**: WARNING
- **Common cause**: Missing DSS settings after upgrade, conflicting prconfig.xml entries, orphaned ruleset references
- **Fix**: Run System Health Check. Resolve configuration conflicts. Apply post-upgrade configuration.

## PEGA0060 — License Threshold Warning
- **What**: License usage approaching the licensed limit (users, transactions, etc.)
- **Severity**: WARNING
- **Common cause**: User growth, increased transaction volume, license renewal needed
- **Fix**: Contact Pega licensing. Optimize user management (deactivate unused operators). Plan capacity.
"""
    },
    {
        "url": "curated://pega-alerts-pega0061-to-pega0075-security",
        "title": "PEGA0061–PEGA0075 — Security, Authentication, and Authorization Alert Codes",
        "content": """# PEGA0061–PEGA0075 — Security, Authentication, and Authorization Alerts

## PEGA0061 — Authentication Failure
- **What**: A user or service authentication attempt failed
- **Severity**: WARNING (ERROR after repeated failures)
- **Context**: Username/operator ID, authentication method, source IP, failure reason
- **Common causes**:
  - Wrong password
  - Account locked/disabled
  - LDAP/AD server unreachable
  - SSO/SAML token invalid or expired
  - OAuth client credentials invalid
  - Certificate authentication failure
- **Fix**: Check operator record status. Verify LDAP connectivity. Check SAML metadata. Verify OAuth token.
- **Security concern**: Multiple failures from same IP may indicate brute-force attack

## PEGA0062 — Authorization Failure (Access Denied)
- **What**: An authenticated user attempted an action they don't have permission for
- **Severity**: WARNING
- **Context**: Operator ID, attempted action, required privilege, access group
- **Common causes**:
  - Missing role in access group
  - Missing privilege on the role
  - Access When/Deny rule blocking access
  - ARO (Access Role to Object) not configured for the class
  - Attempted to access a restricted portal
- **Fix**: Check Access Group → Roles → Privileges. Check ARO for the class. Review Access When/Deny rules.
- **Security concern**: Repeated authorization failures may indicate privilege escalation attempt

## PEGA0063 — Brute Force Detection
- **What**: Multiple failed login attempts detected from the same source within a short period
- **Severity**: ERROR
- **Threshold DSS**: `security/bruteforce/threshold` (default: 5 attempts in 5 minutes)
- **Common cause**: Password guessing attack, misconfigured service account retrying with wrong credentials
- **Response**:
  1. Account auto-locks after threshold (configurable)
  2. Alert sent to security team
  3. Source IP may be blocked (if WAF configured)
- **Fix**: If legitimate user: unlock account, reset password. If attack: block IP, enable CAPTCHA, implement MFA.

## PEGA0064 — Session Hijacking Attempt Detected
- **What**: Suspicious session behavior detected — possible session hijacking
- **Severity**: ERROR
- **Detection criteria**: Session token reused from different IP, user-agent changed mid-session, concurrent sessions from different locations
- **Response**: Session terminated. User must re-authenticate.
- **Fix**: Enable secure session settings. Use HttpOnly and Secure cookie flags. Implement session binding to IP.
- **DSS settings**: `security/session/bindToIP=true`, `security/session/validateUserAgent=true`

## PEGA0065 — Cross-Site Scripting (XSS) Attempt Blocked
- **What**: Input containing potential XSS payload was detected and blocked
- **Severity**: WARNING
- **Context**: Input field, payload pattern, source IP, user
- **Common cause**: Malicious user input, penetration testing, automated scanner
- **Fix**: Ensure output encoding is enabled. Validate all user inputs. Use Content Security Policy (CSP) headers.
- **DSS settings**: `security/xss/filter/enabled=true`

## PEGA0066 — Cross-Site Request Forgery (CSRF) Token Mismatch
- **What**: CSRF token validation failed — request may be forged
- **Severity**: WARNING
- **Common cause**: Session timeout (token expired), bookmark to a form page, actual CSRF attack
- **Fix**: If legitimate: ensure CSRF tokens are included in all forms. If attack: review access logs, block source.
- **DSS settings**: `security/csrf/enabled=true`

## PEGA0067 — Authentication Service Unavailable
- **What**: The external authentication service (LDAP, SAML IdP, OAuth provider) is unreachable
- **Severity**: ERROR
- **Common cause**: LDAP server down, SAML IdP maintenance, OAuth provider network issue
- **Impact**: Users cannot log in while the auth service is down
- **Fix**: Check auth service availability. Configure fallback authentication. Implement auth service health monitoring.
- **Mitigation**: Configure local fallback auth for emergency admin access

## PEGA0068 — Password Policy Violation
- **What**: A password change or set operation violated the configured password policy
- **Severity**: INFO
- **Common cause**: Password too short, missing complexity requirements, password reuse, password in dictionary
- **Fix**: Inform user of password requirements. Adjust password policy if too restrictive.
- **Configuration**: Security → Password Policies → Complexity, History, Expiration rules

## PEGA0069 — Privilege Escalation Attempt
- **What**: A user attempted to access functionality above their assigned privilege level
- **Severity**: ERROR
- **Detection**: User tried to modify their own access group, access admin portals, or bypass access controls
- **Common cause**: Actual attack attempt, misconfigured URL allowing direct access to admin functions
- **Fix**: Review URL access controls. Ensure all admin functions check privileges. Enable security auditing.

## PEGA0070 — Sensitive Data Access Logged
- **What**: A user accessed data marked as sensitive (PII, financial, health data)
- **Severity**: INFO
- **Context**: User, data class, record ID, access type (read/write)
- **Purpose**: Compliance audit trail — required for GDPR, HIPAA, SOX
- **Configuration**: Mark properties as "sensitive" in class definition. Enable audit logging.

## PEGA0071 — Encryption/Decryption Failure
- **What**: A property encryption or decryption operation failed
- **Severity**: ERROR
- **Common cause**: Encryption key missing or corrupted, key rotation issue, unsupported algorithm
- **Fix**: Check keystore configuration. Verify encryption keys are present. Check algorithm compatibility.
- **Debugging**: SMA → Security → Encryption → verify keystore status

## PEGA0072 — Certificate Expiry Warning
- **What**: An SSL/TLS certificate is approaching expiration
- **Severity**: WARNING (30 days before), ERROR (7 days before)
- **Common cause**: Certificate not renewed in time
- **Fix**: Renew the certificate. Import new certificate into Pega's keystore/truststore. Restart affected services.
- **Monitoring**: Set up automated certificate expiry monitoring

## PEGA0073 — Unauthorized API Access Attempt
- **What**: An API call was made without proper authentication or with insufficient authorization
- **Severity**: WARNING
- **Context**: API endpoint, HTTP method, source IP, error code (401/403)
- **Common cause**: Expired API token, missing OAuth scope, wrong API key, IP not whitelisted
- **Fix**: Verify API credentials. Check OAuth token expiration. Review API security configuration.

## PEGA0074 — Security Configuration Change
- **What**: A change was made to security-related configuration (roles, privileges, access groups, auth settings)
- **Severity**: INFO
- **Context**: Who made the change, what was changed, old value, new value
- **Purpose**: Security audit trail — tracks all security configuration modifications
- **Compliance**: Required for SOX, PCI-DSS, HIPAA audit trails

## PEGA0075 — Suspicious Activity Pattern Detected
- **What**: System detected an unusual pattern of user activity that may indicate compromise
- **Severity**: ERROR
- **Detection criteria**: Unusual access times, accessing resources never accessed before, bulk data export, rapid navigation through many cases
- **Response**: Alert security team. Optionally suspend the session pending investigation.
- **Fix**: Investigate the user's activity. Check if account was compromised. Reset credentials if needed.
"""
    },
    {
        "url": "curated://pega-alerts-pega0076-to-pega0099-system",
        "title": "PEGA0076–PEGA0099 — System, Infrastructure, and Operational Alert Codes",
        "content": """# PEGA0076–PEGA0099 — System, Infrastructure, and Operational Alerts

## PEGA0076 — Node Startup Failure
- **What**: A Pega node failed to start properly
- **Severity**: FATAL
- **Common cause**: Database unreachable, invalid configuration, missing JARs, port conflict
- **Fix**: Check startup logs. Verify database connectivity. Check prconfig.xml. Verify port availability.

## PEGA0077 — Node Shutdown Initiated
- **What**: A Pega node is shutting down (planned or unplanned)
- **Severity**: INFO (planned) / ERROR (unplanned)
- **Context**: Reason for shutdown, node name, time
- **Fix for unplanned**: Check why the node crashed (OOM, kill signal, hardware failure). Review logs before the shutdown.

## PEGA0078 — Cluster Node Joined
- **What**: A new node joined the Pega cluster
- **Severity**: INFO
- **Purpose**: Operational tracking — confirms horizontal scaling events

## PEGA0079 — Cluster Node Left
- **What**: A node left the Pega cluster
- **Severity**: WARNING (planned) / ERROR (unexpected departure)
- **Common cause for unexpected**: Node crash, network partition, Hazelcast timeout
- **Fix**: Check the departed node's status. Restart if crashed. Check network if partition.

## PEGA0080 — Schema Validation Error
- **What**: Database schema doesn't match expected Pega schema version
- **Severity**: ERROR
- **Common cause**: Incomplete upgrade, DDL script failure, manual schema modification
- **Fix**: Run Pega's schema validation tool. Apply missing DDL scripts. Never modify Pega tables manually.

## PEGA0081 — Ruleset Version Lock Conflict
- **What**: Attempt to modify a rule in a locked ruleset version
- **Severity**: WARNING
- **Common cause**: Developer trying to edit production ruleset, locked version not unlocked for development
- **Fix**: Unlock the ruleset version for development. Use a new version for changes.

## PEGA0082 — Import/Export Error
- **What**: RAP import or product rule export failed
- **Severity**: ERROR
- **Common cause**: Version conflict, missing dependencies, schema mismatch, disk space
- **Fix**: Check import log for specific errors. Resolve dependencies. Verify target environment compatibility.

## PEGA0083 — Background Process Stalled
- **What**: A background process (agent, queue processor, data flow) has not made progress for an extended period
- **Threshold**: No progress for 15 minutes (configurable)
- **Common cause**: Deadlock, infinite loop, waiting for locked resource, external system blocking
- **Fix**: Check thread dump. Identify the blocked process. Restart if necessary. Fix root cause.

## PEGA0084 — Cassandra/External Data Store Error
- **What**: Connection or operation failure with an external data store (Cassandra, MongoDB, etc.)
- **Severity**: ERROR
- **Common cause**: Data store unreachable, timeout, authentication failure
- **Fix**: Check data store cluster health. Verify connection settings. Check authentication.

## PEGA0085 — Search Index Rebuild Required
- **What**: The search index is out of sync with the database and needs rebuilding
- **Severity**: WARNING
- **Common cause**: Elasticsearch crash during indexing, database restore without index restore
- **Fix**: Trigger full re-index from SMA → Search → Rebuild Index

## PEGA0086 — Hazelcast Partition Lost
- **What**: Hazelcast lost a data partition, potentially losing cached data
- **Severity**: ERROR
- **Common cause**: Multiple node failures, network partition affecting majority of cluster
- **Fix**: Restart affected nodes. Verify data integrity. Cluster will recover automatically if majority is intact.

## PEGA0087 — Tenant Isolation Violation (Multi-Tenant)
- **What**: A request attempted to access data belonging to a different tenant
- **Severity**: FATAL (security incident)
- **Common cause**: Missing tenant filter in custom code, misconfigured access policy
- **Fix**: IMMEDIATELY investigate. Fix the tenant filter. Review all custom data access code.

## PEGA0088 — Deprecated API Usage
- **What**: Application code is using a deprecated Pega API that will be removed in a future version
- **Severity**: INFO
- **Context**: Deprecated API name, replacement API, removal version
- **Fix**: Update code to use the replacement API before upgrading.

## PEGA0089 — Deprecated Feature Warning
- **What**: Application uses a feature deprecated in the current Pega version
- **Severity**: WARNING
- **Common deprecated features**: Classic UI in Infinity '24, certain activity methods, legacy authentication
- **Fix**: Plan migration to the replacement feature. Check Pega upgrade guide.

## PEGA0090 — Data Integrity Check Failed
- **What**: A data integrity validation detected inconsistent data
- **Severity**: ERROR
- **Common cause**: Concurrent modification, failed transaction rollback, database corruption
- **Fix**: Identify the inconsistent records. Repair data manually or via admin activity. Investigate root cause.

## PEGA0091 — Cache Synchronization Failure
- **What**: Cache synchronization between nodes failed
- **Severity**: WARNING
- **Common cause**: Network latency, large cache update, cluster communication issue
- **Impact**: Some nodes may serve stale data until sync recovers
- **Fix**: Check cluster communication. Force cache clear on affected nodes via SMA.

## PEGA0092 — Long-Running Decision Strategy
- **What**: A Next-Best-Action or decision strategy execution exceeded the threshold
- **Threshold DSS**: `alerts/strategy/threshold` (default: 5000ms)
- **Common cause**: Complex strategy with many actions, slow adaptive model scoring, large customer context
- **Fix**: Optimize strategy. Reduce action count. Pre-compute customer features.

## PEGA0093 — Predictive Model Scoring Error
- **What**: An error occurred while scoring a predictive or adaptive model
- **Severity**: ERROR
- **Common cause**: Missing predictor values, model corruption, incompatible model version
- **Fix**: Retrain the model. Ensure all predictor properties are populated. Check model compatibility with current Pega version.

## PEGA0094 — Data Flow Processing Error
- **What**: A Data Flow run encountered errors during batch processing
- **Severity**: ERROR
- **Context**: Data flow name, error count, records processed, records failed
- **Fix**: Check failed records. Fix data issues. Re-run the data flow for failed records only.

## PEGA0095 — Kafka/Messaging Connectivity Error
- **What**: Connection to Kafka broker or JMS provider failed
- **Severity**: ERROR
- **Common cause**: Broker down, network issue, authentication failure, topic doesn't exist
- **Fix**: Check broker availability. Verify connection settings. Check authentication. Create missing topics.

## PEGA0096 — Robot Runtime Error (RPA)
- **What**: A Pega RPA robot encountered a runtime error
- **Severity**: ERROR
- **Common cause**: Target application UI changed, element not found, application not responding
- **Fix**: Update robot automation for UI changes. Add wait steps. Implement error recovery paths.

## PEGA0097 — GenAI Service Error
- **What**: A Pega GenAI feature (Knowledge Buddy, case summarization) encountered an error
- **Severity**: WARNING
- **Common cause**: LLM service unreachable, token limit exceeded, prompt rejected
- **Fix**: Check LLM provider connectivity. Verify API key. Check prompt content. Review token limits.

## PEGA0098 — System Health Check Warning
- **What**: Automated system health check detected a degraded condition
- **Severity**: WARNING
- **Checks include**: Database connectivity, search health, cluster membership, memory, disk
- **Fix**: Address the specific health check failure reported in the alert details.

## PEGA0099 — Custom Application Alert
- **What**: Custom application-level alert triggered by developer-defined conditions
- **Severity**: Configurable
- **How to create**: Use `pega_rules_alert` API in activities or Java steps to fire custom alerts
- **Use cases**: Business SLA breach, data quality threshold, custom performance metric
"""
    },
    {
        "url": "curated://pega-security-event-log",
        "title": "Pega Security Event Log — Complete Guide to Security Auditing and Forensics",
        "content": """# Pega Security Event Log — Complete Guide

## What is the Security Event Log?
The SecurityEvent.log is a dedicated log file that records ALL security-related events in Pega — authentication attempts, authorization decisions, security configuration changes, and suspicious activity. It's critical for compliance (SOX, HIPAA, PCI-DSS, GDPR) and security forensics.

## Log Location
- **Embedded Tomcat**: `<PEGA_HOME>/logs/SecurityEvent.log`
- **WebSphere**: `<WAS_PROFILE>/logs/<SERVER>/SecurityEvent.log`
- **WebLogic**: `<DOMAIN>/servers/<SERVER>/logs/SecurityEvent.log`

## Events Logged

### Authentication Events
| Event Type | Description | Fields Logged |
|-----------|-------------|---------------|
| AUTH_SUCCESS | Successful login | Operator ID, IP, timestamp, auth method |
| AUTH_FAILURE | Failed login attempt | Attempted username, IP, failure reason, auth method |
| AUTH_LOCKOUT | Account locked after failed attempts | Operator ID, IP, attempt count |
| AUTH_UNLOCK | Account unlocked (admin or auto) | Operator ID, unlocked by, method |
| SESSION_CREATE | New session created | Operator ID, session ID, IP |
| SESSION_DESTROY | Session ended (logout or timeout) | Operator ID, session ID, reason |
| SESSION_TIMEOUT | Session expired due to inactivity | Operator ID, session ID, idle duration |
| TOKEN_ISSUED | OAuth/JWT token issued | Client ID, scope, token type |
| TOKEN_REVOKED | OAuth/JWT token revoked | Client ID, token ID, reason |

### Authorization Events
| Event Type | Description | Fields Logged |
|-----------|-------------|---------------|
| ACCESS_GRANTED | Access to resource allowed | Operator, resource, privilege used |
| ACCESS_DENIED | Access to resource denied | Operator, resource, required privilege, user's roles |
| PRIVILEGE_CHECK | Privilege evaluation | Operator, privilege name, result (pass/fail) |
| ROLE_ASSIGNMENT | Role added to or removed from user | Operator, role, action (add/remove), changed by |

### Configuration Change Events
| Event Type | Description | Fields Logged |
|-----------|-------------|---------------|
| ACCESS_GROUP_CHANGED | Access group configuration modified | Old config, new config, changed by |
| ROLE_MODIFIED | Role privileges modified | Role name, privileges added/removed, changed by |
| AUTH_CONFIG_CHANGED | Authentication settings changed | Setting name, old value, new value, changed by |
| PASSWORD_POLICY_CHANGED | Password policy modified | Policy, old rules, new rules, changed by |
| OPERATOR_CREATED | New operator record created | Operator ID, created by, access group |
| OPERATOR_DISABLED | Operator account disabled | Operator ID, disabled by, reason |

### Security Incident Events
| Event Type | Description | Fields Logged |
|-----------|-------------|---------------|
| BRUTE_FORCE_DETECTED | Multiple failed logins from same source | Source IP, attempt count, time window |
| SESSION_HIJACK_SUSPECT | Suspicious session behavior | Session ID, original IP, new IP, user-agent change |
| XSS_BLOCKED | XSS attempt detected and blocked | Input field, payload sample, source IP |
| CSRF_BLOCKED | CSRF token validation failed | Request URL, source IP, referer |
| SQL_INJECTION_BLOCKED | SQL injection attempt detected | Input field, payload sample, source IP |
| PRIVILEGE_ESCALATION | Unauthorized privilege elevation attempt | Operator, attempted action, current privileges |

## Enabling Security Event Logging
1. Navigate to **SMA → Security → Audit Configuration**
2. Enable each event category you want to log
3. Configure log destination (file, database, SIEM integration)
4. Set retention period (regulatory minimum: typically 1-7 years)

### DSS Settings for Security Logging
| DSS | Purpose | Recommended Value |
|-----|---------|-------------------|
| security/audit/authentication/enabled | Log auth events | true |
| security/audit/authorization/enabled | Log access decisions | true |
| security/audit/configchange/enabled | Log security config changes | true |
| security/audit/dataaccess/enabled | Log sensitive data access | true (for compliance) |
| security/audit/level | Detail level (BASIC/DETAILED/VERBOSE) | DETAILED for prod |

## Log Analysis for Security Forensics

### Detecting Brute Force Attacks
```bash
# Count failed logins per IP in the last hour
grep "AUTH_FAILURE" SecurityEvent.log | grep "$(date +%Y-%m-%d)" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -10
```

### Detecting Unauthorized Access
```bash
# Find all ACCESS_DENIED events for a specific user
grep "ACCESS_DENIED" SecurityEvent.log | grep "operatorID=admin" | tail -20
```

### Detecting Session Anomalies
```bash
# Find sessions that changed IP mid-session
grep "SESSION_HIJACK_SUSPECT" SecurityEvent.log | tail -10
```

## SIEM Integration
Pega security events can be forwarded to SIEM systems (Splunk, QRadar, ArcSight, Sentinel):
1. Configure syslog forwarding in prlog4j2.xml
2. Map Pega event types to SIEM event categories
3. Set up SIEM correlation rules for Pega-specific attack patterns
4. Create SIEM dashboards for Pega security monitoring

## Compliance Requirements
| Regulation | Required Events | Retention |
|-----------|-----------------|-----------|
| SOX | Auth, access, config changes | 7 years |
| HIPAA | All events + data access | 6 years |
| PCI-DSS | Auth, access, config changes | 1 year |
| GDPR | Data access, consent changes | Varies |
"""
    },
    {
        "url": "curated://pega-security-exceptions-deep-dive",
        "title": "Pega Security Exceptions — Authentication, Authorization, and Encryption Error Reference",
        "content": """# Pega Security Exceptions — Complete Reference

## Authentication Exceptions

### PRSecurityException: Authentication Failed
- **Message**: `com.pega.pegarules.pub.PRSecurityException: Authentication failed for operator [username]`
- **Causes**: Wrong password, account locked, account disabled, auth service unreachable
- **Debug steps**:
  1. Check operator record: Dev Studio → Records → SysAdmin → Operator ID
  2. Check if account is locked (too many failed attempts)
  3. Check if account is disabled
  4. Check auth service: SMA → Security → Authentication Service → Test Connection
  5. Check SecurityEvent.log for AUTH_FAILURE details

### LDAPException: Cannot Connect to LDAP Server
- **Message**: `javax.naming.CommunicationException: LDAP server unreachable`
- **Causes**: LDAP server down, wrong host/port, firewall blocking LDAP port (389/636)
- **Fix**: Test LDAP connectivity: `telnet ldap.example.com 389`. Check LDAP URL in auth service config. Check SSL certificate for LDAPS (port 636).

### SAMLException: SAML Assertion Invalid
- **Message**: `SAML Response validation failed: signature mismatch` or `SAML assertion expired`
- **Common causes**:
  - Clock skew between Pega and IdP (SAML assertions have timestamps)
  - Wrong IdP certificate configured in Pega
  - SAML metadata not refreshed after IdP certificate rotation
  - Audience restriction mismatch
- **Fix**: Sync clocks (NTP). Re-import IdP metadata. Verify audience URI matches. Check certificate validity.

### OAuthException: Token Validation Failed
- **Messages**:
  - `Invalid access token` — token is malformed or from wrong issuer
  - `Token expired` — access token TTL exceeded
  - `Insufficient scope` — token doesn't have required scope/permission
  - `Invalid client credentials` — client ID or secret is wrong
- **Fix**: Refresh the token. Check token issuer URL. Verify client credentials. Request additional scopes.

### KerberosException: Kerberos Authentication Failed
- **Message**: `GSSException: No valid credentials provided`
- **Causes**: Keytab file missing/invalid, SPN mismatch, clock skew with KDC, Kerberos realm misconfigured
- **Fix**: Verify keytab file. Check SPN registration. Sync clocks with domain controller. Verify realm configuration.

## Authorization Exceptions

### PRSecurityException: Not Authorized
- **Message**: `com.pega.pegarules.pub.PRSecurityException: Not authorized to perform [action] on [class]`
- **Debug steps**:
  1. Identify the user's Access Group: Dev Studio → check operator record
  2. Check Access Group roles: What roles are assigned?
  3. Check each role's privileges: Does any role have the required privilege?
  4. Check ARO (Access Role to Object): Does the role have read/write/delete for the target class?
  5. Check Access When/Deny rules: Is there a deny rule blocking this specific user?

### AccessDeniedException: Access When Rule Failed
- **Message**: `Access denied by Access When rule [rule-name] on class [class-name]`
- **Causes**: The Access When condition evaluated to false for this user/record combination
- **Fix**: Check the Access When rule logic. Verify the user's properties match the condition. Test with Tracer → Security tracking enabled.

### PrivilegeException: Missing Privilege
- **Message**: `Privilege [privilege-name] required but not found in operator's roles`
- **Fix**: Add the privilege to one of the user's roles, or add a role that has the privilege to the user's access group.

## Encryption Exceptions

### CryptographyException: Encryption Failed
- **Message**: `com.pega.pegarules.pub.CryptographyException: Failed to encrypt property [property-name]`
- **Causes**: Encryption key not found, keystore corrupt, algorithm not supported
- **Fix**: Check keystore: SMA → Security → Keystores. Verify the encryption key exists. Regenerate key if corrupted.

### CryptographyException: Decryption Failed
- **Message**: `Failed to decrypt property — key mismatch or data corrupted`
- **Causes**: Data encrypted with a different key (key rotation issue), data corrupted, wrong algorithm
- **Fix**: Identify which key encrypted the data. Ensure old keys are retained during key rotation. Re-encrypt data with current key if needed.

### KeyStoreException: Keystore Access Failed
- **Message**: `java.security.KeyStoreException: Cannot load keystore`
- **Causes**: Keystore file missing, wrong password, corrupted file, unsupported format
- **Fix**: Verify keystore path in prconfig.xml. Check keystore password. Re-create keystore if corrupted.

## SSL/TLS Exceptions

### SSLHandshakeException: Certificate Not Trusted
- **Message**: `javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException: PKIX path building failed`
- **Translation**: Pega doesn't trust the external system's SSL certificate
- **Fix**: Import the external system's CA certificate into Pega's truststore:
  ```bash
  keytool -import -alias myservice -file service-cert.pem -keystore cacerts -storepass changeit
  ```
  Restart Pega after importing.

### SSLHandshakeException: Certificate Expired
- **Message**: `NotAfter: [date]` in the SSL exception
- **Fix**: Renew the expired certificate. Import the new certificate. Restart affected services.

### SSLProtocolException: Protocol Version Not Supported
- **Message**: `SSLProtocolException: TLS 1.0 is not supported`
- **Causes**: Server or client requires a higher TLS version than the other supports
- **Fix**: Enable TLS 1.2+ on both sides. Disable TLS 1.0/1.1 (security requirement). Configure in JVM args: `-Dhttps.protocols=TLSv1.2,TLSv1.3`
"""
    },
    {
        "url": "curated://pega-security-alert-response-runbook",
        "title": "Security Alert Response Runbook — How to Respond to Each Security Alert Type",
        "content": """# Security Alert Response Runbook

## Purpose
This runbook provides step-by-step response procedures for each type of Pega security alert. Follow these procedures to ensure consistent, timely, and appropriate responses to security events.

## Severity Levels and Response Times
| Severity | Response Time | Examples |
|----------|--------------|---------|
| FATAL | Immediate (< 15 min) | Tenant isolation violation, system compromise |
| ERROR | Within 1 hour | Brute force, session hijacking, privilege escalation |
| WARNING | Within 4 hours | Auth failures, CSRF blocked, certificate expiry |
| INFO | Next business day | Password policy violations, config changes, audit events |

## Response Procedures

### Procedure 1: Failed Authentication (PEGA0061)
**Single occurrence:**
1. Check if it's a legitimate user with a typo — no action needed
2. Log for audit trail

**Multiple occurrences (same user):**
1. Check operator record — is it locked?
2. If locked: verify the user's identity before unlocking
3. If not locked: monitor for continued failures
4. Check SecurityEvent.log for source IP

**Multiple occurrences (same IP, different users):**
1. **ESCALATE** — potential credential stuffing attack
2. Block the source IP at WAF/firewall
3. Enable CAPTCHA for login page
4. Notify security team
5. Review all accounts that were targeted

### Procedure 2: Brute Force Detected (PEGA0063)
1. **Immediately block** the source IP at WAF/firewall
2. Verify the targeted account is locked
3. Check if the account was compromised (any successful login from the attacker IP)
4. If compromised: force password reset, revoke all sessions, audit activity
5. If not compromised: keep account locked until user verifies identity
6. Report the incident per security policy
7. Review firewall rules and rate limiting configuration

### Procedure 3: Session Hijacking Suspect (PEGA0064)
1. **Immediately terminate** the suspicious session
2. Force re-authentication for the affected user
3. Check SecurityEvent.log: what actions were performed during the suspicious session?
4. Check if sensitive data was accessed
5. If confirmed hijacking: reset user credentials, audit all actions during the suspicious period
6. Review session security configuration (cookie flags, IP binding)

### Procedure 4: XSS/CSRF Attack Blocked (PEGA0065/0066)
1. Record the attack payload for analysis
2. Check if the same source IP is attempting other attacks
3. If automated scanner: likely penetration testing — verify if authorized
4. If not authorized: block IP, review input validation rules
5. Verify all output encoding is properly configured
6. Run security scan on the application

### Procedure 5: Privilege Escalation Attempt (PEGA0069)
1. **Immediately suspend** the user's session
2. Check SecurityEvent.log: what was the user trying to access?
3. Check if any escalation was successful (did they get elevated access?)
4. If successful: **CRITICAL** — revoke access, audit all actions with elevated privileges, engage security team
5. If blocked: review why the attempt was possible (URL access control gap?)
6. Fix the access control gap
7. Report the incident

### Procedure 6: Tenant Isolation Violation (PEGA0087)
1. **CRITICAL SECURITY INCIDENT** — engage security team immediately
2. Identify which tenant's data was exposed
3. Identify which user/request triggered the violation
4. Determine the scope: how much data was exposed?
5. Fix the tenant filter immediately (emergency patch)
6. Notify affected tenant(s) per data breach policy
7. Conduct full code review of data access patterns
8. Document the incident for compliance reporting

### Procedure 7: Certificate Expiry Warning (PEGA0072)
1. Identify which certificate is expiring and when
2. Initiate certificate renewal process
3. Plan the certificate replacement (may require maintenance window)
4. Test the new certificate in a non-production environment
5. Deploy the new certificate before the old one expires
6. Verify all services are functioning with the new certificate

## Post-Incident Steps (For All Security Incidents)
1. **Document** the incident: timeline, impact, response actions
2. **Root cause analysis**: why did it happen? what failed?
3. **Remediation**: fix the vulnerability/gap that allowed the incident
4. **Lessons learned**: update runbook, improve monitoring, add new alert rules
5. **Compliance reporting**: notify compliance team if required by regulations
"""
    },
    {
        "url": "curated://pega-ldap-sso-exceptions",
        "title": "LDAP, SSO, SAML, and OAuth Exceptions in Pega — Troubleshooting Authentication Integrations",
        "content": """# LDAP, SSO, SAML, and OAuth Exceptions — Troubleshooting Guide

## LDAP Authentication Errors

### javax.naming.AuthenticationException
- **Message**: `[LDAP: error code 49 - Invalid Credentials]`
- **Cause**: LDAP bind failed — wrong username or password for the LDAP service account
- **Fix**: Verify LDAP bind DN and password in Pega auth service. Test with `ldapsearch` from Pega server.

### javax.naming.CommunicationException
- **Message**: `LDAP server [host:port] not reachable`
- **Cause**: LDAP server down, wrong host/port, firewall blocking
- **Fix**: Test connectivity: `telnet ldap.example.com 389`. Check DNS. Check firewall rules for LDAP ports (389 for LDAP, 636 for LDAPS).

### javax.naming.NamingException: LDAP Referral
- **Message**: `Unprocessed continuation reference(s)`
- **Cause**: LDAP search crossed a domain boundary and returned a referral
- **Fix**: Set referral handling to "follow" in LDAP connection settings: `java.naming.referral=follow`

### LDAP Error Code Reference
| Code | Meaning | Fix |
|------|---------|-----|
| 1 | Operations error | Check LDAP server logs |
| 32 | No such object | Verify base DN is correct |
| 34 | Invalid DN syntax | Check LDAP bind DN format |
| 48 | Inappropriate authentication | Wrong auth mechanism (simple vs SASL) |
| 49 | Invalid credentials | Wrong password or bind DN |
| 50 | Insufficient access rights | LDAP service account needs more permissions |
| 52 | Unavailable | LDAP server is not accepting connections |
| 53 | Unwilling to perform | Server policy prevents the operation |
| 81 | Server not available | Network issue or server down |

## SAML/SSO Errors

### SAML Response Signature Validation Failed
- **Cause**: IdP certificate in Pega doesn't match the one the IdP used to sign the response
- **Fix**: Re-download IdP metadata. Import the current IdP signing certificate into Pega.

### SAML Assertion Expired
- **Message**: `SAML assertion not valid — NotOnOrAfter exceeded`
- **Cause**: Clock skew between Pega server and the IdP (SAML assertions have 5-minute validity)
- **Fix**: Synchronize clocks using NTP. Maximum allowed skew is typically 300 seconds.

### SAML Audience Restriction Mismatch
- **Message**: `SAML assertion audience [url] doesn't match expected [url]`
- **Cause**: The Audience URI in SAML configuration doesn't match what the IdP sends
- **Fix**: Check Pega's SAML SP configuration — the Entity ID/Audience must match exactly with what's configured in the IdP.

### SAML NameID Not Found in Pega
- **Message**: `No operator found for SAML NameID [value]`
- **Cause**: The IdP sends a username that doesn't match any Pega operator record
- **Fix**: Verify NameID format matches Pega operator IDs. Check if auto-provisioning is enabled. Verify the operator record exists.

### SAML Debugging Checklist
1. Check IdP metadata in Pega: is it current?
2. Check SP metadata sent to IdP: does Entity ID match?
3. Check certificate: has it been rotated?
4. Check clocks: NTP in sync?
5. Check NameID: format and value match Pega operators?
6. Enable SAML debug logging: `com.pega.pegarules.session.external.saml=DEBUG`

## OAuth 2.0 / OIDC Errors

### Invalid Client Error
- **Message**: `{"error": "invalid_client", "error_description": "Client authentication failed"}`
- **Cause**: Wrong client_id or client_secret
- **Fix**: Verify client credentials in Pega's OAuth client registration. Regenerate client secret if needed.

### Invalid Grant Error
- **Message**: `{"error": "invalid_grant", "error_description": "Authorization code expired or already used"}`
- **Cause**: Auth code used twice, or took too long between auth and token exchange
- **Fix**: Auth codes are single-use and time-limited (typically 10 minutes). Re-initiate the auth flow.

### Invalid Scope Error
- **Message**: `{"error": "invalid_scope", "error_description": "Requested scope is not allowed"}`
- **Cause**: Pega requesting scopes the OAuth provider doesn't allow for this client
- **Fix**: Check allowed scopes in the OAuth provider. Update Pega's requested scopes to match.

### Token Refresh Failed
- **Message**: `Refresh token is expired or revoked`
- **Cause**: Refresh token has a TTL and has expired. Or the OAuth provider revoked it.
- **Fix**: Re-authenticate the user (full login flow). Check refresh token TTL settings. Don't store refresh tokens beyond their lifetime.

### OIDC ID Token Validation Failed
- **Messages**: `ID token signature validation failed`, `ID token expired`, `nonce mismatch`
- **Cause**: Wrong signing key, clock skew, CSRF protection nonce mismatch
- **Fix**: Update OIDC provider's signing keys (JWKS). Sync clocks. Verify nonce handling.

## General Auth Debugging Steps
1. Enable security debug logging in prlog4j2.xml:
   - `com.pega.pegarules.session.security=DEBUG`
   - `com.pega.pegarules.session.external=DEBUG`
2. Check SecurityEvent.log for AUTH_FAILURE events
3. Check PegaRULES.log for the full exception stack trace
4. Test auth service connectivity from Pega server
5. Verify certificates haven't expired
6. Check clock sync between all systems involved
"""
    },
]


def seed_phase21():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE21:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase21_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE21)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 21 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase21()
