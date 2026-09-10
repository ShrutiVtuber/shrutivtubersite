import React from 'react';
/* An astronomical mark, set in the bundled AstroSymbols cut. Type, never emoji:
   every glyph is emitted with U+FE0E so no colour-emoji font can claim it. */
export const MARKS = {
  sun:'\u2609', moon:'\u263E', waxing:'\u263D', mercury:'\u263F', venus:'\u2640',
  mars:'\u2642', jupiter:'\u2643', saturn:'\u2644', uranus:'\u2645', neptune:'\u2646',
  pluto:'\u2647', node:'\u260A', southnode:'\u260B', retrograde:'\u211E',
  degree:'\u00B0', arcmin:'\u2032', arcsec:'\u2033',
  aries:'\u2648', taurus:'\u2649', gemini:'\u264A', cancer:'\u264B', leo:'\u264C',
  virgo:'\u264D', libra:'\u264E', scorpio:'\u264F', sagittarius:'\u2650',
  capricorn:'\u2651', aquarius:'\u2652', pisces:'\u2653'
};
const SIZES = { sm:13, md:16, lg:22, xl:34 };
export function Glyph({ name, char, size='md', tone='ink', label, style, ...rest }) {
  const c = (char || MARKS[name] || '') + '\uFE0E';
  const color = { ink:'var(--ink)', soft:'var(--soft)', faint:'var(--faint)', gilt:'var(--gilt)',
    accent:'var(--accent)', rose:'var(--rose)', hour:'var(--hour)', live:'var(--live)',
    inherit:'inherit' }[tone] || tone;
  return <span className="t-glyph" role={label?'img':undefined} aria-label={label}
    aria-hidden={label?undefined:'true'}
    style={{ fontFamily:'var(--font-glyph)', fontSize:(SIZES[size]||size)+'px', lineHeight:1,
      color, fontVariantEmoji:'text', display:'inline-block', ...style }} {...rest}>{c}</span>;
}
