import React from 'react';
/* Three shapes of waiting.
   bar        determinate — a pack downloading, a chart casting
   ring       indeterminate, inline — an instrument computing
   refresh    the pull-to-refresh puck: a gilt arc that turns, because the sky
              turning is the app's own idiom
   skeleton   the shape of the thing that is coming — never a grey box with no
              shape; the reading card's skeleton is a reading card. */
export function Progress({ kind='ring', value, size=22, label='Working' }) {
  if (kind === 'bar') return (
    <div role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100} aria-label={label}
      style={{ height:4, borderRadius:99, background:'var(--inset)', overflow:'hidden' }}>
      <div style={{ height:'100%', width:(value??0)+'%', background:'var(--accent)',
        transition:'width var(--dur-2) var(--ease-out)' }}/>
    </div>
  );
  if (kind === 'refresh') return (
    <div role="status" aria-label={label} style={{ display:'grid', placeItems:'center', padding:'10px 0' }}>
      <span style={{ width:30, height:30, borderRadius:99, border:'2px solid var(--line)',
        borderTopColor:'var(--gilt)', animation:'as-spin 900ms linear infinite' }}/>
      <style>{'@keyframes as-spin{to{transform:rotate(360deg)}}'}</style>
    </div>
  );
  if (kind === 'skeleton') return <Skeleton/>;
  return (
    <span role="status" aria-label={label} style={{ display:'inline-block', width:size, height:size,
      borderRadius:99, border:'2px solid var(--line)', borderTopColor:'var(--accent)',
      animation:'as-spin 700ms linear infinite' }}>
      <style>{'@keyframes as-spin{to{transform:rotate(360deg)}}'}</style></span>
  );
}
export function Skeleton({ lines=3, title=true, height }) {
  return (
    <div aria-hidden="true" style={{ display:'grid', gap:10 }}>
      <style>{'@keyframes as-shim{0%,100%{opacity:.5}50%{opacity:.85}}'}</style>
      {title && <Bar w="62%" h={16}/>}
      {height ? <Bar w="100%" h={height}/> : Array.from({length:lines},(_,i)=>
        <Bar key={i} w={i===lines-1?'48%':'100%'} h={11}/>)}
    </div>
  );
}
function Bar({ w, h }) {
  return <span style={{ display:'block', width:w, height:h, borderRadius:4, background:'var(--veil)',
    animation:'as-shim 1.6s var(--ease-in-out) infinite' }}/>;
}
