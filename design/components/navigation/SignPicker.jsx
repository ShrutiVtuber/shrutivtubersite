import React from 'react';

export const SIGNS = [
  { key: 'aries', name: 'Aries', glyph: '♈︎', dates: '21 Mar – 19 Apr' },
  { key: 'taurus', name: 'Taurus', glyph: '♉︎', dates: '20 Apr – 20 May' },
  { key: 'gemini', name: 'Gemini', glyph: '♊︎', dates: '21 May – 20 Jun' },
  { key: 'cancer', name: 'Cancer', glyph: '♋︎', dates: '21 Jun – 22 Jul' },
  { key: 'leo', name: 'Leo', glyph: '♌︎', dates: '23 Jul – 22 Aug' },
  { key: 'virgo', name: 'Virgo', glyph: '♍︎', dates: '23 Aug – 22 Sep' },
  { key: 'libra', name: 'Libra', glyph: '♎︎', dates: '23 Sep – 22 Oct' },
  { key: 'scorpio', name: 'Scorpio', glyph: '♏︎', dates: '23 Oct – 21 Nov' },
  { key: 'sagittarius', name: 'Sagittarius', glyph: '♐︎', dates: '22 Nov – 21 Dec' },
  { key: 'capricorn', name: 'Capricorn', glyph: '♑︎', dates: '22 Dec – 19 Jan' },
  { key: 'aquarius', name: 'Aquarius', glyph: '♒︎', dates: '20 Jan – 18 Feb' },
  { key: 'pisces', name: 'Pisces', glyph: '♓︎', dates: '19 Feb – 20 Mar' }
];

export function SignPicker({ current, onChange, hrefFor, ownSign, layout = 'grid' }) {
  const row = layout === 'row';
  const wrap = row
    ? { display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }
    : { display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(150px,1fr))', gap: 'var(--space-3)' };

  return (
    <div role="group" aria-label="Choose a sign" style={wrap}>
      {SIGNS.map(s => {
        const on = current === s.key;
        const mine = ownSign === s.key;
        const style = row
          ? {
            display: 'inline-flex', alignItems: 'baseline', gap: 6, padding: '7px 12px',
            border: '1px solid ' + (on ? 'var(--accent)' : 'var(--line)'),
            background: on ? 'var(--accent-wash)' : 'transparent',
            color: on ? 'var(--accent)' : 'var(--ink-soft)',
            borderRadius: 'var(--radius-full)', font: '500 var(--text-sm) var(--font-body)',
            textDecoration: 'none', cursor: 'pointer', minHeight: 36
          }
          : {
            display: 'grid', gap: 2, padding: '14px 16px', textAlign: 'left',
            border: '1px solid ' + (on ? 'var(--accent)' : 'var(--line)'),
            background: on ? 'var(--accent-wash)' : 'var(--surface-card)',
            borderRadius: 'var(--radius-md)', boxShadow: on ? 'none' : 'var(--shadow-1)',
            textDecoration: 'none', cursor: 'pointer', minHeight: 44,
            transition: 'border-color var(--dur-1) var(--ease-out)'
          };
        const inner = row ? (
          <>
            <span aria-hidden="true" className="t-glyph" style={{ font: '400 15px var(--font-display)', color: on ? 'var(--accent)' : 'var(--rose)' }}>{s.glyph}</span>
            <span>{s.name}</span>
            {mine && <span aria-hidden="true" style={{ font: '600 9px var(--font-mono)', letterSpacing: '.08em', color: 'var(--rose)' }}>YOURS</span>}
          </>
        ) : (
          <>
            <span style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
              <span aria-hidden="true" className="t-glyph" style={{ font: '400 1.5rem var(--font-display)', lineHeight: 1, color: 'var(--rose)' }}>{s.glyph}</span>
              <span style={{ font: '600 var(--text-h4) var(--font-display)', color: on ? 'var(--accent)' : 'var(--ink)' }}>{s.name}</span>
              {mine && <span style={{ marginLeft: 'auto', font: '600 9px var(--font-mono)', letterSpacing: '.08em', color: 'var(--rose)' }}>YOURS</span>}
            </span>
            <span className="t-tabular" style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)' }}>{s.dates}</span>
          </>
        );
        const aria = mine ? s.name + ' — your sign' : s.name;
        return hrefFor
          ? <a key={s.key} href={hrefFor(s.key)} aria-current={on ? 'page' : undefined} aria-label={aria} style={style}>{inner}</a>
          : <button key={s.key} type="button" aria-pressed={on} aria-label={aria} onClick={() => onChange && onChange(s.key)} style={style}>{inner}</button>;
      })}
    </div>
  );
}
