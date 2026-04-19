"""
Curated Pega Knowledge Base — Phase 13 (Testing, Quality & Guardrails)
Run: python -m crawler.seed_kb_phase13
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE13 = [
    {
        "title": "Pega Application Guardrails — Complete Guide",
        "url": "https://pegadocs.internalfaq/guardrails-complete",
        "content": """# Pega Application Guardrails — Complete Guide

## What Are Guardrails?

Guardrails are automated quality checks in Pega Designer Studio that scan your application for violations of Pega best practices, performance patterns, security standards, and maintainability rules. They provide scores (0-100) across multiple categories and track technical health over time.

## Guardrail Score Interpretation

- **90-100**: Excellent — minimal violations, production-ready
- **75-89**: Good — acceptable, monitor for improvement opportunities
- **60-74**: Fair — several violations to address before major release
- **Below 60**: Poor — critical issues blocking deployment

## Guardrail Categories

### Performance Guardrails
- Rule execution time optimization
- Database query efficiency
- Caching strategy validation
- Service call optimization
- XML/JSON parsing best practices

### Maintainability Guardrails
- Code duplication detection
- Rule complexity analysis
- Documentation completeness
- Naming convention compliance
- Rule inheritance patterns

### Security Guardrails
- Privilege escalation risks
- Unsafe data handling
- SQL injection vulnerabilities
- Authentication/authorization gaps
- Credential storage violations

### Best Practices Guardrails
- Case model structure adherence
- Flow design patterns
- Data model normalization
- Integration pattern compliance
- Operator/role configuration standards

## Running a Guardrails Report

1. Navigate to **Application → Quality → Guardrails**
2. Click **Scan** to run full analysis (takes 5-30 min depending on app size)
3. View results by category or violation type
4. Filter by severity: Info, Warning, Severe
5. Export report as PDF or Excel

## Common Guardrail Violations & Fixes

### "Property accessed before validation"
**Issue**: Reading a property without checking existence first
**Fix**: Use `PegaRULES:IfNotEmpty()` or add validation rule before access

### "Direct database query without pagination"
**Issue**: Loading unlimited rows from database
**Fix**: Use `Fetch All Pages With Filter` or implement limit with offset

### "Service rule without error handling"
**Issue**: Calling service without try-catch pattern
**Fix**: Wrap in error handler, implement circuit breaker for external APIs

### "Rule without documentation"
**Issue**: Missing purpose/usage notes
**Fix**: Add `Description` and sample input/output in rule metadata

## Guardrail Warnings vs Severe

**Warnings**: Non-blocking issues, should be resolved before production push
**Severe**: Blocking issues causing performance degradation or security risks — must fix before deployment

## Target Guardrail Scores by Phase

- **Development**: 70+ (identify patterns early)
- **QA/Testing**: 80+ (before system testing)
- **Staging**: 85+ (production readiness)
- **Production**: 90+ (live applications should maintain excellence)

## Optimization Tips

- Run guardrails weekly in development
- Address Severe violations within sprint
- Schedule Warning fixes in backlog refinement
- Use guardrail trends to identify architectural issues
- Correlate guardrail scores with production incidents
"""
    },
    {
        "title": "Scenario Testing in Pega",
        "url": "https://pegadocs.internalfaq/scenario-testing",
        "content": """# Scenario Testing in Pega

## Scenario Testing Overview

Pega's Scenario Testing tool enables end-to-end testing of case lifecycles without manual UI interaction. Tests are data-driven, repeatable, and can be executed in automated pipelines.

## Creating Test Suites

1. Navigate to **Application → Testing → Test Definition**
2. Click **Create → Test Suite**
3. Specify test data source (spreadsheet or inline)
4. Configure case lifecycle steps:
   - Case creation with initial data
   - Assignment and work item completion
   - Service calls and integrations
   - Decision trees and branching

## Testing Case Lifecycle End-to-End

### Basic Test Structure
```
1. Setup: Create operator, department, work queue
2. Trigger: Initialize case with input data
3. Execute: Process case through multiple assignments
4. Validate: Assert final state matches expected output
5. Cleanup: Archive test case, reset data
```

### Multi-Stage Case Testing
Test complex cases with multiple assignments and approval workflows:
- Stage 1: Create case → verify initial state
- Stage 2: Auto-process first assignment → check routed correctly
- Stage 3: Approve/reject → verify alternate path
- Stage 4: Final step → validate completion

## Data Setup for Tests

### Test Data Sources
- **Inline**: Small test sets defined in test definition UI
- **Spreadsheet**: Excel/CSV with parameterized values
- **Database**: Query existing test records for realistic scenarios
- **API**: Generate dynamic data via service call before test runs

### Key Practices
- Use unique identifiers per test run (timestamps, UUIDs)
- Separate read-only reference data from test-specific data
- Create test-specific accounts with limited privileges
- Use data masking for sensitive fields in test sets

## Assertions and Validations

### Property Assertions
```
Assert Case Property: CaseID equals "TEST-12345"
Assert Clipboard Property: Status equals "Approved"
```

### Service Response Validation
```
Assert Service Response: Response Code is 200
Assert JSON Path: $.result.approved_amount > 5000
```

### Database Validation
```
Assert Database Query: SELECT COUNT(*) FROM Cases WHERE Status='Closed' > 0
```

## Running Test Suites

1. Open Test Suite definition
2. Click **Execute Test Suite**
3. Choose batch mode (all tests) or single test
4. Select test environment/database
5. Monitor execution progress in real-time
6. Review pass/fail results immediately after

## Test Reports

Reports capture:
- Pass/fail rate (should target 100% for automated gates)
- Execution time per test and overall
- Failed assertion details with actual vs expected values
- Performance metrics per case step
- Error logs and stack traces

Export formats: HTML, PDF, XML for CI/CD integration

## Debugging Failing Scenario Tests

### Common Issues

**"Test case creation failed: Service returned 500"**
- Check service endpoint connectivity in test environment
- Verify service authentication (API keys, OAuth tokens)
- Review service request payload formatting
- Check database permissions for write operations

**"Assertion failed: Expected 'Approved' but got 'Pending'"**
- Verify routing rules not blocked by organization context
- Check assignment queue capacity (might auto-reject if overloaded)
- Review SLA rules that might alter status automatically
- Check for conflicting workflow versions

**"Test timed out waiting for assignment completion"**
- Increase timeout threshold for complex orchestrations
- Check for deadlocks in multi-case orchestrations
- Verify agent pool capacity during load testing
- Review thread wait conditions in activity scripts

## Automating Test Execution

### Jenkins/GitLab CI Integration
```bash
# Run test suite via command line
python -m pega.test_runner --suite="MainWorkflow" --env="qa" --report=junit.xml
```

### Scheduling Nightly Tests
- Schedule daily full suite execution on QA environment
- Trigger regression tests on every code deployment
- Run performance tests weekly in staging
- Archive test results for trend analysis

### Failed Test Notifications
- Email team on test failure with details
- Post failure summary to Slack channel
- Create Jira tickets for blocking failures
- Track flaky tests (pass/fail inconsistently)
"""
    },
    {
        "title": "Application Quality Dashboard & Code Review",
        "url": "https://pegadocs.internalfaq/quality-dashboard",
        "content": """# Application Quality Dashboard & Code Review

## Quality Dashboard Overview

The Pega Quality Dashboard provides real-time visibility into application health metrics, compliance scores, and technical debt. Access via **Application → Administration → Quality**.

## Key Quality Metrics

### Compliance Score
- **Definition**: Percentage of rules passing quality checks
- **Calculation**: (Passing Rules / Total Rules) × 100
- **Target**: 85%+ for production applications
- **Components**: Code standards, naming conventions, documentation, pattern adherence

### Rule Coverage
- **Unit test coverage**: Percentage of rules with associated test cases
- **Target**: 70%+ critical rules, 50%+ overall
- **Priority**: Test rules handling monetary calculations, approvals, integrations first

### Cyclomatic Complexity
- **Definition**: Number of independent paths through rule logic
- **Threshold**: Warn if > 10, severe if > 20
- **Improvement**: Break complex rules into smaller, focused rules

## Technical Debt Tracking

### Identifying Debt
- **Obsolete Rules**: Rules created over 2 years ago with zero usage
- **Dead Code**: Conditional branches that never execute
- **Duplicate Logic**: Same validation/calculation in multiple rules
- **Anti-Patterns**: Using deprecated Pega features (Rule-List instead of Decision Tree)

### Measuring Debt
Dashboard shows:
- Count of issues by severity
- Estimated remediation hours
- Debt vs new development ratio (target: < 20%)
- Debt accumulation trend (should be stable/declining)

## Code Review Process in Pega

### Peer Review Workflow
1. Developer creates change (rule, process, report)
2. Submits for review with description of changes
3. Reviewer(s) examine via **Development → Code Review**
4. Reviewer approves, requests changes, or rejects
5. Developer resolves comments and resubmits
6. Approval merged to main branch

### Code Review Checklist
- Rule documentation complete (purpose, inputs, outputs)
- Follows team naming conventions
- No hardcoded values (use ruleset parameters or data objects)
- Error handling implemented for all service calls
- Performance considerations addressed (caching, queries optimized)
- Security: No sensitive data logged, proper privilege rules applied
- Guardrails: No new severe violations introduced

## Peer Review Best Practices

### For Reviewers
- Review within 24 hours to maintain velocity
- Leave constructive comments explaining "why" not just "no"
- Suggest improvements as "optional" vs "required"
- Approve changes you're confident in; escalate architectural questions
- Check consistency with existing codebase patterns

### For Developers
- Keep changes focused (avoid mixing refactoring with features)
- Write clear change descriptions with context
- Respond to all review comments before re-requesting approval
- Request re-review only after addressing feedback
- Thank reviewers and discuss learning opportunities

## Automated Quality Checks

### Pre-Commit Hooks
- Guardrails scan on every save (can be run locally)
- Naming convention validation
- Documentation completeness check
- No hardcoded credentials detection

### Build-Time Checks
- Full guardrails report generated
- Code duplication analysis (similar rule logic)
- Security vulnerability scan
- Dependency version compatibility check

## Integrating Quality Gates in CI/CD

### Pipeline Stages
1. **Commit**: Pre-commit hooks run locally
2. **Build**: Guardrails report generated, must pass threshold
3. **Test**: Automated scenario tests execute
4. **Deploy to QA**: Quality dashboard updated
5. **Approval**: Manual code review gate
6. **Deploy to Staging**: Performance tests run
7. **Production Release**: Quality sign-off required

### Enforcement Policies
- Cannot merge if guardrails < 75
- Must have 2+ peer approvals for rule changes
- Security scan must show zero critical findings
- Test coverage must increase or stay same (never decrease)
- Performance regression tests must pass

### Dashboard Visibility
- Display current compliance score in build logs
- Show guardrail trends over releases
- Link failed quality checks to remediation backlog
- Track which teams maintain highest standards
"""
    },
    {
        "title": "Performance Testing Pega Applications",
        "url": "https://pegadocs.internalfaq/performance-testing",
        "content": """# Performance Testing Pega Applications

## Load Testing Tools & Setup

### Apache JMeter with Pega
- Download JMeter; add Pega plugin for case/work item handling
- Create thread groups representing different user types (agents, customers, integrations)
- Configure ramp-up (how quickly users increase) and hold duration
- Record baseline response times under normal load

### Gatling for Pega
- Scala-based, better for continuous load testing in CI/CD
- Simulates user scenarios with realistic think time
- Generates HTML reports with percentile response times (p95, p99)
- Can run distributed across multiple machines for massive load

## Performance Test Plan

### Phase 1: Baseline (Current State)
- Document current user count, daily case volume, API call rates
- Record typical case processing time (p50, p95, p99 percentiles)
- Measure database response times and query durations
- Identify current resource utilization (CPU, memory, disk I/O)

### Phase 2: Load Testing
- Increase concurrent users 10% weekly until reaching target
- Monitor response time degradation under load
- Identify when system reaches 80% capacity (before breaking)
- Document performance at each load level

### Phase 3: Stress Testing
- Push load beyond expected peak (2-3x normal volume)
- Identify breaking point and recovery behavior
- Test failover scenarios and graceful degradation
- Verify monitoring/alerting triggers appropriately

### Phase 4: Soak Testing
- Run sustained load (80-90% capacity) for 4-8 hours
- Detect memory leaks, connection pool exhaustion
- Monitor database growth and log file size
- Check for gradual performance degradation

## Identifying Bottlenecks

### Using PAL (Performance Analysis Log)
```
1. Enable PAL in system settings
2. Execute case processing under load
3. Review generated .pal files in /pegarules directory
4. Look for methods with high execution time or call count
5. Correlate with slow case processing times
```

### Using APD (Application Profiler & Debugger)
- **Trace Database Calls**: Identify slow queries or N+1 query patterns
- **Measure Rule Execution**: Which rules consume most CPU time
- **Monitor Service Calls**: Identify external API latency issues
- **Track Memory Allocation**: Look for unnecessary object creation

### Using Tracer Tool
1. Open **Development → Tracer**
2. Run test case and capture execution trace
3. Review timeline: identify steps taking longest
4. Drill into slow steps: understand why (DB query, service call, complex logic)
5. Look for duplicate work or unnecessary processing

## Common Performance Anti-Patterns

### "Query Everything, Filter in Memory"
**Problem**: Loading 100k records then filtering to 10
**Fix**: Add WHERE clause to only fetch needed records; use pagination

### "Service Call Per Record"
**Problem**: Loop calling external API once per case/item
**Fix**: Batch requests into single call; use bulk APIs

### "No Caching for Lookup Data"
**Problem**: Querying reference tables on every transaction
**Fix**: Cache with TTL; invalidate on data changes

### "Synchronous Processing for Large Datasets"
**Problem**: Processing 10k cases sequentially blocking UI
**Fix**: Queue work asynchronously; process in background via scheduler

## Interpreting Performance Metrics

### Response Time Percentiles
- **p50** (median): Most users experience this response time
- **p95**: 95% of users are this fast or faster (crucial for SLA)
- **p99**: Tail latency; still impacts user experience for worst-case users

### Throughput (TPS)
- **Baseline**: Cases/second under normal load
- **Peak**: Maximum achievable cases/second
- **Sustainable**: TPS maintainable for hours without degradation

### Resource Metrics
- **CPU**: Peak utilization should stay below 70% for headroom
- **Memory**: GC pauses should be < 500ms, heap usage stable
- **Database**: Query time p95 < 100ms, connection pool availability > 20%
- **Disk I/O**: Write latency < 10ms, read cache hit rate > 85%

## Capacity Planning

### Calculating Required Infrastructure
```
Required Threads = (Expected Concurrent Users) × (Avg Response Time / Target Response Time)
Example: 1000 users × (500ms / 200ms) = 2500 user threads capacity needed
```

### Headroom Calculation
- Never run production above 70% capacity
- Plan for 50% growth over next fiscal year
- Add 20% buffer for seasonal peaks
- Example: If need 2500 threads max, provision 3500-4000
"""
    },
    {
        "title": "Test Data Management & Environment Strategy",
        "url": "https://pegadocs.internalfaq/test-data-management",
        "content": """# Test Data Management & Environment Strategy

## Creating Test Data for Pega

### Manual Test Data Creation
1. Open target work object form (e.g., LoanRequest)
2. Fill in required fields with test-appropriate values
3. Create multiple variants (edge cases, typical cases, error cases)
4. Save cases with clear naming: TEST_ScenarioName_YYYYMMDD
5. Document test case purpose in Case Notes

### Bulk Test Data Generation

#### Via Spreadsheet Import
1. Create CSV with columns matching case properties
2. Use **Utilities → Import → Bulk Case Import**
3. Configure mapping between CSV columns and case properties
4. Validate import preview before executing
5. Monitor import job progress (can take hours for large datasets)

#### Via API Automation
```python
for i in range(1000):
    payload = {
        "Name": f"TestApplicant_{i}",
        "Email": f"test_{i}@example.com",
        "LoanAmount": 50000 + (i * 1000),
        "Employer": "TEST_CORP"
    }
    requests.post(f"{pega_url}/api/application/v1/cases", json=payload)
```

## Data Masking for Non-Prod Environments

### Why Data Masking is Critical
- Prevents PII exposure (SSN, phone, email)
- Ensures compliance with GDPR, CCPA, HIPAA
- Protects sensitive business data in lower environments
- Enables developers to test production-like data safely

### Masking Strategies

#### Field-Level Masking
- **PII Fields** (SSN, DOB, Phone): Replace with fake but valid formats
- **Email Addresses**: Replace with test@example.com variations
- **Credit Card**: Replace with test card numbers (4111-1111-1111-1111)
- **Amounts**: Keep ranges but shift actual values

#### Record-Level Masking
- Exclude records for VIP customers
- Exclude super-user accounts
- Remove inactive/archived records (waste of space)

## Synthetic Data Generation

### Benefits
- Generates diverse scenarios automatically
- No privacy concerns (completely fictional)
- Can target edge cases and rare conditions
- Reproducible with seed values for regression testing

### Tools & Approaches
- **Faker Library** (Python): Generate realistic names, emails, addresses
- **TestDataBuilder Pattern**: Fluent API to construct test objects
- **Pega Data Generator Rule**: Use decision tree to create valid variations
- **Combinatorial Testing**: Generate permutations of input values

## Managing Test Operator Records

### Test Operator Naming Convention
```
TEST_FirstName_LastName_MMDD
Example: TEST_John_Smith_0416
```

### Operator Configuration for Testing
- Assign to TEST_ROLE (minimal privileges)
- Set work queue capacity to avoid bottlenecks
- Disable email notifications (prevent alert spam)
- Set password to expire in 30 days (if created monthly)
- Document purpose: "Automated load testing operator"

### Cleanup Schedule
- Disable operators older than 60 days
- Delete operators older than 90 days
- Archive associated work items before deletion
- Validate no active cases assigned to test operators

## Environment Refresh Strategy

### Refresh Frequency
- **Development**: On-demand, developers can reset anytime
- **QA**: Weekly after regression test completion
- **Staging**: Monthly or before major release
- **Production**: Never (obviously)

### Refresh Procedure
1. Backup current environment (for incident analysis)
2. Restore database from production snapshot
3. Execute data masking scripts
4. Remove production operators; create test operators
5. Run smoke tests to verify critical paths
6. Notify team of refresh completion

### What Gets Removed/Reset
- All test cases and work items
- Production operator accounts
- Configuration changes made during testing
- Log files and temporary data
- Browser cache and user preferences

## Debugging Data-Dependent Test Failures

### Common Issues

**"Test case data not found"**
- Verify test data actually exists in target database
- Check environment refresh didn't delete test data
- Confirm case ID format matches expectations
- Check authorization: does test operator have access?

**"Assertion fails intermittently (flaky test)"**
- Timing issue: Data not written before assertion
- Add explicit wait for database commit
- Check for race condition with parallel test execution
- Verify no automatic archiving of test cases mid-test

**"Data setup succeeds but case creation fails"**
- Verify all required properties set (not just database fields)
- Check business rules (case rules, routing rules) not rejecting test data
- Review application user access permissions on test operator
- Check data consistency (referenced objects must exist)

### Debugging Steps

1. **Capture Full Test Context**
   - Log all input data before case creation
   - Screenshot application state at failure point
   - Save API request/response payloads

2. **Replicate Issue Locally**
   - Create isolated test with same data
   - Run in development with tracing enabled
   - Reproduce without test framework overhead

3. **Analyze Logs**
   - Search application logs for errors around test timestamp
   - Check database logs for constraint violations
   - Review security logs for permission denials

4. **Isolate Variables**
   - Test with minimal dataset first
   - Gradually add fields until failure recurs
   - Identify which property value causes issue
   - Test boundary values (empty strings, zeros, max values)
"""
    }
]

def seed_phase13():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE13:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase13_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE13)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 13 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase13()
