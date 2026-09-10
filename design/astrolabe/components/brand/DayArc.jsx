import React from 'react';
import { MoonDisc } from '../marks/MoonDisc.jsx';
import { Glyph } from '../marks/Glyph.jsx';
/* The day, drawn. Sunrise to sunset as an arc, the Sun where it actually is,
   the night shaded either side, the Moon's phase at the end of it.

   This is Sky's header and it exists for one reason: the app knows what the sky
   is doing, on device, offline, and that is a signal almost no app has. It also
   stops every screen looking like the same stack of cards — Home has the plate,
   Sky has the arc, and neither borrows the other's surface.

   All four times are real inputs; nothing here is decorative. */
export function DayArc({ sunrise = '06:58', sunset = '19:51', now = '13:42', phase = 0.38,
  ruler = 'sun', height = 132, label }) {
  const t = (s) => { const [h,m] = s.split(':').map(Number); return h*60 + m; };
  const rise = t(sunrise), set = t(sunset), cur = t(now);
  const day = Math.max(1, set - rise);
  const frac = Math.min(1, Math.max(0, (cur - rise) / day));
  const isDay = cur >= rise && cur <= set;
  const W = 320, H = 92, pad = 26, span = W - pad*2, base = H - 20;
  const peak = 18;
  const x = pad + span * frac;
  const y = base - Math.sin(Math.PI * frac) * (base - peak);
  const path = `M ${pad} ${base} Q ${W/2} ${peak - (base-peak)*0.32} ${W-pad} ${base}`;
  return (
    <section className="scatter hem hem-hour" style={{ position:'relative', minHeight:height,
      background:'linear-gradient(180deg,#0B1322 0%,#16203A 52%,#241E2E 100%)',
      borderRadius:'var(--radius-lg)', border:'1px solid var(--line)', overflow:'hidden',
      padding:'12px 0 0' }}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img"
        aria-label={label || `Sunrise ${sunrise}, sunset ${sunset}, now ${now}`}
        style={{ display:'block' }} preserveAspectRatio="none">
        <defs>
          <linearGradient id="as-arc-h" x1="0" x2="1">
            <stop offset="0" stopColor="var(--gilt)" stopOpacity="0"/>
            <stop offset=".5" stopColor="var(--gilt)" stopOpacity=".55"/>
            <stop offset="1" stopColor="var(--gilt)" stopOpacity="0"/>
          </linearGradient>
        </defs>
        <path d={path} fill="none" stroke="var(--gilt-dim)" strokeWidth="1" strokeDasharray="3 4"/>
        <path d={`${path} L ${W-pad} ${base} L ${pad} ${base} Z`} fill="var(--gilt)" opacity=".07"/>
        <line x1="0" y1={base} x2={W} y2={base} stroke="url(#as-arc-h)" strokeWidth="1"/>
        <line x1={pad} y1={base-4} x2={pad} y2={base+4} stroke="var(--gilt-dim)" strokeWidth="1"/>
        <line x1={W-pad} y1={base-4} x2={W-pad} y2={base+4} stroke="var(--gilt-dim)" strokeWidth="1"/>
        {isDay && <>
          <line x1={x} y1={y} x2={x} y2={base} stroke="var(--gilt)" strokeWidth="0.8" opacity=".45"/>
          <circle cx={x} cy={y} r="9" fill="var(--gilt)" opacity=".16"/>
          <circle cx={x} cy={y} r="4.5" fill="var(--gilt-bright)"/>
        </>}
      </svg>
      <div style={{ position:'relative', display:'flex', alignItems:'flex-end',
        justifyContent:'space-between', gap:10, padding:'0 14px 12px', marginTop:-6 }}>
        <Time mark="\u2609" label="Rose" value={sunrise}/>
        <span style={{ display:'grid', justifyItems:'center', gap:4 }}>
          <Glyph name={ruler} tone="hour" size="sm"/>
          <span className="t-data" style={{ font:'600 15px/1 var(--font-body)', color:'var(--ink)',
            fontVariantNumeric:'tabular-nums' }}>{now}</span>
        </span>
        <span style={{ display:'grid', justifyItems:'center', gap:4 }}>
          <MoonDisc phase={phase} size={18}/>
          <span className="t-caption" style={{ fontSize:11 }}>{Math.round(phase*100)}%</span>
        </span>
        <Time mark="\u2609" label="Sets" value={sunset} align="right"/>
      </div>
    </section>
  );
}
function Time({ mark, label, value, align = 'left' }) {
  return <span style={{ display:'grid', justifyItems:align === 'right' ? 'end' : 'start', gap:3 }}>
    <span className="t-eyebrow" style={{ fontSize:10 }}>{label}</span>
    <span style={{ font:'500 13px/1 var(--font-body)', color:'var(--soft)',
      fontVariantNumeric:'tabular-nums' }}>{value}</span>
  </span>;
}
