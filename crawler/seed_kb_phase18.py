"""
Curated Pega Knowledge Base — Phase 18 (Final — Operators, Access Groups, Regex, Job Scheduler, Linked Properties)
Run: python -m crawler.seed_kb_phase18
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE18 = [
    {
        "title": "Operator Records & User Management",
        "url": "https://pega.example.com/operator-records",
        "content": """
# Operator Records & User Management in Pega

## What is an Operator Record?

An operator record is a user account in Pega. Each operator has:
- **User ID** (.pyUserName) — unique login identifier
- **Operator Label** (.pyLabel) — display name
- **Assigned Access Groups** — determines permissions
- **Password** — encrypted storage
- **Operator Status** — active, inactive, locked
- **Data class** — typically `PegaRULES.Operator`

## Creating Operator Records

### Method 1: System Management Application (SMA)
1. Navigate to System → Operations → Operators
2. Click "Create Operator"
3. Enter User ID (must be lowercase, alphanumeric)
4. Assign one or more Access Groups
5. Set initial password
6. Click Save

### Method 2: Programmatic Creation
```
Create an instance of PegaRULES.Operator
Set .pyUserName, .pyLabel, .pyPassword
Add to .pxAccessGroups collection
Call Save method
```

## Operator ID vs Access Group

- **Operator ID (.pyUserName)**: WHO the person is (authentication)
- **Access Group**: WHAT they can do (authorization)

One operator can belong to multiple access groups. Permissions are **cumulative** from all assigned groups.

### Important Properties
| Property | Purpose | Read-Only |
|----------|---------|-----------|
| .pyUserName | Login ID | Yes (after creation) |
| .pyLabel | Display name | No |
| .pyPassword | Hashed password | No (write-only) |
| .pxCreateDateTime | Creation timestamp | Yes |
| .pxCreateOperator | Who created it | Yes |
| .pxUpdateOperator | Last modifier | Yes |
| .pyStatus | Active/Inactive | No |
| .pyLockedUntil | Lock expiration | No |

## Password Management

### Setting a Password
- Only write .pyPassword directly — never store plaintext
- Pega automatically hashes on save
- Minimum requirements typically enforced

### Password Resets
- Users can self-reset via portal if enabled
- Admins can force reset by clearing password and setting temporary

### Account Locking
- After N failed login attempts, account locks automatically
- Lock duration set in Security policies
- Check .pyLockedUntil timestamp
- Admin can manually unlock by setting .pyLockedUntil to past date

## Common Issues & Debugging

### "Not Authorized" for Operator
**Symptoms**: Operator can log in but gets permission errors
**Checks**:
1. Verify operator is in correct access group: `pxAccessGroups.ListGroup()`
2. Check access group has required rules mapped
3. Confirm access group applications include target app
4. Test with simple portal first to isolate

### Operator Won't Lock After Failed Attempts
**Checks**:
1. Verify security policies are active
2. Check access group doesn't have "Bypass Security" flag
3. Ensure password policy is configured in Access Group

### Delegated Administration Issues
- If operator can't manage others, check their access group has "Admin" privileges
- Confirm target access group is delegatable
- Verify operator's access group includes the same organizations

### Bulk Operator Creation
Use Import/Export or automation:
1. Create flat file (CSV) with UserID, Label, AccessGroup
2. Use Data Transform to batch-create operators
3. Set temporary passwords, force change on first login
4. Log the operation for audit trail

## Best Practices
- Use Role-based access group naming (e.g., "CSR_Team", "Manager_Ops")
- Regularly audit operator status and group assignments
- Implement password policies (expiration, complexity)
- Log operator creations/modifications for compliance
- Disable rather than delete operators for audit trail
"""
    },
    {
        "title": "Access Groups — Configuration Deep Dive",
        "url": "https://pega.example.com/access-groups",
        "content": """
# Access Groups — Configuration Deep Dive

## What is an Access Group?

An access group is a security container that defines what an operator can do. It's **not** a role — it's a set of permissions tied to:
- Rules accessible (apps, case types, data)
- Portal availability
- Requestor settings (work queues, reports)
- Organization/division context

## Creating Access Groups

### Step-by-Step
1. **Navigate** to System → Security → Access Groups
2. **Create New** access group
3. **Name it** (e.g., "CSR_USA_West", "Underwriter_Team")
4. **Assign Organization** (usually multi-tenant context)
5. **Map Privileges** (next section)
6. **Configure Portal Settings** (next section)
7. **Set Requestor Defaults** (optional)
8. **Save & Test**

### Naming Convention
- Use `RoleName_Division_Location` or similar
- Make it searchable and meaningful
- Example: `Claims_Adjuster_TX`, `Manager_Admin_HQ`

## Mapping Roles & Privileges

Access groups contain **privileges** — rules that specify what's accessible.

### Common Privilege Types
- **Portal Access**: Which portals/dashboards
- **Application Access**: Which applications visible
- **Case Type Access**: Create/view specific case types
- **Data Access**: View/modify specific object types
- **Report Access**: Visibility of reports
- **Rule Categories**: Code, data, reports

### Privilege Rules Structure
Privilege rules typically grant:
```
Application: MyApp
Case Types: [CaseType1, CaseType2]
Data Classes: [PegaRULES.Company, MyApp.Customer]
Report Access: All or Restricted
```

## Portal & Requestor Settings

### Portal Settings
- **Default Portal**: Which portal loads on login
- **Portal Availability List**: Which portals accessible
- **Workspace Configuration**: Layout/customization options

### Requestor Settings (Critical!)
- **Work Queue Assignment**: Determines which work visible
- **Queue/Pool Membership**: What gets routed here
- **Work Distribution**: Round-robin, load-balanced, manual
- **Thread/Requestor Context**:
  - Set `.pxThread.pxRequester` to route work
  - Controls inbox filtering

## Default Access Group

- First access group created becomes DEFAULT
- Assigned to new operators if not explicitly set
- Change via System → Security → Configuration
- Should be minimal permissions for safety

## Application Access

Access Group has **Applications** list:
- Operators can only see apps in their access group
- Apps include case types, data, portals
- Remove app from access group = operator can't access

### Debugging: Operator Sees Nothing
1. Check operator is assigned to access group
2. Check access group has applications mapped
3. Verify portal rule exists and is available
4. Test with SysAdmin access group to isolate

## Inheritance & Best Practices

### Access Group Hierarchy (if using)
- Parent access group = base permissions
- Child access group = adds additional permissions
- Not automatic in Pega — implement via structure

### Debugging "Not Authorized"
**Quick Checklist**:
1. `Operator.AccessGroups.ListGroup()` — verify membership
2. Access Group → Applications → see target app?
3. Application → Privileges → see required rule?
4. Rule Category → Rule Name — rule exists?
5. Is rule enabled/active?
6. Check org/division context matching

### Common Misconfiguration
- Operator in access group, but access group has no applications
- Privilege rule exists but not mapped to access group
- Application removed from access group mid-project
- Case type privilege too restrictive

## Testing Access

### Quick Test
1. Login as test operator with access group
2. Attempt to open case type — should work or show "Not Authorized"
3. If denied, trace access group configuration
4. Use Tracer to see authorization checks: search "Not authorized"

### Audit Access Changes
- Keep changelog of access group modifications
- Document who added/removed applications
- Review quarterly for compliance
- Archive decommissioned access groups for audit trail
"""
    },
    {
        "title": "Validation Rules & Regex Patterns in Pega",
        "url": "https://pega.example.com/validation-regex",
        "content": """
# Validation Rules & Regex Patterns in Pega

## Validate Rules Overview

A **Validate Rule** checks if property data meets requirements. Uses:
- **Regular Expressions** (regex)
- **Expression Rules** (custom logic)
- **Script Rules** (Groovy/JavaScript)
- **Built-in validators**

## Creating Validate Rules

### Method 1: Rule Designer
1. **Highlight** property in form
2. **Right-click** → Configure Validation
3. **Enter regex pattern** or select validator
4. **Add message**: "Invalid format: {expected pattern}"
5. **Save & Publish**

### Method 2: Edit Validate Rule Directly
- Navigate to **Rules → Validation → Validate**
- Create new rule: `YourApp.ValidatePhoneNumber`
- Set **applies to** data class (e.g., MyApp.Company)
- Set **property name** (e.g., PhoneNumber)
- Enter regex or expression
- Set **error message**

## Common Regex Patterns

### Email Validation
```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```
Matches: user@example.com, john.doe+tag@company.co.uk
Fails: user@, @example.com, missing TLD

### Phone Number (US Format)
```regex
^\d{3}-\d{3}-\d{4}$
```
Matches: 555-123-4567
For flexible: `^[\d\s\-\(\)]{10,14}$`

### Social Security Number (SSN)
```regex
^\d{3}-\d{2}-\d{4}$
```
Matches: 123-45-6789
Note: Add server-side check to avoid known-bad SSNs

### Date (MM/DD/YYYY)
```regex
^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}$
```
Matches: 01/15/2024, 12/31/2025
Note: Doesn't validate leap years — add expression validation for that

### Alphanumeric with Spaces (Product Code)
```regex
^[a-zA-Z0-9\s]{1,50}$
```
Matches: ABC123, Product Code XYZ
Fails: Special characters

### URL Validation
```regex
^https?:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$
```
Matches: http://example.com, https://sub.example.co.uk/path

## Property-Level vs Page-Level Validation

### Property-Level
- Applies to **single property**
- Runs **immediately** when property changes
- **Client-side first**, then server
- Example: Email field must be valid email

### Page-Level
- Applied to **entire page/section**
- Runs on **page submission or save**
- Can do **cross-field validation**
- Example: "If state is TX, zip must start with 7, 8, or 9"

### Cross-Field Validation Example
```
Rule Type: Validate
Applies to: MyApp.Order
Property: OrderAmount
Expression:
  If (.ShippingMethod == "Standard") then
    .OrderAmount >= 50
  else true
Message: "Standard shipping requires $50 minimum order"
```

## Server-Side vs Client-Side

### Client-Side (Browser)
- **Speed**: Immediate feedback
- **UX**: Better user experience
- **Risk**: Can be bypassed, not secure
- Pega: Runs first, decorative red X

### Server-Side (Pega)
- **Security**: Cannot be bypassed
- **Accuracy**: Authoritative validation
- **Timing**: Runs on every Save/Submit
- Pega: Always runs, blocks actual save if fails

**Best Practice**: Use both. Client-side for UX, server-side for security.

## Custom Validation Activities

For complex logic, use an Activity Rule:

```
Activity: ValidateOrderPayment
Input: .Order page
Logic:
  1. Check payment amount vs order total
  2. Call external service to validate card
  3. If fails, append error to ErrorList
  4. Return .ErrorList
```

Then reference in form: "On page submit, run activity ValidateOrderPayment"

## Common Validation Issues & Debugging

### Issue: Validation Runs Client-Side but Not Server
**Cause**: Validate rule not properly mapped to server-side validation
**Fix**:
1. Confirm validate rule is Published
2. Check rule applies to correct data class
3. Add validation at Save() method, not just form
4. Test via Tracer: search "Validation" or "Validate"

### Issue: Regex Pattern Works in Tester, Not in Form
**Causes**:
- Pega uses Java regex (not PCRE or JavaScript)
- Backslashes need escaping: `\\d` not `\d` in JSON
- Case sensitivity: `[a-z]` vs `[a-zA-Z]`

**Fix**: Test in Pega Dev Studio Regex Tester with actual data

### Issue: "Please correct errors" but Can't See Error Message
**Cause**: Error message property not bound to label
**Fix**:
1. Add property to form with binding to validation error
2. Use standard Pega error summary section
3. Check visibility conditions on error label

### Issue: Date Validation Accepts Invalid Dates (Feb 30)
**Cause**: Regex only checks format, not actual calendar validity
**Fix**: Use Expression validation with DateValid() function:
```
And(
  Match(.DateField, "^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}$"),
  DateValid(.DateField)
)
```

## Best Practices

- **Test edge cases**: Empty, null, special characters, SQL injection attempts
- **Avoid overly complex regex**: If regex > 100 chars, use expression instead
- **Localize patterns**: Phone/zip/date formats vary by country
- **Document patterns**: Comment why regex is structured a certain way
- **Use whitelist not blacklist**: `[a-z0-9]` better than `[^"<>]`
- **Server-side always**: Never trust client validation alone
"""
    },
    {
        "title": "Job Scheduler & Agent Scheduling",
        "url": "https://pega.example.com/job-scheduler-agents",
        "content": """
# Job Scheduler & Agent Scheduling in Pega

## What Are Agents?

Agents are **background processes** (jobs) that run automatically on a schedule. They:
- Run **without user interaction**
- Execute on **configurable schedules** (cron-like)
- Process **work items** or **periodic tasks**
- Run on **specific nodes** in a cluster
- Are **monitored** via System Management Application (SMA)

### Agent vs Requestor
| Aspect | Agent | Requestor |
|--------|-------|-----------|
| Trigger | Schedule or Queue | User action or Router |
| Context | System thread | User thread |
| Workload | Batch/async | Interactive/sync |
| Thread ID | .pxThread.pxAgent | .pxThread.pxRequester |

## Creating Agent Rules

### Step 1: Create Activity to Execute
```
Activity: ProcessPendingOrders
1. Query for orders in "Pending" status
2. For each order, validate and route to review
3. Log completion
4. Return result message
```

### Step 2: Create Agent Rule
1. **Navigate** to Rules → Agents → Agent
2. **Name**: MyApp.ProcessPendingOrders
3. **Applies To**: PegaRULES.Agent
4. **Activity to Run**: MyApp.ProcessPendingOrders
5. **Schedule Type**: Select Time-based or Queue-based
6. **Save**

### Step 3: Configure Schedule

#### Time-Based Agent (Periodic)
```
Frequency: Daily
Start Time: 01:00 (1 AM)
Recurrence: Every 1 day
Expires: Never
Days Active: Mon-Fri
```

Uses **cron-like syntax** internally:
- `0 1 * * *` = 1 AM daily
- `0 */4 * * *` = Every 4 hours
- `30 8 * * 1-5` = 8:30 AM weekdays

#### Queue-Based Agent (Event-Driven)
- Watches specific **work queue** for items
- Triggers when work arrives
- Processes **batch or single item**
- Better for **near-real-time** scenarios

## Agent Schedules (Cron Reference)

### Format
```
Minute | Hour | Day-of-Month | Month | Day-of-Week
  0-59  | 0-23 |    1-31      | 1-12  |    0-6 (Sun=0)
```

### Common Examples
| Goal | Cron | Meaning |
|------|------|---------|
| Hourly | `0 * * * *` | Every hour at :00 |
| Every 30 min | `*/30 * * * *` | 12:00, 12:30, 1:00, 1:30... |
| Daily 2 AM | `0 2 * * *` | 2:00 AM every day |
| Weekdays 9 AM | `0 9 * * 1-5` | Mon-Fri at 9:00 AM |
| 1st of month | `0 0 1 * *` | Midnight, first day each month |
| Every 2 hours | `0 */2 * * *` | 12:00, 2:00, 4:00 AM... |

## Agent Management in SMA

### Viewing Active Agents
1. **System → Operations → Agents**
2. See **Agent Status**, **Last Run**, **Next Run**
3. **Enabled/Disabled** toggle
4. **Run Count** and **Errors**

### Node-Specific Scheduling
- Agents run on **specific nodes** (not all nodes)
- Configure via **Node Configuration**
- Prevent **duplicate processing** on clustered systems
- Example: "Run ProcessPendingOrders only on Node1"

### Enabling/Disabling Agents
- **Per Agent**: Toggle in SMA
- **Per Node**: Node configuration settings
- **Disable if**: Development, troubleshooting, or during maintenance

## Debugging Agents Not Running

### Checklist
1. **Is agent enabled?** Check System → Operations → Agents
2. **Is schedule correct?** Verify cron expression
3. **Is node running?** Confirm in cluster manager
4. **Activity exists & publishable?** Try running manually
5. **Check logs**: Alert Log, Activity Tracer, Agent Log
6. **Permission issues?** Agent runs as system, check rules access

### Agent Runs but Fails Silently
- Check **Alert Log** for exceptions
- Run activity manually to catch errors
- Add logging to activity: `logMessage("Debug point", True)`
- Trace the agent's execution in System Tracer

### Agent Processes Wrong Data
- Verify **queue assignment** (if queue-based)
- Check **query clause** filters correctly
- Confirm **date filters** (time zones, format)
- Add **count logging**: "Processing X items"

## Agent Activity Patterns

### Pattern 1: Bulk Processing
```
1. Query for items matching criteria
2. Loop through items
3. Perform action (update status, send notification)
4. Increment counter
5. Log summary (processed 47 items)
```

### Pattern 2: Time-Based Cleanup
```
1. Find old records (created > 30 days ago)
2. Archive or delete
3. Log operation
4. Alert if threshold exceeded
```

### Pattern 3: Polling External Service
```
1. Query for pending external requests
2. Call API/service
3. Update with response
4. Handle timeouts gracefully
5. Retry if failed
```

## Long-Running Agent Monitoring

### Issues with Slow Agents
- **Timeout**: Agent killed if > max duration
- **Resource contention**: Agent blocks other work
- **Database locks**: Long queries hold locks

### Solutions
- **Batch in chunks**: Process 100 items, pause, repeat
- **Query optimization**: Add indexes, filter early
- **Async delegation**: Agent queues work, activity processes asynchronously
- **Monitor duration**: Log start/end times, alert if > threshold

### Setting Agent Timeout
- **System → Security → Policies** or **Node Configuration**
- Typical default: 30-60 minutes
- Increase if agent legitimately needs more time
- Monitor actual duration to tune correctly

## Best Practices
- **Test activity independently** before linking to agent
- **Start and end logging** to trace execution
- **Implement error handling** — don't let exceptions silently fail
- **Schedule conservatively** — run off-peak if intensive
- **Monitor** — set up alerts for failed runs
- **Version control** — track agent changes
"""
    },
    {
        "title": "Linked Properties & Data References",
        "url": "https://pega.example.com/linked-properties",
        "content": """
# Linked Properties & Data References in Pega

## What Are Linked Properties?

A **Linked Property** is a reference to external data (another object) rather than embedding that data directly.

### Linked vs Embedded
```
Embedded Data:
{
  "Customer": {
    "Name": "John Doe",
    "Phone": "555-1234",
    "Address": "123 Main St"
  }
}

Linked Data:
{
  "CustomerID": "CUST-123",
  "CustomerRef": <reference to PegaRULES.Customer object>
}
```

**Linked**: Store reference (ID), fetch data on demand
**Embedded**: Store full copy in clipboard

## Data Reference vs Embedded Data

### When to Use Data Reference (Linked)
- Data is **large** (many properties)
- Data is **shared** across multiple objects
- Data **changes frequently** (don't want stale copies)
- Want to **minimize clipboard size**
- Performance-critical applications
- Example: Linking to master Customer record

### When to Use Embedded Data
- Data is **small** (few properties)
- Data is **unique** to this instance
- Data is **static** for this case
- Offline/async processing needed
- Example: Customer name/email on order line item

## Creating Linked Properties

### Step 1: Define Reference Property
1. **Add property** to your data class
2. Set **Mode**: Data Reference
3. Set **Type**: Target data class (e.g., MyApp.Customer)
4. **Save**

### Step 2: Reference in Form
```
Section showing linked data:
- Property: .Customer (data reference)
- Display: .Customer.Name, .Customer.Phone
- All accessed via .Customer reference
```

### Step 3: Populate Reference
```
Activity: GetCustomerData
Input: .CustomerID
Process:
  1. Call activity to fetch customer
  2. Set .Customer = returned object
  3. Return page
```

## Lazy Loading vs Eager Loading

### Eager Loading (Load All at Once)
```
Activity: PopulateOrder
1. Load Order data
2. Load Customer data (even if not used now)
3. Load Payment data
4. Load Shipping data
Result: Full page loaded, ready for any reference
```
**Pros**: All data available, no delays
**Cons**: Slow initial load, wasteful if data not used

### Lazy Loading (Load on Demand)
```
Activity: GetOrderSummary
1. Load Order data
2. DO NOT load Customer, Payment, Shipping
When user clicks "View Customer Details":
3. Fetch Customer on-demand
Result: Fast initial load, delay when accessing
```
**Pros**: Fast initial load, efficient
**Cons**: Delays when accessing linked data, requires careful UX

### Implementation
**Eager**: Set linked property in main activity
**Lazy**: Use SmartFetch() or explicit fetch() when property accessed

## Impact on Clipboard Size

### Example
```
Order with 10 embedded customers = 500KB clipboard
Order with 10 customer references = 50KB clipboard
```

**Why it matters**:
- **Network**: Larger clipboard = slower transfers
- **Storage**: If persisted, takes more space
- **Performance**: Large clipboard = slower processing
- **Memory**: More memory on server

**Guideline**: Keep clipboard under 1MB for responsive systems

## Referencing External Data Objects

### Data Pages for Linked Data
```
DataPage: D_CustomerMaster
Source: SQL query to Customer system
Scope: Global (cached)
Key: CustomerID
```

Then link: `.Customer` = `D_CustomerMaster(CustomerID)`

### API/Service Data
```
Connector: GetCustomerService
URL: /api/customers/{id}
Cache: 5 minutes
Result: Mapped to PegaRULES.Customer class
```

Used similarly: Link external via connector

## Common Issues & Debugging

### Issue: "Property Not Populated" with Linked Properties
**Symptoms**: `.Customer` is empty/null even though reference set

**Causes**:
1. Reference not actually populated (activity didn't run)
2. Data page not loaded or timed out
3. Connector failed silently
4. Scope issue (page lost after clipboard clear)

**Debug**:
1. Add logging: `logMessage("Customer = " + .Customer, True)` in activity
2. Check **Data Page** is enabled and returns data
3. Trace activity: Watch `.Customer` being set
4. Verify **scope**: Is clipboard cleared between steps?

### Issue: Linked Data Shows as Null in Form
**Cause**: Reference loaded, but property accessed wrong

**Fix**:
```
WRONG: <expression>.Customer</expression>
RIGHT: <expression>.Customer.Name</expression>
If linked property empty, test:
<expression>If(IsNull(.Customer), "No Customer", .Customer.Name)</expression>
```

### Issue: "Cannot Update Linked Property"
**Symptoms**: Can read `.Customer.Name` but can't set it

**Cause**: Linked properties are **read-only references**. To update:
1. Fetch the referenced object
2. Modify it
3. Save it back
4. Refresh reference

```
Activity: UpdateCustomerPhone
Input: .CustomerID, .NewPhone
1. Fetch customer object
2. Update .Phone property
3. Save customer
4. Reload .Customer reference
```

### Issue: Data Page Context for Linked Properties
**Problem**: Data page needs parameter but property doesn't have it

**Solution**: Set data page context before loading
```
Activity: PrepareOrderWithCustomer
1. Create context: .D_CustomerSearchFilter.ID = .CustomerID
2. Load data page with context
3. Reference via context: .Customer = .D_CustomerMaster(.CustomerID)
```

## Performance Optimization

### Caching Linked Data
- Use **Scope: Global** on data pages
- Set appropriate **TTL (Time to Live)**
- Cache master data (doesn't change often)
- Don't cache personal data (may stale)

### Prefetching
- Load likely references upfront (eager)
- Use background activity to warm cache
- Reduces user-facing delays

### Query Optimization
- If using SQL data page, add **filters**
- Index on lookup key (e.g., CustomerID)
- Don't load all fields if only few needed
- Use **SELECT *** sparingly

## Best Practices
- **Use references for master data** (customers, products, rules)
- **Embed transactional data** (line items, attachments specific to instance)
- **Document data relationships** — which properties are linked
- **Monitor clipboard size** — log in activities
- **Test with realistic data volumes** — performance differs with scale
- **Plan for data page failures** — graceful fallback if reference can't load
"""
    },
    {
        "title": "Auto-Populated Properties & System Properties",
        "url": "https://pega.example.com/auto-populated-properties",
        "content": """
# Auto-Populated Properties & System Properties in Pega

## Understanding .px and .py Prefixed Properties

Pega automatically manages properties with special prefixes — you don't explicitly set them, they're maintained by the system.

### .px Prefix (System Properties)
- **p** = Pega
- **x** = eXtended system properties
- Managed by **Pega engine**, never directly set
- Examples: `.pxCreateDateTime`, `.pxUpdateOperator`, `.pxUrgencyWork`

### .py Prefix (Operator-Managed System Properties)
- **p** = Pega
- **y** = customiZable system properties (you can set them)
- Mixed: Some auto-populated, some you manage
- Examples: `.pyLabel`, `.pyDescription`, `.pyStatus`

## Key Auto-Populated Properties

### Timeline & Audit Properties
| Property | Auto-Set | Purpose | Read-Only |
|----------|----------|---------|-----------|
| `.pxCreateDateTime` | On creation | When record created | Yes |
| `.pxCreateOperator` | On creation | Who created record | Yes |
| `.pxUpdateDateTime` | On every save | Last modification time | Yes |
| `.pxUpdateOperator` | On every save | Who last modified | Yes |

### Case/Work Properties
| Property | Purpose | When Set |
|----------|---------|----------|
| `.pyStatusWork` | Case status (New, Open, Resolved) | You set via workflow |
| `.pxUrgencyWork` | Case urgency (1-10) | Manual or rule-based |
| `.pxCreateDateTime` | Case creation time | Auto on create |
| `.pxDueDateTime` | When case due | You set in workflow |

### Operator/Contact Properties
| Property | Purpose | Read-Only |
|----------|---------|-----------|
| `.pyUserName` | Operator login ID | Yes (after create) |
| `.pyLabel` | Display name | No |
| `.pyDescription` | Description | No |
| `.pyStatus` | Active/Inactive | No |

## How Auto-Populated Properties Work

### On Record Save
```
1. Pega intercepts save
2. Sets .pxCreateDateTime (if new)
3. Sets .pxCreateOperator = current operator (if new)
4. Always sets .pxUpdateDateTime = now
5. Always sets .pxUpdateOperator = current operator
6. Persists to database
```

### On Record Retrieve
```
1. Load from database
2. .pxCreateDateTime populated from DB
3. .pxCreateOperator populated from DB
4. .pxUpdateDateTime populated from DB
5. .pxUpdateOperator populated from DB
All read-only in memory
```

## Which System Properties Are Read-Only?

### Read-Only (Cannot Change)
- `.pxCreateDateTime` — set once at creation
- `.pxCreateOperator` — set once at creation
- `.pxUpdateDateTime` — always auto-updated
- `.pxUpdateOperator` — always auto-updated
- `.pxInsKey` — internal database key

### Modifiable
- `.pyLabel` — change anytime
- `.pyDescription` — change anytime
- `.pyStatus` — change anytime
- Custom `.py*` properties you create

## Using System Properties in Reports & Conditions

### In Report SQL
```sql
SELECT p.pyLabel, p.pxCreateDateTime, p.pxUpdateOperator
FROM pr_case p
WHERE p.pxCreateDateTime >= DATEADD(day, -7, GETDATE())
ORDER BY p.pxUpdateDateTime DESC
```

### In Decision Tree Condition
```
If .pxCreateOperator == "admin"
  Then route to Manager
Else
  Route to Standard Queue
```

### In Activity Expression
```
If (DateDiff(.pxCreateDateTime, Now()) > 30)
  {Case overdue — trigger escalation}
Else
  {Case still within SLA}
```

### In Harness Visibility
```
<expression>
  If(pxUpdateOperator == "system",
    "false",     {Hide if system updated}
    "true")      {Show if operator updated}
</expression>
```

## Common Mistakes

### Mistake 1: Trying to Set .pxCreateDateTime
```
WRONG:
.pxCreateDateTime = "2024-01-15"

CORRECT:
// This is auto-set, can't change
// If you need custom create time, use separate property
.pyCreatedByUser = Now()
```

### Mistake 2: Assuming .pxUpdateOperator is Always User
```
WRONG:
// Assuming pxUpdateOperator is who triggered case
.pxUpdateOperator may be "system" if batch job ran

CORRECT:
// If need to track user changes, use custom property
.pyLastModifiedBy = User.userName  // Track yourself
```

### Mistake 3: Not Considering Timezone
```
.pxCreateDateTime is stored as UTC
When displaying, must convert to user's timezone

Activity:
  .DisplayCreateTime =
    ConvertTimeZone(.pxCreateDateTime, "UTC", .pyUserTimeZone)
```

### Mistake 4: Relying on .pxUpdateDateTime for Audit
```
WRONG:
// Timestamp updates on ANY change
.pxUpdateDateTime updated even if data didn't really change

CORRECT:
// For change tracking, use custom property
.pyLastRealChange = Now()  // Only when specific fields change
.pyChangeLog.Add()         // Full history per change
```

## Best Practices for System Properties

### Audit Trail
```
Activity: LogSignificantChange
When:
  Important property changes
Do:
  1. Record .pxUpdateOperator
  2. Record .pxUpdateDateTime
  3. Save old vs new value
  4. Add to .pyChangeLog list
```

### Age-Based Logic
```
In Decision:
  If (DateDiff(.pxCreateDateTime, Now()) > 90)
    Then: Escalate
    Else: Standard handling

In Report:
  Filter: WHERE pxCreateDateTime >= DATEADD(day, -30, GETDATE())
```

### Operator Tracking
```
Form Section title:
  "Created by {pxCreateOperator} on {pxCreateDateTime}
   Last modified by {pxUpdateOperator} on {pxUpdateDateTime}"
```

### SLA Calculations
```
SLA Calculation:
  Created: .pxCreateDateTime
  Due: .pxCreateDateTime + 48 hours
  Remaining: Max(0, DateDiff(Now(), DueDateTime))
```

## System Property Reference Quick Lookup

| Goal | Property | Read-Only | Auto-Set |
|------|----------|-----------|----------|
| Who created | .pxCreateOperator | Yes | Yes |
| When created | .pxCreateDateTime | Yes | Yes |
| Who last changed | .pxUpdateOperator | Yes | Yes |
| When last changed | .pxUpdateDateTime | Yes | Yes |
| Case status | .pyStatusWork | No | No |
| Case urgency | .pxUrgencyWork | No | No |
| Display label | .pyLabel | No | No |
| Description | .pyDescription | No | No |
"""
    },
    {
        "title": "Pega Certification & Learning Path Guide",
        "url": "https://pega.example.com/certification-guide",
        "content": """
# Pega Certification & Learning Path Guide

## Pega Certification Tracks

Pega offers multiple certification paths based on your role and experience level.

### Available Certifications (2024-2025)

| Certification | Level | Prerequisites | Focus |
|---------------|-------|----------------|-------|
| **CSA** | Associate | None | Pega basics, case management, UI |
| **CSSA** | Senior Associate | CSA recommended | Advanced case management, APIs |
| **CLSA** | Lead Senior Associate | CSSA recommended | Architecture, design, leadership |
| **LSA** | Lead Specialist Architect | CLSA recommended | Enterprise solutions, governance |
| **Robotics** | Associate | None | RPA, automation, bot building |
| **Decisioning** | Specialist | CSA recommended | AI/ML, predictive models |

## Exam Format & Topics

### Typical CSA Exam Structure
- **Duration**: 90 minutes
- **Questions**: ~60 multiple choice
- **Passing Score**: ~70% (varies)
- **Format**: Proctored (online or in-person)

### CSA Core Topics
1. **Pega Basics** (10-15%)
   - Architecture, clipboard, case lifecycle
   - This knowledge base Phase 1-4 coverage

2. **Case Management** (20-25%)
   - Case types, workflows, routing
   - Phases 5-8, 14-16

3. **User Interface** (15-20%)
   - Harness design, sections, layouts
   - Phases 9-10

4. **Rules & Configuration** (25-30%)
   - Data classes, properties, validation
   - Phases 2-3, 17-18

5. **Debugging & SMA** (10-15%)
   - Tracer, logs, alerts, monitoring
   - Phase 12

## Recommended Learning Path for Beginners

### Phase 1: Foundation (Week 1-2)
**Goal**: Understand Pega concepts
- **Read**: Phases 1-2 of this knowledge base
  - Pega architecture
  - Case types & lifecycle
  - Data classes & properties
- **Practice**: Create simple case type in dev environment
- **Time**: 10-15 hours

### Phase 2: Core Concepts (Week 3-4)
**Goal**: Build functional cases
- **Read**: Phases 3-5
  - Workflows & decision logic
  - Routing & assignments
  - Validation & data validation
- **Practice**: Add workflow, routing rules to case type
- **Time**: 15-20 hours

### Phase 3: UI & Interaction (Week 5-6)
**Goal**: Design user experience
- **Read**: Phases 9-10
  - Harness design
  - Sections & layouts
  - User experience patterns
- **Practice**: Create form harness, section, responsive design
- **Time**: 15-20 hours

### Phase 4: Advanced Topics (Week 7-8)
**Goal**: Production-ready patterns
- **Read**: Phases 11-13, 15-18
  - Exception handling
  - Integration patterns
  - Security & operators
- **Practice**: Add error handling, external system calls
- **Time**: 20-25 hours

### Phase 5: Exam Prep (Week 9-10)
**Goal**: Review & practice exam
- **Review**: All phases 1-18, focus on weak areas
- **Practice**: Sample exams, flashcards
- **Study Groups**: Join Pega community forums
- **Time**: 15-20 hours

**Total Estimated Time**: 75-100 hours for CSA readiness

## Pega Academy Resources

### Official Learning
- **Pega Academy** (academy.pega.com)
  - Free and paid courses
  - Video lectures, hands-on labs
  - Role-based learning paths
  - Certification practice exams

### Recommended Courses
1. **Pega Fundamentals** (Free) — Start here
2. **Case Management Essentials** (Paid)
3. **Building Applications with Pega** (Paid)
4. **Pega Application Development** (Advanced)

### Community Resources
- **Pega Community** (pega.com/community)
- **Forums**: Ask questions, learn from others
- **Blogs**: Industry insights, tips & tricks
- **Webinars**: Live training sessions

## Study Tips & Exam Strategies

### Before Exam
1. **Time Management**: Practice full exams under time constraints
2. **Weak Areas**: Identify gaps, focused review
3. **Terminology**: Flash cards for key terms & acronyms
4. **Hands-On**: Build projects — practice > reading
5. **Sleep Well**: Night before exam, rest is important

### During Exam
1. **Read Carefully**: Don't rush, understand each question
2. **Flag Uncertain**: Skip hard ones, return later
3. **Time Budget**: 60 questions in 90 minutes = 1.5 min/question
4. **Context Clues**: Use answer choices to infer what's being asked
5. **Review**: If time remains, review flagged questions

### Common Exam Pitfalls
- **Overcomplicating**: Pick simplest correct answer
- **Pega-specific terms**: "Case routing" ≠ "case assignment"
- **Outdated info**: Study latest Pega version docs
- **Guessing patterns**: No pattern (answers vary)
- **Overthinking**: Trust your knowledge, move on

## Common Exam Topics Mapped to This Knowledge Base

### "How does a case move through states?"
**Answer Location**: Phase 5 (Workflows & Routing)
**Key Concepts**: Transitions, stages, path flows

### "What's the difference between a data class and a concrete class?"
**Answer Location**: Phase 2 (Data Concepts)
**Key Concepts**: Inheritance, purpose

### "How do you prevent unauthorized access?"
**Answer Location**: Phase 17 (Access Groups)
**Key Concepts**: Access groups, privileges, operator assignment

### "What's the impact of embedding vs linking data?"
**Answer Location**: Phase 18 (Linked Properties)
**Key Concepts**: Clipboard size, performance, reference management

### "How do you validate user input?"
**Answer Location**: Phase 18 (Validation & Regex)
**Key Concepts**: Validate rules, regex patterns, server-side validation

### "What happens when an agent fails to run?"
**Answer Location**: Phase 18 (Job Scheduler)
**Key Concepts**: Troubleshooting, logging, monitoring

### "Why would an operator see 'Not Authorized'?"
**Answer Location**: Phase 17-18 (Operators, Access Groups)
**Key Concepts**: Access group assignment, privilege mapping

## Using This Knowledge Base for Exam Prep

### Strategy 1: Weak Area Deep-Dive
1. Identify weak exam topic
2. Read relevant phase thoroughly
3. Create flashcards from key points
4. Write mini activity implementing concept
5. Explain concept aloud (teaches brain better)

### Strategy 2: Full Curriculum Review
1. Read all 18 phases sequentially
2. Take notes in your own words
3. Create mind map connecting phases
4. Quiz yourself after each phase
5. Take practice exam mid-way

### Strategy 3: Active Learning
1. Read phase
2. Build project implementing concepts
3. Get stuck, debug using knowledge base
4. Repeat for each phase
5. Final capstone project combining all

## Beyond CSA: Continuing Your Path

### CSSA Preparation (After CSA)
- **Focus**: Advanced configurations, APIs, custom code
- **Projects**: Multi-component systems, API integrations
- **Time**: 3-6 months of hands-on work

### CLSA/LSA Path (Architect Track)
- **Prerequisite**: 2+ years production Pega experience
- **Focus**: System design, governance, mentoring
- **Projects**: Enterprise solutions, team leadership

### Decisioning/Robotics Specialization
- **Parallel tracks**: Can pursue while developing core skills
- **Focus**: AI/ML (decisioning) or automation (robotics)
- **Time**: 2-3 months after CSA

## Summary: Learning Path Flowchart
```
Start (Week 1)
  ↓
Foundation: Phases 1-2 (Week 1-2)
  ↓
Core: Phases 3-5 (Week 3-4)
  ↓
UI: Phases 9-10 (Week 5-6)
  ↓
Advanced: Phases 11-13, 15-18 (Week 7-8)
  ↓
Exam Prep: Review + Practice (Week 9-10)
  ↓
CSA Exam (Week 11)
  ↓
Success → CSSA Track (if interested)
```

## Final Tips
- **Start early**: Don't cram 2 weeks before
- **Build projects**: Hands-on learning > passive reading
- **Join community**: Learn from others' experiences
- **Take breaks**: Burnout reduces retention
- **Celebrate wins**: Acknowledge progress along the way
"""
    }
]

def seed_phase18():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE18:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase18_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE18)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 18 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase18()
