import React from 'react';
/* The app's surface. Four tones and no more:
   plain       a container
   tappable    it pushes somewhere — deepens and strengthens on press, never lifts
   highlighted an offer; gilt hairline + hem, because offers are the only place
               the brand ornament is allowed to sell something
   warning     something needs attention or cannot be reckoned; rose, with a mark */
export function Card({ tone='plain', onClick, href, hem=false, pad=16, children, style, ...rest }) {
  const Tag = href ? 'a' : onClick ? 'button' : 'div';
  const tappable = !!(href || onClick);
  const tones = {
    plain:{ background:'var(--card)', border:'1px solid var(--line)' },
    tappable:{ background:'var(--card)', border:'1px solid var(--line)' },
    highlighted:{ background:'linear-gradient(168deg,var(--gilt-wash) 0%,var(--card) 58%)',
      border:'1px solid color-mix(in srgb,var(--gilt) 38%,transparent)' },
    warning:{ background:'var(--rose-wash)', border:'1px solid color-mix(in srgb,var(--rose) 40%,transparent)' },
    inset:{ background:'var(--inset)', border:'1px solid var(--line)' }
  };
  return <Tag href={href} onClick={onClick} type={Tag==='button'?'button':undefined}
    className={(tappable?'card-tappable ':'') + (hem||tone==='highlighted'?'hem':'')}
    style={{ display:'block', width:'100%', textAlign:'left', position:'relative',
      borderRadius:'var(--radius-md)', padding:pad, color:'inherit', textDecoration:'none',
      boxShadow:'var(--shadow-1)', cursor:tappable?'pointer':'default', overflow:'hidden',
      ...tones[tone], ...style }} {...rest}>{children}</Tag>;
}
