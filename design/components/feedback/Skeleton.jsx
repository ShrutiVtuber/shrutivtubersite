import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function Skeleton({variant='line',width,height,lines=1,style}){
  css('sh-skeleton',`.sh-skel{display:block;background:var(--surface-veil);border-radius:4px;animation:sh-skel-pulse 1.6s var(--ease-in-out) infinite}
.sh-skel[data-variant=rect]{border-radius:var(--radius-md)}
.sh-skel[data-variant=circle]{border-radius:999px}
.sh-skel-group{display:grid;gap:8px}
@keyframes sh-skel-pulse{0%,100%{opacity:1}50%{opacity:.55}}`);
  if(variant==='text'&&lines>1){
    return <span className="sh-skel-group" aria-hidden="true" style={style}>
      {Array.from({length:lines}).map((_,i)=><span key={i} className="sh-skel" data-variant="line" style={{height:height||12,width:i===lines-1?'62%':(width||'100%')}}></span>)}
    </span>;
  }
  const dim=variant==='circle'?{width:width||40,height:width||40}:{width:width||(variant==='rect'?'100%':'100%'),height:height||(variant==='rect'?96:12)};
  return <span className="sh-skel" data-variant={variant} aria-hidden="true" style={{...dim,...style}}></span>;
}
