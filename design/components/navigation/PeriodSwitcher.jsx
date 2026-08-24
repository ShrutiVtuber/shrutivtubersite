import React from 'react';

const PERIODS = [
  { key: 'daily', name: 'Daily' },
  { key: 'monthly', name: 'Monthly' },
  { key: 'seasonal', name: 'Seasonal' },
  { key: 'yearly', name: 'Yearly' }
];

export function PeriodSwitcher({ current, available = ['monthly'], onChange, hrefFor, label }) {
  const shown = PERIODS.filter(p => available.indexOf(p.key) >= 0);
  // A single available period still renders — the switcher is the layout, not the choice.
  return (
    <div style={{
      display: 'flex', alignItems: 'baseline', gap: 'var(--space-3)', flexWrap: 'wrap',
      paddingBottom: 'var(--space-3)', borderBottom: '1px solid var(--line)'
    }}>
      <div role="group" aria-label="Reading period" style={{ display: 'flex', gap: 'var(--space-1)' }}>
        {shown.map(p => {
          const on = current === p.key;
          const style = {
            padding: '7px 13px', minHeight: 36, borderRadius: 'var(--radius-sm)',
            border: '1px solid ' + (on ? 'var(--line-strong)' : 'transparent'),
            background: on ? 'var(--surface-card)' : 'transparent',
            color: on ? 'var(--ink)' : 'var(--ink-soft)',
            font: (on ? '600' : '500') + ' var(--text-sm) var(--font-body)',
            textDecoration: 'none', cursor: 'pointer'
          };
          return hrefFor
            ? <a key={p.key} href={hrefFor(p.key)} aria-current={on ? 'page' : undefined} style={style}>{p.name}</a>
            : <button key={p.key} type="button" aria-pressed={on} onClick={() => onChange && onChange(p.key)} style={style}>{p.name}</button>;
        })}
      </div>
      {label && (
        <span className="t-tabular" style={{
          marginLeft: 'auto', font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)'
        }}>{label}</span>
      )}
    </div>
  );
}
