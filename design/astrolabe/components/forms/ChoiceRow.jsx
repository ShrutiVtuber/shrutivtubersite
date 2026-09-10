import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
/* One row of a choice: a radio (pick one — the sunrise convention) or a checkbox
   (a consent). Both carry an optional `rule` line, because the app's disagreement
   controls are never bare labels: each option states the rule it applies.
   Consents are never pre-ticked and never bundled — one row, one decision. */
export function ChoiceRow({ type='radio', label, rule, checked=false, disabled=false, name,
  value, onChange, id, ...rest }) {
  css('as-choice',`.as-choice{display:flex;gap:14px;width:100%;min-height:var(--tap-comfort);padding:12px 0;background:none;border:0;text-align:left;cursor:pointer;color:inherit;align-items:flex-start}
.as-choice:active{background:var(--veil)}
.as-choice-mark{flex:none;width:22px;height:22px;margin-top:1px;border:1.5px solid var(--line-strong);background:var(--inset);display:grid;place-items:center;transition:border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.as-choice[data-type=radio] .as-choice-mark{border-radius:99px}
.as-choice[data-type=checkbox] .as-choice-mark{border-radius:5px}
.as-choice-mark i{opacity:0;transition:opacity var(--dur-1) var(--ease-out);font-style:normal}
.as-choice[data-type=radio] .as-choice-mark i{width:10px;height:10px;border-radius:99px;background:var(--on-accent)}
.as-choice[data-type=checkbox] .as-choice-mark i{font:700 13px/1 var(--font-body);color:var(--on-accent)}
.as-choice[data-checked=true] .as-choice-mark{background:var(--accent);border-color:var(--accent)}
.as-choice[data-checked=true] .as-choice-mark i{opacity:1}
.as-choice-txt{flex:1;min-width:0;display:grid;gap:4px}
.as-choice-lab{font:400 var(--size-body)/1.35 var(--font-body);color:var(--ink)}
.as-choice[data-checked=true] .as-choice-lab{font-weight:500}
.as-choice-rule{font:400 var(--size-caption)/1.5 var(--font-body);color:var(--faint)}
.as-choice[disabled]{opacity:.38;cursor:not-allowed}`);
  const uid = id || React.useId();
  return <button className="as-choice" data-type={type} data-checked={checked||undefined}
    role={type==='radio'?'radio':'checkbox'} aria-checked={checked} type="button" id={uid}
    disabled={disabled} onClick={()=>onChange&&onChange(type==='radio'?value:!checked)} {...rest}>
    <span className="as-choice-mark" aria-hidden="true"><i>{type==='checkbox'?'✓':''}</i></span>
    <span className="as-choice-txt">
      <span className="as-choice-lab">{label}</span>
      {rule && <span className="as-choice-rule">{rule}</span>}
    </span>
  </button>;
}
