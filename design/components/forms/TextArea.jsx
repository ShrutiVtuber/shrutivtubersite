import React from 'react';
import {fieldCss} from './TextField.jsx';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
let uid=0;
export function TextArea({label,hint,error,success,required,optionalLabel,disabled,id,rows=5,maxLength,value,...rest}){
  css('sh-field',fieldCss);
  css('sh-textarea','.sh-field textarea.sh-f-ctrl{resize:vertical;min-height:110px;line-height:var(--leading-body)}.sh-f-count{font-family:var(--font-mono);font-size:10.5px;color:var(--ink-faint);justify-self:end;font-variant-numeric:tabular-nums}');
  const fid=id||('sh-ta-'+(++uid));
  return <div className="sh-field" data-invalid={!!error} data-disabled={!!disabled}>
    <label className="sh-f-label" htmlFor={fid}>{label}{required&&<span className="sh-f-req" aria-hidden="true">*</span>}{!required&&optionalLabel&&<span className="sh-f-optional">optional</span>}</label>
    <textarea className="sh-f-ctrl" id={fid} rows={rows} required={required} disabled={disabled} maxLength={maxLength} value={value}
      aria-invalid={!!error} aria-describedby={error?fid+'-err':hint?fid+'-hint':undefined} {...rest}></textarea>
    {error?<span className="sh-f-error" id={fid+'-err'} role="alert">{error}</span>
      :success?<span className="sh-f-ok">{success}</span>
      :hint?<span className="sh-f-hint" id={fid+'-hint'}>{hint}</span>:null}
    {maxLength&&typeof value==='string'&&<span className="sh-f-count">{value.length} / {maxLength}</span>}
  </div>;
}
