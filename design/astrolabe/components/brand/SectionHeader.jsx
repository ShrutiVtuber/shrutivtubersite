import React from 'react';
/* An eyebrow that opens a section, with an optional action on the right and an
   optional rule beneath. Sentence case in the title, uppercase comes from CSS. */
export function SectionHeader({ eyebrow, title, action, onAction, rule=false, mark }) {
  return (
    <div style={{ display:'grid', gap:8, marginBottom:12 }}>
      <div style={{ display:'flex', alignItems:'baseline', gap:12, minHeight:24 }}>
        <div style={{ flex:1, minWidth:0, display:'grid', gap:4 }}>
          {eyebrow && <span className="t-eyebrow">{eyebrow}</span>}
          {title && <h2 style={{ margin:0, font:'600 var(--size-title)/var(--leading-title) var(--font-display)',
            color:'var(--ink)' }}>{title}</h2>}
        </div>
        {action && <button type="button" onClick={onAction} style={{ flex:'none', appearance:'none',
          background:'none', border:0, padding:'6px 2px', minHeight:32, color:'var(--accent)',
          font:'500 var(--size-caption)/1 var(--font-body)', cursor:'pointer' }}>{action}</button>}
      </div>
      {rule && <div className="rule">{mark || '\u263E\uFE0E'}</div>}
    </div>
  );
}
