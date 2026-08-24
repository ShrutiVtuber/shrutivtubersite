import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
const GLYPH={info:'☾',success:'✓',error:'✕'};
export function Toast({tone='info',title,body,action,onDismiss}){
  css('sh-toast',`.sh-toast{display:flex;gap:12px;align-items:flex-start;width:min(380px,90vw);background:var(--surface-card);border:var(--border-w) solid var(--line);border-left:3px solid var(--accent);border-radius:var(--radius-md);box-shadow:var(--shadow-3);padding:14px 16px;font-family:var(--font-body);animation:sh-toast-in var(--dur-2) var(--ease-out)}
.sh-toast[data-tone=success]{border-left-color:var(--accent)}
.sh-toast[data-tone=error]{border-left-color:var(--live)}
.sh-toast .sh-to-glyph{font-family:var(--font-display);font-size:15px;color:var(--accent);flex:none;line-height:1.4}
.sh-toast[data-tone=error] .sh-to-glyph{color:var(--live)}
.sh-toast .sh-to-main{display:grid;gap:3px;flex:1;min-width:0}
.sh-toast .sh-to-title{font-size:var(--text-sm);font-weight:600;color:var(--ink);margin:0}
.sh-toast .sh-to-body{font-size:var(--text-xs);color:var(--ink-soft);margin:0}
.sh-toast .sh-to-action{margin-top:6px}
.sh-toast .sh-to-x{appearance:none;border:0;background:transparent;color:var(--ink-faint);cursor:pointer;font-size:13px;line-height:1;padding:4px;border-radius:var(--radius-sm);flex:none;transition:color var(--dur-1) var(--ease-out)}
.sh-toast .sh-to-x:hover{color:var(--ink)}
@keyframes sh-toast-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}`);
  return <div className="sh-toast" data-tone={tone} role={tone==='error'?'alert':'status'}>
    <span className="sh-to-glyph" aria-hidden="true">{GLYPH[tone]||GLYPH.info}</span>
    <div className="sh-to-main">
      <p className="sh-to-title">{title}</p>
      {body&&<p className="sh-to-body">{body}</p>}
      {action&&<div className="sh-to-action">{action}</div>}
    </div>
    {onDismiss&&<button className="sh-to-x" type="button" aria-label="Dismiss" onClick={onDismiss}>✕</button>}
  </div>;
}
