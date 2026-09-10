import React from 'react';
import { Icon } from '../marks/Icon.jsx';
/* A row in a list: settings, places, licences, a pushed destination.
   56px minimum. `value` sits right, `trailing` replaces the chevron when the
   row does something other than push. `danger` is for the one row that deletes. */
export function ListRow({ label, description, value, leading, trailing, chevron=true,
  danger=false, disabled=false, onClick, href, external=false, ...rest }) {
  const Tag = href ? 'a' : onClick ? 'button' : 'div';
  const tappable = !!(href || onClick);
  return (
    <Tag href={href} target={external?'_blank':undefined} rel={external?'noreferrer':undefined}
      type={Tag==='button'?'button':undefined} disabled={Tag==='button'?disabled:undefined}
      onClick={onClick} className={tappable?'card-tappable':undefined} style={{
        display:'flex', alignItems:'center', gap:14, width:'100%', textAlign:'left',
        minHeight:'var(--tap-comfort)', padding:'12px 16px', background:'none', border:0,
        borderRadius:0, cursor:tappable?'pointer':'default', textDecoration:'none',
        opacity:disabled?.38:1, color:'inherit'
      }} {...rest}>
      {leading && <span style={{ flex:'none', display:'grid', placeItems:'center', width:24 }}>{leading}</span>}
      <span style={{ flex:1, minWidth:0, display:'grid', gap:3 }}>
        <span style={{ font:'400 var(--size-body)/1.35 var(--font-body)',
          color: danger ? 'var(--live)' : 'var(--ink)', overflow:'hidden', textOverflow:'ellipsis' }}>{label}</span>
        {description && <span style={{ font:'400 var(--size-caption)/1.45 var(--font-body)',
          color:'var(--faint)', textWrap:'pretty' }}>{description}</span>}
      </span>
      {value && <span className="t-tabular" style={{ flex:'none', font:'400 var(--size-caption) var(--font-body)',
        color:'var(--soft)', maxWidth:'42%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap',
        textAlign:'right' }}>{value}</span>}
      {trailing ? <span style={{ flex:'none' }}>{trailing}</span>
        : (tappable && chevron) ? <Icon name={external?'open_in_new':'chevron_right'} size={20} tone="faint"/> : null}
    </Tag>
  );
}
/* A hairline-separated group of rows on a card. */
export function ListGroup({ children, inset=false }) {
  const rows = React.Children.toArray(children).filter(Boolean);
  return <div className={inset?'card-inset':'card'} style={{ overflow:'hidden' }}>
    {rows.map((c,i) => <div key={i} style={{ borderTop: i ? '1px solid var(--line)' : 'none' }}>{c}</div>)}
  </div>;
}
