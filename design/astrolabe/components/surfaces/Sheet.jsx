import React from 'react';
import { IconButton } from '../forms/IconButton.jsx';
/* A bottom sheet: the place picker, the sunrise convention, a share row.
   28px top corners, a grab handle, and a scrim you can tap. It never covers the
   whole screen — that is a full-screen Dialog, which is a different thing. */
export function Sheet({ open=true, title, onClose, actions, children, maxHeight='72%' }) {
  if (!open) return null;
  return (
    <div style={{ position:'absolute', inset:0, zIndex:60, display:'grid', alignItems:'end' }}>
      <div onClick={onClose} style={{ position:'absolute', inset:0,
        background:'rgba(9,12,22,.62)', backdropFilter:'blur(2px)',
        animation:'as-fade var(--dur-2) var(--ease-out)' }}/>
      <section role="dialog" aria-modal="true" aria-label={title} className="hem" style={{
        position:'relative', background:'var(--card)', borderTopLeftRadius:'var(--radius-xl)',
        borderTopRightRadius:'var(--radius-xl)', borderTop:'1px solid var(--line)',
        boxShadow:'var(--shadow-3)', maxHeight, display:'grid', gridTemplateRows:'auto 1fr auto',
        animation:'as-rise var(--dur-2) var(--ease-sheet)', overflow:'hidden'
      }}>
        <style>{'@keyframes as-rise{from{transform:translateY(18px);opacity:.6}to{transform:none;opacity:1}}@keyframes as-fade{from{opacity:0}to{opacity:1}}'}</style>
        <header style={{ display:'grid', justifyItems:'center', gap:10, padding:'10px 8px 6px' }}>
          <span aria-hidden="true" style={{ width:36, height:4, borderRadius:99, background:'var(--line-strong)' }}/>
          {title && <div style={{ display:'grid', gridTemplateColumns:'1fr auto', alignItems:'center',
            width:'100%', paddingLeft:16 }}>
            <h2 style={{ margin:0, font:'600 var(--size-title)/1.25 var(--font-display)', color:'var(--ink)' }}>{title}</h2>
            <IconButton icon="close" label="Close" onClick={onClose}/>
          </div>}
        </header>
        <div className="as-scroll" style={{ overflowY:'auto', overflowX:'hidden',
          scrollbarWidth:'none', padding:'0 16px 8px' }}>{children}</div>
        {actions && <footer style={{ display:'flex', gap:10, padding:'12px 16px 20px',
          borderTop:'1px solid var(--line)' }}>{actions}</footer>}
      </section>
    </div>
  );
}
