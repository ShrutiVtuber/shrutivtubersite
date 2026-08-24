const {SectionHeader,StatBlock,AssetDownloadCard,EmptyState,Button}=window.ShrutiDesignSystem_cb687f;
function PressScreen(){
  const A=window.ASSETS;
  const Sw=({name,hex})=><div style={{display:'flex',alignItems:'center',gap:10,padding:'8px 0',borderBottom:'1px solid var(--line)'}}><span style={{width:18,height:18,borderRadius:4,background:hex,border:'1px solid var(--line)',flexShrink:0}}></span><span style={{font:'400 var(--text-sm) var(--font-body)',color:'var(--ink)',flex:1}}>{name}</span><code style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)'}}>{hex}</code></div>;
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☿" eyebrow="Press &amp; media kit" title="Working with Shruti" body="Numbers, brand rules and ready-to-use assets for sponsors, event organisers and press. Business enquiries get a reply within two working days."/>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))',gap:16}}>
      <StatBlock value="12.4k" label="Followers" note="all platforms" glyph="☾"/>
      <StatBlock value="214" label="Avg concurrent" note="past 90 days"/>
      <StatBlock value="38%" label="Returning viewers" note="past 90 days"/>
      <StatBlock value="EN·EL·HI" label="Stream languages"/>
    </div>
    <p style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:0}}>Sample figures — live numbers come from the platform APIs on request.</p>
    <SectionHeader as="h2" title="Brand safety" body="Streams are software and practice: no gambling segments, no sponsored financial or health claims, no undisclosed promotion. Occult subject matter is scholarly and practice-based — sponsors uncomfortable with that context should pass, and I'd rather they did. Every sponsorship is disclosed on stream and in the VOD description."/>
    <SectionHeader as="h2" title="Past collaborations"/>
    <EmptyState glyph="○" title="The first collaboration slot is open" body="Placements here list the partner, format and date — a record, not a wall of logos."/>
    <SectionHeader as="h2" title="Assets" body="Transparent PNGs, current as of this kit. Keep clear space around the wordmark equal to the height of its 'S'; never recolour, stretch, or set it over busy art."/>
    <div className="grid-2">
      <AssetDownloadCard name="Wordmark — full" meta="PNG · 2778×1000 · transparent" preview={<img src={A.wordmarkHiRes} alt="Shruti wordmark"/>} previewOn="checker" href={A.wordmarkHiRes} filename="shruti-wordmark.png"/>
      <AssetDownloadCard name="Wordmark — small" meta="PNG · 500×180 · transparent" preview={<img src={A.wordmark} alt="Shruti wordmark, small"/>} previewOn="checker" href={A.wordmark} filename="shruti-wordmark-small.png"/>
      <AssetDownloadCard name="Avatar" meta="PNG · 512×512" preview={<img src={A.avatar} alt="Shruti avatar"/>} previewOn="ink" href={A.avatar} filename="shruti-avatar.png"/>
      <AssetDownloadCard name="Clouds motif" meta="PNG · 2026×2837 · twilight sky" preview={<img src={A.clouds} alt="Clouds motif"/>} previewOn="sky" href={A.clouds} filename="shruti-clouds.png"/>
    </div>
    <SectionHeader as="h2" title="Colour" body="One sky, two hours — dawn is the light theme, dusk the dark. Same palette, different hour."/>
    <div className="grid-2">
      <div><h3 style={{font:'600 var(--text-sm) var(--font-ui, var(--font-body))',textTransform:'uppercase',letterSpacing:'.14em',color:'var(--ink-soft)',margin:'0 0 4px'}}>Dawn</h3>
        <Sw name="Paper" hex="#F8F6F3"/><Sw name="Ink" hex="#26304A"/><Sw name="Accent blue" hex="#33639C"/><Sw name="Rose" hex="#A85A76"/><Sw name="Live red" hex="#A62639"/></div>
      <div><h3 style={{font:'600 var(--text-sm) var(--font-ui, var(--font-body))',textTransform:'uppercase',letterSpacing:'.14em',color:'var(--ink-soft)',margin:'0 0 4px'}}>Dusk</h3>
        <Sw name="Page" hex="#121829"/><Sw name="Ink" hex="#E9E6F0"/><Sw name="Accent" hex="#8FBEE8"/><Sw name="Rose" hex="#E0A4BC"/><Sw name="Live" hex="#F07A8C"/></div>
    </div>
    <div style={{display:'flex',gap:10,flexWrap:'wrap',alignItems:'center'}}>
      <Button href="#contact">Start a business enquiry</Button>
      <span style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)'}}>business@shrutivtuber.com</span>
    </div>
  </main>;
}
Object.assign(window,{PressScreen});