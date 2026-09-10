import React from 'react';
import { Icon } from '../marks/Icon.jsx';
/* An inline notice pinned under the app bar. Four tones, and the offline one is
   the important one:
   ⚠ offline does NOT mean broken. Every instrument still computes on device.
   The copy says which half is missing, never "no connection". */
const TONES = {
  offline:{ icon:'cloud_off', fg:'var(--gilt)', bg:'var(--gilt-wash)', bd:'color-mix(in srgb,var(--gilt) 34%,transparent)' },
  error:{ icon:'error', fg:'var(--live)', bg:'var(--live-wash)', bd:'color-mix(in srgb,var(--live) 40%,transparent)' },
  note:{ icon:'info', fg:'var(--accent)', bg:'var(--accent-wash)', bd:'color-mix(in srgb,var(--accent) 34%,transparent)' },
  caution:{ icon:'priority_high', fg:'var(--rose)', bg:'var(--rose-wash)', bd:'color-mix(in srgb,var(--rose) 38%,transparent)' }
};
export function Banner({ tone='note', title, children, action, onAction, onDismiss, icon }) {
  const t = TONES[tone] || TONES.note;
  return (
    <div role={tone==='error'?'alert':'status'} style={{ display:'flex', gap:11, alignItems:'flex-start',
      background:t.bg, border:'1px solid '+t.bd, borderRadius:'var(--radius-md)', padding:'11px 13px' }}>
      <Icon name={icon||t.icon} size={19} tone={t.fg} style={{ marginTop:1 }}/>
      <div style={{ flex:1, minWidth:0, display:'grid', gap:3 }}>
        {title && <span style={{ font:'600 var(--size-label)/1.35 var(--font-body)', color:t.fg }}>{title}</span>}
        {children && <span style={{ font:'400 var(--size-caption)/1.5 var(--font-body)', color:'var(--soft)',
          textWrap:'pretty' }}>{children}</span>}
        {action && <button type="button" onClick={onAction} style={{ justifySelf:'start', appearance:'none',
          background:'none', border:0, padding:'6px 0 2px', color:t.fg, cursor:'pointer',
          font:'600 var(--size-caption)/1 var(--font-body)' }}>{action}</button>}
      </div>
      {onDismiss && <button type="button" onClick={onDismiss} aria-label="Dismiss" style={{ appearance:'none',
        background:'none', border:0, padding:2, cursor:'pointer', color:'var(--faint)', lineHeight:0 }}>
        <Icon name="close" size={17} tone="faint"/></button>}
    </div>
  );
}
