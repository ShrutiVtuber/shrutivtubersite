import React from 'react';
function css(id,txt){if(typeof document!=='undefined'&&!document.getElementById(id)){const s=document.createElement('style');s.id=id;s.textContent=txt;document.head.appendChild(s)}}
export function LiveBadge({status='unknown',title,game,viewers,nextStream,href,compact=false}){
  css('sh-livebadge',`.sh-live{display:inline-flex;align-items:center;gap:10px;min-height:40px;padding:6px 14px 6px 10px;border-radius:var(--radius-full);border:var(--border-w) solid var(--line);background:var(--surface-card);font-family:var(--font-body);font-size:var(--text-sm);color:var(--ink-soft);text-decoration:none;max-width:100%;transition:border-color var(--dur-1) var(--ease-out)}a.sh-live:hover{border-color:var(--line-strong);color:var(--ink-soft)}.sh-live .sh-dot{width:8px;height:8px;border-radius:99px;flex:none}.sh-live[data-status=live]{border-color:color-mix(in srgb,var(--live) 45%,transparent);background:var(--live-wash)}.sh-live[data-status=live] .sh-dot{background:var(--live);animation:sh-pulse 2s var(--ease-in-out) infinite}.sh-live[data-status=offline] .sh-dot{background:var(--ink-faint);opacity:.5}.sh-live[data-status=unknown] .sh-dot{background:transparent;border:1.5px dashed var(--ink-faint);width:7px;height:7px}.sh-live .sh-word{font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:var(--text-micro)}.sh-live[data-status=live] .sh-word{color:var(--live)}.sh-live .sh-meta{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sh-live .sh-meta b{font-weight:600;color:var(--ink)}.sh-live .sh-count{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:var(--text-xs);color:var(--ink-faint);flex:none}@keyframes sh-pulse{0%,100%{opacity:1}50%{opacity:.35}}`);
  const Tag=href?'a':'span';
  const word=status==='live'?'Live':status==='offline'?'Offline':'Status unavailable';
  return <Tag className="sh-live" data-status={status} href={href} role="status" aria-live="polite">
    <span className="sh-dot" aria-hidden="true"></span>
    <span className="sh-word">{word}</span>
    {!compact&&status==='live'&&(title||game)&&<span className="sh-meta"><b>{title}</b>{game?<> · {game}</>:null}</span>}
    {!compact&&status==='live'&&viewers!=null&&<span className="sh-count">{Intl.NumberFormat().format(viewers)} watching</span>}
    {!compact&&status==='offline'&&<span className="sh-meta">{nextStream?<>next: <b>{nextStream}</b></>:'streams announced on Discord'}</span>}
    {!compact&&status==='unknown'&&<span className="sh-meta">check Twitch directly</span>}
  </Tag>;
}
