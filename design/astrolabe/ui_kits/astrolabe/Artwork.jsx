/* "Where your art goes" — every slot from guidelines/artwork-spec.md, at its
   real size, inside the real screen, with a drop target in it.
   Drag a PNG onto any slot and it stays there; the app themes around it live. */

function Slot({ id, w, h, shape = 'rounded', radius = 12, placeholder, src, style }) {
  /* The component fills its container, so size the WRAPPER, never the slot. */
  return <div style={{ position:'relative', width:w, height:h, flex:'none', ...style }}>
    <image-slot id={id} shape={shape} radius={radius} placeholder={placeholder || '\u00a0'}
      src={src} style={{ position:'absolute', inset:0 }}></image-slot>
  </div>;
}
/* The Masthead's portrait column, at its real size: 150 × 244 logical. */
function FillSlot({ id, placeholder }) {
  return <Slot id={id} w="150px" h="244px" shape="rect" placeholder={placeholder}/>;
}

function Spec({ n, name, need, rows, note }) {
  return (
    <div style={{ display:'grid', gap:10, minWidth:0 }}>
      <div style={{ display:'flex', alignItems:'baseline', gap:10, flexWrap:'wrap' }}>
        <span className="t-eyebrow" style={{ color:'var(--gilt)' }}>{n}</span>
        <h3 style={{ margin:0, font:'500 21px/1.25 var(--font-display)', color:'var(--ink)' }}>{name}</h3>
        <span style={{ font:'600 10px/1 var(--font-body)', letterSpacing:'.12em',
          textTransform:'uppercase', padding:'4px 8px', borderRadius:'var(--radius-full)',
          color: need === 'Essential' ? 'var(--gilt)' : 'var(--faint)',
          background: need === 'Essential' ? 'var(--gilt-wash)' : 'transparent',
          border:'1px solid ' + (need === 'Essential'
            ? 'color-mix(in srgb,var(--gilt) 38%,transparent)' : 'var(--line)') }}>{need}</span>
      </div>
      <div className="card" style={{ padding:'12px 14px' }}>
        {rows.map((r,i) => <DataRow key={i} label={r[0]} value={r[1]} small={r[2]}/>)}
      </div>
      {note && <p style={{ margin:0, font:'400 13px/1.6 var(--font-body)', color:'var(--faint)',
        maxWidth:'46ch', textWrap:'pretty' }}>{note}</p>}
    </div>
  );
}

/* A phone, for showing a slot in situ. */
function Mini({ children, h = 460, label, live, hour = 'venus', tab = 'home', chrome = true }) {
  return (
    <figure style={{ margin:0, display:'grid', gap:8, justifyItems:'center' }}>
      <div data-live={live?'true':undefined} data-hour={hour} style={{ width:360, height:h,
        display:'flex', flexDirection:'column', position:'relative', overflow:'hidden',
        background:'var(--page)', border:'1px solid var(--line-strong)', borderRadius:30,
        boxShadow:'0 18px 48px -18px rgba(0,0,0,.65)' }}>
        {chrome && <StatusBar live={live}/>}
        {children}
        {chrome && <TabBar active={tab} onChange={()=>{}}/>}
      </div>
      {label && <figcaption style={{ font:'400 12px/1.4 var(--font-body)', color:'var(--faint)' }}>{label}</figcaption>}
    </figure>
  );
}

function Section({ children }) {
  return <section style={{ display:'grid', gridTemplateColumns:'minmax(300px,380px) minmax(280px,1fr)',
    gap:32, alignItems:'start', padding:'30px 0', borderTop:'1px solid var(--line)' }}>{children}</section>;
}

function ArtworkDoc() {
  const A = window.AL;
  return (
    <div style={{ maxWidth:1080, margin:'0 auto', padding:'36px 28px 100px' }}>
      <header style={{ display:'grid', gap:12, maxWidth:'60ch' }}>
        <span className="t-eyebrow">Astrolabe · artwork</span>
        <h1 style={{ margin:0, font:'500 40px/1.1 var(--font-display)', color:'var(--ink)',
          letterSpacing:'-0.014em' }}>Where your art goes</h1>
        <p style={{ margin:0, font:'400 17px/1.65 var(--font-display)', color:'var(--soft)',
          textWrap:'pretty' }}>
          Every drawing the app asks for, at its real size, inside the real screen.
          <strong style={{ color:'var(--ink)', fontWeight:500 }}> Drag a PNG onto any dotted
          slot</strong> — it stays there, and the app themes around it immediately, so you can see
          how a piece sits before you finish it. Nothing here is required for the app to ship: every
          slot has a designed state without art, shown beside it.
        </p>
        <p style={{ margin:0, font:'400 13px/1.6 var(--font-body)', color:'var(--faint)' }}>
          Full written spec, including the AGPL licence question about your drawings:
          <code style={{ color:'var(--soft)' }}> guidelines/artwork-spec.md</code>
        </p>
        <div className="rule" style={{ maxWidth:420, marginTop:6 }}>{'\u263E\uFE0E'}</div>
      </header>

      {/* 3 — Home portrait, offline */}
      <Section>
        <Spec n="Essential · 3" name="Home portrait — offline" need="Essential"
          rows={[['Canvas','800 × 1200 px'],['Used at','150 × 244 logical (450 × 732 @3×)'],
            ['Transparency','Transparent PNG + layered source'],
            ['May be cropped','left 18%, bottom 12%'],
            ['Behind it','the plate: cloak navy → card, with the star scatter'],
            ['Seen','every open of the app', true]]}
          note="Three-quarter view, turned slightly away, looking down at something in her hands. Quiet, occupied, mid-thought — not addressing the viewer. She is doing her own work while you check the sky."/>
        <div style={{ display:'grid', gap:16 }}>
          <Mini h={430} label="Drop the transparent portrait here">
            <AppBar title="Astrolabe" hour/>
            <Body pad={16} gap={14}>
              <Masthead greeting="Good evening" line="A waxing gibbous moon, four days from full."
                artSlot={<FillSlot id="portrait-offline" placeholder="Portrait — offline"/>}/>
              <div style={{ display:'flex', gap:8, alignItems:'center' }}>
                <HourChip ruler="venus" ordinal={7} diurnal ends="14:12"/>
                <MoonDisc phase={0.38} size={22}/>
              </div>
              <ContentCard kind="reading" sign="Scorpio" signMark={A.S.scorpio} date="9 Sep"
                readingTime="2 min" excerpt="Mercury is still in the shadow."/>
            </Body>
          </Mini>
          <p className="t-caption" style={{ margin:0, textAlign:'center' }}>
            With no drawing at all, the same plate holds a gilt ☾ in that column — see the app kit.
          </p>
        </div>
      </Section>

      {/* 4 — Home portrait, live */}
      <Section>
        <Spec n="Essential · 4" name="Home portrait — live" need="Essential"
          rows={[['Canvas','800 × 1200 px, same crop rules as #3'],
            ['Transparency','Transparent PNG'],
            ['Behind it','the plate, warmed by a rose glow from the lower right'],
            ['Seen','every open during a stream', true]]}
          note="A second drawing, not a recolour. Facing out, mid-speech, hood back. Let the live rose #F07A8C appear somewhere small and real — a ribbon, the lining catching light — so the rose hem has something to answer."/>
        <Mini h={430} live label="Drop the live portrait here">
          <AppBar title="Astrolabe" hour/>
          <Body pad={16} gap={14}>
            <Masthead live greeting="She is live" line="Casting charts for the chat, since 20:04 Athens."
              artSlot={<FillSlot id="portrait-live" placeholder="Portrait — live"/>}/>
            <LiveBanner status="live" title="Casting charts for the chat" game="Just Chatting" viewers={412}/>
          </Body>
        </Mini>
      </Section>

      {/* 1 — App icon */}
      <Section>
        <Spec n="Essential · 1" name="App icon — adaptive" need="Essential"
          rows={[['Canvas','two layers, 432 × 432 (also 1024 flat for iOS)'],
            ['Safe zone','264 × 264 centred — the rest is cropped to a shape you cannot predict'],
            ['Foreground','transparent'],['Background','fully opaque, edge to edge'],
            ['Seen','several times a day, for a fifth of a second', true]]}
          note="One mark, not a scene. The crescent-and-star clasp at the throat of your cloak reads at 48 px; a face does not. Background: flat #2B3450 with five or six stars, none crossing into the safe zone."/>
        <div style={{ display:'grid', gap:18, justifyItems:'start' }}>
          <div style={{ display:'flex', gap:22, alignItems:'flex-end', flexWrap:'wrap' }}>
            {[['icon-108',108,'108 px'],['icon-72',72,'72 px'],['icon-48',48,'48 px']].map(([id,px,lab]) =>
              <div key={id} style={{ display:'grid', gap:8, justifyItems:'center' }}>
                <Slot id={id} w={px+'px'} h={px+'px'} shape="rounded" radius={Math.round(px*0.23)}
                  placeholder={px >= 72 ? 'Icon' : '\u00a0'}/>
                <span className="t-caption">{lab}</span>
              </div>)}
          </div>
          <div style={{ display:'grid', gap:10, width:'100%' }}>
            <span className="t-eyebrow">The two layers, at 216 with the safe zone drawn</span>
            <div style={{ display:'flex', gap:18, flexWrap:'wrap' }}>
              {[['icon-bg','Background — opaque'],['icon-fg','Foreground — transparent']].map(([id,lab]) =>
                <div key={id} style={{ display:'grid', gap:8, justifyItems:'center' }}>
                  <div style={{ position:'relative', width:216, height:216 }}>
                    <Slot id={id} w="216px" h="216px" shape="rect" placeholder={lab}/>
                    <span aria-hidden="true" style={{ position:'absolute', inset:'20.8%',
                      border:'1px dashed color-mix(in srgb,var(--gilt) 65%,transparent)',
                      borderRadius:6, pointerEvents:'none' }}/>
                    <span aria-hidden="true" style={{ position:'absolute', inset:0, borderRadius:'50%',
                      border:'1px solid color-mix(in srgb,var(--accent) 40%,transparent)',
                      pointerEvents:'none' }}/>
                  </div>
                  <span className="t-caption">{lab}</span>
                </div>)}
            </div>
            <p className="t-caption" style={{ margin:0 }}>
              Gold dashed = the 264 safe zone. Blue circle = one of the shapes a launcher may crop to.
            </p>
          </div>
        </div>
      </Section>

      {/* 2 — Notification icon */}
      <Section>
        <Spec n="Essential · 2" name="Notification icon" need="Essential"
          rows={[['Canvas','96 × 96 (24 dp @4×); also 72 / 48 / 36 / 24'],
            ['Transparency','⚠ transparent, and pure white at varying alpha ONLY'],
            ['Behind it','the system status bar, any wallpaper'],
            ['Seen','every time you go live', true]]}
          note="⚠ Android throws away every colour in this file and renders the alpha channel as a flat silhouette. A gold icon arrives as a white blob. Draw the clasp as a solid silhouette with no interior detail — at 24 dp the inner line becomes mud."/>
        <div style={{ display:'grid', gap:14, justifyItems:'start' }}>
          <div style={{ display:'flex', alignItems:'center', gap:14, padding:'10px 16px',
            background:'var(--inset)', border:'1px solid var(--line)',
            borderRadius:'var(--radius-md)', width:360, boxSizing:'border-box' }}>
            <span className="t-tabular" style={{ font:'600 12px/1 var(--font-body)', color:'var(--soft)' }}>20:41</span>
            <span style={{ flex:1 }}/>
            <Slot id="icon-notification" w="18px" h="18px" shape="rect" placeholder=""/>
            <Icon name="wifi" size={14} tone="soft"/>
            <Icon name="battery_5_bar" size={14} tone="soft"/>
          </div>
          <div style={{ display:'flex', gap:16, alignItems:'flex-end' }}>
            {[['notif-96',96],['notif-48',48],['notif-24',24]].map(([id,px]) =>
              <div key={id} style={{ display:'grid', gap:6, justifyItems:'center' }}>
                <Slot id={id} w={px+'px'} h={px+'px'} shape="rect" placeholder=""/>
                <span className="t-caption">{px}</span>
              </div>)}
          </div>
        </div>
      </Section>

      {/* 5 — Splash */}
      <Section>
        <Spec n="Essential · 5" name="Splash / launch mark" need="Essential"
          rows={[['Canvas','1152 × 1152 (288 dp); visible circle 768 × 768'],
            ['Safe zone','the centre 768 circle — everything outside is masked'],
            ['Transparency','transparent; the background is #121829 from the theme'],
            ['Seen','every cold start, for under a second', true]]}
          note="No text, no wordmark, no character — anything with detail in it flickers. Draw the crescent and the star on separate layers if you want the star to fade in 200 ms behind it."/>
        <Mini h={430} chrome={false} label="Cold start">
          <div style={{ flex:1, display:'grid', placeItems:'center', background:'var(--page)' }}>
            <div style={{ position:'relative', width:192, height:192 }}>
              <Slot id="splash-mark" w="192px" h="192px" shape="circle" placeholder="Splash mark"/>
              <span aria-hidden="true" style={{ position:'absolute', inset:0, borderRadius:'50%',
                border:'1px dashed color-mix(in srgb,var(--gilt) 55%,transparent)',
                pointerEvents:'none' }}/>
            </div>
          </div>
        </Mini>
      </Section>

      {/* 6 — Wordmark */}
      <Section>
        <Spec n="Essential · 6" name="Wordmark, re-cut for the night" need="Essential"
          rows={[['Format','SVG, plus PNG at 1500 × 540'],['Transparency','transparent'],
            ['Behind it','#121829 and #1A2138'],
            ['Seen','Settings, licences, the store listing', true]]}
          note="⚠ A re-cut of your existing wordmark, not a new logo. The current one is the WordPress-era pink and blue: on #121829 the pale pink vibrates and the outline disappears. Same letterforms, same Devanagari, re-coloured for night — ink with gilt accents, or a single gilt cut."/>
        <div style={{ display:'grid', gap:14, width:'100%' }}>
          <div className="card" style={{ padding:20, display:'grid', gap:6, justifyItems:'center' }}>
            <Slot id="wordmark-night" w="280px" h="100px" shape="rect" placeholder="Wordmark — night cut"/>
          </div>
          <div className="card-inset" style={{ padding:20, display:'grid', gap:10, justifyItems:'center' }}>
            <img src="../../assets/wordmark-small.png" alt="The existing wordmark" style={{ height:64 }}/>
            <span className="t-caption" style={{ color:'var(--rose)' }}>
              What exists today — off-palette on this page. Never redrawn here.</span>
          </div>
        </div>
      </Section>

      {/* 7–9 empty states */}
      <Section>
        <Spec n="Nice to have · 7–9" name="Empty-state drawings" need="Nice to have"
          rows={[['Canvas','512 × 512 each'],['Transparency','transparent'],
            ['Sits above','two lines of authored text and a button'],
            ['Behind it','#121829'],['Seen','often for a new user, rarely for an old one', true]]}
          note="⚠ The offline one is the hard brief and the important one: it is not an error drawing. The instruments all still work — what is missing is you. The cloak on a peg; a lit window seen from outside. An absence with a promise in it. Nothing red, no exclamation mark."/>
        <div style={{ display:'flex', gap:20, flexWrap:'wrap' }}>
          {[['empty-practice','The room is quiet','Nobody has posted a reading this week. Yours would be the first.','Practice, empty'],
            ['empty-offline','Her half is out of reach','The instruments all still work — they compute on your phone.','Offline'],
            ['empty-unwritten','Nothing written yet','A reading here is a few hundred words on one chart. It does not have to be right.','Mine, empty']
          ].map(([id,title,body,lab]) =>
            <figure key={id} style={{ margin:0, display:'grid', gap:8, justifyItems:'center' }}>
              <div style={{ width:280, background:'var(--page)', border:'1px solid var(--line)',
                borderRadius:'var(--radius-md)', padding:'8px 0' }}>
                <EmptyState compact art={undefined} title={title} body={body}
                  action={<Button size="sm" variant="outlined">An action</Button>}/>
              </div>
              <Slot id={id} w="148px" h="148px" shape="rounded" radius={14} placeholder="Drop the drawing"/>
              <figcaption className="t-caption">{lab}</figcaption>
            </figure>)}
        </div>
      </Section>

      {/* 10 — motifs */}
      <Section>
        <Spec n="Nice to have · 10" name="Motifs and dividers" need="Nice to have"
          rows={[['Format','SVG, single colour — the app tints them'],
            ['Grids','24 × 24 (crescent, star), 120 × 24 (divider), 72 × 24 (phase strip)'],
            ['Seen','section rules and empty states, constantly, small', true]]}
          note="Drawn on a pixel grid rather than scaled down from something larger — these are the pieces that break when they are shrunk. Today the app uses ☾ and ✦ from the bundled glyph font, which is why the rules already look intentional."/>
        <div style={{ display:'grid', gap:18, width:'100%' }}>
          <div className="card" style={{ padding:'18px 20px', display:'grid', gap:16 }}>
            <div className="rule">{'\u263E\uFE0E'}</div>
            <span className="t-caption" style={{ textAlign:'center' }}>The rule today, set in AstroSymbols</span>
          </div>
          <div style={{ display:'flex', gap:16, flexWrap:'wrap', alignItems:'center' }}>
            <div style={{ display:'grid', gap:6, justifyItems:'center' }}>
              <Slot id="motif-crescent" w="72px" h="72px" shape="rect" placeholder="☾"/>
              <span className="t-caption">crescent 24</span>
            </div>
            <div style={{ display:'grid', gap:6, justifyItems:'center' }}>
              <Slot id="motif-star" w="72px" h="72px" shape="rect" placeholder="✦"/>
              <span className="t-caption">star 24</span>
            </div>
            <div style={{ display:'grid', gap:6, justifyItems:'center' }}>
              <Slot id="motif-divider" w="240px" h="48px" shape="rect" placeholder="divider 120 × 24"/>
              <span className="t-caption">divider</span>
            </div>
            <div style={{ display:'grid', gap:6, justifyItems:'center' }}>
              <Slot id="motif-phases" w="144px" h="48px" shape="rect" placeholder="phase strip"/>
              <span className="t-caption">phase strip 72 × 24</span>
            </div>
          </div>
        </div>
      </Section>

      {/* 11 — live band */}
      <Section>
        <Spec n="Nice to have · 11" name="Live-state ornament" need="Nice to have"
          rows={[['Canvas','1200 × 200'],['Transparency','transparent'],
            ['Behind it','the live plate, behind the greeting'],
            ['Seen','during every stream', true]]}
          note="A thin band of the cloak's star scatter with the gold trim running through it, fading out at both ends. This is what makes live feel like an event rather than a colour change. If it competes with the rose hem, thin it."/>
        <div style={{ display:'grid', gap:10, width:360 }}>
          <div data-live="true" className="plate hem hem-strong" style={{ position:'relative',
            height:150, display:'grid', alignContent:'end', padding:'0 16px 16px', overflow:'hidden' }}>
            <div style={{ position:'absolute', inset:'0 0 auto 0', height:70 }}>
              <Slot id="live-band" w="100%" h="70px" shape="rect" placeholder="Live band — 1200 × 200"/>
            </div>
            <span className="t-eyebrow" style={{ color:'var(--live)', position:'relative' }}>Live now</span>
            <span style={{ font:'500 30px/1.1 var(--font-display)', color:'var(--ink)',
              position:'relative', marginTop:6 }}>She is live</span>
          </div>
          <span className="t-caption" style={{ textAlign:'center' }}>Live plate, band across the top</span>
        </div>
      </Section>

      <section style={{ padding:'30px 0 0', borderTop:'1px solid var(--line)', display:'grid',
        gap:12, maxWidth:'62ch' }}>
        <h2 style={{ margin:0, font:'600 22px/1.25 var(--font-display)', color:'var(--rose)' }}>
          ⚠ The licence question, before anything is committed</h2>
        <p style={{ margin:0, font:'400 15px/1.7 var(--font-body)', color:'var(--soft)', textWrap:'pretty' }}>
          Astrolabe is AGPL-3.0 and everything in the repository is published under it. That is fine
          for code and OFL fonts. It is <strong style={{ color:'var(--ink)' }}>not automatically
          fine for your drawings</strong> — under the AGPL anybody may fork the app, keep your face
          on it, and ship it. The three options, and what each costs you, are set out at the foot of
          <code style={{ color:'var(--ink)' }}> guidelines/artwork-spec.md</code>. The design system
          assumes a dual licence (code AGPL, artwork yours) until you say otherwise.
        </p>
      </section>
    </div>
  );
}
Object.assign(window, { ArtworkDoc, Slot, FillSlot, Spec, Mini });
