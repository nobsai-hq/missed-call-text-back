# Missed Call Text Back

A free n8n workflow for local businesses. When you miss a call, the caller gets a friendly text right away.

Built by Bobby Ve.

## The problem

You are busy with a customer. The phone rings. You can't pick up.

Most people who reach voicemail don't leave a message. They just call the next shop on the list. That is a lost customer, and you never even knew they called.

## What it does

1. Your phone system tells this workflow when a call ends.
2. If the call was missed (no answer, busy, or failed), the workflow checks a few safety rules.
3. If it is safe, it sends the caller a text like this:

> Hi! Sorry we missed your call at Sample Barber Shop. Book anytime here: https://example.com/book or just reply to this text and we will get back to you. Reply STOP to opt out.

## Safety rules built in

- **Reply STOP to opt out.** Every text says it. If someone replies STOP, they never get another text from this workflow. If they reply START, they are added back.
- **No repeat texts.** The same caller gets at most one text every 12 hours (you can change this).
- **Quiet hours.** No texts before 8 AM or after 9 PM, your local time (you can change this).
- **No blocked numbers.** If the caller's number is hidden, nothing is sent.

## What you need

- An n8n account (cloud or self-hosted).
- A phone number that can send texts and send call alerts. This template is set up for Twilio, but any service with a "send a text" web address can work with small changes.
- Your texting number registered for business texting (in the US this is called A2P 10DLC). Your phone provider walks you through it.

## Setup steps

1. In n8n, click **Import from File** and pick `workflow.json`.
2. Open the **Settings** node. Change the sample values:
   - your business name
   - your booking link
   - your texting number
   - your Twilio Account SID inside the send address
   - your time zone and texting hours
3. Open the **Send Text** node. Add a **Basic Auth** login. The user is your Twilio Account SID. The password is your Twilio Auth Token. Keep these private and never paste them in the workflow itself.
4. Turn the workflow on (Active). Copy the two **Production URLs**:
   - **Call Ended**: paste it in your phone number's "call status changes" setting.
   - **Text Reply In**: paste it in your phone number's "a message comes in" setting.
5. Test it. Call your business number from your own cell and don't answer. You should get the text in a few seconds. Reply STOP and call again. You should NOT get a second text.

## Good to know

- The opt-out list and the "texted recently" list live inside the workflow's own memory. They only save when the workflow is on (Active), not during manual test runs. If you delete the workflow, the lists are gone too.
- Twilio also blocks texts to people who reply STOP on its own. This workflow keeps its own list as a second layer.
- Want the owner to see customer replies? Add a node after **Handle STOP and START** that sends the reply to your email or phone.
- Texting rules differ by place. Check the rules where you do business before you turn this on.

## Files

- `workflow.json`: the n8n workflow to import.
- `build_workflow.py`: the script that makes `workflow.json`, if you want to change it in code.
- `TESTING.md`: what we tested and how.
- `LICENSE`: MIT. Free to use and change.

## Built by

Built by Bobby Ve, No BS AI.

---

**Want it set up for your business? No BS AI does it for you. bobby@nobsai.com**
