import React from 'react';
/* Two or three segments, never more — beyond three it is a tab bar or a list.
   The selected segment is a filled pill that slides; the labels stay put so the
   row does not reflow. */
export function SegmentedControl({ segments, active, onChange, label='View' }) {
  const i = Math.max(0, segments.findIndex(s => (s.id||s) === active));
  const n = segments.length;
  return (
    <div role="tablist" aria-label={label} style={{ position:'relative', display:'grid',
      gridTemplateColumns:`repeat(${n},1fr)`, background:'var(--inset)', border:'1px solid var(--line)',
      borderRadius:'var(--radius-sm)', padding:3, gap:0 }}>
      <span aria-hidden="true" style={{ position:'absolute', top:3, bottom:3, left:3,
        width:`calc((100% - 6px)/${n})`, transform:`translateX(${i*100}%)`, background:'var(--card)',
        border:'1px solid var(--line-strong)', borderRadius:'calc(var(--radius-sm) - 2px)',
        transition:'transform var(--dur-2) var(--ease-out)' }}/>
      {segments.map(s => {
        const id = s.id || s, lab = s.label || s, on = id === active;
        return <button key={id} role="tab" aria-selected={on} type="button" onClick={()=>onChange&&onChange(id)}
          style={{ position:'relative', appearance:'none', background:'none', border:0, cursor:'pointer',
            minHeight:40, padding:'0 6px', font:(on?600:400)+' var(--size-caption)/1 var(--font-body)',
            color: on ? 'var(--ink)' : 'var(--faint)', whiteSpace:'nowrap', overflow:'hidden',
            textOverflow:'ellipsis', transition:'color var(--dur-2) var(--ease-out)' }}>{lab}</button>;
      })}
    </div>
  );
}
