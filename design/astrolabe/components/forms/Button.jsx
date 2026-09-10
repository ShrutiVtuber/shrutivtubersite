import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
/* The app's button. Filled is the one action a screen is for; outlined is the
   alternative; text is everything else. Destructive is outlined-only — nothing
   irreversible gets a filled button. Press deepens and sinks 1px; it never scales. */
export function Button({ variant='filled', size='md', destructive=false, disabled=false,
  loading=false, full=false, external=false, iconLeft, iconRight, href, type='button', onClick, children, ...rest }) {
  css('as-btn',`.as-btn{--_bg:var(--accent);--_fg:var(--on-accent);--_bd:transparent;appearance:none;display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:var(--font-body);font-weight:600;border-radius:var(--radius-sm);border:var(--border-w) solid var(--_bd);background:var(--_bg);color:var(--_fg);cursor:pointer;text-decoration:none;line-height:1;white-space:nowrap;position:relative;transition:background var(--dur-1) var(--ease-out),color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),transform var(--dur-1) var(--ease-out)}
.as-btn[data-size=sm]{font-size:var(--size-caption);padding:0 14px;min-height:36px}
.as-btn[data-size=md]{font-size:var(--size-label);padding:0 20px;min-height:48px}
.as-btn[data-size=lg]{font-size:var(--size-body);padding:0 24px;min-height:56px}
.as-btn[data-full=true]{display:flex;width:100%}
.as-btn:active{transform:translateY(1px)}
.as-btn:hover{--_bg:var(--accent-hover)}
.as-btn[data-variant=outlined]{--_bg:transparent;--_fg:var(--accent);--_bd:color-mix(in srgb,var(--accent) 55%,transparent)}
.as-btn[data-variant=outlined]:hover,.as-btn[data-variant=outlined]:active{--_bg:var(--accent-wash);--_bd:var(--accent)}
.as-btn[data-variant=text]{--_bg:transparent;--_fg:var(--accent);--_bd:transparent;padding:0 12px}
.as-btn[data-variant=text]:hover,.as-btn[data-variant=text]:active{--_bg:var(--veil)}
.as-btn[data-destructive=true][data-variant=outlined]{--_fg:var(--live);--_bd:color-mix(in srgb,var(--live) 55%,transparent)}
.as-btn[data-destructive=true][data-variant=outlined]:hover,.as-btn[data-destructive=true][data-variant=outlined]:active{--_bg:var(--live-wash);--_bd:var(--live)}
.as-btn[data-destructive=true][data-variant=text]{--_fg:var(--live)}
.as-btn[data-destructive=true][data-variant=filled]{--_bg:var(--live);--_fg:#2A0F16}
.as-btn[disabled],.as-btn[data-disabled=true]{opacity:.38;cursor:not-allowed;pointer-events:none}
.as-btn[data-loading=true]>*{visibility:hidden}
.as-btn[data-loading=true]::after{content:"";visibility:visible;position:absolute;inset:0;margin:auto;width:16px;height:16px;border-radius:99px;border:2px solid color-mix(in srgb,var(--_fg) 28%,transparent);border-top-color:var(--_fg);animation:as-spin .7s linear infinite}
@keyframes as-spin{to{transform:rotate(360deg)}}`);
  const Tag = href && !disabled ? 'a' : 'button';
  return <Tag className="as-btn" data-variant={variant} data-size={size} data-full={full||undefined}
    data-destructive={destructive||undefined} data-loading={loading||undefined} data-disabled={disabled||undefined}
    href={href} target={external?'_blank':undefined} rel={external?'noreferrer':undefined}
    type={Tag==='button'?type:undefined} disabled={Tag==='button'?(disabled||loading):undefined}
    aria-busy={loading||undefined} onClick={onClick} {...rest}>
    {iconLeft}<span>{children}</span>{iconRight}
    {external && <span aria-hidden="true" style={{ opacity:.7, fontSize:'0.85em' }}>↗</span>}
  </Tag>;
}
