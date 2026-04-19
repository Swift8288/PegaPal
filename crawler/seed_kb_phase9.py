"""
Curated Pega Knowledge Base — Phase 9 (AI, Decisioning & Customer Decision Hub)
Run: python -m crawler.seed_kb_phase9
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE9 = [
    {
        "title": "Prediction Studio Deep Dive",
        "url": "https://docs.pega.com/bundle/platform/page/prediction-studio.html",
        "content": """
# Prediction Studio Deep Dive

## Overview
Prediction Studio is Pega's native environment for building, testing, deploying, and monitoring machine learning models. It provides end-to-end ML lifecycle management without requiring data science expertise.

## Types of Models

### Adaptive Models
- **Self-learning**: Continuously update from customer feedback
- **Algorithm**: Naive Bayes classifier
- **Use case**: Real-time behavior prediction (propensity, next-best-action)
- **No retraining required**: Model improves automatically

### Predictive Models
- **Static**: Trained once, deployed as-is
- **Algorithms**: Decision trees, gradient boosting, logistic regression
- **Use case**: Complex business rules, high-volume predictions
- **Requires retraining**: Manual process when performance degrades

## Model Lifecycle

### Build Phase
1. Select predictor variables (customer attributes, transaction history)
2. Define target outcome (conversion, churn, propensity)
3. Configure binning/discretization for continuous variables
4. Train on historical data
5. Validate with holdout test set

### Test Phase
- Run against test dataset
- Review lift charts, gain charts, ROC curves
- Compare model performance vs. baseline
- Identify under/overperforming segments

### Deploy Phase
- Publish model to Decision Rules
- Integrate into case/flow rules
- Configure fallback behavior
- Set up monitoring dashboards

### Monitor Phase
- Track prediction accuracy over time
- Monitor model decay (performance degradation)
- Create alerts for threshold violations
- Schedule retraining if accuracy drops > 10%

## Model Decay & Retraining

**Common Causes**:
- Customer behavior shifts
- Business policy changes
- Data quality degradation
- Seasonal variations

**Detection**:
- Monitor actual vs. predicted outcomes
- Calculate population shift metrics
- Set up automated alerts in Analytics

**Resolution**:
- Re-run model training with fresh data
- Adjust predictor variables
- Consider ensemble approaches
- Review business rules vs. model conflicts

## Common Issues & Debugging

**Issue**: Model predictions not appearing in case
- Check: Is model published to Decision Rules?
- Check: Are required predictors available in case?
- Check: Model confidence threshold settings

**Issue**: Very high/low prediction confidence
- Cause: Sparse historical data, imbalanced outcomes
- Fix: Increase training dataset, adjust binning strategy

**Issue**: Model decay detected
- Check: Data pipeline integrity, predictor data quality
- Check: Has customer behavior fundamentally changed?
- Fix: Retrain with recent data, update predictor set

**Performance Bottleneck**:
- Prediction Studio = batch analysis tool, not real-time
- For real-time: Use Adaptive Models or cache predictions
- Optimize predictor queries, consider materialized views
"""
    },
    {
        "title": "Next Best Action (NBA) — Complete Guide",
        "url": "https://docs.pega.com/bundle/platform/page/nba-framework.html",
        "content": """
# Next Best Action (NBA) — Complete Guide

## NBA Framework Overview

Next Best Action is Pega's intelligent recommendation engine that determines the optimal action (offer, message, channel) for each customer interaction in real-time.

### Core Components

1. **Strategies**: Decision logic that ranks actions by effectiveness
2. **Actions**: Offers, messages, content pieces to recommend
3. **Arbitration**: Selection algorithm (propensity, priority, context weighting)
4. **Channels**: Delivery mechanisms (email, SMS, app, web)
5. **Engagement Policies**: Frequency/timing rules

## Strategy Design in NBA Designer

### Step 1: Define Treatment Groups
- Create audience segments (high-value, at-risk, new customers)
- Use customer attributes, analytics scores, segmentation

### Step 2: Configure Actions
- **Offer actions**: Product recommendations, discounts
- **Treatment actions**: Service improvements, retention offers
- **Content actions**: Educational material, case resolution steps
- Assign baseline propensity/priority scores

### Step 3: Set Up Arbitration Rules
- **Propensity-based**: Predict likelihood of customer response
- **Priority-based**: Business importance of action
- **Context weighting**: Situational modifiers (time, channel, intent)
- Combined scoring: `Final Score = (Propensity × 0.5) + (Priority × 0.3) + (Context × 0.2)`

### Step 4: Configure Channels
- Map actions to available channels
- Set channel preferences per customer
- Define fallback logic if primary channel unavailable

## Testing & Debugging NBA

### Test in NBA Designer
1. Create test audience segment
2. Run strategy simulation (100-1000 customers)
3. Review top recommended actions, scores, arbitration results
4. Verify action ranking matches business logic

### Enable NBA Logging
```
Logging: Pega-IntegrationEngine level DEBUG
Monitor: PegaRULES log for strategy execution traces
```

### Common NBA Issues

**Issue**: Same action recommended to all customers
- Cause: Propensity scores not calculated or all uniform
- Fix: Verify predictive models are active, propensity rules configured

**Issue**: Wrong action prioritized despite high propensity
- Cause: Priority/context weighting skewing results
- Fix: Review arbitration rules, test with different weightings

**Issue**: No actions recommended (empty result)
- Cause: Engagement/contact policies suppressing all actions
- Fix: Check suppression rules, policy constraints, customer history

**Issue**: NBA response latency > 1 second
- Cause: Strategy complexity, model scoring, many actions
- Fix: Reduce action set, simplify propensity logic, cache results

## Engagement & Contact Policies

**Engagement Policies**: Control when/how often to engage customer
- Max touches per week/month
- Action frequency per customer segment
- Channel rotation rules

**Contact Policies**: Business compliance rules
- Opt-out/preference management
- DNC lists, TCPA compliance
- Time windows (no weekend/night contact)
"""
    },
    {
        "title": "Adaptive Models — Self-Learning AI in Pega",
        "url": "https://docs.pega.com/bundle/platform/page/adaptive-models.html",
        "content": """
# Adaptive Models — Self-Learning AI in Pega

## How Adaptive Models Work

Adaptive Models are machine learning models that continuously improve by learning from real customer behavior without manual retraining. They use Naive Bayes algorithm for binary classification.

### Key Characteristics
- **Self-updating**: Learn from feedback automatically
- **Real-time**: Available immediately for decisioning
- **Low maintenance**: No data scientist required
- **Explainable**: Clear predictor-outcome relationships

## Naive Bayes Algorithm in Pega

Adaptive Models use multinomial Naive Bayes classifier:
```
P(Outcome|Predictors) = P(Outcome) × P(Predictor1|Outcome) × P(Predictor2|Outcome) × ...
```

**Advantages**:
- Fast, memory-efficient
- Works well with limited data
- Handles missing values gracefully

**Limitations**:
- Assumes predictor independence (often unrealistic)
- May underperform vs. gradient boosting on complex patterns
- Requires sufficient feedback for reliable updates

## Predictor Binning & Model Maturity

### Binning (Discretization)
- Continuous variables (age, income) are grouped into bins
- Pega auto-bins: equal-width, equal-frequency, or decision-tree-based
- Bins allow Naive Bayes to learn relationships efficiently

### Model Maturity Levels

| Level | Feedback Count | Reliability | Action |
|-------|----------------|-------------|--------|
| 0-100 | Insufficient | Very Low | Use baseline scores |
| 100-500 | Growing | Low | Monitor closely |
| 500-2000 | Good | Medium | Begin relying on model |
| 2000+ | Strong | High | Full deployment |

**Check maturity**: Analytics > Adaptive Models > Model Performance > Feedback Count

## Feedback Loop & Customer Response Capture

### Recording Feedback
Feedback **must be captured explicitly** in Decision Rules or case completion:
```
When customer acts on recommendation:
  Call: Decision Model > Record Feedback
  Outcome: SUCCESS / FAILURE / NEUTRAL
```

### No Feedback = No Learning
- If feedback not recorded: model never updates
- **Common mistake**: Assuming feedback happens automatically
- **Fix**: Create explicit feedback logging in case completion rules

### Feedback Best Practices
1. Record outcome **immediately** after customer action
2. Use consistent outcome categories
3. Exclude invalid feedback (system errors, test cases)
4. Monitor feedback data quality

## Adaptive vs. Predictive Models: When to Use

| Aspect | Adaptive | Predictive |
|--------|----------|-----------|
| Learning | Continuous | Manual retraining |
| Setup Time | Days | Weeks |
| Accuracy | Good (eventually) | Potentially higher |
| Scale | < 10M decisions/month | High volume |
| Use Case | Real-time scoring, NBA | Complex patterns, batch |

## Model Performance Reports

**Key Metrics**:
- **Accuracy**: % of correct predictions
- **Lift**: Model performance vs. random baseline
- **Feedback Count**: How many outcomes recorded
- **Model Decay**: Accuracy degradation over time

**Access**: Prediction Studio > Models > Reports

## Common Issues & Debugging

**Issue**: Model accuracy very low initially
- **Expected**: Adaptive models need 100+ feedback samples
- **Timeline**: Typically improves significantly after 500+ samples

**Issue**: Model not updating despite feedback recorded
- Check: Is feedback being committed to database?
- Check: Feedback outcome values match model definition?

**Issue**: Accuracy plateau or decay
- Check: Customer behavior changed?
- Check: Feedback quality degraded (gaming, test records)?
- Fix: Manual retrain or retire model

**Performance**: Model predictions causing case delays
- Adaptive models use pre-calculated probability tables (fast)
- If slow: Check database load, consider model refresh frequency
"""
    },
    {
        "title": "Customer Decision Hub (CDH) — Architecture & Configuration",
        "url": "https://docs.pega.com/bundle/platform/page/customer-decision-hub.html",
        "content": """
# Customer Decision Hub (CDH) — Architecture & Configuration

## CDH Overview

Customer Decision Hub is Pega's unified platform for real-time, always-on customer decisioning. It orchestrates interactions across channels and ensures consistent, optimized customer experience.

### Core Functions
- **Real-time inbound decisioning**: When customer initiates (web, call, app)
- **Always-on outbound**: Proactive recommendations (email, SMS campaigns)
- **Event-driven actions**: Triggered by business events
- **Personalization**: Per-customer offer, content, timing

## Real-Time Decisioning Architecture

### Inbound Interaction Flow
```
Customer Action → NBA Strategy Evaluation → Predict Propensity →
Arbitrate Actions → Apply Engagement Policies → Deliver Experience
```

**Latency**: Typical < 200ms for single-customer decisions

### Always-On Outbound
- **Batch mode**: Nightly/scheduled NBA execution for audiences
- **Configuration**: Strategy, frequency cap, suppression rules
- **Output**: Action queue fed to email/SMS/push systems

## Event Strategies & Triggers

**Events** feed CDH with real-time signals:
- Customer purchases, returns, support interactions
- Account milestones (anniversary, renewal date)
- External events (market data, competitor actions)

**Event Strategy**:
1. Define event type (OrderPlaced, SupportTicket)
2. Set event conditions (product category, region)
3. Map to NBA strategy or business action
4. Configure contact policy enforcement

## Engagement Policies Configuration

### Frequency Caps
```
Max Interactions per Customer:
  - Per Week: 5 (all channels)
  - Per Day: 2 (email only)
  - Per Channel: SMS max 2/week, email max 10/week
```

**Implementation**: Policy rule evaluates before action delivery

### Contact Policies
- **Quiet hours**: No contact 9pm-8am
- **Channel preferences**: Customer selects delivery method
- **Opt-out management**: DNC list integration
- **Compliance**: GDPR, CCPA, TCPA

### Suppression Rules
- Don't offer current product to customer (owns it)
- Don't contact high-churn-risk without special approval
- Skip action if customer recently received similar offer
- Exclude test/internal accounts

## Channel Limits & Configuration

**Multi-channel decisioning**:
- **Email**: 1-10/week (configurable per segment)
- **SMS**: 1-3/week (regulatory limits)
- **Mobile App**: Unlimited (customer-controlled)
- **Web**: Real-time, personalized experience
- **Outbound Call**: 1-2/week (contact policy)

**Channel Prioritization**:
1. Customer preference (stored in profile)
2. Engagement channel limit status
3. Action channel requirements
4. Fallback to secondary channel if primary unavailable

## CDH Configuration Checklist

- [ ] Customer profiles loaded with attributes, segments
- [ ] NBA strategies designed and tested
- [ ] Propensity models built/trained (Prediction Studio)
- [ ] Actions/treatments configured with channels
- [ ] Engagement policies defined and published
- [ ] Contact policies reviewed for compliance
- [ ] Suppression rules defined
- [ ] Event streams configured (if event-driven)
- [ ] Channel connectors active (email SMTP, SMS gateway)
- [ ] Monitoring dashboards created

## Common CDH Issues & Debugging

**Issue**: No actions recommended in real-time
- Check: Is NBA strategy active/published?
- Check: Are engagement policies over-suppressing?
- Check: Does customer meet any treatment criteria?

**Issue**: Same action to all customers
- Check: Are propensity models calculating?
- Check: Predictor data available in customer profile?
- Check: Model confidence above threshold?

**Issue**: Actions not being delivered to channels
- Check: Channel connector health (email queue, SMS gateway)
- Check: Customer contact preferences/opt-out status
- Check: Action has channel assignment

**Issue**: Engagement policy limits not respected
- Check: Policy SQL query executing correctly
- Check: Frequency counts accurate in database
- Check: Interaction history being recorded

**Performance Issues**:
- NBA strategy evaluation < 200ms → check: model/rule complexity
- Channel delivery > 30 seconds → check: gateway/queue health
- Solution: Cache decisions, use batch outbound for scale
"""
    },
    {
        "title": "Text Analytics & NLP in Pega",
        "url": "https://docs.pega.com/bundle/platform/page/text-analytics.html",
        "content": """
# Text Analytics & NLP in Pega

## Text Analytics Overview

Pega's Text Analytics engine extracts insights from unstructured text: customer emails, chat messages, case notes, feedback. It uses NLP (Natural Language Processing) to identify entities, sentiment, topics, and categorize content.

## Core Text Analytics Features

### Entity Extraction
Automatically identifies and tags:
- **People**: Customer names, employee names
- **Organizations**: Company names, institutions
- **Locations**: Cities, countries, regions
- **Dates/Times**: Appointment dates, deadlines
- **Products**: Product names, SKUs
- Custom entities (defined by business rules)

### Topic Detection
- Identifies dominant topics in text
- Uses LDA (Latent Dirichlet Allocation) or TF-IDF
- Example: "Shipping problem" detected in support email
- Maps topics to case categories, routing rules

### Sentiment Analysis
Classifies text emotional tone:
- **Positive**: "Your service is excellent!"
- **Negative**: "I'm very disappointed with the product"
- **Neutral**: "Confirming receipt of order"

**Confidence scores**: 0-100% for each sentiment class

### Text Categorization
Multi-label classification:
- Email → {Billing, Complaint, Product-Inquiry}
- Chat message → {Question, Feedback, Bug-Report}
- Auto-routes to appropriate queue/specialist

## Text Extractor & Analyzer Rules

### Text Extractor Rule
Extracts text from various sources:
```
Source: Email message body, attachment content
Extract: Clean, relevant text only
Filter: Remove signatures, disclaimers, HTML
Output: Standardized text property
```

### Text Analyzer Rule
Runs extraction pipeline:
```
Input Text → Tokenization → Part-of-Speech Tagging →
Entity Recognition → Topic/Sentiment Detection → Output Results
```

## Email Triage with NLP

**Workflow**:
1. Email arrives in mailbox
2. Extract subject + body
3. Run Text Analyzer
4. Detect sentiment, topic, entities
5. Auto-assign priority (negative sentiment → high priority)
6. Route to specialist queue (topic-based)
7. Pre-populate case with extracted data (customer name, product)

**Benefits**:
- 50-70% reduction in manual triage time
- Improved first-response time
- Better SLA compliance

## Configuring Text Analyzers

### Step 1: Define Analyzer Properties
```
Name: "Customer Sentiment Analyzer"
Language: English (supports 10+ languages)
Entities: Customer, Product, Emotion
Topics: {Support, Billing, Feature-Request}
```

### Step 2: Train (if custom model)
- Provide labeled examples (text + expected output)
- Typical training set: 100-500 labeled samples
- Pega trains classification model automatically

### Step 3: Deploy
- Create Decision Rule that calls Text Analyzer
- Integrate into email/chat intake rules
- Set confidence thresholds (0-100%)

### Step 4: Monitor
- Track extraction accuracy vs. manual review
- Collect feedback for continuous improvement
- Retrain if accuracy < 80%

## Text Analytics Best Practices

1. **Clean input text**: Remove irrelevant sections (signatures, legal notices)
2. **Define clear entities**: More specific = better accuracy (e.g., "Product SKU" vs. generic "Product")
3. **Use confidence thresholds**: Only trust high-confidence (>80%) predictions
4. **Fallback rules**: For low-confidence cases, escalate to human review
5. **Regular retraining**: Add new examples, address drift
6. **Monitor data quality**: Watch for encoding issues, unexpected formats

## Common Issues & Debugging

**Issue**: Entity extraction missing obvious entities
- Cause: Custom entity not trained, or low training sample size
- Fix: Provide 50+ labeled examples, retrain model

**Issue**: High false-positive sentiment (neutral → negative)
- Cause: Sparse training data, sarcasm/context issues
- Fix: Add more training examples with context, adjust confidence threshold

**Issue**: Email categorization wrong
- Cause: Ambiguous categories, overlapping definitions
- Fix: Refine category definitions, add distinguishing training examples

**Issue**: Text Analyzer rule slow (>500ms)
- Cause: Rule runs on every character entered (no debouncing)
- Fix: Trigger analyzer only on form submission, not keystroke

**Issue**: Special characters breaking extraction
- Cause: Encoding mismatch, non-ASCII characters
- Fix: Ensure UTF-8 encoding, strip non-ASCII if needed

## Text Analytics Performance Tips

- Cache analyzer results for frequently-seen text (identical emails)
- Run on background thread for non-blocking UX
- Pre-filter spam before text analysis (saves compute)
- Use rule caching to avoid re-analyzing same content
"""
    },
    {
        "title": "Event Strategies & Triggers",
        "url": "https://docs.pega.com/bundle/platform/page/event-strategies.html",
        "content": """
# Event Strategies & Triggers

## Event Strategy Manager

Event Strategies enable real-time customer decisioning triggered by external events. When a business event occurs, it automatically invokes NBA or other actions without waiting for customer interaction.

### Event Strategy Flow
```
External System → Pega Event Adapter → Event Rule Evaluation →
Condition Check → Trigger Decision Rule (NBA, Policy, etc.) → Action Execution
```

## Defining Event Sources

### Event Types (from External Systems)
- **E-commerce**: OrderPlaced, PaymentFailed, ItemShipped
- **Banking**: DepositReceived, LoanApproved, FraudAlert
- **Telecom**: SubscriptionCanceled, BillNonpayment, DataOverage
- **Insurance**: ClaimFiled, PolicyRenewed, QuoteExpired

### Integration Methods

**1. REST API**
```
POST /pega/prweb/events
Body: {
  "eventType": "OrderPlaced",
  "customerId": "C123456",
  "orderId": "O789",
  "amount": 99.99,
  "timestamp": "2026-04-16T10:30:00Z"
}
```

**2. Messaging Queue** (Kafka, MQ Series)
- Async, high-volume event processing
- Built-in retry and dead-letter handling

**3. File Drop**
- Batch event import via SFTP/file system
- Scheduled polling

**4. Web Services Connector**
- Poll external API for events
- Transform response to event format

## Event Condition Configuration

**Event Rules** specify when to trigger actions:

```
Event Type: OrderPlaced
Conditions:
  - Order Amount > $100
  - Customer Segment = "VIP"
  - Product Category IN {Electronics, Premium}

Action: Invoke NBA Strategy (Upsell & Cross-Sell)
```

**Operators**:
- Comparison: =, !=, <, >, <=, >=
- Membership: IN, NOT IN
- String: CONTAINS, STARTS WITH, ENDS WITH
- Logical: AND, OR, NOT

## Triggering NBA from Events

**Automated NBA Invocation**:
```
When: Order > $500
Then: Invoke NBA Strategy (Premium Cross-Sell)
  Apply to: Customer segment
  Deliver via: Email (next day)
```

**Benefits**:
- Zero latency (no customer action required)
- Contextual offers (based on order details)
- Consistent customer experience

**Configuration**:
1. Create Decision Rule to invoke NBA
2. Map event properties to NBA input parameters
3. Define delivery channel/timing
4. Test with sample events

## Real-Time Event Processing

### Processing Modes

**Synchronous**:
- Event → Decision → Action (< 1 second)
- Blocks caller until complete
- Used for: Fraud detection, payment authorization

**Asynchronous**:
- Event → Queue → Background worker → Action (minutes/hours)
- Non-blocking, scalable to high volumes
- Used for: Email campaigns, batch decisions

### High-Volume Event Handling

**Architecture**:
```
Event Adapter → Message Queue (Kafka/RabbitMQ) →
Worker Pool (parallel processing) → Decision Rules → Actions
```

**Configuration**:
- Set queue batch size (process N events at once)
- Tune worker thread pool (CPU cores × 2-4)
- Monitor queue depth (target < 1000 events waiting)

## Debugging Event Strategies

### Enable Event Logging
```
System Admin → Loggers
Set: Pega-IntegrationEngine = DEBUG
Set: Pega-RuleEvent = DEBUG
```

### Trace Event Execution
```
Monitor > Alerts and Logs > System Events
Filter: Event Type, Time Range, Condition Results
```

### Common Event Issues

**Issue**: Event received but action not triggered
- Check: Does event match conditions exactly?
- Check: Event properties mapped correctly?
- Check: NBA strategy active and published?
- Check: Event timestamp valid (not in past/future)?

**Issue**: Event processing delayed (queue backlog)
- Check: Worker thread count sufficient?
- Check: Decision rules too complex (optimize?)
- Check: Downstream system (email gateway) bottleneck?
- Fix: Increase worker threads, simplify rules, add resources

**Issue**: Duplicate events triggering multiple actions
- Cause: Retry logic invoking event multiple times
- Check: Unique event ID handling
- Fix: Implement idempotency key (event ID) deduplication

**Issue**: Event data missing/malformed
- Check: Source system sending all required fields
- Check: Data type conversions (string → number, date parsing)
- Check: Null/empty value handling
- Fix: Add validation rules before condition check

## Event Strategy Best Practices

1. **Unique Event IDs**: Use event ID to prevent duplicate processing
2. **Timestamps**: Validate event timestamp (should be recent, not future)
3. **Fallback Actions**: If decision rule fails, define default behavior
4. **Testing**: Use test event generator to validate conditions
5. **Monitoring**: Dashboard tracking event volume, latency, error rate
6. **Throttling**: Avoid overwhelming downstream systems with simultaneous actions
7. **Audit Trail**: Log all triggered actions for compliance/debugging

## Common Configuration Mistakes

- **Mistake**: Event rule too broad (triggers for all orders)
  - Fix: Add specific conditions (amount range, segment, product category)

- **Mistake**: No timeout configured (event processing hangs)
  - Fix: Set decision rule timeout (typically 5-30 seconds)

- **Mistake**: Event property name mismatch
  - Fix: Verify mapping exactly matches incoming JSON keys
"""
    },
    {
        "title": "Pega GenAI & Knowledge Buddy",
        "url": "https://docs.pega.com/bundle/platform/page/pega-genai.html",
        "content": """
# Pega GenAI & Knowledge Buddy

## Pega GenAI Overview (Pega 23+/Infinity)

Pega GenAI integrates Large Language Models (LLMs) for intelligent automation:
- **Case summarization**: AI reads case history, generates summary
- **Email generation**: Auto-draft responses, recommendations
- **Knowledge suggestions**: Surface relevant articles during case work
- **Intelligent assignment**: Route to optimal specialist
- **Process mining insights**: Analyze case flow, identify bottlenecks

### Supported LLMs
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Azure OpenAI**: Azure-hosted GPT models
- **Google Vertex AI**: PaLM 2, Gemini models
- **Custom**: On-premises or proprietary LLMs

## Knowledge Buddy Configuration

Knowledge Buddy is a conversational AI assistant integrated into Pega workspace.

### Setup Steps

**1. Enable in System Settings**
```
Admin → GenAI → Enable Knowledge Buddy
Select: LLM provider (OpenAI, Azure, etc.)
Input: API key, endpoint
```

**2. Create Conversation Rules**
Define conversation scopes:
- Support case resolution
- Product troubleshooting
- Policy inquiry
- General Q&A

**3. Configure Knowledge Sources**
Link to knowledge base:
- Pega Knowledge Object instances
- External Wikipedia/Confluence
- Help articles, FAQs
- Case templates

**4. Set Security & Compliance**
- Redact PII (SSN, credit card) before LLM
- Configure audit logging
- Set token limits (cost control)
- Enable content moderation filters

### Knowledge Buddy Workflow
```
Agent Question → LLM Search Knowledge Base →
Generate Response with Citations → Display in Workspace
Agent Reviews & Refines → Submit/Send to Customer
```

## GenAI-Powered Features

### Case Summarization
- **Trigger**: Manual button or automatic on case completion
- **Input**: Case history (messages, activities, resolutions)
- **Output**: 3-5 paragraph summary of issue, resolution, outcome
- **Use**: Knowledge transfer, QA review, customer communication

### Email Generation
- **Trigger**: Agent selects "AI Draft Response"
- **Input**: Case context, previous email thread
- **Output**: Professional draft email with tone matching case
- **Agent Action**: Review, edit, personalize, approve before sending

**Best for**:
- First response (faster ramp-up for new agents)
- Follow-up inquiries (consistent tone)
- Escalation notices (professional format)

**Not recommended**:
- Sensitive negotiations, apologies (needs human nuance)
- Regulatory/legal notices (must be lawyer-reviewed)

### Knowledge Suggestions
- **Trigger**: Real-time as agent works on case
- **Input**: Case classification, customer history, issue
- **Output**: Ranked list of relevant knowledge articles
- **Agent Action**: Click to open article in side pane

**Ranking factors**:
- Relevance to case type
- Recency (updated within 6 months)
- Popularity (frequently used)
- Agent rating feedback

## Prompt Engineering in Pega

### Prompt Customization
Modify prompts to change LLM behavior:

**Default Case Summary Prompt**:
```
"Summarize this support case in 4 paragraphs. Include: (1) customer issue,
(2) root cause, (3) resolution steps taken, (4) outcome. Be concise and
professional."
```

**Custom Prompt (Technical Support)**:
```
"Create a technical summary of this case. Include: (1) symptoms reported,
(2) troubleshooting steps, (3) tools/logs used, (4) final resolution,
(5) preventive recommendations."
```

### Prompt Best Practices
1. **Be specific**: "Generate a professional email response to a billing complaint" vs. "Write an email"
2. **Set tone**: "Empathetic but professional", "Technical and detailed", "Conversational"
3. **Define format**: "Numbered list", "3 paragraphs", "Bullet points"
4. **Include constraints**: "Under 200 words", "Avoid jargon", "Reference case number"
5. **Test and iterate**: A/B test prompts, measure agent satisfaction, refine

### Redaction Rules
Define PII to redact before sending to LLM:
```
Redact Patterns:
  - SSN: \d{3}-\d{2}-\d{4} → [SSN]
  - Credit Card: \d{4} \d{4} \d{4} \d{4} → [CC]
  - Email: \S+@\S+ → [EMAIL]
  - Phone: \d{3}-\d{3}-\d{4} → [PHONE]
  - Custom: "Internal Account ID" → [ACCT]
```

## Connecting to LLMs

### OpenAI Setup
```
1. Create OpenAI account, generate API key
2. Admin → GenAI → Add Provider
3. Provider Type: OpenAI
4. Model: gpt-4-turbo or gpt-3.5-turbo
5. API Key: [paste key]
6. Test connection
```

### Azure OpenAI Setup
```
1. Create Azure account, deploy OpenAI resource
2. Get: Endpoint URL, API key, Deployment name
3. Admin → GenAI → Add Provider
4. Provider Type: Azure OpenAI
5. Endpoint: https://[resource].openai.azure.com/
6. API Key, Deployment Name: [from Azure]
7. Test connection
```

### Cost Optimization
- **Token limits**: Set max tokens per request to control spend
- **Caching**: Cache frequent prompts (knowledge articles)
- **Fallback**: Use cheaper model if primary unavailable
- **Monitoring**: Track token usage, cost per case

## Debugging GenAI Features

**Issue**: Knowledge Buddy returns irrelevant articles
- Check: Knowledge base indexed correctly?
- Check: Article metadata (title, keywords) descriptive?
- Check: Relevance ranking parameters tuned?
- Fix: Update articles, retrain search index, refine prompts

**Issue**: Email generation tone wrong/offensive
- Check: Prompt instructions clear?
- Check: LLM model appropriate for task?
- Check: Temperature/sampling parameters?
- Fix: Refine prompt, test with diverse cases, add guardrails

**Issue**: GenAI responses include PII
- Check: Redaction rules configured?
- Check: Patterns matching actual data format?
- Check: Multiple PII types covered?
- Fix: Add missing redaction rules, audit logs

**Issue**: LLM API calls timing out
- Check: API endpoint healthy (test directly)?
- Check: Network latency, rate limits?
- Check: Token count too high?
- Fix: Add timeout, implement retry logic, reduce prompt size

**Issue**: Inconsistent summaries for similar cases
- Check: Randomness parameters (temperature) too high?
- Check: Knowledge base up-to-date?
- Check: Different agents working different cases?
- Fix: Lower temperature, standardize case data, test consistency

## GenAI Governance & Compliance

- **Audit logging**: All LLM calls logged (prompt, response, cost)
- **Content moderation**: Detect/block harmful outputs
- **Bias monitoring**: Track if recommendations differ by demographic
- **Data retention**: LLM call history retained per regulation
- **Acceptable use**: Define prohibited uses (generating fraudulent content, etc.)
"""
    }
]

def seed_phase9():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE9:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase9_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE9)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 9 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase9()
