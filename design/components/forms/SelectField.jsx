import React from 'react';
import {fieldCss} from './TextField.jsx';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
let uid=0;
export function SelectField({label,hint,error,required,disabled,id,options=[],placeholder,value,onChange,...rest}){
  css('sh-field',fieldCss);
  css('sh-select','.sh-f-selwrap{position:relative}.sh-f-selwrap select.sh-f-ctrl{padding-right:34px;cursor:pointer}.sh-f-selwrap::after{content:"▾";position:absolute;right:12px;top:50%;transform:translateY(-50%);color:var(--ink-faint);pointer-events:none;font-size:12px}');
  const fid=id||('sh-sel-'+(++uid));
  return <div className="sh-field" data-invalid={!!error} data-disabled={!!disabled}>
    <label className="sh-f-label" htmlFor={fid}>{label}{required&&<span className="sh-f-req" aria-hidden="true">*</span>}</label>
    <span className="sh-f-selwrap">
    <select className="sh-f-ctrl" id={fid} required={required} disabled={disabled} value={value} onChange={onChange}
      aria-invalid={!!error} aria-describedby={error?fid+'-err':hint?fid+'-hint':undefined} {...rest}>
      {placeholder&&<option value="" disabled>{placeholder}</option>}
      {options.map(o=>typeof o==='string'?<option key={o} value={o}>{o}</option>:<option key={o.value} value={o.value}>{o.label}</option>)}
    </select></span>
    {error?<span className="sh-f-error" id={fid+'-err'} role="alert">{error}</span>
      :hint?<span className="sh-f-hint" id={fid+'-hint'}>{hint}</span>:null}
  </div>;
}
