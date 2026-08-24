import React from 'react';

const { useId } = React;

export function ConsentCheckbox({ label, explanation, basis, required, error, checked, onChange, name, meta }) {
  const id = useId();
  const descId = explanation ? id + '-d' : undefined;
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '22px 1fr', gap: '4px 12px',
      padding: '14px 16px', borderRadius: 'var(--radius-md)',
      border: '1px solid ' + (error ? 'var(--live)' : 'var(--line)'),
      background: 'var(--surface-card)'
    }}>
      <input
        type="checkbox" id={id} name={name} checked={checked} onChange={onChange}
        aria-describedby={descId} aria-invalid={error ? true : undefined}
        style={{ width: 18, height: 18, margin: '2px 0 0', accentColor: 'var(--accent)', cursor: 'pointer' }}
      />
      <div style={{ display: 'grid', gap: 6, minWidth: 0 }}>
        {basis && (
          <span style={{
            font: '600 var(--text-micro) var(--font-mono)', letterSpacing: 'var(--tracking-caps)',
            textTransform: 'uppercase', color: required ? 'var(--ink-faint)' : 'var(--rose)'
          }}>{basis}{required ? ' · required' : ' · optional'}</span>
        )}
        <label htmlFor={id} style={{
          font: '400 var(--text-body)/1.5 var(--font-body)', color: 'var(--ink)', cursor: 'pointer'
        }}>{label}</label>
        {explanation && (
          <p id={descId} style={{
            margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)', maxWidth: '62ch'
          }}>{explanation}</p>
        )}
        {meta && (
          <span style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)' }}>{meta}</span>
        )}
        {error && (
          <span style={{ font: '500 var(--text-sm) var(--font-body)', color: 'var(--live)' }}>
            <span aria-hidden="true">✕ </span>{error}
          </span>
        )}
      </div>
    </div>
  );
}
