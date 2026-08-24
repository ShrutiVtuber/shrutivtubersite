/* Tailwind preset mapping utilities onto the design tokens.
 *
 * Every colour resolves to a CSS custom property rather than a literal, so a
 * utility class follows the theme automatically and there is no parallel
 * palette to keep in sync. `bg-page` is correct in Dawn and Dusk without a
 * `dark:` variant anywhere.
 */
const v = (name) => `var(--${name})`;

module.exports = {
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        page: v("surface-page"),
        card: v("surface-card"),
        veil: v("surface-veil"),
        inset: v("surface-inset"),
        ink: { DEFAULT: v("ink"), soft: v("ink-soft"), faint: v("ink-faint") },
        line: { DEFAULT: v("line"), strong: v("line-strong") },
        accent: {
          DEFAULT: v("accent"),
          hover: v("accent-hover"),
          wash: v("accent-wash"),
          on: v("on-accent"),
        },
        rose: { DEFAULT: v("rose"), hover: v("rose-hover"), wash: v("rose-wash") },
        live: { DEFAULT: v("live"), wash: v("live-wash") },
        sky: {
          zenith: v("sky-zenith"),
          mid: v("sky-mid"),
          horizon: v("sky-horizon"),
          line: v("horizon-line"),
        },
      },
      backgroundImage: { sky: v("sky") },
      ringColor: { DEFAULT: v("focus-ring") },
    },
  },
};
