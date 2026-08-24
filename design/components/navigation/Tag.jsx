import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Tag({label,href,active=false,count,onClick}){
  css('sh-tag',`.sh-tagc{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:var(--text-xs);font-weight:500;color:var(--ink-soft);background:var(--surface-veil);border:var(--border-w) solid transparent;border-radius:var(--radius-full);padding:5px 12px;text-decoration:none;cursor:pointer;line-height:1;transition:color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-tagc:hover{color:var(--accent-hover);border-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.sh-tagc:active{transform:translateY(1px)}
.sh-tagc[data-active=true]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 50%,transparent);color:var(--accent)}
.sh-tagc .sh-tag-n{font-family:var(--font-mono);font-size:10px;color:var(--ink-faint);font-variant-numeric:tabular-nums}`);
  const Tg=href?'a':'button';
  return <Tg className="sh-tagc" data-active={active} href={href} type={href?undefined:'button'} onClick={onClick} aria-pressed={href?undefined:active||undefined}>
    {label}{count!=null&&<span className="sh-tag-n">{count}</span>}
  </Tg>;
}
