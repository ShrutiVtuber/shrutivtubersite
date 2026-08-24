const {SectionHeader,ProjectCard,ProfileFieldTable,EmptyState,Button,Tag}=window.ShrutiDesignSystem_cb687f;
function WorkScreen(){
  const Entry=({card,credits,contributors})=>
    <div style={{display:'grid',gap:'var(--space-5)',alignContent:'start'}}>
      {card}
      <div>
        <h3 style={{font:'600 var(--text-micro) var(--font-body)',letterSpacing:'var(--tracking-eyebrow)',textTransform:'uppercase',color:'var(--ink-faint)',margin:'0 0 10px'}}>Credits</h3>
        <ProfileFieldTable columns={1} fields={credits}/>
        {contributors&&<p style={{font:'400 var(--text-xs)/1.6 var(--font-mono)',color:'var(--ink-faint)',margin:'10px 0 0'}}>{contributors}</p>}
      </div>
    </div>;
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="✶" eyebrow="The work" title="A portfolio of instruments"
      body="Not an app-store listing. Each of these is a working tool, shipped and maintained — most of it built live on stream. Every entry carries its role, stack, licence and status, because that is what another engineer wants to know."/>
    <div className="grid-2">
      <Entry
        card={<ProjectCard name="Theourgia" tagline="A practitioner's toolkit that takes the calendar seriously."
          description="Open-source magickal journal CMS: Attic lunar calendar, Swiss Ephemeris astrology, planetary hours, six divination systems, sigil generation, gematria, an offerings ledger, and federation. Authored under Soror Eu. A."
          status="active" meta="AGPL-3.0 · self-hosted · federation" liveHref="https://theourgia.com" repoHref="#" screenshot={null}/>}
        credits={[
          {label:'Name',value:'Theourgia'},
          {label:'Role',value:'Author · maintainer'},
          {label:'Stack',value:'Astro · TypeScript · Postgres · Swiss Ephemeris'},
          {label:'Licence',value:'AGPL-3.0'},
          {label:'Status',value:'Active'}]}
        contributors="Ephemeris data © Astrodienst · translations by the Discord"/>
      <Entry
        card={<ProjectCard name="BeeRanked" tagline="An SEO CMS that earns its keep."
          description="Commercial SEO CMS SaaS — structured content, rank tracking, and the platform this site's journal is served from."
          status="active" meta="Proprietary · commercial SaaS · hosts /journal" liveHref="https://beeranked.online" screenshot={null}/>}
        credits={[
          {label:'Name',value:'BeeRanked'},
          {label:'Role',value:'Founder · lead developer'},
          {label:'Stack',value:'Next.js · Postgres · Redis · Cloudflare'},
          {label:'Licence',value:'Proprietary'},
          {label:'Status',value:'Active · commercial'}]}/>
    </div>
    <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
      <Tag label="ephemeris"/><Tag label="lunisolar calendars"/><Tag label="divination"/><Tag label="sigils"/><Tag label="gematria"/><Tag label="federation"/><Tag label="astro.js"/>
    </div>
    <SectionHeader as="h2" glyph="☿" title="Instruments you can run here" body="Six of Theourgia's tools run in the browser on their own pages — the software demonstrating itself, no install."/>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(180px,1fr))',gap:12}}>
      {[['☉','Planetary hours','The day divided by its own light.'],['☽','Attic calendar','The lunisolar month, kept current.'],['◐','Pañcāṅga','The five limbs of the day.'],['Σ','Isopsephy','Greek letter-reckoning.'],['✶','Natal chart','A figure for a moment and a place.'],['●','Sigil generator','Intent, reduced and drawn.']].map(([g,n,d])=>
        <a key={n} href="#" style={{display:'block',background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:10,boxShadow:'var(--shadow-1)',padding:16,textDecoration:'none'}}>
          <span aria-hidden="true" style={{font:'400 1.25rem var(--font-display)',color:'var(--rose)'}}>{g}</span>
          <span style={{display:'block',marginTop:8,font:'600 var(--text-h4) var(--font-display)',color:'var(--ink)'}}>{n}</span>
          <span style={{display:'block',marginTop:4,font:'400 var(--text-xs)/1.5 var(--font-body)',color:'var(--ink-soft)'}}>{d}</span>
        </a>)}
    </div>
    <EmptyState glyph="◐" title="What follows"
      body="The next instrument is chosen on stream. Suggestions land in the Discord's #workbench channel."
      action={<Button variant="secondary">Join the Discord</Button>}/>
  </main>;
}
Object.assign(window,{WorkScreen});