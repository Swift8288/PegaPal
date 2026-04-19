"""
Curated Pega Knowledge Base — Phase 7 (Pega Robotics & RPA)
Run: python -m crawler.seed_kb_phase7
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE7 = [
    {
        "url": "curated://pega-rpa-overview",
        "title": "Pega Robotic Process Automation (RPA) Overview",
        "content": """
# Pega Robotic Process Automation (RPA) Overview

## What is Pega RPA?

Pega RPA (Robotic Process Automation) is a software robot framework that automates repetitive, high-volume business processes across desktop applications, web interfaces, and legacy systems. Unlike traditional integration APIs, RPA robots mimic human user behavior—clicking, typing, navigating—enabling automation of systems without code changes.

## Architecture Components

### Robot Runtime
- Executes automations on desktop or server
- Runs Robot Studio projects (.roborun files)
- Communicates with Robot Manager for orchestration
- Supports 32-bit and 64-bit application automation

### Robot Manager
- Central orchestration and monitoring service
- Manages robot deployment, scheduling, and fleet monitoring
- Tracks execution history, logs, and robot health
- Integrates with Pega Decision Hub for work allocation

### Robot Studio
- IDE for designing automations without code
- Visual workflow designer with drag-and-drop components
- Integrated debugger and testing framework
- Interrogation tools for capturing UI element attributes

## Attended vs Unattended Robots

### Attended Robots
- User-triggered, runs on user's desktop with human oversight
- Acts as desktop assistant (e.g., form-filling helper)
- Requires interactive session and display
- Lower complexity, easier debugging
- Example: RPA triggered on-demand to populate data entry forms

### Unattended Robots
- Server-side execution without user interaction
- Runs on scheduled intervals or event-driven
- Supports parallel execution for high-volume processing
- Requires non-interactive credential management
- Example: Nightly batch processing of transaction feeds across legacy systems

## RPA in Intelligent Automation Strategy

Pega RPA bridges legacy systems and modern process automation:
- **System Integration**: Connect to applications without native APIs
- **Process Acceleration**: Automate repetitive steps in case management
- **Exception Handling**: Let robots handle routine exceptions, escalate complex issues to humans
- **Cost Reduction**: 70-80% cost savings on manual data entry and reconciliation

## Licensing & Deployment

- RPA licensing bundled with Pega Platform subscriptions
- Per-robot licensing for unattended instances
- Robot Runtime free; Robot Manager/Studio licensed separately
- Deployment support: on-premise and cloud environments

## Common RPA Use Cases

| Industry | Scenario |
|----------|----------|
| Banking | Loan application processing, KYC verification |
| Insurance | Claims intake, policy underwriting |
| HR | Employee onboarding, benefits enrollment |
| Finance | Invoice processing, reconciliation |
| Telecom | Order provisioning, service activation |

## Key Considerations Before Implementation

1. **Process Suitability**: RPA works best on stable, high-volume, rule-based processes
2. **Application Accessibility**: Ensure target apps support automation (UI elements must be interrogatable)
3. **Change Management**: Robots break if upstream applications change; version control automations
4. **Security**: Use credential vaults, not hardcoded credentials; audit robot actions
5. **Scalability**: Unattended robots scale horizontally; plan infrastructure accordingly
"""
    },
    {
        "url": "curated://pega-robot-studio-building",
        "title": "Pega Robot Studio — Building Automations",
        "content": """
# Pega Robot Studio — Building Automations

## Robot Studio IDE Overview

Robot Studio is the integrated development environment for designing, testing, and debugging automations. It provides a low-code, visual interface for creating RPA workflows without requiring programming expertise.

### Core IDE Components

- **Automation Editor**: Visual workflow canvas with action library
- **Frame Library**: Pre-built UI interaction templates (click, type, wait)
- **Interrogation Tools**: Inspect application UI elements and capture selectors
- **Testing & Debug Panel**: Run automations step-by-step with breakpoints
- **Package Manager**: Version control and dependency management

## Creating Automations: Recording vs Manual Design

### Recording Mode (Recommended for Beginners)
```
1. Launch target application
2. Click "Record" in Robot Studio
3. Perform actions naturally (click, type, navigate)
4. Studio captures clicks and keyboard input as frames
5. Stop recording and review captured frames
```
**Pros**: Quick automation of UI flows, minimal manual coding
**Cons**: Fragile to UI changes, records absolute coordinates (breaks if window resizes)

### Manual Design (Recommended for Complex Workflows)
```
1. Start blank automation
2. Drag "Application" action to launch target app
3. Add "Click", "Type", "Wait" frames explicitly
4. Use interrogation to capture element selectors (CSS, XPath, Win32 ID)
5. Add conditional logic (if-then-else for error handling)
```
**Pros**: Robust to UI changes, reusable selectors, better error handling
**Cons**: Higher initial effort, requires understanding of element selectors

## Interacting with Desktop Applications

### Supported Application Types

| Application Type | Interrogation | Notes |
|------------------|---------------|-------|
| **Browser (Chrome, FF, Edge)** | CSS/XPath selectors | Fast, reliable; use inspect element |
| **Java Applications** | Java accessibility API | Requires Enable Accessibility in settings |
| **Win32 (Windows native)** | Win32 window handles, control IDs | Stable; use Interrogator on form controls |
| **Citrix/VDI** | Image-based + OCR | Slower; use as fallback when element access fails |
| **Legacy DOS/Terminal** | ASCII text matching | OCR; limited interactivity |

### Best Practices for Application Interaction

1. **Explicit Waits**: Always wait for elements before interacting
   ```
   Wait for Element (TextBox: "UserID")
   Type "john.doe" → TextBox
   Wait for Element Button: "Submit" → timeout 10 sec
   Click Button: "Submit"
   ```

2. **Robust Selectors**: Use unique attributes, not absolute coordinates
   ```
   Bad:  Click at coordinates (456, 234)
   Good: Click element with ID="btnSubmit"
   ```

3. **Error Handling**: Add try-catch frames for expected failures
   ```
   Try:
     Wait for Element → Timeout 5 sec
   Catch Timeout:
     Click "Retry" button
     Restart sequence
   ```

## Components: Automations, Frames, and Interrogation

### Automations (Projects)
- Top-level container for a complete RPA workflow
- Contains frames, variables, error handlers
- Version-controlled; deployable to Robot Manager
- Example: "LoanApplicationProcessor_v2.0"

### Frames (Actions)
- Discrete UI interaction steps (click, type, screenshot, extract)
- Inputs: variables, element selectors
- Outputs: return values, screenshots, extracted text
- Chainable: output of frame N feeds to frame N+1

### Interrogation
Robot Studio's interrogation panel allows real-time inspection of running applications:
```
1. Launch target app
2. Open Interrogation panel (Tools → Interrogator)
3. Click "Pick" and select UI element
4. Studio displays element properties:
   - XPath / CSS selector
   - Win32 control ID
   - Text content, attributes
5. Click "Copy Selector" to add to automation
```

## Common Errors When Building Automations

| Error | Cause | Solution |
|-------|-------|----------|
| **Element Not Found** | Selector incorrect or element didn't load | Re-interrogate; add Wait frame; use OCR as fallback |
| **Timeout Expired** | Application slow or element missing | Increase timeout; add explicit wait conditions |
| **Application Crash** | Unsupported interaction or memory leak | Test with manual interactions; isolate automation step |
| **Flaky Execution** | Timing race condition; element appears/disappears | Add explicit waits; use stable selectors; log execution |
| **Credential Errors** | Hardcoded passwords or expired tokens | Use Robot Manager credential vault |

## Debugging Workflow

1. **Breakpoints**: Set breakpoints on frames to pause execution
2. **Step-Through**: Execute frame-by-frame; inspect variable values
3. **Logging**: Add "Log" frames to record state at key points
4. **Screenshots**: Capture application state at each step
5. **Replay**: Re-run failed automation with detailed logs enabled

## Deployment Checklist

- [ ] Automation tested end-to-end (min. 3 runs)
- [ ] All credentials in vault (Robot Manager, not hardcoded)
- [ ] Error handling for timeouts, missing elements, invalid data
- [ ] Documentation: purpose, target systems, expected duration, owner
- [ ] Performance baseline: execution time, resource usage
- [ ] Monitoring: alerts for failures, execution count thresholds
"""
    },
    {
        "url": "curated://pega-attended-unattended-robots",
        "title": "Attended vs Unattended Robots — Architecture & Debugging",
        "content": """
# Attended vs Unattended Robots — Architecture & Debugging

## Attended Robots: User-Triggered Desktop Assistants

Attended robots run on a user's desktop, triggered on-demand or by user action. They augment human work, not replace it.

### Deployment Model
```
User Desktop
    ↓
[Robot Studio / Desktop Automation]
    ↓
Target Application (Legacy System, Web, etc.)
```

### Characteristics
- **Execution**: Synchronous; visible on user's desktop during run
- **Triggering**: User clicks button, hotkey, or RPA portal request
- **Session**: Requires logged-in user and active display
- **Scaling**: One robot per user (or shared terminal server session)
- **Monitoring**: User sees execution in real-time

### Use Cases
- Form auto-fill assistance
- Data export/import helpers
- Report generation triggered by user
- Legacy system data entry with validation

### Debugging Attended Robots
```
1. Reproduce issue locally with user's credentials
2. Enable debug mode in Robot Studio:
   Settings → Logging Level = DEBUG
3. Run automation; capture full execution log
4. Check for:
   - UI element selector changes (application updates)
   - Timing issues (user's system slower than dev)
   - Credential/permission problems specific to user
5. Screenshot the exact error point
```

## Unattended Robots: Server-Side Batch Processing

Unattended robots run on servers without user interaction, typically scheduled or triggered by events. They scale horizontally for high-volume workloads.

### Deployment Model
```
Robot Manager (Orchestration Server)
    ↓
[Robot Runtime Pool] (N virtual machines / containers)
    ↓
Target Applications (APIs, Databases, Legacy Systems)
```

### Architecture

**Robot Manager**
- Listens for work requests (API, Pega case system)
- Queues automations, monitors execution
- Logs results, stores audit trail
- Manages robot credentials securely

**Robot Runtime**
- Non-interactive process running on Windows Server
- Executes queued automations in parallel
- Reports execution status back to Manager
- Supports X11 virtual display for UI automation

### Characteristics
- **Execution**: Asynchronous; queued and scheduled
- **Triggering**: Time-based (cron), event-driven (case arrives), API call
- **Session**: Non-interactive; uses virtual desktop (Xvfb, RDP)
- **Scaling**: Horizontal; add runtime instances for capacity
- **Monitoring**: Automated; alerts on failures, SLAs

### Scaling Unattended Robots

#### Horizontal Scaling Strategy
```
1. Monitor Robot Manager queue depth and execution time
2. If queue > 100 items or avg runtime > 5 min:
   - Provision new Robot Runtime VM (same specs)
   - Register with Robot Manager
   - Redistribute workload automatically
3. Target: 30-40 running automations per runtime instance
```

#### Resource Planning
- **CPU**: 2-4 cores per runtime (UI automation is single-threaded)
- **RAM**: 4-8 GB per runtime + OS overhead
- **Disk**: 100 GB (app caches, logs, temporary files)
- **Network**: Stable connection to target systems; 5-10 Mbps sufficient

## Debugging Robot Failures

### Common Failure Scenarios

| Failure Mode | Indicators | Root Cause |
|--------------|-----------|-----------|
| **Element Not Found** | Selector mismatch; UI changed | Target app updated; selector stale |
| **Timeout** | Automation stuck on Wait frame | Target system slow; network latency |
| **Application Crash** | Automation stops; app closes | Memory leak; unsupported interaction |
| **Credential Error** | Auth failure; timeout on login | Expired token; wrong vault reference |
| **State Mismatch** | Logic error; wrong branch taken | Assumption about app state invalid |

### Debugging Workflow for Unattended Robots

#### Step 1: Locate Execution Log
```
Robot Manager Dashboard
  ↓ Execution History
  ↓ [Failed Run ID]
  ↓ View Log (JSON format)
```

#### Step 2: Analyze Log Entries
```json
{
  "timestamp": "2025-04-16T09:23:45Z",
  "frame": "WaitForElement(UserIDTextBox)",
  "status": "TIMEOUT",
  "details": {
    "selector": "id='txtUserID'",
    "timeout_seconds": 10,
    "last_screenshot": "frame_09_23_45.png"
  }
}
```

#### Step 3: Compare Runs
- Successful run: Did element load? How long?
- Failed run: What changed?
- Query logs: Is target system down? Responding slowly?

#### Step 4: Reproduce Locally
```
1. Export failed automation + inputs
2. Run in Robot Studio with same credentials
3. Inspect UI at failure point
4. Update selector or add error handling
5. Re-test 5+ times to verify fix
```

## Log Analysis Best Practices

### What to Capture
```
- Timestamp: correlation with target system logs
- Frame name + status (SUCCESS, TIMEOUT, ERROR)
- Element selector used
- Screenshot at failure point
- Exception stack trace (if applicable)
- Elapsed time for each frame
```

### Useful Log Patterns
```bash
# Find all timeouts in past 24 hours
grep -i "TIMEOUT" robot_manager.log | grep "2025-04-15" | wc -l

# Extract failed automation names
grep "status.*FAILED" *.log | cut -d: -f2 | sort | uniq -c

# Find slow frames (> 30 sec)
grep "elapsed_ms.*[0-9][0-9][0-9][0-9][0-9]" robot.log
```

## Monitoring & Alerting for Unattended Robots

### Key Metrics
| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| **Queue Depth** | > 500 items | Scale up runtime instances |
| **Failure Rate** | > 5% | Page on-call; investigate logs |
| **Avg Execution Time** | +50% increase | Profile robot; check target system |
| **Credential Failures** | > 10/day | Verify vault; check token expiry |

### Example Alert Configuration
```yaml
alerts:
  - name: RobotExecutionFailure
    condition: failure_rate > 0.05
    window: 1h
    action: page_oncall
    notification: slack

  - name: QueueDepth
    condition: pending_items > 500
    window: 5m
    action: auto_scale
    notification: email
```
"""
    },
    {
        "url": "curated://pega-rpa-case-management",
        "title": "RPA Integration with Case Management",
        "content": """
# RPA Integration with Case Management

## Triggering Robots from Pega Cases

Pega's case management engine seamlessly integrates with RPA, allowing cases to invoke robots as automated steps. This creates hybrid workflows where humans and robots collaborate on case resolution.

### Case + RPA Integration Points

```
Case arrives
    ↓
Case routing (assignment rule)
    ↓
[Decision: Human or Robot?]
    ├─→ Human task → Workbasket
    └─→ Robot step → Submit to Robot Manager
        ↓
        Robot executes
        ↓
        Update case with results
        ↓
        Next step (human review or close)
```

## Robot as a Case Step

### Design Pattern: Case Step Calls RPA

1. **Add Case Automation Step**
   ```
   Property: AutomationStepType = "RPA"
   Connector: Call Robot Manager API
   RobotName: "LoanDocumentExtractor"
   InputVars: Case.CaseID, Case.DocumentPath
   OutputVars: Case.ExtractedData
   ```

2. **Configure Success/Failure Flows**
   ```
   OnSuccess:
     - Update case with extracted data
     - Transition to review step
   OnFailure:
     - Log error details
     - Escalate to supervisor
     - Create follow-up activity
   ```

3. **Error Handling**
   ```
   If RobotTimeout (> 5 min):
     - Retry once (with exponential backoff)
     - If still fails, escalate to human

   If ElementNotFound:
     - Log screenshot
     - Route to RPA support queue
     - Human debugs and updates selector
   ```

## Passing Data Between Case and Robot

### Case → Robot Input

**Pattern: Structured Payload**
```json
{
  "caseId": "C-2025-04-16-001",
  "caseType": "LoanApplication",
  "inputs": {
    "applicantName": "John Doe",
    "loanAmount": 250000,
    "systemURL": "https://legacy-system.acme.com",
    "credentials": "vault://loan-system-user"
  },
  "executionTimeout": 300,
  "retryPolicy": "exponential-backoff"
}
```

**Implementation in Pega Case**
```
Activity: RPA_InitiateLoanDocExtraction
  Input: CaseID
  Output: RobotExecutionID
  Steps:
    1. Fetch case details (ApplicationName, LoanAmount)
    2. Construct JSON payload
    3. Call REST service: Robot Manager API
    4. Store RobotExecutionID in case
    5. Transition case to "AwaitingRobotCompletion"
```

### Robot → Case Output

**Pattern: Callback Notification**
```
Robot completes execution
    ↓
Call case REST API:
  PUT /cases/{caseId}/update-from-robot
    {
      "status": "completed",
      "outputs": {
        "documentExtracted": true,
        "pageCount": 47,
        "tables": 3,
        "extractedText": "..."
      }
    }
    ↓
Case event triggered
    ↓
Update case properties
    ↓
Progress to next step
```

## Handling Robot Failures in Case Flow

### Failure Modes & Case Responses

| Robot Failure | Case Behavior | Recovery |
|---------------|---------------|----------|
| **Timeout** | Hold case; create reminder | Retry after 1 hour |
| **ElementNotFound** | Route to exception queue | Human reviews; updates automation |
| **Auth Failed** | Lock case; escalate | Verify credentials in vault |
| **SystemDown** | Queue case; retry later | Wait for system recovery |

### Implementation Example: Exception Handling
```
Try:
  RobotStep: ExtractLoanDocuments
  Wait for result: 300 seconds
  If RobotStatus == "FAILED":
    Go to Exception handler

Catch RobotTimeout:
  Create activity: "Robot did not complete in 5 min"
  Route to: "RPA Support Queue"
  Set priority: "High"

Catch RobotError:
  Log: RobotErrorMessage
  If "ElementNotFound" in error:
    Route to: "RPA Developer Queue"
    Attach: Robot execution log
  Else:
    Route to: "Application Support Queue"
```

## Best Practices for Hybrid Human+Robot Workflows

### 1. Clear Ownership & Handoff

**Define Explicit Case Stages**
```
Stage 1: Intake (Human)
  - Validate submission
  - Extract key fields
  - Route to automation

Stage 2: Automation (Robot)
  - Fetch supplementary documents
  - Verify data consistency
  - Populate core system

Stage 3: Verification (Human)
  - Review robot-populated data
  - Approve or correct
  - Authorize final submission

Stage 4: Completion (Robot)
  - Submit to downstream system
  - Update customer records
  - Close case
```

### 2. Monitor Handoff Points

**Add Case Metrics**
```
case.automation_start_time
case.automation_end_time
case.automation_duration_seconds
case.automation_success_flag
case.human_review_required
case.total_case_time_seconds
```

**Dashboard: Hybrid Case Performance**
- Avg time for human steps vs robot steps
- % cases requiring human correction post-robot
- Cycle time improvements vs manual-only baseline

### 3. Audit & Compliance

**Capture Robot Actions in Case Audit Log**
```
CaseHistory:
  - Timestamp: 2025-04-16 09:15:00
    Actor: "RPA Robot: LoanDocExtractor_v1.2"
    Action: "ExtractedDocuments"
    Details: {
      documents_found: 8,
      pages_scanned: 156,
      data_quality_score: 0.94
    }

  - Timestamp: 2025-04-16 09:35:00
    Actor: "User: jane.reviewer@acme.com"
    Action: "ApprovedRobotOutput"
    Details: {
      reviewed_items: 8,
      corrections: 2,
      approval: "APPROVED"
    }
```

### 4. SLA Management

**Define RPA as Critical Path**
```
SLA: Loan Application Processing
  Total: 2 business days
  Breakdown:
    - Intake: 4 hours (human)
    - Document extraction: 30 min (robot)
    - Verification: 2 hours (human)
    - Submission: 10 min (robot)
    - Buffer: 1.5 days (escalations, rework)
```

**Monitor SLA Breaches**
- If robot step exceeds 1 hour: escalate to RPA support
- If human step exceeds SLA: assign priority case
- Track root causes: system issues vs volume spikes

## Security & Governance

### Credential Management
- Never store passwords in case properties
- Use Robot Manager credential vault (encrypted)
- Rotate credentials monthly; audit access logs
- Tag sensitive operations: require approval before execution

### Audit Trail
- Log all robot actions against case
- Maintain immutable audit log (not case property; separate DB)
- Support eDiscovery: export case + robot activity for review
"""
    },
    {
        "url": "curated://pega-workforce-intelligence",
        "title": "Pega Workforce Intelligence",
        "content": """
# Pega Workforce Intelligence

## What is Pega Workforce Intelligence?

Pega Workforce Intelligence (WFI) is an analytics platform that captures, analyzes, and visualizes how workers interact with applications and perform work. It identifies automation opportunities by discovering repetitive manual tasks and measuring process inefficiencies.

### WFI Positioning in Intelligent Automation

```
Manual Work (Employees)
    ↓
WFI Monitors & Analyzes
    ↓
Process Discovery Dashboard
    ↓
[Automation Recommendations]
    ├─→ High confidence: RPA candidate
    ├─→ Medium: Workflow redesign
    └─→ Low: Monitor further
    ↓
RPA Development (Robot Studio)
    ↓
Deployment → ROI Measurement
```

## Desktop Activity Mining

### What WFI Captures

WFI installs a lightweight desktop agent that captures:

| Data Type | Captured | Privacy |
|-----------|----------|---------|
| **Application Events** | Window titles, app switches, form fills | No keystroke logging |
| **Mouse/Keyboard Activity** | Click coordinates, dwell time, repetition patterns | Aggregated, not raw keys |
| **UI Element Interactions** | Buttons clicked, fields populated, menu selections | Element metadata only |
| **Work Duration** | Time on task, idle time, multitasking | Aggregated by hour |
| **Exception Handling** | Error messages, retry loops, workarounds | Log analysis |

### Installation & Configuration

**Deploy Agent via Installer**
```
1. Provision WFI license (per-user or organizational)
2. Download agent installer from Pega cloud
3. Push to desktops via SCCM / Puppet / MDM
4. Agent auto-starts; minimal system impact (< 1% CPU)
5. Data sent encrypted to Pega analytics server
```

**Privacy & Compliance Controls**
```
Settings → Activity Capture
  ☑ Capture application activity
  ☑ Capture keyboard/mouse activity
  ☐ Capture clipboard (opt-out available)
  ☐ Capture screen recording (off by default)

Blocked Applications (never captured):
  - Password managers
  - Banking/financial apps
  - Email clients (auto-excluded)
```

## Process Discovery: Identifying Automation Candidates

### WFI Discovery Workflow

```
Step 1: Collect Data
  Deploy agent to user group (e.g., loan officers)
  Collect data for 2-4 weeks
  Accumulate > 100 hours of activity

Step 2: Process Mining
  WFI algorithm extracts workflows from raw events
  Identifies: task sequences, decisions, loops, workarounds
  Calculates: frequency, duration, variability

Step 3: Generate Candidate List
  Rank processes by:
    - Frequency (> 50 instances/month)
    - Repetitiveness (low variability in steps)
    - Manual effort (> 30 min per cycle)
    - Stability (application doesn't change often)

Step 4: Analyst Review
  Subject matter expert validates candidates
  Eliminates: complex edge cases, policy exceptions
  Prioritizes: highest ROI opportunities
```

### Discovery Dashboard Metrics

**Process Overview**
```
Process: "Loan Document Verification"
  ├─ Instances/Month: 450
  ├─ Avg Duration: 18 min
  ├─ Variability: ±5 min (low—good automation candidate)
  ├─ Manual Apps: 3 (legacy_system, email, Excel)
  ├─ Total Monthly Hours: 135 hours
  └─ Estimated Robot Savings: 120 hours/month (89%)
```

**Automation Feasibility Score**
```
Criteria:
  Frequency: 450/month           → 95/100 ✓
  Stability: App changes < 2x/yr → 90/100 ✓
  Clarity: Decision trees < 5    → 85/100 ✓
  System Access: APIs available  → 70/100 ~ (legacy system)
  ────────────────────────────────────────
  Overall Automation Score: 85/100 → "HIGH PRIORITY"
```

## How WFI Data Feeds into RPA Decisions

### From Discovery to RPA Project

```
WFI Candidate Report:
  ├─ Process: "Loan Document Verification"
  ├─ Business Value: $180K annual savings
  ├─ Effort Estimate: 80 hours RPA dev
  ├─ Payback Period: 3.2 weeks
  └─ Key Steps: [step sequence from mining]

  ↓ (Hand off to RPA team)

RPA Development:
  1. Use WFI-identified steps as automation spec
  2. Validate step sequence in Robot Studio
  3. Build automation closely matching WFI workflow
  4. Test against WFI data (replay automation on captured data)
  5. Deploy; compare execution to baseline
```

### Validation Loop: WFI Monitors RPA Impact

```
Before RPA:
  Manual execution: 18 min/instance
  Monthly instances: 450
  Total effort: 135 hours/month

After RPA Deployment:
  Robot execution: 3 min/instance
  Success rate: 92%
  Human review (8% failures): 5 min × 36 = 180 min
  Total effort: 3 + 3 = 6 hours/month

Measured Savings: 129 hours/month (96%)
Actual ROI: 98% (exceeds estimate)
```

## Reports and Dashboards

### Executive Dashboard

**KPIs Tracked**
```
Total Workforce Hours Analyzed:        12,500 hours
Processes Identified:                   47 candidates
High-Priority Automations:              12 live
Estimated Annual Savings:               $2.4M
Active WFI Licenses:                    450 users
```

**Trend Analysis**
```
Month    Instances   Avg Duration   Variability   ROI Potential
────────────────────────────────────────────────────────────
Jan      380         22 min         ±8 min        $85K
Feb      420         20 min         ±6 min        $95K
Mar      450         18 min         ±5 min        $108K
Apr      475         17 min         ±4 min        $120K  ← Improving
```

### Process Mining Dashboard

**Visual Workflow Discovery**
```
Sankey diagram showing:
  Step 1: Open Legacy System    (100% of cases)
     ↓ (98%)
  Step 2: Query Customer Record
     ├─ (95%) Step 3: Download Documents
     │    ├─ (85%) Step 4: Email To-Loan-Officer
     │    └─ (10%) Step 4b: Handle Exception
     └─ (5%) Step 3b: Manual Lookup (workaround)

Insight: "Step 3b" (workaround) appears in 5% of cases
  → Opportunity: Fix underlying query; eliminate workaround
  → Savings: 22.5 hours/month
```

### Activity Pattern Report

**Identify Manual Workarounds**
```
User: John Smith
  Normal Process (80% of work):
    1. Open CRM         (2 min)
    2. Query customer   (1 min)
    3. Export to Excel  (3 min)
    4. Email to peer    (1 min)
    ────────────────────────
    Total: 7 min/instance

  Exception Handling (20% of work):
    1. Open CRM         (2 min)
    2. Manual lookup in old database  (15 min) ← WORKAROUND
    3. Reconcile data in Excel        (10 min) ← WORKAROUND
    ────────────────────────
    Total: 27 min/instance

Recommendation: Fix CRM query to eliminate workaround
  Potential: 80 hours/month savings if workaround eliminated
```

### Utilization & Idle Time Report

**Identify Efficiency Opportunities**
```
Department: Loan Processing
  Average Task Duration:     18 min
  Context-Switch Rate:       4.2 switches/hour
  Idle Time (waiting):       12% (~7 min/hour)
  Multitasking Overhead:     +15% longer task duration

Findings:
  - Users context-switch frequently (interruptions)
  - Idle time suggests waiting for system (backend processing lag)
  - Multitasking adds 2-3 min to each task

Recommendations:
  1. Batch process instead of individual tasks (reduce context-switching)
  2. Async backend processing (reduce idle wait time)
  3. Dedicated focus time blocks (minimize interruptions)
  → Potential: 25% efficiency gain without RPA
```

## Best Practices: From Data to Decision

### 1. Set Clear Scope for Mining
- Target specific process or team
- Define time window (2-4 weeks minimum)
- Ensure >80% participation for statistical validity

### 2. Validate Candidates with Business Owners
- WFI algorithm identifies patterns; business validates feasibility
- Ask: "Can this automation handle all cases in scope?"
- Identify exceptions: policy changes, manual overrides, judgment calls

### 3. Account for Change Management
- Automating old processes may not be optimal
- Use WFI insights to redesign process first
- Then automate optimized workflow

### 4. Measure and Iterate
- Compare planned vs actual RPA performance
- Feedback to improve automation (better error handling, timeouts)
- Re-run WFI after 3 months to identify follow-up opportunities
"""
    },
    {
        "url": "curated://pega-rpa-debugging-troubleshooting",
        "title": "RPA Debugging & Troubleshooting",
        "content": """
# RPA Debugging & Troubleshooting

## Robot Studio Debugger

Robot Studio includes a powerful integrated debugger for step-by-step execution and runtime inspection.

### Enabling Debug Mode

**Method 1: Debug Button in IDE**
```
1. Open automation in Robot Studio
2. Click "Debug" (green play icon, or F5)
3. Choose: "Debug in Studio" (local) or "Debug on Robot Manager" (remote)
4. Studio launches target application in debug context
5. Execution pauses at first frame
```

**Method 2: Programmatic Breakpoints**
```
Add Debug Frame (in automation):
  [Debug(message: "About to query customer")]
  [Click Element: CustomerSearchButton]
  [Debug(message: "Click completed")]

When running with debugger enabled:
  Execution pauses at Debug frames
  Inspector shows all variables at that point
```

### Debugger Interface

```
┌─────────────────────────────────────────┐
│ Variables Panel                         │
├─────────────────────────────────────────┤
│ Global Vars:                            │
│   caseId = "C-2025-04-16-001"          │
│   customerName = "John Doe"             │
│   tempData = {nested object...}         │
│ Local Vars:                             │
│   clickCount = 5                        │
│   retryAttempt = 2                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Execution Stack (Call Stack)            │
├─────────────────────────────────────────┤
│ [Main Automation]                       │
│   └─ [SubAutomation: FetchCustomer]     │
│       └─ [Frame: WaitForElement] ← HERE │
│         [Paused]                        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Inspector Panel                         │
├─────────────────────────────────────────┤
│ Current Frame: WaitForElement           │
│   Input:  selector = "id='txtCustomer'" │
│   Timeout: 10 seconds                   │
│   Status: WAITING (3.2 sec elapsed)     │
│ ────────────────────────────────────────│
│ [Step Over] [Step Into] [Continue] ...  │
└─────────────────────────────────────────┘
```

## Setting Breakpoints

### Breakpoint Types

| Type | Use Case |
|------|----------|
| **Frame Breakpoint** | Pause before specific frame executes; inspect inputs |
| **Conditional Breakpoint** | Pause only if condition true (e.g., retryCount > 3) |
| **Variable Watch** | Break if variable changes |
| **Exception Breakpoint** | Break on error/timeout before handling |

### Creating Breakpoints

```
In Robot Studio Editor:
1. Right-click on frame
2. Select "Set Breakpoint"
3. (Optional) Right-click again, "Edit Breakpoint"
4. Add condition: "if retryAttempt >= 2"
5. Run automation; execution pauses when condition met

Result:
  Frame highlighted (red circle)
  Variables panel shows state at breakpoint
  Target application frozen at interaction point
  Can inspect UI, take screenshot, modify variables
```

## Log Levels and Detailed Logging

### Configuring Log Levels

**Global Log Level (Robot Studio Settings)**
```
Tools → Options → Logging
  Level: [Debug | Info | Warning | Error]
  Output: [Console | File | Both]
  File Location: C:\Temp\robot_studio.log
```

**Per-Frame Log Levels**
```
In automation, add Log frame:
  [Log("CustomerName: " + varCustomerName, level: "DEBUG")]
  [Log("Query returned " + rows.length + " results", level: "INFO")]
  [Log("Unexpected result type: " + typeof(rows), level: "WARNING")]
  [Log("CRITICAL: Authentication failed", level: "ERROR")]
```

### Log Output Example

```
2025-04-16 09:15:23.045 [INFO]  Automation started: LoanDocExtractor_v1.2
2025-04-16 09:15:23.067 [DEBUG] Initializing variables: caseId=C-2025-001, timeout=30
2025-04-16 09:15:23.100 [DEBUG] Launching legacy_app.exe
2025-04-16 09:15:25.234 [INFO]  Application window detected
2025-04-16 09:15:25.456 [DEBUG] Interrogating element: CustomerIDTextBox
2025-04-16 09:15:25.467 [DEBUG] Selector found: id='txtCustomer'
2025-04-16 09:15:25.489 [INFO]  Clicking element
2025-04-16 09:15:26.012 [DEBUG] Type: "C-2025-001" into CustomerIDTextBox
2025-04-16 09:15:26.145 [DEBUG] Frame elapsed: 656ms
2025-04-16 09:15:26.156 [WARNING] Long frame duration (> 500ms); may indicate lag
2025-04-16 09:15:26.200 [ERROR] Element not found: SubmitButton (timeout 10s)
2025-04-16 09:15:26.205 [INFO]  Attempting fallback: click by XPath
2025-04-16 09:15:26.345 [INFO]  Fallback successful
2025-04-16 09:15:26.678 [INFO]  Automation completed successfully
```

## Common Runtime Errors & Resolution

### 1. Element Not Found

**Symptom**
```
[ERROR] Element not found: LoginButton (timeout 10 seconds)
  Selector: xpath="//button[@id='btnLogin']"
  Last screenshot: /logs/error_screenshot_09_15_26.png
```

**Debugging Steps**
```
1. Open target application manually
2. Find the button visually
3. Right-click → Inspect (browser) or Interrogate (Studio)
4. Check if XPath is still valid:
   - Application UI changed?
   - Element ID changed?
   - Element dynamically rendered?
5. Update selector to more robust version:
   Bad:  //button[@id='btnLogin']  (fragile to ID changes)
   Good: //button[contains(text(), 'Log In')]  (content-based)
6. Re-test 3+ times to confirm fix
```

**Common Causes**
| Cause | Fix |
|-------|-----|
| Selector changed | Re-interrogate; use stable attributes (text, aria-label) |
| Element not loaded yet | Add Wait frame before Click; increase timeout |
| Wrong window/tab active | Add frame to switch window/tab first |
| Application crashed | Add error handling; retry frame |
| Citrix/VDI lag | Increase timeout; use slower interaction frame |

### 2. Timeout Expired

**Symptom**
```
[ERROR] Timeout waiting for element: ProcessingSpinner (timeout 30 seconds)
  Automation paused after 30.0 sec
  Check: Is target system processing? Hang? Network lag?
```

**Debugging Steps**
```
1. Take screenshot at timeout point
   → Is application visible but unresponsive?
   → Is network disconnected?
   → Is CPU pegged at 100%?

2. Check target system logs
   → Any errors in application event log?
   → Database queries running slow?
   → API calls failing?

3. Increase timeout incrementally
   Original: 10 sec → Try: 30 sec
   If success: system is slow (not broken)
   If fail: systemic issue

4. Add intermediate wait conditions
   Instead of:    Wait 30 sec for element
   Better:        Wait 5 sec for element
                  If found: continue
                  If not: Wait another 10 sec for "loading" spinner
                         Continue waiting (system is still loading)
```

**Resolution Options**
```
Increase timeout:
  [WaitForElement("ProcessingSpinner", timeout: 60)]

Add retry logic:
  Try:
    [WaitForElement("ProcessingSpinner", timeout: 10)]
  Catch Timeout:
    [Log("Spinner not detected; checking for result")]
    [WaitForElement("SuccessMessage", timeout: 5)]

Fall back to OCR:
  If element selector fails (Citrix/VDI):
    [WaitForText("Processing...", timeout: 30)]
    [WaitForText("Complete", timeout: 60)]
```

### 3. Application State Mismatch

**Symptom**
```
Logic Error: Automation expects UserID field but sees Login screen
  Frame: [Type "john.doe" into UserID field]
  Error: Field not found; assumption about app state violated
```

**Debugging Steps**
```
1. Add screenshot frames at decision points
   [Screenshot("before_login_check")]
   [If: authenticated == true]
     [Proceed to main screen]
   [Else]
     [Log("Unexpected state: not authenticated")]
     [Screenshot("error_state")]
     [Throw error]
   [Endif]

2. Understand state transitions
   Assumption 1: "After login, user is authenticated"
   Validate: Query app state property (e.g., window title contains username)

3. Add state guards
   [WaitForElement("UsernameLabel")]  ← Proof of authenticated state
   [Click("Logout")]
```

**Common Causes**
| Scenario | Fix |
|----------|-----|
| Unexpected login screen | Previous session logged out; add login step |
| Stale data in fields | Add Clear frame before Type |
| Navigation failed silently | Add WaitForElement after navigation |
| Session timeout mid-automation | Add re-authentication logic |

### 4. Citrix/VDI Issues

**Symptoms**
```
- Clicks not registering
- Text appearing in wrong fields
- Automation "works locally but fails in VDI"
- Intermittent timeouts
```

**Root Causes**
- **Latency**: VDI display refresh lag (300-500ms)
- **Resolution**: Citrix compression; OCR accuracy drops at low res
- **Rendering**: Rich UI elements slow to render over RDP
- **Screenshot**: Only captures compressed VDI stream

**Debugging Workflow**

```
1. Test with slowest settings first
   [WaitForElement(..., timeout: 30)]  ← VDI-sized timeout
   [Wait(1000)]  ← Add 1-second pause between clicks

2. Use OCR as fallback
   Element-based: xpath="//button[@id='submit']"
   Fallback:      OCRText("Submit")

3. Log rendering times
   [Screenshot("before_click")]
   [Wait(500)]  ← Allow VDI to re-render
   [Screenshot("after_click")]
   [AnalyzeScreenshot()]  ← Verify visual state changed

4. Reduce UI complexity
   Disable animations in app settings
   Use text-only mode if available
   Maximize color palette (reduces compression artifacts)

5. Add retry with backoff
   Attempt 1: element-based click
   Attempt 2: (if fail) OCR-based click
   Attempt 3: (if fail) coordinate-based click (last resort)
```

## Robot Manager Monitoring

### Health Dashboard

```
Robot Manager Status Page:
  ├─ Runtime Instances: 8/10 healthy
  ├─ Queued Automations: 42 pending
  ├─ Active Executions: 7 running
  ├─ Failed (last 24h): 3 failures
  ├─ Avg Duration: 8.2 minutes
  └─ Success Rate: 98.4%

Recent Failures:
  1. LoanDocExtractor      [09:15] Timeout
  2. CustomerLookup        [09:08] Element not found
  3. DataExport            [08:52] Credential error
```

### Diagnosing Flaky Automations

**Pattern Analysis**
```
Automation: LoanDocExtractor
  Success Rate: 94% (failing ~6% of time)

Analyze failures:
  - Monday: 98% success (high success)
  - Friday: 88% success (fails more often)
  → Hypothesis: Friday is high-volume; system slower

Solution:
  Increase timeout from 10sec to 20sec
  Add retry logic for Friday runs
  Monitor if success improves to 96%+
```

**Statistical Approach**
```
Track per-execution metrics:
  execution_time: [5.2, 5.8, 6.1, 18.3 ← outlier, 5.9]
  success: [pass, pass, pass, FAIL, pass]

Flag automations with:
  - Success rate < 95% → Investigate
  - Execution time variance > 50% → Timing issues
  - Errors only on specific time/day → Workload-based
```

### Alerting & Escalation

```yaml
Monitor:
  - failure_rate > 5% for 1 hour  → Page RPA team
  - single_failure in critical automation → Immediate alert
  - queue_depth > 200 items → Scale up
  - avg_duration > baseline * 1.5 → Investigate

Actions:
  - Auto-retry once (exponential backoff)
  - Log to RPA troubleshooting queue
  - Notify case worker if related to case
  - Escalate to RPA engineers if pattern emerges
```
"""
    }
]

def seed_phase7():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE7:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase7_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE7)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 7 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase7()
