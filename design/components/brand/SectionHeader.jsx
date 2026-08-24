import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function SectionHeader({eyebrow,title,body,action,align='left',glyph,as:Tag='h2'}){
  css('sh-sectionheader',`.sh-sechead{display:grid;gap:10px;max-width:var(--measure-ui)}.sh-sechead[data-align=center]{justify-items:center;text-align:center;margin-inline:auto}.sh-sechead .sh-eyebrow{font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint);display:inline-flex;align-items:center;gap:8px}.sh-sechead .sh-eyebrow .sh-glyph{font-family:var(--font-display);font-size:1.1em;color:var(--rose);text-transform:none;letter-spacing:0}.sh-sechead .sh-title{font-family:var(--font-display);font-size:var(--text-h2);line-height:var(--leading-heading);font-weight:600;color:var(--ink);margin:0}.sh-sechead .sh-body{font-family:var(--font-body);font-size:var(--text-body);line-height:var(--leading-body);color:var(--ink-soft);margin:0}.sh-sechead .sh-action{margin-top:2px}`);
  return <header className="sh-sechead" data-align={align}>
    {eyebrow&&<span className="sh-eyebrow">{glyph&&<span className="sh-glyph" aria-hidden="true">{glyph}</span>}{eyebrow}</span>}
    <Tag className="sh-title">{title}</Tag>
    {body&&<p className="sh-body">{body}</p>}
    {action&&<div className="sh-action">{action}</div>}
  </header>;
}
