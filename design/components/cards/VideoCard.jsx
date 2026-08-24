import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
const PLAT={twitch:{name:'Twitch',slug:'twitch'},youtube:{name:'YouTube',slug:'youtube'}};
export function VideoCard({title,thumb,platform='twitch',duration,date,href='#',loading=false}){
  css('sh-videocard',`.sh-vid{display:grid;gap:10px;text-decoration:none;color:inherit;font-family:var(--font-body);border-radius:var(--radius-md);outline-offset:4px}
.sh-vid .sh-vid-thumb{position:relative;aspect-ratio:16/9;border-radius:var(--radius-md);border:var(--border-w) solid var(--line);overflow:hidden;background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon));transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-vid .sh-vid-thumb img{width:100%;height:100%;object-fit:cover;display:block}
.sh-vid .sh-vid-play{position:absolute;inset:0;margin:auto;width:44px;height:44px;border-radius:99px;background:color-mix(in srgb,var(--surface-page) 72%,transparent);backdrop-filter:blur(6px);border:var(--border-w) solid color-mix(in srgb,var(--line) 70%,transparent);display:grid;place-items:center;color:var(--ink);font-size:15px;opacity:0;transition:opacity var(--dur-1) var(--ease-out)}
.sh-vid:hover .sh-vid-play,.sh-vid:focus-visible .sh-vid-play{opacity:1}
.sh-vid[data-noart=true] .sh-vid-play{opacity:1}
.sh-vid .sh-vid-dur{position:absolute;right:8px;bottom:8px;font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:10.5px;color:var(--ink);background:color-mix(in srgb,var(--surface-page) 80%,transparent);border:var(--border-w) solid color-mix(in srgb,var(--line) 60%,transparent);border-radius:4px;padding:2px 6px}
.sh-vid:hover .sh-vid-thumb{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-vid .sh-vid-title{font-size:var(--text-sm);font-weight:600;color:var(--ink);line-height:var(--leading-tight);margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color var(--dur-1) var(--ease-out)}
.sh-vid:hover .sh-vid-title{color:var(--accent-hover)}
.sh-vid .sh-vid-meta{display:flex;align-items:center;gap:8px;font-size:var(--text-xs);color:var(--ink-faint)}
.sh-vid .sh-vid-plat{display:inline-flex;align-items:center;gap:5px;font-weight:500}
.sh-vid .sh-vid-plat i{width:12px;height:12px;display:inline-block;background:currentColor}
.sh-vid .sh-vid-horizon{position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--horizon-line)}`);
  const p=PLAT[platform]||PLAT.twitch;
  if(loading)return <VideoCardSkeleton/>;
  return <a className="sh-vid" href={href} data-noart={!thumb}>
    <span className="sh-vid-thumb">
      {thumb?<img src={thumb} alt="" loading="lazy"/>:<span className="sh-vid-horizon" aria-hidden="true"></span>}
      <span className="sh-vid-play" aria-hidden="true">▶</span>
      {duration&&<span className="sh-vid-dur">{duration}</span>}
    </span>
    <h3 className="sh-vid-title">{title}</h3>
    <span className="sh-vid-meta">
      <span className="sh-vid-plat"><i aria-hidden="true" style={{WebkitMask:`url(https://cdn.simpleicons.org/${p.slug}) center/contain no-repeat`,mask:`url(https://cdn.simpleicons.org/${p.slug}) center/contain no-repeat`}}></i>{p.name}</span>
      {date&&<>·<span>{date}</span></>}
    </span>
  </a>;
}
export function VideoCardSkeleton(){
  css('sh-vidskel','.sh-vid-skel{display:grid;gap:10px}.sh-vid-skel .sk{background:var(--surface-veil);border-radius:var(--radius-md);animation:sh-skel 1.6s var(--ease-in-out) infinite}.sh-vid-skel .sk-thumb{aspect-ratio:16/9}.sh-vid-skel .sk-t1{height:13px;width:82%;border-radius:4px}.sh-vid-skel .sk-t2{height:11px;width:40%;border-radius:4px}@keyframes sh-skel{0%,100%{opacity:1}50%{opacity:.55}}');
  return <div className="sh-vid-skel" aria-hidden="true"><span className="sk sk-thumb"></span><span className="sk sk-t1"></span><span className="sk sk-t2"></span></div>;
}
