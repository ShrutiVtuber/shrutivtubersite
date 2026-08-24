import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Prose({children,html,lang,byline,className='',style}){
  css('sh-prose',`.sh-prose{font-family:var(--font-display);font-size:var(--text-prose);line-height:var(--leading-prose);color:var(--ink);max-width:var(--measure-prose)}
.sh-prose>*+*{margin-top:1em}
.sh-prose h2,.sh-prose h3{font-weight:600;line-height:var(--leading-heading);margin-top:1.6em}
.sh-prose h2{font-size:var(--text-h2)}.sh-prose h3{font-size:var(--text-h3)}
.sh-prose a{color:var(--accent)}.sh-prose a:hover{color:var(--accent-hover)}
.sh-prose strong{font-weight:600}
.sh-prose blockquote{margin:1.4em 0;padding:2px 0 2px 20px;border-left:2px solid var(--rose);font-style:italic;color:var(--ink-soft)}
.sh-prose code{font-family:var(--font-mono);font-size:.82em;background:var(--surface-veil);border:var(--border-w) solid var(--line);border-radius:4px;padding:1px 5px}
.sh-prose pre{font-family:var(--font-mono);font-size:.78em;line-height:1.6;background:var(--surface-inset);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);padding:16px 18px;overflow:auto}
.sh-prose pre code{background:none;border:0;padding:0}
.sh-prose hr{border:0;margin:2em 0;text-align:center}
.sh-prose hr::after{content:"⁂";font-size:.9em;color:var(--ink-faint);letter-spacing:.4em}
.sh-prose ul,.sh-prose ol{padding-left:1.3em}.sh-prose li+li{margin-top:.4em}
.sh-prose li::marker{color:var(--ink-faint)}
.sh-prose figure{margin:1.6em 0}.sh-prose figcaption{font-family:var(--font-body);font-size:var(--text-xs);color:var(--ink-faint);margin-top:8px}
.sh-prose img{border-radius:var(--radius-md);border:var(--border-w) solid var(--line)}
.sh-prose table{width:100%;border-collapse:collapse;font-family:var(--font-body);font-size:var(--text-sm)}
.sh-prose th{text-align:left;font-size:var(--text-micro);letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint);font-weight:600;padding:8px 12px 8px 0;border-bottom:var(--border-w) solid var(--line-strong)}
.sh-prose td{padding:10px 12px 10px 0;border-bottom:var(--border-w) solid var(--line)}
.sh-prose .sh-prose-byline{font-family:var(--font-body);font-size:var(--text-sm);color:var(--ink-faint);margin-top:2.4em;display:flex;align-items:center;gap:12px}`);
  return <div className={'sh-prose '+className} lang={lang} style={style}>
    {html?<div dangerouslySetInnerHTML={{__html:html}}></div>:children}
    {byline&&<div className="sh-prose-byline"><span className="seal seal-line">{byline}</span></div>}
  </div>;
}
