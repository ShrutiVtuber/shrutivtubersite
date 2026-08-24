import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function FanArtCard({image,title,artist,artistHref,platform,onOpen}){
  css('sh-fanartcard',`.sh-fan{display:grid;gap:8px;font-family:var(--font-body)}
.sh-fan .sh-fan-img{position:relative;aspect-ratio:1;border-radius:var(--radius-md);border:var(--border-w) solid var(--line);overflow:hidden;background:var(--surface-veil);cursor:zoom-in;padding:0;appearance:none;display:block;width:100%;transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-fan .sh-fan-img:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-fan .sh-fan-img img{width:100%;height:100%;object-fit:cover;display:block}
.sh-fan .sh-fan-img[data-empty=true]{display:grid;place-items:center;cursor:default;background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon))}
.sh-fan .sh-fan-img [data-glyph]{font-family:var(--font-display);font-size:34px;color:color-mix(in srgb,var(--ink) 45%,transparent)}
.sh-fan .sh-fan-credit{display:flex;align-items:baseline;gap:6px;font-size:var(--text-sm)}
.sh-fan .sh-fan-by{color:var(--ink-faint);font-size:var(--text-xs)}
.sh-fan .sh-fan-artist{font-weight:600;color:var(--ink)}
.sh-fan a.sh-fan-artist{color:var(--ink);text-decoration-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.sh-fan a.sh-fan-artist:hover{color:var(--accent-hover)}
.sh-fan .sh-fan-title{font-size:var(--text-xs);color:var(--ink-soft);font-style:italic;font-family:var(--font-display);font-size:var(--text-sm)}`);
  return <figure className="sh-fan" style={{margin:0}}>
    {image
      ?<button type="button" className="sh-fan-img" onClick={onOpen} aria-label={`Open ${title||'fan art'} by ${artist}`}><img src={image} alt={title||`Fan art by ${artist}`} loading="lazy"/></button>
      :<span className="sh-fan-img" data-empty="true"><span data-glyph aria-hidden="true">✶</span></span>}
    <figcaption className="sh-fan-credit">
      <span className="sh-fan-by">art by</span>
      {artistHref?<a className="sh-fan-artist" href={artistHref}>{artist}</a>:<span className="sh-fan-artist">{artist}</span>}
      {platform&&<span className="sh-fan-by">on {platform}</span>}
    </figcaption>
    {title&&<span className="sh-fan-title">“{title}”</span>}
  </figure>;
}
