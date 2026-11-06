# How this template was tested

Date: Nov 1, 2026. Tool: n8n 2.45.7, run locally with npx (free). All phone numbers are fake 555 numbers.

The texting service was swapped for a fake local server, so no real texts were sent and no Twilio account was used. Texting hours were opened to all day for the test.

| # | What we sent in | Expected | Result |
|---|---|---|---|
| 1 | Missed call (no-answer) | Text sent | Pass |
| 2 | Same caller again | No text (12 hour rule) | Pass |
| 3 | Answered call (completed) | No text | Pass |
| 4 | Hidden number (busy) | No text | Pass |
| 5 | Reply "STOP" | Opted out, empty reply sent back | Pass |
| 6 | Opted-out caller misses again | No text | Pass |
| 7 | Reply "start", then missed call | Text sent | Pass |
| 8 | Forwarded call not answered (DialCallStatus=no-answer) | Text sent | Pass |

All 9 runs finished with no errors. The real `workflow.json` (with the Basic Auth login setting) also imports cleanly.

Not tested yet: a real Twilio number and login, real texts to a phone, and the quiet hours rule.
