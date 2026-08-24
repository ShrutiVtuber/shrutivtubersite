const {SectionHeader,Button,Badge,EmptyState}=window.ShrutiDesignSystem_cb687f;
function SupportScreen(){
  const Tier=({name,price,note,items,badge,primary})=>
    <div style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:10,boxShadow:'var(--shadow-1)',padding:'22px 20px',display:'grid',gap:12,alignContent:'start'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:8}}>
        <h2 style={{font:'600 var(--text-h3, 20px) var(--font-display)',color:'var(--ink)',margin:0}}>{name}</h2>{badge}</div>
      <div style={{font:'500 26px var(--font-mono)',color:'var(--ink)',fontVariantNumeric:'tabular-nums'}}>{price}<span style={{font:'400 var(--text-sm) var(--font-body)',color:'var(--ink-soft)'}}> {note}</span></div>
      <ul style={{listStyle:'none',margin:0,padding:0,display:'grid',gap:6}}>
        {items.map(i=><li key={i} style={{font:'400 var(--text-sm)/1.5 var(--font-body)',color:'var(--ink-soft)'}}>{i}</li>)}
      </ul>
      <div><Button variant={primary?'primary':'secondary'} href="#">{primary?'Join on Ko-fi':'Open Ko-fi'}</Button></div>
    </div>;
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="♄" eyebrow="Support" title="Keep the bench lit" body="Streams are free and the tools are open source. Support pays for the ephemeris server, art commissions, and the hours the software takes."/>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(240px,1fr))',gap:20}}>
      <Tier name="One-off" price="€3" note="once, or any amount" items={['A coffee for the bench','Name read on stream if you leave one','No account needed']}/>
      <Tier name="Lamplighter" price="€4" note="/ month" badge={<Badge tone="rose">Most common</Badge>} primary items={['Members channel on Discord','Schedule a day early','Name in the monthly credits roll']}/>
      <Tier name="Almanac" price="€9" note="/ month" items={['Everything in Lamplighter','Monthly practice notes, signed Soror Eu. A.','A vote on the next instrument']}/>
    </div>
    <p style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:0}}>Memberships are Ko-fi-hosted; cancel any time. Tiers ship only if memberships open — this is the design for that day.</p>
    <SectionHeader as="h2" title="Merch"/>
    <EmptyState glyph="◐" title="No merch yet" body="Designs are commissioned before anything is printed — nothing exists that I wouldn't wear. Discord hears first when that changes."/>
  </main>;
}
Object.assign(window,{SupportScreen});