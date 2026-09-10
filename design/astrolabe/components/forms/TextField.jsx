import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
/* A text field. Inset well, hairline, label above — not a floating label: birth
   data and a 2,000-word reading both go in here and the label must stay put.
   An error is a message AND a colour AND a mark; never colour alone. */
export function TextField({ label, value, defaultValue, placeholder, helper, error, multiline=false,
  rows=4, disabled=false, required=false, type='text', suffix, prefix, mono=false, maxLength,
  counter=false, onChange, id, ...rest }) {
  css('as-field',`.as-field{display:grid;gap:6px}
.as-field-lab{font:600 var(--size-caption)/1.3 var(--font-body);color:var(--soft);display:flex;gap:5px;align-items:baseline}
.as-field-lab i{font-style:normal;color:var(--rose)}
.as-field-box{display:flex;align-items:center;gap:8px;background:var(--inset);border:var(--border-w) solid var(--line);border-radius:var(--radius-sm);padding:0 12px;min-height:48px;transition:border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.as-field-box:focus-within{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.as-field-box[data-multiline=true]{padding:10px 12px;align-items:flex-start}
.as-field-box[data-error=true]{border-color:var(--live)}
.as-field-box[data-error=true]:focus-within{box-shadow:0 0 0 1px var(--live)}
.as-field-box[data-disabled=true]{opacity:.45}
.as-field input,.as-field textarea{flex:1;min-width:0;appearance:none;background:none;border:0;outline:0;color:var(--ink);font:400 var(--size-body)/1.5 var(--font-body);padding:0;resize:vertical}
.as-field[data-mono=true] input,.as-field[data-mono=true] textarea{font-variant-numeric:tabular-nums lining-nums;letter-spacing:.02em}
.as-field input::placeholder,.as-field textarea::placeholder{color:var(--faint)}
.as-field-aff{font:400 var(--size-caption) var(--font-body);color:var(--faint);flex:none}
.as-field-help{font:400 var(--size-caption)/1.45 var(--font-body);color:var(--faint);display:flex;gap:6px;justify-content:space-between}
.as-field-help[data-error=true]{color:var(--live)}
.as-field-help b{font-weight:600}`);
  const uid = id || React.useId();
  const Input = multiline ? 'textarea' : 'input';
  return <div className="as-field" data-mono={mono||undefined}>
    {label && <label className="as-field-lab" htmlFor={uid}>{label}{required && <i aria-hidden="true">required</i>}</label>}
    <div className="as-field-box" data-multiline={multiline||undefined} data-error={!!error||undefined} data-disabled={disabled||undefined}>
      {prefix && <span className="as-field-aff">{prefix}</span>}
      <Input id={uid} type={multiline?undefined:type} rows={multiline?rows:undefined} value={value}
        defaultValue={defaultValue} placeholder={placeholder} disabled={disabled} maxLength={maxLength}
        aria-invalid={!!error||undefined} aria-describedby={(helper||error)?uid+'-h':undefined}
        onChange={onChange} {...rest}/>
      {suffix && <span className="as-field-aff">{suffix}</span>}
    </div>
    {(helper||error||counter) && <div className="as-field-help" id={uid+'-h'} data-error={!!error||undefined}>
      <span>{error ? <><b>Error ·</b> {error}</> : helper}</span>
      {counter && maxLength && <span className="t-tabular">{String(value||'').length}/{maxLength}</span>}
    </div>}
  </div>;
}
