import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function EmptyState({glyph='○',title,body,action,compact=false}){
  css('sh-emptystate',`.sh-empty{display:grid;justify-items:center;text-align:center;gap:10px;padding:48px 24px;border:var(--border-w) dashed var(--line-strong);border-radius:var(--radius-md);font-family:var(--font-body);background:color-mix(in srgb,var(--surface-veil) 40%,transparent)}
.sh-empty[data-compact=true]{padding:28px 20px}
.sh-empty .sh-em-glyph{font-family:var(--font-display);font-size:30px;line-height:1;color:var(--ink-faint)}
.sh-empty .sh-em-title{font-family:var(--font-display);font-size:var(--text-h3);font-weight:600;color:var(--ink);margin:0}
.sh-empty .sh-em-body{font-size:var(--text-sm);color:var(--ink-soft);margin:0;max-width:44ch}
.sh-empty .sh-em-action{margin-top:8px}`);
  return <div className="sh-empty" data-compact={compact}>
    <span className="sh-em-glyph" aria-hidden="true">{glyph}</span>
    <h3 className="sh-em-title">{title}</h3>
    {body&&<p className="sh-em-body">{body}</p>}
    {action&&<div className="sh-em-action">{action}</div>}
  </div>;
}
