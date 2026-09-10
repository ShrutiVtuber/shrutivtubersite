import React from 'react';
/* Long-form: a reading, an article, a licence. EB Garamond at 17/1.65 with a
   38em measure, because these are read on a phone in bed. Glyphs inside prose
   keep their AstroSymbols face; blockquotes take a gilt hairline, not a box. */
export function Prose({ children, size='prose', drop=false }) {
  return (
    <div className={'as-prose' + (drop?' as-prose-drop':'')} style={{
      font:`400 ${size==='small'?'15px':'var(--size-prose)'}/var(--leading-prose) var(--font-display)`,
      color:'var(--ink)', maxWidth:'var(--measure-prose)' }}>
      <style>{`.as-prose>*{margin:0 0 1em}.as-prose>*:last-child{margin-bottom:0}
.as-prose h2{font:600 22px/1.3 var(--font-display);color:var(--ink);margin:1.6em 0 .5em}
.as-prose h3{font:600 var(--size-heading)/1.35 var(--font-body);color:var(--ink);margin:1.5em 0 .4em}
.as-prose strong{font-weight:600}
.as-prose em{font-style:italic;color:var(--soft)}
.as-prose a{color:var(--accent)}
.as-prose blockquote{margin:1.4em 0;padding-left:16px;border-left:1px solid color-mix(in srgb,var(--gilt) 45%,transparent);color:var(--soft);font-style:italic}
.as-prose ul,.as-prose ol{padding-left:1.3em}
.as-prose li{margin-bottom:.4em}
.as-prose code{font-family:var(--font-body);font-variant-numeric:tabular-nums;letter-spacing:.03em;background:var(--inset);border:1px solid var(--line);border-radius:4px;padding:1px 5px;font-size:.9em}
.as-prose hr{border:0;border-top:1px solid var(--line);margin:2em 0}
.as-prose .t-glyph{font-family:var(--font-glyph)}
.as-prose-drop>p:first-of-type::first-letter{float:left;font-size:3.1em;line-height:.82;padding:.06em .1em 0 0;color:var(--gilt);font-weight:500}`}</style>
      {children}
    </div>
  );
}
