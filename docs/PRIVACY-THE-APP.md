# The privacy policy has to cover the app before it can be submitted

Apple requires a privacy policy URL, and the reviewer reads the page. Ours
currently opens with *"This policy covers shrutivtuber.com"* — which is true,
and which is exactly the sentence that gets an app rejected.

**Three changes, all from the admin, no deploy.** Every fact below was read out
of the app's source, not assumed. Read it and change anything that is not how
you want it said — it is your policy, and these are claims you have to stand
behind.

---

## 1. Amend the section `what` — one sentence

Replace the first sentence:

> This policy covers shrutivtuber.com.

with:

> This policy covers shrutivtuber.com and **Shruti's Astrolabe**, the app for
> Android and iPhone.

Leave the rest of that section alone.

---

## 2. New section — key `app`, title "If you use the app"

Put it after `charts` and before `newsletter`.

```markdown
The app is the same tools, on a phone. It talks to **this site and nowhere
else**, apart from the notification services named below, and it has no
analytics, no advertising and no tracking in it of any kind.

**The sky is computed on the phone.** A chart, a station table, the planetary
hours — the arithmetic happens on the device, from tables built into the app.
What you type to cast a chart is used there and then and is **not sent to any
server**, including this one.

**What the app keeps on your phone**, and nowhere else:

- the place you chose, so it does not have to ask again
- whether you count sunrise by the disc's edge or its centre
- whether you asked for notifications, and this phone's notification address
- if you signed in, the token that keeps you signed in

All of it goes when the app does. Deleting the app deletes the lot; there is
no copy of it here.

**If you sign in**, the app uses the account you already have, under the
section above. It is the same account and the same data — there is not a
separate app one.

**If you turn notifications on**, the phone is given an address by Google's
Firebase Cloud Messaging, and that address is registered here so a notice can
be sent to it. Turning notifications off deletes the registration, and so does
signing out. Nothing is sent to a phone that has not asked.

**The limit of that, said plainly.** A phone can only be woken by Google's
service or Apple's, and using either means that service knows this app is
installed on your phone and holds the address notices go to. That is inherent
in push notifications rather than a choice made here, and the only way to
avoid it entirely is to leave notifications off — which costs you nothing else
in the app.
```

---

## 3. Amend the section `processors` — two lines

Add to the list:

```markdown
- **Google (Firebase Cloud Messaging)** — carries notifications to Android
  phones, and holds the address of the phone each one goes to.
- **Apple (Push Notification service)** — the same, for iPhones.
```

The "no analytics company is on this list" paragraph underneath stays true and
should stay where it is.

---

## Then

Tell me and I will set the privacy URL on the App Store listing to
`https://shrutivtuber.com/privacy`. Until the page says the app is covered,
pointing Apple at it is worse than pointing them at nothing.
