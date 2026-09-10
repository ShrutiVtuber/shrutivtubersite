import React from 'react';
/* The drawn moon phase disc. A real drawing, not a glyph — it is correct for any
   fraction of the cycle and it reads at 16px. phase: 0=new, .25=first quarter,
   .5=full, .75=last quarter. Colour is never the only signal: pass `label`. */
export function MoonDisc({ phase=0.5, size=28, label, showLabel=false, tone='gilt' }) {
  const r = size/2, lit = { gilt:'var(--gilt-bright)', ink:'var(--ink)', soft:'var(--soft)' }[tone] || tone;
  const p = ((phase % 1) + 1) % 1;
  const k = Math.cos(2*Math.PI*p);          /* terminator half-width, -1..1 */
  const waxing = p < 0.5;
  const rx = Math.abs(k)*r;
  const sweepOuter = waxing ? 1 : 0;
  const sweepInner = (waxing ? (k>0?0:1) : (k>0?1:0));
  const d = `M ${r} 0 A ${r} ${r} 0 0 ${sweepOuter} ${r} ${size} A ${rx} ${r} 0 0 ${sweepInner} ${r} 0 Z`;
  const name = label || phaseName(p);
  return (
    <span style={{ display:'inline-flex', alignItems:'center', gap:8 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={name}
        style={{ flex:'none', display:'block' }}>
        <circle cx={r} cy={r} r={r-0.5} fill="var(--inset)" stroke="var(--line-strong)" strokeWidth="1"/>
        {p > 0.02 && p < 0.98 && <path d={d} fill={lit}/>}
        {p >= 0.98 || p <= 0.02 ? null : null}
        <circle cx={r} cy={r} r={r-0.5} fill="none" stroke="color-mix(in srgb,var(--gilt) 40%,transparent)" strokeWidth="1"/>
      </svg>
      {showLabel && <span className="t-caption" style={{ color:'var(--soft)' }}>{name}</span>}
    </span>
  );
}
export function phaseName(p){
  if (p<0.03||p>0.97) return 'New moon';
  if (p<0.22) return 'Waxing crescent';
  if (p<0.28) return 'First quarter';
  if (p<0.47) return 'Waxing gibbous';
  if (p<0.53) return 'Full moon';
  if (p<0.72) return 'Waning gibbous';
  if (p<0.78) return 'Last quarter';
  return 'Waning crescent';
}
