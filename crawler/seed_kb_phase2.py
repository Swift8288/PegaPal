"""
Curated Pega Knowledge Base — Phase 2
Covers: Activity errors, Data Pages, Clipboard issues, When rules,
Flow errors, Data Transforms, Correspondence, Import/Export, and more.

Run: python -m crawler.seed_kb_phase2
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE2 = [
    # ═══════════════════════════════════════════════════════════════════
    # ACTIVITY ERRORS — Common failures and debugging
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/activities/activity-errors.html",
        "title": "Activity Errors — Common Failures and Debugging Guide",
        "content": """# Activity Errors — Complete Debugging Guide

## Overview
Activities are step-based rule types that execute server-side logic. When an activity fails, the error can originate from any step — understanding the failure patterns helps isolate the root cause quickly.

## Common Activity Errors

### "Activity failed status error"
**Root Cause**: The activity completed but one or more steps returned a failure status. The pyStatusValue property is set to a non-success value.
**Diagnosis**:
1. Enable Tracer with Activity Steps + Exceptions event types
2. Run the activity and check which step sets pyStatusValue to failure
3. Look at pyStatusMessage for the specific error description
4. Check the step's method — Obj-Save, Obj-Open, Connect-REST, etc. each have their own failure modes

**Common causes of activity failed status**:
- Obj-Save failed due to locking or constraint issues
- Obj-Open failed because the object was not found
- Connect-REST/SOAP returned an HTTP error
- A When condition evaluated unexpectedly
- A called activity or data transform threw an exception
- Property-Set failed due to type mismatch

**Fix**:
1. Wrap critical steps in try-catch blocks
2. Check pyStatusValue after each database or connector step
3. Add logging steps to capture property values at failure points
4. Verify all referenced pages exist on the clipboard before use
5. Check the step's transition conditions (Jump, Exit, etc.)

### "Step X failed: Page 'PageName' not found on clipboard"
**Root Cause**: The activity references a clipboard page that doesn't exist at the time the step executes.
**Fix**:
1. Ensure the page is created before the step (via Obj-Open, Page-New, or Data Transform)
2. Check if a previous step removed the page (Page-Remove)
3. Verify the page name spelling matches exactly (case-sensitive)
4. If the page comes from a data page, ensure the data page has loaded

### "Activity step timeout"
**Root Cause**: A step took longer than the configured timeout.
**Fix**:
1. Check for slow database queries (Obj-List without proper filters)
2. Check for external service calls that are timing out
3. Optimize the step logic or increase the timeout
4. Consider moving heavy processing to a Queue Processor

### "Java exception in activity step"
**Root Cause**: A Java step or Java-backed method threw an unhandled exception.
**Fix**:
1. Check PegaRULES log for the full Java stack trace
2. Common causes: NullPointerException (missing page/property), ClassCastException (type mismatch)
3. Wrap Java steps in try-catch
4. Replace Java steps with Pega method steps where possible (Guardrails compliance)

### "Activity not found / rule not resolved"
**Root Cause**: The activity rule cannot be resolved from the current context.
**Fix**:
1. Check the activity's class (applies-to) matches the calling context
2. Verify the ruleset and version are available in the calling application
3. Check for circumstance-qualified activities that might not match
4. Verify access controls — the operator may not have access to the ruleset

### "Infinite loop detected in activity"
**Root Cause**: Activity calls itself recursively or has a loop step that never terminates.
**Fix**:
1. Check loop conditions — ensure they converge (counter increments, list decrements)
2. Check for recursive activity calls (Activity A calls Activity B which calls Activity A)
3. Add a maximum iteration limit to loop steps
4. Use Tracer to see the execution path

## Activity Debugging Best Practices
- Always use Tracer as the first debugging step
- Add Obj-Validate before Obj-Save to catch data issues early
- Use try-catch-finally for all database and connector operations
- Log step entry/exit for complex activities
- Check pyStatusValue and pyStatusMessage after critical operations
- Use Page-Remove in finally blocks to prevent clipboard bloat
- Test activities in standalone mode before embedding in flows
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/activities/activity-best-practices.html",
        "title": "Activity Configuration — Parameters, Pages, and Common Mistakes",
        "content": """# Activity Configuration — Common Mistakes

## Parameter Tab Errors

### "Parameter type mismatch"
**Root Cause**: The activity expects a parameter of one type but receives another.
**Fix**: Check the calling rule — ensure parameter types match (String, Integer, Boolean, Page, etc.)

### "Required parameter not provided"
**Root Cause**: A parameter marked as required was not passed by the caller.
**Fix**: Check all callers of this activity and ensure they pass all required parameters.

## Pages & Classes Tab Errors

### "Page not found" on Pages tab reference
**Root Cause**: The page listed in the Pages & Classes tab doesn't exist when the activity runs.
**Fix**:
1. Pages listed here are NOT automatically created — they must exist before the activity runs
2. Check if the calling flow/activity creates these pages
3. Use "Obj-Open" or "Page-New" in Step 1 to create the page
4. The Primary page is the only page guaranteed to exist (if called from a flow)

### "Class mismatch on page"
**Root Cause**: The page's actual class doesn't match what's declared in Pages & Classes.
**Fix**: Verify the page was created with the correct class in Obj-Open or Page-New.

## Step Method Errors

### "Property-Set: property is read-only"
**Root Cause**: Attempting to set a value on a property that is declared as read-only or is a system property.
**Fix**: Check if the property is a calculated (Declare Expression) property or a system property (pz-prefixed).

### "Call activity: insufficient privileges"
**Root Cause**: The operator's access group doesn't have permission to execute the called activity.
**Fix**: Check access group roles and activity security settings.

## Transition / Flow Control Issues

### Activity completes but flow doesn't advance
**Root Cause**: The activity's exit status doesn't match what the flow connector expects.
**Fix**:
1. Check the activity's exit status (Pass/Fail)
2. Verify the flow connector's condition matches the activity's output
3. Check if the activity sets pyStatusValue correctly

### Activity executes wrong branch
**Root Cause**: Step transition conditions (Jump, Exit) evaluate incorrectly.
**Fix**:
1. Use Tracer to see which transition fires at each step
2. Check When rule conditions used in transitions
3. Verify property values used in jump conditions
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # DATA PAGES — Loading, caching, and common errors
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/datapages/data-page-overview.html",
        "title": "Data Pages — Loading, Caching, and Troubleshooting",
        "content": """# Data Pages — Troubleshooting Guide

## Overview
Data pages (D_ pages) are the primary mechanism for loading data in Pega. They support multiple data sources (activity, connector, report definition, data transform) and have configurable scope and caching.

## Common Errors

### "Data page failed to load"
**Root Cause**: The data source (activity, connector, report) failed during execution.
**Diagnosis**:
1. Check the data page's source — Activity, Report Definition, Connector, or Data Transform
2. Enable Tracer and trigger the data page load
3. Look for errors in the source execution
4. Check pyStatusValue on the data page after load attempt

**Common causes**:
- Source activity failed (see Activity Errors)
- REST connector returned error (see Connector Errors)
- Report Definition has SQL errors
- Required parameters not passed to the data page

### "Data page returns empty results"
**Root Cause**: The data source query/call returned no data.
**Fix**:
1. Test the source activity/connector/report independently
2. Check parameter values passed to the data page
3. Verify the data exists in the source system
4. Check access controls that may filter results
5. For Report Definition sources — run the report standalone

### "Stale data on data page"
**Root Cause**: Cached data page is not refreshing when expected.
**Fix**:
1. Check the data page's cache settings (Reload Once, Reload if older than, etc.)
2. Check the scope (Thread, Requestor, Node) — node-scoped pages persist across sessions
3. Force refresh: use D_PageName.pxRefresh in activity or data transform
4. For requestor-scoped pages — they persist until the session ends or MaxAge expires
5. Consider using "Reload if older than" with an appropriate interval

### "Data page causing performance issues"
**Root Cause**: Data page loads too much data or loads too frequently.
**Fix**:
1. Add parameters to filter data at the source level
2. Use appropriate scope — don't use Thread scope for data that rarely changes
3. Set MaxAge/cache duration to reduce reloads
4. Limit results in the source (MaxRecords for Obj-List, TOP for reports)
5. Use "Load management" settings to debounce concurrent requests

### "Circular reference in data page"
**Root Cause**: Data page A's source references data page B, which references data page A.
**Fix**:
1. Map the data page dependency chain
2. Break the cycle by loading one page via activity with direct database access
3. Use clipboard pages (non-data pages) as intermediaries

## Data Page Scope Guide

| Scope | Lifetime | Shared? | Use For |
|-------|----------|---------|---------|
| Thread | Single interaction | No | Transient data, form-specific lookups |
| Requestor | User session | No | User-specific preferences, session data |
| Node | JVM lifetime | All users on node | Reference data, code tables, config |

## Data Page Parameters
- Parameters filter data at load time
- If parameters change, the data page reloads automatically (for "Reload when inputs change")
- Parameters must be declared on the data page rule
- Access via D_PageName[Param1:value1,Param2:value2]

## Best Practices
- Always set appropriate scope — default Thread is often too narrow
- Set cache expiration for reference data
- Use parameters to filter data at source, not after loading
- Monitor data page sizes — large node-scoped pages consume JVM memory on all nodes
- Use "Load management > Limit concurrent loads" for expensive data sources
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # CLIPBOARD — Memory, page management, and debugging
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/clipboard/clipboard-overview.html",
        "title": "Clipboard — Memory Management and Debugging",
        "content": """# Clipboard — Memory Management and Debugging

## Overview
The clipboard is the in-memory workspace for each requestor session. It holds pages (data objects) that rules operate on. Understanding the clipboard is essential for debugging data flow issues.

## Common Clipboard Issues

### "OutOfMemoryError" / High clipboard memory
**Root Cause**: Too many or too large pages on the clipboard.
**Diagnosis**:
1. Use SysAdmin > Clipboard Viewer to inspect pages
2. Look for large page lists (hundreds/thousands of entries)
3. Check for pages that should have been removed

**Fix**:
1. Add Page-Remove calls after processing temporary pages
2. Use Page-Remove in finally blocks of activities
3. Limit Obj-List results with MaxRecords
4. Use Obj-Browse instead of Obj-List for read-only scenarios
5. Reduce Queue Processor thread count to lower concurrent memory
6. Check for data page leaks — node-scoped data pages with too much data

### "Property not found on page"
**Root Cause**: Referencing a property that doesn't exist on the clipboard page.
**Fix**:
1. Check the page's class — the property must be defined on that class or a parent class
2. Verify the page exists (Page-Exists step or @if check)
3. Check for typos in property references (case-sensitive)
4. Use the Clipboard Viewer to inspect the actual page contents
5. Check if the property is populated — it may exist but be empty

### "Page already exists" conflict
**Root Cause**: Attempting to create a page with a name that already exists on the clipboard.
**Fix**:
1. Use Page-Remove before creating the new page
2. Use a unique page name
3. Check if a data page or flow already created a page with that name

### Clipboard page has wrong class
**Root Cause**: Page was created with one class but is being used as another.
**Fix**:
1. Check what created the page (Obj-Open, Page-New, Data Transform)
2. Verify the class parameter in the creating step
3. Use Clipboard Viewer to check the page's actual pxObjClass

## Debugging with Clipboard Viewer
1. Open Dev Studio > Tools > Clipboard
2. Select the requestor to inspect
3. Browse the page tree
4. Check property values, page classes, and embedded pages
5. Look for unexpectedly large pages or page lists
6. Use "Show page XML" for a complete dump

## Clipboard Property References
- `.PropertyName` — property on the current page (Step Page context)
- `PageName.PropertyName` — property on a named top-level page
- `.PageList(1).PropertyName` — first item in a page list
- `.PageGroup(Key).PropertyName` — keyed page group entry
- `D_DataPage.PropertyName` — property on a data page

## Best Practices
- Always clean up temporary pages with Page-Remove
- Use meaningful page names for debugging clarity
- Monitor clipboard size in production via SMA
- Avoid storing large datasets on the clipboard — use pagination
- Use Declare Pages for frequently accessed reference data
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # WHEN RULES — Conditions and debugging
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/whenrules/when-rule-overview.html",
        "title": "When Rules — Conditions, Logic, and Debugging",
        "content": """# When Rules — Troubleshooting Guide

## Overview
When rules evaluate boolean conditions used throughout Pega — in flow connectors, activity transitions, visibility conditions, validation rules, and access controls. They can be simple (property comparisons) or complex (expression-based).

## Common When Rule Errors

### "When rule evaluates incorrectly"
**Root Cause**: The condition logic doesn't match the expected behavior.
**Diagnosis**:
1. Enable Tracer > When Rule events
2. Check which When rules fire and their true/false results
3. Verify the property values at evaluation time

**Fix**:
1. Check the When rule's logic — AND vs OR conditions
2. Verify property references point to the correct page context
3. Check for null/empty property handling — empty strings, zero vs null
4. Test the When rule independently using the rule form's "Run" button
5. Check for circumstance-qualified When rules that might override

### "When rule not found / rule resolution failure"
**Root Cause**: The When rule can't be resolved from the current context.
**Fix**:
1. Verify the When rule's class matches the calling context
2. Check ruleset availability in the application
3. Verify the rule name is correct (case-sensitive)

### "When rule causes performance issues"
**Root Cause**: When rules that execute expensive logic (database queries, complex expressions).
**Fix**:
1. Avoid using Obj-List or database calls inside When rules
2. Cache When rule results when possible
3. Simplify complex conditions — break into multiple smaller When rules
4. Profile with Tracer to find slow When rule evaluations

### "When rule on visibility causes UI flickering"
**Root Cause**: When rule re-evaluates on every UI refresh.
**Fix**:
1. Use client-side When rules for simple conditions
2. Minimize server-side When rules on frequently refreshed sections
3. Cache the condition result in a property

## When Rule Types
- **Simple**: Direct property comparisons (equals, greater than, etc.)
- **Expression**: Uses Pega expression language for complex logic
- **Activity-based**: Calls an activity to determine the result (avoid for performance)

## Best Practices
- Keep When rules simple — complex logic belongs in activities or decision tables
- Use meaningful rule names that describe the condition
- Test When rules independently before using in flows
- Avoid database operations inside When rules
- Use client-side When rules for UI visibility where possible
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # DATA TRANSFORMS — Mapping, errors, and debugging
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/datatransforms/data-transform-overview.html",
        "title": "Data Transforms — Configuration and Troubleshooting",
        "content": """# Data Transforms — Troubleshooting Guide

## Overview
Data Transforms are declarative rules for setting, copying, and manipulating property values on clipboard pages. They are the recommended replacement for activity-based data manipulation.

## Common Errors

### "Target property not set / remains empty"
**Root Cause**: The source value is empty, or the data transform step is not executing.
**Fix**:
1. Enable Tracer > Data Transform events
2. Check each step's source and target
3. Verify the source page/property exists and has a value
4. Check if the step has a When condition that's evaluating to false
5. Verify page context — the Data Transform's primary page must be set

### "Type mismatch in Data Transform"
**Root Cause**: Source property type doesn't match target property type.
**Fix**:
1. Check property types on both sides (String vs Integer vs DateTime)
2. Use @convertType or explicit conversion functions
3. For Date/DateTime: ensure format matches

### "Data Transform not executing"
**Root Cause**: The Data Transform isn't being called or is being skipped.
**Fix**:
1. Verify the DT is referenced in the correct flow action / case type
2. Check the DT's class (applies-to) matches the calling context
3. Verify ruleset availability
4. Check for circumstanced DTs that might take priority

### "Append to list adds empty rows"
**Root Cause**: Using Append without verifying source data exists.
**Fix**:
1. Add a When condition to check source isn't empty before appending
2. Use "Update" mode instead of "Append" if modifying existing rows
3. Check the source list isn't empty before iterating

### "Data Transform causes slow performance"
**Root Cause**: DT operates on large page lists or calls expensive sub-DTs.
**Fix**:
1. Limit iteration over large page lists
2. Avoid calling activities from within DTs
3. Use "For Each Embedded Page" efficiently — minimize steps inside loops
4. Profile with Tracer to identify slow steps

## Data Transform Actions
- **Set**: Assign a value to a property
- **Append**: Add a row to a page list
- **Update**: Modify properties on existing pages
- **Remove**: Remove a property, page, or page list row
- **Apply DT**: Call another Data Transform
- **For Each**: Iterate over a page list

## Debugging Data Transforms
1. Enable Tracer > Data Transform + Property Set events
2. Run the flow/activity that triggers the DT
3. Watch each property value as it's set
4. Check source values — empty sources produce empty targets
5. Use Clipboard Viewer to verify the page state before/after DT

## Best Practices
- Use Data Transforms instead of activities for data manipulation (Guardrails)
- Keep DTs focused — one DT per logical purpose
- Use When conditions to skip unnecessary steps
- Avoid circular DT calls (DT_A calls DT_B calls DT_A)
- Test DTs independently using the "Run" button on the rule form
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # FLOW ERRORS — Processing, connectors, routing
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/flows/flow-errors.html",
        "title": "Flow Errors — Processing, Routing, and Troubleshooting",
        "content": """# Flow Errors — Troubleshooting Guide

## Common Flow Errors

### "Flow cannot advance past assignment"
**Root Cause**: The flow action completed but no connector from the assignment evaluates to true.
**Fix**:
1. Check connector conditions — use Tracer to see evaluations
2. Add an "Otherwise" connector as a fallback
3. Verify the flow action sets the correct properties for connector evaluation
4. Check if pyStatusValue or other decision properties are set correctly

### "Flow stuck in infinite loop"
**Root Cause**: Flow connectors create a cycle that never exits.
**Fix**:
1. Map the flow visually — look for circular paths
2. Check decision shape conditions — ensure at least one path exits the loop
3. Add a counter property to force exit after N iterations
4. Use Tracer to see the repeated flow path

### "Assignment not created / not visible"
**Root Cause**: The flow advanced past the assignment shape without creating a worklist item.
**Fix**:
1. Check the assignment shape's routing — is it routed to the correct operator/workgroup?
2. Verify the operator has the required access role
3. Check the work queue configuration
4. Look at the assignment table: SELECT * FROM pc_assign_worklist WHERE pxRefObjectKey = 'KEY'
5. Check if the assignment was created but immediately completed by an auto-advance rule

### "Case creation failed"
**Root Cause**: The case type or flow cannot start.
**Fix**:
1. Check the case type's Create stage configuration
2. Verify the operator has permission to create cases of this type
3. Check for required properties that aren't provided
4. Look at PegaRULES log for class or rule resolution errors

### "Sub-case / spin-off not created"
**Root Cause**: The sub-case creation step failed silently.
**Fix**:
1. Check the sub-case type's class and flow configuration
2. Verify the parent case is in the correct stage/step for sub-case creation
3. Check property propagation — required properties on the sub-case may be missing
4. Look at the flow's sub-case shape configuration

### "Parallel flow shapes not synchronizing"
**Root Cause**: Split-Join shapes wait for all branches; if one branch is stuck, the join never fires.
**Fix**:
1. Check each parallel branch for stuck assignments or errors
2. Use Tracer to see which branches completed and which are pending
3. Add timeouts to parallel branches
4. Check for locking conflicts between parallel branches modifying the same case

## Flow Debugging Steps
1. Open the case > Actions > Flow History to see the execution path
2. Enable Tracer > Flow Processing events
3. Check each shape's entry/exit
4. Verify connector conditions at decision shapes
5. Check assignment routing and operator workbaskets

## Best Practices
- Always add an "Otherwise" connector to decision shapes
- Use flow-level exception handlers for production case types
- Keep flows simple — complex logic belongs in activities or decision tables
- Test flows with different user scenarios (permissions, data states)
- Monitor stuck cases with reports on assignment age
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # VALIDATION — Rules, errors, and UI messages
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/validation/validation-overview.html",
        "title": "Validation Rules — Errors and Troubleshooting",
        "content": """# Validation Rules — Troubleshooting Guide

## Overview
Validate rules check data integrity before processing. They run on flow action submit, on save, or when explicitly called.

## Common Validation Errors

### "Validation fails but error message not displayed"
**Root Cause**: The validation runs but the UI doesn't show the error.
**Fix**:
1. Check that the validation rule is configured on the flow action
2. Verify pyMessageLabel or pyMessage is set in the validate rule
3. Check the UI section — it must include error display components
4. Ensure the validation runs client-side if immediate feedback is needed

### "Validation passes when it should fail"
**Root Cause**: The validation condition is incorrect or not running.
**Fix**:
1. Test the validate rule independently
2. Check the condition logic — AND vs OR, null handling
3. Verify the validate rule is attached to the correct flow action
4. Check for circumstanced validate rules that might override

### "Validation blocks submission unexpectedly"
**Root Cause**: An unintended validation condition is evaluating to true.
**Fix**:
1. Enable Tracer to see all validation evaluations
2. Check property values at validation time
3. Look for inherited validation rules from parent classes
4. Check for Declare Constraints that may add validation

### "Custom validation message not appearing"
**Root Cause**: The message property is not set or the UI component doesn't display it.
**Fix**:
1. Set pyMessageLabel in the validate rule (not just pyMessage)
2. Verify the section includes the pxValidationMessage display
3. Check the message's localization configuration

## Validation Types
- **Edit Validate**: Runs on property change (client-side)
- **Flow Action Validate**: Runs on submit (server-side)
- **Obj-Validate**: Called explicitly in activities
- **Declare Constraint**: Declarative validation rule

## Best Practices
- Use client-side validation for immediate feedback
- Use server-side validation for security-critical checks
- Provide clear, actionable error messages
- Test validation with boundary values (empty, null, max length)
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # IMPORT / EXPORT — RAP, Product rules, migration errors
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/import-export/import-export-overview.html",
        "title": "Import/Export and Migration — Troubleshooting",
        "content": """# Import/Export and Migration Troubleshooting

## Common Import Errors

### "Import failed: rule already exists"
**Root Cause**: The target system already has a rule with the same key.
**Fix**:
1. Use "Import with overwrite" if you want to replace existing rules
2. Check if the rule was already promoted by another developer
3. Verify the ruleset version matches between source and target

### "Import failed: class not found"
**Root Cause**: The target system doesn't have the class definition.
**Fix**:
1. Import the class and its parent classes first
2. Check the import order — classes before instances
3. Verify the application stack includes the required rulesets

### "Import failed: foreign key violation"
**Root Cause**: The rule references another rule that doesn't exist in the target.
**Fix**:
1. Import dependent rules first (classes, properties, data types)
2. Use Product rules or RAP files that include all dependencies
3. Check the import log for specific missing references

### "Product rule / RAP deployment failed"
**Root Cause**: Product rule packaging or deployment error.
**Fix**:
1. Check the product rule includes all required rulesets
2. Verify no locked rules conflict with the import
3. Check the deployment log for specific error messages
4. Ensure the target application has the required access

### "Schema mismatch after migration"
**Root Cause**: Database schema on target doesn't match the imported rules.
**Fix**:
1. Run DDL generation to compare schemas
2. Apply ALTER TABLE statements for missing columns
3. Run Column Populator after import
4. Check the Database Table records match between environments

## Best Practices
- Use Product rules for controlled deployments
- Always export and test in a staging environment first
- Include all dependencies in your export package
- Document the import order for complex deployments
- Run smoke tests after import to verify rule resolution
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # DECISION TABLES & DECISION TREES — Logic errors
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/decisions/decision-table-overview.html",
        "title": "Decision Tables and Decision Trees — Troubleshooting",
        "content": """# Decision Tables & Decision Trees — Troubleshooting

## Common Issues

### "Decision table returns wrong result"
**Root Cause**: Row evaluation order or condition logic is incorrect.
**Fix**:
1. Decision tables evaluate top-to-bottom, first match wins
2. Check the order of rows — more specific conditions should be first
3. Verify the "Otherwise" row is at the bottom
4. Test with specific input values using the rule form's test feature
5. Check for empty/null handling — does the table handle missing values?

### "Decision table returns no result"
**Root Cause**: No row matches the input and there's no "Otherwise" row.
**Fix**:
1. Add an "Otherwise" row as a catch-all
2. Check if the input property values match any row
3. Verify property types — "5" (string) does not equal 5 (integer)
4. Check for null/empty input values

### "Decision tree evaluation is slow"
**Root Cause**: Tree is too deep or has expensive conditions.
**Fix**:
1. Keep decision trees shallow (max 3-4 levels)
2. Put most frequently matched conditions first
3. Avoid database queries in decision tree conditions
4. Consider converting deep trees to decision tables

## Decision Table vs Decision Tree

| Feature | Decision Table | Decision Tree |
|---------|---------------|---------------|
| Structure | Flat rows | Hierarchical branches |
| Best for | Multiple conditions, lookup | Sequential evaluation |
| Performance | O(n) rows | O(depth) |
| Readability | Easy for simple logic | Better for complex branching |

## Best Practices
- Always include an "Otherwise" / default result
- Test with edge cases (null, empty, boundary values)
- Document the business logic behind each row/branch
- Use allowed values to constrain input ranges
- Keep it simple — complex decision logic should use a strategy
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # CORRESPONDENCE & EMAIL — Template and delivery errors
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/correspondence/correspondence-overview.html",
        "title": "Correspondence and Email — Troubleshooting",
        "content": """# Correspondence and Email Troubleshooting

## Common Issues

### "Email not sent / correspondence not delivered"
**Root Cause**: SMTP configuration issue or email listener not running.
**Fix**:
1. Check SysAdmin > Email Accounts for SMTP configuration
2. Verify the SMTP server is reachable from the Pega server
3. Check the email listener agent is running
4. Look at PegaRULES log for SMTP connection errors
5. Test SMTP connectivity: telnet smtp-server 587

### "Email sent but not received"
**Root Cause**: Email delivered to SMTP but blocked downstream.
**Fix**:
1. Check spam/junk folders
2. Verify the recipient email address is correct
3. Check the from address — DKIM/SPF records may reject it
4. Review SMTP server logs for delivery status
5. Check if the email is queued in Pega's outbound email queue

### "Correspondence template shows wrong data"
**Root Cause**: Property references in the template resolve to wrong page or empty values.
**Fix**:
1. Check the correspondence rule's primary page
2. Verify property references use correct page context
3. Test the correspondence in preview mode
4. Check for HTML rendering issues — use the correspondence preview

### "Attachment not included in email"
**Root Cause**: Attachment reference is incorrect or file doesn't exist.
**Fix**:
1. Verify the attachment is linked to the case (pxAttachStream)
2. Check the correspondence rule's attachment configuration
3. Verify file size limits — SMTP servers often limit attachment size
4. Check for special characters in file names

## Best Practices
- Test correspondence in non-production with safe email addresses
- Use email templates for consistent branding
- Configure email bounce handling
- Monitor the outbound email queue for stuck items
- Use BCC for audit trails where required
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # COMMON PEGA ERRORS — Quick reference
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/errors/common-error-messages.html",
        "title": "Common Pega Error Messages — Quick Reference",
        "content": """# Common Pega Error Messages — Quick Reference

## Database Errors

### "You cannot save a page that your session does not hold a lock on"
**Cause**: Obj-Save called without prior Obj-Open(Lock=True) on a lockable class.
**Fix**: Add Lock=True to Obj-Open. Use ReleaseOnCommit=True.

### "Attempt to save an object that has been modified by another session"
**Cause**: Optimistic locking conflict — another session modified the object.
**Fix**: Use Obj-Refresh-And-Lock, implement retry logic.

### "Deadlock detected"
**Cause**: Two sessions waiting for each other's locks.
**Fix**: Consistent lock ordering, reduce lock duration, add retry with backoff.

### "Object not found"
**Cause**: pzInsKey doesn't match any database row.
**Fix**: Verify the key format, check the correct environment/table.

### "Column not found" / "Property not mapped"
**Cause**: Property used in query but not mapped to a database column.
**Fix**: Run Column Populator, add column mapping.

## Rule Resolution Errors

### "Rule not found" / "No rule was found"
**Cause**: Rule can't be resolved from current application context.
**Fix**: Check applies-to class, ruleset availability, circumstance qualifications.

### "Multiple rules found, ambiguous resolution"
**Cause**: Multiple rules match with the same specificity.
**Fix**: Use circumstancing to differentiate, check ruleset priorities.

## Clipboard Errors

### "Page not found"
**Cause**: Referenced clipboard page doesn't exist.
**Fix**: Create the page before referencing (Obj-Open, Page-New, Data Transform).

### "Property not found on page"
**Cause**: Property doesn't exist on the page's class.
**Fix**: Check class definition, verify property name spelling.

### "Type mismatch"
**Cause**: Operation expects one type but gets another.
**Fix**: Check property types, use conversion functions.

## Connector Errors

### "Connection timed out"
**Cause**: External service didn't respond within timeout period.
**Fix**: Increase timeout, check network connectivity, verify endpoint URL.

### "SSL handshake failed"
**Cause**: Certificate trust issue.
**Fix**: Import certificate into keystore, check TLS version compatibility.

### "HTTP 401 Unauthorized"
**Cause**: Authentication credentials invalid or missing.
**Fix**: Check auth profile, verify credentials, check token expiry.

### "HTTP 403 Forbidden"
**Cause**: Authenticated but not authorized.
**Fix**: Check API permissions, IP whitelisting, OAuth scopes.

## UI Errors

### "Section not found"
**Cause**: Referenced section rule can't be resolved.
**Fix**: Check section name, class, and ruleset availability.

### "Harness not rendering"
**Cause**: Harness or section has configuration errors.
**Fix**: Check Dev Studio for errors, validate section references.

### "Client-side script error"
**Cause**: JavaScript error in custom client-side logic.
**Fix**: Check browser console (F12), fix JavaScript errors.

## Performance Warnings

### "Guardrails violation: Large clipboard"
**Cause**: Clipboard memory exceeds recommended limits.
**Fix**: Use Page-Remove, limit Obj-List results, use pagination.

### "Long-running activity detected"
**Cause**: Activity execution exceeds expected duration.
**Fix**: Profile with Tracer, optimize database queries, consider async processing.
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # PEGA LOG FILES — Where to look for errors
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/logging/pega-log-files.html",
        "title": "Pega Log Files — Where to Find Error Details",
        "content": """# Pega Log Files — Debugging Guide

## Key Log Files

### PegaRULES.log (most important)
**Location**: {PegaInstallDir}/logs/PegaRULES.log
**Contains**: Application errors, rule execution failures, database errors, connector failures.
**When to check**: Any server-side error that isn't visible in Tracer.

### Alert.log
**Location**: {PegaInstallDir}/logs/Alert.log
**Contains**: Performance alerts — slow rules, long database queries, memory warnings.
**When to check**: Performance issues, slow processing, timeout errors.

### PegaALERT log entries
**Key alerts**:
- PEGA0001: Long-running interaction (>X seconds)
- PEGA0002: Long-running activity
- PEGA0003: Large clipboard page
- PEGA0004: Long-running SQL query
- PEGA0005: Rule assembly took too long
- PEGA0026: Too many interactions

### SecurityEvent.log
**Location**: {PegaInstallDir}/logs/SecurityEvent.log
**Contains**: Authentication failures, access denials, security violations.
**When to check**: Login issues, access control problems.

## How to Read PegaRULES.log
1. Search for ERROR or WARN level entries
2. Look for the timestamp matching your issue
3. Check the thread name to correlate with your requestor
4. Read the stack trace for the root cause
5. Look for "Caused by:" lines which show the original exception

## Setting Log Levels
1. SysAdmin > Logging > Set Logging Levels
2. Set specific categories to DEBUG for detailed output:
   - com.pega.pegarules.integration (connector debugging)
   - com.pega.pegarules.session.security (auth debugging)
   - com.pega.pegarules.data (database debugging)
3. Remember to reset to WARN/ERROR after debugging (DEBUG is verbose)

## Best Practices
- Check PegaRULES.log FIRST for any server-side error
- Use Alert.log for performance investigations
- Set targeted log levels — don't set everything to DEBUG
- Rotate logs to prevent disk space issues
- Use Log-Message in activities to add custom log entries for debugging
"""
    },
]


def seed_knowledge_base_phase2(output_dir: Path = RAW_DOCS_DIR) -> int:
    """Write Phase 2 curated docs to the raw_docs directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE2:
        doc["content_length"] = len(doc["content"])
        filename = f"curated_p2_{count:03d}.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        logger.info(f"  Saved: {doc['title'][:60]} ({doc['content_length']} chars)")
        count += 1
    logger.info(f"\nSeeded {count} Phase 2 documents to {output_dir}")
    return count


if __name__ == "__main__":
    count = seed_knowledge_base_phase2()
    print(f"\nDone! {count} Phase 2 documents written.")
    print("Now run: python -m indexer.index_docs")
