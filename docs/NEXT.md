# What is next, in order

Written 2026-08-26 so the queue survives a context reset.

## 1. Design pass on `/compatible` — WITH THE DESIGNER, IN PARALLEL

`docs/DESIGN_REQUEST_COMPATIBLE.md`. Hero, the card showcase, the five bands,
and two to four finished share-card designs. The page works today and looks
like engineers built it, which they did.

**Do not wait on this.** Items 2 and 3 proceed while the designer works.

## 2. SEO and marketing audit — NEXT

**Audit as though the holding page were already down.** It is `Disallow: /`
today, which makes every finding trivially "nothing is indexed" and teaches us
nothing. Assume launch day and audit what will be true then.

Worth covering:

- **Technical:** the sitemap and robots as they will be, canonicals, structured
  data (Person + WebSite on the home page, BlogPosting from BeeRanked on the
  journal, and what is still missing — Product on shop items, Course on
  classes, FAQPage on the answered questions)
- **Content:** what each page is actually trying to rank for, and whether its
  title and description say so. Several are still the designer's placeholder
  phrasing.
- **The instruments as the moat.** Nine working tools nobody else has is the
  strongest organic asset on the site and none of them has a page written to
  be found. "Planetary hours calculator", "pañcāṅga today", "Attic calendar
  converter" are all real searches.
- **`/compatible` as the viral loop**, and what the share card needs to do
  well on each platform.
- **Discoverability she controls:** the journal (BeeRanked exists for this),
  the newsletter, the Discord, and cross-posting.
- **What NOT to do**, given the site's own commitments: no third-party
  analytics, no tracking pixels, no engagement patterns, nothing that trades
  the zero-third-party-request property for a metric.

Measured numbers already gathered, for reference: zero third-party requests on
every page, LCP 139–514ms locally.

## 3. The Discord bot — AFTER THE AUDIT

Her own, on her own server, controlled from the admin panel. ~70 people in the
Discord now, growing. The point is not to save the cost of a hosted bot; it is
that the bot is another surface she owns.

Sketch, not a decision:

- Announce a stream when the live watcher fires — the same transition logic
  that already drives web push, so one source of truth for "she is live"
- Post a new journal entry, and the monthly letter when it goes out
- Run a poll in Discord that is the SAME poll as the one on `/community`
- `/compatible` from Discord — someone runs a command, gets an invite link
- Admin panel: what it posts, where, and an off switch for each

**Do not start this before the audit.** Some of what the audit finds will
change what the bot should announce.

## Still outstanding, not blocking

- **Rotate the live Stripe secret and webhook signing secret.** Both went
  through a chat transcript. She said she would do it herself.
- **The imprint** — the one hard legal blocker left before launch.
- Her content: About, credits, outfits, schedule, horoscopes.
- The BeeRanked description on `/partners` is still a draft in her voice and
  marked as one on the live page.
- Push notifications have never been delivered to a real browser — headless
  Chromium cannot subscribe. The server half is verified against Mozilla's
  live service.
- The library reader with federated search (Perseus, Wikisource, Gutenberg,
  Sefaria, GRETIL) — designed and agreed, not started. Wikisource needs a
  User-Agent; Gutendex 301s and needs redirects followed.
