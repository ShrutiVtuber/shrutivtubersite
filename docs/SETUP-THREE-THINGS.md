# The three things that need you

Written the night of 9–10 September 2026, for the morning after. Everything in
this document is **built, tested and deployed** — it is dormant because it needs
a credential or a switch that only you can create. Nothing is broken while it
waits: unconfigured is a working state everywhere below, so the site does not
error and the app does not crash.

**Say "walk me through the three things" and I will take them in this order.**
Roughly 15 minutes, 5 minutes, and 2 minutes.

---

## 1. Firebase, so notifications actually leave the building

**Why first:** it is the longest, and it unblocks the feature people install an
app for — knowing you have gone live.

### What you do

1. Go to <https://console.firebase.google.com> and **Add project**. Call it
   anything; `shruti-tools` is fine. Google Analytics is not needed — say no.
2. In the project, **Add app → Android**. It asks for a package name. It is
   exactly:

   ```
   com.shrutivtuber.shruti_tools
   ```

   Nickname and SHA-1 are optional; skip both.
3. It offers **`google-services.json`**. Download it. That is the file I need —
   tell me where it landed and I will put it in place.
4. **Project settings → Service accounts → Generate new private key.** That
   downloads a JSON file. This one is a **secret** — it can send notifications
   as you. Do not paste it into a chat; tell me the path and I will read it
   from disk and put it in `.env` on the server.

### What I do

- Put `google-services.json` in `shruti-tools/android/app/`.
- Add `firebase_core` and `firebase_messaging` to the app.
- Fill in `_registrationToken()` in `lib/services/notifications.dart` — the five
  lines are already written out in the comment above it.
- Set `SHRUTI_FCM_SERVICE_ACCOUNT` on the server and restart the backend.
- Build and install the app on your phone.

### How we know it worked

I turn notifications on in the app on your phone, then publish a test set of
readings for a period nobody will look at, and your phone buzzes. Then I delete
the test readings. If it does not buzz I can see exactly where it stopped —
there is a log line for the token, the send, and FCM's answer.

⚠ **iOS needs an Apple developer account** and a key uploaded to the same
Firebase project. There is no iOS build yet, so this can wait; the backend
already sends the APNs block, so nothing changes on this side when it comes.

---

## 2. MESSAGE_CONTENT, so Discord can talk back

**Why:** the bridge already posts practice submissions INTO your
`#horoscope-practise` channel. This is the other direction — replies in Discord
becoming comments the app sees.

### What you do

1. <https://discord.com/developers/applications> → your bot's application.
2. **Bot** in the sidebar → scroll to **Privileged Gateway Intents**.
3. Turn on **MESSAGE CONTENT INTENT**. Save.
4. Tell me the **channel id** of `#horoscope-practise`. To get it: Discord
   Settings → Advanced → turn on Developer Mode, then right-click the channel →
   **Copy Channel ID**.

### What I do

Set three things in `.env` and start the gateway consumer:

```
SHRUTI_DISCORD_PRACTICE_CHANNEL=<the id you copied>
SHRUTI_INTERNAL_SECRET=<I generate this>
VCORDBOT_INTERNAL_URL=http://bot:8000
```

### How we know it worked

You type something in the channel and it appears on the reading in the app. And
if the intent is still off, we will KNOW rather than guess: Discord then sends
every message with empty content, which looks exactly like a quiet channel — so
the reader counts blanks and writes "MESSAGE_CONTENT is probably off" into the
log rather than sitting there silently.

⚠ If Discord asks you to verify the application before granting the intent, that
is a form and a wait, not a problem. The outbound half keeps working meanwhile.

---

## 3. Your own compatibility test

**Why last:** it is two minutes, and it is only waiting because it needs your
chart and I will not invent a birth moment for you.

### What you do

Cast your chart on the site and **keep** it — `/tools/natal-chart`, then the
keep button. That is all.

### What I do

Point `/compatible-with/shruti` at it, permanently. One call. Re-running it
repoints the existing one rather than refusing, so if you later keep a better
one we just do it again.

### How we know it worked

`/compatible-with/shruti` says "Are you compatible with Shruti?" with a **Take
it** button, and somebody who is not signed in can take it.

---

## What is already working, so you can look at it now

- `/tools/ephemeris` — retrograde bands, the month's eclipses and phases, the
  aspectarian, full width.
- `/tools/horoscope-writing` — the sky in full behind a button, the writing box
  with the whole page, drafts kept to your account when signed in.
- The practice room, in the app's **Practice** tab and at `/api/practice`.
- Editing a published reading, with the correction on the record at
  `/horoscopes/<sign>/<period>/<covers>/history`.
- Everything on a page editable from `/admin/preview`, including pictures.
