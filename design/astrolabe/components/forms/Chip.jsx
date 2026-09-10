import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
/* Chips. Three kinds and they do not mix on one row:
   choice  — pick one of a set (sign, house system)
   filter  — pick any number (feed filters); selected carries a tick, not just a tint
   meta    — not interactive; a fact with a size on it (language packs: "Greek · 2.1 MB") */
export function Chip({ kind='choice', selected=false, disabled=false, leading, trailing, meta,
  onClick, children, ...rest }) {
  css('as-chip',`.as-chip{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:0 12px;border-radius:var(--radius-sm);border:var(--border-w) solid var(--line);background:transparent;color:var(--soft);font:500 var(--size-caption)/1 var(--font-body);cursor:pointer;white-space:nowrap;transition:background var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),color var(--dur-1) var(--ease-out)}
.as-chip:hover{border-color:var(--line-strong);color:var(--ink)}
.as-chip:active{background:var(--veil)}
.as-chip[data-selected=true]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 55%,transparent);color:var(--accent)}
.as-chip[data-kind=meta]{cursor:default;background:var(--inset);color:var(--faint)}
.as-chip[data-kind=meta]:hover{border-color:var(--line);color:var(--faint)}
.as-chip[disabled]{opacity:.38;cursor:not-allowed;pointer-events:none}
.as-chip .as-chip-meta{font-variant-numeric:tabular-nums;color:var(--faint);font-weight:400}
.as-chip[data-selected=true] .as-chip-meta{color:color-mix(in srgb,var(--accent) 75%,var(--faint))}
.as-chip .as-chip-tick{font:600 12px/1 var(--font-body)}`);
  const interactive = kind !== 'meta';
  return <button className="as-chip" data-kind={kind} data-selected={selected||undefined}
    type="button" disabled={disabled||!interactive} aria-pressed={interactive?selected:undefined}
    onClick={onClick} {...rest}>
    {kind==='filter' && selected && <span className="as-chip-tick" aria-hidden="true">✓</span>}
    {leading}
    <span>{children}</span>
    {meta && <span className="as-chip-meta">{meta}</span>}
    {trailing}
  </button>;
}
