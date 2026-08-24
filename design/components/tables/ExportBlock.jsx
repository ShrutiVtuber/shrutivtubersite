import React from 'react';

export function ExportBlock({
  feedHref, fileHref, fileName = 'stations.ics', fileScope, googleLinks = [],
  meta, onCopyFeed, copyLabel = 'Copy feed URL'
}) {
  const secondary = {
    display: 'inline-flex', alignItems: 'center', minHeight: 40, padding: '0 14px',
    font: '600 var(--text-sm) var(--font-body)', color: 'var(--ink)', textDecoration: 'none',
    background: 'transparent', border: '1px solid var(--line-strong)', borderRadius: 'var(--radius-sm)', cursor: 'pointer'
  };

  return (
    <section className="export-block" style={{ display: 'grid', gap: 'var(--space-4)' }}>
      <p className="t-eyebrow" style={{ margin: 0 }}>Take it with you</p>

      {/* The feed is the habit-forming route, so it is the only one styled as a primary action. */}
      <div style={{
        background: 'var(--surface-card)', border: '1px solid var(--line-strong)',
        borderRadius: 'var(--radius-md)', boxShadow: 'var(--shadow-1)', padding: 'var(--space-4)', display: 'grid', gap: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
          <h3 style={{ margin: 0, font: '600 var(--text-h4) var(--font-display)', color: 'var(--ink)' }}>
            Subscribe to the feed
          </h3>
          <span style={{
            font: '600 .625rem var(--font-mono)', letterSpacing: 'var(--tracking-caps)',
            textTransform: 'uppercase', color: 'var(--rose)'
          }}>stays correct · notifies</span>
        </div>
        <p style={{ margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)', maxWidth: '58ch' }}>
          Your calendar re-reads this as the year turns, so the times keep matching the sky and your
          reminders keep arriving. This is the one that becomes a habit.
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', alignItems: 'center' }}>
          <a href={feedHref} style={{
            display: 'inline-flex', alignItems: 'center', minHeight: 44, padding: '0 18px',
            font: '600 var(--text-sm) var(--font-body)', color: 'var(--on-accent)', textDecoration: 'none',
            background: 'var(--accent)', border: '1px solid var(--accent)', borderRadius: 'var(--radius-sm)'
          }}>Subscribe in my calendar</a>
          <button type="button" onClick={onCopyFeed} style={secondary}>{copyLabel}</button>
        </div>
        <code style={{
          font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)', wordBreak: 'break-all'
        }}>{feedHref}</code>
        {meta && (
          <span style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)' }}>{meta}</span>
        )}
      </div>

      <div style={{ display: 'grid', gap: 'var(--space-3)', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))' }}>
        <div style={{ display: 'grid', gap: 8, alignContent: 'start' }}>
          <h3 style={{ margin: 0, font: '600 var(--text-body) var(--font-body)', color: 'var(--ink)' }}>
            Download a snapshot
          </h3>
          <p style={{ margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)' }}>
            A fixed <code style={{ font: '400 var(--text-xs) var(--font-mono)' }}>.ics</code> file of the range shown.
            It does not update — <strong style={{ fontWeight: 600, color: 'var(--ink)' }}>it will go stale</strong>,
            so take it only if you want exactly these dates and nothing more.
          </p>
          <div><a href={fileHref} download={fileName} style={secondary}>Download .ics</a></div>
          {fileScope && (
            <span className="t-tabular" style={{ font: '400 var(--text-xs) var(--font-mono)', color: 'var(--ink-faint)' }}>
              {fileScope}
            </span>
          )}
        </div>

        {googleLinks.length > 0 && (
          <div style={{ display: 'grid', gap: 8, alignContent: 'start' }}>
            <h3 style={{ margin: 0, font: '600 var(--text-body) var(--font-body)', color: 'var(--ink)' }}>
              Add one station to Google
            </h3>
            <p style={{ margin: 0, font: '400 var(--text-sm)/1.6 var(--font-body)', color: 'var(--ink-soft)' }}>
              A single event for a single station, if you only keep one of the four.
            </p>
            <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
              {googleLinks.map(g => (
                <a key={g.label} href={g.href} style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6, minHeight: 36, padding: '0 12px',
                  font: '500 var(--text-sm) var(--font-body)', color: 'var(--accent)', textDecoration: 'none',
                  border: '1px solid var(--line)', borderRadius: 'var(--radius-full)'
                }}>
                  {g.glyph && <span aria-hidden="true" className="t-glyph" style={{ color: 'var(--rose)' }}>{g.glyph}</span>}
                  {g.label}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
