import React from 'react';
/* An authored empty state. Quiet and honest — never a shrug, never a fake.
   ⚠ The drawing is optional and its absence is designed: with no art the mark
   ring holds the space at the same height, so the screen never reflows when
   her artwork lands. */
export function EmptyState({ mark='\u263E', art, artAlt='', title, body, action, secondary, compact=false }) {
  return (
    <div style={{ display:'grid', justifyItems:'center', gap:14, textAlign:'center',
      padding: compact ? '28px 20px' : '48px 24px', maxWidth:'38ch', margin:'0 auto' }}>
      {art
        ? <img src={art} alt={artAlt} style={{ width:compact?96:148, height:'auto', opacity:.95 }}/>
        : <span aria-hidden="true" className="scatter-faint scatter" style={{ width:compact?56:72,
            height:compact?56:72, borderRadius:'var(--radius-full)', display:'grid', placeItems:'center',
            border:'1px solid color-mix(in srgb,var(--gilt) 34%,transparent)', background:'var(--inset)' }}>
            <span className="t-glyph" style={{ fontSize:compact?22:28, color:'var(--gilt)' }}>{mark}{'\uFE0E'}</span>
          </span>}
      <div style={{ display:'grid', gap:7 }}>
        {title && <h3 style={{ margin:0, font:'500 var(--size-title)/1.25 var(--font-display)',
          color:'var(--ink)', textWrap:'balance' }}>{title}</h3>}
        {body && <p style={{ margin:0, font:'400 var(--size-label)/1.55 var(--font-body)',
          color:'var(--faint)', textWrap:'pretty' }}>{body}</p>}
      </div>
      {(action||secondary) && <div style={{ display:'grid', gap:8, justifyItems:'center', marginTop:2 }}>
        {action}{secondary}</div>}
    </div>
  );
}
