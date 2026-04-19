"""
Curated Pega Knowledge Base — Phase 6 (Conceptual & Comparison Content)
Covers: SOAP vs REST, Activity vs Data Transform, Rule Types Guide,
        Data Page Scopes, Pega Architecture Overview, Design Patterns,
        When Rules vs Declare Rules, Case Types vs Data Types,
        Integration Patterns, Security Concepts

Run: python -m crawler.seed_kb_phase6
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE6 = [
    {
        "url": "curated://pega-soap-vs-rest",
        "title": "SOAP vs REST in Pega — Security, Performance, and When to Use Which",
        "content": """# SOAP vs REST in Pega — Comparison Guide

## Overview
Pega supports both SOAP and REST for integrations (connectors and services). Choosing between them depends on security requirements, performance needs, and the systems you're integrating with.

## Security Comparison

### SOAP Security
- **WS-Security**: Built-in standard for message-level security (encryption + signing of individual XML elements)
- **Message-level encryption**: The SOAP body can be encrypted independently of the transport layer — the message stays encrypted even if intercepted after TLS termination
- **XML Digital Signatures**: Individual parts of the message can be signed, providing non-repudiation
- **WS-SecureConversation**: Establishes a security context for multiple message exchanges
- **SAML tokens**: Can carry identity assertions inside the SOAP header
- **Summary**: SOAP has MORE GRANULAR security — you can encrypt/sign specific fields within a message

### REST Security
- **Transport-level security**: Relies on HTTPS/TLS for encryption — protects data in transit but not at rest or after TLS termination
- **OAuth 2.0 / OpenID Connect**: Standard for authorization and authentication
- **API Keys**: Simple but less secure — key is sent with every request
- **JWT tokens**: Signed tokens for stateless authentication
- **No built-in message-level encryption**: You'd need to implement field-level encryption yourself
- **Summary**: REST security is SIMPLER and sufficient for most modern applications

### Which is More Secure?
**SOAP offers stronger built-in security features** — specifically message-level encryption and XML digital signatures. This matters when:
- Messages pass through intermediaries (ESBs, message queues) where TLS is terminated
- You need non-repudiation (proof that a specific party sent a specific message)
- Regulatory requirements mandate message-level encryption (financial services, healthcare)

**REST with HTTPS is secure enough for most use cases** — especially for direct point-to-point communication. REST + OAuth 2.0 + TLS is the modern standard and is considered secure for the vast majority of applications.

**Bottom line**: SOAP is not inherently "more secure" — it has more security OPTIONS built into the standard. REST achieves equivalent security with proper implementation (HTTPS + OAuth 2.0 + field-level encryption where needed).

## Performance Comparison
| Aspect | SOAP | REST |
|--------|------|------|
| Payload size | Larger (XML envelope overhead) | Smaller (JSON, no envelope) |
| Parsing speed | Slower (XML parsing) | Faster (JSON parsing) |
| Caching | Not cacheable (POST only) | Cacheable (GET requests) |
| Bandwidth | Higher | Lower |
| Statelessness | Can be stateful (WS-*) | Stateless by design |

## When to Use SOAP in Pega
1. Integrating with legacy enterprise systems (SAP, mainframes) that only support SOAP
2. When WS-Security message-level encryption is required by regulation
3. When you need formal contracts (WSDL) for strict API governance
4. Financial services integrations requiring non-repudiation

## When to Use REST in Pega
1. Modern API integrations (cloud services, SaaS platforms)
2. Mobile/web applications (lighter payload, faster)
3. Microservices communication
4. When you need caching for read-heavy operations
5. Public APIs (REST is the de facto standard)

## Pega Configuration
- **SOAP Connector**: Integration → Connectors → SOAP. Import WSDL to auto-generate.
- **REST Connector**: Integration → Connectors → REST. Configure endpoint, method, headers.
- **SOAP Service**: Expose Pega functionality via WSDL for external SOAP consumers.
- **REST Service (Service REST)**: Expose Pega functionality as REST API endpoints.
"""
    },
    {
        "url": "curated://pega-activity-vs-data-transform",
        "title": "Activity vs Data Transform — When to Use Which in Pega",
        "content": """# Activity vs Data Transform — When to Use Which

## Overview
Both Activities and Data Transforms manipulate data in Pega, but they serve different purposes and have different capabilities. Pega best practice strongly favors Data Transforms for data manipulation.

## Data Transforms
- **Purpose**: Set, copy, and transform property values declaratively
- **How they work**: Visual rule with rows that map source → target properties
- **Execution**: Runs synchronously, modifying the clipboard
- **Debugging**: Easy — each row shows source/target, can use Tracer
- **Reusability**: Can call other Data Transforms (chaining)
- **Guardrails**: Pega RECOMMENDS Data Transforms for data manipulation

### When to Use Data Transforms
1. Setting default values on case creation
2. Copying data between pages (e.g., customer data → case data)
3. Mapping integration response to Pega properties
4. Transforming data formats (date formatting, string manipulation)
5. Initializing pages and page lists
6. Any data manipulation that doesn't need Java, external calls, or database operations

## Activities
- **Purpose**: General-purpose procedural logic (like a scripting language)
- **How they work**: Step-by-step methods with Java snippets, built-in methods
- **Execution**: Can be synchronous or asynchronous
- **Debugging**: Harder — step through in Tracer, Java errors can be cryptic
- **Capabilities**: Can do EVERYTHING — Java, database calls, external calls, file I/O, commits
- **Guardrails**: Pega says AVOID Activities when a declarative alternative exists

### When to Use Activities (and ONLY activities)
1. **Database operations**: Direct SQL, obj-Save, obj-Delete, obj-Open
2. **Java code**: When you need custom Java logic
3. **External system calls**: When connector rules don't fit
4. **Commit/save control**: When you need explicit save/commit points
5. **Queue processors**: Processing items from a queue
6. **Agents**: Background processing tasks
7. **Complex looping**: When Data Transform iteration isn't sufficient
8. **File operations**: Reading/writing files
9. **Sending emails programmatically**: Using the Email-Thread method

## Key Differences
| Aspect | Data Transform | Activity |
|--------|---------------|----------|
| Guardrail score | Good (recommended) | Poor (if used for data manipulation) |
| Complexity | Simple, declarative | Complex, procedural |
| Java required | No | Often yes |
| Can save to DB | No | Yes (obj-Save) |
| Can call connectors | No | Yes |
| Can commit | No | Yes |
| Performance | Fast | Varies (can be slow) |
| Testable | Easy | Harder |
| Maintainability | High | Lower |

## Common Mistake
Using an Activity to set property values when a Data Transform would work. This is a **guardrail violation** and shows up in Pega's Application Guardrails report. If your Activity only has Property-Set methods, replace it with a Data Transform.

## Migration Path
If you have Activities that only do data manipulation:
1. Create a new Data Transform with the same class
2. Recreate the property mappings as Data Transform rows
3. Update all callers to use the Data Transform
4. Delete the old Activity
5. Re-run guardrails to verify improvement
"""
    },
    {
        "url": "curated://pega-rule-types-guide",
        "title": "Pega Rule Types — Complete Guide to When to Use Which Rule",
        "content": """# Pega Rule Types — When to Use Which

## Overview
Pega has hundreds of rule types. Choosing the right one is critical for maintainability, performance, and guardrail compliance. This guide covers the most important rule types and when to use each.

## Data Manipulation Rules
- **Data Transform**: Set/copy/transform property values (USE THIS FIRST)
- **Activity**: Procedural logic with Java, DB ops, external calls (use as last resort)
- **Declare Expression**: Auto-calculate a property value whenever inputs change
- **Declare OnChange**: Trigger actions when a property value changes
- **Map Value**: Look up a value from a mapping table (like a switch/case)

## Decision Rules
- **When Rule**: Boolean condition (true/false) — use for visibility, validation, routing
- **Decision Table**: Multiple conditions → single result (like a lookup table)
- **Decision Tree**: Hierarchical if/else logic with branches
- **Map Value**: Simple key → value mapping
- **Decision Shape (in Flow)**: Route the flow based on conditions

### When to Use Which Decision Rule
- Simple yes/no? → **When Rule**
- Multiple inputs, one output, flat logic? → **Decision Table**
- Multiple inputs, one output, hierarchical logic? → **Decision Tree**
- Simple key-to-value lookup? → **Map Value**

## UI Rules
- **Section**: Reusable UI component (form, panel, layout)
- **Flow Action**: Screen in a workflow (what the user sees at an assignment)
- **Harness**: Page template (portal layout)
- **Dynamic Layout**: Responsive container that adapts to screen size
- **Paragraph**: Rich text template for display

## Process Rules
- **Flow**: Visual workflow definition (the case lifecycle)
- **Case Type**: Defines a business process (top-level container)
- **Stage**: High-level phase of a case (e.g., Create → Review → Resolve)
- **Step**: Individual action within a stage
- **SLA**: Service Level Agreement (urgency, deadline, escalation)

## Integration Rules
- **Connect REST**: Call an external REST API
- **Connect SOAP**: Call an external SOAP service
- **Service REST**: Expose a Pega REST endpoint
- **Service SOAP**: Expose a Pega SOAP endpoint
- **Data Page**: Cache data from any source (DB, connector, activity)
- **Data Transform**: Map external data to Pega properties

## Declarative Rules (Auto-Execute)
- **Declare Expression**: Forward-chaining calculation (auto-updates when inputs change)
- **Declare Constraint**: Validation that's always active
- **Declare OnChange**: Trigger when a property changes
- **Declare Trigger**: Fire an activity on database events (save, delete)
- **Declare Index**: Expose properties for reporting

## Best Practices for Rule Selection
1. **Always prefer declarative over procedural** — Declare Expression over Activity-based calculation
2. **Use Data Transforms over Activities** for data manipulation
3. **Use When Rules over Java conditions** in flows and UI
4. **Use Decision Tables over nested When Rules** for complex logic
5. **Use Data Pages over Activities** for data access (caching, reuse)
6. **Check guardrails** — Pega's guardrail report tells you when you've used the wrong rule type
"""
    },
    {
        "url": "curated://pega-data-page-scopes",
        "title": "Data Page Scopes — Thread, Requestor, Node — When to Use Which",
        "content": """# Data Page Scopes — When to Use Which

## Overview
Data Pages in Pega cache data at different scopes. Choosing the right scope affects performance, memory usage, and data freshness. This is one of the most common areas where developers make mistakes.

## Scope Types

### Thread Scope
- **Lifetime**: Exists only during the current interaction (one flow execution)
- **Visibility**: Only the current thread/flow can see it
- **Memory**: Freed when the flow/interaction ends
- **Use when**: Data is specific to the current case or interaction
- **Examples**: Current case details, user's form input, case-specific lookup data

### Requestor Scope
- **Lifetime**: Exists for the entire user session (until logout or timeout)
- **Visibility**: All threads within the same user session can see it
- **Memory**: Freed when the session ends
- **Use when**: Data is user-specific but needed across multiple interactions
- **Examples**: Current user's profile, user's role/permissions, user preferences, operator details

### Node Scope
- **Lifetime**: Exists as long as the server node is running
- **Visibility**: ALL users on the same node share the same data page instance
- **Memory**: Persists in server memory — be careful with large datasets
- **Use when**: Data is the same for all users and changes rarely
- **Examples**: Dropdown options (country list, state list), configuration settings, exchange rates, reference data

## Common Mistakes

### 1. Using Node Scope for User-Specific Data
**Problem**: All users see the same data — first user's data gets cached and shown to everyone
**Symptom**: User A sees User B's data
**Fix**: Change to Requestor or Thread scope

### 2. Using Thread Scope for Reusable Data
**Problem**: Data is fetched repeatedly for every interaction, killing performance
**Symptom**: Slow page loads, excessive database queries
**Fix**: Change to Requestor scope (user-specific) or Node scope (shared)

### 3. Node Scope with Large Datasets
**Problem**: Large dataset cached in memory for the entire server lifetime
**Symptom**: OutOfMemoryError, server performance degradation over time
**Fix**: Add pagination, reduce dataset size, or change to Requestor scope with shorter timeout

### 4. Forgetting to Set Refresh Strategy
**Problem**: Node-scoped data page never refreshes — stale data served indefinitely
**Fix**: Set a reload interval (e.g., reload every 60 minutes) or use "Reload once per interaction"

## Decision Guide
| Question | Answer | Recommended Scope |
|----------|--------|-------------------|
| Is the data same for all users? | Yes | Node |
| Is the data user-specific? | Yes | Requestor |
| Is the data case-specific? | Yes | Thread |
| Does the data change frequently? | Yes | Thread or Requestor with short timeout |
| Is the dataset very large? | Yes | Thread (don't cache long-term) |
| Is it dropdown/reference data? | Yes | Node |

## Performance Impact
- **Thread**: Lowest memory, highest DB load (fetches every time)
- **Requestor**: Medium memory, medium DB load (fetches once per session)
- **Node**: Highest memory, lowest DB load (fetches once for all users)

## Debugging Data Page Scope Issues
1. **Check clipboard**: Use Clipboard tool to see which data pages exist and their scope
2. **Check Tracer**: Look for data page load events — too many loads = wrong scope
3. **Check PAL**: Performance Analyzer shows data page load times and frequencies
4. **Check memory**: SMA → Node → Memory shows large data pages consuming memory
"""
    },
    {
        "url": "curated://pega-architecture-overview",
        "title": "Pega Platform Architecture — Layers, Engines, and How It All Fits Together",
        "content": """# Pega Platform Architecture — Overview

## Overview
Understanding Pega's architecture helps with debugging, performance tuning, and making correct design decisions. Pega is a Java-based application that runs on standard J2EE application servers.

## Technology Stack
- **Application Server**: Tomcat (embedded in Pega 8+), or external (WebSphere, WebLogic, JBoss)
- **Database**: Oracle, PostgreSQL, Microsoft SQL Server, IBM Db2
- **Search**: Elasticsearch (built-in for full-text search)
- **Caching**: Hazelcast/Ignite (cluster communication and distributed caching)
- **JVM**: Java 11+ (Pega 8.x), Java 17+ (Pega 23.x+)

## Architectural Layers

### 1. Presentation Layer (UI)
- **Constellation UI** (Pega 23+): React-based modern UI framework
- **Classic UI** (Pega 8.x): Server-rendered HTML with Pega's own JS framework
- **DX API**: REST API layer for headless/custom frontends
- **Portals**: Container for the user interface (Designer Studio, user portals)

### 2. Application Layer (Rules Engine)
- **PRPC Engine**: The core rules engine — resolves and executes rules
- **Rule Resolution**: Finds the right rule based on class hierarchy, circumstancing, date range, access group
- **Clipboard**: In-memory data storage for the current session (pages, properties)
- **Declarative Engine**: Manages forward-chaining, declare expressions, constraints

### 3. Data Layer
- **PegaRULES Database**: Stores all rules, data, and work objects
- **BLOB Storage**: Case data stored as BLOBs in the database (pr_other, pc_work tables)
- **External Data**: Accessed via connectors (REST, SOAP, JMS, File, etc.)
- **Data Pages**: Caching layer between application logic and data sources

### 4. Integration Layer
- **Connectors (outbound)**: REST, SOAP, JMS, Kafka, File, Email, SAP
- **Services (inbound)**: REST, SOAP, File, Email — expose Pega functionality
- **OAuth/OIDC**: Authentication for external APIs
- **MQ/JMS Listeners**: Receive messages from queues

## Key Engines

### Case Management Engine
- Manages the lifecycle of cases (work items)
- Enforces SLAs, assignments, approvals
- Handles case hierarchy (parent/child cases)

### Decision Engine
- Executes When rules, Decision Tables, Decision Trees
- Supports predictive analytics (Prediction Studio)
- Handles Next Best Action (NBA) recommendations

### Reporting Engine
- Generates reports from the PegaRULES database
- Supports SQL-based Report Definitions
- Elasticsearch for full-text search across cases

### Agent Engine
- Runs background processing tasks on schedule
- Queue processors for asynchronous work
- Batch processing and data flows

## Node Types (Cluster)
- **Web Node**: Handles user requests (stateless, scalable)
- **Batch/Background Node**: Runs agents, queue processors
- **Search Node**: Dedicated Elasticsearch instance
- **Universal Node**: Does everything (common in dev/test)

## Important Tables
- **pr4_base / pr4_rule**: All rules
- **pc_work**: Active cases (work objects)
- **pc_history_work**: Case history/audit trail
- **pc_assign_worklist**: User worklist assignments
- **pc_assign_workbasket**: Workbasket assignments
- **pr_other**: BLOBs for data objects
- **pc_data_workattach**: Case attachments

## How a Request Flows Through Pega
1. User clicks a button in the UI
2. HTTP request hits the load balancer → routes to a web node
3. Pega servlet receives the request
4. **Rule Resolution**: Finds the correct flow, flow action, section rules
5. **Clipboard**: Loads/creates pages for the current interaction
6. **Activity/Data Transform**: Executes business logic
7. **Declarative Engine**: Evaluates declare expressions, constraints
8. **Save**: Commits changes to the database (BLOB + indexed columns)
9. **Response**: Renders the UI and sends HTML/JSON back to the browser
"""
    },
    {
        "url": "curated://pega-design-patterns",
        "title": "Common Pega Design Patterns — Best Practices for Application Architecture",
        "content": """# Common Pega Design Patterns

## Overview
Pega development follows specific design patterns that leverage the platform's strengths. Understanding these patterns helps you build maintainable, performant applications.

## 1. Enterprise Class Structure Pattern
**Problem**: How to organize classes for reusability across applications
**Pattern**:
```
Organization layer (MyOrg-)
  └── Division/Framework layer (MyOrg-FW-)
       └── Application layer (MyOrg-App-)
            ├── Work classes (MyOrg-App-Work-*)
            ├── Data classes (MyOrg-App-Data-*)
            └── Integration classes (MyOrg-App-Int-*)
```
**Why**: Rules defined at higher layers are inherited by all applications below. Common data transforms, properties, and UI sections defined once, used everywhere.

## 2. Data Page Caching Pattern
**Problem**: Avoid repeated database/API calls for the same data
**Pattern**:
1. Create a Data Page with appropriate scope (Node for shared, Requestor for user-specific)
2. Set a data source (Report Definition, Connector, Activity)
3. Set refresh strategy (time-based, event-based, or manual)
4. Access data via the Data Page — Pega auto-loads and caches

**Anti-pattern**: Calling a connector directly from an Activity every time you need data. Use a Data Page instead.

## 3. Specialization by Circumstance Pattern
**Problem**: Different behavior needed for different conditions (region, product, channel)
**Pattern**:
1. Create a base rule with default behavior
2. Create circumstanced variants for specific conditions
3. Pega automatically resolves to the most specific matching rule

**Example**: A "Calculate Premium" Data Transform has a base version, plus circumstanced variants for "Auto", "Home", "Life" product types.

**Why**: No if/else spaghetti. Adding a new product just means adding a new circumstanced rule — no changes to existing code.

## 4. Delegation Pattern
**Problem**: Business users need to change decision logic without developer involvement
**Pattern**:
1. Create a Decision Table or Map Value rule
2. Mark it as "Allow rule to be delegated"
3. Business users modify the rule through a simplified UI
4. Changes take effect immediately (no deployment needed)

**Use for**: Tax rates, routing rules, approval thresholds, SLA deadlines, any business-owned logic.

## 5. Savable Data Page Pattern
**Problem**: Need to save user-edited data back to the database without a full case
**Pattern**:
1. Create a Data Page with "Savable" option enabled
2. User edits properties on the data page
3. Call Save-DataPage to persist changes
4. No case/work object needed

**Use for**: Reference data management, user preferences, configuration screens.

## 6. Sub-Case Pattern
**Problem**: A business process has independent sub-processes that should be tracked separately
**Pattern**:
1. Parent case creates child cases (sub-cases) for independent work streams
2. Child cases have their own lifecycle, assignments, SLAs
3. Parent case can wait for all children to complete (Wait shape)
4. Data can flow between parent and child via Data Propagation

**Example**: Insurance claim (parent) creates sub-cases for Medical Review, Fraud Check, Payment Processing.

## 7. Integration Retry Pattern
**Problem**: External system calls can fail transiently
**Pattern**:
1. Configure retry count and interval on the connector
2. Use a Queue Processor for async retries with exponential backoff
3. Implement a Dead Letter Queue for permanently failed messages
4. Alert on repeated failures (PDC/Alerts)

## 8. Declare Expression vs Data Transform Pattern
**Problem**: When to calculate a value declaratively vs. imperatively
**Rule of thumb**:
- **Declare Expression**: Value depends on other properties and should ALWAYS stay in sync (e.g., TotalPrice = Quantity × UnitPrice)
- **Data Transform**: Value is set once at a specific point (e.g., setting defaults on case creation)

## 9. Security Layering Pattern
**Problem**: Implement defense in depth for application security
**Pattern** (layers from outer to inner):
1. **Network**: Firewall, VPN, TLS
2. **Authentication**: OAuth/OIDC, SSO, MFA
3. **Role-Based Access (RBAC)**: Access Groups, Roles, Privileges
4. **Row-Level Security**: Access When/Deny rules
5. **Field-Level Security**: Property encryption, masking
6. **Audit**: Logging all access and changes

## 10. Performance Optimization Pattern
**Problem**: Application is slow under load
**Checklist**:
1. Use Node-scoped Data Pages for reference data
2. Add database indexes for properties used in Access When and Report Definitions
3. Optimize BLOB size (remove unused properties from case types)
4. Use Declare Index for properties that need to be reportable
5. Enable requestor pooling for service requests
6. Run PAL (Performance Analyzer Landing Page) to identify bottlenecks
"""
    },
    {
        "url": "curated://pega-when-vs-declare-rules",
        "title": "When Rules vs Declarative Rules — Understanding the Difference",
        "content": """# When Rules vs Declarative Rules — Understanding the Difference

## Overview
A common confusion point for Pega developers is the difference between "When" rules (a specific rule type) and "Declarative" rules (a category of rule types). They both evaluate conditions, but they work very differently.

## When Rules
- **Type**: Evaluated ON DEMAND — someone/something must explicitly invoke them
- **Returns**: Boolean (true/false)
- **Use cases**: Visibility conditions, routing, validation triggers, flow decision shapes
- **How to invoke**: Referenced by name in sections (visibility), flows (decision shapes), or other rules
- **Performance**: Runs only when called

### When Rule Examples
- "Is the customer a VIP?" → Referenced in a section for conditional visibility
- "Is the claim amount over $10,000?" → Used in a flow decision shape for routing
- "Is the user a manager?" → Used for button visibility

## Declarative Rules
- **Type**: Evaluated AUTOMATICALLY — Pega watches for changes and triggers them
- **Subtypes**: Declare Expression, Declare Constraint, Declare OnChange, Declare Trigger
- **Key concept**: You define WHAT should happen, Pega decides WHEN to execute it
- **Performance**: Runs whenever dependent properties change (forward-chaining)

### Declare Expression
- **Calculates** a property value automatically when any input property changes
- Example: `.TotalPrice` = `.Quantity * .UnitPrice` — recalculates whenever Quantity or UnitPrice changes
- Like a spreadsheet formula — always up to date

### Declare Constraint
- **Validates** a property value continuously
- Example: `.Age` must be >= 18 — shows error whenever Age is set below 18
- Unlike a Validate rule, it's always active (not just at save time)

### Declare OnChange
- **Triggers an action** when a property value changes
- Example: When `.Status` changes, send a notification
- Like an event listener

### Declare Trigger
- **Fires an activity** when a database event occurs (insert, update, delete)
- Example: When a case is saved (obj-Save), run an audit logging activity
- Operates at the database level, not the clipboard level

## Key Differences Summary
| Aspect | When Rule | Declare Expression | Declare Constraint |
|--------|-----------|-------------------|-------------------|
| Execution | On demand | Automatic | Automatic |
| Returns | Boolean | Any value | Validation result |
| Who calls it | You (explicitly) | Pega (when inputs change) | Pega (when property changes) |
| Scope | Point-in-time check | Continuous calculation | Continuous validation |
| Analogy | "if" statement | Spreadsheet formula | Always-on validator |

## Common Mistakes
1. **Using an Activity to recalculate totals** → Use Declare Expression instead
2. **Using a When Rule for always-on validation** → Use Declare Constraint instead
3. **Using Declare Expression for one-time defaults** → Use Data Transform instead (Declare Expression recalculates on every change, which you don't want for defaults)
4. **Circular Declare Expressions** → A depends on B, B depends on A → infinite loop error
"""
    },
    {
        "url": "curated://pega-case-vs-data-types",
        "title": "Case Types vs Data Types — When to Model as a Case vs Data Object",
        "content": """# Case Types vs Data Types — When to Model as a Case vs Data Object

## Overview
One of the most important modeling decisions in Pega is whether something should be a **Case Type** (work object) or a **Data Type** (data object). Getting this wrong causes architectural problems that are expensive to fix later.

## Case Types (Work Objects)
- **What they are**: Represent a unit of work that goes through a lifecycle (stages, steps, assignments)
- **Stored in**: pc_work table (with history, assignments, SLAs)
- **Features**: Audit trail, assignments, SLAs, approvals, sub-cases, attachments, case history
- **Class hierarchy**: Extends from Work- base class

### Model as a Case Type When:
1. It has a **lifecycle** with stages (Created → In Progress → Resolved → Closed)
2. It involves **human assignments** (someone needs to work on it)
3. It needs **SLAs/deadlines** (must be completed by a date)
4. It needs an **audit trail** (who did what, when)
5. It needs **approvals** (review and approve/reject)
6. It has **sub-processes** that should be tracked independently

### Examples of Case Types:
- Insurance Claim, Service Request, Loan Application, Purchase Order, Incident Ticket, Employee Onboarding

## Data Types (Data Objects)
- **What they are**: Represent reference data or entities — no lifecycle, no assignments
- **Stored in**: pr_other table (or external systems via connectors)
- **Features**: Properties, data pages, simple CRUD operations
- **Class hierarchy**: Extends from Data- base class

### Model as a Data Type When:
1. It's **reference data** that doesn't change often (Countries, Products, Categories)
2. It's an **entity** that multiple cases reference (Customer, Address, Vehicle)
3. It has **no lifecycle** — it just exists (no stages, no assignments)
4. It doesn't need **SLAs or deadlines**
5. It's **shared across** multiple case types

### Examples of Data Types:
- Customer, Address, Product, Vehicle, Employee, Country, Currency, Configuration

## Decision Flowchart
```
Does it have a lifecycle with stages?
  YES → Case Type
  NO → Does it involve human assignments?
    YES → Case Type
    NO → Is it reference/entity data shared across cases?
      YES → Data Type
      NO → Is it configuration or lookup data?
        YES → Data Type
        NO → Does it need SLAs, approvals, or audit trails?
          YES → Case Type
          NO → Data Type (probably)
```

## Common Mistakes
1. **Modeling a Customer as a Case Type**: Customers don't have a lifecycle — they're reference data. Model as Data Type.
2. **Modeling a Task as a Data Type**: If it has assignments and deadlines, it's a Case Type.
3. **Using one mega Case Type for everything**: Break complex processes into parent + child case types.
4. **Not creating Data Types for reusable entities**: If Customer data is duplicated across case types, extract it into a shared Data Type.

## Performance Implications
- **Case Types**: Heavier — more database writes (history, assignments, audit). Don't create cases for trivial operations.
- **Data Types**: Lighter — simpler storage. But overloading a single data type with too many properties causes BLOB bloat.
"""
    },
    {
        "url": "curated://pega-integration-patterns",
        "title": "Pega Integration Patterns — Sync vs Async, Connectors vs Services, Best Practices",
        "content": """# Pega Integration Patterns — Comprehensive Guide

## Overview
Pega integrations come in two directions: **Outbound** (Pega calls external systems via Connectors) and **Inbound** (external systems call Pega via Services). Within each direction, you choose synchronous or asynchronous patterns.

## Outbound Patterns (Pega → External System)

### 1. Synchronous REST/SOAP Connector
- **How**: Pega sends a request and WAITS for the response
- **Use when**: You need the response immediately (e.g., validate an address, get a credit score)
- **Risk**: If the external system is slow, the user waits. If it's down, the operation fails.
- **Timeout**: Configure appropriate timeout (default 20 seconds may be too long for UI calls)

### 2. Asynchronous via Queue Processor
- **How**: Pega puts the request on a queue → Queue Processor picks it up → calls the external system → processes the response
- **Use when**: The response isn't needed immediately. Fire-and-forget or eventual consistency.
- **Benefits**: Decouples from external system availability. Built-in retry. No user wait.
- **Example**: Submit a claim to the backend system — user doesn't need to wait for the result.

### 3. Data Page + Connector (Cached)
- **How**: Data Page sources from a connector. First access triggers the call; subsequent access uses cache.
- **Use when**: The same data is needed multiple times (e.g., product catalog, exchange rates)
- **Benefits**: Automatic caching reduces external calls. Refresh strategy controls staleness.

### 4. Kafka/JMS Integration
- **How**: Pega publishes messages to Kafka topics or JMS queues
- **Use when**: Event-driven architecture. Publishing domain events for other systems to consume.
- **Benefits**: Fully asynchronous, highly scalable, decoupled.

## Inbound Patterns (External System → Pega)

### 1. Service REST
- **How**: External system calls Pega's REST endpoint
- **Use when**: Modern integrations, mobile apps, microservices calling Pega
- **Setup**: Create a Service REST rule, map incoming JSON to Pega data, execute logic, return response

### 2. Service SOAP
- **How**: External system calls Pega's SOAP endpoint with a WSDL contract
- **Use when**: Legacy integrations, enterprise systems that only support SOAP

### 3. File Listener
- **How**: Pega monitors a directory for new files → processes them automatically
- **Use when**: Batch processing, receiving data files from partners, ETL

### 4. Email Listener
- **How**: Pega monitors an email inbox → creates cases from incoming emails
- **Use when**: Customer support ticket creation from email, document intake

### 5. Kafka/JMS Listener
- **How**: Pega consumes messages from Kafka topics or JMS queues
- **Use when**: Event-driven architecture, reacting to events from other systems

## Sync vs Async Decision Guide
| Factor | Choose Sync | Choose Async |
|--------|-------------|--------------|
| User needs result NOW | Yes | No |
| External system is reliable | Yes | Doesn't matter |
| Volume is low | Yes | High volume |
| Failure handling | Immediate error to user | Retry automatically |
| Latency tolerance | Low (< 5 seconds) | High (minutes/hours ok) |

## Error Handling Best Practices
1. **Always set timeouts** on connectors (don't use infinite/default)
2. **Implement retry logic** for transient failures (use Queue Processor pattern)
3. **Dead Letter Queue** for messages that fail permanently
4. **Circuit breaker** pattern: After N consecutive failures, stop calling the system temporarily
5. **Fallback behavior**: What should Pega do if the external system is down? (Cache last known good? Show error? Use default?)
6. **Log all integration failures** with request/response details for debugging

## Common Integration Debugging Steps
1. **Check Tracer**: Look for connector step, see request/response
2. **Check logs**: PegaRULES log for HTTP errors, timeout errors
3. **Test endpoint independently**: Use Postman/curl to verify the external system works
4. **Check authentication**: Most 401/403 errors are auth issues (expired tokens, wrong credentials)
5. **Check mapping**: Data transforms mapping request/response — verify property paths
"""
    },
    {
        "url": "curated://pega-security-concepts",
        "title": "Pega Security Concepts — Authentication, Authorization, and Defense in Depth",
        "content": """# Pega Security Concepts — Complete Guide

## Overview
Pega security operates in layers: authentication (who are you?), authorization (what can you do?), and data security (what data can you see?). Understanding how these layers work together is essential for debugging access issues.

## Authentication (Who Are You?)

### Authentication Methods
1. **Pega Internal**: Credentials stored in Pega's database (operator records)
2. **LDAP/Active Directory**: Delegated authentication to corporate directory
3. **SAML 2.0**: Single Sign-On with identity providers (Okta, Azure AD, ADFS)
4. **OAuth 2.0 / OpenID Connect**: Token-based authentication for APIs and modern apps
5. **Kerberos**: Windows integrated authentication (auto-login from domain-joined machines)
6. **Custom**: Custom authentication activity for special requirements

### Common Authentication Issues
- **Login fails**: Check operator record status (not locked/disabled), password rules, LDAP connectivity
- **SSO not working**: Verify SAML metadata exchange, certificate validity, claim mapping
- **API auth fails**: Check OAuth token expiration, scope, client credentials

## Authorization (What Can You Do?)

### Authorization Hierarchy
1. **Access Group**: The main container — maps a user to an application + set of roles
2. **Role**: A collection of privileges (e.g., "ClaimProcessor" role)
3. **Privilege**: A single permission (e.g., "CanApproveClaim")
4. **Access Role to Object (ARO)**: Maps a role to specific class-level permissions (read, write, delete)

### How Authorization Works
```
User logs in → Pega checks Operator record → finds Access Group
→ Access Group has Roles → Roles have Privileges → ARO maps role to class permissions
→ User can only see/do what their roles allow
```

### Common Authorization Issues
- **"Not authorized" error**: User's role lacks the required privilege. Check Access Group → Roles → Privileges.
- **User can't see a menu item**: Check portal visibility conditions — they reference privileges.
- **User can't open a case type**: Check ARO for the work class — role needs at least "read" permission.

## Data Security (What Data Can You See?)

### Row-Level Security
- **Access When**: User can see records WHERE condition is true
- **Access Deny**: User CANNOT see records WHERE condition is true
- Combined with ARO to implement fine-grained data access

### Field-Level Security
- **Property encryption**: Encrypt sensitive fields at rest (PII, financial data)
- **Column-level masking**: Show masked values (e.g., SSN as ***-**-1234)
- **Privileged access**: Only users with specific privileges see unmasked values

## Security Debugging Checklist
1. **Can't log in**: Check operator record, authentication service, LDAP/SSO config
2. **Logged in but can't see anything**: Check Access Group assignment on operator record
3. **Can see app but missing features**: Check role privileges for the specific feature
4. **Can see cases but wrong ones**: Check Access When/Deny rules
5. **Can't create/edit/delete**: Check ARO permissions for the class
6. **API returns 401**: Check OAuth token, expiration, scope
7. **API returns 403**: Check service authentication profile, operator privileges

## Security Best Practices
1. **Principle of least privilege**: Start with no access, add only what's needed
2. **Use roles, not individual privileges**: Easier to manage
3. **Don't hardcode operator IDs in rules**: Use roles and privileges instead
4. **Enable audit logging** for security events
5. **Regularly review access**: Remove unused roles/privileges
6. **Use SSO in production**: Don't rely on Pega's built-in authentication for production
7. **Encrypt sensitive properties**: PII, financial data, health data
8. **Set password policies**: Complexity, expiration, lockout
9. **Implement MFA** for administrative access
10. **Test security with multiple user roles** before go-live
"""
    },
]


def seed_phase6():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE6:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase6_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE6)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 6 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase6()
