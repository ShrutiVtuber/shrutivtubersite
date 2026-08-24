import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Modal({open,onClose,title,children,footer,variant='panel',labelledBy}){
  css('sh-modal',`.sh-modal-ov{position:fixed;inset:0;z-index:80;display:grid;place-items:center;padding:24px;background:color-mix(in srgb,var(--surface-inset) 55%,transparent);backdrop-filter:var(--blur-veil);-webkit-backdrop-filter:var(--blur-veil);animation:sh-fade var(--dur-2) var(--ease-out)}
.sh-modal{background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-lg);box-shadow:var(--shadow-3);width:min(560px,100%);max-height:min(84vh,720px);display:flex;flex-direction:column;overflow:hidden;animation:sh-rise var(--dur-2) var(--ease-out);font-family:var(--font-body)}
.sh-modal[data-variant=lightbox]{width:auto;max-width:min(920px,100%);background:var(--surface-inset)}
.sh-modal .sh-mo-head{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 22px;border-bottom:var(--border-w) solid var(--line)}
.sh-modal[data-variant=lightbox] .sh-mo-head{border:0;position:absolute;inset:0 0 auto;z-index:2;background:linear-gradient(color-mix(in srgb,var(--surface-inset) 70%,transparent),transparent);padding:14px 18px}
.sh-modal .sh-mo-title{font-family:var(--font-display);font-size:var(--text-h3);font-weight:600;color:var(--ink);margin:0}
.sh-modal .sh-mo-x{appearance:none;border:var(--border-w) solid var(--line);background:var(--surface-card);color:var(--ink-soft);cursor:pointer;width:32px;height:32px;border-radius:var(--radius-full);display:grid;place-items:center;font-size:13px;flex:none;transition:color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out)}
.sh-modal .sh-mo-x:hover{color:var(--ink);border-color:var(--line-strong)}
.sh-modal .sh-mo-body{padding:20px 22px;overflow:auto}
.sh-modal[data-variant=lightbox] .sh-mo-body{padding:0;display:grid;place-items:center}
.sh-modal .sh-mo-foot{display:flex;justify-content:flex-end;gap:10px;padding:14px 22px;border-top:var(--border-w) solid var(--line);background:var(--surface-page)}
@keyframes sh-fade{from{opacity:0}}@keyframes sh-rise{from{opacity:0;transform:translateY(10px)}}`);
  React.useEffect(()=>{
    if(!open)return;
    const h=e=>{if(e.key==='Escape')onClose&&onClose()};
    document.addEventListener('keydown',h);return ()=>document.removeEventListener('keydown',h);
  },[open,onClose]);
  if(!open)return null;
  return <div className="sh-modal-ov" onMouseDown={e=>{if(e.target===e.currentTarget&&onClose)onClose()}}>
    <div className="sh-modal" data-variant={variant} role="dialog" aria-modal="true" aria-labelledby={labelledBy} aria-label={typeof title==='string'?title:undefined}>
      <div className="sh-mo-head">
        {title?<h2 className="sh-mo-title">{title}</h2>:<span></span>}
        <button className="sh-mo-x" type="button" aria-label="Close" onClick={onClose}>✕</button>
      </div>
      <div className="sh-mo-body">{children}</div>
      {footer&&<div className="sh-mo-foot">{footer}</div>}
    </div>
  </div>;
}
