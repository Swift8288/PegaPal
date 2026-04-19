"""
Curated Pega Knowledge Base — Phase 3C
Covers: SMA/Admin Studio, System Settings, Node Management, Pega Terminology/Glossary

Run: python -m crawler.seed_kb_phase3c
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE3C = [
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/sma/system-management-application.html",
        "title": "SMA (System Management Application) and Admin Studio — Overview and Troubleshooting",
        "content": """# SMA (System Management Application) and Admin Studio

## What is SMA?
SMA stands for **System Management Application** — it is Pega's administration console for managing the runtime environment. SMA is NOT "Service Level Agreement."

## SMA vs Admin Studio — Version History
- **Pega 7.x - 8.5**: SMA was the primary admin interface, accessed at `/prweb/PRServlet?pyActivity=Data-Admin-DB-Name.pxOpenSMADashboard`
- **Pega 8.6+**: Admin Studio was introduced as the modern replacement for SMA, accessible from Dev Studio → Configure → System → Operations
- **Pega Infinity '23 (8.8)**: Admin Studio is the default. SMA still accessible but deprecated in UI.
- **Pega Infinity '24**: SMA UI is further reduced. Most functions moved to Admin Studio. Some SMA endpoints may return 404 or redirect.

## "There is no SMA in version 24.x"
This is a common issue after upgrading to Infinity '23 or '24. SMA functionality has been **replaced by Admin Studio**, not removed.

### Where to find SMA features in newer versions:
| Old SMA Feature | New Location in '23/'24 |
|----------------|------------------------|
| Agent Management | Admin Studio → Operations → Agent Management |
| Queue Processors | Admin Studio → Operations → Queue Management |
| Requestor Management | Admin Studio → Operations → Requestor Management |
| Database Statistics | Admin Studio → Database → Statistics |
| Cluster/Node Management | Admin Studio → Operations → Cluster Management |
| System Health | Admin Studio → Dashboard |
| Import/Export | Admin Studio → Operations → Import/Export |
| Search Index | Admin Studio → Search → Index Management |
| Log Management | Admin Studio → Logging → Log Settings |

### How to access Admin Studio:
1. Dev Studio → Configure → System → Operations (opens Admin Studio)
2. Direct URL: `/prweb/PRServlet?pyActivity=pxOpenAdminStudio`
3. Or: Navigation menu → Configure → System → Administration

### Common Issues After Migration:
1. **Bookmarks to old SMA URLs return 404**: Update bookmarks to Admin Studio URLs
2. **Custom SMA gadgets missing**: Recreate as Admin Studio dashboard widgets
3. **Scripts that call SMA REST endpoints**: Update to new Admin Studio API endpoints
4. **Operator permissions**: Admin Studio uses different access roles — check operator has PegaRULES:SysAdmin4 or appropriate admin role

## Admin Studio Key Sections

### Operations Dashboard
- **Cluster Management**: View all nodes, health status, CPU/memory usage per node
- **Agent Management**: Start/stop/configure agents per node
- **Queue Management**: Monitor queue processors, queue depth, stuck items
- **Requestor Management**: View active sessions, kill stuck requestors

### Database Administration
- **Table Statistics**: Update table statistics for query optimizer
- **Schema Changes**: View pending schema changes after rule imports
- **Connection Pools**: Monitor pool usage, active connections, wait times

### Search Administration
- **Index Status**: View search index health, queue depth, last rebuild time
- **Rebuild Index**: Trigger full or incremental index rebuild
- **Search Settings**: Configure which classes are indexed, field mappings

### Logging
- **Log Settings**: Change log levels dynamically (no restart needed)
- **PEGA Log Viewer**: View PegaRULES log entries in-browser
- **Alert Log**: View system alerts (threshold violations, slow rules)

## Troubleshooting Admin Studio

### Can't Access Admin Studio
**Causes**:
- Missing admin role on operator (needs PegaRULES:SysAdmin4 or equivalent)
- URL routing changed after upgrade
- Load balancer/reverse proxy blocking admin endpoints

**Fix**:
1. Check operator record → Access tab → ensure admin access role is present
2. Try direct URL with specific servlet path
3. Check web.xml and prweb configuration for admin servlet mapping

### Admin Studio Shows Stale Data
**Cause**: Dashboard caching or browser cache
**Fix**: Hard refresh (Ctrl+Shift+R), or clear Admin Studio cache from settings

### Node Not Appearing in Cluster View
**Cause**: Node failed to register with database, or node is down
**Fix**: Check node health, verify prconfig.xml has correct database connection, restart node if needed
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/system/dynamic-system-settings.html",
        "title": "Dynamic System Settings (DSS) — Configuration and Common Settings",
        "content": """# Dynamic System Settings (DSS) — Configuration and Troubleshooting

## What are Dynamic System Settings?
DSS (Dynamic System Settings) are runtime configuration values stored in the database, changeable without restarting Pega. They control system behavior like timeouts, thresholds, feature flags, and limits.

## How to Access DSS
- **Dev Studio**: Configure → System → Settings → Dynamic System Settings
- **Direct search**: Search for "Data-Admin-System-Settings" in Dev Studio
- **prconfig.xml**: Some settings can also go in prconfig.xml (server restart needed)

## Priority Order
When the same setting exists in multiple places:
1. **DSS (database)** — highest priority, wins over everything
2. **prconfig.xml** — used if DSS doesn't exist
3. **Default value** — built-in Pega default

## Commonly Needed DSS Values

### Performance Settings
| Setting | Purpose | Default | Recommended |
|---------|---------|---------|-------------|
| `Pega-RULES/MaxQueryTime` | Max SQL query execution time (seconds) | 5 | 10-30 for complex reports |
| `Pega-RULES/MaxReportRows` | Max rows returned by reports | 10000 | Adjust per use case |
| `Pega-RULES/EnableParallelPageProcessing` | Parallel processing for data pages | false | true for high-throughput |
| `Pega-RULES/requestor/tempPageCleanupThreshold` | Threshold for temp page cleanup | 50 | Lower if memory issues |

### Timeout Settings
| Setting | Purpose | Default |
|---------|---------|---------|
| `Pega-RULES/requestor/timeoutMinutes` | Requestor timeout | 30 |
| `Pega-RULES/activityTimeout` | Activity execution timeout | 20 |
| `Pega-RULES/connectTimeout` | Connector timeout (seconds) | 30 |
| `Pega-RULES/httpConnectTimeout` | HTTP connection timeout | 30 |

### Security Settings
| Setting | Purpose |
|---------|---------|
| `Pega-RULES/authentication/maxLoginAttempts` | Max failed login attempts before lockout |
| `Pega-RULES/passwordComplexity` | Password complexity enforcement |
| `Pega-RULES/sessionTimeout` | User session timeout |
| `Pega-RULES/enableCSRFProtection` | CSRF token enforcement |

### Feature Flags
| Setting | Purpose |
|---------|---------|
| `Pega-RULES/EnableAsyncDeclareExpression` | Async declare expression evaluation |
| `Pega-RULES/EnableOptimizedRuleResolution` | Faster rule resolution algorithm |
| `Pega-RULES/EnableConstellationUI` | Enable/disable Constellation UI globally |
| `Pega-RULES/DisableAutoComplete` | Disable autocomplete in UI forms |

## Troubleshooting DSS

### Setting Not Taking Effect
**Causes**:
1. Typo in setting name (case-sensitive!)
2. Setting needs node restart (some DSS require restart despite being "dynamic")
3. prconfig.xml override taking precedence (check for conflicts)
4. Setting is on wrong context/ruleset

**Fix**:
1. Verify exact setting name from Pega documentation
2. Try restarting the node after changing
3. Check prconfig.xml for the same setting
4. Ensure DSS is saved on the correct production ruleset

### How to Find the Right DSS Name
1. Search Pega Community for the behavior you want to control
2. Check Dev Studio → Configure → System → Settings → search by keyword
3. Look in prconfig.xml reference documentation
4. Check Pega Support knowledge articles for the specific version
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/glossary/pega-terminology.html",
        "title": "Pega Terminology and Abbreviations — Quick Reference",
        "content": """# Pega Terminology and Abbreviations

## System Components
- **SMA** = System Management Application — admin console for managing Pega runtime environment. Replaced by Admin Studio in Pega 8.6+.
- **Admin Studio** = Modern replacement for SMA. Accessed from Dev Studio → Configure → System.
- **Dev Studio** = Developer Studio — the main IDE for building Pega applications.
- **App Studio** = Low-code application studio for business users and citizen developers.
- **Prediction Studio** = AI/ML model management for Next-Best-Action and decision strategies.

## Architecture Terms
- **PRPC** = Pega Rules Process Commander — original name for the Pega platform (pre-7.x).
- **PegaRULES** = The core rules engine and database schema.
- **PegaDATA** = Database schema for application/business data.
- **Node** = A single Pega server instance in a cluster.
- **Cluster** = Multiple Pega nodes sharing the same database, providing load balancing and failover.
- **Requestor** = A user session on a Pega node. Each browser session creates a requestor.

## Data & Processing Terms
- **Clipboard** = In-memory data store for the current requestor/session. Properties and pages live here.
- **Data Page** = Declarative data source — loads data on demand and caches it. Scopes: Thread, Requestor, Node.
- **Data Transform** = Rule for mapping/transforming data between pages. Replaces old Activity-based data mapping.
- **Declare Expression** = Declarative rule that automatically computes property values when dependencies change.
- **Declare Index** = Creates a database index based on property values for faster queries.

## Case & Process Terms
- **Case Type** = Blueprint for a business process (e.g., "Insurance Claim", "Service Request").
- **Case** = Instance of a Case Type — a specific running business process.
- **Stage** = Major phase of a case lifecycle (e.g., "Create", "Review", "Resolve").
- **Process (Flow)** = Sequence of steps within a stage.
- **Assignment** = A task assigned to a user or work queue for action.
- **SLA** = Service Level Agreement — defines urgency escalation timers on assignments.
- **pyStatusWork** = Property that tracks case status (Open, Resolved, Closed, etc.).

## Integration Terms
- **Connector** = Rule that calls external systems (REST Connector, SOAP Connector, Connect SQL, etc.).
- **Service** = Rule that exposes Pega functionality to external callers (Service REST, Service SOAP, etc.).
- **Service Package** = Groups service rules for deployment and management.
- **Data Set** = Abstraction over data sources (database, Kafka, file, etc.) for data flows.

## DevOps Terms
- **RAP** = Rules Application Package — exported application archive (.zip) for deployment.
- **Branch** = Isolated development workspace within a pipeline for parallel development.
- **Pipeline** = CI/CD pipeline for promoting applications across environments (Dev → QA → Prod).
- **Deployment Manager** = Tool for managing application deployments across environments.

## Performance & Debugging Terms
- **PAL** = Performance Analyzer — tool for profiling rule execution performance.
- **Tracer** = Real-time debugger for tracing rule execution, data flow, and errors.
- **Guardrails** = Best practice rules that grade application quality (1-100 score).
- **PDN** = Pega Developer Network — community and documentation portal.
- **DSS** = Dynamic System Settings — runtime configuration values in the database.

## UI Terms
- **Section** = Reusable UI component in Traditional UI (HTML/JSP-based).
- **Harness** = Top-level page layout in Traditional UI (contains sections).
- **View** = Constellation equivalent of a Section (React-based).
- **Portal** = User's main application interface (e.g., Case Manager Portal, User Portal).
- **Constellation** = React-based UI framework replacing Traditional UI (Pega 8.6+).
- **DX API** = Digital Experience API — REST API for Constellation and headless UI.
- **DX Component** = Custom React component for Constellation UI.

## Database & Class Terms
- **Class** = Pega's object model — like a table/entity definition. Rules and data are organized by class.
- **Class Group** = Maps a top-level class hierarchy to a database table.
- **Work Class** = Class that represents a case type (extends Work-).
- **Data Class** = Class that represents reusable data (extends Data-).
- **Rule-** = Class hierarchy containing all rule types (Rule-HTML-Section, Rule-Obj-Activity, etc.).
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/system/prconfig-settings.html",
        "title": "prconfig.xml — Common Settings and Troubleshooting",
        "content": """# prconfig.xml — Common Settings and Troubleshooting

## Overview
prconfig.xml is the primary server-side configuration file for Pega. Located in the Pega application's WEB-INF/classes directory. Changes require a node restart to take effect.

## Location
- **Tomcat**: `<TOMCAT_HOME>/webapps/prweb/WEB-INF/classes/prconfig.xml`
- **WebSphere**: Inside the deployed EAR/WAR, or via JVM system properties
- **Kubernetes/Docker**: Mounted as ConfigMap or volume
- **Pega Cloud**: Managed via Pega Cloud Services — direct file access not available

## Common Settings

### Database Connection
```xml
<env name="database/databases/PegaRULES/dataSource" value="java:comp/env/jdbc/PegaRULES" />
<env name="database/databases/PegaDATA/dataSource" value="java:comp/env/jdbc/PegaDATA" />
```

### Node Type Classification
```xml
<env name="identification/node.type" value="WebUser,BackgroundProcessing,Search" />
```
Node types control which services run on which node:
- **WebUser**: Handles interactive user requests
- **BackgroundProcessing**: Runs agents, queue processors, scheduled tasks
- **Search**: Runs Elasticsearch/search indexing
- **Stream**: Handles Kafka/event streaming

### Cluster Settings
```xml
<env name="cluster/name" value="MyPegaCluster" />
<env name="identification/node.id" value="Node1" />
```

### Logging
```xml
<env name="prlogging/rootLogger/level" value="WARN" />
<env name="prlogging/logger/com.pega" value="INFO" />
<env name="prlogging/appender/console/class" value="com.pega.pegarules.priv.logimpl.ConsoleAppender" />
```

## Common prconfig.xml Issues

### 1. Node Not Starting After Config Change
**Cause**: XML syntax error in prconfig.xml (unclosed tags, bad characters)
**Fix**: Validate XML syntax before restarting. Check application server log for XML parse errors.

### 2. Setting in prconfig.xml Being Ignored
**Cause**: DSS (Dynamic System Settings) in database overrides prconfig.xml
**Fix**: Check for same setting in DSS. Remove DSS entry if you want prconfig.xml to take effect.

### 3. Wrong Node Type Causing Missing Features
**Symptoms**: Agents not running, search not indexing, queue processors idle
**Cause**: Node type doesn't include required classification
**Fix**: Add required node type to `identification/node.type` setting. Restart node.

### 4. Database Connection Failure on Startup
**Symptoms**: Node fails to start, "Cannot connect to database" in logs
**Cause**: JNDI datasource name mismatch between prconfig.xml and application server config
**Fix**: Verify JNDI name matches exactly between prconfig.xml and Tomcat's context.xml (or equivalent).
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/system/node-cluster-management.html",
        "title": "Node and Cluster Management — Configuration, Health, and Troubleshooting",
        "content": """# Node and Cluster Management — Troubleshooting

## Overview
Pega runs as a cluster of nodes sharing a single database. Each node handles user requests, background processing, or both, depending on its node type classification.

## Cluster Architecture
- All nodes connect to the same PegaRULES/PegaDATA database
- Nodes communicate via the database (no direct node-to-node messaging by default)
- Hazelcast or Ignite used for distributed caching in newer versions
- Each node has a unique node ID and type classification

## Common Cluster Issues

### 1. Node Shows "Unknown" or Missing in Cluster View
**Symptoms**: Admin Studio → Cluster Management shows fewer nodes than expected
**Causes**:
- Node failed to register (database connectivity issue)
- Node crashed or was killed without graceful shutdown
- Stale node entry in database (ghost node)
- Different cluster name in prconfig.xml between nodes

**Fix**:
1. Check the node's PegaRULES log for startup errors
2. Verify `cluster/name` is identical across all nodes in prconfig.xml
3. Check database connectivity from the problem node
4. For stale entries: wait for automatic cleanup or manually remove from pr_sys_statusnode table
5. Restart the affected node

### 2. Agents Running on Wrong Node / Not Running
**Symptoms**: Background jobs not executing, agents showing disabled
**Causes**:
- Node type doesn't include "BackgroundProcessing"
- Agent schedule configured for specific node ID that changed
- Multiple nodes competing for same agent (no coordination)

**Fix**:
1. Check prconfig.xml → `identification/node.type` includes "BackgroundProcessing"
2. Check agent schedule — is it pinned to a specific node?
3. Use Admin Studio → Agent Management to verify agent status per node

### 3. Distributed Cache Inconsistency
**Symptoms**: Different data on different nodes, stale rule versions, "rule not found" on some nodes
**Causes**:
- Cache not invalidating properly across cluster
- Hazelcast/Ignite cluster formation failure
- Network partitioning between nodes

**Fix**:
1. Clear rule cache on all nodes: Admin Studio → Cache → Clear
2. Check Hazelcast cluster membership logs
3. Verify network connectivity between all nodes (multicast or TCP-IP)
4. Restart affected nodes if cache is badly corrupted

### 4. Session Stickiness Issues
**Symptoms**: Users lose session, random logouts, "requestor not found"
**Causes**:
- Load balancer not configured for session stickiness
- Node crashed mid-session and no session failover configured
- Requestor timeout too aggressive

**Fix**:
1. Configure load balancer for sticky sessions (cookie or IP-based)
2. For session failover: configure session serialization in prconfig.xml
3. Increase requestor timeout if appropriate
4. Check load balancer health check configuration

### 5. Split-Brain in Cluster
**Symptoms**: Different nodes processing the same work, duplicate assignments, data conflicts
**Causes**: Network partition causing nodes to form separate sub-clusters
**Fix**:
1. Fix network connectivity between nodes
2. Restart the minority partition nodes
3. Check for duplicate work items and resolve conflicts
4. Review Hazelcast split-brain protection settings

## Cluster Health Monitoring
1. Admin Studio → Dashboard for overall health
2. Check each node's CPU, memory, thread count
3. Monitor database connection pool usage per node
4. Set up alerts for node departure events
5. Use PAL (Performance Analyzer) for per-node performance metrics
"""
    },
]


def seed_phase3c():
    """Write Phase 3C curated docs to raw_docs directory."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc in CURATED_DOCS_PHASE3C:
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
        filename = f"phase3c_{slug}.json"
        filepath = RAW_DOCS_DIR / filename

        payload = {
            "url": doc["url"],
            "title": doc["title"],
            "content": doc["content"].strip(),
        }
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE3C)}] Saved: {doc['title']}")

    logger.info(f"\nPhase 3C complete — {count} documents saved to {RAW_DOCS_DIR}")
    logger.info("Next: python -m indexer.index_docs")


if __name__ == "__main__":
    seed_phase3c()
