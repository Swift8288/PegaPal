"""
Curated Pega Knowledge Base — Phase 20 (Common Java/Pega Runtime Exceptions)
Covers: IndexOutOfBounds, NullPointer, ClassNotFound, ClassCast, NumberFormat,
        StackOverflow, OutOfMemory, ConcurrentModification, Timeout, and more.

Run: python -m crawler.seed_kb_phase20
"""

import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE20 = [
    {
        "url": "curated://pega-index-out-of-bounds",
        "title": "IndexOutOfBoundsException in Pega — Array, String, and Page List Index Errors",
        "content": """# IndexOutOfBoundsException in Pega — Causes and Fixes

## What It Means
An IndexOutOfBoundsException (including ArrayIndexOutOfBoundsException and StringIndexOutOfBoundsException) occurs when code tries to access an element at an index that doesn't exist — for example, accessing item 5 in a list that only has 3 items, or accessing character position 10 in a 5-character string.

## Common Error Messages
- `java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 3`
- `java.lang.StringIndexOutOfBoundsException: String index out of range: -1`
- `java.lang.IndexOutOfBoundsException: Index: 4, Size: 2`
- `Index out of bounds` or `index out of the bound issue`

## Common Causes in Pega

### 1. Page List Index Error in Activities
- Accessing a page list item by index when the list has fewer items than expected
- Example: `MyPageList(5)` when the list only has 3 items
- **Fix**: Always check `.pxResultCount` or use `@(MyPageList).pxResultCount` before accessing by index. Use `For each page in` loops instead of index-based access.

### 2. Java Step Array Access
- Custom Java code in an activity step accessing an array out of bounds
- Example: `String[] parts = input.split(","); String third = parts[2];` when input only has 2 parts
- **Fix**: Add bounds checking: `if (parts.length > 2) { ... }`. Always validate array length before accessing elements.

### 3. Data Transform Iteration Error
- Data Transform iterating over a source page list and writing to a target page list with mismatched sizes
- **Fix**: Use "Append to" target mode instead of index-based mapping. Check source list size.

### 4. Substring/String Operations
- Using `.substring()`, `.charAt()`, or `.indexOf()` on a string that's shorter than expected or empty
- Example: `myString.substring(0, 10)` when myString is only 5 characters
- **Fix**: Check string length first: `if (myString != null && myString.length() >= 10)`.

### 5. Report Definition Column Mapping
- A report tries to map results to page list positions that don't exist
- **Fix**: Verify column count matches expected structure. Handle empty result sets.

### 6. Parse Rule Processing
- JSON or XML parsing where the structure is different than expected (missing array elements)
- **Fix**: Add null/size checks in the parse rule mapping. Handle variable-length arrays.

### 7. Split/ForEach in Flows
- A Split-ForEach shape tries to create iterations based on a page list, but the list is empty or modified during processing
- **Fix**: Add a condition before the split to check if the list is non-empty.

## Debugging Steps
1. **Check the stack trace** — find the exact line number and method name
2. **Identify the index value** — the error message shows which index was attempted (e.g., "Index 5")
3. **Identify the actual size** — the error message shows the actual collection size (e.g., "Size: 3")
4. **Open the rule** — go to the activity step, data transform row, or Java code at that line
5. **Run the Tracer** — trace the interaction and watch page list sizes at each step
6. **Check the Clipboard** — use Clipboard Viewer to inspect the page list before the failing step
7. **Add logging** — add a Property-Set or log step before the failing step to output the list size

## Common Fixes

### Fix: Guard with Size Check (Activity Java Step)
```java
// WRONG — crashes if list has fewer than 3 items
ClipboardPage item = myPageList.getPageValue(3);

// RIGHT — check size first
if (myPageList.size() > 3) {
    ClipboardPage item = myPageList.getPageValue(3);
} else {
    oLog.warn("Expected at least 4 items, found " + myPageList.size());
}
```

### Fix: Use For-Each Instead of Index (Data Transform)
Instead of mapping `Source: MyList(1).Name → Target: .FirstName`, use a For-Each loop:
- For each page in MyList:
  - Append and Map to TargetList

### Fix: Handle Empty Page Lists (Flow)
Add a Decision shape before processing:
- When rule: `MyPageList.pxResultCount > 0` → proceed to processing
- Else → skip to next step or show "no items" message

## Prevention Best Practices
1. Never assume a page list has a specific number of items — always check first
2. Use For-Each loops instead of hard-coded index access
3. Validate external data (API responses, file imports) before processing
4. Add null/empty checks for strings before substring operations
5. Use `.pxResultCount` property to check page list sizes in When rules
"""
    },
    {
        "url": "curated://pega-null-pointer-exception",
        "title": "NullPointerException in Pega — Causes, Debugging, and Prevention",
        "content": """# NullPointerException (NPE) in Pega — Complete Guide

## What It Means
A NullPointerException occurs when code tries to use an object reference that is null (doesn't point to any object). In Pega, this typically means accessing a property on a page that doesn't exist, or calling a method on a null object in Java.

## Common Error Messages
- `java.lang.NullPointerException`
- `java.lang.NullPointerException: Cannot invoke method on null object`
- `Null pointer exception in step X of activity MyOrg-App-Work.MyActivity`

## Common Causes in Pega

### 1. Accessing Properties on a Missing Page
- Referencing `.Customer.Name` when the Customer page doesn't exist on the clipboard
- **Fix**: Check page existence first: use `.pyIsPagePresent` or `@if(.Customer != "", .Customer.Name, "")`

### 2. Data Page Not Loaded
- Referencing a data page property before the data page has been loaded
- Data page load failed silently (connector error, empty result)
- **Fix**: Check if data page loaded: `D_CustomerData.pxResultCount > 0`. Handle empty data pages.

### 3. Null Property in Java Step
- Custom Java code: `String value = tools.findPage("MyPage").getString(".MyProp");` when MyPage doesn't exist
- **Fix**: Null-check: `ClipboardPage page = tools.findPage("MyPage"); if (page != null) { ... }`

### 4. Missing Page in Data Transform
- Data Transform referencing a source page that doesn't exist (e.g., copying from a page not on clipboard)
- **Fix**: Add a condition "When" to the Data Transform row to check page existence.

### 5. Activity Parameter Not Passed
- Activity expects a parameter page but the caller didn't pass it
- **Fix**: Add null check in the first activity step. Set default values for optional parameters.

### 6. Report Definition Returns Empty
- Processing report results without checking if any rows were returned
- **Fix**: Check `.pxResultCount` before accessing result pages.

## Debugging Steps
1. **Read the stack trace** — find the activity name and step number
2. **Open the activity** — go to the failing step
3. **Check the Clipboard** — does the page/property exist? Use Clipboard Viewer.
4. **Run Tracer** — trace the flow and watch for when the page is expected vs when it's actually created
5. **Add null-check logging** — temporarily add a step before the failing one to log page existence

## Prevention
1. Always use `tools.findPage()` with null check in Java steps
2. Use `.pyIsPagePresent` in When rules before accessing pages
3. Set default values in Data Transforms to handle missing data
4. Validate data page loads with `.pxResultCount > 0`
5. Use "Relation to a case" in Data Transforms carefully — ensure the source case exists
"""
    },
    {
        "url": "curated://pega-class-cast-exception",
        "title": "ClassCastException in Pega — Type Mismatch Errors and Fixes",
        "content": """# ClassCastException in Pega — Causes and Fixes

## What It Means
A ClassCastException occurs when code tries to cast an object to a class that it isn't. In Pega, this often happens with page types, property types, or Java object casting.

## Common Error Messages
- `java.lang.ClassCastException: com.pega.pegarules.data.internal.clipboard.ClipboardPropertyStringImpl cannot be cast to ClipboardPage`
- `ClassCastException: Expected page but found scalar property`
- `Cannot cast Data-Party to MyOrg-App-Data-Customer`

## Common Causes

### 1. Property Type Mismatch
- Treating a Single Value property as a Page, or vice versa
- Example: `.CustomerName` is a text property but code tries to access `.CustomerName.FirstName` (treating it as a page)
- **Fix**: Check the property type in the class definition. Use the correct access pattern.

### 2. Page Class Mismatch
- A page is of class `Data-Party` but code expects `MyOrg-App-Data-Customer`
- Common when data transforms or activities copy pages without proper class mapping
- **Fix**: Verify page class in Clipboard Viewer. Use `obj-Open` with correct class. Set page class explicitly in Data Transform.

### 3. Java Casting Error
- Java step casting to wrong type: `(String) tools.findPage("MyPage")` — a page can't be cast to String
- **Fix**: Use correct types: `ClipboardPage page = tools.findPage("MyPage"); String value = page.getString(".MyProp");`

### 4. List vs Single Property Confusion
- Treating a Page List as a single Page, or accessing a single property as a list
- **Fix**: Check property mode (Single, Page, Page List, Value List) in the class definition.

### 5. Data Transform Source/Target Type Mismatch
- Source is a Value List but target is a Page List, or source is a scalar but target expects a page
- **Fix**: Ensure source and target types match in Data Transform rows.

## Debugging Steps
1. Read the stack trace — identify the classes involved in the cast
2. Check the Clipboard — what class is the actual page vs. what was expected?
3. Check the property definition — is it the right type (Single Value, Page, Page List)?
4. Trace the data flow — where did the wrong type originate?
"""
    },
    {
        "url": "curated://pega-concurrent-modification-exception",
        "title": "ConcurrentModificationException in Pega — Thread Safety and Page List Issues",
        "content": """# ConcurrentModificationException in Pega — Causes and Fixes

## What It Means
A ConcurrentModificationException occurs when a collection (like a page list) is modified while it's being iterated over. This is a Java thread-safety issue that commonly appears in Pega during parallel processing or when modifying page lists inside For-Each loops.

## Common Error Messages
- `java.util.ConcurrentModificationException`
- `ConcurrentModificationException during page list iteration`
- `Concurrent modification detected on clipboard page`

## Common Causes

### 1. Modifying Page List Inside For-Each Loop
- Adding or removing items from a page list while iterating over it
- Example: Loop through orders, remove cancelled orders during iteration
- **Fix**: Collect items to remove in a separate list, then remove them after the loop completes. Or iterate in reverse order.

### 2. Parallel Processing Accessing Same Page
- Two threads (parallel flow paths, Split-ForEach) modifying the same clipboard page simultaneously
- **Fix**: Use separate pages for each parallel path. Copy data to thread-local pages before parallel processing. Use synchronization in Java steps.

### 3. Agent/Queue Processor and UI Conflict
- A background agent modifies a case while a user is viewing/editing it simultaneously
- **Fix**: Use proper case locking. Refresh the page after background processing. Use deferred save pattern.

### 4. Declare OnChange Modifying Trigger Page
- A Declare OnChange rule modifying the same page that triggered the change
- **Fix**: Modify a different page, or use a flag to prevent recursive triggering.

### 5. Node-Scoped Data Page Being Updated
- Multiple requestors reading a Node-scoped data page while it's being refreshed
- **Fix**: Use `Reload once per interaction` strategy. Pega handles thread-safety for data pages, but custom code accessing the page might not be thread-safe.

## Debugging Steps
1. Check the stack trace — identify which page list and which operation caused it
2. Check for parallel processing — are there Split shapes or parallel flows?
3. Check for background agents running on the same case
4. Check Declare OnChange rules — are any modifying pages that triggered them?
5. Add synchronization in Java steps if needed: `synchronized(page) { ... }`

## Prevention
1. Never modify a collection while iterating — use a copy or collect changes for after the loop
2. Isolate data in parallel processing — each thread gets its own clipboard pages
3. Use case locking to prevent concurrent modification
4. Test concurrent scenarios — multiple users on the same case, agent + user interactions
"""
    },
    {
        "url": "curated://pega-timeout-connection-exceptions",
        "title": "Timeout and Connection Exceptions in Pega — Network, DB, and Service Errors",
        "content": """# Timeout and Connection Exceptions in Pega — Complete Guide

## Common Timeout/Connection Error Messages
- `java.net.SocketTimeoutException: Read timed out`
- `java.net.ConnectException: Connection refused`
- `java.net.UnknownHostException: Unable to resolve host`
- `java.sql.SQLTimeoutException: Query timeout`
- `com.pega.pegarules.pub.PRTimeoutException: Interaction timeout`
- `org.apache.http.conn.ConnectTimeoutException: Connect to [host] timed out`
- `Connection pool exhausted — no available connections`

## Types of Timeouts in Pega

### 1. HTTP Connect Timeout
- **What**: Can't establish a TCP connection to the external system
- **Cause**: Host unreachable, firewall blocking, DNS failure, wrong port
- **Fix**: Verify hostname/IP. Check firewall rules. Test with `ping`/`telnet`. Check DNS.

### 2. HTTP Read Timeout
- **What**: Connection established but response not received within the time limit
- **Cause**: External system processing slowly, large response, network latency
- **Fix**: Increase read timeout on the connector. Optimize external API. Use async pattern.

### 3. Database Query Timeout
- **What**: SQL query exceeded the database timeout
- **Cause**: Missing index, full table scan, lock contention, large result set
- **Fix**: Add indexes. Optimize query. Increase timeout for batch operations. Check for locks.

### 4. Interaction Timeout
- **What**: Pega's overall interaction time limit exceeded (PEGA0001)
- **Cause**: Combination of slow operations in a single request
- **Fix**: Identify the slowest operation via Tracer/PAL. Optimize or move to async.

### 5. Session Timeout
- **What**: User's session expired due to inactivity
- **Cause**: Session timeout setting too short, user idle, passivation issues
- **Fix**: Adjust session timeout DSS. Implement keep-alive. Warn users before timeout.

### 6. Connection Pool Timeout
- **What**: All database/HTTP connections are in use, new requests wait and timeout
- **Cause**: Too many concurrent requests, slow queries holding connections, connection leak
- **Fix**: Increase pool size. Fix slow queries. Fix connection leaks. Add connection pool monitoring.

## Debugging Connection Issues
1. **Test connectivity**: From the Pega server, `ping` / `telnet` / `curl` the target host
2. **Check DNS**: `nslookup` the hostname from the Pega server
3. **Check firewall**: Are the required ports open between Pega and the target?
4. **Check certificates**: For HTTPS, is the SSL certificate valid and trusted?
5. **Check connection pool**: SMA → Database/Integration → Connection Pool utilization
6. **Check logs**: PegaRULES log for the full exception stack trace with hostname/port details

## Timeout Configuration Reference
| Timeout Type | Where to Configure | Default |
|-------------|-------------------|---------|
| HTTP Connect | Connector rule → Service tab | 10 seconds |
| HTTP Read | Connector rule → Service tab | 30 seconds |
| DB Query | prconfig.xml or DSS | 30 seconds |
| Interaction | DSS: alerts/interaction/threshold | 20 seconds |
| Session | DSS: session/timeout | 30 minutes |
| Connection Pool Wait | prconfig.xml → connection pool settings | 30 seconds |
"""
    },
    {
        "url": "curated://pega-number-format-parse-exceptions",
        "title": "NumberFormatException and ParseException in Pega — Data Conversion Errors",
        "content": """# NumberFormatException and ParseException in Pega

## What They Mean
- **NumberFormatException**: Trying to convert a non-numeric string to a number (Integer, Double, etc.)
- **ParseException**: Trying to parse a string into a date, number, or other format that doesn't match the expected pattern

## Common Error Messages
- `java.lang.NumberFormatException: For input string: "abc"`
- `java.lang.NumberFormatException: For input string: ""`
- `java.lang.NumberFormatException: For input string: "12,345.67"` (locale issue)
- `java.text.ParseException: Unparseable date: "2024/03/15"`
- `NumberFormatException in Data Transform at row 5`

## Common Causes

### 1. Empty String to Number Conversion
- Property is empty/blank but code tries to convert it to Integer or Double
- **Fix**: Check for empty before converting: `@if(.Amount != "", .Amount, "0")`

### 2. Non-Numeric Characters
- User input contains spaces, commas, currency symbols, or letters
- Example: "$1,234.56" can't be parsed as a plain number
- **Fix**: Strip non-numeric characters first. Use Pega's built-in number formatting. Validate input with regex.

### 3. Locale-Specific Number Formatting
- European format uses comma as decimal separator (1.234,56) vs US format (1,234.56)
- **Fix**: Use Pega's localization settings. Be consistent with number format across the application.

### 4. Date Format Mismatch
- External system sends date as "2024/03/15" but Pega expects "20240315" or "2024-03-15T00:00:00.000Z"
- **Fix**: Use Pega's date/time parsing functions. Configure the correct format in the parse rule or connector mapping.

### 5. Property Type Mismatch in Data Transform
- Mapping a Text property to an Integer property without conversion
- **Fix**: Use `@(toInt(.TextProperty))` or set proper type conversion in the Data Transform.

### 6. Integration Response Parsing
- External API returns a number as a string with unexpected format
- **Fix**: Add data cleaning in the response mapping. Handle edge cases (null, empty, non-numeric).

## Debugging Steps
1. Check the stack trace — find the exact property and value being converted
2. Check the Clipboard — what is the actual value of the property? (may have invisible characters)
3. Add logging before the conversion to output the raw value
4. Check for whitespace: values like " 123 " (with spaces) will fail number parsing
5. Check locale settings if numbers work in one environment but not another

## Prevention
1. Validate all user input with Validate rules before processing
2. Set property types correctly (Integer, Double, Text) in the class definition
3. Use Pega's built-in conversion functions instead of Java parsing
4. Handle null/empty values with @if or @default functions
5. Standardize date/number formats across all integrations
"""
    },
    {
        "url": "curated://pega-common-runtime-exceptions-quick-ref",
        "title": "Pega Runtime Exceptions — Quick Reference for All Common Java Errors",
        "content": """# Pega Runtime Exceptions — Quick Reference

## Exception Index (Alphabetical)

### ArrayIndexOutOfBoundsException
- **Cause**: Accessing array element beyond its size
- **Where**: Activity Java steps, Parse rules
- **Quick fix**: Check array.length before accessing. Use bounds checking.

### ClassCastException
- **Cause**: Wrong type — treating text as page, wrong page class
- **Where**: Data Transforms, Activities, Java steps
- **Quick fix**: Check property type (Single/Page/PageList). Verify page class.

### ClassNotFoundException
- **Cause**: Missing JAR or class file
- **Where**: Rule assembly, custom Java compilation
- **Quick fix**: Check classpath. Re-import JARs. Verify class exists.

### ConcurrentModificationException
- **Cause**: Modifying a list while iterating over it
- **Where**: Parallel processing, For-Each loops, agents
- **Quick fix**: Don't modify collection during iteration. Use thread-safe approach.

### ConnectException (Connection Refused)
- **Cause**: Target system not listening on the specified port
- **Where**: REST/SOAP connectors
- **Quick fix**: Verify host:port. Check if target service is running.

### IllegalArgumentException
- **Cause**: Invalid argument passed to a method
- **Where**: Activities, Data Transforms, Java steps
- **Quick fix**: Validate inputs before passing. Check method documentation.

### IllegalStateException
- **Cause**: Object is in wrong state for the requested operation
- **Where**: Case processing, flow execution
- **Quick fix**: Check case status before performing operations. Verify flow state.

### IndexOutOfBoundsException
- **Cause**: Index out of range for a list, string, or array
- **Where**: Page list access, String operations, Activities
- **Quick fix**: Check .pxResultCount before accessing. Use For-Each instead of index.

### NullPointerException
- **Cause**: Accessing a method/property on a null reference
- **Where**: Everywhere — most common Pega exception
- **Quick fix**: Null-check pages with .pyIsPagePresent. Check findPage() != null.

### NumberFormatException
- **Cause**: Converting non-numeric string to a number
- **Where**: Data Transforms, Activities, property conversion
- **Quick fix**: Validate input. Handle empty strings. Check locale.

### OutOfMemoryError
- **Cause**: JVM heap exhausted
- **Where**: System-wide
- **Quick fix**: Increase -Xmx. Fix clipboard bloat. Check for memory leaks.

### ParseException
- **Cause**: Date/number string doesn't match expected format
- **Where**: Date parsing, number formatting, integration responses
- **Quick fix**: Verify format matches. Use Pega's built-in parsing functions.

### SocketTimeoutException
- **Cause**: Network connection or read timed out
- **Where**: REST/SOAP connectors, external calls
- **Quick fix**: Increase timeout. Check network. Verify endpoint.

### StackOverflowError
- **Cause**: Infinite recursion (activity calling itself)
- **Where**: Activities, Declare Expressions (circular)
- **Quick fix**: Break circular dependency. Add recursion limit.

### StringIndexOutOfBoundsException
- **Cause**: String operation at invalid position (substring, charAt)
- **Where**: Activities, Data Transforms, Java steps
- **Quick fix**: Check string.length() before substring/charAt operations.

### UnsupportedOperationException
- **Cause**: Calling an operation not supported on this object type
- **Where**: Trying to modify an unmodifiable collection
- **Quick fix**: Create a mutable copy before modifying.

### WorkLockedException
- **Cause**: Case is locked by another user/thread
- **Where**: Case open, save operations
- **Quick fix**: Wait or force-release lock. Check SMA for lock holders.

## General Debugging Process for Any Exception
1. **Read the full stack trace** — don't just read the first line
2. **Find YOUR code** — skip Pega internal frames, find the line with your rule name
3. **Check the step number** — method name like `MyActivity_step3` tells you it's Step 3
4. **Check the Clipboard** — use Clipboard Viewer to see actual data state
5. **Run Tracer** — reproduce and trace to see what happens step by step
6. **Add temporary logging** — add a log step before the failing step to capture state
7. **Check PegaRULES.log** — full stack trace with more context
"""
    },
]


def seed_phase20():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE20:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase20_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE20)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 20 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase20()
