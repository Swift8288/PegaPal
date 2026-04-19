"""
Curated Pega Knowledge Base — Phase 15 (Advanced Integrations & Remaining Features)
Run: python -m crawler.seed_kb_phase15
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE15 = [
    {
        "title": "SAP Integration with Pega",
        "url": "https://pega.doc/integration/sap",
        "content": """
# SAP Integration with Pega

## Overview
Pega connects to SAP through multiple protocols: BAPI (Business API), RFC (Remote Function Call), IDoc (Intermediate Document), and OData. Each offers different capabilities and trade-offs.

## SAP Connector Types

### BAPI Integration
- **Best for**: Real-time synchronous calls to SAP business functions
- **Setup**: Create SAP connector with BAPI call type
- **Config in Pega**:
  - SAP Connection class (under Pega-ProCom-SAP)
  - Specify SAP system ID, gateway host, gateway service
  - Username/password or certificate auth
  - Specify BAPI function name (e.g., `SD_SALESDOCUMENT_CREATE`)
- **Common error**: "Authorization Check Failed" — verify SAP user has necessary RFC authorizations

### RFC (Remote Function Call)
- **Use case**: Direct function calls to SAP backend
- **Configuration**: Similar to BAPI but uses RFC interface
- **Troubleshooting**:
  - Test RFC connectivity via SAP transaction SM59
  - Verify gateway and dispatcher are running
  - Check firewall rules for SAP gateway port (typically 33XX)

### IDoc (Intermediate Document)
- **Best for**: Asynchronous batch data exchange
- **Flow**: Pega sends/receives IDocs via SAP ALE (Application Link Enabling)
- **Setup**:
  - Configure SAP RFC destination in SM59
  - Map IDoc segments to Pega page structures
  - Create inbound/outbound process rules
- **Debugging**: Check SAP transaction BD87 for IDoc status and errors

### OData Integration
- **Modern approach**: RESTful access to SAP data
- **Advantage**: Firewall-friendly, no RFC connector needed
- **Setup in Pega**:
  - Create HTTP service rule pointing to SAP OData endpoint
  - Map XML/JSON response to Pega page
  - OAuth token management for authentication
- **Common issues**: OData URL misconfiguration, expired tokens, entity path mismatch

## Connector Configuration Steps

1. **SAP System Entry**:
   - Navigate to Admin > System Settings > Third-Party System Settings
   - Add SAP system: host, instance, client, port

2. **Connection Testing**:
   - Use "Test Connection" button before saving
   - Monitor logs for RFC library errors
   - Verify network connectivity: `telnet <saphost> 3299`

3. **Data Mapping**:
   - Create mapping rules (Data-Pega-REST/SOAP-Adapter)
   - Handle SAP date format (YYYYMMDD) conversion
   - Map SAP amount fields (decimal vs. integer)

4. **Error Handling**:
   - Set up ABAP exception mappings
   - Create Pega exception handling activities
   - Log detailed trace for debugging

## SAP Integration Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Gateway/Dispatcher down | Start SAP gateway: `sapstartsrv` |
| Timeout (SOCKET_TIMED_OUT) | Network latency or SAP overload | Increase timeout, check SAP load |
| Authorization failed | Insufficient RFC privileges | Grant RFC authorization in SAP |
| Function not found | BAPI name typo | Validate via transaction SE37 in SAP |
| Data mapping mismatch | Type conversion error | Review SAP BAPI signature |
| IDoc posting failed | Invalid segment data | Check IDoc format, run BD10 reconciliation |

## Debugging Best Practices

- **Enable Pega Tracer** on SAP connector activities to capture request/response
- **Monitor SAP logs**: Check transaction SM21 (System Log) for errors
- **Use SAP RFC trace**: Transaction ST05 to monitor RFC calls
- **Test BAPI independently**: Use SAP transaction BAPI Test Console (transaction BAPI)
- **Network monitoring**: Use tcpdump or Wireshark to inspect RFC protocol
- **Performance tuning**: Enable connection pooling, batch IDoc processing

## Common Integration Gotchas

1. **Timezone handling**: SAP timestamps differ from Pega; always convert
2. **Character encoding**: SAP may use EBCDIC; ensure UTF-8 mapping
3. **Session management**: Some BAPI calls require stateful RFC connection
4. **Transaction isolation**: Multiple calls may need BAPI transaction wrapper
5. **Decimal precision**: SAP CURRENCY type requires special handling in Pega
"""
    },
    {
        "title": "Salesforce Integration with Pega",
        "url": "https://pega.doc/integration/salesforce",
        "content": """
# Salesforce Integration with Pega

## Overview
Pega connects to Salesforce via REST API, supporting OAuth 2.0, JWT bearer token flow, and bi-directional data sync. Salesforce connectors enable real-time case synchronization and data consistency.

## Authentication Methods

### OAuth 2.0 Flow (Recommended)
- **Setup in Salesforce**:
  - Create Connected App (Setup > Apps > App Manager > New)
  - Enable OAuth 2.0: Authorization Code flow
  - Set Redirect URI to Pega callback (e.g., `https://pega.instance/prweb/oauth/callback`)
  - Capture Client ID and Client Secret

- **Pega Configuration**:
  - Create OAuth connector in Admin > System Settings > Third-Party Systems
  - Paste Client ID and Client Secret
  - Test authentication; user is prompted to authorize Pega app
  - Tokens cached; automatic refresh on expiry

### JWT Bearer Token Flow (Service-to-Service)
- **Use when**: No interactive user approval needed
- **Setup**:
  - Create Self-Signed Certificate in Salesforce
  - Configure JWT issuer (typically `https://login.salesforce.com`)
  - Create custom auth rule in Pega with JWT token generation
  - Token expires in 5 minutes (renewed automatically)

## SOQL & Data Retrieval

### SOQL (Salesforce Object Query Language)
```
SELECT Id, Name, Email FROM Contact WHERE AccountId = '0012X00000IEXXX'
```

- **Pega Integration**:
  - Create HTTP service rule with SOQL in URL query param
  - Parse JSON response into Pega page
  - Handle pagination: use LIMIT/OFFSET or `nextRecordsUrl`

### Common SOQL Errors
- `INVALID_FIELD`: Column name typo — verify in Salesforce data model
- `MALFORMED_QUERY`: WHERE clause syntax — test in Salesforce SOQL IDE
- `EXCEEDED_ID_LIMIT`: Batch size too large — split into smaller queries
- `INVALID_TYPE`: Field type mismatch — review Salesforce schema

## Bi-Directional Sync

### One-Way Push (Pega → Salesforce)
- Trigger activity on Pega case save
- Call Salesforce REST API to insert/update records
- Handle HTTP response: check `success` and `errors` fields
- Retry logic: exponential backoff for failures

### Two-Way Sync (Pega ↔ Salesforce)
- **Outbound**: Pega events trigger Salesforce API calls
- **Inbound**: Salesforce outbound messages or webhooks trigger Pega
- **Reconciliation**: Periodic audit to detect sync gaps
- **Conflict resolution**: Last-write-wins or Pega-priority rule

### Event-Driven Architecture
- **Salesforce Platform Events**: Publish custom events from Salesforce
- **Pega MQ Listener**: Subscribe to events via Apache Kafka or JMS
- **Real-time notification**: Low-latency case updates

## Common Salesforce Integration Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired token | Regenerate OAuth token or JWT |
| 403 Forbidden | Insufficient Salesforce permissions | Grant object CRUD permissions to connected app user |
| 404 Not Found | Record ID invalid or deleted | Validate record exists before API call |
| 400 Bad Request | Malformed JSON or invalid field | Check API request schema, test in Postman |
| Rate limit exceeded (429) | Too many API calls per minute | Implement bulk API, batch requests, add throttling |
| Duplicate records | Sync logic creates duplicates | Implement upsert by external ID, deduplication logic |

## Debugging Authentication Errors

1. **OAuth token invalid**:
   - Check token expiration: `curl -H "Authorization: Bearer <token>" https://instance.salesforce.com/services/data/v57.0/`
   - Regenerate in Pega connector settings
   - Clear browser cache if using interactive OAuth

2. **Connected app not authorized**:
   - Verify IP whitelist in Connected App (if enabled)
   - Check Salesforce org API version matches Pega REST adapter
   - Test with Postman using same Client ID/Secret

3. **JWT token claims mismatch**:
   - Validate `iss` (issuer), `sub` (subject), `aud` (audience)
   - Check certificate expiration
   - Ensure system clock is synchronized

## Debugging Data Sync Errors

- **Enable Tracer on Salesforce activities**: Capture full HTTP request/response
- **Check Salesforce logs**: Monitor Setup > Monitoring > Debug Logs
- **Field mapping validation**: Verify Pega page structure matches Salesforce object schema
- **Test API manually**: Use Salesforce REST API Explorer or Postman collection

## Performance Tips

- **Batch operations**: Use Salesforce Bulk API 2.0 for large data loads
- **SOQL optimization**: Index frequently queried fields, avoid SELECT *
- **Rate limit management**: Implement adaptive throttling based on remaining quota
- **Connection pooling**: Reuse HTTP connections for multiple API calls
"""
    },
    {
        "title": "Database Integration — Direct SQL & Report Definitions",
        "url": "https://pega.doc/integration/database",
        "content": """
# Database Integration — Direct SQL & Report Definitions

## Overview
Pega integrates with external databases via JDBC (Java Database Connectivity) without requiring the data to be stored in Pega rules. Direct SQL activities and report definitions enable real-time queries against external data sources.

## JDBC Configuration

### Connection Setup
1. **Database Connection Details**:
   - Host, port, database name
   - JDBC URL format: `jdbc:oracle:thin:@hostname:port:dbname` (Oracle example)
   - Username/password with appropriate DML permissions

2. **Driver Configuration**:
   - Place JDBC driver JAR in Pega classpath: `PegaRULES/tomcat/lib/`
   - Verify driver class name: `oracle.jdbc.driver.OracleDriver` (Oracle)
   - Test connectivity before enabling in production

3. **Data Source Setup in Pega**:
   - Navigate to Admin > System Settings > Data Source
   - Create Data Source rule
   - Test connection: "Test Connection" button
   - Common error: "No suitable driver" — verify JAR in classpath and restart

### Connection Pooling
- **Why**: Reuse connections, reduce overhead
- **Configuration in Pega**:
  - Set min pool size: typically 5-10 connections
  - Set max pool size: based on database connections available (e.g., 50)
  - Connection timeout: 30-60 seconds
  - Idle timeout: 300-600 seconds
- **Monitoring**: Check connection pool utilization in Admin > System Monitoring

## External Database Class Mapping

### Setting Up External DB Class
1. **Create External Data Class**:
   - Class type: "External database"
   - Map class properties to database columns
   - Define primary key (for updates/deletes)

2. **Property Mapping**:
   - Property name ↔ Column name
   - Data type conversion: Pega Text → Oracle VARCHAR2
   - Required fields: mark with asterisk

3. **Query Mapping**:
   - Define SELECT statement
   - Add filters, joins, ORDER BY
   - Example:
     ```sql
     SELECT CustomerID, CustomerName, Email, PhoneNumber
     FROM Customers
     WHERE Country = ?
     ORDER BY CustomerName
     ```

## Direct SQL in Activities

### Using SQL Activities
- **Best for**: Complex queries, aggregations, data that doesn't fit class mapping
- **Syntax**: Create SQL activity with explicit SELECT/INSERT/UPDATE/DELETE
- **Parameter binding** (to prevent SQL injection):
  ```
  SELECT * FROM Orders WHERE OrderID = :1 AND CustomerID = :2
  ```
  Bind parameters in activity: `objPage.GetDatabase().SQLExecute(sql, param1, param2)`

### Common SQL Activity Mistakes
1. **SQL Injection vulnerability**: Never concatenate user input into SQL
   ```sql
   -- WRONG: SELECT * FROM Users WHERE Name = '" + userName + "'
   -- RIGHT: SELECT * FROM Users WHERE Name = ?
   ```

2. **Missing transaction handling**: Wrap multi-statement SQL in transaction
   ```
   BEGIN TRANSACTION
   UPDATE Table1 SET ...
   UPDATE Table2 SET ...
   COMMIT
   ```

3. **Timeout issues**: Complex queries on large tables hang
   - Add query hints/indexes
   - Limit result set with WHERE clause
   - Implement pagination

## Report Definitions Against External DB

### Creating External Data Report
1. **Data Source**: Select external database class
2. **Columns**: Choose columns to display from external table
3. **Filters**: Add WHERE clause conditions
4. **Sorting**: Define default sort order
5. **Pagination**: Set rows per page (typically 25-100)

### Report Performance Optimization
- **Indexes**: Ensure indexed columns in WHERE/ORDER BY clauses
- **Query complexity**: Avoid expensive JOINs in report definition
- **Caching**: Mark report as cacheable if data changes infrequently
- **Pagination depth**: Limit ability to jump to page 1000 (slow on large tables)

## Database Connectivity Issues & Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Database service down | Verify DB service is running, check hostname/port |
| Invalid username/password | Auth credentials wrong | Test credentials with DB client tool (SQL*Plus, MySQL CLI) |
| Connection timeout | Firewall blocking | Open DB port in firewall, verify network route |
| No suitable driver | JDBC JAR missing | Add driver JAR to classpath, restart Pega |
| Out of memory | Connection pool leak | Check if connections are properly closed, review connection usage |
| Stale connection | Connection dropped by DB | Enable connection validation (SELECT 1 query) |
| Deadlock detected | Concurrent transaction conflict | Review transaction isolation level, reduce lock time |

## Debugging Database Integration

1. **Connection Testing**:
   - Use Pega Admin Tool > Test Connection
   - Test with external DB client: `sqlplus user/password@hostname:port/dbname` (Oracle)
   - Verify firewall with telnet: `telnet hostname port`

2. **Query Debugging**:
   - Enable Pega Tracer on SQL activities
   - Check Pega log: Admin > System Monitoring > Logs
   - Capture actual SQL sent: Check database query log (e.g., `V$SQL` in Oracle)
   - Execution plan analysis: Test query in DB IDE, check explain plan

3. **Connection Pool Monitoring**:
   - Admin > System Monitoring > Data Source Statistics
   - Monitor active/idle connections over time
   - Alert on connection exhaustion

## Best Practices

- **Data freshness**: Cache external DB results if real-time not required
- **Failover**: Configure connection to read replica if primary DB unavailable
- **Row limits**: Always add LIMIT/TOP clause to prevent runaway queries
- **Backup**: External DB queries should not be critical path for case progress
- **Audit**: Log all external database operations for compliance
"""
    },
    {
        "title": "Legacy System Integration — Mainframe, AS/400, CICS",
        "url": "https://pega.doc/integration/legacy",
        "content": """
# Legacy System Integration — Mainframe, AS/400, CICS

## Overview
Pega integrates with mainframe and AS/400 systems through MQ/JMS connectors, CICS Transaction Gateway (CTG), and screen scraping. Each approach has trade-offs in cost, maintenance, and modernization path.

## Mainframe Integration via MQ (Message Queue)

### IBM MQ Overview
- **Use case**: Asynchronous messaging with legacy mainframe apps
- **Advantage**: Decoupled, reliable message delivery, supports transactional semantics
- **Flow**: Pega → MQ Queue Manager → Mainframe CICS/Batch program

### MQ Configuration in Pega
1. **Queue Manager Connection**:
   - Create MQ Connector rule in Admin > System Settings > Third-Party
   - Specify Queue Manager name, host, port (typically 1414)
   - Transport type: TCP/IP
   - Channel name (e.g., `SYSTEM.DEF.SVRCONN`)

2. **Queue Setup**:
   - Local queues for sending: Input queue on mainframe system
   - Reply-to queue for responses: Pega-specific queue for mainframe replies
   - Dead-letter queue: Fallback for undeliverable messages

3. **Message Format**:
   - Define message schema (COBOL copybook structure in binary or text)
   - Create mapping: Pega page → MQ message bytes
   - Handle EBCDIC encoding (mainframe) ↔ ASCII (Pega)

### JMS Bridge (Java Message Service)
- **Alternative to native MQ**: JMS provides abstraction over MQ, ActiveMQ, others
- **Pega JMS integration**:
  - Create JMS connector with connection factory details
  - Define topic or queue name
  - Map incoming JMS messages to Pega pages
  - Implement message listener for async processing

## CICS Transaction Gateway (CTG)

### CTG Overview
- **What is it**: IBM middleware that exposes CICS transactions to remote clients
- **Advantage**: Direct call to CICS programs (synchronous), lower latency than MQ
- **Disadvantage**: Requires license, network connectivity must be stable

### CTG Configuration Steps
1. **Install and configure CTG server**:
   - CTG server runs on z/OS or x86 Linux
   - Exposes CICS transactions via IP

2. **Pega-side setup**:
   - Download CTG client library (jar files) to Pega classpath
   - Create CTG Connector rule
   - Specify CTG server host, port, and CICS region name
   - Test connection

3. **Calling CICS Programs**:
   - Create activity to call CICS transaction
   - Program name: e.g., `ORDENTRY` (CICS program name)
   - Input/output data mapping:
     ```
     COBOL COPYBOOK MAPPING:
     01 ORDER-REQUEST.
       05 ORDER-ID      PIC 9(8).
       05 CUSTOMER-NAME PIC X(30).
       05 ORDER-AMOUNT  PIC 9(7)V99.
     ```
   - Pega maps Request/Response page structures to COBOL layouts

## AS/400 Integration

### Accessing AS/400 (IBM iSeries)
- **Protocol**: IBM Secure Sockets Layer (SSL) over port 9445 or unencrypted 9440
- **Access methods**:
  - Java Toolbox for i (JTBx): JDBC drivers, Program Call service
  - Native SQL: Query data files directly
  - Service programs: Call ILE programs

### Setup Example
```
Create Java Service rule:
  Class: com.ibm.as400.access.AS400
  Constructor params: hostname, username, password
  Create connection: AS400 obj = new AS400(host, user, pwd)
  Call service program: ProgramCall pgm = new ProgramCall(as400obj)
```

### Data Access
- Create external data class mapping to AS/400 file
- SQL: Query logical/physical files
- Avoid: Direct access to QTEMP (temporary files)

## Screen Scraping vs Modernization

### When Screen Scraping Applies
- **Legacy mainframe**: No API available, transaction-driven UI
- **Example**: CICS screens with 3270 emulation
- **Tool**: Pega supports screen scraping plugins (e.g., UiPath, Blue Prism integration)

### Screen Scraping Risks
1. **Brittle**: Screen layout changes break automation
2. **Maintenance**: Constant updates as legacy system evolves
3. **Performance**: Slow compared to API-based integration
4. **Error handling**: Difficult to detect failures (e.g., error message on screen)

### Modernization Path
- **Encapsulation**: Wrap mainframe logic in middleware API
- **Service-oriented**: Extract mainframe functions into SOA services
- **Strangler pattern**: Gradually replace legacy with Pega workflows

## COBOL Copybook Data Mapping

### Converting COBOL to Pega Structure
**COBOL Copybook Example**:
```cobol
01 EMPLOYEE-RECORD.
  05 EMP-ID          PIC 9(6).
  05 EMP-NAME        PIC X(30).
  05 SALARY-INFO.
    10 BASE-SALARY   PIC 9(7)V99.
    10 BONUS         PIC 9(7)V99.
  05 HIRE-DATE       PIC 9(8).
```

**Pega Page Structure**:
```
EmployeeRecord (page)
  ├─ EmpID (integer, 6 digits)
  ├─ EmpName (text, max 30 chars)
  ├─ SalaryInfo (page)
  │  ├─ BaseSalary (decimal)
  │  └─ Bonus (decimal)
  └─ HireDate (datetime, format YYYYMMDD)
```

### Mapping Tips
- **Numeric**: PIC 9(n) → Integer or Decimal in Pega
- **Text**: PIC X(n) → Text property
- **Date**: PIC 9(8) YYYYMMDD → Pega datetime with custom formatter
- **Nested groups**: PIC with indentation → Nested page structures
- **Occurs clause**: PIC ... OCCURS 100 → Pega Page List

## Common Legacy Integration Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | MQ/CTG server down | Verify service running, check host/port |
| Character encoding error | EBCDIC vs ASCII mismatch | Apply EBCDIC-to-ASCII codec in mapping |
| Message format error | Copybook structure mismatch | Validate exact byte positions and padding |
| Timeout on mainframe call | Slow legacy transaction | Increase timeout, check mainframe load |
| Dead-letter queue buildup | Poison message in queue | Manual inspection, replay valid messages |
| CICS ABEND on call | Invalid program call params | Check CTG server logs, validate input data |

## Debugging Strategies

1. **MQ Message Inspection**:
   - Use MQ Explorer: View queue depth, browse messages
   - Check message properties: Timestamp, correlation ID, format

2. **CTG Tracing**:
   - Enable CTG client trace: `tc.properties` file in classpath
   - Monitor CICS transaction trace: Mainframe CESL utility

3. **Mainframe Logs**:
   - Check CICS log: CEDF transaction execution diagnostics
   - MVS syslog for connection errors

4. **Pega-side Debugging**:
   - Enable Tracer on legacy integration activities
   - Check Pega application log for mapping errors
   - Monitor MQ listener for queue backlog
"""
    },
    {
        "title": "Pega Process Fabric",
        "url": "https://pega.doc/integration/process-fabric",
        "content": """
# Pega Process Fabric

## What is Process Fabric?

### Definition
Process Fabric is Pega's distributed case management platform that enables **cross-application process visibility** and **federated case management**. It connects independent Pega applications (or external services) into a unified workflow ecosystem while maintaining data sovereignty and operational independence.

### Key Concepts
- **Federated cases**: A parent case spans multiple Pega applications
- **Case orchestration**: Automatic routing between applications based on business rules
- **Process visibility**: Real-time view of process state across all connected systems
- **Decoupled architecture**: Each app maintains its own database and business logic

## When to Use Process Fabric

### Use Cases
1. **Multi-application enterprise**: Large organizations with multiple Pega apps (Sales, Service, HR)
2. **Partner ecosystems**: Extend workflows to external partner systems via APIs
3. **Microservices architecture**: Decompose monolithic BPM into independent services
4. **Regulatory compliance**: Maintain audit trail across organizational boundaries
5. **Digital transformation**: Gradually migrate from legacy to Pega without big-bang cutover

### Not Suitable For
- Simple single-app cases (overhead not justified)
- High-frequency real-time integrations (latency considerations)
- Tight data consistency requirements (eventual consistency model)

## Process Fabric Architecture

### Components
- **Orchestrator**: Central Process Fabric service (runs in Pega infra)
- **Connector Apps**: Individual Pega applications connected to Fabric
- **Case Repository**: Shared metadata about case structure (not data storage)
- **Event Bus**: Async messaging between apps (Kafka, MQ, etc.)

### Data Flow
```
App A (Sales) → Fabric Connector → Event Bus → Fabric Connector → App B (Service)
  (Case created)                                                     (Receive case)
```

## Process Fabric Configuration

### Step 1: Enable Process Fabric
- Admin > System Settings > Process Fabric Configuration
- Register Orchestrator URL (central Pega deployment)
- Specify organizational unit and tenant identifier
- Test connectivity: "Test Fabric Connection"

### Step 2: Configure Case for Fabric
- Case type properties:
  - "Expose to Process Fabric": Yes
  - "Fabric primary key": Usually pxRefObjectKey
  - "Fabric context": Define which properties sync across apps
  - "Replication rules": Which app "owns" which properties

### Step 3: Define Process Fabric Assignments
- Create work assignments that route to external apps
- Example:
  ```
  Order Case → Sales App processes → [Fabric decision] → Service App for support
  ```
- Use Fabric decision shapes in process flow diagrams
- Map assignment targets to remote applications

### Step 4: Event Mapping & Subscription
- **Publish events**: Define what case events (create, update, close) are published to Fabric
- **Subscribe events**: Define which events from other apps this app listens to
- **Transform data**: Map external app data schema to local case structure
- **Exception handling**: Define behavior on sync failures

## Cross-Application Process Visibility

### Unified Case Dashboard
- Single view of all cases in Fabric ecosystem
- Real-time status from each connected app
- Custom dashboards aggregating across apps
- Fiber-level KPI visibility (not just single-app metrics)

### Case Linking & Hierarchy
- Link parent case (e.g., Customer Support) to child cases (e.g., Multiple Service Requests)
- View complete case ancestry and relationships
- Trace decisions made in upstream applications

### Audit & Compliance
- Immutable event log across all applications
- Compliance reporting with cross-app data
- Regulatory evidence of process execution across org

## Federated Cases Example

### Order-to-Cash Process
```
Customer Order (Sales App)
  ↓ [Fabric sync]
  Fulfillment Request (Operations App)
    ↓ [Fabric sync]
    Delivery Tracking (Logistics Partner)
      ↓ [Fabric sync]
      Billing & Collections (Finance App)
```

Each app independent; Process Fabric ensures:
- Order updates propagate to Fulfillment
- Fulfillment status reflected in Billing
- Any app can query complete order state

## Monitoring Distributed Processes

### Process Fabric Dashboard
- Admin > System Monitoring > Process Fabric Health
- Monitor:
  - Event delivery latency (avg, max, p99)
  - Event loss/retry metrics
  - Connector app connectivity status
  - Fabric orchestrator resource utilization

### Event Debugging
- Query event log: Which events published/failed
- Check event schema validation
- Review data transformation errors in middleware logs

### Performance Tuning
- Batch event publishing (reduce latency spike)
- Configure event replay policy (on failure)
- Set TTL on events (prevent stale data processing)

## Common Process Fabric Setup Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Apps not discovering each other | Orchestrator connection down | Verify Orchestrator accessible, check firewall |
| Event sync lag (minutes delay) | Event bus backlog | Check Kafka/MQ capacity, increase consumer threads |
| Data inconsistency across apps | Replication rule conflict | Review ownership rules, implement reconciliation |
| Event loss | Message broker failure | Enable persistence, check broker status |
| Case not visible in Fabric | Case not exposed to Fabric | Enable "Expose to Process Fabric" in case type |

## Best Practices

1. **Design for eventual consistency**: Expect delays between apps; don't require strong consistency
2. **Idempotent events**: Events may be replayed; ensure duplicate processing is safe
3. **Versioning**: Update event schema carefully; support multiple versions during transition
4. **Monitoring**: Invest in observability across app boundaries
5. **Testing**: Test entire federated case flow end-to-end, not just single app
6. **Governance**: Define clear ownership: which app owns which data domain
7. **Rollback strategy**: Plan how to operate if Fabric connector fails (fallback mode)
"""
    },
    {
        "title": "Pega App Studio vs Dev Studio — When to Use Which",
        "url": "https://pega.doc/tools/app-studio-vs-dev-studio",
        "content": """
# Pega App Studio vs Dev Studio — When to Use Which

## Overview

### App Studio
- **Audience**: Citizen developers, business analysts
- **Approach**: Low-code, visual, configuration-first
- **Time-to-value**: Fast (days to weeks)
- **Customization**: Limited to pre-built components
- **Maintenance**: Easier for business teams

### Dev Studio
- **Audience**: System architects, software engineers
- **Approach**: Pro-code, text-based, unlimited customization
- **Time-to-value**: Slower (weeks to months)
- **Customization**: Unlimited (Java, XML, proprietary languages)
- **Maintenance**: Requires technical expertise

## Feature Comparison Matrix

| Feature | App Studio | Dev Studio |
|---------|-----------|-----------|
| **Case Types** | Visual builder | XML/Java |
| **Stages & Steps** | Drag-drop | Rules + code |
| **Forms** | Template-based | Custom HTML/CSS |
| **Workflows** | Process flows (visual) | Flows + activities |
| **Validations** | UI rules | Code + rules |
| **Integrations** | Pre-built connectors | Full API access |
| **Expressions** | Simple formulas | Python/JavaScript/Java |
| **Database queries** | Report definitions | Direct SQL |
| **Custom components** | No | Yes (Java classes) |
| **Performance tuning** | Limited | Full control |

## What You Can ONLY Do in Dev Studio

### Advanced Technical Features
1. **Custom Java classes and adapters**:
   - Extend Pega base classes
   - Implement custom connectors
   - Create reusable utility libraries

2. **Direct rule development**:
   - Activities (multi-step processes)
   - Flows (complex routing logic)
   - Decision tables (complex branching)
   - Strategies (load-balancing)

3. **Database access**:
   - Direct SQL activities
   - External database classes
   - Custom SQL report definitions
   - Database triggers

4. **System administration**:
   - Access control (granular security rules)
   - Custom data model design
   - Performance tuning
   - Tracer and debugging tools

5. **Advanced customizations**:
   - JavaScript/HTML custom controls
   - Pixel-perfect form designs
   - Browser API integration
   - Custom theme development

6. **Integration deepening**:
   - Custom authentication handlers
   - Complex data mappers
   - Message transformers
   - Error recovery logic

## What's Easier in App Studio

### Business-Friendly Features
1. **Rapid case type creation**:
   - Wizard-based case builder
   - Pre-built stage templates
   - Auto-generated forms from case fields

2. **Low-code workflow automation**:
   - Process flow designer (point-click routing)
   - Assignment rules (visual)
   - Approval workflows (no coding)

3. **Business-managed content**:
   - Portal configuration
   - Widget customization
   - Dashboard building
   - Portal pages (no HTML)

4. **Data management**:
   - Record types (structured data)
   - Data objects (non-case entities)
   - Import/export tools
   - Data sync (built-in)

5. **Security & governance**:
   - Role-based access (UI-driven)
   - Delegation (self-service)
   - Audit logs (automated)

## Common Confusion Points

### Myth 1: "App Studio is only for prototyping"
**Reality**: App Studio is production-ready for many use cases. Large enterprises use it for standard processes.

### Myth 2: "Dev Studio is always better"
**Reality**: Dev Studio is slower to implement and maintain. Use it only when App Studio limitations are encountered.

### Myth 3: "You can't mix App Studio and Dev Studio"
**Reality**: Hybrid approach is common. Build 80% in App Studio, use Dev Studio for 20% custom logic.

### Myth 4: "App Studio can't handle complex workflows"
**Reality**: App Studio process flows handle multi-branch logic, parallel paths, and business rules.

### Myth 5: "Dev Studio apps perform better"
**Reality**: Performance depends on implementation, not the tool. Poorly written Dev Studio code is slow; well-built App Studio is fast.

## Decision Matrix: App Studio vs Dev Studio

```
START HERE
↓
Is requirement within App Studio pre-built capabilities?
├─ YES → Use App Studio
│        (faster, easier maintenance, less expensive)
│
├─ NO → Is custom Java/SQL/code required?
        ├─ YES → Use Dev Studio
        │        (need programmatic control)
        │
        └─ NO → Use App Studio + light Dev Studio extensions
                 (hybrid approach, best of both worlds)
```

## Hybrid Approach (Recommended for Complex Apps)

### Strategy
1. **App Studio**: Case type, stages, basic forms, standard workflows
2. **Dev Studio**: Custom data mappers, complex validations, integrations
3. **Integration point**: Call Dev Studio activities from App Studio flows

### Example: Insurance Claims Processing
```
App Studio builds:
  - Claim case type with stages (submitted, reviewed, approved, paid)
  - Standard assignment workflows
  - Pre-built approval forms

Dev Studio extends with:
  - Custom fraud detection algorithm (Java)
  - Integration with 3rd-party claims verification service
  - Complex pricing calculation (SQL + Python expression)

Integration:
  App Studio workflow calls Dev Studio "CheckFraud" activity
  Result feeds into App Studio routing decision
```

## Transitioning Between Studios

### App Studio → Dev Studio Upgrade
- **When**: Business requirements exceed App Studio capabilities
- **Process**:
  1. Export case definition from App Studio
  2. Convert to Dev Studio rules (semi-automated)
  3. Extend with custom Dev Studio rules
  4. Testing & validation

- **Gotcha**: Not all App Studio features export cleanly; manual work required

### Dev Studio → App Studio (Rare)
- **When**: Simplifying legacy complex app
- **Approach**: Refactor to use App Studio patterns where possible

## Performance Considerations

### App Studio Performance
- Pre-optimized for standard use cases
- Form rendering faster (templates)
- Workflow evaluation optimized
- Auto-caching enabled

### Dev Studio Performance
- Performance depends on implementation quality
- Raw SQL can be faster or slower than abstraction
- Custom Java classes must be tuned manually
- No built-in safety rails; easy to create performance problems

### Benchmarking
- App Studio case processing: ~50-200ms per action
- Dev Studio (well-tuned): ~30-150ms per action
- Dev Studio (poorly tuned): >1 second, potential bottlenecks

## Migration & Coexistence

### Can Apps Coexist?
- Yes: Single Pega environment can run App Studio and Dev Studio apps
- Common pattern: New features in App Studio, legacy monolith in Dev Studio

### Integration
- App Studio apps call Dev Studio services via REST connectors
- Dev Studio apps embed App Studio case management (advanced)
- Shared case types possible (with caution)

## Practical Decision Examples

### Scenario 1: Employee Onboarding
- **Best tool**: App Studio
- **Reason**: Standard workflow (pre-hire → hire → training → productive), pre-built HR connectors, minimal custom logic
- **Effort**: 2-3 weeks (vs. 2 months in Dev Studio)

### Scenario 2: Complex Insurance Underwriting
- **Best tool**: Hybrid (App Studio + Dev Studio)
- **App Studio**: Case type, stages, forms
- **Dev Studio**: Risk scoring algorithm, 3rd-party integration, rule engine
- **Effort**: 6-8 weeks hybrid (vs. 3-4 months pure Dev Studio)

### Scenario 3: Real-Time Financial Trading System
- **Best tool**: Dev Studio
- **Reason**: Sub-second latency requirements, complex mathematical models, legacy data integration
- **App Studio limitations**: Not optimized for high-frequency operations
- **Effort**: 3-4 months

## Maintenance & Support

### App Studio Advantages
- Non-developers can make bug fixes
- Changes deploy faster (immediate in cloud)
- Lower training overhead
- Vendor support covers most scenarios

### Dev Studio Advantages
- Leverage existing developer skills
- Fine-grained control for edge cases
- Easier version control & CI/CD
- Open to external libraries

## Recommendation Summary

**Use App Studio for**:
- Rapid MVP delivery
- Standard business processes
- Citizen-developer maintainability
- Clear ROI requirement

**Use Dev Studio for**:
- Algorithmic complexity
- Performance-critical systems
- Novel integrations
- Regulated industries with audit trails

**Use Hybrid for**:
- Most enterprise applications
- Balancing speed & customization
- Leveraging best of both platforms
"""
    }
]

def seed_phase15():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE15:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase15_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE15)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 15 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase15()
