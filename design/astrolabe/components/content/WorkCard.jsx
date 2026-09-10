import React from 'react';
import { Icon } from '../marks/Icon.jsx';
import { VoteControl } from './VoteControl.jsx';
/* A community reading in the practice room. Somebody else's work, or your own.
   Own work carries its status: draft, posted, or corrected.
   ⚠ Long content is designed: the title clamps at two lines and the body at
   three; a forty-character name truncates from the middle of the row, not the
   card. Nothing here ever pushes the vote control off screen. */
const STATUS = { draft:{ t:'Draft', c:'var(--faint)' }, posted:{ t:'Posted', c:'var(--accent)' },
  corrected:{ t:'Corrected', c:'var(--gilt)' } };
export function WorkCard({ title, author, avatar, date, excerpt, votes=0, myVote=0, comments=0,
  status, mine=false, onOpen, onVote, sign }) {
  const st = status && STATUS[status];
  return (
    <article className="card card-tappable" style={{ display:'grid', gridTemplateColumns:'auto 1fr',
      gap:12, padding:14, alignItems:'start' }}>
      <VoteControl value={votes} mine={myVote} onVote={onVote}/>
      <button type="button" onClick={onOpen} style={{ appearance:'none', background:'none', border:0,
        padding:0, textAlign:'left', minWidth:0, display:'grid', gap:6, cursor:'pointer', color:'inherit' }}>
        <span style={{ display:'flex', alignItems:'center', gap:7, minWidth:0 }}>
          {avatar
            ? <img src={avatar} alt="" style={{ width:18, height:18, borderRadius:99, flex:'none' }}/>
            : <span aria-hidden="true" style={{ width:18, height:18, borderRadius:99, flex:'none',
                background:'var(--veil)', border:'1px solid var(--line)' }}/>}
          <span className="t-caption" style={{ minWidth:0, overflow:'hidden', textOverflow:'ellipsis',
            whiteSpace:'nowrap', color:'var(--soft)' }}>{mine ? 'You' : author}</span>
          <span className="t-caption" aria-hidden="true">·</span>
          <span className="t-caption t-tabular" style={{ flex:'none' }}>{date}</span>
          {st && <span style={{ flex:'none', font:'600 10px/1 var(--font-body)', letterSpacing:'.1em',
            textTransform:'uppercase', color:st.c }}>{st.t}</span>}
        </span>
        <span style={{ font:'500 18px/1.3 var(--font-display)', color:'var(--ink)', display:'-webkit-box',
          WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden', textWrap:'pretty' }}>{title}</span>
        {excerpt && <span style={{ font:'400 var(--size-caption)/1.55 var(--font-body)', color:'var(--faint)',
          display:'-webkit-box', WebkitLineClamp:3, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{excerpt}</span>}
        <span style={{ display:'flex', alignItems:'center', gap:14, marginTop:2 }}>
          {sign && <span className="t-caption">{sign}</span>}
          <span style={{ display:'inline-flex', alignItems:'center', gap:5 }}>
            <Icon name="mode_comment" size={15} tone="faint"/>
            <span className="t-caption t-tabular">{comments}</span>
          </span>
        </span>
      </button>
    </article>
  );
}
