import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function AssetDownloadCard({name,meta,preview,previewOn='checker',href,filename}){
  css('sh-assetcard',`.sh-asset{display:grid;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);overflow:hidden;font-family:var(--font-body);transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-asset:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-asset .sh-as-prev{height:120px;display:grid;place-items:center;border-bottom:var(--border-w) solid var(--line);padding:12px}
.sh-asset .sh-as-prev[data-on=checker]{background:repeating-conic-gradient(var(--surface-veil) 0 25%,var(--surface-card) 0 50%) 0 0/16px 16px}
.sh-asset .sh-as-prev[data-on=sky]{background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon))}
.sh-asset .sh-as-prev[data-on=ink]{background:var(--dusk-page)}
.sh-asset .sh-as-prev img{max-height:100%;max-width:100%}
.sh-asset .sh-as-prev [data-fallback]{font-family:var(--font-mono);font-size:11px;color:var(--ink-faint)}
.sh-asset .sh-as-body{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px}
.sh-asset .sh-as-name{font-size:var(--text-sm);font-weight:600;color:var(--ink);margin:0}
.sh-asset .sh-as-meta{font-family:var(--font-mono);font-size:10px;color:var(--ink-faint);letter-spacing:.02em}
.sh-asset .sh-as-dl{flex:none;display:inline-flex;align-items:center;gap:6px;font-size:var(--text-xs);font-weight:600;color:var(--accent);text-decoration:none;border:var(--border-w) solid color-mix(in srgb,var(--accent) 50%,transparent);border-radius:var(--radius-sm);padding:7px 12px;transition:background var(--dur-1) var(--ease-out)}
.sh-asset .sh-as-dl:hover{background:var(--accent-wash);color:var(--accent-hover)}
.sh-asset .sh-as-dl:active{transform:translateY(1px)}`);
  return <div className="sh-asset">
    <div className="sh-as-prev" data-on={previewOn}>{preview||<span data-fallback>no preview</span>}</div>
    <div className="sh-as-body">
      <div><h3 className="sh-as-name">{name}</h3>{meta&&<span className="sh-as-meta">{meta}</span>}</div>
      <a className="sh-as-dl" href={href} download={filename}><span aria-hidden="true">⤓</span> Download</a>
    </div>
  </div>;
}
