import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
const STATUS={active:{word:'Active',tone:'accent'},maintained:{word:'Maintained',tone:'neutral'},archived:{word:'Archived',tone:'faint'}};
export function ProjectCard({name,tagline,description,status='active',repoHref,liveHref,screenshot,meta}){
  css('sh-projectcard',`.sh-proj{display:grid;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);box-shadow:var(--shadow-1);overflow:hidden;font-family:var(--font-body);transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-proj:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-proj .sh-proj-shot{aspect-ratio:16/9;background:var(--surface-inset);border-bottom:var(--border-w) solid var(--line);position:relative;overflow:hidden}
.sh-proj .sh-proj-shot img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
.sh-proj .sh-proj-shot[data-empty=true]{display:grid;place-items:center;background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon))}
.sh-proj .sh-proj-shot [data-plate]{font-family:var(--font-mono);font-size:11px;color:var(--ink-soft);background:color-mix(in srgb,var(--surface-page) 62%,transparent);backdrop-filter:blur(8px);border:var(--border-w) solid color-mix(in srgb,var(--line) 60%,transparent);border-radius:var(--radius-sm);padding:6px 12px}
.sh-proj .sh-proj-shot [data-horizon]{position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--horizon-line)}
.sh-proj .sh-proj-body{display:grid;gap:8px;padding:18px 20px 20px}
.sh-proj .sh-proj-top{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.sh-proj .sh-proj-name{font-family:var(--font-display);font-size:var(--text-h3);font-weight:600;color:var(--ink);margin:0}
.sh-proj .sh-proj-status{font-size:var(--text-micro);font-weight:600;letter-spacing:.06em;text-transform:uppercase;border-radius:var(--radius-full);padding:3px 9px;border:var(--border-w) solid}
.sh-proj .sh-proj-status[data-tone=accent]{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent);background:var(--accent-wash)}
.sh-proj .sh-proj-status[data-tone=neutral]{color:var(--ink-soft);border-color:var(--line);background:var(--surface-veil)}
.sh-proj .sh-proj-status[data-tone=faint]{color:var(--ink-faint);border-color:var(--line);background:transparent}
.sh-proj .sh-proj-tag{font-size:var(--text-sm);color:var(--ink-soft);font-style:italic;font-family:var(--font-display);font-size:var(--text-h4)}
.sh-proj .sh-proj-desc{font-size:var(--text-sm);line-height:var(--leading-body);color:var(--ink-soft);margin:0}
.sh-proj .sh-proj-meta{font-family:var(--font-mono);font-size:10.5px;color:var(--ink-faint);letter-spacing:.02em}
.sh-proj .sh-proj-links{display:flex;gap:14px;margin-top:6px;border-top:var(--border-w) solid var(--line);padding-top:12px}
.sh-proj .sh-proj-links a{font-size:var(--text-sm);font-weight:500}`);
  const st=STATUS[status]||STATUS.active;
  return <article className="sh-proj">
    <div className="sh-proj-shot" data-empty={!screenshot}>
      {screenshot?<img src={screenshot} alt={name+' screenshot'} loading="lazy"/>:<><span data-plate>screenshot pending</span><span data-horizon aria-hidden="true"></span></>}
    </div>
    <div className="sh-proj-body">
      <div className="sh-proj-top"><h3 className="sh-proj-name">{name}</h3><span className="sh-proj-status" data-tone={st.tone}>{st.word}</span></div>
      {tagline&&<p className="sh-proj-tag">{tagline}</p>}
      {description&&<p className="sh-proj-desc">{description}</p>}
      {meta&&<span className="sh-proj-meta">{meta}</span>}
      {(repoHref||liveHref)&&<div className="sh-proj-links">
        {liveHref&&<a href={liveHref}>Visit ↗</a>}
        {repoHref&&<a href={repoHref}>Source ↗</a>}
      </div>}
    </div>
  </article>;
}
