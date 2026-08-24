import React from 'react';

const { useId } = React;

export function SubscribeBlock({
  variant = 'panel',
  heading = 'The monthly letter',
  body = 'Your horoscope, what I published and streamed, and a letter I write by hand. Once a month, from Athens.',
  state = 'idle',
  email = '',
  onEmailChange,
  onSubmit,
  consented = false,
  onConsentChange,
  error
}) {
  const id = useId();
  const panel = variant === 'panel';
  const aside = variant === 'aside';

  if (state === 'sent') {
    return (
      <div style={{
        background: 'var(--surface-card)', border: '1px solid var(--line)',
        borderRadius: 'var(--radius-md)', boxShadow: 'var(--shadow-1)',
        padding: panel ? 'var(--space-6) var(--space-5)' : 'var(--space-5)', display: 'grid', gap: 10
      }}>
        <span aria-hidden="true" style={{ font: '400 1.5rem var(--font-display)', lineHeight: 1, color: 'var(--rose)' }}>◐</span>
        <h3 style={{ margin: 0, font: '600 var(--text-h3) var(--font-display)', color: 'var(--ink)' }}>Check your email</h3>
        <p style={{ margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)', maxWidth: '52ch' }}>
          A confirmation link is on its way to <strong style={{ fontWeight: 600, color: 'var(--ink)' }}>{email || 'your address'}</strong>.
          You are not subscribed until you click it — an unconfirmed address is not consent.
        </p>
        <p style={{ margin: 0, font: '400 var(--text-xs)/1.6 var(--font-mono)', color: 'var(--ink-faint)' }}>
          Nothing arrives yet · the link expires in 24 hours · check spam if it does not appear
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate style={{
      background: panel ? 'var(--surface-card)' : 'transparent',
      border: panel ? '1px solid var(--line)' : 'none',
      borderTop: panel ? undefined : '1px solid var(--line)',
      borderRadius: panel ? 'var(--radius-md)' : 0,
      boxShadow: panel ? 'var(--shadow-1)' : 'none',
      padding: panel ? 'var(--space-6) var(--space-5)' : 'var(--space-5) 0 0',
      display: 'grid', gap: 'var(--space-4)'
    }}>
      <div style={{ display: 'grid', gap: 6 }}>
        <h3 style={{ margin: 0, font: '600 var(--text-h3) var(--font-display)', color: 'var(--ink)' }}>{heading}</h3>
        <p style={{ margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)', maxWidth: '56ch' }}>{body}</p>
      </div>

      <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: aside ? 'wrap' : 'nowrap', alignItems: 'flex-start' }}>
        <label htmlFor={id} style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0 0 0 0)' }}>Email address</label>
        <input
          id={id} type="email" inputMode="email" autoComplete="email" placeholder="you@example.com"
          value={email} onChange={onEmailChange} aria-invalid={error ? true : undefined}
          style={{
            flex: '1 1 200px', minWidth: 0, minHeight: 44, boxSizing: 'border-box',
            font: '400 var(--text-body) var(--font-mono)', color: 'var(--ink)',
            background: 'var(--surface-page)', padding: '10px 12px',
            border: '1px solid ' + (error ? 'var(--live)' : 'var(--line-strong)'),
            borderRadius: 'var(--radius-sm)'
          }}
        />
        <button type="submit" style={{
          flex: 'none', minHeight: 44, padding: '0 18px', cursor: 'pointer',
          font: '600 var(--text-sm) var(--font-body)', color: 'var(--on-accent)',
          background: 'var(--accent)', border: '1px solid var(--accent)', borderRadius: 'var(--radius-sm)'
        }}>Subscribe</button>
      </div>
      {error && (
        <span style={{ font: '500 var(--text-sm) var(--font-body)', color: 'var(--live)' }}>
          <span aria-hidden="true">✕ </span>{error}
        </span>
      )}

      <label style={{
        display: 'grid', gridTemplateColumns: '20px 1fr', gap: '2px 10px',
        padding: 'var(--space-3)', borderRadius: 'var(--radius-sm)', background: 'var(--surface-inset)', cursor: 'pointer'
      }}>
        <input type="checkbox" checked={consented} onChange={onConsentChange}
          style={{ width: 17, height: 17, margin: '2px 0 0', accentColor: 'var(--accent)', cursor: 'pointer' }} />
        <span style={{ font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink)' }}>
          Send me the monthly letter, <strong style={{ fontWeight: 600 }}>including offers for courses and
          services</strong> when they open. I can unsubscribe in one click, and pause instead if I would rather.
        </span>
      </label>

      <p style={{ margin: 0, font: '400 var(--text-xs)/1.6 var(--font-mono)', color: 'var(--ink-faint)' }}>
        Double opt-in · one email a month · no tracking pixels · <a href="#privacy" style={{ color: 'var(--accent)' }}>what is stored</a>
      </p>
    </form>
  );
}
