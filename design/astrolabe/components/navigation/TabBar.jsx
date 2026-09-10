import React from 'react';
import { Icon } from '../marks/Icon.jsx';
export const TABS = [
  { id:'home', label:'Home', icon:'cottage' },
  { id:'sky', label:'Sky', icon:'clear_night' },
  { id:'chart', label:'Chart', icon:'target' },
  { id:'letters', label:'Letters', icon:'text_fields_alt' },
  { id:'practice', label:'Practice', icon:'group' },
  { id:'settings', label:'Settings', icon:'tune' }
];
/* Six tabs. At 360px that is 60px each, so the icon carries the weight — but
   the label always stays: an unlabelled icon row is a memory test.

   Selection is four things at once, none of them colour alone: a gilt hem over
   the item, a warm wash behind the icon, the icon filled, and the label at full
   ink. The bar sits on the inset well rather than the card, so it reads as the
   floor of the app instead of another card. */
export function TabBar({ tabs = TABS, active = 'home', badges = {}, onChange }) {
  return (
    <nav aria-label="Sections" style={{ position:'relative', flex:'none', display:'grid',
      gridTemplateColumns:`repeat(${tabs.length},1fr)`,
      background:'linear-gradient(180deg,var(--card) 0%,var(--inset) 100%)',
      borderTop:'1px solid var(--line)', minHeight:'var(--tabbar-h)',
      paddingBottom:'env(safe-area-inset-bottom,0)' }}>
      <span aria-hidden="true" style={{ position:'absolute', top:0, left:0, right:0, height:1,
        background:'linear-gradient(90deg,transparent,color-mix(in srgb,var(--ornament) 42%,transparent) 26%,color-mix(in srgb,var(--ornament) 42%,transparent) 74%,transparent)',
        transition:'background var(--dur-3) var(--ease-in-out)' }}/>
      {tabs.map(t => {
        const on = t.id === active;
        return (
          <button key={t.id} type="button" onClick={()=>onChange&&onChange(t.id)}
            aria-current={on?'page':undefined} style={{
              position:'relative', appearance:'none', background:'none', border:0, cursor:'pointer',
              display:'grid', justifyItems:'center', alignContent:'center', gap:5,
              padding:'9px 1px 8px', minHeight:'var(--tabbar-h)',
              color: on ? 'var(--ink)' : 'var(--faint)',
              transition:'color var(--dur-2) var(--ease-out)' }}>
            {on && <span aria-hidden="true" style={{ position:'absolute', top:0, left:'18%',
              right:'18%', height:2, borderRadius:'0 0 2px 2px', background:'var(--ornament)',
              boxShadow:'0 0 10px color-mix(in srgb,var(--ornament) 55%,transparent)',
              transition:'background var(--dur-3) var(--ease-in-out)' }}/>}
            <span style={{ position:'relative', display:'grid', placeItems:'center',
              width:44, height:26, borderRadius:'var(--radius-full)',
              background: on ? 'color-mix(in srgb,var(--ornament) 15%,transparent)' : 'transparent',
              transition:'background var(--dur-2) var(--ease-out)' }}>
              <Icon name={t.icon} size={21} fill={on?1:0} tone={on?'ink':'faint'}/>
              {badges[t.id] ? <span aria-hidden="true" style={{ position:'absolute', top:-1,
                right:6, width:7, height:7, borderRadius:99, background:'var(--live)',
                border:'1.5px solid var(--card)' }}/> : null}
            </span>
            <span style={{ font:(on?600:400)+' 10px/1 var(--font-body)', letterSpacing:'.015em',
              whiteSpace:'nowrap' }}>{t.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
