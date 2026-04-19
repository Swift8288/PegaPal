"""
Curated Pega Knowledge Base — Phase 5C (Remaining gaps)
Covers: Access When/Deny, Declare Constraints, Data Sets, Docker/K8s,
        Audit Logging, Scenario Testing, Map Values, Declare Pages

Run: python -m crawler.seed_kb_phase5c
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE5C = [
    {
        "url": "curated://pega-access-when-deny",
        "title": "Access When and Access Deny Rules — Row-Level Security and Troubleshooting",
        "content": """# Access When and Access Deny Rules — Troubleshooting

## Overview
Access When and Access Deny rules implement **row-level security** in Pega — they control which specific data records a user can see or modify, beyond what role-based access provides.

- **Access When**: Grants access to specific records WHEN a condition is true
- **Access Deny**: Denies access to records WHEN a condition is true
- **Access Of Role To Object (ARO)**: Maps roles to access permissions on specific classes

## How Row-Level Security Works
1. User requests data (opens a case, runs a report, views a list)
2. Pega checks ARO rules for the user's role + the data class
3. Access When/Deny rules filter which records the user can see
4. Only records passing the access check are returned

## Configuration
1. Create Access When rule on the data class (e.g., MyApp-Work-Claim)
2. Define condition: e.g., `.pyAssignedOperatorID = pxRequestor.pxUserIdentifier` (user sees only their own cases)
3. Create ARO mapping: Role → Class → Access When rule
4. Apply to access group

## Common Issues

### 1. User Can't See Any Records
**Root Causes**:
- Access When condition too restrictive (evaluates false for all records)
- ARO not configured for the user's role
- Access Deny rule blocking everything
- Property referenced in condition is null

**Fix**:
1. Test the Access When condition with sample data
2. Verify ARO exists for the role + class combination
3. Check for conflicting Access Deny rules
4. Use Tracer to see access rule evaluation

### 2. User Sees Records They Shouldn't
**Root Causes**:
- No Access When/Deny rules configured (no row-level filtering)
- Access When condition too permissive
- User has admin role that bypasses access checks
- Report Definition bypasses security (uses "Run as privileged" option)

**Fix**:
1. Add/tighten Access When rules
2. Remove unnecessary admin privileges
3. Check report security settings
4. Audit all roles for excessive permissions

### 3. Performance Impact of Access Rules
**Symptoms**: Slow reports, slow case list loading
**Root Cause**: Access When adds WHERE clauses to every query — complex conditions slow queries down
**Fix**: Keep Access When conditions simple (indexed properties only). Avoid function calls in conditions.

## Best Practices
1. Start with restrictive access, then open up — never the reverse
2. Use simple property comparisons (indexed columns) for Access When conditions
3. Test with multiple user roles to verify correct filtering
4. Don't rely solely on UI hiding — always implement server-side access rules
5. Audit access rules regularly
"""
    },
    {
        "url": "curated://pega-declare-constraints",
        "title": "Declare Constraints — Property Validation, Warnings, and Troubleshooting",
        "content": """# Declare Constraints — Troubleshooting

## Overview
Declare Constraints enforce data quality by automatically validating property values. Unlike Validate rules (which run at specific points), constraints are **always active** — they fire whenever the constrained property changes.

## Constraint Types
- **Error**: Blocks the operation (case can't be saved) if violated
- **Warning**: Shows a warning message but allows the operation to proceed
- **Info**: Informational message only

## Configuration
1. Create Declare Constraint rule on the class
2. Define property to constrain and the condition
3. Set severity (Error, Warning, Info)
4. Set the message to display when violated

## Common Issues

### 1. Constraint Not Firing
**Root Causes**:
- Constraint defined on wrong class (not in inheritance chain)
- Property changed via direct database update (bypasses Pega)
- Constraint disabled or in wrong ruleset
- Property change doesn't trigger re-evaluation

**Fix**: Verify class, check ruleset stack, ensure property is changed through Pega.

### 2. Constraint Fires When It Shouldn't
**Root Causes**:
- Condition logic inverted (checking wrong thing)
- Constraint fires on page load, not just on save
- Missing null check — constraint triggers on empty values

**Fix**: Review condition carefully. Add null check (`.Property != "" AND .Property < 0`).

### 3. Too Many Constraint Violations Slowing Performance
**Root Cause**: Constraints evaluate on every property change, including intermediate steps
**Fix**: Minimize constraints. Use Validate rules for complex validations that should only run at save time.

## Constraints vs Validate Rules
| Aspect | Declare Constraint | Validate Rule |
|--------|-------------------|---------------|
| When it runs | On every property change | When explicitly invoked |
| Scope | Single property | Multiple properties |
| Performance | Runs frequently | Runs once per validation |
| Use case | Simple field-level checks | Complex cross-field validation |
"""
    },
    {
        "url": "curated://pega-data-sets",
        "title": "Data Sets — Database, File, Queue Sources for Data Flows",
        "content": """# Data Sets — Configuration and Troubleshooting

## Overview
Data Sets abstract data sources and destinations for Data Flows and reporting. They provide a unified interface regardless of whether data comes from a database, file, Kafka topic, or REST endpoint.

## Data Set Types
- **Database**: Read/write from Pega database tables
- **File**: Read/write from CSV, JSON, or XML files
- **Kafka**: Read/write from Kafka topics
- **Queue**: Read from JMS/MQ queues
- **REST**: Read from external REST APIs

## Configuration
1. Records → Data Model → Data Set
2. Choose type (Database, File, Kafka, etc.)
3. Configure source details (table, file path, topic, etc.)
4. Define the schema (properties/columns)
5. Set read/write permissions

## Common Issues

### 1. Data Set Returns No Data
**Root Causes**:
- Database query returns empty result (filter conditions wrong)
- File path incorrect or file doesn't exist
- Kafka consumer group already past the messages
- Authentication failure to external source

**Fix**: Test the source independently. Check filters, paths, credentials.

### 2. Schema Mismatch
**Symptoms**: Data loads but properties are empty or wrong type
**Root Causes**: Column names or types don't match between source and Data Set definition
**Fix**: Verify column mapping. Check data types match (String vs Integer vs DateTime).

### 3. Data Set Performance
**Root Cause**: Loading too much data without pagination or filtering
**Fix**: Add WHERE clauses for database. Use file chunking. Implement pagination.

## Best Practices
1. Always define explicit schemas — don't rely on auto-detection
2. Add filters to limit data volume
3. Test with production-volume data before deployment
4. Use database Data Sets for structured queries, File Data Sets for batch imports
"""
    },
    {
        "url": "curated://pega-docker-kubernetes",
        "title": "Docker and Kubernetes Deployment — Containerized Pega and Troubleshooting",
        "content": """# Docker and Kubernetes Deployment — Troubleshooting

## Overview
Pega supports containerized deployment on Docker/Kubernetes for cloud-native environments. Pega provides official Docker images and Helm charts for deployment.

## Architecture
- **Pega Web tier**: Handles user requests (stateless, horizontally scalable)
- **Pega Batch tier**: Runs agents, queue processors (background processing)
- **Pega Search tier**: Runs Elasticsearch for full-text search
- **Database**: External database (PostgreSQL, Oracle, SQL Server) — NOT containerized
- **Load Balancer**: Routes traffic to web tier pods

## Deployment Components
- **Pega Docker images**: Official images from Pega (pega-ready, installer, search)
- **Helm charts**: Kubernetes deployment configuration
- **ConfigMaps**: prconfig.xml, environment variables
- **Secrets**: Database credentials, API keys, certificates

## Common Issues

### 1. Pod Keeps Restarting (CrashLoopBackOff)
**Root Causes**:
- Database connection failure (wrong JDBC URL, credentials, network)
- Insufficient memory (JVM heap > container memory limit)
- Missing configuration (prconfig.xml not mounted)
- License file missing or expired

**Fix**:
1. Check pod logs: `kubectl logs <pod-name>`
2. Verify database connectivity from within the pod
3. Ensure container memory limit > JVM heap (-Xmx) + ~1GB overhead
4. Verify ConfigMap has correct prconfig.xml

### 2. Nodes Not Forming Cluster
**Root Causes**:
- Hazelcast/Ignite discovery not configured for Kubernetes
- Pod network policy blocking inter-pod communication
- Different cluster names between pods

**Fix**:
1. Configure Kubernetes discovery plugin for Hazelcast
2. Verify network policies allow pod-to-pod communication
3. Ensure all pods use same cluster name in prconfig.xml

### 3. Search (Elasticsearch) Not Working
**Root Causes**:
- Search tier pod not running
- Elasticsearch data volume lost (PersistentVolume issue)
- Web/batch pods can't reach search pods (service DNS)

**Fix**:
1. Check search tier pod status and logs
2. Verify PersistentVolumeClaim is bound
3. Test DNS resolution: `kubectl exec <pod> -- nslookup <search-service>`

### 4. Scaling Issues
**Symptoms**: Adding more web pods doesn't improve performance
**Root Causes**:
- Database is the bottleneck (not the web tier)
- Session stickiness not configured on ingress/load balancer
- Connection pool per pod too large (exhausting database connections)

**Fix**:
1. Check database CPU/IO during load
2. Configure session affinity in Kubernetes Ingress
3. Size connection pool per pod = total DB connections / number of pods

## Best Practices
1. Set resource limits on all pods (CPU and memory)
2. Use PersistentVolumes for search data and logs
3. Configure horizontal pod autoscaler for web tier
4. Keep database OUTSIDE Kubernetes (managed database service)
5. Use health checks (liveness/readiness probes) for all tiers
6. Store secrets in Kubernetes Secrets, not ConfigMaps
"""
    },
    {
        "url": "curated://pega-audit-logging-compliance",
        "title": "Audit Logging and Compliance — SOX, HIPAA, and Troubleshooting",
        "content": """# Audit Logging and Compliance — Troubleshooting

## Overview
Pega provides audit capabilities for regulatory compliance (SOX, HIPAA, GDPR, etc.). Audit trails track who did what, when, and to what data.

## Audit Mechanisms
- **Case history**: Automatic log of all case actions (status changes, assignments, updates)
- **Rule history**: Tracks rule changes (who modified, when, what changed)
- **Security audit**: Login/logout, failed auth, privilege changes
- **Custom audit**: Application-specific audit via activities or Declare OnChange

## Configuration
- Case history: Automatic for all case types (stored in pc_history_work)
- Rule history: Automatic for all rule changes (History tab on any rule)
- Security events: Configure in Security → Audit Policy
- Custom audit: Create audit activity and trigger via Declare OnChange or flow step

## Common Issues

### 1. Audit Trail Missing Entries
**Root Causes**:
- Direct database updates bypass Pega audit
- Batch processing doesn't create history entries (depends on configuration)
- Custom activity not logging as expected
- History purge job deleted old entries

**Fix**:
1. Ensure all data changes go through Pega (not direct SQL)
2. Check batch processing configuration for history creation
3. Verify custom audit activity is triggered correctly
4. Review history purge schedule and retention period

### 2. Audit Log Too Large (Performance Impact)
**Root Cause**: Every minor change creates history entry, table grows huge
**Fix**:
1. Configure which changes to audit (not everything)
2. Implement archival for old audit records
3. Use separate reporting database for audit queries
4. Index audit tables appropriately

### 3. Compliance Report Requirements
**Common reports needed**:
- Who accessed patient data (HIPAA)
- Who approved financial transactions (SOX)
- Data subject access requests (GDPR)
- Failed login attempts (all regulations)

**How to build**:
1. Use Report Definitions on history tables
2. Include: operator, timestamp, action, data affected
3. Schedule regular audit report generation
4. Store reports in secure, tamper-proof location

## Best Practices
1. Define audit requirements BEFORE building the application
2. Audit security events (logins, role changes, privilege escalations)
3. Audit all data changes to sensitive/regulated data
4. Implement audit log retention policy matching regulatory requirements
5. Protect audit logs from tampering (separate storage, read-only access)
6. Test audit completeness as part of compliance testing
"""
    },
]


def seed_phase5c():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE5C:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase5c_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE5C)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 5C complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase5c()
