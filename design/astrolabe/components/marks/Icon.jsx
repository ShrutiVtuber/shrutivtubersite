import React from 'react';
/* A UI icon. Material Symbols Outlined — the set the Flutter app already uses. */
export function Icon({ name, size=24, tone='soft', fill=0, weight=400, label, style, ...rest }) {
  const color = { ink:'var(--ink)', soft:'var(--soft)', faint:'var(--faint)', gilt:'var(--gilt)',
    accent:'var(--accent)', rose:'var(--rose)', live:'var(--live)', hour:'var(--hour)',
    inherit:'inherit' }[tone] || tone;
  return <span className="material-symbols-outlined" role={label?'img':undefined}
    aria-label={label} aria-hidden={label?undefined:'true'}
    style={{ fontSize:size+'px', lineHeight:1, color, flex:'none', userSelect:'none',
      fontVariationSettings:`'FILL' ${fill}, 'wght' ${weight}, 'GRAD' 0, 'opsz' ${size}`,
      ...style }} {...rest}>{name}</span>;
}
