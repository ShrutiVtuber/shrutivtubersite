import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
/* A settings switch on its own row. The whole row is the target (56px), the
   switch is the affordance. State is carried by position AND fill AND the
   knob's tick, so it survives a monochrome screen. */
export function Switch({ label, description, checked=false, disabled=false, onChange, id, ...rest }) {
  css('as-switch',`.as-switch{display:flex;align-items:center;gap:16px;width:100%;min-height:var(--tap-comfort);padding:10px 0;background:none;border:0;text-align:left;cursor:pointer;color:inherit}
.as-switch:active{background:var(--veil)}
.as-switch-txt{flex:1;min-width:0;display:grid;gap:3px}
.as-switch-lab{font:400 var(--size-body)/1.35 var(--font-body);color:var(--ink)}
.as-switch-desc{font:400 var(--size-caption)/1.4 var(--font-body);color:var(--faint)}
.as-switch-track{flex:none;width:48px;height:28px;border-radius:99px;background:var(--inset);border:1.5px solid var(--line-strong);position:relative;transition:background var(--dur-2) var(--ease-out),border-color var(--dur-2) var(--ease-out)}
.as-switch-knob{position:absolute;top:3px;left:3px;width:19px;height:19px;border-radius:99px;background:var(--faint);display:grid;place-items:center;font:700 11px/1 var(--font-body);color:var(--inset);transition:transform var(--dur-2) var(--ease-out),background var(--dur-2) var(--ease-out),width var(--dur-2) var(--ease-out)}
.as-switch[data-checked=true] .as-switch-track{background:var(--accent);border-color:var(--accent)}
.as-switch[data-checked=true] .as-switch-knob{transform:translateX(20px);background:var(--on-accent)}
.as-switch[disabled]{opacity:.38;cursor:not-allowed}`);
  const uid = id || React.useId();
  return <button className="as-switch" role="switch" aria-checked={checked} type="button"
    data-checked={checked||undefined} disabled={disabled} id={uid}
    onClick={()=>onChange&&onChange(!checked)} {...rest}>
    <span className="as-switch-txt">
      <span className="as-switch-lab">{label}</span>
      {description && <span className="as-switch-desc">{description}</span>}
    </span>
    <span className="as-switch-track" aria-hidden="true">
      <span className="as-switch-knob">{checked?'✓':''}</span>
    </span>
  </button>;
}
