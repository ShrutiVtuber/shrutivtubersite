import React from 'react';
function css(id,txt){if(typeof document!==('undefined')&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
const LANGS={en:{code:'EN',name:'English'},el:{code:'ΕΛ',name:'Ελληνικά'},hi:{code:'हि',name:'हिन्दी'},fr:{code:'FR',name:'Français'}};
export function LanguageSwitcher({current='en',languages=['en','el','hi','fr'],onChange,hrefFor}){
  css('sh-langsw',`.sh-lang{display:inline-flex;align-items:center;border:var(--border-w) solid var(--line);border-radius:var(--radius-full);padding:2px;background:var(--surface-card);gap:2px}.sh-lang [data-l]{appearance:none;border:0;background:transparent;font-family:var(--font-body);font-size:var(--text-xs);font-weight:600;letter-spacing:.04em;color:var(--ink-faint);padding:6px 11px;border-radius:var(--radius-full);cursor:pointer;text-decoration:none;line-height:1;transition:color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}.sh-lang [data-l]:hover{color:var(--ink)}.sh-lang [data-l][aria-current=true],.sh-lang [data-l][aria-pressed=true]{background:var(--surface-veil);color:var(--ink)}`);
  return <nav className="sh-lang" aria-label="Language">
    {languages.map(l=>{const L=LANGS[l]||{code:l.toUpperCase(),name:l};
      return hrefFor
        ?<a key={l} data-l href={hrefFor(l)} lang={l} hrefLang={l} title={L.name} aria-current={l===current}>{L.code}</a>
        :<button key={l} data-l type="button" lang={l} title={L.name} aria-pressed={l===current} onClick={()=>onChange&&onChange(l)}>{L.code}</button>;
    })}
  </nav>;
}
