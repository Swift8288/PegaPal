"""
Curated Pega Knowledge Base — Phase 14 (Reporting, Analytics & Dashboards)
Run: python -m crawler.seed_kb_phase14
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE14 = [
    {
        "title": "Report Definition Deep Dive",
        "url": "https://pega-kb.internal/reports/definition-deep-dive",
        "content": """
# Report Definition Deep Dive

## Overview
Report definitions in Pega are the backbone of case analytics and operational reporting. They define what data is queried, how it's formatted, and who can access it.

## Types of Reports

### Summary Reports
- Aggregate data using GROUP BY and aggregate functions
- Show counts, sums, averages, min/max values
- Used for KPIs, trend analysis, capacity planning
- Typically fast with proper indexing
- Best for executive dashboards

### List Reports
- Show detailed row-by-row data
- Support filtering, sorting, and pagination
- Can join multiple tables/classes
- May be slower with large datasets (>100K rows)
- Include all requested columns for each row

## Creating Report Definitions

### Step 1: Create Report Class
1. Open **Reports** tab in App Studio
2. Click **Create Report**
3. Select report class (typically extends `Report-`)
4. Choose **Summary** or **List** as base class

### Step 2: Configure Data Source
- Select primary **Data Model** (usually your case class)
- Configure **joins** to related tables if needed
- Set **joins** carefully—multiple joins degrade performance
- Use **sub-reports** instead of heavy joins when possible

### Step 3: Add Filters
- Click **Add Filter** to restrict data
- Use **dynamic filter rules** for context-aware filtering
- Avoid `OR` conditions in filters (use two separate reports instead)
- Date range filters (e.g., "past 30 days") should be parameterized

### Step 4: Configure Columns
- Add only necessary columns to reduce I/O
- Use **display format** for currency, percentage, dates
- **Calculated columns** (expressions) slow execution—minimize usage
- Define **sort order** (primary, secondary, tertiary)

## Aggregate Functions

| Function | Use Case | Performance Note |
|----------|----------|------------------|
| COUNT(*) | Row count | Very fast |
| SUM() | Total amounts | Fast with index |
| AVG() | Average values | Fast with index |
| MIN/MAX | Range queries | Fast |
| COUNT(DISTINCT) | Unique values | Slower—use sparingly |

## Report Performance Optimization

### Identify Slow Reports
1. Enable query logging: `prconfig.xml` → `Log-Database` tracer
2. Review SQL execution time in **Pega Log**
3. Check **row counts**—if >500K rows, add filters or use pagination

### Common Bottlenecks
- **No indexes on filter columns**: Index properties used in WHERE clause
- **Multiple joins**: Replace with sub-reports
- **LIKE filters**: Prefix matching (LIKE 'A%') is faster than wildcard
- **Calculated columns**: Move logic to database views

### Optimization Checklist
- [ ] Add indexes to all filter properties
- [ ] Use parameterized date ranges instead of hardcoded dates
- [ ] Replace expensive joins with sub-reports
- [ ] Remove unused columns from SELECT
- [ ] Test with realistic data volumes (UAT → Prod comparison)

## Using Custom SQL in Reports

### When to Use Custom SQL
- Complex multi-table aggregations
- Window functions (ROW_NUMBER, RANK)
- Cross-table comparisons
- Direct database optimization

### Custom SQL Syntax
```sql
SELECT COUNT(*) as case_count, pxclass, SUM(amount) as total
FROM {class}
WHERE pxcreateoperator = ? AND pxcreatedatetime > ?
GROUP BY pxclass
ORDER BY total DESC
```

**Placeholders**:
- `{class}` = Case class table name
- `?` = Parameter binding (safe from SQL injection)
- Always use parameterized queries—never concatenate user input

### Risks
- SQL injection if not parameterized
- Database-specific syntax may break on migration
- Harder to debug than UI-driven reports

## Sub-Reports

### When to Use
- Reduce primary report complexity
- Show related data in secondary report
- Faster than heavy JOIN operations
- Example: Main report shows cases, sub-report shows activities per case

### Configuration
1. Create child report (e.g., `Report-CaseActivities`)
2. In parent report, add column of type **Sub-Report**
3. Pass **linking parameters** to child (case ID, date range)
4. Child filters based on parameters

### Performance Benefit
- Parent queries base data
- Child queries run only for displayed rows (pagination-aware)
- Avoids N+1 query problem if implemented correctly

## Report Categories & Organization

- Use **folders** to organize by domain (Sales, Service, Operations)
- Assign **access control rules** to categories
- Prefix report names: `PROD_` for production, `DEV_` for development
- Maintain report **documentation** in design (title, purpose, refresh frequency)

## Common Report Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Property not available for reporting" | Property not indexed | Add Declare Index rule |
| "Timeout executing query" | Too many rows or slow joins | Add filters, check indexes |
| "No data displays" | Filter too restrictive | Test with broader date range |
| "Wrong totals in summary" | NULL values in aggregation | Use COALESCE, handle NULLs |

## Debugging Slow Reports

1. **Check execution time**: Admin → Pega Log → Filter by report name
2. **Review query plan**: Database admin tool, check join order
3. **Validate indexes**: Ensure all filter columns are indexed
4. **Test with production data volume**: Dev data may be too small
5. **Monitor concurrency**: Multiple users running same report?
6. **Analyze row count**: If >100K rows, add filters or pagination

## Best Practices

- Review reports quarterly—business needs change
- Document expected refresh frequency (hourly, daily, on-demand)
- Set **row limits** in reports to prevent runaway queries
- Use **caching** where appropriate (Pega's report cache)
- Always test with realistic data before deploying to production
"""
    },
    {
        "title": "Dashboard Widgets and Real-Time Metrics",
        "url": "https://pega-kb.internal/dashboards/widgets-real-time",
        "content": """
# Dashboard Widgets & Real-Time Metrics

## Dashboard Fundamentals

### What is a Dashboard?
- Collection of **widgets** displaying KPIs and analytics
- Can be **personal** (individual user) or **shared** (role-based)
- Composed on **portal** pages (Pega's layout system)
- Data refreshes at configured intervals (real-time or batch)

### Dashboard vs Portal
- **Dashboard**: Business-focused, metric-heavy, read-only
- **Portal**: Work-focused, task-heavy, interactive with actions

## Widget Types

### 1. Chart Widgets
- **Line**: Trends over time (case volume, resolution time)
- **Bar**: Comparisons (cases by region, workload by team)
- **Pie**: Distribution (case types, priority breakdown)
- **Combination**: Mix metrics with secondary axis

### 2. List Widgets
- Display tabular data (open cases, pending reviews)
- Support **sorting** and **filtering** at runtime
- Link to detail views (click case ID → opens case)
- Typically limited to 50-100 rows for dashboard performance

### 3. Summary Widgets
- Single metric display (Total Cases, Avg Resolution Time)
- Show trend indicator (↑ ↓ for comparison periods)
- Ideal for executive dashboards
- Fast rendering—minimal calculation

### 4. KPI (Key Performance Indicator) Widgets
- Metric + **target** + **actual** + **status** (green/yellow/red)
- Include **trend sparkline** (7-day history)
- Color-coded by thresholds (On Target, At Risk, Below Target)
- Refreshes frequently (often every 5-15 minutes)

## Configuring Data Sources for Widgets

### Step 1: Create Report or Data Source
- Use **existing report** (preferred—data already optimized)
- Create **new report** specifically for widget (lightweight)
- Reports must be **optimized**—widget displays don't wait long

### Step 2: Add Widget to Dashboard Portal
1. Edit **portal page** (drag-drop interface)
2. Add widget component
3. Bind to **report** or **ruleset definition**
4. Configure **parameters** (date range, filter values)

### Step 3: Set Data Source Properties
```
Data Source Report: Report-DashboardCases
Primary Key: CaseID
Display Columns: CaseID, CaseName, Status, Priority
Filter Rule: MyTeam=CurrentUser
```

### Step 4: Map Parameters
- Allow dashboard **drop-down** to filter widget
- Pass **dynamic parameters**: `&Date=@TODAY@ - 30`
- Support **user context**: filter by department, region

## Refresh Intervals

### Real-Time (WebSocket)
- **Interval**: Every 5-15 seconds
- **Use case**: Inbound queue, live support metrics
- **Cost**: Higher database load, network traffic
- **Configuration**: Set `Refresh = Immediate` or `5s`

### Near Real-Time (AJAX Polling)
- **Interval**: Every 1-5 minutes
- **Use case**: Daily KPIs, trend monitoring
- **Cost**: Moderate—acceptable for most dashboards
- **Configuration**: Set `Refresh = 300s` (5 minutes)

### Batch (On-Demand)
- **Interval**: Manual refresh or hourly
- **Use case**: Executive dashboards, historical reports
- **Cost**: Low—single query per refresh
- **Configuration**: `Refresh = Manual` or `3600s` (1 hour)

### Performance Tips
- **Avoid 5s refresh on large datasets** (100K+ rows)
- **Cache results** when multiple users view same widget
- **Stagger refresh times** to avoid thundering herd (Dashboard A at :00, B at :20, C at :40)

## Dashboard Portals

### Creating a Portal
1. **Application** → **Portals**
2. Click **Create** → Select **Dashboard Portal**
3. Add **layout** (3-column, 2-column, etc.)
4. Drag-drop **widget components**
5. Configure **responsive design** for mobile

### Portal Sections
- **Header**: Title, refresh button, filter controls
- **Left/Center/Right Columns**: Widget placement (drag-drop responsive)
- **Footer**: Last updated timestamp, export option

### Styling
- Use **theme** for consistent colors (corporate branding)
- Configure **colors** for dashboard theme
- Set **widget borders** and spacing
- Support **dark mode** for accessibility

## Role-Based Dashboards

### Implementation Approach
1. Create **portal page** per role (PortalManagerDashboard, PortalAgentDashboard)
2. Configure **access control**: Only role members can view
3. Use **personal instance** for user-specific data
4. Pass **user context** as filter parameter

### Example: Manager vs Agent Dashboard
**Manager Dashboard**: Team workload, capacity planning, SLA metrics
**Agent Dashboard**: My cases, pending tasks, personal SLA progress

### Dynamic Filtering
```
Widget Filter: Manager = @CONTEXT.Manager  // Only my team's data
```

## Debugging Widget Display Issues

### Widget Shows "No Data"
1. **Check report**: Run report directly in Studio—does it return rows?
2. **Verify filter**: Click widget → Check applied filters
3. **Check date range**: Default date range too restrictive?
4. **Test permissions**: User has access to underlying report?

### Widget Shows Stale Data
1. **Check refresh interval**: Too long (1 hour) vs expected (5 min)?
2. **Force refresh**: Click browser refresh (F5) or widget refresh button
3. **Check cache**: Some widgets cache—look for cache settings
4. **Verify report currency**: Report queries correct date (not hardcoded old date)?

### Widget Displays Incorrectly (Layout Broken)
1. **Inspect browser**: Right-click → Inspect Element
2. **Check responsive breakpoints**: Mobile vs desktop widths
3. **Verify column widths**: Widget too narrow for content?
4. **Test in incognito**: Rule versioning/caching issue?

### Chart Widget Won't Render
1. **Check data**: Are X and Y axes properly configured?
2. **Verify numeric data**: Non-numeric columns in SUM field?
3. **Check aggregation**: Ensure GROUP BY for summary metrics
4. **Review chart type**: Pie chart requires 100% data (no NULL)

### Performance Issues (Widget Slow to Load)
1. **Check report row count**: Limit to 1000 rows max for widgets
2. **Verify refresh interval**: Real-time (5s) too aggressive?
3. **Review indexes**: Widget report filters need indexes
4. **Monitor load**: Concurrent user load on dashboard?

## Best Practices

- **One dashboard per role/persona**—avoid single monolithic dashboard
- **Size widgets appropriately**—balance information density with readability
- **Use caching**—if data doesn't need to be truly real-time
- **Test performance with prod data**—dev data often too small
- **Document refresh intervals**—users need to know data currency
- **Provide export options**—CSV/Excel for offline analysis
"""
    },
    {
        "title": "Pega Insights and Business Intelligence",
        "url": "https://pega-kb.internal/analytics/pega-insights-bi",
        "content": """
# Pega Insights & Business Intelligence

## Pega Insights Overview

### What is Pega Insights?
- **Unified analytics platform** within Pega
- Connects to **Pega Data Warehouse** (PDW) for reporting
- Pre-built **KPI definitions** and **dashboards**
- Enables **predictive analytics** and **AI-driven insights**
- Built on **Elasticsearch** for fast aggregations

### Pega Insights vs Traditional Reports
| Aspect | Pega Insights | Traditional Reports |
|--------|---------------|-------------------|
| Speed | Near real-time (seconds) | Minutes to hours |
| Scope | Organization-wide KPIs | Specific use case |
| Customization | Pre-built + limited custom | Highly customizable |
| Data Source | PDW + streaming | Case database |
| AI/ML | Predictive models included | Custom development |

## Pega Data Warehouse (PDW)

### Architecture
```
Pega System → ETL Pipeline → Data Warehouse → Analytics Tools
   (source)    (hourly load)      (snowflake)   (Pega Insights, BI)
```

### Key Tables
- **Fact_Work**: Case lifecycle events (created, opened, assigned, resolved)
- **Fact_Activity**: Activity timing and outcomes
- **Dimension_User**: User profiles and metadata
- **Dimension_Case**: Case attributes and hierarchies
- **Fact_Performance**: SLA, queue times, automation success

### Refresh Frequency
- **Typical**: Nightly batch (midnight → 6 AM)
- **Some tables**: Hourly refresh (high-priority KPIs)
- **Real-time**: Streaming tables (case creation, assignment)
- **Lag**: Usually 5-30 minutes for real-time data

### Accessing PDW
1. **Pega Studio** → **PDW Data Explorer**
2. Browse **databases** and **tables**
3. Query via **SQL** or **report builder**
4. Schedule **automated exports**

## Connecting to BI Tools (Tableau, Power BI)

### Prerequisites
- **Pega Data Warehouse** deployed and populated
- **JDBC/ODBC driver** configured (database-specific)
- **Network access** to PDW database (firewall rules)
- **Authentication** (service account with PDW read access)

### Tableau Connection Steps
1. **Connect** → **New Data Source** → Select database type (SQL Server, PostgreSQL, etc.)
2. Enter **PDW connection details**:
   - Server: `warehouse.pega.internal`
   - Port: `5432` (or database-specific)
   - Database: `pega_dw`
   - Username: `tableau_svc`
3. **Authenticate** and browse available tables
4. Build **worksheets** and **dashboards** on Fact/Dimension tables

### Power BI Connection Steps
1. **Get Data** → **Database** → Select connector type
2. Enter **server address** and **database name**
3. Use **service account** credentials (cached securely)
4. Import **tables** into Power BI data model
5. Create **relationships** (Fact to Dimension tables)
6. Build **reports** and **dashboards**

### Authentication Patterns
- **Service account**: Dedicated account with PDW read access
- **Windows/Azure AD**: Mapped to Pega roles (enterprise)
- **OAuth**: For cloud-based BI tools
- **SSL/TLS**: Encrypt all PDW connections

## Data Extraction for Analytics

### Methods

#### 1. Scheduled Exports
- Configure **export frequency** (nightly, weekly)
- Destination: Cloud storage (S3, Azure Blob) or SFTP
- Format: CSV, Parquet, or native database dump
- Typical use: Data lakes for data scientists

#### 2. JDBC/ODBC Connection
- Direct **real-time** connection to PDW
- Used by **BI tools** for interactive queries
- Requires **network access** to PDW database
- Performance depends on **query complexity**

#### 3. REST API
- Pega provides **REST endpoints** for data extraction
- Authentication: OAuth or API key
- Returns: JSON payloads
- Rate-limited: Typically 100 requests/min

#### 4. Direct Database Query
- Advanced users query PDW **SQL directly**
- Full control over **joins, aggregations, filtering**
- Risk: Complex queries may timeout
- Recommended: Use **views** (pre-built for common queries)

### Best Practices
- **Schedule exports during low-traffic** windows (3-6 AM)
- **Filter large tables** (Fact_Work) by date range to reduce size
- **Use incremental loads** for large datasets (export delta since last run)
- **Test exports with realistic volume** before production
- **Monitor extraction time** and optimize queries if >30 minutes

## Insights-Powered Reports

### Pre-Built Reports
- **Case Performance**: Volume, SLA, resolution time trends
- **Resource Utilization**: Workload distribution, agent productivity
- **Automation Metrics**: Bot utilization, automation ROI
- **Customer Journey**: Multi-case customer analysis

### Customizing Insights
1. **Clone** pre-built report as starting point
2. Add **filters** (business unit, case type, date range)
3. Configure **dimensions** (group by region, team, priority)
4. Add **metrics** (count, sum, average, percentile)
5. **Publish** and share with stakeholders

### Predictive Insights
- **Case time prediction**: Estimate remaining case duration
- **Priority prediction**: Auto-assign priority based on patterns
- **Churn prediction**: Identify at-risk customers
- **Effort prediction**: Estimate automation potential

## Real-Time vs Batch Analytics

### Real-Time Analytics
- **Data source**: Streaming tables or PDW with hourly refresh
- **Latency**: 5-30 minutes
- **Use cases**: Live dashboards, on-call metrics, incident tracking
- **Cost**: Higher (more frequent queries)
- **Example**: "Cases in progress right now"

### Batch Analytics
- **Data source**: PDW nightly refresh
- **Latency**: 6-24 hours
- **Use cases**: Trend analysis, historical reports, executive dashboards
- **Cost**: Lower (single daily query)
- **Example**: "Cases resolved yesterday"

### Choosing the Right Approach
| Metric | Latency Requirement | Recommended |
|--------|-------------------|------------|
| Team performance KPI | Must be current | Real-time (5 min) |
| Executive summary | Daily is sufficient | Batch (nightly) |
| Live agent queue | Must be live | Real-time (WebSocket) |
| Customer journey analysis | Historical OK | Batch (nightly) |

## Troubleshooting Analytics Issues

### PDW Data Missing or Stale
1. **Check ETL job status**: Admin → Data Integration → Job Log
2. **Verify data source**: Cases being created in Pega system?
3. **Check extraction schedule**: When was last successful run?
4. **Look for errors**: ETL logs may show data quality issues

### Reporting Tool Can't Connect to PDW
1. **Test network access**: `ping warehouse.pega.internal`
2. **Verify credentials**: Service account has PDW read permission
3. **Check firewall**: Port open (5432, 3306, 1433 depending on DB)
4. **Validate JDBC/ODBC driver**: Installed and configured correctly

### Slow Analytics Queries
1. **Check PDW table size**: Some Fact tables may have 100M+ rows
2. **Verify indexes**: Dimension join columns should be indexed
3. **Optimize joins**: Avoid joining many Fact tables
4. **Use views**: Pre-aggregated views are faster than raw tables

## Best Practices

- **Start with pre-built reports**—understand them before customizing
- **Use PDW for analytics, not operational queries**—don't slow down case processing
- **Schedule heavy exports during maintenance windows**
- **Document BI dashboards**—business users need to understand metrics
- **Version BI dashboards** like code—track changes, test before production
- **Monitor analytics performance**—slow queries impact user experience
"""
    },
    {
        "title": "Elasticsearch Configuration and Search",
        "url": "https://pega-kb.internal/search/elasticsearch-config",
        "content": """
# Elasticsearch Configuration & Search

## Pega's Built-In Elasticsearch

### Overview
- Pega includes **embedded Elasticsearch** for full-text case search
- Automatically **indexes** case content (text, documents, activity notes)
- Provides **sub-second search** across millions of cases
- Supports **faceted search** and **advanced filters**
- Optional: Deploy **standalone Elasticsearch cluster** for scale

### When to Use Elasticsearch vs Database Search
| Feature | Elasticsearch | Database |
|---------|---------------|----------|
| Full-text search | Excellent | Limited (LIKE is slow) |
| Phrase search | "exact phrase" | Not supported |
| Fuzzy matching | Typo tolerance | Must be exact |
| Performance (100K+ docs) | Sub-second | Slow (>5s) |
| Index size | ~30% of source | Same as source |

## Indexing Strategy

### What Gets Indexed by Default
- **Case ID, Type, Status** (all case metadata)
- **Notes and attachments** (text content)
- **Custom rich text fields** (description, comments)
- **Date fields** (created, resolved dates)

### What's NOT Indexed
- **Binary files** (PDFs, images—requires OCR)
- **Embedded objects** (not exposed to search by default)
- **Performance metrics** (response time, CPU)

### Index Names and Shards
```
Index: pega_cases_202604
Shards: 5 (default, adjust based on volume)
Replicas: 1 (for HA)
Retention: 90 days rolling (configurable)
```

### Configuring Index Properties
1. **Case class** → **Full-text search properties**
2. Check **searchable** flag on properties
3. Configure **analyzer** (language, stemming, tokenization)
4. Set **boost** for important fields (Title: 2x, Description: 1x)

### Analyzer Configuration
- **Standard**: Default tokenization and lowercasing
- **English**: Stemming (run → running → runs)
- **Keyword**: No tokenization (exact match)
- **Custom**: Domain-specific (medical terms, product codes)

## Full-Text Search Across Cases

### Search Syntax

#### Simple Search
```
urgent customer complaint
```
Finds cases containing ALL words anywhere.

#### Phrase Search
```
"customer urgently needs"
```
Finds exact phrase match.

#### Boolean Operators
```
urgent AND customer OR critical
(high priority) NOT resolved
```

#### Fuzzy Search
```
custmer~1  // Typo tolerance (1 edit distance)
resolvd~2  // 2 character edits allowed
```

#### Wildcard
```
cus* AND (pending OR open)
```

### Search Query Examples
```
Case ID: PG-2024-001234
Status: open AND (high priority OR urgent)
Created: [2024-01-01 TO 2024-03-31]
Owner: john.doe@company.com
```

## Search Configuration

### Step 1: Enable Full-Text Search
1. **App Studio** → **Case Class**
2. Go to **Full-Text Search** section
3. Set **Enable search** = Yes
4. Choose **properties to index** (select only needed)
5. Configure **field boost** (Title: 2.0, Description: 1.5)

### Step 2: Set Index Refresh Rate
- **Real-time** (refresh_interval: 1s): Newly created cases searchable within 1 second
- **Near real-time** (refresh_interval: 30s): Acceptable for most use cases
- **Batch** (refresh_interval: 5m): Low-frequency updates only

### Step 3: Configure Retention
```
Elasticsearch Settings:
  Index retention: 90 days
  Rollover frequency: Daily (new index each day)
  Compression: 50% (via ILM policy)
```

### Step 4: Test Search
1. Open **case list** → **Search bar**
2. Type search query
3. Verify results appear (should be <1 second)
4. Try **advanced filters** and **facets**

## Custom Search Categories

### Purpose
- Organize **saved searches** by business domain
- Enable **role-based search templates**
- Provide **quick-access filters** for common queries

### Creating a Search Category
1. **Admin** → **Search** → **Search Categories**
2. Click **Create**
3. Define **name** (e.g., "Escalations")
4. Set **base filter** (e.g., Priority = High)
5. Add **facets** (Agent, Team, Region)

### Example: Support Team Escalations Category
```
Base Filter: Status = Escalated
Facets: Agent, Queue, DateRange, Priority
Display: Newest first
Access: Support role only
```

## Search Relevance Tuning

### Improving Relevance

#### 1. Field Boost
- Title matches: Boost 3x
- Description matches: Boost 1.5x
- Comments: Boost 0.5x
- Rationale: Title more relevant than old comments

#### 2. Freshness Boost
```
Boost recent cases: decay_function
  Newer cases slightly higher rank
  1-year-old cases no boost penalty
```

#### 3. Popularity Boost
```
Cases with many activities ranked slightly higher
  (Indicates important cases)
```

### Tuning Steps
1. **Identify common searches**: What do users search for?
2. **Assess result quality**: Are top 5 results useful?
3. **Adjust boost values**: Re-weight fields
4. **A/B test**: Show 50% old ranking, 50% new ranking
5. **Measure improvement**: CTR, time-to-resolution

## Elasticsearch Cluster Health

### Health Check
1. **Admin** → **System** → **Elasticsearch Health**
2. Check **cluster status**:
   - Green: All shards allocated, cluster healthy
   - Yellow: Some replicas unallocated (tolerable)
   - Red: Missing shards—investigate immediately

### Monitoring Metrics
- **Index size**: Should grow predictably (investigate spikes)
- **Query latency**: p95 <1000ms, p99 <2000ms
- **Heap usage**: 80% max (if >85%, memory pressure)
- **Disk usage**: Monitor free space (need 20% reserve)

### Common Health Issues

| Status | Cause | Fix |
|--------|-------|-----|
| Yellow | Missing replica | Add nodes or reduce replica count |
| Red | Missing shard | Restore from backup, investigate data loss |
| High latency | Undersized cluster | Add nodes, optimize queries |
| Heap OOM | Too many indices | Archive old indices, reduce fields |

## Debugging Search Issues

### Missing Results
1. **Check index exists**: Admin → Elasticsearch → Indices
2. **Verify property indexed**: Property should have "searchable" = true
3. **Test with broader query**: Remove filters, search just by case type
4. **Check index refresh**: Data may not yet be indexed (wait 30s)
5. **Review access control**: User has permission to see cases?

### Slow Search
1. **Check query complexity**: Wildcard or fuzzy search? (slower)
2. **Monitor cluster health**: Yellow/Red = performance issues
3. **Review heap usage**: If >80%, performance degrades
4. **Check concurrent load**: Many simultaneous searches?
5. **Profile query**: Use Elasticsearch `_explain` to see scoring

### Index Corruption
1. **Check shard allocation**: Any unassigned shards?
2. **Review logs**: Elasticsearch errors in `pega.log`
3. **Force shard allocation**: `_cluster/reroute` (advanced)
4. **Reindex**: Create new index, copy data (safe but time-consuming)
5. **Restore backup**: If corruption detected, restore from snapshot

### Search Returns Wrong Case Type
1. **Verify filter**: Is case type filter applied?
2. **Check mapping**: Elasticsearch may confuse field types
3. **Review boost configuration**: Another type boosted higher?
4. **Test exact search**: Case ID search—is it finding correct case?

## Best Practices

- **Index only necessary fields**—reduce index size, improve speed
- **Monitor index growth**—implement retention policies
- **Test search with production data volume**—dev indexes often too small
- **Use facets strategically**—limit to 5-10 most common filters
- **Document search syntax**—users may not know advanced operators
- **Schedule index maintenance** (optimize, shrink) during low-traffic
- **Backup Elasticsearch regularly**—snapshots to NAS or cloud storage
"""
    },
    {
        "title": "Declare Index and Reporting Properties",
        "url": "https://pega-kb.internal/optimization/declare-index",
        "content": """
# Declare Index & Reporting Properties

## What Declare Index Does

### Purpose
Declare Index **exposes embedded properties** for use in reporting and filtering, without requiring denormalization or ETL. It creates **database indexes** on properties to enable fast WHERE/GROUP BY operations.

### Key Points
- Makes **nested properties accessible** in reports (e.g., WorkType from embedded Work object)
- Creates **database index** for filtering performance
- Enables properties to be **reported on without duplication**
- Critical for **filtering large datasets** efficiently

### Example Use Case
```
Case has embedded: WorkItems {WorkType, DueDate, Priority}
Without Declare Index: Can't filter/group by WorkType easily
With Declare Index: WorkType available in report filters, GROUP BY fast
```

## When to Use Declare Index

### Good Use Cases
- **Frequently filtered properties** (Status, AssignedTo, Priority)
- **Frequently grouped properties** (Type, Region, Team)
- **Date fields** used in date range filters
- **Lookup values** (reference codes, categories)
- **Performance-critical queries** (executive dashboards)

### When NOT to Use Declare Index
- **Binary fields** (images, PDFs)
- **Large text** (notes, descriptions) → use Elasticsearch instead
- **Rarely used** properties (one-off reports)
- **High-cardinality fields** (UUIDs, timestamps with milliseconds)
- **Performance acceptable without it** → don't add indexes

## Creating Declare Index Rules

### Step 1: Identify Properties to Index
1. List all properties used in report **WHERE clauses** (filters)
2. List all properties used in report **GROUP BY clauses**
3. Identify **date range filters**
4. Prioritize by **frequency of use**

### Step 2: Create Declare Index Rule
1. **App Studio** → **Create** → **Declare Index**
2. Specify **index class** (usually your case class)
3. Add **indexed properties**:
```
Property         Data Type      Sort Order
Status          Text            Ascending
Priority        Text            Ascending
CreatedDate     DateTime        Descending
AssignedTeam    Text            Ascending
```

### Step 3: Configure Index Options
```
Unique: No (Status can have many cases)
Sparse: No (All cases should have Status)
Background: Yes (Build without locking tables)
```

### Step 4: Activate Index
1. Click **Activate** to create physical database index
2. Pega generates SQL: `CREATE INDEX idx_case_status ON case_table (status)`
3. Process may take **hours for large tables** (100M+ rows)
4. Can be scheduled during **maintenance window**

## Performance Impact of Indexes

### Benefits
- **10-100x faster filters** on indexed properties (1000ms → 10ms)
- **Sub-second GROUP BY** on indexed properties
- **Range queries faster** (created between date1 and date2)

### Costs
- **Storage**: Index uses 10-30% extra disk space
- **Write performance**: INSERT/UPDATE slightly slower (update index too)
- **Index maintenance**: Fragmentation over time (requires REBUILD)

### Should You Index?
|Factor | Index | No Index |
|-------|-------|----------|
| Query frequency | >10x/day | <1x/week |
| Data volume | >100K rows | <10K rows |
| Performance requirement | Sub-second | <5 seconds OK |
| Update frequency | <10x/day | >100x/day |

## Declare Index vs Property Optimization

### Property Optimization (Search Index)
- **Purpose**: Enable full-text search (Elasticsearch)
- **Scope**: Text search (find by keywords)
- **Impact**: Negligible on database performance
- **Use for**: Content search (notes, descriptions)

### Declare Index (Database Index)
- **Purpose**: Enable fast filtering and grouping
- **Scope**: Exact match and range queries
- **Impact**: Faster queries, slower updates
- **Use for**: Reporting, dashboards, filters

### Decision Tree
```
Is property used in reporting WHERE clause?
  ├─ YES → Declare Index
  └─ NO → Check full-text search needed?
            ├─ YES → Property Optimization (Elasticsearch)
            └─ NO → No indexing needed
```

## Index Creation Process

### Phase 1: Design (Dev Environment)
1. Identify candidate properties for indexing
2. Create Declare Index rules
3. Test reports with indexes activated
4. Measure performance improvement
5. Verify no negative side effects

### Phase 2: Pre-Production Validation (UAT)
1. Activate indexes in UAT with **production data volume**
2. Run **performance tests** (suite of critical reports)
3. Monitor **application responsiveness** during index creation
4. Verify **index size** (should not exceed estimates)

### Phase 3: Production Deployment
1. Schedule **maintenance window** (typically Saturday night)
2. Backup production database
3. Activate Declare Index (may take hours for large tables)
4. Verify index creation completed: `SELECT * FROM user_indexes`
5. Run **production validation queries** (critical reports)
6. Monitor **system performance** for 24 hours post-deployment

### Monitoring Index Creation
```
SELECT table_name, index_name, status
FROM user_indexes
WHERE index_name LIKE 'PEGA_%'
ORDER BY created DESC;
```

Status should transition from `CREATING` → `VALID`.

## Debugging "Property Not Available for Reporting"

### Error Message
```
Property Status not available for reporting
Cause: Property not exposed in class structure
```

### Root Causes and Fixes

| Cause | Symptom | Fix |
|-------|---------|-----|
| Property exists but not indexed | Other properties work | Create Declare Index |
| Property is embedded/nested | Can't GROUP BY | Declare Index the parent |
| Property is virtual/calculated | Always unavailable | Use base property instead |
| Class is abstract base | Properties hidden | Add to concrete subclass |
| Access control restricts property | Only certain users see it | Review property access rules |

### Resolution Steps
1. **Verify property exists**: Case class → Data Model → search property name
2. **Confirm property type**: Should be Text, Number, DateTime, Boolean
3. **Create Declare Index**: If not already indexed
4. **Test in report**: Add column, verify it appears
5. **Verify permissions**: User role has access to property

## Optimizing Report Performance with Indexes

### Before Optimization
```
Report: CasesByStatus
SQL: SELECT status, COUNT(*) FROM cases WHERE created > '2024-01-01' GROUP BY status
Execution: 45 seconds (full table scan, 10M rows)
```

### After Adding Indexes
```
Declare Index on [Status, CreatedDate]
Same SQL: 0.2 seconds (index range scan)
45x faster!
```

### Index Maintenance

#### Regular Maintenance
- **Weekly**: Monitor index fragmentation (`DBCC SHOWCONTIG`)
- **Monthly**: Rebuild fragmented indexes (>30% fragmentation)
- **Quarterly**: Review unused indexes, remove if not needed

#### Detecting Fragmentation
```
SELECT index_name, avg_fragmentation_in_percent
FROM index_stats
WHERE avg_fragmentation_in_percent > 30;
```

#### Rebuilding an Index
```
ALTER INDEX idx_case_status ON cases REBUILD;
-- Or during low-traffic window:
ALTER INDEX idx_case_status ON cases REBUILD ONLINE;
```

## Best Practices

- **Index conservatively**: Start with most critical properties
- **Monitor index impact**: Check write performance after indexing
- **Document indexes**: Track which reports use which indexes
- **Size capacity**: 1 index per 100M rows of high-volume tables
- **Review quarterly**: Add/remove indexes based on actual query patterns
- **Test on production-volume data**: Dev indexes may hide problems
- **Use composite indexes**: (Status, CreatedDate) faster than separate indexes
- **Schedule maintenance**: Rebuild fragmented indexes proactively
"""
    }
]

def seed_phase14():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE14:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase14_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE14)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 14 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase14()
