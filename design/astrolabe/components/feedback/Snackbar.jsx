import React from 'react';
/* A snackbar: something happened, here is the undo. Sits above the tab bar,
   never over it. One at a time, 4s, and it never carries an error a screen
   should be showing inline. */
export function Snackbar({ open=true, children, action, onAction, tone='neutral', above=true }) {
  if (!open) return null;
  const fg = tone==='error' ? 'var(--live)' : tone==='good' ? 'var(--accent)' : 'var(--ink)';
  return (
    <div role="status" aria-live="polite" style={{ position:'absolute', left:12, right:12,
      bottom: above ? 'calc(var(--tabbar-h) + 12px)' : 12, zIndex:50, display:'flex', alignItems:'center',
      gap:12, background:'var(--veil)', border:'1px solid var(--line-strong)',
      borderRadius:'var(--radius-sm)', boxShadow:'var(--shadow-2)', padding:'12px 14px',
      animation:'as-snack var(--dur-2) var(--ease-out)' }}>
      <style>{'@keyframes as-snack{from{transform:translateY(8px);opacity:0}to{transform:none;opacity:1}}'}</style>
      <span style={{ flex:1, minWidth:0, font:'400 var(--size-label)/1.4 var(--font-body)', color:fg,
        textWrap:'pretty' }}>{children}</span>
      {action && <button type="button" onClick={onAction} style={{ flex:'none', appearance:'none',
        background:'none', border:0, padding:'4px 2px', minHeight:32, color:'var(--accent)', cursor:'pointer',
        font:'600 var(--size-caption)/1 var(--font-body)', textTransform:'none' }}>{action}</button>}
    </div>
  );
}
