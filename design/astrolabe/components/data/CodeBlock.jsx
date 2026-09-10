import React from 'react';
/* Monospace-ish block: isopsephy tables, offer codes, the wheel's SVG source.
   The app ships no mono face, so this is Commissioner locked to tabular figures
   with letter-spacing — close enough to read as data, and free. */
export function CodeBlock({ children, label, copyable=false, onCopy, wrap=false, align='left' }) {
  return (
    <div className="card-inset" style={{ overflow:'hidden' }}>
      {label && <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between',
        padding:'8px 12px', borderBottom:'1px solid var(--line)' }}>
        <span className="t-eyebrow">{label}</span>
        {copyable && <button type="button" onClick={onCopy} style={{ appearance:'none', background:'none',
          border:0, padding:4, color:'var(--accent)', font:'500 var(--size-caption)/1 var(--font-body)',
          cursor:'pointer' }}>Copy</button>}
      </div>}
      <pre style={{ margin:0, padding:'12px', overflowX:'hidden', textAlign:align,
        font:'400 var(--size-data-dense)/1.7 var(--font-body)', fontVariantNumeric:'tabular-nums lining-nums',
        letterSpacing:'.04em', color:'var(--ink)', whiteSpace:'pre-wrap',
        wordBreak:'break-word' }}>{children}</pre>
    </div>
  );
}
