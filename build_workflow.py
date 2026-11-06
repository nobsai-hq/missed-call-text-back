"""Builds workflow.json for the Missed Call Text Back template. Written from scratch by No BS AI."""
import json, uuid

def nid(): return str(uuid.uuid4())

SETTINGS = r"""// EDIT THESE for your business. Sample values only.
const settings = {
  business_name: 'Sample Barber Shop',
  booking_link: 'https://example.com/book',
  // Your texting number, in +1 format. This is a fake sample number.
  from_number: '+15555550100',
  // Twilio send-message address. Put YOUR Account SID in place of YOUR_ACCOUNT_SID.
  sms_api_url: 'https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json',
  timezone: 'America/New_York',
  // Only text between these hours (24 hour clock, local time).
  text_from_hour: 8,
  text_until_hour: 21,
  // Don't text the same caller again within this many hours.
  cooldown_hours: 12,
};
return $input.all().map(item => ({ json: { ...item.json, settings } }));
"""

WAS_MISSED = r"""// Phone systems send a note when a call ends. Here we decide if it was missed.
// Works with Twilio style fields (CallStatus, From, DialCallStatus) and simple JSON test calls.
const MISSED = ['no-answer', 'busy', 'failed', 'canceled', 'missed'];
return $input.all().map(item => {
  const body = item.json.body || item.json;
  const status = String(body.DialCallStatus || body.CallStatus || body.status || '').toLowerCase();
  const caller = String(body.From || body.from || body.caller || '').trim();
  return { json: { settings: item.json.settings, caller_phone: caller, call_status: status, missed: MISSED.includes(status) } };
});
"""

SAFETY = r"""// Safety checks before we text anyone.
// 1) Real looking phone number  2) Not opted out  3) Not texted recently  4) Not quiet hours
const store = $getWorkflowStaticData('global');
store.optedOut = store.optedOut || {};
store.lastTexted = store.lastTexted || {};

return $input.all().map(item => {
  const s = item.json.settings;
  const caller = item.json.caller_phone;
  const now = DateTime.now().setZone(s.timezone);
  let ok = true, reason = 'ok';

  if (!/^\+[1-9]\d{7,14}$/.test(caller)) { ok = false; reason = 'no valid caller number (maybe blocked or private)'; }
  else if (store.optedOut[caller]) { ok = false; reason = 'caller opted out'; }
  else if (store.lastTexted[caller] && (now.toMillis() - store.lastTexted[caller]) < s.cooldown_hours * 3600 * 1000) { ok = false; reason = 'already texted recently'; }
  else if (now.hour < s.text_from_hour || now.hour >= s.text_until_hour) { ok = false; reason = 'quiet hours'; }

  const message = `Hi! Sorry we missed your call at ${s.business_name}. ` +
    `Book anytime here: ${s.booking_link} or just reply to this text and we will get back to you. ` +
    `Reply STOP to opt out.`;

  if (ok) store.lastTexted[caller] = now.toMillis();
  return { json: { ...item.json, ok_to_text: ok, reason, message } };
});
"""

REPLY = r"""// Handles texts people send back. STOP words opt them out. START opts them back in.
const STOP = ['stop', 'stopall', 'unsubscribe', 'cancel', 'end', 'quit'];
const START = ['start', 'unstop', 'yes'];
const store = $getWorkflowStaticData('global');
store.optedOut = store.optedOut || {};

return $input.all().map(item => {
  const body = item.json.body || item.json;
  const from = String(body.From || body.from || '').trim();
  const text = String(body.Body || body.body || body.text || '').trim().toLowerCase();
  let action = 'none';
  if (from && STOP.includes(text)) { store.optedOut[from] = true; action = 'opted_out'; }
  else if (from && START.includes(text)) { delete store.optedOut[from]; action = 'opted_in'; }
  // Any other reply is a real customer message. Forward it to the owner here if you like.
  return { json: { from, text, action } };
});
"""

def code(name, js, pos):
    return {"parameters": {"jsCode": js}, "id": nid(), "name": name,
            "type": "n8n-nodes-base.code", "typeVersion": 2, "position": pos}

def if_node(name, field, pos):
    return {"parameters": {"conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{"id": nid(), "leftValue": "={{ $json." + field + " }}", "rightValue": True,
                                "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                "combinator": "and"}, "options": {}},
            "id": nid(), "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2, "position": pos}

nodes = [
    {"parameters": {"httpMethod": "POST", "path": "missed-call", "options": {}},
     "id": nid(), "name": "Call Ended", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
     "position": [0, 0], "webhookId": nid()},
    code("Settings", SETTINGS, [220, 0]),
    code("Was It Missed?", WAS_MISSED, [440, 0]),
    if_node("Missed?", "missed", [660, 0]),
    code("Safety Checks", SAFETY, [880, -100]),
    if_node("OK to Text?", "ok_to_text", [1100, -100]),
    {"parameters": {"method": "POST", "url": "={{ $json.settings.sms_api_url }}",
                    "authentication": "genericCredentialType", "genericAuthType": "httpBasicAuth",
                    "sendBody": True, "contentType": "form-urlencoded",
                    "bodyParameters": {"parameters": [
                        {"name": "To", "value": "={{ $json.caller_phone }}"},
                        {"name": "From", "value": "={{ $json.settings.from_number }}"},
                        {"name": "Body", "value": "={{ $json.message }}"}]},
                    "options": {}},
     "id": nid(), "name": "Send Text", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
     "position": [1320, -200]},
    {"parameters": {"httpMethod": "POST", "path": "missed-call-reply",
                    "responseMode": "responseNode", "options": {}},
     "id": nid(), "name": "Text Reply In", "type": "n8n-nodes-base.webhook", "typeVersion": 2,
     "position": [0, 400], "webhookId": nid()},
    code("Handle STOP and START", REPLY, [220, 400]),
    {"parameters": {"respondWith": "text", "responseBody": "<Response></Response>",
                    "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "text/xml"}]}}},
     "id": nid(), "name": "Reply OK", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1,
     "position": [440, 400]},
    {"parameters": {"content": "## Missed Call Text Back\nBuilt by Bobby Ve, No BS AI.\n\n1. Edit the **Settings** node.\n2. Add a Basic Auth credential to **Send Text** (Twilio Account SID + Auth Token).\n3. Point your phone number's call status webhook to **Call Ended**, and its text webhook to **Text Reply In**.\n\nEvery text ends with: Reply STOP to opt out.",
                    "height": 300, "width": 420},
     "id": nid(), "name": "Read Me", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
     "position": [-40, -380]},
]
def c(a, b, idx=0): return (a, b, idx)
links = [c("Call Ended","Settings"), c("Settings","Was It Missed?"), c("Was It Missed?","Missed?"),
         c("Missed?","Safety Checks"), c("Safety Checks","OK to Text?"), c("OK to Text?","Send Text"),
         c("Text Reply In","Handle STOP and START"), c("Handle STOP and START","Reply OK")]
connections = {}
for a, b, idx in links:
    connections.setdefault(a, {"main": [[]]})["main"][idx].append({"node": b, "type": "main", "index": 0})

wf = {"name": "Missed Call Text Back (No BS AI template)", "nodes": nodes, "connections": connections,
      "active": False, "settings": {"executionOrder": "v1"},
      "meta": {"templateCredsSetupCompleted": False, "builtBy": "Bobby Ve, No BS AI"}, "tags": []}
json.dump(wf, open("workflow.json", "w"), indent=2)
print("ok")
