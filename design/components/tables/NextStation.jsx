import React from 'react';

export function NextStation({
  name, glyph, at, inLabel, currentName, currentSince, attribution,
  progress = 0, size = 'hero', undefinedReason
}) {
  const hero = size === 'hero';

  if (undefinedReason) {
    return (
      <div style={{
        border: '1px solid var(--line)', borderRadius: 'var(--radius-md)',
        background: 'var(--surface-card)', padding: hero ? 'var(--space-5)' : 'var(--space-4)', display: 'grid', gap: 8
      }}>
        <span className="t-eyebrow" style={{ margin: 0, color: 'var(--rose)' }}>○ No station to count to</span>
        <p style={{ margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)', maxWidth: '48ch' }}>
          {undefinedReason}
        </p>
      </div>
    );
  }

  return (
    <div style={{
      border: '1px solid var(--line)', borderRadius: 'var(--radius-md)', background: 'var(--surface-card)',
      boxShadow: 'var(--shadow-1)', padding: hero ? 'var(--space-5)' : 'var(--space-4)', display: 'grid', gap: hero ? 14 : 10
    }}>
      {currentName && (
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
          <span className="t-eyebrow" style={{ margin: 0 }}>Now</span>
          <span style={{ font: '500 var(--text-sm) var(--font-body)', color: 'var(--ink)' }}>{currentName}</span>
          {currentSince && (
            <span className="t-tabular" style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)' }}>
              since {currentSince}
            </span>
          )}
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'baseline', gap: hero ? 14 : 10, flexWrap: 'wrap' }}>
        {glyph && (
          <span aria-hidden="true" className="t-glyph" style={{
            font: `400 ${hero ? '2.25rem' : '1.5rem'} var(--font-display)`, lineHeight: 1, color: 'var(--rose)'
          }}>{glyph}</span>
        )}
        <div style={{ display: 'grid', gap: 2, minWidth: 0 }}>
          <span style={{ font: `600 ${hero ? 'var(--text-h3)' : 'var(--text-body)'} var(--font-display)`, color: 'var(--ink)' }}>
            {name}
          </span>
          {attribution && (
            <span style={{ font: '400 var(--text-xs) var(--font-body)', color: 'var(--rose)' }}>{attribution}</span>
          )}
        </div>
        <div style={{ marginLeft: 'auto', textAlign: 'right', display: 'grid', gap: 2 }}>
          {/* The countdown is the answer. It is the largest number on the page. */}
          <span className="t-tabular" style={{
            font: `500 ${hero ? 'clamp(1.75rem,5vw,2.5rem)' : '1.375rem'} var(--font-mono)`,
            lineHeight: 1, color: 'var(--ink)'
          }}>in {inLabel}</span>
          <span className="t-tabular" style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-soft)' }}>
            at {at} your time
          </span>
        </div>
      </div>

      <div aria-hidden="true" style={{ height: 2, background: 'var(--line)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{
          width: Math.max(0, Math.min(1, progress)) * 100 + '%', height: '100%',
          background: 'var(--rose)', transition: 'width var(--dur-2) var(--ease-out)'
        }}></div>
      </div>
    </div>
  );
}
