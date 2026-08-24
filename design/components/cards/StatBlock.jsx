import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function StatBlock({value,label,note,glyph}){
  css('sh-statblock',`.sh-stat{display:grid;gap:6px;padding:18px 20px;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);font-family:var(--font-body);position:relative}
.sh-stat .sh-st-value{font-family:var(--font-display);font-size:2.4rem;line-height:1;font-weight:500;color:var(--ink);font-variant-numeric:tabular-nums lining-nums}
.sh-stat .sh-st-label{font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint)}
.sh-stat .sh-st-note{font-size:var(--text-xs);color:var(--ink-soft)}
.sh-stat .sh-st-glyph{position:absolute;top:14px;right:16px;font-family:var(--font-display);font-size:18px;color:var(--rose)}`);
  return <div className="sh-stat">
    {glyph&&<span className="sh-st-glyph" aria-hidden="true">{glyph}</span>}
    <span className="sh-st-label">{label}</span>
    <span className="sh-st-value">{value}</span>
    {note&&<span className="sh-st-note">{note}</span>}
  </div>;
}
