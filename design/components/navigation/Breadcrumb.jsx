import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Breadcrumb({items=[]}){
  css('sh-breadcrumb',`.sh-bc{font-family:var(--font-body);font-size:var(--text-xs)}
.sh-bc ol{display:flex;flex-wrap:wrap;align-items:center;gap:8px;list-style:none;margin:0;padding:0}
.sh-bc li{display:inline-flex;align-items:center;gap:8px}
.sh-bc li+li::before{content:"›";color:var(--ink-faint)}
.sh-bc a{color:var(--ink-faint);text-decoration:none;transition:color var(--dur-1) var(--ease-out)}
.sh-bc a:hover{color:var(--accent-hover);text-decoration:underline}
.sh-bc [aria-current=page]{color:var(--ink-soft);font-weight:500}`);
  return <nav className="sh-bc" aria-label="Breadcrumb"><ol>
    {items.map((it,i)=><li key={i}>{i===items.length-1
      ?<span aria-current="page">{it.label}</span>
      :<a href={it.href}>{it.label}</a>}</li>)}
  </ol></nav>;
}
