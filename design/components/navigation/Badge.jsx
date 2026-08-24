import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Badge({tone='neutral',dot=false,children}){
  css('sh-badge',`.sh-badge{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:.06em;text-transform:uppercase;border-radius:var(--radius-full);padding:3px 9px;border:var(--border-w) solid;line-height:1.4}
.sh-badge i{width:6px;height:6px;border-radius:99px;background:currentColor}
.sh-badge[data-tone=neutral]{color:var(--ink-soft);border-color:var(--line);background:var(--surface-veil)}
.sh-badge[data-tone=accent]{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent);background:var(--accent-wash)}
.sh-badge[data-tone=rose]{color:var(--rose);border-color:color-mix(in srgb,var(--rose) 45%,transparent);background:var(--rose-wash)}
.sh-badge[data-tone=live]{color:var(--live);border-color:color-mix(in srgb,var(--live) 45%,transparent);background:var(--live-wash)}
.sh-badge[data-tone=faint]{color:var(--ink-faint);border-color:var(--line);background:transparent}`);
  return <span className="sh-badge" data-tone={tone}>{dot&&<i aria-hidden="true"></i>}{children}</span>;
}
