import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Hero({greeting,title,subtitle,actions,footnote,art,artAlt='',clouds,minHeight=420}){
  css('sh-hero',`.sh-hero{position:relative;border-radius:var(--radius-lg);overflow:hidden;background:linear-gradient(180deg,var(--sky-zenith) 0%,var(--sky-mid) 58%,var(--sky-horizon) 100%);transition:background var(--dur-3) var(--ease-in-out);display:flex;align-items:flex-end}.sh-hero .sh-hero-horizon{position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--horizon-line)}.sh-hero .sh-hero-clouds{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.28;mix-blend-mode:luminosity;pointer-events:none}.sh-hero .sh-hero-stars{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity var(--dur-3) var(--ease-in-out);background-image:radial-gradient(1px 1px at 12% 22%,rgba(233,230,240,.9) 50%,transparent 51%),radial-gradient(1px 1px at 28% 8%,rgba(233,230,240,.7) 50%,transparent 51%),radial-gradient(1.5px 1.5px at 44% 30%,rgba(233,230,240,.8) 50%,transparent 51%),radial-gradient(1px 1px at 61% 12%,rgba(233,230,240,.6) 50%,transparent 51%),radial-gradient(1px 1px at 73% 26%,rgba(233,230,240,.85) 50%,transparent 51%),radial-gradient(1.5px 1.5px at 86% 9%,rgba(233,230,240,.7) 50%,transparent 51%),radial-gradient(1px 1px at 93% 41%,rgba(233,230,240,.6) 50%,transparent 51%)}
[data-theme=dark] .sh-hero .sh-hero-stars{opacity:1}@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .sh-hero .sh-hero-stars{opacity:1}}
.sh-hero .sh-hero-inner{position:relative;z-index:2;display:grid;gap:16px;padding:clamp(24px,5vw,56px);max-width:60ch}
.sh-hero .sh-hero-greet{font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-soft)}
.sh-hero .sh-hero-title{font-family:var(--font-display);font-size:var(--text-hero);line-height:var(--leading-display);font-weight:500;letter-spacing:-0.01em;color:var(--ink);margin:0;text-wrap:balance}
.sh-hero .sh-hero-sub{font-family:var(--font-body);font-size:var(--text-h4);line-height:var(--leading-body);color:var(--ink-soft);margin:0;max-width:46ch}
.sh-hero .sh-hero-actions{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:4px}
.sh-hero .sh-hero-foot{margin-top:8px}
.sh-hero .sh-hero-art{position:absolute;right:clamp(16px,5vw,64px);bottom:0;z-index:1;width:clamp(200px,30%,340px);aspect-ratio:1;object-fit:cover;border-radius:var(--radius-lg) var(--radius-lg) 0 0;border:var(--border-w) solid color-mix(in srgb,var(--ink) 18%,transparent);border-bottom:0;box-shadow:var(--shadow-2)}
.sh-hero[data-art=present] .sh-hero-inner{max-width:min(56ch,58%)}
.sh-hero .sh-hero-moon{position:absolute;z-index:1;right:clamp(24px,8vw,96px);top:18%;width:clamp(56px,9vw,96px);aspect-ratio:1;border-radius:50%;border:1px solid color-mix(in srgb,var(--ink) 22%,transparent);background:color-mix(in srgb,var(--surface-card) 14%,transparent);pointer-events:none}
@media (max-width:720px){.sh-hero{align-items:flex-start}.sh-hero .sh-hero-art{position:relative;right:auto;display:block;margin:0 auto;width:min(70%,300px);order:2}.sh-hero[data-art=present]{flex-direction:column;align-items:stretch}.sh-hero[data-art=present] .sh-hero-inner{max-width:100%}}`);
  return <section className="sh-hero" data-art={art?'present':'absent'} style={{minHeight}}>
    {clouds&&<img className="sh-hero-clouds" src={clouds} alt="" aria-hidden="true"/>}
    <div className="sh-hero-stars" aria-hidden="true"></div>
    {!art&&<div className="sh-hero-moon" aria-hidden="true"></div>}
    <div className="sh-hero-inner">
      {greeting&&<span className="sh-hero-greet">{greeting}</span>}
      <h1 className="sh-hero-title">{title}</h1>
      {subtitle&&<p className="sh-hero-sub">{subtitle}</p>}
      {actions&&<div className="sh-hero-actions">{actions}</div>}
      {footnote&&<div className="sh-hero-foot">{footnote}</div>}
    </div>
    {art&&<img className="sh-hero-art" src={art} alt={artAlt}/>}
    <div className="sh-hero-horizon" aria-hidden="true"></div>
  </section>;
}
