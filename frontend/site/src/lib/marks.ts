/* The section's marks — forty-two drawings, ours.
 *
 * ⚠ Only the path data lives here. The designer's files carry a provenance
 * manifest several kilobytes long, and inlining that on every row would cost
 * more than the whole page. The drawing is the path; the wrapper is Icon.astro.
 *
 * ⚠ A mark never carries state. State is the four colours and the four shapes;
 * a slot's mark is the same drawing whether the slot is empty or on the
 * character. The dot at the left says which, the mark says what the place is.
 * Never fill one, never colour one, never draw one above 24px.
 */
export const MARKS = {
  "kind-active": "M12 2v6m0 8v6M2 12h6m8 0h6M6.5 6.5l3 3m5 5 3 3m0-11-3 3m-5 5-3 3",
  "kind-affix": "M4 6h11l5 6-5 6H4zM8 12h6",
  "kind-aspect": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 3a9 9 0 0 1 0 18 6 6 0 0 0 0-18z",
  "kind-board": "M4 4h16v16H4zM4 9.5h16M4 14.5h16M9.5 4v16M14.5 4v16",
  "kind-glyph": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7l5 5-5 5-5-5z",
  "kind-manual": "M5 4h6a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H5zM19 4h-6a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h6zM12 6v12",
  "kind-node": "M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM12 8.5V3m-3 9H3m18 0h-6m-3 3.5V21",
  "kind-progression": "M3 20h5v-5h5v-5h5V5h3M3 20V15",
  "kind-runeword": "M3 8h18v8H3zM8 9.5l2.5 2.5L8 14.5 5.5 12zM16 9.5l2.5 2.5L16 14.5 13.5 12z",
  "kind-set": "M3 7h6v6H3zM15 7h6v6h-6zM9 17h6v4H9zM9 10h6M12 13v4",
  "kind-support": "M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM12 8V3m0 18v-5m-4-4H3m18 0h-5",
  "kind-unique": "M3 18h18M4.5 18 6 7l4 5 2-8 2 8 4-5 1.5 11",
  "slot-belt": "M3 9h18v6H3zM9.5 9v6M14.5 9v6",
  "slot-body": "M8 5h8l2 4-2 1v9H6v-9L4 9z",
  "slot-charm": "M12 8l5 5-5 5-5-5zM12 8V4.5M10.5 4.5h3",
  "slot-feet": "M6 5h4v9l7 3v3H6z",
  "slot-flask": "M10 3h4v4l3.5 8a3 3 0 0 1-2.7 4.3H9.2A3 3 0 0 1 6.5 15L10 7zM7.6 14h8.8",
  "slot-focus": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 8l4 4-4 4-4-4z",
  "slot-hands": "M7 20V9a2 2 0 0 1 4 0v3m0 0V7.5a2 2 0 0 1 4 0V12m0-1.5a2 2 0 0 1 2 2V17a4 4 0 0 1-4 4H9",
  "slot-head": "M5 14a7 7 0 0 1 14 0M4 14h16M8 17.5h8",
  "slot-jewel": "M12 3l7 4.5v9L12 21l-7-4.5v-9z",
  "slot-legs": "M7 4h10v5l-1.5 11H14l-1-9h-2l-1 9H8.5L7 9z",
  "slot-mercenary": "M12 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM4.5 21a7.5 7.5 0 0 1 15 0M18 6l3-3",
  "slot-neck": "M4 5a8 8 0 0 0 16 0M12 13l3 3-3 3-3-3z",
  "slot-quiver": "M7 9h10v12H7zM10 9V3m4 6V3m-2 6V4.5M7 13h10",
  "slot-ranged": "M6 3a14 14 0 0 1 0 18M6 3l13 9L6 21M19 12h-8",
  "slot-ring": "M12 21a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM12 17.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM9.5 5h5l-1 3h-3z",
  "slot-rune": "M8 3v18M8 8l7-5M8 14l7 5M15 3v6",
  "slot-shield": "M12 3l8 2.5V12c0 5-4 7.5-8 9-4-1.5-8-4-8-9V5.5z",
  "slot-socket": "M5 6h14v12H5zM12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z",
  "slot-weapon-1h": "M12 3v11M8.5 14h7M12 14v5M10 19h4",
  "slot-weapon-2h": "M12 2v13M7 15h10M12 15v6M9.5 21h5M12 4.5l2-1.5",
  "stat-armour": "M12 3l8 2.5V12c0 5-4 7.5-8 9-4-1.5-8-4-8-9V5.5zM4 11h16",
  "stat-cold": "M12 2v20M3.5 7l17 10M3.5 17l17-10M12 6.5 9 4.5m3 2 3-2m-3 13 3 2m-3-2-3 2",
  "stat-fire": "M12 21c3.5 0 6-2.4 6-5.5 0-4.5-6-12.5-6-12.5S6 11 6 15.5C6 18.6 8.5 21 12 21zM12 21c-1.6 0-3-1.3-3-3s3-5 3-5 3 3.4 3 5-1.4 3-3 3z",
  "stat-holy": "M12 16.5a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9zM12 2v2.5m0 15V22M2 12h2.5m15 0H22M5 5l1.8 1.8m10.4 10.4L19 19M19 5l-1.8 1.8M6.8 17.2 5 19",
  "stat-life": "M7 4v11a5 5 0 0 0 10 0V4M7 11h10M9.5 4h5",
  "stat-lightning": "M13.5 2 6 13h5l-1.5 9L18 10h-5z",
  "stat-mana": "M12 3 6 13a6 6 0 0 0 12 0zM6.5 14c1.8 0 2.8-1.2 5.5-1.2s3.7 1.2 5.5 1.2",
  "stat-physical": "M12 3l8 18H4zM12 9v6",
  "stat-poison": "M12 21a6 6 0 0 0 4.2-10.3L12 3l-4.2 7.7A6 6 0 0 0 12 21zM9.5 15.5h5",
  "stat-shadow": "M15.5 3a9 9 0 1 0 0 18 7 7 0 0 1 0-18z",
} as const;

export type Mark = keyof typeof MARKS;

export function isMark(name: string): name is Mark {
  return Object.prototype.hasOwnProperty.call(MARKS, name);
}
