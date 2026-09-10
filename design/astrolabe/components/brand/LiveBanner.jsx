import React from 'react';
import { Glyph } from '../marks/Glyph.jsx';
/* Live is a state the app is in, not a badge on a card.
   live      — the plate warms, the hem goes rose, the dot pulses, the title is the stream's
   offline   — a quiet line with the next stream, if one is known
   unknown   — we could not reach her side. Never says "offline"; never fakes liveness.
   Stamp data-live="true" on the shell to turn the whole app's ornament rose. */
export function LiveBanner({ status='offline', title, game, viewers, nextStream, onOpen, compact=false }) {
  const live = status==='live';
  const word = live ? 'Live now' : status==='offline' ? 'Not live' : 'Status unavailable';
  const line = live ? [title, game].filter(Boolean).join(' · ')
    : status==='offline' ? (nextStream ? 'Next: ' + nextStream : 'Streams are announced on Discord first')
    : 'Could not reach Twitch — check directly';
  const Tag = onOpen ? 'button' : 'div';
  return (
    <Tag onClick={onOpen} type={onOpen?'button':undefined} className={live?'hem hem-strong':'hem'} style={{
      display:'flex', alignItems:'center', gap:12, width:'100%', textAlign:'left', cursor:onOpen?'pointer':'default',
      background: live ? 'linear-gradient(96deg,var(--live-wash) 0%,var(--card) 62%)' : 'var(--card)',
      border:'1px solid ' + (live ? 'color-mix(in srgb,var(--live) 42%,transparent)' : 'var(--line)'),
      borderRadius:'var(--radius-md)', padding: compact ? '10px 14px' : '14px 16px',
      minHeight:'var(--tap-comfort)', color:'inherit',
      transition:'background var(--dur-3) var(--ease-in-out),border-color var(--dur-3) var(--ease-in-out)'
    }} role="status" aria-live="polite">
      <Dot status={status}/>
      <span style={{ flex:1, minWidth:0, display:'grid', gap:3 }}>
        <span className="t-eyebrow" style={{ color: live ? 'var(--live)' : 'var(--faint)' }}>{word}</span>
        <span style={{ font:'400 var(--size-label)/1.35 var(--font-body)', color: live?'var(--ink)':'var(--soft)',
          overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{line}</span>
      </span>
      {live && viewers!=null && <span className="t-data" style={{ color:'var(--faint)', fontSize:'var(--size-caption)', flex:'none' }}>
        {Intl.NumberFormat().format(viewers)}<span aria-hidden="true"> watching</span></span>}
      {!live && status==='unknown' && <Glyph name="moon" tone="faint" size="sm"/>}
    </Tag>
  );
}
function Dot({ status }) {
  if (status==='unknown') return <span aria-hidden="true" style={{ flex:'none', width:10, height:10,
    borderRadius:99, border:'1.5px dashed var(--faint)' }}/>;
  if (status==='offline') return <span aria-hidden="true" style={{ flex:'none', width:10, height:10,
    borderRadius:99, background:'var(--faint)', opacity:.45 }}/>;
  return <span aria-hidden="true" style={{ flex:'none', width:10, height:10, borderRadius:99,
    background:'var(--live)', boxShadow:'var(--glow-live)', animation:'as-live-pulse 2s var(--ease-in-out) infinite' }}>
    <style>{'@keyframes as-live-pulse{0%,100%{opacity:1}50%{opacity:.4}}'}</style></span>;
}
