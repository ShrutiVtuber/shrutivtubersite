import React from 'react';
import { IconButton } from '../forms/IconButton.jsx';
/* Two dialogs.
   small      — a confirm. One question, two buttons, the destructive one outlined.
   fullscreen — the sky drawer: reference material that wants the whole screen but
                is not a place in the app, so it closes rather than pops. */
export function Dialog({ open=true, size='small', title, subtitle, onClose, actions, children }) {
  if (!open) return null;
  const full = size === 'fullscreen';
  return (
    <div style={{ position:'absolute', inset:0, zIndex:70, display:'grid',
      alignItems:full?'stretch':'center', justifyItems:'center', padding:full?0:20 }}>
      <div onClick={full?undefined:onClose} style={{ position:'absolute', inset:0,
        background:'rgba(9,12,22,.7)', animation:'as-fade var(--dur-2) var(--ease-out)' }}/>
      <section role="dialog" aria-modal="true" aria-label={title} className={full?'hem hem-hour':'hem'} style={{
        position:'relative', width:'100%', maxWidth:full?'none':400, background:'var(--card)',
        border:full?'none':'1px solid var(--line)', borderRadius:full?0:'var(--radius-lg)',
        boxShadow:'var(--shadow-3)', display:'grid', gridTemplateRows:'auto 1fr auto',
        overflow:'hidden', animation: full ? 'as-push var(--dur-2) var(--ease-sheet)' : 'as-pop var(--dur-2) var(--ease-out)'
      }}>
        <style>{'@keyframes as-pop{from{transform:scale(.97);opacity:0}to{transform:none;opacity:1}}@keyframes as-push{from{transform:translateY(24px);opacity:.5}to{transform:none;opacity:1}}@keyframes as-fade{from{opacity:0}to{opacity:1}}'}</style>
        <header style={{ display:'grid', gridTemplateColumns:'1fr auto', alignItems:'center', gap:8,
          padding: full ? '0 6px 0 16px' : '18px 18px 0', minHeight: full ? 'var(--appbar-h)' : 0,
          borderBottom: full ? '1px solid var(--line)' : 'none' }}>
          <div style={{ minWidth:0 }}>
            <h2 style={{ margin:0, font:`600 ${full?'19px':'var(--size-title)'}/1.25 var(--font-display)`,
              color:'var(--ink)' }}>{title}</h2>
            {subtitle && <div className="t-caption" style={{ marginTop:3 }}>{subtitle}</div>}
          </div>
          {(full||onClose) && <IconButton icon="close" label="Close" onClick={onClose}/>}
        </header>
        <div className="as-scroll" style={{ overflowY:'auto', overflowX:'hidden',
          scrollbarWidth:'none', padding: full ? '12px 12px 20px' : '12px 18px 4px',
          font:'400 var(--size-body)/1.5 var(--font-body)', color:'var(--soft)' }}>{children}</div>
        {actions && <footer style={{ display:'flex', gap:10, justifyContent:'flex-end',
          padding:'14px 18px 18px' }}>{actions}</footer>}
      </section>
    </div>
  );
}
