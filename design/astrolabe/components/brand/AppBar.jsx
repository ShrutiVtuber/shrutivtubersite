import React from 'react';
import { IconButton } from '../forms/IconButton.jsx';
/* The top bar of a pushed or tabbed screen. Title in EB Garamond, because the
   app talks in her voice even in its chrome. The hem sits under it and takes
   the ruling hour's colour — the one place the sky tints the shell. */
export function AppBar({ title, subtitle, back, onBack, actions, hour=true, large=false, sticky=true }) {
  return (
    <header className={'hem hem-bottom' + (hour ? ' hem-hour' : '')} style={{
      position: sticky ? 'sticky' : 'relative', top:0, zIndex:20, background:'var(--page)',
      display:'grid', gridTemplateColumns:'auto 1fr auto', alignItems:'center',
      gap:4, padding:'0 6px', minHeight:large?72:'var(--appbar-h)'
    }}>
      {back ? <IconButton icon="arrow_back" label="Back" onClick={onBack} tone="ink"/> : <span style={{ width:8 }}/>}
      <div style={{ minWidth:0, padding:back?'0':'0 10px' }}>
        <div style={{
          font:`${large?500:600} ${large?'26px':'19px'}/1.2 var(--font-display)`, color:'var(--ink)',
          letterSpacing:'-0.01em', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'
        }}>{title}</div>
        {subtitle && <div className="t-caption" style={{ marginTop:2, overflow:'hidden',
          textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{subtitle}</div>}
      </div>
      <div style={{ display:'flex', alignItems:'center' }}>{actions}</div>
    </header>
  );
}
