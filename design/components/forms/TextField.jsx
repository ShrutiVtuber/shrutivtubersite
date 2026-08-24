import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export const fieldCss=`.sh-field{display:grid;gap:6px;font-family:var(--font-body);max-width:var(--measure-ui)}
.sh-field .sh-f-label{font-size:var(--text-sm);font-weight:600;color:var(--ink);display:flex;gap:6px;align-items:baseline}
.sh-field .sh-f-req{color:var(--rose)}
.sh-field .sh-f-optional{font-weight:400;font-size:var(--text-xs);color:var(--ink-faint)}
.sh-field .sh-f-ctrl{appearance:none;width:100%;box-sizing:border-box;font:inherit;font-size:var(--text-body);color:var(--ink);background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-sm);padding:10px 12px;min-height:44px;transition:border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-field .sh-f-ctrl::placeholder{color:var(--ink-faint)}
.sh-field .sh-f-ctrl:hover{border-color:var(--line-strong)}
.sh-field .sh-f-ctrl:focus-visible{outline:2px solid var(--focus-ring);outline-offset:1px;border-color:var(--accent)}
.sh-field[data-invalid=true] .sh-f-ctrl{border-color:var(--live);background:color-mix(in srgb,var(--live-wash) 55%,var(--surface-card))}
.sh-field[data-disabled=true]{opacity:.55}.sh-field[data-disabled=true] .sh-f-ctrl{background:var(--surface-inset);cursor:not-allowed}
.sh-field .sh-f-hint{font-size:var(--text-xs);color:var(--ink-faint)}
.sh-field .sh-f-error{font-size:var(--text-xs);color:var(--live);display:flex;gap:6px;align-items:baseline}
.sh-field .sh-f-error::before{content:"✕";font-size:.9em}
.sh-field .sh-f-ok{font-size:var(--text-xs);color:var(--accent);display:flex;gap:6px;align-items:baseline}.sh-field .sh-f-ok::before{content:"✓"}`;
let uid=0;
export function TextField({label,hint,error,success,required,optionalLabel,disabled,id,type='text',...rest}){
  css('sh-field',fieldCss);
  const fid=id||('sh-tf-'+(++uid));
  return <div className="sh-field" data-invalid={!!error} data-disabled={!!disabled}>
    <label className="sh-f-label" htmlFor={fid}>{label}{required&&<span className="sh-f-req" aria-hidden="true">*</span>}{!required&&optionalLabel&&<span className="sh-f-optional">optional</span>}</label>
    <input className="sh-f-ctrl" id={fid} type={type} required={required} disabled={disabled}
      aria-invalid={!!error} aria-describedby={error?fid+'-err':hint?fid+'-hint':undefined} {...rest}/>
    {error?<span className="sh-f-error" id={fid+'-err'} role="alert">{error}</span>
      :success?<span className="sh-f-ok">{success}</span>
      :hint?<span className="sh-f-hint" id={fid+'-hint'}>{hint}</span>:null}
  </div>;
}
