import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
const SLUGS={twitch:'twitch',youtube:'youtube',discord:'discord',x:'x',twitter:'x',github:'github',kofi:'kofi',instagram:'instagram',bluesky:'bluesky',mastodon:'mastodon'};
const URLS={linkedin:'https://unpkg.com/lucide-static@0.454.0/icons/linkedin.svg'};
const NAMES={twitch:'Twitch',youtube:'YouTube',discord:'Discord',x:'X',twitter:'X',github:'GitHub',linkedin:'LinkedIn',kofi:'Ko-fi',instagram:'Instagram',bluesky:'Bluesky',mastodon:'Mastodon'};
export function SocialIcon({platform,size=18}){
  const u=URLS[platform]||`https://cdn.simpleicons.org/${SLUGS[platform]||platform}`;
  return <span aria-hidden="true" style={{display:'inline-block',width:size,height:size,background:'currentColor',WebkitMask:`url(${u}) center/contain no-repeat`,mask:`url(${u}) center/contain no-repeat`,flex:'none'}}></span>;
}
export function SocialLinkRow({links=[],variant='row',size=18}){
  css('sh-socialrow',`.sh-socials{display:flex;flex-wrap:wrap;gap:6px;padding:0;margin:0;list-style:none}.sh-socials a{display:inline-flex;align-items:center;gap:8px;color:var(--ink-soft);text-decoration:none;padding:8px;border-radius:var(--radius-sm);transition:color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}.sh-socials a:hover{color:var(--accent-hover);background:var(--surface-veil)}.sh-socials a:active{transform:translateY(1px)}.sh-socials[data-variant=pills] a{border:var(--border-w) solid var(--line);padding:8px 14px}.sh-socials[data-variant=pills] a:hover{border-color:var(--line-strong)}.sh-socials .sh-lbl{font-family:var(--font-body);font-size:var(--text-sm)}`);
  return <ul className="sh-socials" data-variant={variant}>
    {links.map(l=><li key={l.platform+(l.href||'')}><a href={l.href} aria-label={l.label||NAMES[l.platform]||l.platform} title={l.label||NAMES[l.platform]||l.platform}>
      <SocialIcon platform={l.platform} size={size}/>{variant==='pills'&&<span className="sh-lbl">{l.label||NAMES[l.platform]||l.platform}</span>}
    </a></li>)}
  </ul>;
}
