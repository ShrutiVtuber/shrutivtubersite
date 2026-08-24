import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function CreditList({credits=[],dense=false}){
  css('sh-creditlist',`.sh-credits{display:grid;padding:0;margin:0;list-style:none}
.sh-credits li{display:grid;grid-template-columns:140px 1fr;gap:16px;align-items:baseline;padding:14px 0;border-bottom:var(--border-w) solid var(--line)}
.sh-credits[data-dense=true] li{padding:8px 0}
.sh-credits .sh-cr-role{font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint)}
.sh-credits .sh-cr-name{font-family:var(--font-display);font-size:var(--text-h4);color:var(--ink)}
.sh-credits .sh-cr-name a{color:inherit;text-decoration-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.sh-credits .sh-cr-name a:hover{color:var(--accent-hover)}
.sh-credits .sh-cr-note{font-family:var(--font-body);font-size:var(--text-xs);color:var(--ink-faint);margin-left:10px}
@media (max-width:480px){.sh-credits li{grid-template-columns:1fr;gap:2px}}`);
  return <ul className="sh-credits" data-dense={dense}>
    {credits.map((c,i)=><li key={i}>
      <span className="sh-cr-role">{c.role}</span>
      <span className="sh-cr-name">{c.href?<a href={c.href}>{c.name}</a>:c.name}{c.note&&<span className="sh-cr-note">{c.note}</span>}</span>
    </li>)}
  </ul>;
}
