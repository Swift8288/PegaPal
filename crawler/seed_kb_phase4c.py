"""
Curated Pega Knowledge Base — Phase 4C
Covers: Deferred Save, Savable Data Pages, Optimistic Locking,
        Clipboard Management, Flow Actions, Case Dependency

Run: python -m crawler.seed_kb_phase4c
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE4C = [
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/casemanagement/deferred-save.html",
        "title": "Deferred Save — Configuration, Behavior, and Troubleshooting",
        "content": """# Deferred Save — Configuration, Behavior, and Troubleshooting

## What is Deferred Save?
Deferred Save delays committing case data to the database until a specific point in the flow, instead of saving after every assignment/step. This is useful for multi-step forms where you want the user to complete several screens before persisting anything.

## How Deferred Save Works
1. Case starts in "deferred save" mode (configured on the case type or flow)
2. User fills out multiple screens/assignments — data is held on the clipboard only (NOT in the database)
3. At a designated "save point" (typically end of a stage or explicit save step), all accumulated changes are committed to the database in one transaction
4. If the user abandons the process before the save point, NO data is persisted

## When to Use Deferred Save
- Multi-step data entry wizards (application forms, onboarding)
- When you don't want partial/incomplete records in the database
- When you need all-or-nothing transactions across multiple screens
- Customer-facing portals where users may abandon mid-process

## Configuration
- **Case Type level**: Case Designer → Settings → "Defer save until the end of the stage"
- **Flow level**: Flow rule → Properties → "Enable deferred save"
- **Stage level**: Stage configuration → "Commit data at end of stage"
- **Explicit save step**: Add a "Save" step or Obj-Save in the flow

## Common Deferred Save Issues

### 1. Data Lost When User Navigates Away
**Symptoms**: User fills out forms, navigates to another case or portal page, comes back — all data is gone
**Root Cause**: Deferred save holds data only on the clipboard. If the user navigates away, the requestor's clipboard may be cleared, losing all unsaved data.

**Fix**:
1. Warn users before navigation (add "unsaved changes" prompt)
2. Add intermediate save points at key stages (e.g., after each major section)
3. Consider using "Save as draft" pattern — persist partial data with a draft status
4. Configure requestor timeout to be long enough for the expected data entry time
5. Use `pyTemporaryObject` flag to save partial data without triggering validations

### 2. Deferred Save Not Working — Data Saves Immediately
**Symptoms**: Data is committed to database after every screen, despite deferred save being configured
**Root Causes**:
- An Activity in the flow explicitly calls Obj-Save or Commit
- A Declare OnChange rule triggers a save on property change
- A connector or integration step performs a commit
- Flow action post-processing includes a save
- Data Transform calls Obj-Save-Cancel or Commit

**Debug Steps**:
1. Use Tracer → watch for Obj-Save and Commit operations between screens
2. Check flow actions → Post Processing tab → any save activity?
3. Search for Declare OnChange rules on the case class
4. Check all activities called within the flow for Obj-Save/Commit steps

### 3. Validation Errors at Save Point
**Symptoms**: All screens filled correctly, but save point throws multiple validation errors
**Root Causes**:
- Validations deferred to save point fire on ALL data at once
- Conditional validations fail because data was entered in a different order
- Required fields from earlier screens are empty (user skipped back and didn't fill them)
- Cross-field validations fail with data from multiple screens

**Fix**:
1. Implement screen-level validation (validate each screen before allowing next)
2. Don't defer ALL validation — validate critical fields per screen
3. Show clear error messages that indicate which screen/field needs correction
4. Allow users to navigate back to the problematic screen from the error

### 4. Concurrent Access Issues with Deferred Save
**Symptoms**: Two users editing the same case — one user's changes lost
**Root Causes**:
- Deferred save doesn't lock the case during editing (no database lock held)
- Second user starts editing while first user is in deferred save mode
- First user saves → second user saves → overwrites first user's changes

**Fix**:
1. Implement optimistic locking (check version/timestamp at save time)
2. Use pessimistic locking if concurrent editing is expected
3. Show a warning if the case was modified since the user started editing
4. Consider a "check out" pattern for long editing sessions

### 5. Deferred Save and Sub-Cases
**Symptoms**: Parent case in deferred save mode, sub-case creation fails or saves immediately
**Root Causes**:
- Sub-case creation triggers a database commit (sub-case needs a case ID from the database)
- Parent's deferred data gets committed as a side effect of sub-case creation
- Propagation from parent to child fails because parent data isn't persisted yet

**Fix**:
1. Create sub-cases AFTER the parent's save point, not during deferred save
2. If sub-case must be created during deferred save: accept that a partial commit occurs
3. Use temporary IDs for sub-case references until parent is saved
4. Redesign flow to separate sub-case creation from the deferred save segment

### 6. Performance Impact of Deferred Save
**Symptoms**: Save point takes very long, especially with large data volumes
**Root Causes**:
- All accumulated data being saved in one large transaction
- Many Declare Expressions/OnChange triggers firing at commit time
- Database contention when locking multiple rows simultaneously

**Fix**:
1. Add intermediate save points for very long processes (break into chunks)
2. Optimize Declare rules that fire on save
3. Reduce the amount of data accumulated before save (pagination, chunking)
4. Monitor database transaction logs for the commit duration

## Deferred Save vs Immediate Save
| Aspect | Deferred Save | Immediate Save (Default) |
|--------|--------------|--------------------------|
| Data persistence | At designated save point only | After every assignment |
| User abandonment | No partial data in DB | Partial data exists |
| Performance | One large commit | Many small commits |
| Concurrency | No DB lock during editing | Lock acquired per save |
| Sub-cases | Complex — needs planning | Works naturally |
| Validation | Can defer or per-screen | Per screen (default) |

## Best Practices
1. Use deferred save for customer-facing data entry wizards
2. Always implement "save as draft" for long forms
3. Add screen-level validation even with deferred save — don't wait until the end
4. Warn users about unsaved changes before navigation
5. Test the full deferred save flow including abandonment scenarios
6. Plan sub-case creation carefully around save points
7. Monitor save point performance with PAL
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/data/savable-data-pages.html",
        "title": "Savable Data Pages — Write-Back Pattern and Troubleshooting",
        "content": """# Savable Data Pages — Write-Back Pattern and Troubleshooting

## Overview
Savable Data Pages allow data pages to write data BACK to their source (database, connector, etc.) in addition to reading. This is the "write-back" pattern — edit data on a data page, then call Save on the data page to persist changes.

## How It Works
1. Data page loads data from source (database, connector, activity)
2. User or logic modifies properties on the data page
3. Application calls "Save Data Page" (explicitly or via flow step)
4. Data page's configured "Save" source writes changes back to the database/service
5. Data page cache is updated with the saved values

## Configuration
- Data Page rule → Source tab → enable "Save" section
- Configure a save activity, connector, or data transform for the write-back
- Set "Savable" checkbox on the data page

## Common Savable Data Page Issues

### 1. "Data page is not savable" Error
**Symptoms**: Error when trying to save a data page
**Root Causes**:
- Data page not marked as savable in the rule
- No save source configured (save activity/connector missing)
- Trying to save a system/OOTB data page that isn't designed to be saved

**Fix**:
1. Open data page rule → check "Savable" checkbox
2. Configure Save Source tab with appropriate activity/connector
3. For OOTB data pages: create a custom savable data page instead of modifying OOTB

### 2. Save Succeeds But Data Doesn't Persist
**Symptoms**: No error on save, but data reverts on reload
**Root Causes**:
- Save source (activity/connector) doesn't actually write to database
- Save commits to a different database/table than expected
- Transaction rolled back after the save due to subsequent error
- Cache returns old data after save (reload needed)

**Fix**:
1. Test the save source independently
2. Check database directly — did the row update?
3. After save: force reload the data page to verify
4. Check if a later step causes a transaction rollback

### 3. Concurrent Save Conflicts
**Symptoms**: "Optimistic lock failure" or data overwritten by another user
**Root Causes**:
- Multiple users editing the same data page concurrently
- No version/timestamp checking on save

**Fix**:
1. Implement optimistic locking using a version column
2. Check version before save — if changed, refresh and let user retry
3. For critical data: use pessimistic locking (database lock)

### 4. Partial Save on Page List Data Pages
**Symptoms**: Some rows saved, others not; or all rows saved when only one changed
**Root Causes**:
- Save source doesn't handle page list correctly (saves all vs. only changed)
- No dirty-tracking to identify which rows changed
- Error on one row causes entire save to fail

**Fix**:
1. Implement row-level dirty tracking (pxDirtyFlag or custom flag)
2. Save source should iterate and save only changed rows
3. Add error handling per row — don't let one bad row block all saves
4. Use database transactions appropriately (all-or-nothing vs per-row)

## Best Practices
1. Always implement optimistic locking for concurrent access
2. Test save with edge cases: empty data, max-length values, special characters
3. Add validation before save — don't rely on database constraints alone
4. Log save operations for audit trail
5. Handle save failures gracefully — show user a clear error and retry option
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/flow/flow-actions-troubleshooting.html",
        "title": "Flow Actions — Configuration, Connectors, and Troubleshooting",
        "content": """# Flow Actions — Configuration, Connectors, and Troubleshooting

## Overview
Flow Actions define what happens when a user completes an assignment — they specify the UI (section), processing logic, and navigation after submission. Flow actions are the bridge between user interaction and flow progression.

## Flow Action Components
- **Section**: The UI form displayed to the user
- **Pre-Processing**: Data transforms/activities that run BEFORE the form is shown
- **Post-Processing**: Data transforms/activities that run AFTER the user submits
- **Validation**: Validate rules that check data before allowing submission
- **Connector**: Determines which flow path to follow after the action

## Common Flow Action Issues

### 1. Form Submits But Nothing Happens
**Symptoms**: User clicks Submit/button, spinner appears briefly, form stays the same
**Root Causes**:
- Validation error that's not displayed to the user (hidden validation message)
- Post-processing activity throws a silent error
- Flow action's connector condition returns false for all paths
- JavaScript error preventing form submission
- Case is locked by another session

**Debug Steps**:
1. Check browser console for JavaScript errors
2. Enable Tracer → submit the form → look for red error entries
3. Check pyValidationMessages on clipboard (might have errors not shown in UI)
4. Verify flow action connectors — does at least one path evaluate to true?
5. Check case lock status

### 2. Wrong Section/Form Displayed
**Symptoms**: User sees a different form than expected for the assignment
**Root Causes**:
- Flow action references wrong section rule
- Circumstanced flow action selecting a different variant
- Multiple flow actions on the assignment — wrong one selected
- Section is overridden in a higher ruleset

**Fix**:
1. Open the assignment → check which flow action is configured
2. Open the flow action → Section tab → verify the section name
3. Check rule resolution for the section (might be circumstanced)
4. If multiple flow actions: check the action order and selection criteria

### 3. Pre-Processing Not Running
**Symptoms**: Form appears but expected default values are missing
**Root Causes**:
- No pre-processing configured on the flow action
- Pre-processing data transform has an error
- Pre-processing runs but sets values on wrong page
- Caching — form loaded from cache without re-running pre-processing

**Fix**:
1. Check flow action → Pre-Processing tab → is a data transform/activity configured?
2. Test the data transform independently
3. Verify the target page in the data transform matches the form's page context
4. Disable form caching if pre-processing must run every time

### 4. Post-Processing Errors / Data Not Saved
**Symptoms**: Form submits, flow advances, but data changes are lost
**Root Causes**:
- Post-processing data transform maps to wrong target page
- Post-processing activity has a step that clears data
- Obj-Save not called in post-processing (for non-standard save patterns)
- Error in post-processing silently swallowed

**Fix**:
1. Check flow action → Post-Processing tab
2. Trace the post-processing execution step by step
3. Verify target page for data mappings
4. Add explicit error handling in post-processing activities

### 5. Connector Routing Issues
**Symptoms**: Flow goes to wrong step after flow action completion
**Root Causes**:
- Connector when condition evaluates unexpectedly
- Multiple connectors — wrong one is matched first (order matters!)
- Default connector not set (flow has no path to follow)
- Connector condition references a property set during post-processing (timing issue)

**Fix**:
1. Check flow shape → connectors → review each connector's when condition
2. Verify connector order — Pega evaluates in order, uses first match
3. Always have a default/else connector as fallback
4. Test connector conditions with actual runtime data values

### 6. Local Actions vs Connector Flow Actions
**Symptoms**: Action appears in the wrong place or doesn't appear at all
**Root Causes**:
- Local action configured but user expects it on the main action area
- Flow action added to flow but not added to the assignment's action set
- Action visibility controlled by when rule that evaluates to false

**Fix**:
1. Check assignment configuration — is the action in the right action set?
2. Verify when rule on the action (if any) evaluates to true for this scenario
3. Distinguish between: flow action (main Submit), local action (sidebar), case-wide action

## Flow Action Best Practices
1. Always configure validation — don't rely on post-processing to catch bad data
2. Keep post-processing simple — move complex logic to activities/data transforms
3. Always have a default connector path as fallback
4. Test all connector conditions with boundary values
5. Use pre-processing to set defaults — don't hardcode in the section
6. Log key decision points in post-processing for debugging
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/casemanagement/case-dependencies.html",
        "title": "Case Dependencies and Wait Shapes — Blocking, Spinning, and Troubleshooting",
        "content": """# Case Dependencies and Wait Shapes — Troubleshooting

## Overview
Cases often depend on other cases, external events, or timed conditions before they can proceed. Pega provides Wait shapes, Timer events, and case dependencies to handle these patterns.

## Wait Types
- **Wait for case**: Wait for a specific sub-case or related case to complete
- **Wait for timer**: Wait for a specific date/time or duration
- **Wait for condition**: Wait for a property value to meet a condition
- **Wait for external event**: Wait for an external system to send a notification

## Common Dependency Issues

### 1. Case Stuck at Wait Shape Indefinitely
**Symptoms**: Case shows "Pending" status, nothing happening
**Root Causes**:
- Waiting for a sub-case that's also stuck or was resolved to wrong status
- Timer set to a past date (should have fired immediately but didn't)
- Condition will never be true (logical error in the when condition)
- External event listener not configured or not receiving events

**Debug Steps**:
1. Open the case → Process tab → identify which Wait shape it's on
2. Check the wait condition — what is it waiting for?
3. If waiting for sub-case: check sub-case status
4. If waiting for timer: check the timer date/time value
5. If waiting for condition: check the property values on clipboard

### 2. Timer Not Firing
**Symptoms**: Wait on timer set for 2 hours ago, case still waiting
**Root Causes**:
- Timer agent not running (pyTimerAgent)
- Timer date property is empty/null
- Timezone mismatch — timer set in wrong timezone
- Agent interval is longer than expected (checks every 30 mins instead of every minute)

**Fix**:
1. Check Admin Studio → Agent Management → pyTimerAgent → is it running?
2. Verify the timer property value and timezone
3. Reduce timer agent interval for time-sensitive processes
4. Check if timer was created correctly (not pointing to a past date in wrong TZ)

### 3. Case Completes Before Dependency is Met
**Symptoms**: Case advances past the wait shape without the condition being met
**Root Causes**:
- Alternative path in the flow bypasses the wait (parallel branch)
- Wait shape has a timeout that expired, taking the timeout path
- Another user/process advanced the case manually
- Wait condition was briefly true and then changed back

**Fix**:
1. Check the flow for alternative paths around the wait
2. Review timeout configuration on the wait shape
3. Check case audit trail for who/what advanced the case
4. Add logging at the wait shape to capture the trigger

### 4. Circular Dependencies Between Cases
**Symptoms**: Case A waits for Case B, Case B waits for Case A — both stuck forever
**Root Causes**:
- Design error — cases shouldn't wait for each other
- Complex case hierarchy with unintended cross-dependencies

**Fix**:
1. Redesign the process to break the circular dependency
2. Use events/signals instead of direct case-to-case waits
3. Add a timeout on one of the waits as a circuit breaker
4. Consider using a parent case to coordinate the two cases

### 5. External Event Wait Not Receiving Events
**Symptoms**: External system sent the event but case doesn't advance
**Root Causes**:
- Event listener not configured for the correct event type
- Event key/correlation ID doesn't match
- Service rule processing the event has an error
- Event format doesn't match expected schema

**Fix**:
1. Verify the event listener configuration and event type
2. Check correlation ID — must match exactly between event and waiting case
3. Test the service rule independently with sample event data
4. Check Pega logs for event processing errors

## Best Practices
1. Always set timeouts on wait shapes — never wait indefinitely
2. Add timeout handling paths (escalation, notification, auto-resolution)
3. Log when entering and exiting wait states for troubleshooting
4. Test dependency flows end-to-end including timeout scenarios
5. Avoid circular dependencies — redesign if they appear
6. Use SLAs in addition to wait shapes for business-level tracking
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/troubleshooting/clipboard-management.html",
        "title": "Clipboard Management — Memory, Page Cleanup, and Troubleshooting",
        "content": """# Clipboard Management — Memory, Page Cleanup, and Troubleshooting

## Overview
The clipboard is Pega's in-memory data store for the current session. Every page, property, and data page lives on the clipboard. Clipboard mismanagement is a top cause of memory issues, data leaks, and performance problems.

## Clipboard Structure
- **Thread pages**: Specific to the current flow execution (pyWorkPage, pyWorkCover)
- **Requestor pages**: Survive across flows within the session (data pages in Requestor scope)
- **System pages**: Internal Pega pages (pxRequestor, pxThread)
- **Temporary pages**: Created during processing, should be cleaned up

## Common Clipboard Issues

### 1. OutOfMemoryError / Clipboard Bloat
**Symptoms**: java.lang.OutOfMemoryError, slow performance, high JVM heap usage
**Root Causes**:
- Large page lists not cleaned up (loading 100K+ records into clipboard)
- Node-scoped data pages consuming excessive memory
- Temporary pages not removed after use
- Repeating grid loading all rows instead of paginating
- Activity creating pages in a loop without cleanup

**Debug Steps**:
1. Use the Clipboard viewer (Dev Tools → Clipboard) to see all pages
2. Check page sizes — look for unexpectedly large pages
3. Monitor JVM heap usage via Admin Studio or JMX
4. Use PAL to identify operations that create large clipboard structures

**Fix**:
1. Add Page-Remove steps after temporary page usage
2. Limit data page result sets (add TOP N or LIMIT clauses)
3. Use Thread scope instead of Requestor for short-lived data
4. Implement pagination for repeating grids
5. Clean up page lists after processing loops

### 2. Data Leaking Between Cases/Sessions
**Symptoms**: Data from one case appears in another case, wrong customer data shown
**Root Causes**:
- Requestor-scoped data page shared across cases (not parameterized)
- Node-scoped data page returning cached data for wrong context
- Property set on clipboard page that persists across flow executions
- Thread page not cleaned up before starting new flow

**Fix**:
1. Use parameterized data pages (unique per case/customer)
2. Change scope from Node/Requestor to Thread if data is case-specific
3. Add Page-Remove at flow start to clear stale pages
4. Use Step Pages in flows to isolate case data
5. Never store case-specific data on Node-scoped pages

### 3. "Page already exists" Error
**Symptoms**: Error when creating a page that already exists on clipboard
**Root Causes**:
- Activity calling Page-New on a page name that's already in use
- Loop creating pages with the same name each iteration
- Previous flow execution left a page on the clipboard

**Fix**:
1. Use Page-Remove before Page-New if the page might already exist
2. Use unique page names in loops (e.g., append index)
3. Check clipboard before creating — use Page-Exists method
4. Clean up pages at flow start/end

### 4. Clipboard Data Not Available in Background Processing
**Symptoms**: Agent or queue processor can't find data that's available in interactive sessions
**Root Causes**:
- Background processing runs in its own requestor — no access to user's clipboard
- Data pages scoped to Requestor are not available in background threads
- pyWorkPage not loaded in background context — need to load explicitly

**Fix**:
1. In background activities: explicitly load the case with Obj-Open before accessing data
2. Use Thread-scoped data pages with parameters, not Requestor-scoped
3. Pass all needed data as activity parameters instead of relying on clipboard
4. Load data pages explicitly in background context

### 5. Clipboard Viewer Shows Unexpected Pages
**Symptoms**: Too many pages on clipboard, pages from previous flows still present
**Root Causes**:
- Flow didn't clean up properly on completion
- Error in flow caused early exit without cleanup
- Data pages with Requestor scope accumulating over the session

**Fix**:
1. Add cleanup steps in flow (postconditions or explicit Page-Remove)
2. Configure flow end shapes to clean up thread pages
3. For Requestor-scoped data pages: add expiration or refresh policies
4. Monitor clipboard size in PAL for long-running sessions

## Clipboard Best Practices
1. Use Thread scope by default — only use Requestor/Node when caching is needed
2. Always clean up temporary pages with Page-Remove
3. Limit data page result sets — never load unbounded data
4. Parameterize data pages that should be unique per context
5. Use Clipboard viewer regularly during development to verify data state
6. Profile clipboard size with PAL before production deployment
7. Add cleanup logic to flow error handling paths, not just the happy path
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/troubleshooting/pega-predictive-diagnostic-cloud.html",
        "title": "Pega Predictive Diagnostic Cloud (PDC) and Alert Management — Troubleshooting",
        "content": """# Pega Predictive Diagnostic Cloud (PDC) and Alert Management

## Overview
PDC (Predictive Diagnostic Cloud) is Pega's monitoring and diagnostic service that collects alerts, performance data, and health metrics from Pega environments. Alerts indicate rules or operations that exceeded performance thresholds.

## Alert Types
- **Database alert**: SQL query exceeded time threshold (default: 500ms)
- **Interaction alert**: User interaction exceeded time threshold
- **Service alert**: External service call too slow
- **Memory alert**: JVM heap usage exceeded threshold
- **Rule assembly alert**: Rule compilation took too long
- **Connect alert**: Connector call exceeded timeout

## Common Alert Issues

### 1. "Alert: Long-running query" (DB-xxx)
**Symptoms**: Alert log shows database queries exceeding 500ms threshold
**Root Causes**:
- Missing database indexes on filtered columns
- Full table scan on large tables (pc_work, pc_history, pr_data_xxx)
- Complex joins in report definitions
- Table statistics out of date (query optimizer making bad plans)
- Lock contention causing queries to wait

**Fix**:
1. Get the full SQL from the alert (ALERT log or PDC)
2. Run EXPLAIN/EXPLAIN ANALYZE on the SQL
3. Add indexes on filtered/sorted columns
4. Update table statistics: Admin Studio → Database → Update Statistics
5. Optimize the report or query generating the SQL
6. Set threshold: DSS `alerts/database/threshold` (in ms)

### 2. "Alert: Long-running interaction" (PEGA-xxx)
**Symptoms**: User-facing operations taking longer than expected
**Root Causes**:
- Slow data page loads during screen rendering
- Expensive Declare Expressions firing on page load
- Large clipboard pages being serialized
- Multiple consecutive connector calls (N+1 pattern)

**Fix**:
1. Enable PAL → reproduce the slow interaction → analyze the PAL report
2. Look for the top time consumers (data pages, rules, connectors)
3. Optimize the slowest components
4. Cache data where possible (use appropriate data page scoping)

### 3. Too Many Alerts — Alert Fatigue
**Symptoms**: Hundreds of alerts daily, hard to find real issues
**Root Causes**:
- Thresholds too low for the environment
- Known slow operations not excluded
- Batch/report operations triggering alerts (expected to be slow)

**Fix**:
1. Adjust alert thresholds to appropriate levels for your environment
2. Exclude known-slow operations from alerting
3. Categorize alerts by severity and priority
4. Set up alert rules in PDC to group and filter alerts
5. Focus on trends (increasing alert frequency) rather than individual alerts

## PDC Configuration
- **Enable**: prconfig.xml → `pdc/enabled` = true
- **PDC URL**: prconfig.xml → `pdc/url` (cloud service URL)
- **Alert thresholds**: DSS → `alerts/xxx/threshold` for each alert type
- **Alert destination**: Log file (PegaALERT.log) and/or PDC cloud

## Monitoring Best Practices
1. Set up PDC connection for all environments (Dev, QA, Prod)
2. Review alerts daily — they are early warnings of performance degradation
3. Baseline alert thresholds for each environment (prod thresholds ≠ dev thresholds)
4. Investigate new alert patterns after deployments
5. Use PAL for detailed profiling when alerts indicate performance issues
6. Track alert trends over time — increasing alerts = degrading performance
"""
    },
]


def seed_phase4c():
    """Write Phase 4C curated docs to raw_docs directory."""
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for doc in CURATED_DOCS_PHASE4C:
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
        filename = f"phase4c_{slug}.json"
        filepath = RAW_DOCS_DIR / filename

        payload = {
            "url": doc["url"],
            "title": doc["title"],
            "content": doc["content"].strip(),
        }
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE4C)}] Saved: {doc['title']}")

    logger.info(f"\nPhase 4C complete — {count} documents saved to {RAW_DOCS_DIR}")
    logger.info("Next: python -m indexer.index_docs")


if __name__ == "__main__":
    seed_phase4c()
