"""
Curated Pega Knowledge Base — Phase 11 (DevOps, Deployment & Production Operations)
Run: python -m crawler.seed_kb_phase11
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE11 = [
    {
        "title": "Pega Deployment Manager — Complete Guide",
        "url": "https://docs.pega.com/deployment-manager",
        "content": """
# Pega Deployment Manager — Complete Guide

## Overview
Deployment Manager is Pega's enterprise deployment solution for managing application releases across environments. It enables version control, change tracking, and orchestrated rollouts with minimal downtime.

### Core Concepts
- **Deployment Pipeline**: Multi-stage deployment sequence (dev → QA → staging → prod)
- **Application Package (RAP)**: Versioned rule archive containing all rules for a release
- **Deployment Slot**: Named deployment target (e.g., "Production-US", "DR-Europe")
- **Deployment Plan**: Blueprint defining deployment sequence, rollback rules, and approval gates

## Creating Deployment Pipelines

### Step 1: Define Pipeline Stages
```
Dev → QA (automated tests) → Staging (UAT) → Production
```
- **Dev Stage**: Continuous deployment on commit
- **QA**: 2-hour regression suite before promotion
- **Staging**: Full production replica for 48-hour soak test
- **Prod**: Manual approval + canary deployment to 10% of nodes first

### Step 2: Configure Deployment Slots
Access **Deployment Manager → Slots**:
- Slot Name: Production-US-East
- Environment: Production
- Node Count: 5 nodes
- Rollback Window: 1 hour
- Max Concurrent Updates: 2 nodes/slot

### Step 3: Set Approval Gates
- Stage gate requires sign-off from Release Manager
- If gate fails → deployment blocked, alert Slack channel
- Approval SLA: 4 hours (escalate to VP Ops)

## Application Packages (RAP Files)

### Creating RAP Files
1. **Migrate → Tools → Create Distribution**
2. Select rules to package (all custom rules auto-included)
3. Specify version: `v8.2.1-hotfix-3`
4. Generate checksums (validate integrity in target env)
5. Export RAP: `MyApp-8.2.1.rap` (~200MB typical)

### RAP Contents
- All rule definitions (rules, data objects, processes)
- Localization resources (multi-language support)
- Static resources (images, stylesheets)
- Database schema migrations (DDL scripts)
- Baseline configuration (database name, class mappings)

## Rollback Strategies

### Point-in-Time Rollback
**Trigger**: If >10 critical errors post-deploy
```
SMA → Deployment Manager → Current Release → Rollback
Restores previous RAP version + database state from pre-deployment snapshot
Time: 5-15 minutes per environment
```

### Zero-Copy Rollback (PegaRULES Strategy)
- Maintain 2 rule bases in parallel (Blue/Green)
- Switch traffic via configuration flag (instant)
- Preferred method for high-availability systems

### Database Rollback
- Pre-deployment snapshot (DMZ backup) → 5GB per prod environment
- Rollback via SQL script: `rollback-schema-v8.2.0-to-v8.1.9.sql`
- Test rollback in staging first (never in prod blind)

## Deployment Best Practices

### Pre-Deployment Checklist
- ✓ Verify RAP version matches release notes
- ✓ Run integration test suite (pass rate >98%)
- ✓ Validate database upgrade DDL in staging (zero errors)
- ✓ Check disk space (minimum 15GB free)
- ✓ Confirm backups completed and tested
- ✓ Notify support team 2 hours before deployment
- ✓ Disable external integrations if API changes present

### During Deployment
- **1st node**: Monitor logs for 5 min, check SMA health
- **2-4 nodes**: Staggered deployment (1 node per 5 min)
- **Last nodes**: Deploy only if first nodes >10 min healthy

### Post-Deployment Validation
- Smoke tests: Login, search, rule execution
- Business KPI check: Transaction volume, error rate
- Load test: 10% above peak traffic (stress test for 15 min)
- Monitoring: Alert thresholds reduced by 50% for 1 hour

## Common Deployment Errors & Fixes

### Error: "Invalid Merge Strategy — Duplicate Rule Definition"
**Cause**: RAP imports rule that exists in target environment with conflicting changes
**Fix**:
1. Review rule diff: `Developer Studio → Rule Diff Report`
2. Choose: Overlay (use RAP version) or Merge (manual resolution)
3. Re-export RAP with conflict marker resolved

### Error: "Insufficient Disk Space — Cannot Extract RAP"
**Cause**: RAP extraction temp files require 3× RAP size
**Fix**:
- Check disk: `df -h /pega/rules` (need 600GB for 200MB RAP)
- Stop app servers, purge old RAP files: `rm /pega/archive/*.old`
- Extend volume if necessary

### Error: "Database Schema Mismatch — DDL Rollforward Failed"
**Cause**: Schema upgrade script incompatible with existing data
**Fix**:
1. Export baseline schema from current environment
2. Test upgrade script: `sqlplus > @upgrade-schema.sql` (staging)
3. Add data migration: `UPDATE pr_data SET field='value' WHERE condition`
4. Re-test full UAT scenario

### Error: "Rule Audit Failure — Insufficient Permissions"
**Cause**: RAP import user lacks privileges for locked rules
**Fix**:
- Grant: System Admin role + Debug rule privilege
- Or: Package only rules in custom application (avoid framework rules)

## Deployment Monitoring

### Key Metrics
- **Deployment Duration**: 15-30 min per node (flag >45 min)
- **Post-Deployment Errors**: <0.1% error rate in logs
- **User Session Recovery**: >95% sessions persist post-deploy
- **Rollback Frequency**: <5% of all deployments

### Real-Time Monitoring
- SMA → Node Status: All nodes reporting "Active"
- Alert Log: Zero "Deployment" or "Import" errors
- GC Logs: <20 sec pause (full GC), <2 sec (minor GC)
        """
    },
    {
        "title": "Application Packaging — RAP/ZIP Export & Import",
        "url": "https://docs.pega.com/application-packaging",
        "content": """
# Application Packaging — RAP/ZIP Export & Import

## Rule Archives (RAP) Fundamentals

### What is a RAP?
A RAP (Rule Archive Package) is a versioned snapshot of rules, configuration, and metadata. It's the deployment unit in Pega.

**RAP Structure**:
```
MyApp-8.2.1.rap
├── prod_rules/
│   ├── rules.prpc (serialized rule definitions)
│   └── rule-checksums.xml
├── metadata/
│   ├── migration-scripts/
│   └── config-map.xml
├── resources/
│   ├── images/
│   └── stylesheets/
└── manifest.xml (version, build timestamp, dependencies)
```

### RAP vs ZIP Export
- **RAP**: Binary format, checksums, optimized for deployment, prod-grade
- **ZIP**: Text format (for version control), human-readable, for development sharing

## Creating Rule Archives (RAP)

### Method 1: Developer Studio GUI
1. **Migrate → Tools → Create Distribution**
2. Select rules by category:
   - Custom rules (recommended: all)
   - Framework rules (rarely needed)
   - Specific application classes (e.g., `MyApp-*`)
3. Configure export:
   - Version: `8.2.1-hotfix-3`
   - Include ancestors: Yes (base classes)
   - Product rules: Yes
   - Database objects: Yes (DDL scripts)
4. Click **Package** → RAP file generated

### Method 2: Command-Line (prsysutil)
```bash
prsysutil.sh -pzgfexportrule \
  -append \
  -file MyApp-8.2.1.rap \
  -class "MyApp-.*" \
  -selectByLabel "Production Release"
```

### Method 3: Product Rules Export
1. **Configure → Application → Product Rules**
2. Select package: `MyApp-ProductRules`
3. Set version: `8.2.1`
4. Export as RAP (includes dependent classes)

## Product Rules Management

### What Are Product Rules?
Sealed rules (read-only) that define system behavior. Updates come via RAP imports.

**Product Rules Examples**:
- Flow definitions (workflows)
- Data transforms (integrations)
- Keyed properties (configurations)
- Connector rules (API integrations)

### Managing Product Rules in RAP
- **Lock Strategy**: Always lock product rules before export
- **Version Control**: Product rules versioned with parent RAP
- **Inheritance**: Product rules inherit from framework, can't be overridden locally

### Creating Product Rules Package
1. **Configure → Distribution → New Product Rules**
2. Name: `MyApp-ProductRules`
3. Base class: `MyApp`
4. Include rules (select flow, transforms, etc.)
5. Mark as "Sealed" → cannot modify in target environment

## Export Process

### Step-by-Step Export
1. **Create RAP with checksums**:
   - Checksums validate integrity across network
   - Detect corruption: `md5sum MyApp-8.2.1.rap`

2. **Verify rule list**:
   - Export report: `rules-in-package.csv` (5000+ rules typical)
   - Cross-check with release notes

3. **Test export in staging**:
   - Import RAP to staging environment first
   - Run smoke test: Login, execute critical flows

4. **Archive RAP with metadata**:
   - Store RAP + manifest + checksums together
   - Document export timestamp, exported-by user

### Pre-Export Validation
```
Developer Studio → Validate Application
- Rule hierarchy consistency
- Missing rule dependencies
- Class structure errors
- Data model schema compliance
```

## Import Process

### Basic Import Flow
1. **SMA → Deployment Manager → Import Application**
2. Select RAP file: `MyApp-8.2.1.rap`
3. Choose merge strategy (see next section)
4. Configure database upgrade:
   - Auto-apply DDL: Yes
   - Validate schema changes: Yes
5. Click **Import** → monitor progress

### Import Options
- **Confirm imports**: Require manual approval per rule
- **Skip identical rules**: Skip if rule unchanged from last import
- **Update database baseline**: Sync schema to new version
- **Preserve local changes**: Keep locally modified rules (manual merge required)

## Merge vs Overlay

### Overlay Strategy (Default)
**Rule in RAP replaces rule in target environment completely**
- Simpler, faster
- Loses local modifications (if any)
- Use for: Fresh deployments, strict version control

**Process**:
```
RAP rule version 8.2.1 → Replace target environment rule
Target modifications (if any) → LOST
```

### Merge Strategy
**Compare RAP rule and target rule, combine changes intelligently**
- Preserves local customizations
- Complex: Requires conflict resolution
- Use for: Incremental deployments, preserving local patches

**Process**:
```
Compare 3-way:
1. Original rule (from prior RAP)
2. RAP rule (new changes from dev)
3. Target rule (local mods, potentially)
→ Merge engine combines non-conflicting changes
→ Flag conflicts for manual review
```

## Handling Conflicts During Import

### Conflict Scenarios
1. **Rule modified in RAP AND target environment**
2. **Data object schema changed incompatibly**
3. **Dependent rule missing in target**

### Conflict Resolution
**Option A: Accept RAP Version**
- Use rule from RAP, discard local changes
- Risk: Lose customizations
- Use if: Local changes are temporary/testing

**Option B: Accept Target Version**
- Keep target rule, reject RAP changes
- Risk: Miss bug fixes from RAP
- Use if: Target rule has critical local patches

**Option C: Manual Merge**
1. **Compare via Rule Diff**:
   - RAP version (left) vs Target (right)
   - Highlight conflicting sections
2. **Edit target rule manually**:
   - Incorporate RAP changes + local customizations
   - Test merged rule in developer instance
3. **Confirm merge** → rule imported

## Schema Updates During Import

### Automatic DDL Application
RAP includes SQL scripts for schema changes:
```sql
-- MyApp schema upgrade v8.2.0 → v8.2.1
ALTER TABLE pr_data ADD COLUMN new_field VARCHAR(50);
ALTER TABLE pc_work ADD INDEX idx_status (pxCreateDateTime);
```

### Pre-Import Schema Validation
1. **Backup production database** (full backup before import)
2. **Test DDL in staging** (run exact script in staging first)
3. **Estimate duration**: Large table alterations (>10M rows) may take hours
4. **Plan maintenance window**: DDL can lock tables briefly

### Common Schema Issues
- **Incompatible data type**: VARCHAR → INT on column with text data
- **Foreign key constraint violation**: New constraint conflicts with existing data
- **Index lock timeout**: Large table index creation blocks queries

**Fix**:
- Add WHERE clause to DDL: `ALTER TABLE ... WHERE 1=0` (create structure only)
- Use online DDL (MySQL 5.7+): `ALGORITHM=INPLACE`
- Split large DDL into batches

## Debugging Import Failures

### Error: "Rule Import Failed — Checksum Mismatch"
**Cause**: RAP corrupted during transfer or storage
**Debug**:
1. Verify RAP integrity: `md5sum MyApp-8.2.1.rap` (compare with export manifest)
2. Re-download RAP from archive (if available)
3. Check filesystem: `fsck /pega/archive` (verify disk health)

### Error: "Class Inheritance Broken — Missing Parent Class"
**Cause**: Parent class not included in RAP
**Debug**:
1. Identify missing class: `grep "Class-Name" MyApp-8.2.1.rap`
2. Add parent class to RAP export
3. Re-create RAP with full inheritance chain

### Error: "Import Blocked — Insufficient Disk Space"
**Cause**: Extraction needs 3× RAP size
**Debug**:
```bash
df -h /pega/rules  # Should be >600GB free
du -sh /pega/archive  # Purge old RAPs if needed
rm /pega/archive/MyApp-8.0.0.rap  # Remove old versions
```

### Error: "Data Migration Failed — Type Conversion Error"
**Cause**: DDL changes data type, existing data incompatible
**Debug**:
1. Query data before migration: `SELECT COUNT(*) FROM pr_data WHERE field LIKE '%ABC%'`
2. Create migration script: `UPDATE pr_data SET field = CAST(field AS INT) WHERE numeric_check(field)`
3. Pre-validate migration: Test on staging copy before import
        """
    },
    {
        "title": "Pega Cloud (Pega Cloud Services)",
        "url": "https://docs.pega.com/pega-cloud",
        "content": """
# Pega Cloud (Pega Cloud Services)

## Pega Cloud Architecture Overview

### Deployment Models
**Pega-Managed Cloud**
- Hosted on Pega infrastructure (AWS/Azure)
- Auto-scaling, automatic patching, managed backups
- Best for: SaaS applications, rapid scaling needs
- Cost: Per-user licensing, operational overhead minimal

**BYOC (Bring Your Own Cloud)**
- You own AWS/Azure/GCP infrastructure
- Pega provides management plane only
- Best for: Enterprise customers, compliance needs, cost control
- Cost: Infrastructure costs + Pega licensing

### Cloud Environment Types
```
Sandbox (experimental) → Dev (feature development)
         ↓
    QA/UAT (testing) → Staging (pre-prod) → Production
```

**Environment Specs (Pega-Managed)**:
- **Dev**: 1 app node, 2GB RAM, auto-suspend after 8 hours
- **QA**: 2 app nodes, 4GB each, always-on
- **Staging**: Same as prod spec, dedicated database
- **Prod**: 3+ app nodes, auto-scaling 2-8 nodes, dedicated infrastructure

## My Pega Cloud Portal

### Key Features
**Dashboard**:
- Environment status (healthy/degraded/down)
- Node metrics (CPU, memory, disk)
- Deployment history (last 10 releases)
- Cost breakdown (monthly usage)

**Environment Management**:
- **Scale nodes**: Add/remove app servers (1-10 nodes)
- **Upgrade version**: Schedule major Pega version upgrades
- **Backups**: Manual or scheduled (daily, weekly)
- **Security groups**: Configure firewall rules

### Requesting Deployments
1. **Upload RAP file** to My Pega Cloud portal
2. **Select target environment** (dev/QA/staging/prod)
3. **Configure deployment options**:
   - Deployment time: Immediate or scheduled
   - Merge strategy: Overlay or merge (if supported)
   - Rollback window: 1 hour (default)
4. **Request approval** (routing to Release Manager)
5. **Monitor deployment** (real-time logs, progress bar)

### Deployment Workflow
```
Upload RAP → Select Env → Config → Request Approval
                                      ↓
                            Approved? → Deploy → Monitor
```

## Cloud Environment Configuration

### Environment-Specific Settings
1. **Database Connection**:
   - Dev: Shared test database
   - QA/Staging/Prod: Dedicated databases
   - Failover: Automatic for managed cloud

2. **Scaling Policy**:
   - Dev: Min 1, Max 2 nodes
   - QA: Min 2, Max 4 nodes
   - Prod: Min 3, Max 8 nodes (configurable)

3. **Backup Retention**:
   - Dev: 7-day rolling
   - QA: 30-day rolling
   - Prod: 90-day rolling (industry standard)

### Custom Configuration
- **JDBC connection strings**: Environment-specific datasource
- **External integrations**: API endpoints (dev/prod variants)
- **Email servers**: SMTP relay configuration (prod-only)
- **Security**: TLS 1.2+ enforced, certificate management automated

## Monitoring Cloud Health

### SMA Health Check Page
**Path**: `https://your-cloud-env.pegacloud.com/sma` → Health

**Key Metrics**:
- **Node Status**: All nodes active/warning/failed
- **Database connectivity**: Query response time <200ms
- **Disk usage**: <80% threshold (alert if >85%)
- **GC pause time**: <2 sec minor, <20 sec full
- **Request latency**: p95 <2 sec, p99 <5 sec

### PDC Monitoring
- **Node count**: Actual vs expected
- **Load distribution**: Even distribution across nodes
- **Connection pool**: Active connections <80% max

### Alert Thresholds (Pega-Managed)
- CPU >85%: Scale up (add node)
- Memory >90%: Alert operations team
- Disk space >95%: Archive old logs, compress data
- Error rate >5%: Page on-call engineer

## Common Cloud Issues

### Issue: Deployment Timeout (RAP Import >30 min)
**Cause**: Large RAP (>500MB) or resource contention
**Fix**:
1. **Check node resource**: SMA → Node Status (look for high CPU/memory)
2. **Split RAP**: Create multiple smaller RAPs (by application module)
3. **Retry during off-peak**: Off-hours when load lower
4. **Contact Pega Support**: If consistently >1 hour

### Issue: Database Failover Triggered Unexpectedly
**Cause**: Database connection timeout or primary failure
**Fix**:
1. **Check network**: Verify connectivity primary DB → app node
2. **Review database logs**: Look for OOM kills, crashed processes
3. **Increase connection timeout**: `prconfig.xml`: `fail-fast-timeout 30000`
4. **Contact Pega Support**: If failover happening hourly

### Issue: Production Environment Out of Disk Space
**Cause**: Log files accumulating (weeks of logs)
**Symptom**: New log entries rejected, app functionality degraded
**Fix**:
1. **Emergency**: Request Pega Support for extended volume
2. **Cleanup**: `tar czf audit-logs-archive.tar.gz /pega/logs/pegalogs_*`
3. **Remove old logs**: Keep only last 7 days
4. **Enable log rotation**: In `prconfig.xml`, set max-file-size 200MB

### Issue: Slow Application Performance in Production
**Cause**: CPU throttling (limit of managed environment), inefficient queries
**Debug**:
1. **Check auto-scaling**: SMA → System → Scaling History (verify new nodes added)
2. **Profile database**: Slow query log (>5 sec queries)
3. **Analyze GC**: If GC pause >10 sec, heap too small
4. **Contact Pega Support**: Request node spec increase or performance analysis

## BYOC Considerations

### Network Architecture
- **VPC isolation**: Pega runs in your VPC, not shared
- **Egress control**: You control outbound firewall rules
- **VPN/Peering**: Direct connection to on-premise systems

### Compliance & Security
- **Data residency**: Data stays in your AWS region (GDPR/HIPAA compliant)
- **Encryption**: TLS in transit, KMS encryption at rest
- **Audit logs**: CloudTrail logs available for compliance review

### Cost Management
- **Reserved instances**: Purchase AWS reserved capacity (30-40% discount)
- **Auto-scaling**: Scale down during off-hours to save costs
- **Monitoring**: Analyze monthly usage, right-size infrastructure
        """
    },
    {
        "title": "Log File Analysis & Production Debugging",
        "url": "https://docs.pega.com/log-analysis",
        "content": """
# Log File Analysis & Production Debugging

## Pega Log Files Overview

### Core Log Files

**PegaRULES Log** (`pegalogs_<appserver>.log`)
- Primary application log
- Records all user actions, rule executions, errors
- Size: Grows 500MB-2GB per day in production
- Retention: Keep 7-30 days (rotate automatically)

**Alert Log** (`pegarules_<node>.log`)
- High-level warnings and errors
- PEGA0001-PEGA0099 alert codes
- Size: Much smaller (10-50MB/day)
- Retention: Keep 90 days for audit

**GC Logs** (`gc.log`)
- Java garbage collection events
- Full GC pause times, heap usage
- Critical for performance analysis
- Size: 50-100MB/day

**Custom Logs** (application-specific)
- Business process tracking
- Integration error logs
- Audit trails for compliance

## Understanding Log Levels

### Log Level Hierarchy
```
TRACE (most verbose) → DEBUG → INFO → WARN → ERROR → FATAL (least verbose)
```

**TRACE**: Every variable assignment, method entry/exit
- Use for: Deep debugging in dev environment
- Production: NEVER (kills performance)

**DEBUG**: Detailed execution flow, state changes
- Use for: Troubleshooting issues, feature debugging
- Production: Only during incidents (monitor closely)

**INFO**: Normal operations, milestones
- Use for: Production (expected high volume)
- Sample: "User login successful", "Flow started"

**WARN**: Recoverable errors, deprecated features
- Use for: Monitoring threshold (escalate if >10 WARN/min)
- Example: "Retry #3 for external API call"

**ERROR**: Unrecoverable errors, system failures
- Use for: Immediate escalation (>1 ERROR/min = incident)
- Example: "Database connection failed", "Null pointer exception"

**FATAL**: System crash imminent
- Use for: Immediate page on-call (all hands on deck)
- Example: "Out of memory", "Disk full"

## Searching for Errors

### Quick Error Search (Command-Line)
```bash
# Find all ERRORs in last hour
grep "ERROR" /pega/logs/pegalogs_*.log | tail -100

# Search for specific exception
grep "NullPointerException" /pega/logs/pegalogs_*.log

# Count errors by type
grep "ERROR" /pega/logs/pegalogs_*.log | cut -d' ' -f5 | sort | uniq -c | sort -rn
```

### SMA Log Search
1. **SMA → System → Logs → Search**
2. **Query**: `ERROR AND "login"` (find login-related errors)
3. **Time range**: Last 24 hours
4. **Results**: Paginated, show timestamp + full message

### Advanced Search (ELK Stack)
If logs centralized in Elasticsearch:
```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } },
        { "range": { "timestamp": { "gte": "now-1h" } } }
      ]
    }
  }
}
```

## Log4j2 Configuration

### PegaRULES Configuration File
**Path**: `pega/config/log4j2.xml`

### Key Appenders
```xml
<!-- File Appender (PegaRULES log) -->
<RollingFile name="FileAppender" fileName="pegalogs.log">
  <PatternLayout pattern="%d{ISO8601} [%-5p] %m%n" />
  <Policies>
    <SizeBasedTriggeringPolicy size="100MB" />
    <TimeBasedTriggeringPolicy interval="1" modulate="true" />
  </Policies>
  <DefaultRolloverStrategy max="30" />
</RollingFile>

<!-- Console Appender (for container logging) -->
<Console name="ConsoleAppender" target="SYSTEM_OUT">
  <PatternLayout pattern="%d{HH:mm:ss} %-5p - %m%n" />
</Console>
```

### Custom Log Categories
Add category for specific component:
```xml
<Logger name="com.mycompany.rules.MyIntegration" level="DEBUG" additivity="false">
  <AppenderRef ref="MyIntegrationAppender" />
</Logger>
```

Then log in code:
```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

private static final Logger logger = LogManager.getLogger("com.mycompany.rules.MyIntegration");

logger.debug("Processing transaction {}", transactionId);
logger.error("API returned {}", statusCode, new Exception("Timeout"));
```

### Changing Log Levels at Runtime
1. **SMA → System → Logs → Categories**
2. **Select category**: `com.pega.dsm` (example)
3. **Set level**: DEBUG (temporary, 1-hour window)
4. **Confirm**: Changes take effect immediately (no restart)

## Log Rotation & Retention

### Automatic Rotation
**Size-Based**: 100MB per file → rotate
**Time-Based**: Daily at midnight → rotate
**Max files**: Keep 30 files (configurable)

### Manual Cleanup
```bash
# Archive old logs
tar czf pegalogs-2026-04-01-to-10.tar.gz /pega/logs/pegalogs_*2026-04-0[1-9].log

# Remove logs older than 30 days
find /pega/logs -name "pegalogs_*.log" -mtime +30 -delete
```

## Analyzing Production Issues from Logs

### Scenario 1: User Reports Slow Performance
**Debug steps**:
1. **Find user session**: `grep "user.john.doe" pegalogs.log | head -1`
2. **Extract session ID**: Note timestamp + sessionId
3. **Filter logs to session**: `grep "sessionId=ABC123" pegalogs.log > session.log`
4. **Look for slow operations**: `grep "COMPLETED in.*ms" session.log | grep "[0-9]{5,}"` (>10 sec)
5. **Identify bottleneck**: Database query, external API, rule execution

**Common causes**:
- Database query timeout (>30 sec) → check missing index
- External API timeout → check integration endpoint
- Lock contention → multiple users editing same work object

### Scenario 2: Unexpected Errors Spiking
**Debug steps**:
1. **Get error rate baseline**: `tail -100 alert.log | grep "ERROR" | wc -l`
2. **Identify error type**: `tail -500 pegalogs.log | grep "ERROR" | cut -d' ' -f8 | sort | uniq -c`
3. **Check if correlated**:
   - Did a deployment happen? Check deployment log timestamp
   - Did traffic spike? Check transaction count in metrics
   - Did database fail? Check DB connection errors
4. **Find root cause**: `grep "ERROR.*cause" pegalogs.log | head -5`

## PEGA0001-PEGA0099 Alert Codes

### Common Alert Codes
| Code | Severity | Meaning |
|------|----------|---------|
| PEGA0001 | ERROR | Database connection failed |
| PEGA0008 | WARN | Cache invalidation timeout |
| PEGA0012 | ERROR | Rule not found (missing dependency) |
| PEGA0019 | ERROR | Deadlock detected |
| PEGA0025 | WARN | Performance threshold exceeded |
| PEGA0031 | ERROR | XML validation failed |
| PEGA0048 | ERROR | External service unavailable |
| PEGA0055 | FATAL | Out of memory |
| PEGA0067 | ERROR | Authentication failure |
| PEGA0089 | WARN | Deprecated feature used |

### Troubleshooting PEGA0001 (DB Connection Failed)
**Error message**: `PEGA0001: Database service not available`
**Root causes**:
- Database server down → Check DB status, restart if needed
- Connection pool exhausted → Too many connections, increase pool size
- Network timeout → Firewall rule missing, check connectivity

**Fix**:
1. Check DB connectivity: `telnet db-host 5432` (or your DB port)
2. Increase connection pool: `prconfig.xml: pool-size="100"`
3. Monitor connections: `SELECT COUNT(*) FROM pg_stat_activity`
4. Restart app server if connection leak detected

### Troubleshooting PEGA0019 (Deadlock)
**Error message**: `PEGA0019: Deadlock detected in table pr_data`
**Root causes**:
- Concurrent updates to same row
- Long-running transaction blocking others

**Fix**:
1. Identify long transactions: `SELECT * FROM pg_stat_activity WHERE state != 'idle'`
2. Kill blocking transaction: `SELECT pg_terminate_backend(pid)`
3. Add row-level locking: Use SELECT ... FOR UPDATE in Flow
        """
    },
    {
        "title": "Environment Configuration & Promotion",
        "url": "https://docs.pega.com/environment-config",
        "content": """
# Environment Configuration & Promotion

## Environment-Specific Settings

### Configuration Differences Across Environments

**Database Connections**
```
Dev: SQLite (embedded, localhost)
QA: PostgreSQL (shared test instance, 10GB)
Staging: PostgreSQL (production replica, 500GB)
Prod: PostgreSQL (dedicated HA cluster, 2TB failover)
```

**External Integrations**
```
Dev: Mock endpoints (local server)
QA: QA external APIs (non-prod data)
Staging: Production APIs (read-only account, test transactions)
Prod: Production APIs (full access, monitored)
```

**Email Configuration**
```
Dev: In-memory queue (no SMTP)
QA: Test SMTP server (capture all emails to testing@company.com)
Staging: Prod SMTP (but with override recipient)
Prod: Prod SMTP (emails sent to actual users)
```

### DSS Per Environment
**DSS (Decision Support System)** = Environment-specific settings

**Path**: **Configure → Application → DSS Properties**

**Example DSS per environment**:
```
DSS Property: "APIEndpoint"
  Dev: "http://localhost:8080/mock-api"
  QA: "https://qa-api.external.com/v1"
  Staging: "https://prod-api.external.com/v1?testmode=true"
  Prod: "https://prod-api.external.com/v1"
```

**Usage in code**:
```xml
<Data name="apiUrl" source="parameter" sourceName="DSS.APIEndpoint" />
```

## Prconfig.xml Configuration

### Core Configuration File
**Path**: `pega/config/prconfig.xml`
**Size**: ~500 lines
**Purpose**: Low-level system settings (mostly unchanged across environments)

### Key Parameters

**Database Configuration**
```xml
<databasetype>postgres</databasetype>
<jdbc-url>jdbc:postgresql://db-host:5432/pega</jdbc-url>
<jdbc-driver-class>org.postgresql.Driver</jdbc-driver-class>
<userid>pega</userid>
<!-- Password stored in environment variable: PEGA_DB_PASSWORD -->
```

**Connection Pool Settings**
```xml
<max-pool-size>50</max-pool-size>  <!-- Dev: 10, Prod: 100 -->
<idle-timeout-seconds>300</idle-timeout-seconds>
<connection-timeout-ms>30000</connection-timeout-ms>
```

**Cache Configuration**
```xml
<cache-type>distributed</cache-type>  <!-- Dev: local, Prod: distributed (Coherence) -->
<cache-expiry-minutes>60</cache-expiry-minutes>
```

**Session Configuration**
```xml
<session-timeout-minutes>30</session-timeout-minutes>  <!-- Prod: 30, Dev: 120 -->
<enable-session-tracking>true</enable-session-tracking>
```

### Differences Per Environment
```xml
<!-- Dev (prconfig-dev.xml) -->
<max-pool-size>10</max-pool-size>
<log-level>DEBUG</log-level>
<enable-profiling>true</enable-profiling>

<!-- Prod (prconfig-prod.xml) -->
<max-pool-size>100</max-pool-size>
<log-level>INFO</log-level>
<enable-profiling>false</enable-profiling>
```

## Connection Pool Settings

### Sizing Connection Pools
**Formula**: `max-connections = (# app nodes × 25) + 10`

**Example**:
```
Dev (1 node): 35 connections
QA (2 nodes): 60 connections
Staging (3 nodes): 85 connections
Prod (5 nodes): 135 connections
```

### Tuning Parameters
```xml
<!-- Minimum idle connections to maintain -->
<min-pool-size>5</min-pool-size>

<!-- Maximum concurrent connections -->
<max-pool-size>100</max-pool-size>

<!-- Time to wait for connection before timeout -->
<connection-timeout-ms>30000</connection-timeout-ms>

<!-- Close idle connections after this time -->
<idle-timeout-seconds>300</idle-timeout-seconds>

<!-- Connection test query (verify connection alive) -->
<test-query>SELECT 1</test-query>
```

### Monitoring Connection Pool
**SMA → Node Status → Connection Pools**:
- Active connections: Current in-use
- Idle connections: Available for reuse
- Waiting threads: Threads waiting for connection
- Peak usage: Highest concurrent connections

**Alert if**:
- Active >80% of max
- Waiting threads >0 (connection starvation)
- Test query failing frequently (network issues)

## Promoting Code Dev → QA → Staging → Prod

### Promotion Pipeline Overview
```
Developer pushes to Git
         ↓
CI/CD Pipeline (Jenkins/GitLab CI)
- Run unit tests
- Run integration tests (QA database)
         ↓
Build RAP file
         ↓
Deploy to QA environment
- Import RAP
- Run smoke tests
- Run UAT scenario
         ↓
Promote to Staging (prod-like environment)
- Shadow traffic (real prod traffic to staging)
- Monitor for 48 hours
         ↓
Promote to Production
- Business change approval
- Deployment window scheduled
- Deploy with rollback plan
```

### RAP Promotion Process
1. **Build RAP in Dev**:
   - All new rules + updates included
   - Version: `8.2.1-build-2345`
   - Checksum verified

2. **Deploy to QA**:
   - Auto-import via CI/CD
   - Run regression test suite (2-4 hours)
   - If tests fail: Report to dev team, go back to Dev

3. **Promote to Staging**:
   - Manual approval by QA lead
   - Deploy RAP to staging environment
   - Run UAT for 24 hours (real users test)
   - Shadow 10% of production traffic (optional)

4. **Promote to Production**:
   - Change Request (SNOW) created
   - CAB (Change Advisory Board) approval
   - Scheduled deployment window (off-hours)
   - Deploy to prod with 1-hour rollback window

### Rollback Procedures
**If deployment fails in QA/Staging**:
- Rollback to previous RAP version (stored in environment)
- Time: <5 minutes
- No approval needed (automated via SMA)

**If deployment fails in Prod**:
- Execute rollback plan:
  1. Notify stakeholders
  2. Initiate rollback in SMA
  3. Monitor health check page
  4. Confirm business transactions working
- Post-mortem: What went wrong? Why didn't testing catch it?

## Environment Parity

### What is Environment Parity?
**Goal**: Prod and Staging are identical (except data)

**Why**: Issues found in dev/QA don't resurface in prod

### Parity Checklist
- ✓ **Hardware**: Same node count, memory, CPU
- ✓ **OS/JVM**: Same OS version, same JVM version
- ✓ **Database**: Same DB version, same schema version
- ✓ **Configuration**: Same prconfig.xml (except pool sizes)
- ✓ **Pega version**: Same Pega build
- ✓ **Third-party libraries**: Same versions, same patches
- ✓ **External integrations**: Same endpoint URLs (test vs prod)

### Maintaining Parity
1. **Monthly parity audit**:
   - Compare hardware specs: `uname -a`, `free -h`, `nproc`
   - Compare versions: Pega version, DB version, JVM
   - Compare configuration: Diff prconfig files

2. **After major changes**:
   - Update staging (mirror prod immediately)
   - Document variance reason: "QA intentionally running JVM 11 for compatibility testing"

3. **Testing parity issues**:
   - If issue only in prod: Suspect parity gap
   - Reproduce in staging: If reproduced, likely application bug
   - If not reproduced: Likely environment-specific (hardware, config)

### Common Parity Gaps
- **JVM version**: Dev=JVM 11, Prod=JVM 17 → class compatibility issues
- **Database indexes**: Missing index in dev → query slow only in prod
- **Third-party APIs**: Dev mocks API, Prod calls real → latency difference
- **Cache configuration**: Dev=local, Prod=distributed → data consistency issues
        """
    },
    {
        "title": "Production Monitoring & Health Checks",
        "url": "https://docs.pega.com/production-monitoring",
        "content": """
# Production Monitoring & Health Checks

## SMA Health Check Page

### Accessing Health Checks
**URL**: `https://your-pega-instance.com/sma`
**Path**: **System → Monitoring → Health Check**
**Refresh**: Automatic every 30 seconds

### Key Health Indicators
| Indicator | Green (<) | Yellow | Red (>) |
|-----------|-----------|--------|---------|
| CPU Usage | 50% | 50-75% | >75% |
| Memory Usage | 70% | 70-85% | >85% |
| Disk Space | 70% | 70-90% | >90% |
| Active Threads | 100 | 100-200 | >200 |
| DB Connection Pool | 50% | 50-80% | >80% |
| Error Rate | <0.1% | 0.1-1% | >1% |
| Response Time (p95) | <2s | 2-5s | >5s |

### Node Status Details
1. Click **Node Details**
2. Each node shows:
   - **Status**: Active/Warning/Offline
   - **Uptime**: Days since last restart
   - **Heap Memory**: Used/Max (e.g., 2.5GB/4GB)
   - **GC Time**: Last full GC duration
   - **Thread Count**: Active/peak
   - **Log Errors**: Errors in last hour

**Action if node offline**:
- Check network connectivity: `ping node-hostname`
- Check process: `ps aux | grep java` (should be running)
- Check logs: `tail -100 pegalogs_<node>.log` (look for startup errors)
- Restart if needed: Stop app, clear temp files, restart

## PDC Monitoring

### What is PDC?
**PDC = Pega Design Container** = Node-to-node communication layer

**Purpose**: Keeps all nodes' caches in sync, distributes configuration changes

### PDC Status Checks
**Path**: **SMA → System → PDC Status**

**Key metrics**:
- **Member Count**: Expected vs actual nodes
- **Last Heartbeat**: <30 seconds ago (if >60s, communication issue)
- **Cache Sync Lag**: <100ms (if >500ms, network latency)
- **Message Queue**: <100 messages (if >1000, nodes falling behind)

### Common PDC Issues

**Issue: Node shows "DISCONNECTED"**
- **Cause**: Network partition or node crash
- **Fix**:
  1. Check connectivity: `ping node-ip` from other nodes
  2. Check app server status: `ps aux | grep java`
  3. Review logs: `grep "PDC" pegalogs.log | tail -20`
  4. Restart node if needed (drain sessions first)

**Issue: Cache Sync Lag >1 second**
- **Cause**: Network bandwidth saturation or node overloaded
- **Fix**:
  1. Check network: `iftop` (bandwidth usage per connection)
  2. Check node load: `top` (CPU/memory utilization)
  3. Reduce traffic (scale down) or add nodes (scale up)

## Node Health Monitoring

### JVM Metrics
**Path**: **SMA → System → JVM**

**Critical metrics**:
- **Heap Usage**: Should be <80% (if >90%, OutOfMemory risk)
- **GC Pause Time**: Full GC <20s, minor <2s
- **GC Frequency**: Full GC <1/hour (if more frequent, heap too small)

**Example**: If heap 3.2GB/4GB
- Heap usage: 80%
- Risk: OutOfMemory in next spike
- Action: Increase heap size or reduce user load

### Thread Pool Monitoring
**Path**: **SMA → System → Thread Pools**

**Pega thread pools**:
- **Worker Pool**: Business logic execution (size: 50-200)
- **Timer Pool**: Scheduled tasks (size: 10-50)
- **HTTP Pool**: Inbound requests (size: 100-400)

**Alert if**:
- **Waiting Queue**: Threads waiting for pool availability
- **Peak Threads**: Consistently near max capacity
- **Rejected Tasks**: Tasks rejected due to full queue

**Fix**: Increase pool size or scale app node count

### Database Connection Monitoring
**Path**: **SMA → System → Connection Pools**

**Metrics**:
- **Total Connections**: Current connections in use
- **Idle Connections**: Available for new requests
- **Waiting Threads**: Threads waiting for connection
- **Connection Test Failures**: Failed connectivity checks

**Alert if**:
- **Waiting Threads >0**: Connection starvation (user requests waiting)
- **Test Failures >5%**: Database connectivity issues
- **Usage >80%**: Pool may be too small

## Requestor Management

### Understanding Requestors
**Requestor** = User session or batch process instance

**Monitoring**: **SMA → System → Requestor Management**

**Key columns**:
- **Requestor ID**: System-generated session ID
- **User**: Logged-in user name
- **Connection Start**: When session started
- **Duration**: How long session active
- **Status**: Active/idle/locked

### Active Requestor Analysis
1. **Sort by Duration** (longest first)
2. **Identify long-running requests** (>30 min)
3. **Check if blocked**: Status = "Locked" (waiting on something)
4. **Kill if necessary**: Right-click → Kill Requestor (caution: may lose work)

**Why kill requestors?**
- User forgot to logout (connection leak)
- Request hung (infinite loop)
- Database deadlock (waiting indefinitely)

### Requestor Limits
**Configuration**: **Configure → Application → Requestor Limits**

**Settings**:
- **Max Requestors Per User**: (typical: 5, prevent session abuse)
- **Max Session Duration**: (typical: 8 hours, auto-logout)
- **Max Idle Time**: (typical: 30 min, auto-logout on inactivity)

**Increase for**:
- Batch processes (long-running, might need 24 hours)
- Integration APIs (continuous connections)

## Agent Monitoring

### Agent Types in Pega
| Agent | Purpose | Schedule |
|-------|---------|----------|
| **Polling Agent** | Check external system periodically | Every 5-60 min |
| **Listener Agent** | Wait for external event (email, queue) | Continuous |
| **Work Queue Agent** | Process work objects in queue | Every 1-5 min |
| **Batch Agent** | Large batch job (nightly processing) | Scheduled (midnight) |

### Agent Health Checks
**Path**: **SMA → System → Agent Management → Agent Status**

**Metrics per agent**:
- **Status**: Scheduled/Running/Paused
- **Last Run**: When did it last execute?
- **Duration**: How long did it take?
- **Next Run**: When will it execute next?
- **Error**: Any errors in last run?

### Troubleshooting Stuck Agents
**Issue: Agent hasn't run in 2 hours**
**Cause**: Deadlock, database issue, or application crash
**Fix**:
1. Check logs: `grep "AgentName" pegalogs.log | tail -10`
2. Check database: Query work queue table, look for locked rows
3. Restart agent: Pause → Wait 5 min → Resume
4. Escalate if agent won't start

## Queue Depth Monitoring

### Work Queue Depth
**Path**: **SMA → System → Queue Analysis**

**Key metric**: Average queue depth
- **Healthy**: Queue depth <100, processing rate >10/sec
- **Concerning**: Queue depth >500, processing rate declining
- **Critical**: Queue depth >5000, processing stopped

### Queue Monitoring Queries
```sql
SELECT queue_name, COUNT(*) as depth
FROM pr_work_queue
WHERE status = 'ACTIVE'
GROUP BY queue_name
ORDER BY depth DESC;
```

**Action if queue overflowing**:
1. **Scale horizontally**: Add app node (processes faster)
2. **Pause source**: Stop incoming work submissions (if safe)
3. **Manual intervention**: Bulk update old work to "RESOLVED"
4. **Investigate bottleneck**: Why isn't work being processed? (database lock? external API slow?)

## Setting Up Alerts & Thresholds

### Pega Native Alerts
**Path**: **Configure → Monitoring → Alert Rules**

**Example alert**:
```
Rule: "CPU > 80%"
Trigger: If CPU exceeds 80% for 5 minutes
Action: Send email to ops@company.com
Severity: Warning (yellow)
```

**Common alert thresholds**:
- CPU >80% → Scale up
- Memory >85% → Page on-call
- Error rate >1% → Investigate
- Response time p95 >5s → Performance investigation

### PagerDuty Integration
1. **Create PagerDuty integration** in Pega
2. **Configure escalation policy**:
   - Level 1: Page on-call engineer (5 min timeout)
   - Level 2: Page manager (10 min timeout)
   - Level 3: Page VP Operations (15 min timeout)
3. **Map Pega alerts to PD**:
   - Critical (FATAL): Immediate page
   - High (ERROR): Page with 15 min delay
   - Medium (WARN): Slack notification only

### ServiceNow Integration
1. **Create ITSM integration** (API token)
2. **Pega alert creates ticket**: When threshold breached
   - Ticket priority: Urgent (critical alert)
   - Assignment: ops-team
   - Auto-resolution: When alert clears
3. **SLA**: Response 1 hour, resolve 4 hours

## Runbook for Common Production Issues

### Issue: "Out of Memory Exception"
**Symptom**: PEGA0055 error, application crashes
**Immediate action**:
1. **Page on-call** (5 seconds)
2. **Check heap**: SMA → JVM → Heap Usage
3. **Identify memory leak**:
   - Get thread dump: `jstack <pid> > heap-dump.txt`
   - Analyze: Look for unexpected object counts
4. **Restart app server** (controlled failover):
   - Stop app on one node
   - PDC redirects traffic to other nodes
   - Restart node
   - Monitor for memory leak repeat

### Issue: "Database Connection Timeout"
**Symptom**: Users see "Connection refused" error
**Immediate action**:
1. **Check database server**: Can app nodes reach database?
   - `telnet db-host 5432` from app node
   - Check DB is running: `systemctl status postgresql`
2. **Check connection pool**: **SMA → Connection Pools**
   - If 100% utilization: Increase max-pool-size
3. **Kill long-running queries**:
   - `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE duration > interval '10 minutes'`
4. **Restart app server** (last resort)

### Issue: "High Error Rate (>5%)"
**Symptom**: Logs flooding with ERRORs, users reporting failures
**Immediate action**:
1. **Categorize errors**: `grep "ERROR" pegalogs.log | cut -d' ' -f8 | sort | uniq -c`
2. **Root cause**:
   - If all "NullPointerException": Recent code deployment issue
   - If all "Database" errors: Database connectivity
   - If all "Timeout" errors: Slow external service
3. **Apply fix**:
   - Rollback recent deployment: `SMA → Rollback`
   - Wait 10 minutes, monitor error rate
   - If error rate <0.5%: Deployment was cause
4. **Escalate** if error rate remains high

### Issue: "Deployment Failed — Rollback Initiated"
**Symptom**: Automatic rollback triggered after deployment
**Root cause analysis**:
1. **Review deployment logs**: What failed?
2. **Check application logs**: Were errors detected post-deployment?
3. **Post-mortem questions**:
   - Was this tested in staging?
   - Did staging have same database schema?
   - Were backward compatibility issues missed?
4. **Prevent recurrence**:
   - Add extra validation to QA testing
   - Require staging soak test (48 hours) before prod
   - Update deployment runbook
        """
    }
]

def seed_phase11():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE11:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase11_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE11)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 11 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase11()
