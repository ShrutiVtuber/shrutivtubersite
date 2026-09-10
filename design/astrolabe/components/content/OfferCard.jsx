import React from 'react';
import { Icon } from '../marks/Icon.jsx';
/* An offer: a class, a reading slot, the shop, support.
   ⚠ Nothing takes money inside the app. Every offer leaves for her own checkout
   in a browser, and the card says so on its face — the arrow and the words
   "opens in your browser" are not optional decoration, they are the promise
   that the address bar will say whose it is.
   Members-only offers show the lock and stay tappable: tapping explains. */
export function OfferCard({ title, body, price, cadence, membersOnly=false, locked=false,
  href, onOpen, mark='\u2609', soldOut=false }) {
  return (
    <a href={locked?undefined:href} target={locked?undefined:'_blank'} rel="noreferrer"
      onClick={onOpen} className="card hem card-tappable" style={{
        display:'grid', gap:10, padding:14, textDecoration:'none', color:'inherit',
        background:'linear-gradient(168deg,var(--gilt-wash) 0%,var(--card) 58%)',
        border:'1px solid color-mix(in srgb,var(--gilt) 38%,transparent)',
        borderRadius:'var(--radius-md)', boxShadow:'var(--shadow-1)', position:'relative',
        opacity:soldOut?.6:1 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
        <span className="t-glyph" aria-hidden="true" style={{ fontSize:14, color:'var(--gilt)' }}>{mark}{'\uFE0E'}</span>
        <span className="t-eyebrow" style={{ color:'var(--gilt)' }}>{membersOnly?'Members':'Offer'}</span>
        {locked && <Icon name="lock" size={14} tone="gilt"/>}
        {soldOut && <span className="t-eyebrow" style={{ color:'var(--faint)' }}>· full</span>}
      </div>
      <div style={{ display:'grid', gap:5 }}>
        <span style={{ font:'500 19px/1.3 var(--font-display)', color:'var(--ink)', textWrap:'pretty' }}>{title}</span>
        {body && <span style={{ font:'400 var(--size-caption)/1.55 var(--font-body)', color:'var(--soft)',
          textWrap:'pretty' }}>{body}</span>}
      </div>
      <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', gap:10,
        borderTop:'1px solid color-mix(in srgb,var(--gilt) 22%,transparent)', paddingTop:10 }}>
        <span className="t-tabular" style={{ font:'600 var(--size-data)/1 var(--font-body)', color:'var(--gilt)' }}>
          {price}{cadence && <span style={{ color:'var(--faint)', fontWeight:400, fontSize:'var(--size-caption)' }}> {cadence}</span>}
        </span>
        <span style={{ display:'inline-flex', alignItems:'center', gap:5,
          font:'400 var(--size-caption)/1 var(--font-body)', color:'var(--faint)' }}>
          {locked ? 'Members only' : 'opens in your browser'}
          {!locked && <Icon name="open_in_new" size={14} tone="faint"/>}
        </span>
      </div>
    </a>
  );
}
