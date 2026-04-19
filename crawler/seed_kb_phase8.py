"""
Curated Pega Knowledge Base — Phase 8 (Mobile, Channels & Digital Messaging)
Run: python -m crawler.seed_kb_phase8
"""
import json, logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DOCS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CURATED_DOCS_PHASE8 = [
    {
        "url": "curated://pega-mobile-client-native-app-development",
        "title": "Pega Mobile Client — Native App Development",
        "content": """
# Pega Mobile Client — Native App Development

## Overview
Pega Mobile Client enables native iOS and Android applications that leverage Pega's case management and business process capabilities while providing offline-first architecture and device-level integrations.

## Mobile Client Architecture

### Core Components
- **Pega Mobile Client SDK**: Native iOS/Android libraries bundled with Pega 8.4+
- **Mobile App Design Studio**: Low-code UI builder for mobile screens
- **Offline Mode Engine**: Local SQLite DB syncs with Pega server
- **Device Channel**: Secure communication layer for push/biometric auth
- **Sync Framework**: Intelligent delta-sync to minimize bandwidth

### App Structure
```
AppDelegate/MainActivity
  ↓
PegaSDK Initialization
  ↓
Authentication (OAuth2/Kerberos)
  ↓
Local Data Cache (SQLite)
  ↓
WorkList/Case List UI
```

## Building Mobile Apps with Pega

### Getting Started
1. **Create Mobile App Rule** in Designer Studio (App > Mobile)
2. **Define Portal** mapped to mobile rules and screens
3. **Generate SDK** and integrate into native project
4. **Configure Channels**: Add iOS Bundle ID and Android package name in Mobile Channel settings
5. **Test** on device or emulator

### Mobile-Specific UI Considerations
- Keep layouts simple; test on multiple screen sizes (4.7" to 6.9")
- Use section rules optimized for mobile (single column preferred)
- Avoid complex layouts that don't respond to portrait/landscape
- Text must be readable at 16sp minimum (Android) or 12pt (iOS)
- Touch targets minimum 44x44 pts for usability
- High DPI images; test scaling on 2x/3x retina displays

### Offline Mode & Sync
**When to Use Offline**: Intermittent connectivity, field operations, data entry without network

#### Enabling Offline Sync
1. Mark Data Objects eligible for offline in **Mobile Channel settings**
2. Set **sync trigger interval** (default 30s)
3. Configure **conflict resolution**: Last-write-wins or user prompt
4. Test with WiFi disabled on device

#### Sync Debugging
- Check **Activity Log** for sync errors (Designer > System > Activity)
- Verify authentication token validity before/after offline usage
- Monitor local DB size; clear cache if >500MB
- Use Charles Proxy to inspect sync payloads

### Push Notifications Setup

#### iOS (APNs)
1. Obtain **APNs certificate** from Apple Developer account
2. Upload cert to **Pega > Environment > Mobile Certificate Management**
3. Enable **Push Enabled** in Mobile Channel
4. Test via Designer > Mobile > Test Notifications

#### Android (FCM)
1. Create FCM project in Google Cloud Console
2. Obtain **Server API Key** and upload to Pega
3. Enable in Mobile Channel (Android tab)
4. Devices auto-register on first app launch

**Push Payload Limits**: iOS 4096 bytes, Android 4096 bytes. Test with large case titles.

### Mobile Channels Configuration
- **Channel Name**: iOS_Production, Android_Production (or variants)
- **Allowed Users**: Restrict by role/org unit
- **Token Expiry**: 24h default; increase for field workers
- **Request Timeout**: 30s for 4G, 60s for 3G
- **Compression**: Enable for low-bandwidth scenarios

## Common Mobile Issues & Debugging

### Issue: "Authentication Failed" on Mobile
- Check **token expiry** and sync before expiry
- Verify **Kerberos keytab** if using AD auth
- Test with **Postman** using OAuth2 flow
- Enable API logging: `System.setProperty("pega.mobile.debug", "true")`

### Issue: Case Data Not Syncing
- Verify **Data Object** is marked sync-eligible
- Check **Offline Rules** exist for case type
- Monitor **Activity Log** for sync failures (error code 409 = conflict)
- Clear app cache and force full sync

### Issue: Push Notification Not Received
- Verify **device token registered** (Activity Log > Device Events)
- Check **APNs/FCM certificates** not expired
- Confirm notification **rule enabled** and **channel mapped**
- Test with Designer notification tester; validate payload

### Issue: High Battery Drain
- Reduce **sync frequency** (increase interval to 5m for non-critical data)
- Disable **location tracking** if not needed
- Disable **real-time updates** for read-only data
- Profile with Xcode Instruments / Android Profiler

## Debugging Tools

### Mobile Debugging Console
```
Designer > System > Logs > Mobile
  → Filter by Device ID
  → Monitor sync, auth, UI render events
```

### Network Inspection (Charles Proxy)
1. Install Charles on development machine
2. Route device traffic through Charles
3. Inspect HTTPS payloads (decrypt with MITM cert)
4. Monitor request/response sizes and latency

### Offline Database Inspector
- iOS: Use Xcode DB Browser plugin
- Android: Use Android Studio Database Inspector
- Verify schema matches Pega Data Objects
"""
    },
    {
        "url": "curated://pega-cosmos-constellation-for-mobile",
        "title": "Pega Cosmos/Constellation for Mobile",
        "content": """
# Pega Cosmos/Constellation for Mobile

## Overview
Constellation is Pega's modern responsive UI framework shipping with Pega 8.5+. It automatically adapts to mobile, tablet, and desktop without custom rules, enabling true mobile-first design.

## Constellation UI on Mobile Devices

### Responsive Grid System
Constellation uses **CSS Grid** with breakpoints:
- **Mobile**: 0–480px (1 column)
- **Tablet**: 481–1024px (2 columns)
- **Desktop**: 1025px+ (3-4 columns)

Layouts automatically reflow without rule changes. Test across all breakpoints in Designer.

### Mobile-First Design Patterns

#### Navigation
- **Hamburger Menu** collapses on mobile (drawer pattern)
- **Top Navigation Bar** shows 1-2 priority actions on mobile
- **Tab Bar** for primary sections (max 4 tabs)
- Back button auto-added on iOS; use Android system back

#### Forms
- Single column on mobile (stack fields vertically)
- Large touch targets: 48px minimum height
- Keyboard-aware: UI scrolls above soft keyboard
- Error messages inline, not modals
- Validation on blur, not submit

#### Lists/Tables
- Card layout on mobile (1 per row)
- Column hiding: Show name + 1-2 key fields on mobile
- Horizontal scroll for overflow (poor UX; prefer redesign)
- Pagination: 10-20 items per page on mobile

### Constellation vs Classic UI on Mobile

| Feature | Constellation | Classic UI |
|---------|---------------|-----------|
| Responsive | Auto (CSS Grid) | Manual (section rules) |
| Touch UX | Optimized (48px targets) | Limited |
| Offline | Built-in support | Requires custom rules |
| Theme | Light/Dark auto-switch | Limited theming |
| Performance | Mobile-optimized | Can be heavy on 3G |

**Migration Path**: Classic UI apps can coexist with Constellation; new mobile should use Constellation.

## Common Mobile Rendering Issues

### Issue: Layout Breaks on Landscape
- Check **Constellation breakpoints** in rule definition
- Verify **no hard-coded width/height** in sections
- Test on iPad and Android tablets
- Use Designer **mobile preview** tool (toggle portrait/landscape)

### Issue: Text Too Small on High-DPI
- Constellation should auto-scale via `viewport-scale`
- Verify **meta viewport tag** in portal HTML
- Check font-size > 16px (minimum readable)
- Inspect with Chrome DevTools: `Device Pixel Ratio`

### Issue: Form Inputs Hidden Behind Keyboard
- iOS: Scroll handled automatically by Pega
- Android: **softInputMode="adjustPan"** in manifest
- Test with phone form factors in DevTools
- Use **focus handlers** to scroll critical fields visible

### Issue: Images Not Scaling on Mobile
- Use **responsive image rule** (new in Constellation)
- Specify `srcset` for different DPIs
- Avoid hardcoded `width/height` attributes
- Use **picture element** for art direction

### Issue: Slow Performance on 4G
- Profile with **Chrome DevTools > Network tab**
- Reduce **JavaScript payload**: disable unnecessary plugins
- **Lazy-load images** below the fold
- **Minimize CSS**: Constellation CSS is tree-shaken

## Debugging Tools

### Designer Mobile Preview
```
Designer > App > Portal > [Portal Name]
  → "Preview on Mobile" button
  → Shows responsive layout in real-time
  → Slow but useful for quick checks
```

### Chrome DevTools Remote Debugging (Android)
1. Enable **Developer Mode** on Android device
2. Open Chrome, navigate to `chrome://inspect`
3. Connect device via USB
4. Inspect Pega app WebView
5. Monitor Network, Console, Performance tabs

### iOS Safari Remote Debugging (macOS)
1. Enable **Web Inspector** on iOS (Settings > Safari > Advanced)
2. Open Safari on Mac, **Develop > [Device] > [App]**
3. Inspect WebView (Constellation uses WebKit)

### Lighthouse Audits
```
Run Lighthouse (Chrome DevTools > Lighthouse)
  → Focus on Accessibility, Best Practices
  → Target: Accessibility > 85, Performance > 70
```
"""
    },
    {
        "url": "curated://pega-web-mashup-embedding-pega-external-sites",
        "title": "Web Mashup — Embedding Pega in External Sites",
        "content": """
# Web Mashup — Embedding Pega in External Sites

## What is Web Mashup?

Web Mashup embeds Pega UI (rules, sections, workspaces) into external web applications via an **iframe or HTML gadget**. Unlike DX API (headless), mashup delivers complete Pega UI with styling and interaction.

### Use Cases
- Embed case portals into vendor/partner websites
- Add process workspaces to intranet portals
- Extend external CRM with Pega workflows
- Multi-application dashboards

## Embedding Pega UI in External Web Apps

### Via iframe
```html
<iframe
  id="pega-mashup"
  src="https://pega-instance.com/prweb/PRIFrame?
       pyWindowName=IframeName&
       pyMode=Embed&
       pyPortal=EmbeddedPortal"
  width="100%"
  height="600"
  sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
>
</iframe>
```

### Via HTML Gadget Rule
1. Create **HTML gadget** in Designer
2. Use **JavaScript mashup library** to load Pega content
3. Embed gadget in external site or CMS

### Key Parameters
- `pyPortal`: Portal rule to load (must be mashup-enabled)
- `pyMode=Embed`: Hides Pega header/footer
- `pyWindowName`: Unique iframe identifier
- `pyDebug=1`: Enable debug logging (development only)

## Authentication for Mashup

### Single Sign-On (SSO) Options

#### OAuth2 with External OIDC Provider
1. Configure **OIDC client** in Pega (System > Manage Security > OAuth2)
2. External app redirects to Pega OAuth2 endpoint
3. Pega returns **session token** to external site
4. External site adds token to iframe URL: `&pyAuthToken=xyz`

#### Kerberos/NTLM (Windows Auth)
- Pega and external site must be on same domain
- Browser auto-negotiates auth; no token needed
- `sandbox` attribute must NOT include restrictions

#### Custom JWT
1. External app issues **JWT** signed with Pega's public key
2. Pega validates JWT signature
3. Create session from JWT claims
4. Pass JWT in `Authorization: Bearer` header

### Session Timeout Handling
- Pega session expires after inactivity (default 30m)
- External site must **refresh token** before expiry
- Implement **keepalive heartbeat** (POST every 20m)
- Detect logout: `message` event from iframe signals session end

## Cross-Origin Issues (CORS)

### Common CORS Errors
```
Access-Denied: XMLHttpRequest from "external.com"
  → "pega-server.com" blocked by CORS policy
```

### Solutions

1. **CORS Headers** in Pega (System > Manage Security > CORS)
   ```
   Allowed Origins: https://external.com
   Allowed Methods: GET, POST, PUT, DELETE
   Allowed Headers: Authorization, Content-Type
   Allow Credentials: Yes
   ```

2. **Preflight Handling** for custom headers
   - Browser sends OPTIONS request before POST
   - Pega must respond with `Access-Control-Allow-*` headers
   - Pega does this automatically if CORS configured

3. **Credentials/Cookies**
   - Add `withCredentials: true` in JavaScript
   - Iframe must have `sandbox="allow-same-origin"`
   - Verify **SameSite=None; Secure** cookie policy

## Styling/Theming Mashup

### CSS Encapsulation
Pega styles are scoped to `.pega-mashup-container`. External site styles should not conflict.

### Customizing Appearance
1. **Modify Portal theme** in Designer (not recommended)
2. **CSS override** in external page (fragile):
   ```css
   #pega-mashup .pega-button {
     background-color: #custom-color;
   }
   ```
3. **Constellation theming** (Pega 8.5+): Use CSS variables
   ```css
   :root {
     --pega-primary-color: #0077CC;
   }
   ```

### Responsive Sizing
```html
<div id="mashup-container" style="width: 100%; height: auto;">
  <iframe id="pega-mashup" src="..." width="100%"></iframe>
</div>
<script>
// Auto-resize iframe to content height
window.addEventListener('message', (e) => {
  if (e.data.type === 'pega:resize') {
    document.getElementById('pega-mashup').height = e.data.height;
  }
});
</script>
```

## Common Mashup Debugging

### Issue: "CORS Policy: No 'Access-Control-Allow-Origin'"
- Add external origin to **System > Manage Security > CORS**
- Verify Pega server responds with `Access-Control-Allow-Origin: external.com`
- Use **curl** to test:
  ```bash
  curl -i -H "Origin: https://external.com" https://pega-server/prweb/api/...
  ```
- Check for **HTTPS vs HTTP mismatch**

### Issue: Session Expires Inside iframe
- Implement **token refresh** every 20 minutes (before 30m timeout)
- Use `setInterval(() => fetch('/api/keepalive'), 20*60*1000)`
- OR use **persistent session** (not recommended for security)

### Issue: iframe Stuck on Loading
- Check **pyPortal** rule exists and is accessible
- Verify **Pega server reachable** from external site (proxy? firewall?)
- Check **browser console** for JavaScript errors
- Enable `pyDebug=1` and check Activity Log

### Issue: Styling Not Applied / Partial UI
- Inspect iframe DOM: Right-click > Inspect
- Check CSS files are loading (Network tab)
- Verify **no style conflicts** from external site
- Constellation: Ensure CSS variables set in parent page

### Issue: Keyboard/Mouse Not Working Inside iframe
- Check `sandbox` attribute not too restrictive
- Required: `allow-same-origin allow-scripts allow-popups allow-forms`
- Test in incognito (rules out browser cache)
- Check JavaScript event handlers (`onclick` attributes)

## Debugging Tools

### Browser DevTools
- **Elements tab**: Inspect iframe DOM
- **Network tab**: Monitor XHR requests, payload sizes
- **Console tab**: Check for JS errors, Pega debug logs
- **Security tab**: Verify CORS headers, certificate

### Pega Activity Log
```
Designer > System > Activity
  → Filter by Mashup-related rules
  → Check for auth failures, CORS rejections
```

### Charles Proxy
```
Monitor HTTPS traffic between external site and Pega
  → Inspect CORS headers in responses
  → Verify token/session headers present
```
"""
    },
    {
        "url": "curated://pega-digital-messaging-channels",
        "title": "Pega Digital Messaging Channels",
        "content": """
# Pega Digital Messaging Channels

## Overview
Pega Digital Messaging enables omni-channel communication: customers interact via web chat, SMS, WhatsApp, Facebook Messenger, Apple Business Chat, and other channels while maintaining case context.

## Supported Channels

### Synchronous (Real-time)
- **Web Chat**: Embedded JavaScript widget
- **Apple Business Chat (Apple Messages for Business)**: iPhone/iPad native
- **WhatsApp Business**: Customer initiates chat via Business API
- **Facebook Messenger**: Via customer Facebook account

### Asynchronous
- **SMS**: Twilio, Nexmo, or carrier integration
- **Twitter/X Direct Messages**: @-mention or DM
- **Email**: Treat as channel (optional integration)

## Omni-Channel Messaging Architecture

### Message Flow
```
Customer Message (WhatsApp)
  ↓
Channel Adapter (WhatsApp Connector)
  ↓
Pega Message Router (Case/Thread matching)
  ↓
Case Assignment / Queue
  ↓
Agent Response (via Desktop UI or Channel)
  ↓
Routed back to Customer via same Channel
```

### Case-Thread Binding
- Each channel conversation = **Thread** within a Case
- Multiple customer messages → single Thread
- Agent can see **full case history** + **message thread**
- Attachments/media stored in Thread history

## Channel Configuration

### Web Chat Setup
1. **Create Web Chat rule** (Designer > Channels > Web Chat)
2. Configure **queue/assignment rule** (where messages route)
3. Generate **JavaScript widget** embed code:
   ```html
   <script src="https://pega-server/prweb/livechat/launch.js"></script>
   <script>
     PegaLiveChat.launch({
       accountId: 'ACME',
       portalId: 'WebChat_Portal'
     });
   </script>
   ```
4. Embed in website header/footer
5. Configure **available hours** and **offline message**

### WhatsApp Business Integration
1. Apply for **WhatsApp Business API** account (via Meta)
2. Create **Message Template** (pre-approved by WhatsApp)
3. In Pega, configure **WhatsApp Channel** with API credentials
4. Test with **WhatsApp CLI** before go-live
5. Configure **webhook** to receive incoming messages

### SMS Configuration (Twilio Example)
1. Create Twilio account, obtain **SID** and **Auth Token**
2. In Pega, **System > Manage Security > Third-Party Services** add Twilio
3. Create **SMS Outbound Rule** (rule type: Decision Table)
4. Map phone format: normalize to E.164 (+1-555-123-4567)
5. Test sending via Designer

### Apple Business Chat
1. Register with **Apple Business Register**
2. Configure **Apple-specific fields** in Pega channel config
3. Use Apple's **Messages for Business SDK**
4. Enable **Apple Pay integration** if accepting payments

## Routing Messages to Cases

### Thread Matching Logic
1. **Customer identifier**: Phone number, email, or social handle
2. **Lookup existing case**: Search by customer ID and case type
3. **Create new case** if no match
4. **Thread created** under matched case

### Routing Rules
```
Channel Message arrives
  → Extract customer identifier (phone, email, social ID)
  → Search Case by [Customer ID] and [Case Type]
    ├─ Found: Route to existing case thread
    └─ Not found: Create case, assign to queue
  → Notify agent (desktop or mobile)
```

### Custom Routing Logic
Use **Message Router Rule** (new in Pega 8.6):
```
IF channel=SMS AND sender is VIP customer
  THEN assign to Priority Queue
ELSE
  assign to Standard Queue
```

## IVA Integration with Channels

### IVA (Intelligent Virtual Assistant) with Messaging

#### Chatbot Handoff
1. **IVA responds** to customer inquiry (FAQ, simple requests)
2. If escalation needed: **IVA creates case** and notifies agent
3. **Case transferred** to human agent (agent can see IVA transcript)
4. Agent **resumes conversation** in same thread

#### Configuration
- IVA rule type: **Chat Bot** (Designer > Channels > Chat Bot)
- Enable **escalation intent**: If IVA confidence < 70%, escalate
- Map IVA **to case type** (e.g., "Billing Inquiry")
- Set **timeout**: After 5m no IVA response, escalate

#### Common IVA Flows
- Greet customer, route to appropriate channel
- Collect case info (issue description, account number)
- Offer self-service options (check balance, reset password)
- Escalate to agent with rich context

## Debugging Channel Connectivity

### Issue: Messages Not Arriving in Pega
- Check **Channel rule enabled** (Designer > Channels)
- Verify **API credentials** correct (test with vendor's API console)
- Inspect **webhook endpoint**: Is Pega receiving POST requests?
  ```bash
  curl -X POST https://pega-server/rest/channel/webhook \
    -d '{"msg": "test"}' -v
  ```
- Check **Activity Log** for webhook rejections
- Verify **SSL certificate** valid (WhatsApp/Twilio require HTTPS)

### Issue: Agent Not Notified of Incoming Message
- Check **assignment rule** configured in channel
- Verify **queue exists** and **agents assigned** to queue
- Check **agent availability** status (login, do-not-disturb?)
- Inspect **Desktop Activity Log** for assignment failures

### Issue: Customer Messages Show Wrong Format
- Verify **character encoding** (UTF-8 for emoji, international chars)
- Check **message parsing rule** handling special chars
- Test with **Charles Proxy** to inspect raw API payload
- Verify **normalization rule** for phone numbers, emails

### Issue: WhatsApp Template Approval Stuck
- Check **template syntax** matches WhatsApp guidelines
- Submit to WhatsApp via **Meta Business Manager** (not Pega)
- Typical approval: 24-48 hours
- Use **test templates** while waiting for approval

### Issue: Web Chat Not Appearing on Website
- Verify **JavaScript widget URL** not blocked by CSP headers
  ```
  Check: Response Headers > Content-Security-Policy
  Must allow: script-src 'unsafe-inline' https://pega-server
  ```
- Check **embed code on correct page** (test in browser console)
- Verify **portal accessible** to unauthenticated users
- Test in **incognito window** (rules out cached JS)

### Issue: SMS Delivery Delays
- Check **Twilio/Nexmo status** (carrier issues?)
- Verify **phone number format** (E.164 standard)
- Check **rate limiting**: Twilio/Nexmo may throttle high volume
- Inspect **Activity Log** for delivery confirmation status

## Debugging Tools

### Pega Activity Log (Channel Events)
```
Designer > System > Activity
  → Filter: Channels, Message Router
  → Check for webhook, routing, assignment errors
```

### Vendor Dashboards
- **Twilio Console**: Monitor SMS delivery status, logs
- **WhatsApp Cloud API**: Check webhook, message templates
- **Meta Business Manager**: Verify Business Chat integration

### Browser DevTools (Web Chat)
- **Network tab**: Monitor WebSocket (real-time updates)
- **Console tab**: Check for JS errors in widget
- **Security tab**: Verify CSP allows Pega resources

### Charles Proxy (API Debugging)
```
Monitor HTTPS traffic:
  → WhatsApp/Twilio requests/responses
  → Inspect message payload, authentication headers
  → Verify Pega webhook receiving POST requests
```
"""
    },
    {
        "url": "curated://pega-push-notifications-realtime-updates",
        "title": "Push Notifications & Real-time Updates",
        "content": """
# Push Notifications & Real-time Updates

## Overview
Pega supports multiple real-time notification mechanisms: push notifications to mobile devices, in-app Pulse notifications, and server-sent events for desktop clients. Choose based on use case and device type.

## Pega Push Notification Framework

### Architecture
```
Case Updated (Pega Server)
  ↓
Notification Engine (evaluates rules)
  ↓
Push Service (APNs/FCM/Web Push)
  ↓
Device receives notification
```

### Notification Types

#### Push Notifications (Mobile)
- Delivered to device even if app is backgrounded
- Subject line + preview text only (payload size limits)
- User taps notification → app opens to relevant screen
- Example: "New case assigned: Order #12345"

#### In-App Notifications (Pulse)
- Notification center in Pega UI (top-right icon)
- Shows full message, timestamp, action buttons
- Persists until user dismisses
- Appears in desktop and mobile web

#### Real-time Case Updates
- Server-Sent Events (SSE) for live case refresh
- WebSocket for two-way communication
- Agent sees case changes instantly (no polling)
- Example: Co-browse highlighting, live collaboration

## Configuring Mobile Push (APNs/FCM)

### iOS Push (APNs)

#### Prerequisite: APNs Certificate
1. Go to **Apple Developer account > Certificates, IDs & Profiles**
2. Create **App ID** (e.g., `com.example.PegaApp`)
3. Enable **Push Notifications** capability
4. Create **APNs certificate** (development or production)
5. Export as `.p8` file

#### Configure in Pega
1. Designer > System > Manage Security > Mobile Certificates
2. Upload APNs `.p8` file
3. Set **Key ID** and **Team ID** (from Apple account)
4. Create **Mobile Channel** with iOS enabled
5. Map **App ID** to Pega Portal
6. Test via Designer: Mobile > Send Test Notification

#### Certificate Expiry
- Apple certificates valid 1 year
- Set calendar reminder 30 days before expiry
- Renew and upload new cert (no app re-release needed)
- Users won't receive push after cert expires; resolve within 24h

### Android Push (FCM)

#### Prerequisite: FCM Project
1. Create project in **Google Cloud Console**
2. Enable **Cloud Messaging API**
3. Create **Service Account** (JSON key)
4. Download JSON key file

#### Configure in Pega
1. Designer > System > Manage Security > Mobile Certificates
2. Upload FCM JSON key
3. Create **Mobile Channel** with Android enabled
4. Set **Google Project ID**
5. Test via Designer: Mobile > Send Test Notification

#### Server API Key (Legacy)
- Old FCM setup uses **Server API Key**
- Works but deprecated; migrate to **Service Account** (above)
- If using: System > Manage Security > Third-Party Services

## In-App Notifications vs Push

| Aspect | Push | In-App (Pulse) |
|--------|------|----------------|
| **Works Offline** | No (requires network at send time) | Only if app already loaded |
| **Wakes App** | Yes (if backgrounded) | No |
| **Payload** | Limited (4KB) | Full message + actions |
| **User Control** | OS controls (Do Not Disturb, etc.) | Pega controls (settings menu) |
| **Best For** | Urgent, actionable alerts | Informational, detailed updates |

**Recommendation**: Use push for assignments; use in-app for case notes/comments.

## Pulse Notifications

### What is Pulse?
Pega Pulse is the in-app notification system. Notifications appear in a **bell icon** with badge count, expandable to notification center.

### Configure Pulse
1. Create **Notification rule** (Designer > Notif)
2. Set **Trigger condition**: When case updated, assignment created, etc.
3. Define **notification text** (Markdown supported)
4. Enable **sound/badge** for attention
5. Set **action buttons**: Open case, reply, dismiss

### Pulse Template Example
```
Trigger: OnCreate when [Case Type] = "Urgent Request"

Text: "URGENT: {CaseName} assigned to you"
Icon: [alert icon]
Action 1: Open Case → /prweb/list/case/{CaseID}
Action 2: Assign to Colleague → [Dialog]

Delivery: All logged-in users (portal)
Priority: High
Retention: 7 days (auto-expire)
```

## Real-Time Case Updates

### Server-Sent Events (SSE)
```javascript
// Client-side (JavaScript)
const sse = new EventSource(
  '/prweb/api/v2/cases/CASE_ID/subscribe'
);

sse.addEventListener('case-updated', (event) => {
  const caseData = JSON.parse(event.data);
  console.log('Case updated:', caseData);
  // Refresh UI
});

sse.addEventListener('error', () => {
  sse.close();
  // Reconnect after backoff
});
```

### WebSocket (Two-Way)
```javascript
// Co-browsing, real-time collaboration
const ws = new WebSocket(
  'wss://pega-server/prweb/api/v2/cases/CASE_ID/collab'
);

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Shared highlight:', update.field);
};

ws.send(JSON.stringify({
  action: 'highlight',
  field: 'Address'
}));
```

### Configure Real-Time
1. Designer > System > Real-Time Configuration
2. Enable **Server-Sent Events** (or WebSocket)
3. Set **heartbeat interval** (default 30s, reduces to 5s for live collab)
4. Configure **max subscriptions per user** (prevent DoS)

## Notification Debugging

### Issue: Push Notification Not Received
- Verify **APNs/FCM certificate** not expired (renew if needed)
- Check **device token registered**:
  ```
  Designer > System > Activity > Device Events
    → Look for "device-registered" entry
  ```
- Verify **notification rule triggered** (check Activity Log)
- Test with **Designer notification tester**: Mobile > Test Notification
- Check **Do Not Disturb** on device (silences but still delivers)

### Issue: Push Notification Payload Too Large
- APNs: Max 4096 bytes total
- FCM: Max 4096 bytes total
- Limit **case title/description** length in notification
- Remove unnecessary fields from `title`, `body`
- Test: `echo -n '{"aps":{"alert":"..."}}' | wc -c`

### Issue: Pulse Notification Not Appearing
- Check **notification rule enabled** (Active = Yes)
- Verify **trigger condition** met (check with data)
- Inspect **Activity Log** for notification engine errors
- Check **notification retention** not expired
- Clear browser cache (Pulse stores in localStorage)

### Issue: Real-Time Updates Lag/Drop
- Check **heartbeat interval** (too short = excessive traffic)
- Monitor **WebSocket connection**: Browser DevTools > Network
- Look for **connection resets** (firewall, proxy timeout)
- Increase **server timeout** (System > Server Configuration)
- Test with **Charles Proxy** to detect packet loss

### Issue: "Certificate Expired" Error
- Check **APNs/FCM certificate dates** (System > Mobile Certificates)
- For APNs: Generate new `.p8` from Apple Developer
- Upload new cert; old one can be deleted
- Restart Pega (or clear cache) for cert reload
- No app re-release needed for iOS/Android

## Debugging Tools

### Activity Log (Notification Events)
```
Designer > System > Activity
  → Filter: Notification, Device Events, Real-Time
  → Check for certificate errors, rule triggers
```

### Pega Notification Tester
```
Designer > Mobile > Test Notification
  → Select device
  → Send test push
  → Verify receipt on actual device
```

### Browser DevTools (Web Push/SSE)
- **Network tab**: Monitor EventSource connections, latency
- **Console tab**: Check for JS errors in notification handlers
- **Application tab**: Inspect localStorage (Pulse messages)

### FCM/APNs Console
- **Firebase Console**: Monitor FCM delivery, errors
- **Apple Certificate Manager**: Check cert expiry
- **Twilio/Vendor Dashboards**: Verify service status
"""
    },
    {
        "url": "curated://pega-mashup-dx-api-custom-frontends",
        "title": "Pega Mashup & DX API for Custom Frontends",
        "content": """
# Pega Mashup & DX API for Custom Frontends

## Overview
Pega provides two approaches for custom frontends: **Web Mashup** (embed full Pega UI) and **DX API** (headless, API-first). Choose based on needs: mashup for speed, DX API for full control.

## DX API v2 Overview

### What is DX API?
**DX API** (Digital Experience API v2) is a RESTful API enabling applications to interact with Pega without rendering any Pega UI. Build custom UIs in React, Angular, Vue, native mobile, etc.

### Capabilities
- **CRUD operations** on cases and assignments
- **List cases** with filtering, sorting, pagination
- **Case history** and audit trails
- **File upload/download** (attachments)
- **Confirm/resolve actions**
- **Assignments**: Get worklist, take, complete
- **Case search** with complex queries

### API Versioning
- **v2**: Current (Pega 8.4+), stable
- **v1**: Deprecated, do not use
- All examples below use v2

## Building Headless Pega Apps

### Architecture
```
Custom Frontend (React/Angular)
  ↓
HTTP(S) / REST
  ↓
DX API v2 Gateway
  ↓
Pega Business Logic (case management, routing, rules)
  ↓
Database
```

### Example: React App Using DX API
```javascript
import axios from 'axios';

const pega = axios.create({
  baseURL: 'https://pega-server/prweb/api/v2',
  withCredentials: true
});

// Get my assignments
async function getWorklist() {
  const response = await pega.get('/assignments', {
    params: { limit: 20 }
  });
  return response.data.assignments;
}

// Get case details
async function getCase(caseId) {
  const response = await pega.get(`/cases/${caseId}`);
  return response.data.case;
}

// Create new case
async function createCase(caseType, data) {
  const response = await pega.post('/cases', {
    caseTypeID: caseType,
    content: data
  });
  return response.data.caseID;
}

// Complete assignment
async function completeAssignment(assignmentId, action) {
  await pega.post(
    `/assignments/${assignmentId}/actions/${action}`,
    {}
  );
}
```

### Angular/TypeScript Service
```typescript
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class PegaService {
  private api = 'https://pega-server/prweb/api/v2';

  constructor(private http: HttpClient) {}

  getAssignments() {
    return this.http.get(`${this.api}/assignments`);
  }

  createCase(caseType: string, data: any) {
    return this.http.post(`${this.api}/cases`, {
      caseTypeID: caseType,
      content: data
    });
  }
}
```

## React/Angular Consuming DX API

### React Hooks Example
```javascript
import { useState, useEffect } from 'react';

function AssignmentList() {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://pega-server/prweb/api/v2/assignments', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        setAssignments(data.assignments);
        setLoading(false);
      })
      .catch(err => console.error(err));
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <ul>
      {assignments.map(a => (
        <li key={a.ID}>
          {a.name} - {a.caseType}
          <button onClick={() => openCase(a.caseID)}>
            Open
          </button>
        </li>
      ))}
    </ul>
  );
}
```

## Authentication Flow for DX API

### OAuth2 Authorization Code Flow
1. User clicks "Login"
2. Frontend redirects to: `https://pega-server/oauth2/authorize?client_id=YOUR_CLIENT&redirect_uri=...&scope=...`
3. User authenticates with Pega
4. Pega redirects to frontend with **auth code**
5. Frontend sends code to **backend** (secure)
6. Backend exchanges code for **access token** (secret, never expose)
7. Frontend uses access token in API calls: `Authorization: Bearer {token}`

### JWT Token Example
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "xyz..."
}
```

### Adding Token to Requests
```javascript
const token = localStorage.getItem('accessToken');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

fetch('https://pega-server/prweb/api/v2/cases', { headers });
```

## Common DX API Errors

### 401 Unauthorized
- **Cause**: Missing or expired token
- **Solution**: Refresh token or re-authenticate
  ```javascript
  if (error.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  }
  ```

### 403 Forbidden
- **Cause**: User lacks permission to access resource
- **Solution**: Check role/access group in Pega
  ```
  Designer > System > Manage Security > Access Groups
    → Add user to appropriate group
  ```

### CORS: No 'Access-Control-Allow-Origin'
- **Cause**: Frontend origin not allowed
- **Solution**: Add to Pega CORS config
  ```
  System > Manage Security > CORS
    → Allowed Origins: https://localhost:3000
    → Allowed Methods: GET, POST, PUT, DELETE
    → Allow Credentials: Yes
  ```
- Test with curl:
  ```bash
  curl -i -H "Origin: https://localhost:3000" \
    https://pega-server/prweb/api/v2/assignments
  ```

### 400 Bad Request
- **Cause**: Malformed JSON, missing required fields
- **Solution**: Validate payload before sending
  ```javascript
  const payload = {
    caseTypeID: 'ACME-Service-Request', // Required
    content: { Subject: 'Test' }         // May be required
  };
  // Inspect error response body
  console.log(error.response.data);
  ```

### 429 Rate Limited
- **Cause**: Too many requests
- **Solution**: Implement **exponential backoff**
  ```javascript
  async function fetchWithRetry(url, retries = 3) {
    try {
      return await fetch(url);
    } catch (err) {
      if (err.status === 429 && retries > 0) {
        await sleep(Math.pow(2, 4 - retries) * 1000);
        return fetchWithRetry(url, retries - 1);
      }
      throw err;
    }
  }
  ```

## Creating Assignments and Cases via API

### Create Case
```javascript
POST /prweb/api/v2/cases
Content-Type: application/json
Authorization: Bearer {token}

{
  "caseTypeID": "ACME-Service-Request",
  "content": {
    "RequestType": "Technical Support",
    "Description": "Cannot login",
    "Priority": "High",
    "CustomerName": "John Doe"
  }
}

Response:
{
  "caseID": "CASE-12345",
  "status": "Created",
  ...
}
```

### Create Assignment (within Case)
- Assignments are created by **case actions** (flow rules), not directly via API
- To advance case: call action
  ```javascript
  POST /prweb/api/v2/cases/{caseID}/actions/{actionName}
  ```

### List Cases with Filters
```javascript
GET /prweb/api/v2/cases?
    caseType=ACME-Service-Request&
    status=Active&
    limit=50&
    sort=-createdTime

Response:
{
  "cases": [
    { "caseID": "...", "status": "Active", ... },
    ...
  ],
  "totalRows": 147
}
```

### Get Full Case Content
```javascript
GET /prweb/api/v2/cases/CASE-12345

Response:
{
  "caseID": "CASE-12345",
  "caseType": "ACME-Service-Request",
  "status": "Active",
  "content": {
    "RequestType": "Technical Support",
    "Description": "Cannot login",
    ...
  },
  "history": [ ... ],
  "attachments": [ ... ]
}
```

## Mashup vs DX API Comparison

| Aspect | Mashup | DX API |
|--------|--------|--------|
| **Speed to Build** | Fast (embed Pega UI) | Slower (custom UI) |
| **UI Flexibility** | Limited (Pega styles) | Full control |
| **Mobile-Ready** | Yes (responsive) | Yes (headless) |
| **Offline** | Some (app-level) | Must implement |
| **Authentication** | Inherit from Pega | OAuth2 flow |
| **Integration Cost** | Low (just iframe) | Higher (custom frontend) |
| **Best For** | Quick embeds, internal use | Custom branding, mobile apps |

**Hybrid Approach**: Use mashup for admin, DX API for customer portal.

## Debugging DX API

### Use Postman or curl
```bash
# Test endpoint with auth
curl -i -H "Authorization: Bearer {token}" \
  https://pega-server/prweb/api/v2/assignments

# Check response headers (CORS, auth errors)
```

### Browser DevTools Network Tab
- Inspect request headers: `Authorization`, `Origin`
- Check response status: 401, 403, 429?
- Validate JSON response body

### Pega Activity Log
```
Designer > System > Activity
  → Filter: API, Authentication
  → Check for token validation errors
```

### Swagger/OpenAPI Docs
```
https://pega-server/prweb/api/v2/swagger-ui/
  → Interactive API explorer
  → Try endpoints with auth
  → Copy exact curl commands
```
"""
    }
]

def seed_phase8():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for doc in CURATED_DOCS_PHASE8:
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("—", "-").replace("'", "").replace(",", "").replace(".", "")[:80]
        filename = f"phase8_{slug}.json"
        filepath = RAW_DOCS_DIR / filename
        payload = {"url": doc["url"], "title": doc["title"], "content": doc["content"].strip()}
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        count += 1
        logger.info(f"[{count}/{len(CURATED_DOCS_PHASE8)}] Saved: {doc['title']}")
    logger.info(f"\nPhase 8 complete — {count} documents saved to {RAW_DOCS_DIR}")

if __name__ == "__main__":
    seed_phase8()
