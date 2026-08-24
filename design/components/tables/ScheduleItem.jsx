import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
const fmt=(d,tz,opts)=>new Intl.DateTimeFormat('en-GB',{...opts,timeZone:tz}).format(d);
export function ScheduleItem({title,startISO,durationMin,topic,status='upcoming',tz='local',href}){
  css('sh-scheditem',`.sh-sched{display:grid;grid-template-columns:64px 1fr auto;gap:18px;align-items:center;padding:16px 18px;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);font-family:var(--font-body);text-decoration:none;color:inherit;transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
a.sh-sched:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-sched[data-status=live]{border-color:color-mix(in srgb,var(--live) 40%,transparent);background:color-mix(in srgb,var(--live-wash) 40%,var(--surface-card))}
.sh-sched[data-status=past]{opacity:.6}
.sh-sched .sh-sc-date{display:grid;justify-items:center;gap:2px;border-right:var(--border-w) solid var(--line);padding-right:16px}
.sh-sched .sh-sc-dow{font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint)}
.sh-sched .sh-sc-day{font-family:var(--font-display);font-size:28px;font-weight:600;color:var(--ink);line-height:1;font-variant-numeric:tabular-nums}
.sh-sched .sh-sc-main{display:grid;gap:4px;min-width:0}
.sh-sched .sh-sc-title{font-family:var(--font-display);font-size:var(--text-h4);font-weight:600;color:var(--ink);margin:0}
.sh-sched .sh-sc-topic{font-size:var(--text-xs);color:var(--ink-faint)}
.sh-sched .sh-sc-time{display:grid;gap:3px;justify-items:end;text-align:right}
.sh-sched .sh-sc-t1{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:var(--text-sm);color:var(--ink)}
.sh-sched .sh-sc-t2{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:10.5px;color:var(--ink-faint)}
.sh-sched .sh-sc-live{font-size:var(--text-micro);font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--live)}
@media (max-width:560px){.sh-sched{grid-template-columns:56px 1fr}.sh-sched .sh-sc-time{grid-column:2;justify-items:start;text-align:left}}`);
  const d=new Date(startISO);
  const localTz=Intl.DateTimeFormat().resolvedOptions().timeZone;
  const primTz=tz==='athens'?'Europe/Athens':localTz;
  const secTz=tz==='athens'?localTz:'Europe/Athens';
  const t=z=>fmt(d,z,{hour:'2-digit',minute:'2-digit',hour12:false});
  const Tag=href?'a':'article';
  return <Tag className="sh-sched" data-status={status} href={href}>
    <span className="sh-sc-date"><span className="sh-sc-dow">{fmt(d,primTz,{weekday:'short'})}</span><span className="sh-sc-day">{fmt(d,primTz,{day:'2-digit'})}</span><span className="sh-sc-dow" style={{letterSpacing:'.06em'}}>{fmt(d,primTz,{month:'short'})}</span></span>
    <span className="sh-sc-main">
      {status==='live'&&<span className="sh-sc-live">● Live now</span>}
      <h3 className="sh-sc-title">{title}</h3>
      {topic&&<span className="sh-sc-topic">{topic}{durationMin?` · ~${Math.round(durationMin/60*10)/10}h`:''}</span>}
    </span>
    <span className="sh-sc-time">
      <span className="sh-sc-t1">{t(primTz)} {tz==='athens'?'Athens':'your time'}</span>
      <span className="sh-sc-t2">{t(secTz)} {tz==='athens'?'your time':'Athens'}</span>
    </span>
  </Tag>;
}
