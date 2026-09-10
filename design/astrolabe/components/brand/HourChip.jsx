import React from 'react';
import { Glyph } from '../marks/Glyph.jsx';
export const HOUR_RULERS = {
  sun:{ mark:'sun', name:'Sun' }, moon:{ mark:'moon', name:'Moon' },
  mars:{ mark:'mars', name:'Mars' }, mercury:{ mark:'mercury', name:'Mercury' },
  jupiter:{ mark:'jupiter', name:'Jupiter' }, venus:{ mark:'venus', name:'Venus' },
  saturn:{ mark:'saturn', name:'Saturn' }
};
/* The ruling planetary hour. Computed on device, so it is always there, even
   offline — which is exactly why it is allowed to be the app's one ambient
   signal. It tints itself and the hem above it, and nothing else.
   Always names the planet in words as well as the mark. */
export function HourChip({ ruler='sun', ends, ordinal, diurnal=true, onClick }) {
  const r = HOUR_RULERS[ruler] || HOUR_RULERS.sun;
  const Tag = onClick ? 'button' : 'div';
  return (
    <Tag onClick={onClick} type={onClick?'button':undefined} data-hour={ruler} style={{
      display:'inline-flex', alignItems:'center', gap:8, minHeight:36, padding:'0 12px',
      borderRadius:'var(--radius-full)', background:'var(--hour-wash)',
      border:'1px solid color-mix(in srgb,var(--hour) 40%,transparent)',
      color:'var(--soft)', font:'500 var(--size-caption)/1 var(--font-body)',
      cursor:onClick?'pointer':'default', whiteSpace:'nowrap',
      transition:'background var(--dur-hour) var(--ease-in-out),border-color var(--dur-hour) var(--ease-in-out)'
    }}>
      <Glyph name={r.mark} tone="hour" size="sm"/>
      <span style={{ color:'var(--hour)', fontWeight:600 }}>Hour of {r.name}</span>
      {ordinal!=null && <span className="t-tabular" style={{ color:'var(--faint)' }}>
        {ordinal}{diurnal?' of day':' of night'}</span>}
      {ends && <span className="t-tabular" style={{ color:'var(--faint)' }}>· until {ends}</span>}
    </Tag>
  );
}
