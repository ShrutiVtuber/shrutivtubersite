import React from 'react';
import { Icon } from '../marks/Icon.jsx';
/* Up, down, or neither, with the running total between.
   A vote lands by scaling the arrow to 1.18 and back over 240ms and the count
   stepping — no toast, no confirmation. Under reduced-motion the arrow just
   fills. State is fill AND colour AND aria-pressed, never colour alone. */
export function VoteControl({ value=0, mine=0, onVote, disabled=false, compact=false }) {
  const btn = (dir) => {
    const on = mine === dir;
    return <button type="button" disabled={disabled} aria-pressed={on}
      aria-label={dir>0?'Vote up':'Vote down'} onClick={()=>onVote&&onVote(on?0:dir)}
      style={{ appearance:'none', background:'none', border:0, padding:2, cursor:disabled?'not-allowed':'pointer',
        lineHeight:0, opacity:disabled?.38:1, transition:'transform var(--dur-2) var(--ease-out)',
        transform:on?'scale(1.06)':'none' }}>
      <Icon name={dir>0?'keyboard_arrow_up':'keyboard_arrow_down'} size={compact?20:24}
        weight={on?700:400} tone={on ? (dir>0?'accent':'rose') : 'faint'}/>
    </button>;
  };
  return (
    <div style={{ display:'grid', justifyItems:'center', gap:1, minWidth:34, flex:'none' }}>
      {btn(1)}
      <span className="t-tabular" style={{ font:`${mine?600:500} var(--size-caption)/1 var(--font-body)`,
        color: mine>0?'var(--accent)':mine<0?'var(--rose)':'var(--soft)' }}>{value}</span>
      {btn(-1)}
    </div>
  );
}
