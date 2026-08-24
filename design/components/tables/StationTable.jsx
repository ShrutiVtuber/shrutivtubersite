import React from 'react';

export function StationTable({
  stations, glyphs = [], attributions = [], rows, absentLabel = 'none today', undefinedReason, caption
}) {
  if (undefinedReason) {
    return (
      <div style={{
        background: 'var(--surface-card)', border: '1px solid var(--line)', borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-1)', padding: 'clamp(28px,5vw,44px) clamp(20px,4vw,32px)'
      }}>
        <p className="t-eyebrow" style={{ margin: '0 0 10px', color: 'var(--rose)' }}>○ Cannot be reckoned</p>
        <div style={{ font: '400 1.0625rem/1.7 var(--font-display)', color: 'var(--ink)', maxWidth: '52ch' }}>
          {undefinedReason}
        </div>
      </div>
    );
  }

  const hasPhase = rows.some(r => r.phase);
  const cell = { padding: '10px 8px', borderBottom: '1px solid var(--line)', textAlign: 'right' };
  const head = {
    padding: '0 8px 8px', borderBottom: '1px solid var(--line-strong)', textAlign: 'right',
    font: '600 var(--text-micro) var(--font-body)', letterSpacing: 'var(--tracking-eyebrow)',
    textTransform: 'uppercase', color: 'var(--ink-faint)', verticalAlign: 'bottom'
  };

  return (
    <div className="station-table" style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 460 }}>
        {caption && (
          <caption style={{
            captionSide: 'top', textAlign: 'left', paddingBottom: 12,
            font: '400 var(--text-xs)/1.6 var(--font-mono)', color: 'var(--ink-faint)'
          }}>{caption}</caption>
        )}
        <thead>
          <tr>
            <th scope="col" style={{ ...head, textAlign: 'left' }}>Day</th>
            {stations.map((s, i) => (
              <th key={s} scope="col" style={head}>
                <span style={{ display: 'grid', gap: 3, justifyItems: 'end' }}>
                  {glyphs[i] && (
                    <span aria-hidden="true" className="t-glyph" style={{
                      font: '400 1.0625rem var(--font-display)', lineHeight: 1, color: 'var(--rose)', letterSpacing: 0
                    }}>{glyphs[i]}</span>
                  )}
                  <span>{s}</span>
                  {attributions[i] && (
                    <span style={{
                      font: '400 var(--text-micro) var(--font-body)', letterSpacing: 0,
                      textTransform: 'none', color: 'var(--rose)'
                    }}>{attributions[i]}</span>
                  )}
                </span>
              </th>
            ))}
            {hasPhase && <th scope="col" style={head}>Moon</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.date} className="station-row" style={r.today ? { background: 'var(--accent-wash)' } : undefined}>
              <th scope="row" style={{
                ...cell, textAlign: 'left',
                font: (r.today ? '600' : '400') + ' var(--text-sm) var(--font-body)', color: 'var(--ink)', whiteSpace: 'nowrap'
              }}>
                <span className="t-tabular">{r.date}</span>
                {r.weekday && (
                  <span style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)' }}> {r.weekday}</span>
                )}
                {r.today && (
                  <span style={{
                    font: '600 .625rem var(--font-mono)', letterSpacing: 'var(--tracking-caps)',
                    textTransform: 'uppercase', color: 'var(--accent)'
                  }}> today</span>
                )}
              </th>
              {r.times.map((t, i) => {
                const isNow = r.today && r.currentIndex === i;
                return (
                  <td key={i} className="t-tabular" style={{
                    ...cell,
                    /* Times are the reason the table exists: mono, tabular, and large enough to read
                       on a phone at dawn in poor light. */
                    font: (isNow ? '600' : '400') + ' 1.0625rem var(--font-mono)',
                    color: t === null ? 'var(--ink-faint)' : 'var(--ink)',
                    whiteSpace: 'nowrap'
                  }}>
                    {t === null
                      ? <span style={{ font: '400 var(--text-xs) var(--font-body)', fontStyle: 'italic' }}>{absentLabel}</span>
                      : t}
                    {isNow && <span aria-hidden="true" style={{ color: 'var(--accent)' }}> ·</span>}
                  </td>
                );
              })}
              {hasPhase && (
                <td className="t-tabular" style={{ ...cell, font: '400 var(--text-sm) var(--font-mono)', color: 'var(--ink-soft)', whiteSpace: 'nowrap' }}>
                  {r.phase || ''}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
