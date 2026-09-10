import React from 'react';
/* A label and a value, joined by an almanac dotted leader. Used wherever the app
   states a fact: chart data, place, provenance, a licence version. */
export function DataRow({ label, value, mark, leader=true, mono=true, tone='ink', small=false }) {
  const colors = { ink:'var(--ink)', soft:'var(--soft)', faint:'var(--faint)', rose:'var(--rose)',
    accent:'var(--accent)', gilt:'var(--gilt)' };
  return (
    <div style={{ display:'flex', alignItems:'baseline', gap:8, minHeight:small?24:30 }}>
      <span style={{ flex:'none', font:`400 ${small?'var(--size-caption)':'var(--size-label)'}/1.4 var(--font-body)`,
        color:'var(--faint)', display:'inline-flex', alignItems:'baseline', gap:5 }}>
        {mark && <span className="t-glyph" style={{ fontSize:13, color:'var(--gilt)' }} aria-hidden="true">{mark}</span>}
        {label}
      </span>
      {leader && <span aria-hidden="true" style={{ flex:1, minWidth:12, alignSelf:'center', height:1,
        marginTop:2, background:'repeating-linear-gradient(90deg,var(--line) 0 1px,transparent 1px 5px)' }}/>}
      <span className={mono?'t-tabular':undefined} style={{ flex:'none', textAlign:'right',
        font:`${small?400:500} ${small?'var(--size-caption)':'var(--size-data)'}/1.4 var(--font-body)`,
        color:colors[tone]||tone, maxWidth:'62%', overflow:'hidden', textOverflow:'ellipsis' }}>{value}</span>
    </div>
  );
}
