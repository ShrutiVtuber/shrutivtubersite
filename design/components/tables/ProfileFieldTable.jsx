import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function ProfileFieldTable({fields=[],columns=2}){
  css('sh-profiletable',`.sh-pft{display:grid;gap:0 40px;font-family:var(--font-body)}
.sh-pft[data-cols="2"]{grid-template-columns:1fr 1fr}
.sh-pft .sh-pft-row{display:flex;align-items:baseline;gap:10px;padding:10px 0;border-bottom:var(--border-w) solid var(--line)}
.sh-pft .sh-pft-label{font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint);flex:none}
.sh-pft .sh-pft-dots{flex:1;border-bottom:1px dotted var(--line-strong);transform:translateY(-4px);min-width:24px}
.sh-pft .sh-pft-value{font-family:var(--font-display);font-size:var(--text-h4);color:var(--ink);text-align:right}
@media (max-width:560px){.sh-pft[data-cols="2"]{grid-template-columns:1fr}}`);
  return <dl className="sh-pft" data-cols={columns}>
    {fields.map((f,i)=><div className="sh-pft-row" key={i}>
      <dt className="sh-pft-label">{f.label}</dt><span className="sh-pft-dots" aria-hidden="true"></span><dd className="sh-pft-value" style={{margin:0}}>{f.value}</dd>
    </div>)}
  </dl>;
}
