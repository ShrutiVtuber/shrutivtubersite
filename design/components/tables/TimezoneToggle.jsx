import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function TimezoneToggle({value='local',onChange}){
  css('sh-tztoggle',`.sh-tz{display:inline-flex;border:var(--border-w) solid var(--line);border-radius:var(--radius-full);padding:2px;background:var(--surface-card);gap:2px;font-family:var(--font-body)}
.sh-tz button{appearance:none;border:0;background:transparent;font-size:var(--text-xs);font-weight:600;color:var(--ink-faint);padding:6px 12px;border-radius:var(--radius-full);cursor:pointer;line-height:1;display:inline-flex;gap:6px;align-items:center;transition:color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-tz button:hover{color:var(--ink)}
.sh-tz button[aria-pressed=true]{background:var(--surface-veil);color:var(--ink)}
.sh-tz .sh-tz-zone{font-family:var(--font-mono);font-weight:400;font-size:10px;color:var(--ink-faint)}`);
  const local=Intl.DateTimeFormat().resolvedOptions().timeZone.split('/').pop().replace('_',' ');
  return <div className="sh-tz" role="group" aria-label="Timezone">
    <button type="button" aria-pressed={value==='local'} onClick={()=>onChange&&onChange('local')}>Your time <span className="sh-tz-zone">{local}</span></button>
    <button type="button" aria-pressed={value==='athens'} onClick={()=>onChange&&onChange('athens')}>Athens <span className="sh-tz-zone">GMT+3</span></button>
  </div>;
}
