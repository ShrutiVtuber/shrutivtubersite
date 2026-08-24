import React from 'react';

export function LegalImprint({
  entity = 'ShrutiVTuber, LLC',
  street = '[street, no.]',
  postcode = '[postcode]',
  city = 'Athens',
  country = 'GR',
  email = 'business@shrutivtuber.com',
  registry = 'GEMI [000000000000]',
  vat = 'VAT EL[000000000]',
  layout = 'stacked'
}) {
  const inline = layout === 'inline';
  const wrap = {
    margin: 0,
    font: `400 var(--text-xs)/${inline ? '1.7' : '1.9'} var(--font-mono)`,
    color: 'var(--ink-faint)',
    maxWidth: inline ? '68ch' : '40ch'
  };
  const sep = inline ? ' · ' : null;
  return (
    <div>
      <p className="t-eyebrow" style={{ margin: '0 0 8px' }}>Imprint</p>
      <p style={wrap}>
        {entity}{sep || <br />}
        Registered office (virtual): {street} · {postcode} {city}, {country}{sep || <br />}
        <a href={`mailto:${email}`} style={{ color: 'var(--accent)', textDecoration: 'none' }}>{email}</a>{sep || <br />}
        {registry} · {vat}
      </p>
    </div>
  );
}
