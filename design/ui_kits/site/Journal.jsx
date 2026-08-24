const {SectionHeader,Prose,Tag,Pagination,Breadcrumb,LanguageSwitcher,Badge}=window.ShrutiDesignSystem_cb687f;
const POSTS=[
  {date:'2026-08-12',title:'On the hours of Hekate',sub:'Why a planetary hour is not sixty minutes, and what that means for scheduling rites.',by:'soror',tags:['theurgy','astrology'],langs:['en','el']},
  {date:'2026-07-30',title:'Shipping the Attic calendar',sub:'Engineering notes on lunisolar months, intercalation, and tests that fail at dusk.',by:'shruti',tags:['engineering'],langs:['en']},
  {date:'2026-07-11',title:'Six divination systems, one schema',sub:'Designing a data model that respects the differences instead of flattening them.',by:'shruti',tags:['engineering','divination'],langs:['en','hi']},
  {date:'2026-06-24',title:'Offerings, recorded',sub:'A ledger is an act of attention. Notes on the offerings module.',by:'soror',tags:['theurgy'],langs:['en','el','fr']}
];
function JournalScreen({article,openArticle}){
  if(article)return <JournalArticle back={()=>openArticle(false)}/>;
  return <main className="site-main page">
    <div className="section-head">
      <SectionHeader as="h1" glyph="⁂" eyebrow="Journal" title="Field notes" body="Served from BeeRanked at /journal — engineering signed Shruti, magick signed Soror Eu. A."/>
      <div style={{display:'flex',gap:8,flexWrap:'wrap'}}><Tag label="all" active/><Tag label="theurgy" count={7}/><Tag label="astrology" count={5}/><Tag label="engineering" count={12}/><Tag label="divination" count={4}/></div>
    </div>
    <div>
      {POSTS.map((p,i)=><a key={i} className="journal-row" href="#journal" onClick={e=>{e.preventDefault();openArticle(true)}}>
        <span className="jr-date">{p.date}</span>
        <span><h3 className="jr-title">{p.title}</h3><p className="jr-sub">{p.sub}</p>
          <span style={{display:'flex',gap:6,marginTop:8,flexWrap:'wrap'}}>{p.tags.map(t=><Tag key={t} label={t}/>)}</span></span>
        <span className="jr-side">
          {p.by==='soror'?<span className="seal" style={{fontSize:13}}>Soror Eu.&#8202;A.</span>:<span style={{font:'500 12px var(--font-body)',color:'var(--ink-faint)'}}>Shruti</span>}
          <span style={{font:'400 10px var(--font-mono)',color:'var(--ink-faint)',letterSpacing:'.06em'}}>{p.langs.map(l=>l.toUpperCase()).join(' · ')}</span>
        </span>
      </a>)}
    </div>
    <div style={{display:'flex',justifyContent:'center'}}><Pagination page={1} pageCount={7} onChange={()=>{}}/></div>
  </main>;
}
function JournalArticle({back}){
  return <main className="site-main page" style={{maxWidth:820}}>
    <Breadcrumb items={[{label:'Journal',href:'#journal'},{label:'Theurgy',href:'#journal'},{label:'On the hours of Hekate'}]}/>
    <div className="section-head" style={{alignItems:'flex-start'}}>
      <div style={{display:'grid',gap:10}}>
        <h1 style={{font:'600 var(--text-h1)/1.15 var(--font-display)',color:'var(--ink)',margin:0,maxWidth:'22ch',textWrap:'balance'}}>On the hours of Hekate</h1>
        <div style={{display:'flex',gap:12,alignItems:'center',flexWrap:'wrap'}}>
          <span className="seal" style={{fontSize:14}}>Soror Eu.&#8202;A.</span>
          <span style={{font:'400 11px var(--font-mono)',color:'var(--ink-faint)'}}>2026-08-12 · 7 min</span>
          <Badge tone="rose">theurgy</Badge>
        </div>
      </div>
      <LanguageSwitcher current="en" hrefFor={l=>'#journal'} languages={['en','el']}/>
    </div>
    <Prose byline="Soror Eu. A.">
      <p>An hour here is not sixty minutes. Divide the arc of daylight by twelve, and each hour stretches in June and contracts in December — the almanac's kind of precision, where <code>sunrise(φ, date)</code> is the first input of the day.</p>
      <blockquote>The instrument does not believe anything. It computes the sky as it is, and leaves the meaning to the practitioner.</blockquote>
      <p>Theourgia treats this as a first-class primitive. Ask it for the ruler of the moment and it answers from the ephemeris, not from a lookup table of someone else's timezone.</p>
      <hr/>
      <p lang="el">Η ώρα του Ερμή δεν είναι ποτέ εκεί που τη περιμένεις τον χειμώνα — και αυτό είναι το νόημα.</p>
    </Prose>
    <div><a href="#journal" onClick={e=>{e.preventDefault();back()}}>← All field notes</a></div>
  </main>;
}
Object.assign(window,{JournalScreen});
