import React from 'react';
import { Glyph } from '../marks/Glyph.jsx';
/* One of her things: a reading or an article. Same card, two kinds.
   ⚠ Missing content is designed: no title falls back to the sign and date
   ("Scorpio · 9 Sep"), no opening line leaves the card at its shorter height
   rather than showing an empty paragraph. Nothing ever renders "Untitled". */
export function ContentCard({ kind='reading', title, sign, signMark, date, excerpt, readingTime,
  unread=false, onOpen, cover, coverAlt='' }) {
  const heading = title || (sign ? `${sign} · ${date}` : date);
  return (
    <button type="button" onClick={onOpen} className="card card-tappable" style={{
      display:'grid', gridTemplateColumns: cover ? '1fr 72px' : '1fr', gap:14, width:'100%',
      textAlign:'left', padding:14, cursor:'pointer', color:'inherit', alignItems:'start' }}>
      <span style={{ minWidth:0, display:'grid', gap:6 }}>
        <span style={{ display:'flex', alignItems:'center', gap:7 }}>
          {signMark && <Glyph char={signMark} tone="gilt" size="sm"/>}
          <span className="t-eyebrow">{kind==='reading' ? (sign ? sign + ' · reading' : 'Reading') : 'Article'}</span>
          {unread && <span aria-label="unread" style={{ width:6, height:6, borderRadius:99,
            background:'var(--accent)' }}/>}
        </span>
        <span style={{ font:'500 var(--size-heading)/1.35 var(--font-display)', color:'var(--ink)',
          fontSize:19, display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical',
          overflow:'hidden', textWrap:'pretty' }}>{heading}</span>
        {excerpt && <span style={{ font:'400 var(--size-caption)/1.55 var(--font-body)', color:'var(--faint)',
          display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{excerpt}</span>}
        <span className="t-caption" style={{ display:'flex', gap:8, marginTop:2 }}>
          <span className="t-tabular">{date}</span>
          {readingTime && <><span aria-hidden="true">·</span><span>{readingTime}</span></>}
        </span>
      </span>
      {cover && <img src={cover} alt={coverAlt} style={{ width:72, height:72, objectFit:'cover',
        borderRadius:'var(--radius-sm)', border:'1px solid var(--line)' }}/>}
    </button>
  );
}
