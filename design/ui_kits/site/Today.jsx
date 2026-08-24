const {SectionHeader,NextStation,Button,Badge,TextField,EmptyState}=window.ShrutiDesignSystem_cb687f;

function Blk({title,note,children,span}){
  return <section style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:'var(--radius-md)',boxShadow:'var(--shadow-1)',padding:'var(--space-4) var(--space-4)',display:'grid',gap:10,alignContent:'start',gridColumn:span?'span 2':undefined}}>
    <div style={{display:'flex',alignItems:'baseline',gap:8,flexWrap:'wrap'}}>
      <h2 className="t-eyebrow" style={{margin:0}}>{title}</h2>
      {note&&<span className="t-tabular" style={{marginLeft:'auto',font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>{note}</span>}
    </div>
    {children}
  </section>;
}
function Row({k,v,sub}){
  return <div style={{display:'flex',alignItems:'baseline',gap:10}}>
    <span style={{font:'400 var(--text-sm) var(--font-body)',color:'var(--ink-soft)'}}>{k}</span>
    <span style={{flex:1,borderBottom:'1px dotted var(--line-strong)',transform:'translateY(-3px)',minWidth:12}}></span>
    <span className="t-tabular" style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink)'}}>{v}</span>
    {sub&&<span style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>{sub}</span>}
  </div>;
}

function TodayScreen({signedIn,birthTime,polar}){
  return <main className="site-main page">
    <div style={{display:'flex',alignItems:'flex-end',gap:'var(--space-4)',flexWrap:'wrap'}}>
      <SectionHeader as="h1" glyph="◐" eyebrow="Day at a glance" title="The sky, here, now"
        body={polar?'Longyearbyen · 78.22°N 15.63°E · Monday 7 September 2026':'Athens · 37.98°N 23.73°E · Monday 7 September 2026 · your local time'}/>
      <div style={{marginLeft:'auto',display:'flex',gap:8,alignItems:'flex-end'}} className="no-print">
        <TextField label="" defaultValue={polar?'Longyearbyen, SJ':'Athens, GR'}/>
        <Button variant="secondary">Use my location</Button>
      </div>
    </div>

    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(280px,1fr))',gap:'var(--space-4)'}}>
      <Blk title="Sun and Moon" note="right now">
        <div style={{display:'grid',gap:12}}>
          <div style={{display:'flex',alignItems:'baseline',gap:12}}>
            <span aria-hidden="true" className="t-glyph" style={{font:'400 1.75rem var(--font-display)',lineHeight:1,color:'var(--rose)'}}>☉</span>
            <div style={{display:'grid',gap:1}}>
              <span style={{font:'600 var(--text-h4) var(--font-display)',color:'var(--ink)'}}>Virgo 14°52′</span>
              <span style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>tropical · Leo 20°38′ sidereal</span>
            </div>
          </div>
          <div style={{display:'flex',alignItems:'baseline',gap:12}}>
            <span aria-hidden="true" className="t-glyph" style={{font:'400 1.75rem var(--font-display)',lineHeight:1,color:'var(--rose)'}}>☾</span>
            <div style={{display:'grid',gap:1}}>
              <span style={{font:'600 var(--text-h4) var(--font-display)',color:'var(--ink)'}}>Aries 02°17′</span>
              <span style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>moving 13°11′ a day · Pisces 08°03′ sidereal</span>
            </div>
          </div>
          <div style={{height:2,background:'var(--line)',borderRadius:2,overflow:'hidden'}} aria-hidden="true">
            <div style={{width:'18%',height:'100%',background:'var(--rose)'}}></div>
          </div>
          <span style={{font:'400 var(--text-xs)/1.5 var(--font-body)',color:'var(--ink-faint)'}}>The Moon crosses about half a degree an hour — this bar is its progress through Aries.</span>
        </div>
      </Blk>

      <Blk title="Stations">
        {polar
          ?<NextStation size="block" name="Sunrise" at="—" inLabel="—"
            undefinedReason="No sunrise here today, so the solar stations are undefined. The lunar stations still hold."/>
          :<NextStation size="block" glyph="☉︎" name="Sunset" at="20:05" inLabel="2h 14m" currentName="Noon" currentSince="13:29" progress={0.62}/>}
        <NextStation size="block" glyph="☾︎" name="Moonrise" at="17:41" inLabel="41m" currentName="Nadir" currentSince="10:48" progress={0.88}/>
        <div style={{display:'flex',gap:'8px 16px',flexWrap:'wrap',fontSize:'var(--text-sm)'}} className="no-print">
          <a href="#solar-stations" style={{color:'var(--accent)',textDecoration:'none'}}>Solar tracker</a>
          <a href="#lunar-stations" style={{color:'var(--accent)',textDecoration:'none'}}>Lunar tracker</a>
        </div>
      </Blk>

      <Blk title="Planetary hour" note={polar?'undefined here':'unequal · 66 min'}>
        {polar
          ?<p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>The hours divide sunrise to sunset. With no sunrise there is nothing to divide, so they are undefined today — not zero, and not clock hours pretending otherwise.</p>
          :<div style={{display:'grid',gap:12}}>
            <div style={{display:'flex',alignItems:'baseline',gap:12}}>
              <span aria-hidden="true" className="t-glyph" style={{font:'400 1.5rem var(--font-display)',lineHeight:1,color:'var(--rose)'}}>☿</span>
              <div style={{display:'grid',gap:1}}>
                <span style={{font:'600 var(--text-h4) var(--font-display)',color:'var(--ink)'}}>Hour of Mercury</span>
                <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>began 13:29 · ends 14:35</span>
              </div>
            </div>
            <div style={{borderTop:'1px solid var(--line)',paddingTop:10,display:'flex',alignItems:'baseline',gap:12}}>
              <span aria-hidden="true" className="t-glyph" style={{font:'400 1.25rem var(--font-display)',lineHeight:1,color:'var(--rose)'}}>☾</span>
              <div style={{display:'grid',gap:1}}>
                <span style={{font:'500 var(--text-body) var(--font-body)',color:'var(--ink)'}}>Next — hour of the Moon</span>
                <span className="t-tabular" style={{font:'400 var(--text-xs) var(--font-mono)',color:'var(--ink-faint)'}}>14:35 – 15:41 · in 36m</span>
              </div>
              <Badge tone="rose">plan against this</Badge>
            </div>
          </div>}
      </Blk>

      <Blk title="The sky over you" note="now">
        <div className="sky" style={{borderRadius:'var(--radius-sm)',padding:0,overflow:'hidden',border:'1px solid var(--line)'}}>
          <div style={{aspectRatio:'4/3',display:'grid',placeItems:'center',textAlign:'center',padding:'var(--space-4)'}}>
            <div className="sky-veil" style={{padding:'12px 16px',maxWidth:'30ch'}}>
              <p style={{margin:0,font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-soft)',letterSpacing:'.04em'}}>SKY CHART · rendered SVG<br/>visible chart for here and now</p>
            </div>
          </div>
        </div>
      </Blk>

      <Blk title="Transits" note={signedIn?(birthTime?'to your nativity':'partial'):'needs a nativity'}>
        {!signedIn
          ?<div style={{display:'grid',gap:10}}>
            <p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>Everything else on this page works without an account, and always will. This one block needs to know where you were born — nothing else does.</p>
            <div><Button variant="secondary" href="#signup">Save a nativity</Button></div>
            <span style={{font:'400 var(--text-xs)/1.6 var(--font-mono)',color:'var(--ink-faint)'}}>No account? The page above is the whole page. This is an invitation, not a wall.</span>
          </div>
          :<div style={{display:'grid',gap:8}}>
            <Row k="☉ to your Moon" v="square" sub="2°14′"/>
            <Row k="♄ to your Sun" v="trine" sub="0°41′"/>
            <Row k="☿ to your Mercury" v="conjunct" sub="1°02′"/>
            {birthTime
              ?<><Row k="☾ crossing your 7th" v="today" sub="17:41"/><Row k="♂ on your ascendant" v="in 3 days" sub="—"/></>
              :<div style={{borderTop:'1px solid var(--line)',paddingTop:10,display:'grid',gap:6}}>
                <span className="t-eyebrow" style={{margin:0,color:'var(--rose)'}}>◐ Angular transits undefined</span>
                <p style={{margin:0,font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)'}}>Your nativity has no birth time, so the ascendant, midheaven and houses are undefined — and transits to them with it. The planetary transits above stand; the angular ones are not guessed.</p>
                <div><Button variant="ghost" href="#nativity">Add a birth time</Button></div>
              </div>}
          </div>}
      </Blk>

      <Blk title="Today in every reckoning">
        <div style={{display:'grid',gap:6}}>
          <Row k="Gregorian" v="Mon 7 Sep 2026"/>
          <Row k="Attic" v="δωδεκάτη Μεταγειτνιῶνος" sub="12th"/>
          <Row k="Hindu · amānta" v="Bhādrapada kṛṣṇa 11" sub="Vikrama 2083"/>
          <Row k="Thelemic" v="Anno IVxxxiv ☉ in ♍" sub="dies Lunae"/>
        </div>
        <span style={{font:'400 var(--text-xs)/1.5 var(--font-body)',color:'var(--ink-faint)'}}>Each links to the instrument that reckons it, with the rule it used.</span>
      </Blk>
    </div>

    <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-4)',display:'flex',gap:'8px 22px',flexWrap:'wrap',fontSize:'var(--text-sm)'}} className="no-print">
      <a href="#solar-stations" style={{color:'var(--accent)',textDecoration:'none'}}>☉︎ Solar stations</a>
      <a href="#lunar-stations" style={{color:'var(--accent)',textDecoration:'none'}}>☾︎ Lunar stations</a>
      <a href="#horoscopes" style={{color:'var(--accent)',textDecoration:'none'}}>♍︎ Horoscopes</a>
      <a href="#work" style={{color:'var(--accent)',textDecoration:'none'}}>All instruments</a>
    </div>
  </main>;
}
Object.assign(window,{TodayScreen});