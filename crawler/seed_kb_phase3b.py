"""
Curated Pega Knowledge Base — Phase 3B
Covers: Integration patterns, Search/Reporting, Version-specific issues

Run: python -m crawler.seed_kb_phase3b
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE3B = [
    # ═══════════════════════════════════════════════════════════════════
    # INTEGRATION — File Listener, MQ, Kafka, Email Listener
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/integration/file-listener.html",
        "title": "File Listener — Configuration, Errors, and Troubleshooting",
        "content": """# File Listener — Configuration and Troubleshooting

## Overview
File Listeners monitor directories for incoming files and trigger processing (service rules or activities). Common in batch integrations, EDI feeds, and data import pipelines.

## Architecture
- **File Listener rule**: Defines the directory path, file pattern (glob/regex), polling interval
- **Service rule**: Processes the file content (Service File, Service REST, or Activity)
- **File management**: Move/delete/rename after processing

## Common Errors

### 1. File Listener Not Picking Up Files
**Symptoms**: Files sit in directory, no processing occurs
**Root Causes**:
- File Listener agent is not running (check Agent Schedule → pyFileListener)
- Directory path is wrong or inaccessible from the Pega server (not the client machine!)
- File pattern doesn't match (e.g., pattern is `*.csv` but files are `*.CSV` — case-sensitive on Linux)
- File is still being written (file lock) — use staging directory pattern
- Listener is disabled in the node classification

**Debug Steps**:
1. Check System → Operations → Agent Schedule — look for pyFileListener
2. Verify the directory is accessible FROM THE SERVER, not your local machine
3. Check logs for "FileListener" entries: `grep -i filelistener PegaRULES*.log`
4. Test with a simple small file first
5. Check the file pattern regex in the listener rule

### 2. File Processed But Data Missing/Wrong
**Symptoms**: File disappears from directory but records are wrong or incomplete
**Root Causes**:
- Parse rule has wrong delimiter or column mapping
- Character encoding mismatch (UTF-8 vs Latin-1 vs Windows-1252)
- Header row being treated as data or vice versa
- Field truncation due to property length limits

**Fix**:
- Use Tracer to step through the service rule processing
- Check the Parse rule column-to-property mapping
- Verify file encoding matches the parse rule's expected encoding
- Check property definitions for max-length constraints

### 3. File Listener Duplicate Processing
**Symptoms**: Same file processed multiple times
**Root Causes**:
- File management not configured (file stays in directory after processing)
- Multiple nodes running the same listener without proper coordination
- Error during processing causes retry without moving the file

**Fix**:
- Always configure post-processing action: Move to archive, Delete, or Rename
- Use "Processing directory" pattern: move file to temp dir before processing
- Enable single-node processing if coordination is an issue

### 4. Large File Performance Issues
**Symptoms**: OutOfMemoryError, timeouts, or extremely slow processing
**Root Causes**:
- Entire file loaded into memory (default behavior)
- No batch/chunk processing configured
- Database commit happening per-record instead of per-batch

**Fix**:
- Use streaming/chunked reading for large files
- Implement batch commits (e.g., commit every 1000 records)
- Increase JVM heap if necessary but prefer streaming
- Consider splitting large files before ingestion

## File Listener Best Practices
1. Always use staging directory pattern (write to staging, move to pickup)
2. Configure archive directory for processed files
3. Set appropriate polling interval (not too frequent for large directories)
4. Implement error handling with dead-letter directory
5. Log file name and record count for audit trail
6. Test with edge cases: empty files, huge files, special characters in filenames
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/integration/mq-jms-listener.html",
        "title": "MQ/JMS Integration — Listener, Connector, and Troubleshooting",
        "content": """# MQ/JMS Integration — Troubleshooting

## Overview
Pega integrates with message queues (IBM MQ, ActiveMQ, RabbitMQ, etc.) via JMS (Java Message Service). Two directions:
- **JMS Listener (Service)**: Pega consumes messages from a queue
- **JMS Connector**: Pega sends messages to a queue

## Architecture
- **JMS Resource**: Defines connection factory, queue/topic names, JNDI settings
- **Service Package**: Maps JMS listener to a service rule
- **Connector rule**: Sends messages with optional request-reply pattern

## Common Errors

### 1. JMS Connection Failure
**Error**: `javax.jms.JMSException: Failed to create session` or `MQRC_NOT_AUTHORIZED (2035)`
**Root Causes**:
- Wrong connection factory JNDI name
- MQ channel authentication failure (username/password or certificate)
- Firewall blocking the MQ port (default: 1414 for IBM MQ)
- SSL/TLS mismatch between Pega and MQ server

**Debug Steps**:
1. Check SMA → Integration → Services/Connectors for connection status
2. Verify JNDI settings in prconfig.xml or Dynamic System Settings
3. Test MQ connectivity outside Pega (e.g., amqsput/amqsget for IBM MQ)
4. Check MQ server logs for authentication/authorization errors
5. Verify SSL certificates if using encrypted connections

### 2. Messages Not Being Consumed
**Symptoms**: Messages pile up in queue, Pega not processing
**Root Causes**:
- JMS listener service package is stopped
- Node classification doesn't include the JMS listener
- Message selector filter is too restrictive
- Consumer is connected but paused (backout threshold reached)

**Fix**:
1. Check SMA → Services → Service Packages — is the JMS package running?
2. Verify node classification includes this service
3. Review message selector in the service rule
4. Check backout queue — if messages are being backed out, fix the processing error

### 3. Message Deserialization Errors
**Error**: `Unable to parse message` or property mapping failures
**Root Causes**:
- Message format doesn't match the expected schema (XML/JSON/text)
- Character encoding issues
- Message properties not mapped correctly in the service rule
- Unexpected message type (BytesMessage vs TextMessage)

**Fix**:
- Use MQ Explorer or similar tool to examine actual message content
- Verify the service rule's parse shape matches the message format
- Add explicit encoding handling
- Log raw message content for debugging

### 4. Duplicate Message Processing
**Symptoms**: Same business transaction processed multiple times
**Root Causes**:
- No idempotency check in the service rule
- Transaction rollback causes message redelivery
- Multiple consumers without proper acknowledgment

**Fix**:
- Implement idempotency: check for duplicate correlation ID before processing
- Use CLIENT_ACKNOWLEDGE mode and acknowledge after successful processing
- Set a reasonable redelivery limit and dead-letter queue

### 5. JMS Connector Timeout
**Error**: `Connector timeout` or `javax.jms.JMSException: Send timed out`
**Root Causes**:
- Queue manager is down or overloaded
- Queue is full (reached maximum depth)
- Network latency or firewall issues
- Request-reply pattern with no reply coming back

**Fix**:
1. Check queue depth — if full, investigate consumer side
2. Verify queue manager status
3. For request-reply: ensure the reply queue exists and reply is being sent
4. Increase timeout if network latency is the issue
5. Implement async pattern if synchronous isn't required

## MQ Best Practices
1. Always configure dead-letter queue for failed messages
2. Implement idempotency in all message consumers
3. Use correlation IDs for request-reply tracking
4. Monitor queue depths with alerts
5. Set appropriate backout thresholds
6. Test failover scenarios (MQ cluster, Pega node restart)
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/integration/kafka-connector.html",
        "title": "Kafka Integration — Dataset, Connector, and Troubleshooting",
        "content": """# Kafka Integration — Troubleshooting

## Overview
Pega supports Apache Kafka integration for high-throughput event streaming. Available since Pega 8.4+.
- **Kafka Dataset**: Consumes messages from Kafka topics (subscriber)
- **Kafka Connector**: Publishes messages to Kafka topics (producer)
- **Event-driven architecture**: Case creation/update from Kafka events

## Architecture
- **Kafka cluster settings**: Bootstrap servers, authentication, SSL
- **Dataset rule (Kafka type)**: Defines topic, consumer group, deserialization
- **Data flow**: Processes incoming Kafka messages in parallel

## Common Errors

### 1. Kafka Connection Failure
**Error**: `org.apache.kafka.common.errors.TimeoutException: Failed to update metadata`
**Root Causes**:
- Wrong bootstrap server address
- Firewall blocking Kafka port (default: 9092, SSL: 9093)
- SASL authentication configuration wrong
- SSL truststore/keystore misconfigured
- Kafka cluster is using advertised listeners that aren't reachable from Pega

**Debug Steps**:
1. Verify bootstrap servers in System Settings or prconfig.xml
2. Test network connectivity: `telnet kafka-host 9092` from Pega server
3. Check Kafka server logs for connection attempts
4. Verify SASL mechanism matches (PLAIN, SCRAM-SHA-256, etc.)
5. Check SSL certificate chain and truststore configuration

### 2. Consumer Not Receiving Messages
**Symptoms**: Messages in Kafka topic but Pega not processing
**Root Causes**:
- Consumer group already committed offsets past current messages
- Dataset rule is not enabled or not started
- Topic name mismatch (case-sensitive!)
- Consumer group is rebalancing continuously
- Data flow is stopped

**Fix**:
1. Check consumer group status: `kafka-consumer-groups.sh --describe --group <group>`
2. Verify dataset rule is enabled and data flow is running
3. Check for consumer group rebalancing in Kafka logs
4. Reset consumer group offset if needed (careful — may cause reprocessing)
5. Verify topic exists and has partitions with messages

### 3. Deserialization Errors
**Error**: `org.apache.kafka.common.errors.SerializationException`
**Root Causes**:
- Schema mismatch between producer and consumer
- Using Avro/Protobuf without schema registry configuration
- JSON parsing failure due to unexpected format
- Key vs Value deserializer misconfigured

**Fix**:
- Check the producer's serialization format
- Configure appropriate deserializer in the dataset rule
- If using Schema Registry, verify URL and schema compatibility
- Add error handling for malformed messages

### 4. Kafka Producer Errors
**Error**: `org.apache.kafka.common.errors.RecordTooLargeException` or timeout on send
**Root Causes**:
- Message exceeds max.message.bytes (default: 1MB)
- Kafka broker is overloaded or unavailable
- Producer buffer is full
- Acks configuration mismatch

**Fix**:
1. Check message size — compress or split large messages
2. Increase max.message.bytes on both broker and topic if needed
3. Configure appropriate acks level (0, 1, all) based on durability needs
4. Increase producer buffer.memory if throughput is high
5. Implement retry logic with exponential backoff

### 5. Data Flow Performance
**Symptoms**: High lag, slow processing, consumer falling behind
**Root Causes**:
- Not enough partitions for parallel consumption
- Processing logic too slow (database calls, external API calls)
- Insufficient Pega nodes or data flow threads
- Large messages causing memory pressure

**Fix**:
1. Increase topic partitions (but note: partitions can't be decreased)
2. Optimize processing logic — batch database operations
3. Scale Pega nodes or increase data flow thread count
4. Monitor consumer lag: `kafka-consumer-groups.sh --describe`
5. Consider separate topic for high-volume vs low-volume events

## Kafka Best Practices
1. Use Schema Registry for message format governance
2. Implement dead-letter topics for failed messages
3. Monitor consumer lag with alerting
4. Use idempotent producers and exactly-once semantics where needed
5. Plan partition count based on expected throughput and consumer parallelism
6. Test with realistic message volumes before production
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/integration/email-listener.html",
        "title": "Email Listener — Configuration, Parsing, and Troubleshooting",
        "content": """# Email Listener — Configuration and Troubleshooting

## Overview
Email Listeners in Pega monitor email accounts (IMAP/POP3) and trigger case creation or updates based on incoming emails. Common in customer service, HR, and support applications.

## Architecture
- **Email Account rule**: Defines server, port, protocol (IMAP/POP3), credentials
- **Email Listener**: Monitors the account, routes emails to service rules
- **Service Email rule**: Processes email content, attachments, and metadata
- **Triage flow**: Routes to appropriate case type based on subject/sender/content

## Common Errors

### 1. Email Listener Not Connecting
**Error**: `javax.mail.AuthenticationFailedException` or `Connection refused`
**Root Causes**:
- Wrong server/port/protocol (IMAP: 993 SSL, POP3: 995 SSL)
- OAuth2 required but basic auth configured (Gmail, O365 changed policies)
- App-specific password needed (2FA enabled accounts)
- Firewall blocking outbound email ports from Pega server
- SSL certificate not trusted by Pega's JVM truststore

**Debug Steps**:
1. Test email connectivity outside Pega (telnet, openssl s_client)
2. Check if provider requires OAuth2 (Google, Microsoft 365)
3. Verify SSL certificate: `openssl s_client -connect mail.server:993`
4. Check Pega logs for javax.mail exceptions
5. Try with a test email account first

### 2. Emails Not Being Processed
**Symptoms**: Emails arrive in inbox but no cases created
**Root Causes**:
- Email Listener agent is not running
- Service Email rule has errors or wrong mapping
- Email filter/selector excludes the emails (e.g., subject filter)
- Email already marked as read (IMAP) — listener only processes unread
- Attachment size exceeds limit

**Fix**:
1. Check Agent Schedule for email listener agent
2. Verify Service Email rule processes the email format correctly
3. Review email filters in the listener configuration
4. Send a fresh test email (don't reuse already-read emails)
5. Check email account directly — are emails being moved/deleted by another client?

### 3. Email Parsing Failures
**Symptoms**: Case created but data fields are empty or wrong
**Root Causes**:
- HTML email body not being parsed correctly (expecting plain text)
- Email template changed — regex/parsing rules outdated
- Multipart MIME email not handled (text + HTML + attachments)
- Character encoding issues (international characters garbled)
- Inline images vs attachments confusion

**Fix**:
- Use `pyEmailBody` (plain text) or `pyEmailHTMLBody` (HTML) appropriately
- Handle both multipart and simple message formats
- Use regex with generous matching for varying email formats
- Explicitly set character encoding in parsing
- Test with emails from different clients (Outlook, Gmail, mobile)

### 4. Duplicate Cases from Same Email
**Symptoms**: Multiple cases created for one email
**Root Causes**:
- Email Listener running on multiple nodes without coordination
- Email not being marked as processed after handling
- POP3 protocol re-downloading (doesn't support server-side flags like IMAP)
- Error during processing causes retry

**Fix**:
1. Use IMAP instead of POP3 (supports read/flagged status)
2. Configure listener to run on single node only
3. Mark email as read/flagged after successful processing
4. Implement deduplication using Message-ID header
5. Set appropriate error handling to prevent infinite retry

### 5. Attachment Handling Issues
**Error**: `Attachment too large` or attachments missing from case
**Root Causes**:
- Attachment size exceeds Pega's configured limit
- Attachment type not allowed (security filter)
- Inline attachments (CID: references) not extracted
- Total email size exceeds processing limit

**Fix**:
1. Check Dynamic System Settings for max attachment size
2. Review allowed attachment types in security settings
3. Handle inline attachments separately from regular attachments
4. For large attachments, consider storing in external system and linking

## Email Listener Best Practices
1. Use IMAP over POP3 for better state management
2. Implement OAuth2 for Google/Microsoft accounts
3. Create dedicated email account (don't use personal/shared mailbox)
4. Set up error notification for listener failures
5. Implement email triage rules for routing to correct case type
6. Handle bounced/auto-reply emails to prevent infinite loops
7. Archive processed emails instead of deleting
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # SEARCH & REPORTING — Elasticsearch, Report Definition, SQL issues
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/search/search-reporting-errors.html",
        "title": "Search and Reporting — Elasticsearch, Reports, and Troubleshooting",
        "content": """# Search and Reporting — Troubleshooting

## Overview
Pega uses two search/reporting mechanisms:
1. **Full-text search (Elasticsearch/OpenSearch)**: Powers the search bar, work object search, and search landing pages
2. **Report Definition / List views**: SQL-based reporting against the PegaRULES/PegaDATA database

## Elasticsearch / OpenSearch Issues

### 1. Search Returns No Results
**Symptoms**: Search bar returns nothing, "No results found" for known work objects
**Root Causes**:
- Search index is not built or is corrupt
- Elasticsearch service is not running
- Index queue is backed up (new items not yet indexed)
- Search permissions — user doesn't have access to the class being searched

**Debug Steps**:
1. Admin Studio → System → Search → Check index status
2. Verify Elasticsearch is running: check system health in SMA
3. Check search index queue depth (high queue = indexing backlog)
4. Run "Rebuild search index" from Admin Studio
5. Verify the work object's class is included in the search configuration

### 2. Search Index Build Failure
**Error**: `SearchIndexBuildFailure` or `ElasticsearchException`
**Root Causes**:
- Insufficient disk space on Elasticsearch data directory
- Elasticsearch heap memory exhausted (default is often too low)
- Too many fields in the index (mapping explosion)
- Network partition between Pega and Elasticsearch nodes
- Corrupt index segments

**Fix**:
1. Check Elasticsearch logs for specific errors
2. Increase ES_JAVA_OPTS heap size (e.g., `-Xms2g -Xmx2g`)
3. Free disk space or add storage to ES data directory
4. If index is corrupt: delete and rebuild from Admin Studio
5. Check field mapping count — reduce if near the limit (default: 1000)

### 3. Stale Search Results
**Symptoms**: Recently created/updated cases don't appear in search
**Root Causes**:
- Index queue processing is slow or stuck
- Elasticsearch refresh interval is too long
- Data was updated directly in DB (bypassing Pega indexing)
- Near real-time search not enabled

**Fix**:
1. Check search queue depth in Admin Studio
2. Trigger manual index refresh if urgent
3. Rebuild index if data was modified outside Pega
4. Increase indexing thread count if queue is consistently deep

### 4. Elasticsearch Cluster Health Yellow/Red
**Yellow**: At least one replica shard is unassigned (data safe but not replicated)
**Red**: At least one primary shard is unassigned (data potentially unavailable)

**Debug Steps**:
1. Check `_cluster/health` API for unassigned shards
2. Check `_cat/shards?v` for shard status details
3. Common causes: disk watermark exceeded, node down, corrupt shard
4. Fix: add storage, restart failed nodes, or reroute shards

## Report Definition Issues

### 5. Report Returns Wrong Data
**Symptoms**: Report shows unexpected rows, missing data, or duplicate records
**Root Causes**:
- Filter conditions are wrong or missing (especially access group / work pool filters)
- Join configuration incorrect (wrong key mapping)
- Class mapping to wrong database table
- Optimized queries enabled but returning stale cached results
- Missing WHERE clause for resolved/deleted cases

**Fix**:
1. Open Report Definition → SQL tab → examine generated SQL
2. Verify filter conditions match expected criteria
3. Check class-to-table mapping in Data Admin → Database
4. Clear report cache if using optimized queries
5. Test the generated SQL directly in database tool (SQL Developer, pgAdmin)

### 6. Report Performance — Slow Queries
**Symptoms**: Reports take 30+ seconds, timeout, or cause database CPU spikes
**Root Causes**:
- Missing database indexes on filtered/sorted columns
- Full table scan on large tables (pc_work, pc_history)
- Too many joins in report definition
- BLOB/CLOB columns included unnecessarily
- No pagination (loading all 100K+ rows)

**Fix**:
1. Check database query plan (EXPLAIN/EXPLAIN ANALYZE)
2. Add indexes on frequently filtered columns (pxCreateDateTime, pyStatusWork, pyAssignmentStatus)
3. Use database views for complex reports
4. Enable report pagination (avoid "get all rows")
5. Consider Pega's "Optimize" feature for frequently-run reports
6. Move historical data to separate reporting database

### 7. Report Definition Compile Error
**Error**: `Report definition failed to compile` or SQL errors
**Root Causes**:
- Property doesn't exist or has wrong type
- Column name exceeds database identifier limit
- Reserved word used as property/column name
- Database-specific SQL syntax issue (Oracle vs PostgreSQL vs SQL Server)

**Fix**:
1. Check the error details in the report compilation message
2. Verify all properties exist on the class
3. Check column mappings in the class's database table
4. Test generated SQL in the database directly
5. Check for database-specific reserved words

### 8. Declare Index Not Working
**Symptoms**: Declare Index rule exists but queries don't use it
**Root Causes**:
- Declare Index not enabled or not built
- Query pattern doesn't match the index definition
- Index is defined on wrong class
- Database table doesn't have corresponding database index

**Fix**:
1. Verify Declare Index is enabled and assigned to correct class
2. Rebuild indexes from Admin Studio
3. Check that the query pattern matches what the Declare Index provides
4. Verify corresponding database index exists using DBA tools

## Search & Reporting Best Practices
1. Rebuild search index after major data migrations
2. Monitor Elasticsearch cluster health daily
3. Add database indexes for frequently-used report filters
4. Use paginated reports — never "get all"
5. Schedule heavy reports for off-peak hours
6. Use Declare Indexes for frequently queried properties
7. Monitor report performance with PAL (Performance Analyzer)
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # VERSION-SPECIFIC — 8.x vs Infinity '23 vs '24 migration issues
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/migration/version-migration-guide.html",
        "title": "Pega Version Migration — 8.x to Infinity '23/'24 Common Issues",
        "content": """# Pega Version Migration — Common Issues and Breaking Changes

## Overview
Migrating between major Pega versions (8.x → Infinity '23 → Infinity '24) introduces breaking changes, deprecated features, and new patterns. This guide covers the most common issues encountered during upgrades.

## Version Naming Clarification
- **Pega 8.1 - 8.8**: Traditional version numbering
- **Pega Infinity '23**: Equivalent to Pega 8.8.x (rebranded)
- **Pega Infinity '24**: Next major release after '23

## Common Migration Issues: 8.x → Infinity '23

### 1. Constellation UI Breaking Changes
**Issue**: Custom UI sections don't render after upgrade
**Root Cause**: Infinity '23 pushes Constellation (React-based UI) as default. Traditional UI (Section-based) still works but may need configuration.
**Symptoms**:
- Blank screens where custom sections used to render
- JavaScript errors in browser console referencing Constellation components
- Styling/CSS mismatches

**Fix**:
1. Check if the application is set to use Constellation or Traditional UI
2. In Application rule → set "UI Architecture" to "Traditional" if not ready for Constellation
3. For Constellation migration: convert sections to views using the Pega conversion tool
4. Custom JavaScript/CSS in sections won't work in Constellation — rewrite as DX Components

### 2. Security Policy Changes
**Issue**: Users locked out or authentication failing after upgrade
**Root Cause**: Infinity '23 enforces stricter security defaults:
- Password complexity requirements increased
- Session timeout defaults changed
- OAuth2/OIDC configuration requirements updated
- CORS policies more restrictive

**Fix**:
1. Review Security → Authentication policies for changed defaults
2. Update OAuth2 configurations to match new requirements
3. Check CORS allowed origins — update for any new domains/ports
4. Reset affected user passwords if complexity requirements changed
5. Review session timeout settings in prconfig.xml

### 3. Deprecated Java API Calls
**Issue**: Custom Java steps or functions fail with `NoSuchMethodError`
**Root Cause**: Several internal Java APIs deprecated in 8.6+ and removed in '23:
- `ClipboardPage.putString()` replaced with `ClipboardPage.putStringValue()`
- Direct JDBC calls via `PegaHandle` replaced with Connect SQL rules
- Some `PublicAPI` methods removed

**Fix**:
1. Run the Pega Upgrade Pre-check tool to identify deprecated API usage
2. Search custom Java code for deprecated method calls
3. Replace with current API equivalents (see Pega API reference for version)
4. Recompile all custom Java after fixing

### 4. Rule Resolution Changes
**Issue**: Different rule version being picked up after upgrade
**Root Cause**: Infinity '23 changed rule resolution algorithm for better performance, but this can surface previously-masked rule conflicts.
**Symptoms**:
- Different behavior in flows/activities than before upgrade
- "Rule not found" for rules that existed before
- Wrong rule version being used (circumstanced rule issues)

**Fix**:
1. Use the Rule Resolution inspector (Dev Studio → rule form → Other Actions → View Rule Resolution)
2. Check for duplicate rules across rulesets
3. Verify ruleset stack order in the application
4. Review circumstanced rules — ensure they're properly scoped

### 5. Database Schema Changes
**Issue**: Custom SQL or reports broken after upgrade
**Root Cause**: Pega schema updates rename/add/remove columns in system tables during upgrade. Custom SQL referencing internal columns may break.

**Fix**:
1. Review Pega upgrade logs for schema change details
2. Update custom SQL to use new column names
3. Use Report Definition (which abstracts from physical schema) instead of raw SQL
4. Re-run Declare Index builds after schema changes

## Common Migration Issues: Infinity '23 → Infinity '24

### 6. Constellation Enforcement
**Issue**: Traditional UI deprecated warnings become errors in some contexts
**Root Cause**: Infinity '24 further pushes Constellation adoption, with some new features ONLY available in Constellation.

**Fix**:
1. Plan Constellation migration for any new development
2. Existing Traditional UI still works but won't get new features
3. Use the Pega View Conversion utility to batch-convert sections to views
4. Prioritize conversion of customer-facing portals first

### 7. Process AI / Decision Hub Changes
**Issue**: Decision strategies behaving differently after upgrade
**Root Cause**: AI/ML model deployment pipeline changed in '24, with new default model formats and scoring methods.

**Fix**:
1. Retrain and redeploy ML models using new pipeline
2. Check Decision Strategy components for deprecated nodes
3. Verify prediction studio configurations after upgrade
4. Test all NBA (Next-Best-Action) flows end-to-end

### 8. Cloud-Native Features
**Issue**: Features that assume cloud deployment don't work on-premises
**Root Cause**: Infinity '24 adds features designed for Pega Cloud that require specific infrastructure (e.g., Kubernetes, managed services).

**Workaround**:
1. Review release notes for "Cloud only" features
2. For on-premises: check if equivalent functionality is available
3. Plan cloud migration if critical features are cloud-only
4. Contact Pega support for on-premises alternatives

## Pre-Migration Checklist
1. Run Pega Pre-Upgrade Assessment tool
2. Review all custom Java code for deprecated APIs
3. Document all custom SQL and raw database access
4. Test all integrations (REST, SOAP, MQ, file) in staging
5. Verify authentication/SSO flows work with new security defaults
6. Back up production database and application export (RAP) before upgrade
7. Plan for Constellation UI migration (even if deferred)
8. Test all reports and dashboards after schema changes
9. Verify third-party jar compatibility with new Pega version
10. Run full regression test suite after upgrade

## Upgrade Troubleshooting Tips
- Always check UPGRADE.log and UPGRADETOOLS.log for errors
- Enable DEBUG logging for specific packages during upgrade testing
- Keep the previous version's documentation handy for comparison
- Use Pega's compatibility matrix for supported database/JDK/app server versions
- Test upgrade on a copy of production data first (never upgrade production first)
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/constellation/constellation-migration.html",
        "title": "Constellation UI Migration — Traditional to Constellation Conversion",
        "content": """# Constellation UI Migration — Troubleshooting

## Overview
Constellation is Pega's React-based UI framework replacing Traditional (Section/Harness) UI. Migration from Traditional to Constellation involves converting sections to views, replacing custom JavaScript with DX Components, and adapting to a new rendering architecture.

## Key Differences
| Aspect | Traditional UI | Constellation |
|--------|---------------|---------------|
| Technology | Server-rendered HTML (JSP) | Client-rendered React |
| Customization | Custom sections + CSS/JS | DX Components (React) |
| Layouts | Section layouts (dynamic, column, repeating grid) | Constellation design templates |
| Styling | Direct CSS, pxButton, pega-rich-text | Constellation design system (limited custom CSS) |
| JavaScript | Inline JS, onload/onchange handlers | DX Component API only |
| Offline | Not supported | Supported in some configurations |

## Common Migration Errors

### 1. Blank Screen After Switching to Constellation
**Symptoms**: White page, no content rendering
**Root Causes**:
- Application not configured for Constellation (missing Constellation template)
- Custom CSS/JS blocking React rendering
- Incompatible browser (Constellation requires modern browsers)
- CDN/asset loading failure

**Debug Steps**:
1. Open browser Developer Tools → Console for JavaScript errors
2. Check Network tab for failed asset loads (constellation-core.js, etc.)
3. Verify Application rule → UI Architecture setting
4. Check if Constellation packages are installed in the environment
5. Clear browser cache and try incognito mode

### 2. Custom JavaScript Not Working
**Issue**: Inline JavaScript handlers (pxOnChange, custom buttons) do nothing
**Root Cause**: Constellation doesn't support inline JavaScript in sections. All JS must be written as DX Components.

**Fix**:
1. Identify all custom JavaScript in sections (search for `<script>` tags, `pxOnChange`, `pxOnClick`)
2. Rewrite as DX Components following the Constellation Component SDK
3. Register DX Components in the component manifest
4. Test thoroughly — lifecycle is different (React vs page reload)

### 3. Repeating Dynamic Layout Not Rendering
**Issue**: Dynamic layouts inside repeating grids show wrong data or collapse
**Root Cause**: Constellation handles dynamic layouts differently — visibility conditions and refresh mechanisms changed.

**Fix**:
1. Convert dynamic layouts to Constellation Region components
2. Replace visibility conditions with "When" rules that return proper boolean
3. Use Constellation's built-in conditional display instead of custom dynamic logic
4. Test with multiple rows to ensure proper data binding

### 4. Custom Styling Broken
**Issue**: CSS overrides not applying, layout looks different
**Root Cause**: Constellation uses a design system with scoped CSS. Global CSS overrides are deliberately blocked.

**Fix**:
1. Use Constellation's theming/branding features for global styles
2. For component-level styling: use DX Component CSS modules
3. Remove all global CSS overrides from custom sections
4. Use Constellation's design tokens for colors, spacing, typography
5. Accept that pixel-perfect replication of old UI may not be possible

### 5. Data Page Refresh Behavior Changed
**Issue**: Data pages not refreshing when expected in Constellation views
**Root Cause**: Constellation uses a different data lifecycle — React component mounting/unmounting vs page load/refresh.

**Fix**:
1. Understand Constellation's data page refresh triggers
2. Use "Refresh when" strategies instead of manual refresh calls
3. Implement proper React state management in DX Components
4. Test data freshness in various navigation scenarios

## Migration Strategy
1. **Assess**: Use Pega's assessment tool to identify conversion effort per section
2. **Prioritize**: Start with simple screens, defer complex custom UI
3. **Convert incrementally**: Mix Traditional and Constellation views during migration
4. **Test**: Each converted view needs full functional testing
5. **Iterate**: Don't try to convert everything at once — phased approach works best

## DX Component Development Tips
1. Use the Constellation Component SDK (installable via npm)
2. Follow React best practices — functional components with hooks
3. Test components locally with Storybook before deploying
4. Handle all Pega property types (text, date, boolean, page, pagelist)
5. Implement proper error boundaries in React components
6. Follow Constellation design guidelines for consistent UX
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/troubleshooting/common-pega-errors-quickref-2.html",
        "title": "Common Pega Errors Quick Reference — Part 2 (Integration & Performance)",
        "content": """# Common Pega Errors Quick Reference — Part 2

## Integration Errors

### REST Connector: HTTP 401 Unauthorized
**Cause**: Authentication credentials wrong or expired
**Fix**: Check connector auth profile. If OAuth2: verify token endpoint, client ID/secret, and grant type. Regenerate tokens if expired.

### REST Connector: HTTP 403 Forbidden
**Cause**: Authenticated but not authorized for the resource
**Fix**: Check API permissions/scopes. Verify the service account has required roles on the target system.

### REST Connector: HTTP 429 Too Many Requests
**Cause**: Rate limit exceeded on the target API
**Fix**: Implement rate limiting in Pega (use queue or throttle pattern). Add exponential backoff retry. Check target API's rate limit documentation.

### REST Connector: SSL Handshake Failure
**Cause**: Certificate not trusted by Pega's JVM truststore
**Fix**: Import the target server's SSL certificate into Pega's cacerts keystore: `keytool -import -trustcacerts -keystore cacerts -alias target_api -file target_cert.cer`

### SOAP Connector: "Could not find WSDL"
**Cause**: WSDL URL unreachable or changed
**Fix**: Verify WSDL URL is accessible from Pega server. Re-import WSDL if endpoint changed. Check if WSDL requires authentication.

### Connect SQL: "ORA-01000: maximum open cursors exceeded"
**Cause**: Too many open database cursors (Oracle)
**Fix**: Check for cursor leaks in custom Java. Increase OPEN_CURSORS parameter. Ensure Connect SQL rules close ResultSets properly. Review Activities for unclosed cursors in loops.

### Connect SQL: "Connection pool exhausted"
**Cause**: All database connections in use, none available
**Fix**: Increase pool size. Check for long-running queries hogging connections. Look for transaction leaks (Commit/Rollback missing). Monitor active connections with database tools.

## Performance Errors

### java.lang.OutOfMemoryError: Java heap space
**Cause**: JVM heap exhausted — too many objects in memory
**Fix**:
1. Check for clipboard bloat (large page lists, uncleaned data pages)
2. Review data page scope (Thread vs Requestor vs Node)
3. Increase JVM heap (-Xmx) as temporary measure
4. Use PAL to identify memory-heavy operations
5. Check for memory leaks in custom Java code

### java.lang.OutOfMemoryError: GC overhead limit exceeded
**Cause**: JVM spending >98% time in garbage collection
**Fix**: Same as heap space + check for excessive object creation in loops. Use GC logging to identify memory pressure patterns. Consider switching GC algorithm (G1GC recommended for Pega).

### StackOverflowError in Activity/Flow
**Cause**: Infinite recursion — activity/flow calling itself
**Fix**: Check for circular references: Activity A → Activity B → Activity A. Review Declare Expression triggers for cascade loops. Check flow transitions for back-loops without exit conditions.

### Database Deadlock Detected
**Error**: `ORA-00060: deadlock detected` or equivalent
**Cause**: Two transactions waiting for each other's locks
**Fix**:
1. Identify the deadlocked transactions from database logs
2. Review the involved activities/flows for lock ordering
3. Minimize transaction scope (commit early, commit often)
4. Avoid holding locks during user interaction
5. Use optimistic locking where possible

### Thread Pool Exhaustion
**Symptoms**: System becomes unresponsive, new requests queued
**Cause**: All worker threads busy with long-running operations
**Fix**:
1. Identify long-running requests (thread dumps, PAL)
2. Move long operations to background processing (Queue Processor, Agent)
3. Increase thread pool size as temporary measure
4. Set appropriate timeouts on external calls
5. Implement circuit breaker pattern for failing external services

### High CPU Usage
**Cause**: Often caused by: inefficient Declare Expressions, report with full table scan, regex backtracking, or tight loop in Activity
**Fix**:
1. Take thread dumps at intervals to identify hot threads
2. Check running reports for full table scans
3. Review Declare Expressions for unnecessary triggers
4. Profile custom Java code
5. Check for runaway agents or queue processors

## Data Errors

### "Property not found on clipboard"
**Cause**: Referencing a property that doesn't exist on the page
**Fix**: Check property name spelling (case-sensitive). Verify the page exists and is the right class. Use `Obj-Validate` to ensure page is properly populated before access.

### "Invalid date format" / "Date parse exception"
**Cause**: Date string doesn't match expected format
**Fix**: Check date property format (Pega default: yyyyMMdd'T'HHmmss.SSS GMT). Use `@DateTimeString` function for format conversion. Verify timezone handling between systems.

### "Numeric overflow" or "Value too large for column"
**Cause**: Number exceeds database column capacity
**Fix**: Check property type definition (Integer vs Decimal vs Double). Verify database column type and precision. Add validation rule to catch values before save.

### Clipboard Corruption / "Inconsistent page data"
**Cause**: Concurrent modification of clipboard pages (thread safety issue)
**Fix**:
1. Don't share clipboard pages across requestors
2. Use Thread-scoped data pages for thread-specific data
3. Synchronize access to shared resources
4. Avoid storing state in Node-level data pages that gets modified
"""
    },
]


def seed_phase3b():
    """Write Phase 3B curated docs to raw_docs directory."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc in CURATED_DOCS_PHASE3B:
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
        filename = f"phase3b_{slug}.json"
        filepath = RAW_DOCS_DIR / filename

        payload = {
            "url": doc["url"],
            "title": doc["title"],
            "content": doc["content"].strip(),
        }
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE3B)}] Saved: {doc['title']}")

    logger.info(f"\nPhase 3B complete — {count} documents saved to {RAW_DOCS_DIR}")
    logger.info("Next: python -m indexer.index_docs")


if __name__ == "__main__":
    seed_phase3b()
