"""
Curated Pega Knowledge Base — Phase 4A (One Stop Pega style)
Covers: Routing, Worklist/Workbasket, Sub-cases, Assignments, Correspondence Advanced,
        Circumstancing, Class Structure, Property Issues

Run: python -m crawler.seed_kb_phase4a
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE4A = [
    # ═══════════════════════════════════════════════════════════════════
    # ROUTING — Work routing, worklist, workbasket
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://onestoppega.com/routing-troubleshooting",
        "title": "Routing — Worklist, Workbasket, and Assignment Troubleshooting",
        "content": """# Routing — Worklist, Workbasket, and Assignment Troubleshooting

## Overview
Routing determines WHO gets an assignment in Pega. Assignments land in either a user's **Worklist** (personal queue) or a **Workbasket** (shared team queue). Routing problems are among the most common issues in Pega applications.

## How Routing Works
1. A flow reaches an Assignment shape
2. The Assignment shape has a "Route To" configuration
3. Routing evaluates to an Operator ID (worklist) or a Workbasket name
4. The assignment appears in that operator's worklist or the workbasket

## Routing Methods
- **Worklist**: Routes to a specific operator (e.g., `pyWorkParty(Operator).pxOperatorID`)
- **Workbasket**: Routes to a shared queue (e.g., `Claims-Processing`)
- **Business Logic**: Uses a when rule or decision table to determine the target
- **Least Busy**: Routes to the operator with fewest open assignments
- **Round Robin**: Distributes equally among operators
- **Skill-based**: Routes based on operator skills matching case requirements
- **Custom Activity**: Runs an activity to determine routing target

## Common Routing Problems

### 1. Assignment Not Appearing in Anyone's Worklist
**Symptoms**: Case moves to assignment step but nobody sees the assignment
**Root Causes**:
- Route-to expression evaluates to empty/null
- Operator ID doesn't exist or is disabled
- Workbasket doesn't exist
- Routing goes to the correct operator but they're looking at the wrong portal
- Access group doesn't have the work pool containing this case type

**Debug Steps**:
1. Open the case → Assignments tab → check where the assignment is routed
2. Check pyAssignedOperatorID and pyAssignmentStatus on the assignment
3. If workbasket: verify the workbasket exists (Records → Organization → Workbasket)
4. If operator: verify operator ID exists and is active
5. Check the operator's access group includes the right work pool
6. Use Tracer on the flow to see what the route-to expression evaluates to

### 2. Assignment Goes to Wrong Person
**Symptoms**: Assignment appears in the wrong operator's worklist
**Root Causes**:
- Route-to expression evaluates to the wrong operator
- Work party (Stakeholder, Owner, etc.) was set incorrectly earlier in the flow
- Default routing picking up the case creator instead of the intended assignee
- Circumstanced flow picking a different routing rule than expected

**Fix**:
1. Check the Assignment shape → Route To tab → what expression is used
2. Trace through the work parties: Clipboard → pyWorkParty page → check all parties
3. If using a decision table for routing: test the decision table with actual case data
4. Verify the correct flow version is executing (check circumstancing)

### 3. Workbasket Has Items But Operators Can't See Them
**Symptoms**: Items are in the workbasket but operators' "Get Next Work" returns nothing
**Root Causes**:
- Operators are not members of the workbasket
- Access group doesn't include the work pool
- Workbasket membership rule is wrong
- Operator doesn't have the required skill/role to see the work

**Fix**:
1. Check Workbasket rule → Members tab → verify operators are listed
2. Check operator's access group → Work pools → does it include this class?
3. Test with "Get Next Work" button in the portal
4. Check if skill-based routing is filtering out the operator

### 4. "Get Next Work" Returns Wrong Priority Order
**Symptoms**: Urgent items skipped, low-priority items picked first
**Root Causes**:
- Urgency not set correctly on cases (pxUrgencyWork)
- Workbasket selection criteria not using urgency
- SLA not attached or not escalating properly
- Custom "Get Next Work" activity overriding default behavior

**Fix**:
1. Check pxUrgencyWork on the assignments in the workbasket
2. Verify SLA rules are attached to the assignment
3. Review the workbasket's selection criteria / sort order
4. Check if a custom GetNextWork activity exists in the application

### 5. Assignment Stuck — Can't Complete or Route Forward
**Symptoms**: User clicks Submit/Approve but assignment doesn't move
**Root Causes**:
- Validation errors preventing flow advancement (check for hidden validation messages)
- Flow action has a connector condition that fails
- Post-processing activity throws an error
- Case is locked by another user/session
- Assignment is in "Review" status and needs a different action

**Fix**:
1. Open browser Developer Tools → Console for JavaScript errors
2. Check Tracer for flow action processing errors
3. Look for validation messages that might be hidden (check pyValidationMessages clipboard page)
4. Check if case is locked: case → Other Actions → View Lock Status
5. Verify the flow action's connector evaluates correctly

## Routing Best Practices
1. Always set a default/fallback route (don't let assignments go to null)
2. Use workbaskets for team work, worklists only for specific known operators
3. Test routing with multiple scenarios BEFORE going to production
4. Set up SLAs on all assignments to prevent items from getting stuck indefinitely
5. Use "ToWorkbasket" routing for new cases, "ToWorklist" only after a human claims the work
"""
    },
    {
        "url": "https://onestoppega.com/sub-case-troubleshooting",
        "title": "Sub-Cases (Child Cases) — Creation, Propagation, and Troubleshooting",
        "content": """# Sub-Cases (Child Cases) — Troubleshooting

## Overview
Sub-cases (child cases) are cases created within the context of a parent case. They enable breaking complex processes into manageable pieces. Common examples: a main Insurance Claim case spawns sub-cases for Document Review, Medical Assessment, and Payment Processing.

## How Sub-Cases Work
1. Parent case reaches a "Create Case" step in the flow
2. Sub-case is created with a reference back to the parent (pyParentCaseID)
3. Parent can wait for sub-case completion or continue in parallel
4. Data can be passed between parent and child via data propagation

## Common Sub-Case Problems

### 1. Sub-Case Not Being Created
**Symptoms**: Flow passes the Create Case step but no child case appears
**Root Causes**:
- Create Case step has a when condition that evaluates to false
- The sub-case type doesn't exist or has errors in its case type rule
- Insufficient privileges to create the sub-case type
- Data propagation fails before case creation completes

**Debug Steps**:
1. Use Tracer — look for the Create Case step execution
2. Check if a when condition on the Create Case shape is blocking
3. Verify the child case type exists and is valid (no compilation errors)
4. Check operator privileges for the child case type class

### 2. Data Not Passing from Parent to Child
**Symptoms**: Child case is created but fields are empty
**Root Causes**:
- Data propagation not configured on the Create Case step
- Property names don't match between parent and child (case-sensitive!)
- Source property is null/empty at the time of creation
- Data propagation uses a Data Transform that has errors

**Fix**:
1. Open the Create Case step → Data Propagation tab
2. Verify source → target property mappings
3. Check property names match exactly (including case)
4. If using a Data Transform: test it independently
5. Use Clipboard viewer to verify source properties have values BEFORE the Create Case step

### 3. Parent Case Stuck Waiting for Sub-Case
**Symptoms**: Parent case won't advance even though sub-case is resolved
**Root Causes**:
- Parent configured to "Wait for all sub-cases" but one sub-case is still open
- Sub-case resolved to a status the parent doesn't recognize as "complete"
- The "Wait" shape in the parent flow has wrong completion criteria
- Sub-case was resolved outside the normal flow (e.g., manually closed)

**Fix**:
1. Check all child cases — are ALL of them in Resolved/Closed status?
2. Check the parent flow's Wait shape — what completion criteria is set?
3. Verify pyStatusWork on the sub-case matches what the parent expects
4. If one sub-case is stuck: resolve it manually or fix its flow
5. Check if the parent has a "Spine" (case wide) flow that's blocking

### 4. Sub-Case Resolving Before Parent Expects
**Symptoms**: Sub-case completes too early, parent continues before it should
**Root Causes**:
- Sub-case flow is too short (missing steps)
- Auto-processing resolves the sub-case immediately
- No assignments in the sub-case flow (all automated)
- Sub-case creation is non-blocking (parallel) when it should be sequential

**Fix**:
1. Review the Create Case step: is it set to "Wait" or "Don't wait"?
2. Check the sub-case flow for missing assignment steps
3. If sub-case should block parent: set "Wait for this case to complete"

### 5. Circular Sub-Case Creation
**Symptoms**: Infinite loop of sub-cases being created, system slowdown/crash
**Root Causes**:
- Case type A creates sub-case type B, which creates sub-case type A
- Flow loop creates sub-case on every iteration without exit condition
- Declare OnChange triggers case creation in a loop

**Fix**:
1. Add maximum depth check before creating sub-cases
2. Review flow for proper exit conditions on loops
3. Check Declare OnChange rules — ensure they don't trigger cascade creation

## Data Propagation Between Parent and Child
- **Parent → Child**: Configured on Create Case step (Data Propagation tab)
- **Child → Parent**: Use "Propagate to parent" option on Resolve step, or use Data Transform
- **Bidirectional**: Use Data Pages or linked properties (avoid — creates tight coupling)

## Sub-Case Best Practices
1. Keep sub-case flows simple — complex logic stays in the parent
2. Always define what data propagates back to parent on resolution
3. Set SLAs on sub-cases so they don't hang indefinitely
4. Use parallel processing only when sub-cases are truly independent
5. Test the full parent-child lifecycle end-to-end before production
"""
    },
    {
        "url": "https://onestoppega.com/approval-process-troubleshooting",
        "title": "Approval Process — Cascading Approvals, Authority Matrix, and Troubleshooting",
        "content": """# Approval Process — Troubleshooting

## Overview
Pega supports multiple approval patterns: simple one-level approval, cascading (multi-level) approval, authority matrix-based approval, and custom approval flows. Approval steps are implemented using the Approval process in Case Designer or via flow actions.

## Approval Types
- **One-level**: Single approver based on reporting manager or specific role
- **Cascading**: Chain of approvers going up the management hierarchy until authority limit is met
- **Authority Matrix**: Decision table maps case attributes (amount, type, region) to required approvers
- **Voting**: Multiple approvers vote, majority or unanimous wins
- **Custom**: Activity or decision strategy determines approvers

## Common Approval Issues

### 1. Approval Assignment Not Going to the Right Manager
**Symptoms**: Approval goes to wrong person or to nobody
**Root Causes**:
- Reporting structure not configured in operator records (pyReportTo is empty)
- Using wrong work party for the approver lookup
- Operator's manager is disabled/inactive
- Cascading approval logic not finding the next level

**Debug Steps**:
1. Check the case creator's operator record → pyReportTo field
2. Verify the approval flow's "Route To" logic
3. Trace the approval step to see which operator is resolved
4. For cascading: check each level's manager chain is unbroken

### 2. Cascading Approval Goes Too Many or Too Few Levels
**Symptoms**: Approval escalates endlessly, or stops before reaching sufficient authority
**Root Causes**:
- Authority limit not set correctly on the approval step
- Authority matrix conditions don't match the case data
- Manager chain has a loop (manager A reports to B, B reports to A)
- Top-level manager has no reportTo — cascading has no termination

**Fix**:
1. Verify authority matrix / decision table for the approval
2. Check for circular reporting: query operator records for loops
3. Ensure a termination condition: max levels, authority threshold, or top-of-org flag
4. Test with various case amounts/types to verify the right number of levels

### 3. Approval Action Buttons Not Working
**Symptoms**: Approve/Reject buttons visible but clicking does nothing
**Root Causes**:
- Flow action validation failing silently
- JavaScript error preventing form submission
- Missing connector from the approval flow action
- Case locked by another session

**Fix**:
1. Check browser console for JS errors
2. Use Tracer while clicking the button — look for flow action errors
3. Verify the approval flow action has proper connectors (Approve → next step, Reject → reject step)
4. Check case lock status

### 4. Rejected Case Doesn't Return to Submitter
**Symptoms**: After rejection, case goes to wrong state or gets stuck
**Root Causes**:
- Reject connector not configured properly in the flow
- No "return to submitter" routing on the reject path
- Case status set to Resolved-Rejected but should go back to Open for rework

**Fix**:
1. Open the approval flow → check the Reject connector → where does it route?
2. Verify the reject path has routing back to the original submitter
3. Check pyStatusWork after rejection — should it be "Open" for rework?
4. Add a proper rejection reason field and rework assignment

### 5. Authority Matrix Not Matching
**Symptoms**: All approvals go to one level regardless of case attributes
**Root Causes**:
- Decision table conditions not evaluating correctly
- Properties used in authority matrix are empty at approval time
- Wrong version of decision table being used (circumstancing)
- Allowed values don't match actual data (e.g., "USD" vs "US Dollar")

**Fix**:
1. Open the authority matrix / decision table → test with actual case values
2. Check that all referenced properties are populated on the clipboard
3. Verify the decision table is not circumstanced unexpectedly
4. Check for exact value matching (whitespace, case, format)

## Approval Best Practices
1. Always configure both Approve and Reject paths — don't leave dead ends
2. Set SLAs on approval assignments to prevent bottlenecks
3. Add a "delegate" option for managers who are out of office
4. Keep authority matrix simple — complex matrices are hard to debug
5. Log approval decisions for audit trail (who approved, when, at what level)
6. Test the full approval chain with edge cases (absent manager, amount boundaries)
"""
    },
    {
        "url": "https://onestoppega.com/circumstancing-troubleshooting",
        "title": "Circumstancing Rules — Configuration, Resolution, and Troubleshooting",
        "content": """# Circumstancing Rules — Troubleshooting

## Overview
Circumstancing in Pega allows you to create variant versions of rules that apply under specific conditions — without modifying the base rule. Think of it as "if-then" rule selection: if condition X is true, use this variant; otherwise use the base rule.

## How Circumstancing Works
1. A base rule exists (e.g., a Data Transform for "CreateNewClaim")
2. You create a circumstanced version with specific conditions (e.g., Region = "EMEA")
3. At runtime, Pega's rule resolution checks if any circumstance conditions match
4. If matched: uses the circumstanced version. If not: falls back to the base rule.

## Circumstance Types
- **Single Property**: Rule varies based on one property value (e.g., pyCountry = "US")
- **Multi-Property**: Rule varies based on combination of properties
- **Date Range**: Rule applies only within a date range (effective dating)
- **Template**: Based on a circumstance template (reusable condition)
- **As-of Date**: Uses a specific date property for temporal circumstancing

## Common Circumstancing Issues

### 1. Circumstanced Rule Not Being Picked Up
**Symptoms**: The base rule always executes, even when the condition should match
**Root Causes**:
- Circumstance property value doesn't match exactly (case, whitespace, format)
- Property is empty/null at the time of rule resolution
- Circumstanced rule is in a different ruleset version that's not in the stack
- Rule resolution picks a higher-priority non-circumstanced rule from a higher ruleset
- Circumstance is "Date Range" and current date is outside the range

**Debug Steps**:
1. Use "View Rule Resolution" on the rule form (Other Actions → View Rule Resolution)
2. Check the clipboard for the circumstance property value — does it match EXACTLY?
3. Verify the circumstanced rule's ruleset version is in the application's ruleset stack
4. Check if another rule in a higher ruleset is overriding the circumstanced version
5. For date-range: verify the current date falls within the configured range

### 2. Wrong Circumstanced Version Executing
**Symptoms**: A circumstanced rule runs, but it's the wrong variant
**Root Causes**:
- Multiple circumstanced versions exist — wrong one has higher priority
- Circumstance conditions overlap (e.g., Region=US and Region=US+Type=Auto both match)
- Ruleset stack order causes unexpected resolution
- Multi-property circumstance has partial match picking wrong variant

**Fix**:
1. View Rule Resolution to see ALL candidate rules and their priority
2. Check for overlapping circumstance conditions
3. Review ruleset stack order — higher rulesets win
4. For multi-property: ensure the most specific variant has higher priority

### 3. Circumstanced Rule Causes "Rule Not Found"
**Symptoms**: Error about missing rule, but the base rule exists
**Root Causes**:
- The base rule was deleted or moved, but circumstanced versions still reference it
- Circumstance evaluation throws an error, causing the resolution to fail entirely
- Rule is circumstanced in a locked ruleset that wasn't checked out properly

**Fix**:
1. Verify the base rule exists in the expected class and ruleset
2. Check if the circumstance property evaluation itself throws an error
3. Look for broken references in the circumstanced rule form
4. Re-save the circumstanced rule if it references a moved base

### 4. Performance Issues with Circumstancing
**Symptoms**: Slow rule execution, especially for frequently-called rules
**Root Causes**:
- Too many circumstanced versions (Pega checks all candidates)
- Circumstance property requires expensive computation
- Template-based circumstances with complex when rules

**Fix**:
1. Minimize the number of circumstanced versions (consolidate where possible)
2. Ensure circumstance properties are already on the clipboard (not computed on demand)
3. Use simple property-based circumstances over template-based when possible
4. Consider using decision tables instead of heavily-circumstanced rules

## Circumstancing vs Other Approaches
| Use Case | Circumstancing | Decision Table | When Rule |
|----------|---------------|----------------|-----------|
| Different behavior by region | Good | Also good | Not ideal |
| Complex multi-condition logic | Limited | Better | Best for boolean |
| Date-effective rules | Best | Manual | No |
| Performance at scale | Degrades with many variants | Scales better | Fast |

## Best Practices
1. Always have a base (non-circumstanced) rule as fallback
2. Use "View Rule Resolution" to verify which variant gets picked
3. Document WHY each circumstanced version exists
4. Avoid deeply nested or overlapping circumstances
5. Test with all possible property values, including null/empty
6. Prefer decision tables for complex branching logic over many circumstanced rules
"""
    },
    {
        "url": "https://onestoppega.com/class-structure-troubleshooting",
        "title": "Class Structure — Inheritance, Class Groups, and Common Errors",
        "content": """# Class Structure — Inheritance, Class Groups, and Common Errors

## Overview
Everything in Pega is organized into **classes**. Classes form a hierarchy (inheritance tree) that controls rule resolution, data storage, and access. Understanding class structure is fundamental to debugging rule-not-found errors, data mapping issues, and inheritance problems.

## Class Hierarchy
```
@baseclass
├── Rule-                    (all rule types: Rule-HTML-Section, Rule-Obj-Activity, etc.)
├── Data-                    (reusable data classes)
│   ├── Data-Party
│   ├── Data-Address
│   └── MyApp-Data-Customer  (your custom data classes)
├── Work-                    (all case/work types)
│   └── MyApp-Work-          (your application work pool)
│       ├── MyApp-Work-Claim
│       └── MyApp-Work-ServiceRequest
├── Embed-                   (embedded pages — no persistence)
├── Code-                    (code/lookup table classes)
└── @baseclass               (ultimate fallback for all rules)
```

## Key Concepts
- **Directed Inheritance**: A class explicitly inherits from another (configured in the class rule)
- **Pattern Inheritance**: Dashes in class names create implicit inheritance (MyApp-Work-Claim inherits from MyApp-Work-)
- **Class Group**: Maps a top-level class to a database table (all work types under MyApp-Work- share one table)
- **Abstract Class**: Blueprint class that can't be instantiated directly (e.g., MyApp-Work-)
- **Concrete Class**: Can be instantiated as a case (e.g., MyApp-Work-Claim)

## Common Class Structure Errors

### 1. "Rule not found" / "No rule found for class"
**Symptoms**: Rule exists but Pega can't find it at runtime
**Root Causes**:
- Rule is defined on wrong class (e.g., on Data- instead of Work-)
- Ruleset containing the rule is not in the application's ruleset stack
- Class hierarchy broken — inheritance chain doesn't reach the class where rule is defined
- Rule exists but is withdrawn, deleted, or in a checked-out ruleset branch

**Debug Steps**:
1. Search for the rule by name — which class is it on?
2. Check the executing class — does it inherit from the class where the rule lives?
3. Verify ruleset stack includes the rule's ruleset version
4. Use "Rule Resolution" tool to see which candidates are found

### 2. "Class not found" / "Cannot create instance of class"
**Symptoms**: Error when creating a case or data object
**Root Causes**:
- Class doesn't exist or is misspelled (classes are case-sensitive!)
- Class exists but is abstract (can't instantiate)
- Class group table doesn't exist in database
- Application doesn't include the class's ruleset

**Fix**:
1. Verify exact class name spelling and case
2. Check class rule → is it marked as concrete or abstract?
3. For work classes: check class group → database table exists
4. Verify the application includes the class's ruleset

### 3. Properties Not Inheriting as Expected
**Symptoms**: Property exists on parent class but not visible on child class
**Root Causes**:
- Property is defined on a class that's NOT in the inheritance chain
- Directed inheritance misconfigured — child points to wrong parent
- Property is in a ruleset not in the child's application stack
- Pattern inheritance broken by non-standard class naming

**Fix**:
1. Check the child class rule → Directed Inheritance field → points to correct parent?
2. Verify the property's ruleset is in the application's stack
3. Walk the inheritance chain: Child → Parent → Grandparent → @baseclass
4. Use Records → SysAdmin → Class hierarchy to visualize

### 4. Data Saving to Wrong Database Table
**Symptoms**: Data appears in unexpected table, or "Table not found" error
**Root Causes**:
- Class group mapping is wrong
- Multiple class groups point to different tables
- Class doesn't have a class group (no persistence configured)
- Database table was renamed or dropped

**Fix**:
1. Open the class rule → check "Class Group" association
2. Verify class group → Database table name matches actual database
3. Use Data Admin → Database to check table mappings
4. If class has no class group: it can't persist data — add one or inherit from a class that has one

### 5. Cross-Application Class Access Issues
**Symptoms**: "Access denied to class" or "Class not available" errors
**Root Causes**:
- Class belongs to a different application and isn't exposed
- Built-on application doesn't include the required ruleset
- Access group doesn't have the class's work pool

**Fix**:
1. Check Application rule → Built-on tab → is the other application listed?
2. Verify the class's ruleset is accessible from your application
3. Check access group → Work pools for the class

## Debugging Class Issues — Quick Reference
| What to check | Where to find it |
|---------------|-----------------|
| Class hierarchy | Records → SysAdmin → Class |
| Directed inheritance | Open class rule → General tab |
| Class group / table | Open class rule → Data Storage tab |
| Ruleset stack | Application rule → Definition tab |
| Rule resolution | Rule form → Other Actions → View Rule Resolution |
"""
    },
    {
        "url": "https://onestoppega.com/property-troubleshooting",
        "title": "Property Rules — Types, Modes, and Common Troubleshooting",
        "content": """# Property Rules — Types, Modes, and Common Troubleshooting

## Overview
Properties are the data elements in Pega — they define what data an application stores and processes. Properties can be simple values, pages (objects), lists, or computed values. Many bugs trace back to incorrect property configuration.

## Property Types
- **Text**: String values (pyLabel, pyDescription)
- **Integer**: Whole numbers (pxUrgencyWork)
- **Decimal**: Floating point (TotalAmount)
- **DateTime**: Date/time values (pxCreateDateTime)
- **Boolean**: True/false (IsApproved)
- **Date**: Date only, no time (DateOfBirth)
- **Time**: Time only, no date
- **Identifier**: Special text for IDs (pzInsKey)

## Property Modes
- **Value**: Stores a single value (most common)
- **Page**: Contains an embedded object/page (Address page with Street, City, Zip)
- **Page List**: Ordered list of pages (LineItems — list of order items)
- **Page Group**: Keyed collection of pages (indexed by a key property)
- **Value List**: List of simple values (list of email addresses)
- **Value Group**: Keyed collection of simple values

## Common Property Issues

### 1. "Property not found on clipboard"
**Symptoms**: Error referencing a property that should exist
**Root Causes**:
- Property name misspelled (CASE SENSITIVE in Pega!)
- Property defined on wrong class
- Property exists but the page it's on wasn't created
- Referencing .PropertyName instead of .PageName.PropertyName (missing page context)

**Debug Steps**:
1. Check exact property name spelling (including case)
2. Check which class the property is defined on
3. Use Clipboard viewer (Dev Tools → Clipboard) to see what's actually there
4. Verify the parent page exists: if property is .Address.City, does .Address page exist?

### 2. Property Value is Empty When It Shouldn't Be
**Symptoms**: Property should have a value but it's blank
**Root Causes**:
- Data Transform or Activity didn't set the value
- Data Page that supplies the value hasn't loaded yet
- Declare Expression that computes the value has an error
- Property was set but then overwritten by a later step
- Clipboard page was recreated (clearing all values)

**Fix**:
1. Use Tracer to track when/how the property gets set
2. Check Data Transform steps that target this property
3. If computed by Declare Expression: verify the expression and its trigger properties
4. Check if a "Page-New" or "Page-Remove" clears the containing page

### 3. Page List Not Populating / Wrong Number of Rows
**Symptoms**: Repeating grid shows no rows, or wrong number of rows
**Root Causes**:
- Data page that feeds the page list has wrong parameters or an error
- Iterator/loop in Data Transform has wrong source
- Append vs Overwrite mode wrong — overwriting on each iteration
- Source data has duplicates that get merged or filtered

**Fix**:
1. Check the Data Page feeding the page list — does it return data?
2. In Data Transform: verify the source page list and mapping
3. Check Append vs Overwrite setting on the page list mapping
4. Use Clipboard viewer to see the raw page list contents

### 4. Property Truncation / Data Loss on Save
**Symptoms**: Value gets cut off after saving the case
**Root Causes**:
- Property max length too small (e.g., Text max 32 chars but data is 100+)
- Database column size smaller than property max length
- Special characters causing encoding issues
- BLOB/CLOB column not used for large text

**Fix**:
1. Check property rule → Max Length setting
2. Check database column: `SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = 'pc_work'`
3. For large text: use Text (large) or CLOB-mapped property
4. Run "Update Database Schema" if property definition changed

### 5. Declare Expression Not Firing
**Symptoms**: Computed property stays empty or stale
**Root Causes**:
- Trigger properties not configured correctly (Declare Expression doesn't know when to recalculate)
- Declare Expression has a circular dependency
- Property is also set by a Data Transform, overwriting the computed value
- Change tracking is disabled on the trigger property

**Fix**:
1. Open the Declare Expression → check "Participating Properties" (triggers)
2. Verify there are no circular references (A computes B, B computes A)
3. Check if any Data Transform or Activity also sets this property (conflict!)
4. Enable change tracking on the trigger properties

### 6. "Invalid date format" on DateTime Properties
**Symptoms**: Date/time value causes parse error
**Root Causes**:
- Date format doesn't match Pega's internal format (yyyyMMdd'T'HHmmss.SSS GMT)
- Integration returns date in different format (ISO 8601, Unix timestamp, etc.)
- Locale/timezone mismatch between systems

**Fix**:
1. Use @DateTimeString or pxParseDateTime to convert formats
2. Check source system's date format documentation
3. Add explicit format conversion in the Data Transform or connector mapping
4. Set the expected timezone in the conversion function

## Property Best Practices
1. Use meaningful names with proper casing (PascalCase for custom, pyPascalCase for standard)
2. Always set appropriate Max Length for text properties
3. Document the purpose of each property in the Description field
4. Use Declare Expressions for computed values, not Activities
5. Test with edge cases: null, empty string, max length, special characters
6. Run "Update Database Schema" after property changes
"""
    },
    {
        "url": "https://onestoppega.com/correspondence-advanced-troubleshooting",
        "title": "Correspondence and Email — Advanced Templates, Attachments, and Troubleshooting",
        "content": """# Correspondence and Email — Advanced Troubleshooting

## Overview
Correspondence in Pega generates formatted communications (emails, letters, PDFs) from templates. Correspondence rules merge case data into templates and deliver via email, print, or attachment. Common in notifications, approvals, and customer communications.

## Correspondence Architecture
- **Correspondence rule**: Defines the template (HTML/text with property references)
- **Send Correspondence step**: Flow step that triggers sending
- **Email Account**: SMTP configuration for outgoing email
- **Notification**: Lightweight alternative for simple emails

## Common Correspondence Issues

### 1. Email Not Being Sent
**Symptoms**: Send Correspondence step completes but no email received
**Root Causes**:
- SMTP email account not configured or misconfigured
- No "To" address resolved (recipient property is empty)
- Email queued but email agent is not running
- Email blocked by corporate firewall or spam filter
- Send Correspondence step skipped due to when condition

**Debug Steps**:
1. Check the correspondence rule → Recipients tab → is "To" address populated?
2. Check email account configuration: Records → SysAdmin → Email Account
3. Verify the email agent is running: Admin Studio → Agents → look for email-related agents
4. Check the email outbox/queue: Data-Corr-Email instances
5. Check SMTP server connectivity from Pega server
6. Look in PegaRULES log for SMTP errors

### 2. Email Content Has Blank Fields / Missing Data
**Symptoms**: Email sent but property references show blank or <<PropertyName>>
**Root Causes**:
- Property references in template use wrong syntax
- Properties not on the clipboard at send time
- Property is on a different page than what the template references
- Correspondence runs in background (agent) without the case page loaded

**Fix**:
1. Check property references in correspondence: use `<<.PropertyName>>` syntax
2. For properties on sub-pages: `<<.Address.City>>` not `<<.City>>`
3. Ensure the step context has the case loaded (use Step Page or load explicitly)
4. If sent via agent: make sure the case page is loaded before sending
5. Test with Tracer active to see clipboard state at send time

### 3. HTML Email Renders as Plain Text
**Symptoms**: Email shows raw HTML tags instead of formatted content
**Root Causes**:
- Content-Type header not set to text/html
- Email client stripping HTML (security setting)
- Correspondence rule set to "Plain Text" instead of "HTML"

**Fix**:
1. Check correspondence rule → Content Type → should be "HTML"
2. Verify email headers include Content-Type: text/html
3. Test with different email clients to rule out client-side stripping

### 4. Email Attachment Issues
**Symptoms**: Attachment missing, corrupt, or wrong file
**Root Causes**:
- Attachment reference points to wrong location
- File too large for email limits
- Attachment content type (MIME type) wrong
- PDF generation fails silently, sending empty attachment

**Fix**:
1. Check correspondence rule → Attachments tab
2. Verify the attachment source (case attachment, generated PDF, etc.)
3. Check file size limits in email account configuration
4. If PDF: test PDF generation separately before attaching

### 5. Bulk Correspondence Performance
**Symptoms**: Sending many emails takes too long or times out
**Root Causes**:
- Sending synchronously instead of using queue
- SMTP connection opened/closed per email (no connection pooling)
- Large templates with many property lookups
- Attachments generated per-email instead of reused

**Fix**:
1. Use queue-based sending (email agent) for bulk operations
2. Optimize template — reduce number of property references
3. Pre-generate common attachments
4. Increase email agent frequency and thread count for bulk periods

## Correspondence Best Practices
1. Always test emails in a non-production environment first
2. Use notification rules for simple alerts, correspondence for formal communications
3. Set up error handling for failed email delivery
4. Keep templates simple — complex HTML email rendering varies across clients
5. Use CC/BCC sparingly to avoid spam filter triggers
6. Log all sent correspondence for audit compliance
"""
    },
    {
        "url": "https://onestoppega.com/data-page-advanced-troubleshooting",
        "title": "Data Pages — Advanced Patterns, Scope, Refresh, and Troubleshooting",
        "content": """# Data Pages — Advanced Patterns and Troubleshooting

## Overview
Data Pages are Pega's declarative data caching mechanism. They load data on demand (from a database, connector, activity, etc.) and cache it for reuse. Understanding scope, refresh, and load behavior is critical for debugging data issues.

## Data Page Scope
- **Thread**: Private to the current flow execution. Destroyed when the flow ends. Use for case-specific lookups.
- **Requestor**: Private to the current user session. Survives across flows but clears when session ends. Use for user-specific preferences.
- **Node**: Shared across ALL users on one Pega node. Use for reference data that rarely changes (country list, config values). CAUTION: node-scoped pages consume memory permanently.

## Common Data Page Issues

### 1. Data Page Returns Stale/Cached Data
**Symptoms**: Data page shows old values even after source data changed
**Root Causes**:
- Data page scope is Requestor or Node — it's cached from a previous load
- No refresh strategy configured
- "Reload once per interaction" not set appropriately
- Node-scoped data page cached across all users

**Fix**:
1. Check data page scope — Node and Requestor scope survive beyond one request
2. Add a refresh strategy: "Reload when" with a condition, or set a refresh interval
3. For testing: use Clipboard → right-click data page → Force Reload
4. For Node scope: any change requires explicit invalidation or reload on ALL nodes

### 2. Data Page Fails to Load / Returns Empty
**Symptoms**: Data page exists but has no data
**Root Causes**:
- Source (connector, activity, report definition) has an error
- Parameters not passed correctly (data page parameters are empty)
- Source returns data in a format that doesn't map to the data page's class
- Authentication failure on connector (external data source)
- Data page load timing — accessed before parameters are available

**Debug Steps**:
1. Check the data page rule → Source tab → what loads it?
2. Run the source independently (test the connector, run the report, etc.)
3. Check data page parameters — are they being passed from the UI/flow?
4. Use Tracer with "Data Page" events enabled to see load attempts and errors
5. Check PegaRULES log for connector errors if loading from external source

### 3. "Data page is already loading" Deadlock
**Symptoms**: Page hangs, timeout error, "Data page X is being loaded" message
**Root Causes**:
- Circular dependency: Data Page A loads Data Page B, which loads Data Page A
- Data page source is slow (long database query or external call)
- Multiple threads trying to load the same Node-scoped data page simultaneously

**Fix**:
1. Check for circular data page references — map out the dependency chain
2. Optimize the source query/connector (add indexes, reduce data volume)
3. For Node scope: Pega serializes concurrent loads — optimize load time
4. Add timeout configuration to prevent indefinite waits

### 4. Data Page Parameters Not Working
**Symptoms**: Same data regardless of different parameter values
**Root Causes**:
- Parameters not declared on the data page rule
- Parameter passed with wrong name (case-sensitive!)
- Source (connector/activity) doesn't use the parameter
- Node-scoped data page ignoring parameters (only loads once with first parameter set)

**Fix**:
1. Open data page rule → Parameters tab → verify parameters are declared
2. Check where the data page is referenced — are parameters passed in the page reference?
3. Syntax: `D_CustomerInfo[CustomerID: .pyID]` — parameter name must match declaration
4. Verify the source actually filters by the parameter

### 5. Memory Issues with Data Pages
**Symptoms**: OutOfMemoryError, slow performance, high JVM heap usage
**Root Causes**:
- Node-scoped data page loading too much data (millions of rows)
- Requestor-scoped data pages not cleaning up (too many active sessions)
- Page list data pages with unbounded results (no pagination)

**Fix**:
1. Add result limits to data page sources (TOP N, LIMIT clause)
2. Use Thread scope instead of Requestor when data is only needed within one flow
3. For large datasets: use pagination or search instead of loading everything
4. Monitor memory with PAL and JVM heap analysis tools
5. Implement data page cleanup strategies for long-running sessions

## Data Page Refresh Strategies
| Strategy | When to Use |
|----------|-------------|
| No refresh | Static reference data (country codes, etc.) |
| Reload once per interaction | Data that might change between user actions |
| Reload if older than X minutes | Data with known cache duration |
| Reload when condition is true | Data that needs refresh based on business logic |
| Force reload via activity | Manual control for admin/troubleshooting |

## Best Practices
1. Use the narrowest scope possible (Thread > Requestor > Node)
2. Always configure refresh strategy for non-static data
3. Limit result sets — never load "all records" into a data page
4. Monitor node-scoped data page memory consumption
5. Use parameterized data pages instead of loading all data and filtering client-side
6. Test data page behavior across multiple sessions and nodes
"""
    },
    {
        "url": "https://onestoppega.com/pega-unit-testing-troubleshooting",
        "title": "Pega Unit Testing (PegaUnit) — Writing Tests, Common Failures, and Troubleshooting",
        "content": """# Pega Unit Testing (PegaUnit) — Troubleshooting

## Overview
PegaUnit is Pega's built-in unit testing framework. It allows developers to write automated tests for activities, data transforms, when rules, decision tables, and other rule types. Tests run within Pega and validate business logic without manual testing.

## How PegaUnit Works
1. Create a Test Case rule (Rule-Test-Case)
2. Configure test steps: Set clipboard, Run rule, Assert results
3. Execute test manually or as part of a test suite
4. Review pass/fail results in the test dashboard

## Test Step Types
- **Set**: Place values on the clipboard before running the rule
- **Run**: Execute the rule being tested
- **Assert Equals**: Verify a property has an expected value
- **Assert True/False**: Verify a boolean condition
- **Assert Not Null**: Verify a property has any value
- **Mock**: Replace a called rule with a fake implementation (e.g., mock a connector)

## Common PegaUnit Issues

### 1. Test Passes in Dev But Fails in QA/Prod
**Symptoms**: Test green locally, red after deployment
**Root Causes**:
- Test depends on specific data that exists in Dev but not QA (operator IDs, reference data)
- Rule resolution differs (different ruleset versions in QA)
- Environment-specific configuration (DSS, prconfig.xml differences)
- Connector mock not applied in QA environment

**Fix**:
1. Remove dependencies on environment-specific data — use test setup steps
2. Mock all external connectors and data pages
3. Check ruleset stack matches between environments
4. Use test data setup/teardown instead of relying on existing data

### 2. Test Fails with "Page Not Found" or "Property Not Found"
**Symptoms**: Assert step can't find the expected property/page
**Root Causes**:
- Clipboard setup is incomplete — rule expects pages that weren't set up
- Rule creates pages with different names than expected
- Rule modifies clipboard in unexpected ways (Page-Remove, Page-New)

**Fix**:
1. Review the rule being tested — what clipboard structure does it expect?
2. Add more Set steps to properly configure the clipboard before Run
3. Use Tracer during test execution to see actual clipboard changes
4. Check for Page-New/Page-Remove steps that might reorganize the clipboard

### 3. Mocking Not Working
**Symptoms**: Real connector/activity runs instead of mock, causing test failure
**Root Causes**:
- Mock step is after the Run step (must be before!)
- Mock target doesn't match the actual rule being called (class, name mismatch)
- Mock is on wrong class (rule resolves to a different class than mocked)

**Fix**:
1. Ensure Mock steps come BEFORE the Run step in test case order
2. Verify the mock target matches exactly: class + rule name
3. Check rule resolution to confirm which version of the rule gets called
4. Use the "qualified name" for mocking (Class.RuleName)

### 4. Test Suite Execution Order Issues
**Symptoms**: Tests pass individually but fail when run as a suite
**Root Causes**:
- Tests share clipboard state — one test's output pollutes another test's input
- Shared Node-scoped data pages retain state between tests
- Tests depend on specific execution order

**Fix**:
1. Add cleanup/teardown steps at the end of each test
2. Avoid depending on Node-scoped data pages in tests
3. Make each test fully self-contained (setup → run → assert → cleanup)
4. Don't rely on test execution order

## PegaUnit Best Practices
1. Mock ALL external dependencies (connectors, data pages, external systems)
2. Test one rule per test case — keep tests focused
3. Include both positive (happy path) and negative (error) test scenarios
4. Use descriptive test names that explain what's being validated
5. Set up and tear down clipboard state in each test
6. Run tests as part of CI/CD pipeline (Deployment Manager can trigger test suites)
7. Aim for test coverage on critical business logic, not utility rules
"""
    },
]


def seed_phase4a():
    """Write Phase 4A curated docs to raw_docs directory."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc in CURATED_DOCS_PHASE4A:
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
        filename = f"phase4a_{slug}.json"
        filepath = RAW_DOCS_DIR / filename

        payload = {
            "url": doc["url"],
            "title": doc["title"],
            "content": doc["content"].strip(),
        }
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE4A)}] Saved: {doc['title']}")

    logger.info(f"\nPhase 4A complete — {count} documents saved to {RAW_DOCS_DIR}")
    logger.info("Next: python -m indexer.index_docs")


if __name__ == "__main__":
    seed_phase4a()
