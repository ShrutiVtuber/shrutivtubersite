import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
function pages(cur,total){
  if(total<=7)return Array.from({length:total},(_,i)=>i+1);
  const set=new Set([1,total,cur-1,cur,cur+1]);
  const arr=[...set].filter(p=>p>=1&&p<=total).sort((a,b)=>a-b);
  const out=[];let prev=0;
  for(const p of arr){if(p-prev>1)out.push('…');out.push(p);prev=p}
  return out;
}
export function Pagination({page,pageCount,onChange,hrefFor,label='Pagination'}){
  css('sh-pagination',`.sh-pag{display:flex;align-items:center;gap:4px;font-family:var(--font-body)}
.sh-pag [data-p]{appearance:none;border:var(--border-w) solid transparent;background:transparent;min-width:36px;height:36px;padding:0 8px;border-radius:var(--radius-sm);font-size:var(--text-sm);font-variant-numeric:tabular-nums;color:var(--ink-soft);cursor:pointer;display:inline-grid;place-items:center;text-decoration:none;line-height:1;transition:color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-pag [data-p]:hover{color:var(--ink);border-color:var(--line-strong)}
.sh-pag [data-p]:active{transform:translateY(1px)}
.sh-pag [data-p][aria-current=page]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 50%,transparent);color:var(--accent);font-weight:600}
.sh-pag [data-p][aria-disabled=true]{opacity:.4;pointer-events:none}
.sh-pag .sh-pag-gap{color:var(--ink-faint);min-width:24px;text-align:center}`);
  const go=p=>e=>{if(!hrefFor){e.preventDefault();onChange&&onChange(p)}};
  const Item=({p,children,disabled,current,aria})=>{
    const Tg=hrefFor?'a':'button';
    return <Tg data-p href={hrefFor?hrefFor(p):undefined} type={hrefFor?undefined:'button'}
      onClick={go(p)} aria-current={current?'page':undefined} aria-disabled={disabled||undefined} aria-label={aria}>{children}</Tg>;
  };
  return <nav className="sh-pag" aria-label={label}>
    <Item p={page-1} disabled={page<=1} aria="Previous page">←</Item>
    {pages(page,pageCount).map((p,i)=>p==='…'
      ?<span key={'g'+i} className="sh-pag-gap" aria-hidden="true">…</span>
      :<Item key={p} p={p} current={p===page}>{p}</Item>)}
    <Item p={page+1} disabled={page>=pageCount} aria="Next page">→</Item>
  </nav>;
}
