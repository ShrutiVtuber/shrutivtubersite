import React from 'react';
import { Icon } from '../marks/Icon.jsx';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
/* A tap target with an icon in it. Always 48px minimum even when the glyph is 20px —
   the ring, not the glyph, is the target. `label` is required: it is the only name
   a screen reader gets. */
export function IconButton({ icon, label, size=24, variant='ghost', tone='soft', selected=false,
  disabled=false, badge, onClick, href, ...rest }) {
  css('as-iconbtn',`.as-iconbtn{appearance:none;display:inline-grid;place-items:center;min-width:var(--tap-min);min-height:var(--tap-min);border-radius:var(--radius-full);border:var(--border-w) solid transparent;background:transparent;cursor:pointer;position:relative;padding:0;transition:background var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out)}
.as-iconbtn:hover,.as-iconbtn:active{background:var(--veil)}
.as-iconbtn[data-variant=outlined]{border-color:var(--line)}
.as-iconbtn[data-variant=outlined]:hover{border-color:var(--line-strong)}
.as-iconbtn[data-variant=filled]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.as-iconbtn[data-selected=true]{background:var(--accent-wash)}
.as-iconbtn[disabled]{opacity:.38;cursor:not-allowed;pointer-events:none}
.as-iconbtn .as-ib-badge{position:absolute;top:6px;right:6px;min-width:16px;height:16px;padding:0 4px;border-radius:99px;background:var(--live);color:#2A0F16;font:600 10px/16px var(--font-body);text-align:center;border:1.5px solid var(--card)}`);
  const Tag = href ? 'a' : 'button';
  return <Tag className="as-iconbtn" data-variant={variant} data-selected={selected||undefined}
    href={href} type={Tag==='button'?'button':undefined} disabled={Tag==='button'?disabled:undefined}
    aria-label={label} aria-pressed={selected||undefined} onClick={onClick} {...rest}>
    <Icon name={icon} size={size} tone={selected?'accent':tone}/>
    {badge!=null && <span className="as-ib-badge">{badge}</span>}
  </Tag>;
}
