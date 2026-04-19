"""
Curated Pega Knowledge Base — Phase 3A
Covers: Case Management, UI/Section errors, Access Control, DevOps/Deployment

Run: python -m crawler.seed_kb_phase3a
"""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE3A = [
    # ═══════════════════════════════════════════════════════════════════
    # CASE MANAGEMENT — Lifecycle, stages, dependencies
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/casemanagement/case-lifecycle.html",
        "title": "Case Management — Lifecycle, Stages, and Troubleshooting",
        "content": """# Case Management — Lifecycle and Troubleshooting

## Overview
Cases in Pega follow a lifecycle defined by stages, processes (flows), and steps. Understanding the lifecycle is critical for debugging cases that get stuck, skip steps, or behave unexpectedly.

## Case Lifecycle Stages
- **Create**: Initial stage where the case is created and basic data is collected
- **Processing stages**: Custom stages for business logic (Review, Approve, Fulfill, etc.)
- **Resolution**: Final processing before closure
- **Closed**: Terminal stage — case is complete

## Common Case Issues

### "Case stuck at a stage / won't advance"
**Root Cause**: The stage's exit criteria aren't met, or a process within the stage is stuck.
**Diagnosis**:
1. Check the case's current stage and step: Case Designer > Lifecycle view
2. Look at open assignments — is there an assignment waiting for action?
3. Check the flow for the current process — is it stuck at a decision/activity?
4. Review the stage's entry/exit criteria
5. Check for pending SLAs that might be blocking

**Fix**:
1. If stuck at assignment: check routing, operator workbasket, access
2. If stuck at activity: debug the activity (enable Tracer)
3. If stuck at decision: check connector conditions
4. Manual override: use pyFlowAction "FinishAssignment" to push forward

### "Case created but no assignment appears"
**Root Cause**: The case flow started but the assignment step wasn't reached.
**Fix**:
1. Check the case type's Create stage — is there an assignment in the first process?
2. Check for auto-advance steps that skip past the assignment
3. Verify routing — the assignment may be routed to a workgroup/queue not visible to the user
4. Check the flow for errors before the assignment shape
5. Look at case history for any flow processing errors

### "Case skips a stage unexpectedly"
**Root Cause**: Stage transition conditions evaluate to true prematurely.
**Fix**:
1. Check stage transition conditions in the Case Designer
2. Look for auto-complete settings on stages
3. Check if a parallel process completed early and triggered the transition
4. Review When rules used in stage transitions

### "Sub-case not reflecting in parent case"
**Root Cause**: Sub-case data propagation isn't configured correctly.
**Fix**:
1. Check the sub-case shape's "Propagate data" settings
2. Verify the data transform that maps sub-case data back to parent
3. Check if the sub-case has resolved — data propagates on resolution
4. Look for class mismatches between parent and sub-case properties

### "Case data lost after stage transition"
**Root Cause**: A data transform or flow action clears/overwrites data during transition.
**Fix**:
1. Check stage entry/exit data transforms
2. Look for default data transforms that reset properties
3. Check flow actions for unintended property clearing
4. Use Tracer to track property changes during the transition

### "Case ID generation conflict / duplicate case IDs"
**Root Cause**: Custom case ID generation produces duplicates under concurrent creation.
**Fix**:
1. Check the ID generation activity or sequence rule
2. Use database sequences for uniqueness
3. Add retry logic for duplicate ID errors
4. Consider using Pega's default ID generation

## Case Dependency Issues

### "Dependent case blocking parent resolution"
**Root Cause**: Parent case has a "Wait for dependent case" step that requires sub-case resolution.
**Fix**:
1. Check if the dependent case is stuck (debug separately)
2. Check the dependency configuration — is "Wait" required or optional?
3. For optional: change to "Don't wait" if business rules allow
4. For stuck dependent: resolve manually or use admin tools

### "Circular case dependency"
**Root Cause**: Case A depends on Case B which depends on Case A.
**Fix**:
1. Review the case type hierarchy for circular references
2. Use status-based coordination instead of direct dependencies
3. Implement a coordinator pattern with a parent case managing both

## Best Practices
- Keep the case lifecycle simple — fewer stages is better
- Use stage entry/exit data transforms for data initialization and cleanup
- Implement SLAs at the stage level for business deadline tracking
- Test the full lifecycle with different user roles and data scenarios
- Monitor case aging with reports to identify stuck cases
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/casemanagement/case-status.html",
        "title": "Case Status — pyStatusWork and Status Transitions",
        "content": """# Case Status — pyStatusWork Troubleshooting

## Overview
pyStatusWork is the primary property tracking case state. It controls flow behavior, reporting, and assignment visibility. Incorrect status values cause many case processing issues.

## Common Status Values
- **New**: Case just created
- **Open**: Case is active and being worked
- **Pending-***: Waiting for something (Pending-Approval, Pending-External, etc.)
- **Resolved-***: Case resolved (Resolved-Completed, Resolved-Cancelled, etc.)

## Common Issues

### "Case status not updating after flow action"
**Root Cause**: Flow action doesn't set pyStatusWork, or a downstream step overrides it.
**Fix**:
1. Check the flow action's data transform — does it set pyStatusWork?
2. Verify no Declare Expression resets the status
3. Check the flow's post-processing for status changes
4. Use Tracer to track pyStatusWork changes through the flow

### "Cannot reopen a resolved case"
**Root Cause**: Once a case reaches a Resolved-* status, the flow typically ends.
**Fix**:
1. Configure a "Reopen" flow action on the resolved stage
2. Set pyStatusWork back to Open and restart the appropriate flow
3. Check business rules — some case types intentionally prevent reopening

### "Reporting shows wrong case counts by status"
**Root Cause**: Cases have stale or incorrect status values.
**Fix**:
1. Run a report on pyStatusWork to see actual distribution
2. Check for cases stuck in intermediate statuses
3. Verify status-setting logic in flows and data transforms
4. Clean up orphaned cases with admin activities

## Best Practices
- Always set pyStatusWork explicitly in flow actions
- Use status prefixes consistently (Pending-*, Resolved-*)
- Include status in your case reports for monitoring
- Test status transitions for all paths through the case lifecycle
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # UI / SECTION ERRORS — Rendering, dynamic layouts, repeat grids
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/ui/section-errors.html",
        "title": "UI and Section Errors — Rendering and Troubleshooting",
        "content": """# UI and Section Errors — Troubleshooting Guide

## Common Section/UI Errors

### "Section not rendering / blank screen"
**Root Cause**: Section rule has errors or can't be resolved.
**Diagnosis**:
1. Check browser console (F12) for JavaScript errors
2. Check Dev Studio for section compilation errors
3. Verify the section exists in the correct class and ruleset
4. Check for missing referenced sections or properties

**Fix**:
1. Fix any compilation errors shown in Dev Studio
2. Verify all referenced sub-sections exist
3. Check for circular section includes
4. Clear browser cache and retry
5. Check for custom JavaScript that may be breaking

### "Repeat grid shows no data / empty rows"
**Root Cause**: The data source (page list) is empty or not loaded.
**Fix**:
1. Check if the page list property has data (Clipboard Viewer)
2. Verify the data page or activity that populates the list
3. Check the repeat grid's data source configuration
4. Verify the page list property name matches exactly (case-sensitive)
5. Check access controls that may filter grid rows

### "Repeat grid shows too many rows / performance issue"
**Root Cause**: Large dataset loaded without pagination.
**Fix**:
1. Enable server-side pagination on the repeat grid
2. Limit the source data (filter in the data page or report)
3. Use lazy loading for large datasets
4. Consider a report-based grid instead of a clipboard-based one

### "Dynamic layout not showing/hiding correctly"
**Root Cause**: Visibility condition (When rule) evaluates incorrectly.
**Fix**:
1. Check the When rule associated with the layout
2. Verify property values used in the condition
3. Use client-side When rules for responsive visibility
4. Check if server-side refresh is needed (add refresh When condition)
5. Test with different data scenarios

### "Dropdown / autocomplete not loading options"
**Root Cause**: The data source for the control is failing.
**Fix**:
1. Check the data page that provides dropdown options
2. Verify the data page loads successfully (test independently)
3. Check the prompt list or local list configuration
4. Verify the display and value properties are correctly mapped
5. Check for empty data page parameters

### "Modal / popup dialog not opening"
**Root Cause**: JavaScript error or incorrect modal configuration.
**Fix**:
1. Check browser console for JavaScript errors
2. Verify the modal section exists and has no compilation errors
3. Check the action set configuration on the button/link
4. Verify the modal's thread/harness configuration

### "CSS/styling not applied correctly"
**Root Cause**: Skin rule override or CSS specificity issue.
**Fix**:
1. Check the application's skin rule for component styling
2. Use browser DevTools to inspect element styles
3. Look for custom CSS that may override standard Pega styles
4. Check for format rules applied to the control
5. Verify the skin rule hierarchy (application > parent skin)

### "Tab layout errors — tab not selectable or shows wrong content"
**Root Cause**: Tab configuration or dynamic content loading issue.
**Fix**:
1. Verify each tab panel section exists and compiles
2. Check if tabs use deferred loading — content may not load until selected
3. Verify tab visibility conditions
4. Check for duplicate tab names or conflicting configurations

## Client-Side Debugging
1. Open browser DevTools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed API calls (HTTP 4xx/5xx)
4. Use Elements tab to inspect DOM structure
5. Check Application tab for session/cookie issues

## UI Performance Optimization
- Use deferred loading for tabs and hidden sections
- Limit repeat grid page sizes (10-20 rows with pagination)
- Minimize server-side refreshes
- Use client-side validation where possible
- Reduce the number of sections per screen
- Avoid deeply nested section hierarchies
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/ui/harness-errors.html",
        "title": "Harness and Portal Errors — Configuration and Debugging",
        "content": """# Harness and Portal Errors — Troubleshooting

## Common Harness Errors

### "Harness not found" / blank work area
**Root Cause**: The harness rule can't be resolved for the case type.
**Fix**:
1. Check the harness name in the case type configuration
2. Verify the harness exists in the correct class
3. Check ruleset availability in the application
4. Look for circumstance-qualified harnesses

### "Portal not loading / infinite spinner"
**Root Cause**: Portal initialization failed due to missing rules or JavaScript errors.
**Fix**:
1. Check browser console for errors
2. Verify the portal rule configuration
3. Check if the operator has access to the portal
4. Clear browser cache and try incognito mode
5. Check the application server logs for errors

### "Work object opens in wrong harness"
**Root Cause**: Harness resolution picks a different harness than expected.
**Fix**:
1. Check the harness resolution order (circumstanced rules, class hierarchy)
2. Verify the case type's "Open Case" harness configuration
3. Check if a different portal overrides the default harness
4. Review the pyPerformHarness property

### "Action menu items missing or wrong"
**Root Cause**: Flow actions not configured or access controls blocking.
**Fix**:
1. Check the case type's flow actions configuration
2. Verify the operator has access to the flow actions
3. Check When conditions on flow action visibility
4. Verify the case is in the correct stage for the action

## Best Practices
- Test harnesses in different portals (user, manager, admin)
- Use the responsive design features for mobile compatibility
- Keep harness structure simple — delegate to sections for content
- Test with different screen sizes and browsers
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # ACCESS CONTROL — RBAC, ABAC, privileges, access rules
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/security/access-control-overview.html",
        "title": "Access Control — RBAC, ABAC, and Privilege Errors",
        "content": """# Access Control — Troubleshooting Guide

## Overview
Pega uses Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) to control who can do what. Access is determined by the operator's access group, roles, and privilege rules.

## Access Control Hierarchy
1. **Operator** → belongs to an **Access Group**
2. **Access Group** → contains **Roles** and **Application**
3. **Roles** → reference **Privileges** (Access-When, Access-Deny-When, Privilege rules)
4. **Privileges** → control specific actions (create case, view report, etc.)

## Common Access Control Errors

### "Access denied" / "You do not have permission"
**Root Cause**: The operator lacks the required role or privilege.
**Diagnosis**:
1. Check the operator's access group: SysAdmin > Operator Profile
2. Verify the access group's roles
3. Check which privilege the action requires
4. Test with an admin account to confirm it's access-related

**Fix**:
1. Add the required role to the operator's access group
2. Add the required privilege to the role
3. Check for Access-Deny-When rules that may be blocking
4. Verify the role's access-when rules are evaluating correctly

### "Can create case but can't see it afterward"
**Root Cause**: Row-level security (Access-When rules) filter the case from query results.
**Fix**:
1. Check Access-When rules on the case class
2. Verify the rule's condition includes the current operator's team/org
3. Test the Access-When rule independently
4. Check if the case's work group matches the operator's access

### "Flow action not visible / can't perform action"
**Root Cause**: The flow action has access control restrictions.
**Fix**:
1. Check the flow action's privilege configuration
2. Verify the operator's role has the required privilege
3. Check for When rules on the flow action's visibility
4. Verify the case is in the correct stage/status for the action

### "Report returns no data for non-admin users"
**Root Cause**: Row-level security filters out all rows.
**Fix**:
1. Check Access-When rules on the report's class
2. Verify the operator's work group and organization
3. Test the report's SQL with the security filter
4. Consider adding org-based filters to the report

### "Cannot access Dev Studio / Admin tools"
**Root Cause**: Operator lacks PegaRULES:SysAdm4 or similar admin roles.
**Fix**:
1. Check the operator's access group for admin roles
2. Add appropriate roles: PegaRULES:SysAdm4 for Dev Studio, PegaRULES:SysAdm5 for full admin
3. Verify the portal configuration allows Dev Studio access

### "Privilege rule not being enforced"
**Root Cause**: Privilege not attached to any role, or the role isn't in the access group.
**Fix**:
1. Verify the privilege rule exists and is named correctly
2. Check that the privilege is referenced in a role
3. Verify the role is in the operator's access group
4. Check for production-level privilege overrides

## Access-When Rules
- **Access-When**: Grants access when the condition is true
- **Access-Deny-When**: Denies access when the condition is true (overrides Access-When)
- Access-Deny-When takes priority over Access-When
- Use Tracer to see which access rules fire

## Debugging Access Issues
1. Log in as the affected user (or use the "Run as" feature)
2. Enable Tracer > Security events
3. Check which access rules fire and their results
4. Compare with an admin account to identify the blocking rule
5. Review the security event log for detailed denial reasons

## Best Practices
- Use roles for grouping permissions, not individual operator assignments
- Test access with different user profiles during development
- Document your access control model
- Use Access-Deny-When sparingly — it overrides everything
- Monitor the security log for unexpected access denials
- Regular audit of operator access groups and roles
"""
    },
    # ═══════════════════════════════════════════════════════════════════
    # DEVOPS / DEPLOYMENT — Pipeline, branching, deployment manager
    # ═══════════════════════════════════════════════════════════════════
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/devops/deployment-manager.html",
        "title": "DevOps and Deployment — Pipeline Errors and Troubleshooting",
        "content": """# DevOps and Deployment — Troubleshooting Guide

## Deployment Manager Issues

### "Deployment failed: rule conflicts"
**Root Cause**: Rules in the deployment package conflict with existing rules in the target system.
**Fix**:
1. Check the deployment log for specific conflicting rules
2. Compare ruleset versions between source and target
3. Resolve conflicts by merging or overwriting
4. Re-generate the deployment package after resolution
5. Check for locked rulesets in the target that prevent overwrite

### "Deployment failed: schema mismatch"
**Root Cause**: Database schema in target doesn't match the deployment's expected schema.
**Fix**:
1. Run DDL generation to compare schemas
2. Apply missing database changes (ALTER TABLE) before deployment
3. Run Column Populator after deployment
4. Check for custom table mappings that differ between environments

### "Pipeline stuck in pending state"
**Root Cause**: Approval gate not cleared, or pipeline automation failed.
**Fix**:
1. Check the pipeline status in Deployment Manager
2. Verify the approval gate — does someone need to approve?
3. Check for automated test failures blocking the pipeline
4. Review the pipeline log for error details
5. Check connectivity between Pega environments

### "Post-deployment: rules not working in target"
**Root Cause**: Rules deployed but not activated or cached.
**Fix**:
1. Clear the rules cache on the target system
2. Verify the ruleset version is available in the target application
3. Check the application stack includes the deployed rulesets
4. Restart the target system if cache clearing doesn't help
5. Run smoke tests to verify rule resolution

## Branch and Merge Issues

### "Branch merge conflict"
**Root Cause**: Two developers modified the same rule in different branches.
**Fix**:
1. Open the merge tool in Dev Studio
2. Compare the conflicting versions side by side
3. Choose which version to keep, or manually merge changes
4. Test the merged result before committing
5. Communicate with the other developer to align

### "Branch not showing latest changes"
**Root Cause**: Branch not refreshed from the main application.
**Fix**:
1. Update the branch from the base application
2. Check for pending merges from other branches
3. Verify the branch's base ruleset version is current

### "Cannot create branch: access denied"
**Root Cause**: Operator lacks branch creation privileges.
**Fix**:
1. Check the operator's access group for DevOps roles
2. Verify the application allows branching
3. Check the Deployment Manager configuration

## Environment Promotion Best Practices
- Dev → QA → Staging → Production pipeline
- Automated testing at each stage
- Use Product rules for controlled packaging
- Document all deployment steps and rollback procedures
- Monitor post-deployment health (error rates, performance)
- Never deploy directly to production without staging validation
- Keep deployment packages small and focused

## Rollback Procedures
1. **Quick rollback**: Revert the ruleset version to the previous version
2. **Schema rollback**: Restore database from backup (if schema changes were made)
3. **Application rollback**: Restore the previous application stack configuration
4. Always test rollback procedures before they're needed
5. Keep a deployment log with timestamps for rollback reference
"""
    },
    {
        "url": "https://docs.pega.com/bundle/platform/page/platform/devops/application-packaging.html",
        "title": "Application Packaging — RAP, Product Rules, and Export Errors",
        "content": """# Application Packaging — Troubleshooting

## RAP (Rules Archive Package) Issues

### "RAP export fails"
**Root Cause**: Export configuration or rule dependency issue.
**Fix**:
1. Check the export log for specific errors
2. Verify all dependent rules are included in the export scope
3. Check for locked or read-only rules that can't be exported
4. Ensure the export operator has sufficient permissions

### "RAP import fails: version conflict"
**Root Cause**: The target system already has a newer version of the ruleset.
**Fix**:
1. Check the ruleset version in both source and target
2. Use "overwrite" option if downgrading is intended
3. Increment the version in the source before export
4. Check for customization conflicts in the target

### "Product rule missing dependencies"
**Root Cause**: Product rule doesn't include all required rules.
**Fix**:
1. Use the "Dependency Analyzer" to check for missing references
2. Add missing rulesets to the product rule
3. Include data instances (data types, local lists, etc.)
4. Test the product rule import in a clean environment

## Best Practices
- Always test imports in a staging environment first
- Include all dependencies in your RAP/Product rule
- Use the dependency analyzer before packaging
- Version your deployments consistently
- Document the import order for multi-package deployments
"""
    },
]


def seed_knowledge_base_phase3a(output_dir: Path = RAW_DOCS_DIR) -> int:
    """Write Phase 3A curated docs to the raw_docs directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE3A:
        doc["content_length"] = len(doc["content"])
        filename = f"curated_p3a_{count:03d}.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        logger.info(f"  Saved: {doc['title'][:60]} ({doc['content_length']} chars)")
        count += 1
    logger.info(f"\nSeeded {count} Phase 3A documents to {output_dir}")
    return count


if __name__ == "__main__":
    count = seed_knowledge_base_phase3a()
    print(f"\nDone! {count} Phase 3A documents written.")
    print("Now run: python -m indexer.index_docs")
