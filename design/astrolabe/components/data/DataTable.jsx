import React from 'react';
/* A reference table. ⚠ Dense on purpose — a practitioner reading a month wants
   the month on one screen, so rows are 30px, figures are 13px tabular, and the
   only padding is what keeps the columns apart.
   Retrograde is ℞ AND a rose tint; today is a wash AND a rule AND the word.
   Columns: {key,label,mark,align,width,numeric}. */
export function DataTable({ columns, rows, caption, stickyHead=true, zebra=false, onRowClick, emptyLabel='—' }) {
  /* ⚠ The table FITS. A reference table that scrolls sideways is a table a
     practitioner cannot read at a glance, so the columns share the width and the
     figures get tighter instead. If it will not fit, cut a column — never scroll. */
  const head = { position:stickyHead?'sticky':'static', top:0, zIndex:2, background:'var(--inset)',
    padding:'7px 4px', borderBottom:'1px solid var(--line-strong)', textAlign:'left',
    font:'600 9px/1.15 var(--font-body)', letterSpacing:'.08em',
    textTransform:'uppercase', color:'var(--faint)', overflow:'hidden', verticalAlign:'bottom' };
  return (
    <div className="card-inset" style={{ overflow:'hidden', maxWidth:'100%' }}>
      <table style={{ width:'100%', borderCollapse:'collapse', tableLayout:'fixed' }}>
        {caption && <caption style={{ captionSide:'top', textAlign:'left', padding:'8px 10px 6px',
          font:'400 var(--size-caption)/1.5 var(--font-body)', color:'var(--faint)' }}>{caption}</caption>}
        <thead><tr>{columns.map(c => (
          <th key={c.key} scope="col" style={{ ...head, textAlign:c.align||(c.numeric?'right':'left'), width:c.width }}>
            {c.mark ? <span style={{ display:'grid', gap:2, justifyItems:c.numeric?'end':'start' }}>
              <span className="t-glyph" style={{ fontSize:13, color:'var(--gilt)', letterSpacing:0 }} aria-hidden="true">{c.mark}</span>
              <span>{c.label}</span></span> : c.label}
          </th>))}</tr></thead>
        <tbody>{rows.map((r,ri) => (
          <tr key={r.id||ri} onClick={onRowClick?()=>onRowClick(r):undefined} style={{
            background: r.today ? 'var(--accent-wash)' : zebra && ri%2 ? 'rgba(255,255,255,.015)' : 'transparent',
            cursor:onRowClick?'pointer':'default' }}>
            {columns.map((c,ci) => {
              const cell = r[c.key];
              const v = cell && typeof cell==='object' && !React.isValidElement(cell) ? cell : { value:cell };
              return <td key={c.key} style={{
                padding:'6px 4px', borderBottom:'1px solid var(--line)', overflow:'hidden',
                textAlign:c.align||(c.numeric?'right':'left'),
                font:`${v.strong||r.today&&ci===0?600:400} var(--size-data-dense)/1.35 var(--font-body)`,
                fontVariantNumeric: c.numeric!==false ? 'tabular-nums lining-nums' : 'normal',
                color: v.retro ? 'var(--rose)' : v.muted ? 'var(--faint)' : 'var(--ink)',
                whiteSpace:'nowrap', textOverflow:'clip' }}>
                {v.value==null || v.value==='' ? <span style={{ color:'var(--faint)' }}>{emptyLabel}</span> : v.value}
                {v.retro && <span className="t-glyph" style={{ marginLeft:3, fontSize:12 }} title="retrograde">{'\u211E\uFE0E'}</span>}
                {r.today && ci===0 && <span style={{ marginLeft:4, font:'600 8px/1 var(--font-body)',
                  letterSpacing:'.06em', textTransform:'uppercase', color:'var(--accent)' }}>now</span>}
              </td>;
            })}
          </tr>))}
        </tbody>
      </table>
    </div>
  );
}
