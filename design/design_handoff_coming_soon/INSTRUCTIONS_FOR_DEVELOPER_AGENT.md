# Instructions for the implementing agent — coming-soon page

Read `README.md` in this folder in full before touching anything. It is short.

**`index.html` in this folder is the deliverable.** It is finished, self-contained, and needs no
build step. Your job is to deploy it and do the four small jobs in README §3 — not to rebuild it.

## Your mandate

**Implement the design 1:1. Do not interpret it.**

## Do

1. Deploy `index.html` at the domain.
2. Replace the placeholder `S` array with real station times from `GET /stations/next`; geolocate
   with an Athens fallback.
3. Wire the subscribe form to `/newsletter/subscribe` with the **mandatory** double opt-in.
4. Fill in the five social links and the language links — or remove any that do not exist yet.
5. Point the Attic / Hindu / Thelemic reckonings at `GET /today`, or set them per deploy.

## Do not

1. **Do not rebuild it in a framework.** No React, no bundler, no CSS framework. A holding page that
   needs a build pipeline is a liability.
2. **Do not change the headline** to "Coming soon", and do not add a countdown to a launch date or a
   percentage-complete bar. The page states what is true.
3. **Do not remove the live station countdown.** It is the reason this page is not a placard.
4. **Do not weaken the consent copy.** The commercial intent is named at the point of collection on
   purpose, and nobody is subscribed before clicking the confirmation link.
5. **Do not fill in or delete the bracketed imprint values.** Ship the brackets; the client supplies
   them once the company is registered.
6. **Do not add artwork**, stock or generated. The design is built to look finished without it.
7. **Do not say "live"** in the status pill unless she is actually streaming.
8. **Do not leave `href="#"` in production.** Real link or no link.
9. **Do not remove `noindex`** until the full site launches.
10. **Do not add a theme switch, a cookie banner for a page that sets no cookies, or a modal.**

## When the design is silent

Ask. Do not resolve it in code.
