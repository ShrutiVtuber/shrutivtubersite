/** Shruti — Tailwind v3 preset. Wire into tailwind.config.js: `presets: [require('./tailwind.preset')]`.
 * Colours reference the CSS custom properties from tokens/colors.css, so the
 * three theme states (light / dark / system) keep working without `dark:` variants. */
const shrutiPreset = {
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        page: 'var(--surface-page)', card: 'var(--surface-card)', veil: 'var(--surface-veil)', inset: 'var(--surface-inset)',
        ink: { DEFAULT: 'var(--ink)', soft: 'var(--ink-soft)', faint: 'var(--ink-faint)' },
        line: { DEFAULT: 'var(--line)', strong: 'var(--line-strong)' },
        accent: { DEFAULT: 'var(--accent)', hover: 'var(--accent-hover)', wash: 'var(--accent-wash)', on: 'var(--on-accent)' },
        rose: { DEFAULT: 'var(--rose)', hover: 'var(--rose-hover)', wash: 'var(--rose-wash)' },
        live: { DEFAULT: 'var(--live)', wash: 'var(--live-wash)' },
        sky: { zenith: 'var(--sky-zenith)', mid: 'var(--sky-mid)', horizon: 'var(--sky-horizon)', line: 'var(--horizon-line)' },
      },
      fontFamily: {
        display: ['"EB Garamond"', '"Noto Serif Devanagari"', 'Georgia', 'serif'],
        body: ['Commissioner', 'Mukta', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Noto Sans Devanagari"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        hero: ['var(--text-hero)', { lineHeight: '1.08', letterSpacing: '-0.01em' }],
        h1: ['2.25rem', { lineHeight: '1.2' }], h2: ['1.75rem', { lineHeight: '1.2' }], h3: ['1.375rem', { lineHeight: '1.2' }],
        prose: ['1.1875rem', { lineHeight: '1.72' }], micro: ['.75rem', { lineHeight: '1', letterSpacing: '.14em' }],
      },
      spacing: { 1: '4px', 2: '8px', 3: '12px', 4: '16px', 5: '24px', 6: '32px', 7: '48px', 8: '64px', 9: '96px' },
      borderRadius: { sm: '4px', md: '10px', lg: '16px', full: '999px' },
      boxShadow: { 1: 'var(--shadow-1)', 2: 'var(--shadow-2)', 3: 'var(--shadow-3)' },
      transitionTimingFunction: { out: 'cubic-bezier(.2,.7,.3,1)', 'in-out': 'cubic-bezier(.45,0,.25,1)' },
      transitionDuration: { 1: '120ms', 2: '240ms', 3: '600ms' },
      maxWidth: { page: '1120px', prose: '66ch' },
      backgroundImage: { sky: 'linear-gradient(180deg,var(--sky-zenith) 0%,var(--sky-mid) 58%,var(--sky-horizon) 100%)' },
    },
  },
};
if (typeof module !== "undefined" && module.exports) module.exports = shrutiPreset;
else if (typeof window !== "undefined") window.shrutiTailwindPreset = shrutiPreset;
