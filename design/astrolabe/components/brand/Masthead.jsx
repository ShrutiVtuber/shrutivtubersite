import React from 'react';
/* Home's one brand surface. Cloak navy with the light it catches in her
   artwork, a real scatter of stars, a gold hem top and bottom, and her
   portrait standing in the right third.

   Two honest portrait states, because she has one kind of art today and will
   draw the other:
     fit="cutout"  a transparent PNG, bottom-anchored, bleeding off the edge —
                   what artwork-spec.md #3 and #4 ask for
     fit="plate"   an opaque square (the existing painted references), framed
                   with a hairline. Never silhouetted, never faked.

   ⚠ Art-absent is a designed state, not a fallback: with no portrait the plate
   keeps its full height and the column holds a large gilt crescent set in
   AstroSymbols, so the composition is finished before a drawing arrives — and
   the drawing lands in exactly that box. */
export function Masthead({ greeting, line, portrait, portraitAlt = '', fit = 'cutout',
  live = false, children, height = 244, artSlot, col = 150 }) {
  return (
    <section className="plate scatter hem hem-strong" data-live={live || undefined} style={{
      position:'relative', minHeight:height, display:'block',
      borderRadius:'var(--radius-lg)', overflow:'hidden'
    }}>
      {live && <span aria-hidden="true" style={{ position:'absolute', inset:0, zIndex:0,
        background:'radial-gradient(140% 110% at 82% 100%,color-mix(in srgb,var(--live) 24%,transparent) 0%,transparent 60%)' }}/>}

      <div aria-hidden={artSlot || portrait ? undefined : 'true'} style={{ position:'absolute',
        right:0, bottom:0, top:0, width:col, zIndex:1, display:'grid', alignItems:'end',
        justifyItems:'center', padding: fit === 'plate' ? '0 12px 14px 0' : 0 }}>
        {artSlot ? artSlot
          : portrait
          ? (fit === 'plate'
            ? <img src={portrait} alt={portraitAlt} style={{ display:'block', width:'100%',
                aspectRatio:'1/1', objectFit:'cover', borderRadius:'var(--radius-md)',
                border:'1px solid color-mix(in srgb,var(--gilt) 42%,transparent)',
                boxShadow:'0 10px 26px rgba(0,0,0,.5)' }}/>
            : <img src={portrait} alt={portraitAlt} style={{ display:'block', width:'100%',
                height:'100%', objectFit:'cover', objectPosition:'bottom center',
                filter:'drop-shadow(0 8px 22px rgba(0,0,0,.5))' }}/>)
          : <span style={{ position:'absolute', right:-10, bottom:-22,
              font:'400 176px/1 var(--font-glyph)', color:'var(--gilt)', opacity:.3,
              textShadow:'0 0 40px color-mix(in srgb,var(--gilt) 30%,transparent)',
              pointerEvents:'none', userSelect:'none' }}>{'\u263E\uFE0E'}</span>}
      </div>

      <div style={{ position:'relative', zIndex:2, minHeight:height, display:'grid', gap:12,
        alignContent:'end', padding:'20px 16px 18px', paddingRight: col + 8,
        maxWidth:'100%', boxSizing:'border-box' }}>
        <div style={{ minWidth:0 }}>
          {live && <span className="t-eyebrow" style={{ color:'var(--live)', display:'block',
            marginBottom:7 }}>Live now</span>}
          <h1 style={{ margin:0, font:'500 var(--size-masthead)/var(--leading-display) var(--font-display)',
            color:'var(--ink)', letterSpacing:'var(--tracking-display)', overflowWrap:'break-word',
            textWrap:'balance', textShadow:'0 1px 14px rgba(11,15,26,.65)' }}>{greeting}</h1>
          {line && <p style={{ margin:'7px 0 0', font:'400 var(--size-label)/1.5 var(--font-body)',
            color:'var(--soft)', textWrap:'pretty',
            textShadow:'0 1px 10px rgba(11,15,26,.6)' }}>{line}</p>}
        </div>
        {children}
      </div>
    </section>
  );
}
