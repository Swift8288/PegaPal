"""
Curated Pega Knowledge Base — Phase 12 (Digital Experience — Chat, IVA, Knowledge Mgmt)
Run: python -m crawler.seed_kb_phase12
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE12 = [
    {
        "title": "Pega Intelligent Virtual Assistant (IVA) — Chatbot Development",
        "url": "https://pegadocs.example.com/iva-chatbot-development",
        "content": """# Pega Intelligent Virtual Assistant (IVA) — Chatbot Development

## What is Pega IVA?

Pega IVA (Intelligent Virtual Assistant) is a conversational AI platform for building chatbots and virtual agents. It combines natural language processing (NLP), intent recognition, and Pega's workflow automation to create intelligent self-service experiences.

## IVA Architecture

**Core Components:**
- **NLP Engine**: Processes user utterances, extracts intents and entities
- **Dialog Flow Designer**: Creates conversation branches and decision trees
- **Integration Hub**: Connects to Pega case management, external APIs, knowledge bases
- **Channels**: Web chat, Facebook Messenger, WhatsApp, Teams, Slack, SMS
- **Analytics**: Conversation metrics, intent accuracy, escalation rates

**Request Flow:**
```
User Input → Channel Listener → NLP Engine → Intent Match → Dialog Flow →
Action/Response → Knowledge Base/Case Engine → Channel Response
```

## Creating Chatbot Flows

**Steps:**
1. Define intents (e.g., "Check Order Status", "Billing Question", "Complaints")
2. Create entities (named values like order ID, email, phone)
3. Build dialog flows with decision branches
4. Configure actions (query cases, call APIs, create records)
5. Set escalation rules to human agents
6. Test and train the NLP model

**Common IVA Designer Tasks:**
- Use "Dialog Flow" rules to define conversation states
- Create "Response Text" rules for chatbot replies
- Map intents to case types and Pega workflows
- Configure entity extraction patterns

## NLP Model Training

**Best Practices:**
- Provide 10+ training utterances per intent (minimum 5)
- Use varied language and realistic user phrasings
- Test intent accuracy in IVA Designer preview
- Monitor "low confidence" intents in analytics
- Retrain monthly with new conversation data

**Debugging NLP Issues:**
- **Intent Not Recognized**: Add more training utterances, check entity dependencies
- **Wrong Intent Match**: Review utterance overlap, adjust confidence thresholds
- **Entity Extraction Fails**: Verify regex patterns, add context examples
- **Check Logs**: App Studio → IVA → Analytics → Conversation Logs

## Channel Integration

**Web Chat Setup:**
- Deploy web chat widget to page via HTML snippet
- Configure webhook URL in channel settings
- Test in Pega system (Administration → IVA → Channels)

**Messaging Platforms:**
- Generate API tokens in channel provider (e.g., Facebook App, WhatsApp Business API)
- Register webhook URL in provider
- Map inbound message format to Pega request structure

## Escalation to Human Agents

**Triggering Escalation:**
- Intent not understood (confidence < threshold)
- Conversation exceeds turn limit
- User explicitly requests agent (e.g., "speak to human")
- Skill-based routing (e.g., billing issues to billing agents)

**Configuration:**
- Create escalation queue in Pega case management
- Map to CTI system or chat queue
- Log escalation reason in case history

## Debugging Chatbot Conversations

**Key Logs & Monitors:**
- **IVA Trace Log**: Logs intent matching, entity extraction, confidence scores
  - `Pega-RULES > IVA > Trace`
- **Dialog Flow Execution**: Check flow branch logic
  - Enable debug in IVA Designer
- **API Integration Failures**: Review action call responses
  - Alert log for HTTP errors, timeouts

**Common Issues & Solutions:**
| Issue | Cause | Solution |
|-------|-------|----------|
| Chatbot offline | Channel listener down | Check Service Fabric, restart listener |
| Slow responses | API calls timing out | Optimize external queries, increase timeout |
| Wrong responses | Flow logic error | Review flow in Designer, check conditions |
| Message not delivered | Channel auth failed | Verify API token, regenerate if expired |

**Debugging Steps:**
1. Reproduce issue in IVA test widget
2. Capture conversation ID from chat logs
3. Review IVA Trace Log for that ID
4. Check intent confidence scores
5. Verify flow conditions and branch logic
6. Test API integrations independently (Postman)

## Training the NLP Model

**Manual Training:**
- Add utterances directly in IVA Designer
- Flag misunderstood conversations in Analytics
- Mark correct/incorrect intent matches

**Auto-Training (if enabled):**
- System logs accepted and rejected responses
- Model retrains on schedule (hourly/daily)
- Monitor drift in model accuracy

**Tips:**
- Use paraphrases, abbreviations, typos in training data
- Include negative examples (utterances not for this intent)
- Balance training data across intents
- Test model on held-out test set
"""
    },
    {
        "title": "Pega Knowledge Management",
        "url": "https://pegadocs.example.com/knowledge-management",
        "content": """# Pega Knowledge Management

## Overview

Pega Knowledge Management enables organizations to create, organize, and deliver knowledge articles to support customer self-service and agent-assisted interactions. Integrated with Case Management and IVA, knowledge articles reduce case volume and improve resolution times.

## Knowledge Base Architecture

**Components:**
- **Knowledge Articles**: Searchable content (FAQ, how-to, troubleshooting)
- **Categories & Tags**: Taxonomy for organization and discovery
- **Search Engine**: Full-text search with relevance ranking
- **Suggestion Rules**: Context-aware knowledge recommendations
- **Analytics**: Article views, search queries, usage metrics

**Knowledge Lifecycle:**
```
Create → Review/Approve → Publish → Track Usage → Update/Archive
```

## Creating Knowledge Articles

**Article Structure:**
1. **Title**: Clear, keyword-rich (affects search ranking)
2. **Summary**: 1-2 sentence overview
3. **Content**: Detailed steps, screenshots, links
4. **Keywords/Tags**: For search optimization
5. **Category**: Hierarchical organization
6. **Related Articles**: Cross-references

**Best Practices:**
- Use plain language, avoid jargon
- Break into sections with headers
- Include screenshots or diagrams
- Add version/date for tracking
- Test search terms before publishing

**Markdown Support:**
- Headers, bold, italics, lists, links, code blocks
- HTML tags also supported for advanced formatting

## Article Search Integration

**Search Configuration:**
- Pega uses Elasticsearch for knowledge search
- Indexes article title, summary, content, tags
- Configurable relevance boosting (title matches weighted higher)
- Filters: category, status (published/draft), date range

**Improving Search Relevance:**
- Use descriptive titles with common keywords
- Add synonyms in tags (e.g., "login", "sign in", "authentication")
- Monitor search queries in Analytics
- Create articles for frequently searched terms with no results

**Search API:**
```
POST /knowledge/search
{
  "query": "password reset",
  "category": "Account",
  "limit": 10
}
```

## Contextual Knowledge Suggestions

**In Cases:**
- Rule-driven: Suggest articles based on case type, issue category
- NLP-driven: Extract keywords from case notes, suggest matching articles
- Manual: Agent selects "Suggest Knowledge" action

**Configuration:**
- Create "Suggest Knowledge" rules in Case Designer
- Link to knowledge search query (category filters, keywords)
- Display suggestions in Agent UI or Portal

**Common Suggestion Triggers:**
- Case created (based on issue type)
- Notes added (keyword-based)
- Customer provides description

## Knowledge Analytics

**Metrics:**
- **Views**: How many times article read
- **Search Impressions**: How often recommended/searched
- **Click-Through Rate**: Views vs. impressions
- **Helpful Rating**: User feedback (thumbs up/down)
- **Cases Resolved by Article**: Self-service credit

**Usage Dashboard:**
- Top articles by views
- Search queries with no results (gap analysis)
- Article performance trends
- Author/category breakdowns

**Debugging Low Performance:**
- **No views**: Article not discoverable (improve title/tags)
- **Low ratings**: Content unclear (revise article)
- **High bounce rate**: Wrong article recommended (review suggestion rules)

## Integration with IVA

**Chatbot Knowledge Integration:**
- IVA dialog flows call knowledge search API
- Display article snippets or links in chat
- Escalate if article doesn't resolve issue

**Configuration:**
- Create knowledge search action in IVA flow
- Pass extracted entities (e.g., issue type) as filters
- Rank results by relevance, return top 3
- Include article link for full content

## Debugging Knowledge Search Relevance

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Wrong articles ranked first | Title/tag weight mismatch | Adjust Elasticsearch relevance config |
| No results for valid query | Article not indexed | Publish article, check indexing status |
| Irrelevant suggestions | Broad search query | Refine suggestion rule filters |
| Search slow/timeout | Large knowledge base | Add filters (category), optimize query |

**Debugging Steps:**
1. Search for keyword manually in Knowledge Portal
2. Review top results and ranking
3. Check article title/tags match query
4. Monitor Elasticsearch indexing logs
5. Test suggestion rule query in isolation
6. Use Analytics to find missing articles (search with 0 results)

**Knowledge Search Logs:**
- Administration → Monitoring → Alerts & Logs
- Search for "knowledge" or "suggest" actions
- Review response times, error messages
"""
    },
    {
        "title": "Pega Co-Browse",
        "url": "https://pegadocs.example.com/cobrowse",
        "content": """# Pega Co-Browse

## What is Co-Browse?

Co-Browse (or co-browsing) enables an agent and customer to view and navigate the same web page simultaneously during a live interaction. The agent can guide the customer through processes, highlight fields, or take control to complete actions. Essential for high-touch support and onboarding.

## Co-Browse Architecture

**Components:**
- **Co-Browse Engine**: Server managing shared sessions
- **Client-Side Agent**: Injected JavaScript tracking user actions
- **Control Mechanism**: Agent → Customer navigation sync (unidirectional or bidirectional)
- **Session Manager**: Connection pooling, heartbeat, timeout handling
- **Security Layer**: Data masking, encryption, audit logging

**Session Flow:**
```
Customer Page Load → Co-Browse Agent Inject → Agent Request Session →
Server Creates Session → Customer Accepts → Synchronized Browsing
```

## Enabling Co-Browse

**Prerequisites:**
- Co-Browse license enabled in Pega system
- Integration with Chat/Messaging channel
- Supported browser (Chrome, Edge, Safari, Firefox)

**Setup Steps:**
1. **Enable in System**: Administration → Co-Browse → Enable Co-Browse
2. **Configure Channel**: Chat configuration → Enable Co-Browse option
3. **Deploy Script**: Add co-browse JavaScript snippet to target web pages
4. **Set Permissions**: Agent role requires "Co-Browse" permission

**Agent Initiating Co-Browse:**
1. In chat, click "Co-Browse" button
2. System generates unique URL/link
3. Send link to customer via chat
4. Customer clicks link (may require authentication)
5. Agent gains visibility into customer's screen

## Agent-Customer Shared Browsing

**Agent Capabilities:**
- **View-Only**: See customer's screen, mouse cursor, form inputs (read-only)
- **Control**: Agent can click, fill forms, scroll (with customer permission)
- **Highlight**: Draw attention to specific fields or instructions
- **Annotations**: Add visual indicators (arrows, circles, text)
- **Transcription**: Record page content, actions for documentation

**Customer Experience:**
- See agent cursor movements on page
- Receive instructions via chat + visual guidance
- Can interrupt agent control if needed
- Option to reject co-browse request

**Best Practices:**
- Explain co-browse purpose before initiating
- Limit to 15-20 minutes per session (avoid fatigue)
- Take control only when necessary
- Document key actions in case notes

## Masked Fields for Security

**Sensitive Field Types:**
- Passwords, PINs
- Credit card numbers
- Social security numbers
- Bank account numbers
- Healthcare/medical information

**Masking Configuration:**
- **Auto-Masking**: System masks known sensitive fields (input type="password", etc.)
- **Custom Rules**: Define regex patterns for PII (e.g., card numbers: `\d{13,19}`)
- **Visibility Settings**: Mask for agent only, customer only, or both

**Setting Masking Rules:**
```
Administration → Co-Browse → Masking Rules
- Pattern: ^\d{16}$ (credit card)
- Pattern: ^\d{3}-\d{2}-\d{4}$ (SSN)
- Replacement: ****
```

**Testing Masks:**
1. Enable co-browse on test page with sensitive field
2. Verify field displays as masked to agent
3. Confirm customer sees actual value

**Debugging Masking Issues:**
- **Field Not Masked**: Check pattern matches, verify rule is active
- **Over-Masking**: Adjust regex to be more specific
- **Performance Impact**: Masking too many fields can slow sync

## Co-Browse Session Management

**Session Lifecycle:**
1. **Initiate**: Agent requests session, server creates ID
2. **Invite**: Link sent to customer (email, chat, SMS)
3. **Connect**: Customer joins, both sides synchronized
4. **Active**: Bidirectional communication, page sync
5. **End**: Agent or customer terminates (or timeout)

**Timeout Handling:**
- Inactivity timeout (default 30 min): Session auto-closes
- Heartbeat check (every 30 sec): Verifies connection
- Reconnect grace period: 5 min to rejoin if disconnected

**Session Limits:**
- Max co-browse sessions per agent: 5 (configurable)
- Max session duration: 2 hours
- Queued sessions: Auto-clear after 10 min without answer

## Debugging Co-Browse Connection Issues

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Customer can't join | Invalid/expired link | Regenerate, send new link |
| Page not syncing | Network latency, firewall | Check bandwidth, disable VPN/proxy |
| Masked fields visible | Masking rule not applied | Verify rule active, test regex pattern |
| Agent can't take control | Permission missing, JS error | Check agent role, review browser console |
| Session drops frequently | Timeout too short, network unstable | Increase timeout, check connectivity |
| Performance lag | Too many DOM changes | Reduce animations, simplify page |

**Debugging Steps:**
1. **Check Browser Console**: Agent side for JavaScript errors
2. **Network Inspector**: Monitor WebSocket/HTTP requests to co-browse server
3. **Co-Browse Logs**: Administration → Monitoring → Co-Browse Activity
4. **Test Connectivity**: Ping co-browse server from agent, customer network
5. **Verify Permissions**: Agent role includes "Co-Browse" permission
6. **Test with Different Browser**: Rule out browser-specific issues

**Enable Co-Browse Trace:**
- Administration → Diagnostic Tools → Trace
- Filter: "cobrowse"
- Monitor WebSocket handshake, message sync

## Browser Compatibility

**Supported Browsers:**
- Chrome 80+ (full support)
- Edge 80+ (full support)
- Safari 13+ (full support)
- Firefox 75+ (full support)

**Known Limitations:**
- iFrame content may not sync (depends on origin/CORS)
- Flash content not supported
- Some third-party widgets may not track
- Mobile browsers (iOS Safari, Chrome Mobile): Limited control features

**Testing Browser Support:**
1. Test co-browse on each target browser
2. Verify masking works across browsers
3. Check performance on older browser versions
4. Document any browser-specific limitations

**Troubleshooting Specific Browsers:**
- **Safari**: Disable "Prevent cross-site tracking", allow notifications
- **Firefox**: Enable WebSocket, check mixed content (HTTP vs HTTPS)
- **Chrome**: No special configuration needed
- **Mobile**: Use responsive design, test on actual devices
"""
    },
    {
        "title": "Pega Email Bot — Intelligent Email Processing",
        "url": "https://pegadocs.example.com/email-bot",
        "content": """# Pega Email Bot — Intelligent Email Processing

## Overview

Pega Email Bot automatically processes incoming customer emails, extracts key information (customer name, issue type, attachments), classifies emails into case types, and initiates appropriate workflows. Reduces manual email triage and accelerates case creation.

## Email Bot Architecture

**Components:**
- **Email Listener**: Monitors inbox, retrieves new emails
- **NLP Engine**: Parses email body, extracts entities
- **Classification Model**: Predicts case type/priority based on content
- **Entity Extractor**: Identifies customer ID, account, dates, amounts
- **Auto-Triage Rules**: Route to appropriate queue/assignee
- **Suggested Response Engine**: AI-generated reply templates
- **Integration Hub**: Link to case management, ticketing system

**Email Processing Flow:**
```
Email Received → Listener Capture → Body Parse → Entity Extract →
Classification → Case Type Prediction → Create Case → Route → Reply Template
```

## Email Bot Configuration

**Setup Steps:**
1. **Configure Email Listener**:
   - Email account (mailbox, IMAP/Exchange settings)
   - Connection credentials (OAuth or password)
   - Check frequency (e.g., every 5 minutes)

2. **Create Classification Model**:
   - Define case types (Support, Billing, Complaint, etc.)
   - Provide training emails for each type
   - Configure confidence threshold

3. **Define Entity Extractors**:
   - Customer ID patterns (regex)
   - Order/ticket number format
   - Date/amount extraction rules

4. **Set Auto-Triage Rules**:
   - Route by case type, priority, customer segment
   - Assign to queue or specific agent

5. **Enable Suggested Responses**:
   - Build response templates
   - Link to case type

## Automatic Email Classification

**How Classification Works:**
- Email body text passed to ML model
- Model predicts case type with confidence score
- Confidence > threshold: Auto-create case
- Confidence < threshold: Flag for manual review

**Case Types & Examples:**
- **Tech Support**: "I can't log in", "App crashes", "Connection issues"
- **Billing**: "Invoice wrong", "Charge not authorized", "Request refund"
- **Complaint**: "Poor service", "Unhappy with product", "Missed deadline"
- **Sales Inquiry**: "Pricing question", "Feature availability", "Demo request"

**Training Classification Model:**
1. Collect 50-100 emails per case type
2. Label emails with correct case type
3. Run training job (Administration → Email Bot → Train Classifier)
4. Review model accuracy on test set
5. Adjust threshold for precision vs. recall trade-off

**Debugging Classification Issues:**
- **Low Accuracy**: Add more training examples, use domain-specific keywords
- **Slow Training**: Reduce feature dimensionality, use smaller model
- **Too Many Manual Reviews**: Lower confidence threshold, but risk more misclassifications

## Entity Extraction from Emails

**Common Entities:**
- **Customer**: Name, ID, email, phone
- **Account**: Account number, segment, VIP status
- **Issue**: Order ID, product, error code
- **Dates/Times**: Incident date, needed by date
- **Monetary**: Amount, currency, pricing

**Extraction Methods:**
- **Regex-Based**: Pattern matching for structured data (e.g., "Order #\d{8}")
- **NLP-Based**: Token classification for free-form text (e.g., "my name is John Smith")
- **Rule-Based**: Custom logic (e.g., extract between phrases: "Reference:" and "Date:")

**Configuration Example:**
```
Entity: Order ID
Pattern: Order[_ #]{0,2}(\d{8,10})
Capture Group: $1
```

**Testing Extraction:**
1. Provide sample emails
2. Verify extracted entities match ground truth
3. Check false positive/negative rates
4. Adjust patterns or train NLP model

## Auto-Triage to Case Types

**Routing Rules:**
```
IF Case Type = "Billing" AND Amount > $1000 THEN Route to Billing Lead
IF Case Type = "Complaint" THEN Route to Complaints Queue + Escalate
IF Customer Segment = "VIP" THEN High Priority, Route to Specialist
```

**Priority Determination:**
- Keywords (urgent, ASAP, critical) → High
- Amount (>$10k) → High
- VIP customer → High
- Default → Medium

**Queue Assignment:**
- Create email processing queues (Tech Support, Billing, etc.)
- Assign agents to queues
- Configure auto-assignment rules (round-robin, skill-based)

## Suggested Responses

**Response Template System:**
- Store common response templates per case type
- Use dynamic placeholders: `{CustomerName}`, `{OrderID}`, `{DueDate}`
- Generate variations based on sentiment/priority

**Generating Suggestions:**
1. Classification identifies case type
2. System retrieves matching templates
3. Agent reviews, edits, sends
4. Response logged in case history

**Example Templates:**
- Tech Support: "Hi {Name}, thanks for reporting the issue. We've created ticket #{ID}. ETA for fix: {Date}."
- Billing: "Hi {Name}, we've processed your refund of {Amount}. Check your account in 1-2 business days."

**Customizing Suggestions:**
- Edit templates in Administration → Email Bot → Response Templates
- Add sentiment-based variants (angry customer vs. neutral)
- Include links to knowledge articles

## Training the Email Model

**Supervised Training:**
1. Collect labeled email dataset
2. Preprocess: Tokenize, normalize, remove stopwords
3. Feature extraction: TF-IDF, word embeddings
4. Train classifier (Naive Bayes, SVM, neural net)
5. Evaluate on test set

**Continuous Learning:**
- Monitor predicted vs. actual case types
- Flag low-confidence predictions
- Agent corrections fed back to model
- Monthly retraining with new data

**Data Quality Issues:**
- **Spam/Noise**: Filter non-customer emails pre-training
- **Imbalanced Data**: Over-sample minority classes
- **Typos/Abbreviations**: Use robust tokenization, fuzzy matching

**Model Performance Metrics:**
- Precision: % of predicted cases that were correct
- Recall: % of actual cases that were predicted
- F1-Score: Harmonic mean (balanced metric)
- Confusion Matrix: Understand misclassifications

## Debugging Email Bot Accuracy

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Low classification accuracy | Insufficient training data, poor examples | Add more emails, improve label quality |
| Entity not extracted | Regex pattern too strict | Generalize pattern, test variations |
| Wrong case type | Model overfitting to training data | Simplify model, add regularization |
| Slow processing | Heavy email volume, slow classification | Optimize model, increase listener frequency |
| Missed emails | Listener not connecting | Check email account creds, IMAP/Exchange settings |
| Suggested responses irrelevant | Template mismatch | Create more case type specific templates |

**Debugging Steps:**
1. **Check Email Listener Logs**:
   - Administration → Monitoring → Email Listener Activity
   - Verify emails captured, check error messages

2. **Review Classification Results**:
   - Administration → Email Bot → Classification Logs
   - Filter by date, case type, confidence
   - Compare predicted vs. actual

3. **Entity Extraction Testing**:
   - Administration → Email Bot → Entity Extraction
   - Test patterns on sample email
   - View matched entities

4. **Retrain Model**:
   - Collect recent mislabeled emails
   - Add to training set, retrain
   - Compare new accuracy to baseline

5. **Monitor Case Creation**:
   - Check case logs for auto-created cases
   - Verify case type, routing, field population
   - Identify patterns in failures

## Integration with Email Listeners

**Email Listener Setup:**
- Account: Email mailbox address, provider (Gmail, Outlook, Exchange)
- Authentication: OAuth token or password (use service account)
- Check Frequency: Balance responsiveness vs. API rate limits
- Attachment Handling: Download, scan for virus, store in case

**Data Flow:**
1. Listener retrieves emails (IMAP/Exchange API)
2. Email Bot processes each email
3. Case automatically created (if confidence high enough)
4. Case linked to email, attachments stored
5. Auto-reply sent to customer (optional)

**Error Handling:**
- Connection failures → Retry with exponential backoff
- Invalid email format → Log, skip
- API rate limit → Queue for later retry
- Large attachments → Compress or skip if > 50MB
"""
    },
    {
        "title": "Pega Customer Service Application",
        "url": "https://pegadocs.example.com/customer-service-app",
        "content": """# Pega Customer Service Application

## Overview

Pega Customer Service (CS) Application provides a unified platform for managing customer interactions across multiple channels (phone, email, chat, social). Features include case management, agent workspace, omni-channel routing, and service-level management (SLA).

## CS Application Framework

**Architecture:**
- **Case Management Engine**: Lifecycle for customer issues
- **Agent Workspace**: Unified interface for agents
- **Interaction Portal**: Customer self-service and case tracking
- **Routing Engine**: Intelligent case distribution
- **Analytics**: Agent performance, SLA compliance, customer satisfaction

**Application Structure:**
```
Organization → Business Unit → Service Type → Case Type → Case Instance
```

**Default Case Types:**
- Support Request (Technical issues, how-to questions)
- Complaint (Service failures, product issues)
- Billing Issue (Charges, refunds, subscriptions)
- Order Inquiry (Tracking, modifications)
- Feature Request (Product enhancement)

## CS Application Framework Setup

**Configuration:**
1. **Define Organization Hierarchy**:
   - Organization → Regional Office → Department → Team
   - Controls visibility, routing, reporting

2. **Configure Service Types**:
   - Category of support offered (Tech, Billing, Sales, etc.)
   - Maps to business capabilities, SLAs

3. **Create Case Types**:
   - Define under service type
   - Set priority rules, required fields, routing

4. **Build Case Workflows**:
   - Stages: New → Open → Resolved → Closed
   - Actions per stage (escalate, hold, reassign)
   - Automatic actions (send email, create task)

5. **Set Up SLAs**:
   - First response time (e.g., 4 hours)
   - Resolution time (e.g., 48 hours)
   - Set goals per case type, priority

## Interaction Portal

**Customer Capabilities:**
- **Create Case**: Self-service issue submission
- **Track Case**: View status, history, expected resolution
- **Provide Feedback**: Rate agent, satisfaction survey
- **Knowledge Search**: Access knowledge base
- **Chat with Agent**: Initiate live chat
- **Manage Preferences**: Contact info, notification settings

**Portal Configuration:**
- Customize portal theme (colors, logo, layout)
- Enable/disable features per organization
- Set visibility rules (customers see own cases only)
- Configure email notifications

**Best Practices:**
- Keep portal simple, minimal fields on case creation
- Provide immediate confirmation and tracking number
- Show realistic SLA expectations
- Offer self-service alternatives (knowledge, FAQs)

## Case Management for Service

**Case Lifecycle:**

| Stage | Typical Duration | Actions |
|-------|------------------|---------|
| New | Minutes | Validate, auto-classify, route |
| Open | Hours/Days | Agent investigation, customer comm |
| Pending | As needed | Waiting for customer, external info |
| Resolved | Minutes | Apply solution, verify with customer |
| Closed | N/A | Archive, feedback collection |

**Agent Capabilities:**
- **Create/Update Case**: Modify status, priority, fields
- **Work Queue**: View assigned cases, reorder by priority
- **Collaboration**: Add notes, @mention colleagues, escalate
- **Documentation**: Attach emails, files, screenshots
- **Search**: Find related cases, customer history
- **Tasks**: Create subtasks, set reminders

**Case Fields:**
- **Automatic**: ID, Created Date, Created By
- **Standard**: Subject, Description, Priority, Category
- **Custom**: Product, Account, Order Number, etc.
- **System**: Status, Owner, Resolution Time, SLA

## CTI Integration (Call Center)

**Computer Telephony Integration** connects phone system with Pega.

**Features:**
- **Screen Pop**: Customer info displays when call arrives
- **Automatic Case**: Create case from call metadata (caller ID, reason)
- **Call Recording**: Link recording to case
- **Wrap-Up Codes**: Post-call reason, disposition
- **Dial Out**: Agent click-to-call from case
- **Call Transfer**: Route call to different agent, queue

**CTI Setup:**
1. **Configure PBX Integration**:
   - PBX system (Avaya, Genesys, Cisco, etc.)
   - API credentials, webhook URL
   - Caller ID, called number mapping

2. **Agent Configuration**:
   - Assign CTI extension to agent
   - Enable click-to-call permission
   - Configure auto-case creation rules

3. **Phone Number Matching**:
   - Create reverse phone lookup rules
   - Match to customer account, previous cases
   - Display customer profile on screen pop

**Debugging CTI:**
- **No Screen Pop**: Check phone number lookup config, test regex
- **Call Recording Link Missing**: Verify PBX sends recording ID, map to case
- **Wrap-Up Code Not Logged**: Check agent completes code before release
- **Click-to-Dial Not Working**: Verify extension configured, check permission

## Omni-Channel Routing

**Channels Supported:**
- Phone (via CTI)
- Email (via Email Listener)
- Chat (via Chat widget)
- Social (Twitter, Facebook)
- SMS (via SMS gateway)

**Unified Routing Engine:**
- All interactions (phone, email, chat) treated as cases
- Single queue, distributed across team
- Agent skills/availability considered
- Customer history & context retrieved automatically

**Routing Configuration:**
```
IF Channel = Phone THEN Route to Phone Queue
IF Channel = Chat AND Queue Full THEN Offer Callback
IF Customer VIP THEN Route to Specialist Group
IF Case Type = Billing AND Amount > $10K THEN Escalate Manager
```

**Agent Workspace:**
- Single inbox for all cases (email, chat, phone)
- Display customer context (account, history, preferences)
- Switch between cases without re-context
- Real-time notification of incoming cases

**Best Practices:**
- Balance workload across channels
- Prioritize high-value customers, escalations
- Route to agent with previous case experience
- Monitor queue depth, offer callbacks if wait > 5 min

## Wrap-Up Codes

**Purpose:** Classify work reason post-interaction for analytics and training.

**Common Codes:**
- **Technical**: Resolved (tech), Resolved (self-service), Pending customer
- **Billing**: Resolved (billing), Escalated finance, Pending invoice
- **Complaint**: Resolved (apology), Pending manager approval, Escalated
- **Quality**: Follow-up call needed, Refer to specialist

**Configuration:**
- Administration → Service Configuration → Wrap-Up Codes
- Define code name, category, required/optional
- Require agent selection before release (no default)

**Tracking Wrap-Up:**
- Log code in case record
- Use for agent quality evaluation
- Analytics: % calls by wrap-up reason
- Identify training opportunities (high "pending" = gaps)

**Debugging Issues:**
- **Agents Skip Code**: Make mandatory, add timeout warning
- **Same Code for Everything**: Provide more granular options
- **Wrong Code Selected**: Add context-sensitive suggestions

## SLA Management for Service

**SLA Definition:**
```
Case Type: Support Request | Priority: High
First Response: 2 hours
Full Resolution: 24 hours
```

**Tracking:**
- SLA timer starts when case created
- Paused when waiting for customer response
- Resets if priority changes
- Escalated if approaching deadline

**SLA Metrics:**
- **Met**: Resolved within target (green)
- **At Risk**: Within 10% of deadline (yellow)
- **Breached**: Exceeded target (red)

**Escalation Rules:**
- At Risk (5 hours remaining): Email manager
- Breached: Alert director, require manager approval to close

**SLA Dashboard:**
- % Cases Met SLA (by type, team, agent)
- Avg. resolution time vs. target
- At-Risk cases (need intervention)
- Breached cases (post-mortem analysis)

**Best Practices:**
- Set realistic SLA targets (historical data)
- Allow exceptions for complex issues
- Monitor at-risk cases proactively
- Use SLA breaches for process improvement

## Common CS Application Debugging

**Issue: Cases Not Routing**
- Check routing rule conditions
- Verify queue exists, not disabled
- Review skill/availability filter
- Check agent role permissions

**Issue: Screen Pop Not Working**
- Validate customer phone lookup rule
- Test regex pattern on sample numbers
- Check PBX integration active
- Verify case auto-creation enabled

**Issue: SLA Not Triggering**
- Confirm SLA rule created and active
- Check case meets criteria (type, priority)
- Verify timer starts on expected event
- Review escalation rule threshold

**Issue: Omni-Channel Case Duplication**
- Check routing rules (may create duplicate email+chat)
- Link related cases manually or auto-merge rule
- Review email listener for duplicate emails
- Test chat channel assignment

**Debugging Steps:**
1. **Check Case Logs**:
   - Case record → History tab
   - Review creation, routing, SLA events

2. **Monitor Routing**:
   - Administration → Monitoring → Routing Activity
   - Filter by case type, check distribution
   - Identify rule that didn't fire

3. **Review SLA Logs**:
   - Administration → SLA Monitoring
   - Check SLA rule evaluation
   - Monitor pause/resume events

4. **Test Rules in Isolation**:
   - Use Rule Debugger (Administration → Tools)
   - Simulate case creation, check routing
   - Step through rule logic

5. **Check Agent Setup**:
   - Verify agent enabled, queue assigned
   - Check skill tags, availability
   - Confirm permission set includes case type
"""
    }
]

def seed_phase12():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE12:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase12_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE12)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 12 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase12()
