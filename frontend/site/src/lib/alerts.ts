/* What an alert says, and how long it stays.
 *
 * Pure functions over an event, so the whole family can be asserted without a
 * browser, a stream, or somebody actually cheering.
 *
 * The design's rule (handoff §6): one skeleton, nine members, and the glyph
 * carries the KIND of event rather than the platform — which is why nothing
 * here mentions Twitch or YouTube outside the eyebrow. She intends to leave
 * both.
 */

/* Text presentation. Without U+FE0E a client swaps in a colour-emoji font and
   ignores `color`, and the mark stops being type. */
const TEXT = "︎";

export interface RawEvent {
  id: number;
  source: string;
  who: string;
  amountMinor: number;
  currency: string;
  quantity: number;
  message: string;
}

export interface Alert {
  id: number;
  glyph: string;
  eyebrow: string;       // names the door it came through
  headline: string;      // names the person
  amount: string;        // the slot every kind shares
  unit: string;
  message: string;
  hold: number;          // ms
  tone: "accent" | "rose";
  quiet: boolean;        // the follow, and only the follow
}

const SYMBOL: Record<string, string> = { eur: "€", gbp: "£", usd: "$" };

function money(minor: number, currency: string): string {
  const whole = minor / 100;
  return `${SYMBOL[currency] ?? ""}${whole % 1 === 0 ? whole.toFixed(0) : whole.toFixed(2)}`;
}

/* Hold durations are from the handoff's table and are not arbitrary: a gift
   bomb earns six seconds because it names two people and a count, a follow
   earns 1.8 because it names one person and nothing else. */
const SPEC: Record<string, {
  glyph: string; eyebrow: string; hold: number;
  tone: "accent" | "rose"; quiet?: boolean;
  unit: (e: RawEvent) => string;
  amount: (e: RawEvent) => string;
}> = {
  "stripe.support": {
    glyph: `♀${TEXT}`, eyebrow: "Support", hold: 4200, tone: "accent",
    amount: (e) => money(e.amountMinor, e.currency), unit: () => "",
  },
  "stripe.membership": {
    glyph: `♀${TEXT}`, eyebrow: "A membership begins", hold: 4800, tone: "accent",
    amount: (e) => money(e.amountMinor, e.currency), unit: () => "per month",
  },
  "stripe.shop": {
    glyph: `♀${TEXT}`, eyebrow: "From the shop", hold: 4200, tone: "accent",
    amount: (e) => money(e.amountMinor, e.currency), unit: () => "",
  },
  "youtube.superchat": {
    glyph: `♀${TEXT}`, eyebrow: "Super Chat", hold: 4800, tone: "accent",
    amount: (e) => money(e.amountMinor, e.currency), unit: () => "",
  },
  "twitch.sub": {
    glyph: `♃${TEXT}`, eyebrow: "Subscribed", hold: 4200, tone: "accent",
    amount: () => "1", unit: () => "subscription",
  },
  "twitch.gift": {
    // Longer, and the giver is the one named — they are the one being thanked.
    glyph: `☿${TEXT}`, eyebrow: "Gifted", hold: 6000, tone: "accent",
    amount: (e) => String(e.quantity),
    unit: (e) => (e.quantity === 1 ? "recipient" : "recipients"),
  },
  "twitch.bits": {
    // Bits are never converted to money. They are not money.
    glyph: `☉${TEXT}`, eyebrow: "Cheered", hold: 4200, tone: "accent",
    amount: (e) => e.quantity.toLocaleString("en-GB"), unit: () => "bits",
  },
  "twitch.raid": {
    // Different in KIND, not degree — somebody arrived with a crowd.
    glyph: `♂${TEXT}`, eyebrow: "A crowd arrived", hold: 5400, tone: "rose",
    amount: (e) => String(e.quantity), unit: () => "viewers",
  },
  "course.signup": {
    glyph: `☾${TEXT}`, eyebrow: "Joined a class", hold: 4800, tone: "accent",
    amount: () => "1", unit: () => "seat",
  },
  "workshop.signup": {
    glyph: `☾${TEXT}`, eyebrow: "Joined a workshop", hold: 4800, tone: "accent",
    amount: () => "1", unit: () => "seat",
  },
  "twitch.follow": {
    /* The design problem of the whole set. Constant, carries no amount, and
       alerting loudly on it is the commonest way a stream becomes unwatchable
       — so no glyph, no amount, no unit, the shortest hold there is, and a
       flag that strips it of its plate entirely. */
    glyph: "", eyebrow: "Followed", hold: 1800, tone: "accent", quiet: true,
    amount: () => "", unit: () => "",
  },
};

export function toAlert(e: RawEvent): Alert | null {
  const spec = SPEC[e.source];
  if (!spec) return null;      // a source we do not draw is ignored, not guessed
  return {
    id: e.id,
    glyph: spec.glyph,
    eyebrow: spec.eyebrow,
    /* Anonymous is a name, deliberately, not a failed lookup — Twitch permits
       anonymous cheers and gifts and a blank would look broken. */
    headline: e.who || "Someone",
    amount: spec.amount(e),
    unit: spec.unit(e),
    /* Absent unless a person has read it. The plate is two lines instead of
       three rather than showing an empty capsule, and an unmoderated alert
       fires WITHOUT its message rather than waiting for one. */
    message: e.message || "",
    hold: spec.hold,
    tone: spec.tone,
    quiet: Boolean(spec.quiet),
  };
}

export const KINDS = Object.keys(SPEC);
