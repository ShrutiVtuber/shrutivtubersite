const {SectionHeader,ProfileFieldTable,CreditList,FanArtCard,Prose,Badge}=window.ShrutiDesignSystem_cb687f;
function AboutScreen(){
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☾" eyebrow="About" title="Shruti" body="VTuber · theurgist · toolmaker. Athens, GMT+3."/>
    <div style={{display:'grid',gridTemplateColumns:'1.4fr 1fr',gap:'var(--space-7)',alignItems:'start'}} className="about-cols">
      <Prose>
        <p>I stream the building of software for magickal and astrological practice — not a variety stream with an occult skin, but the actual work: ephemeris math, calendar systems, divination engines, and the unglamorous plumbing that makes a grimoire searchable.</p>
        <p>Three initiatory lineages, held at once: Hellenic theurgy under Hekate and the Attic lunisolar calendar; Śākta Tantra, initiated into the Mahāvidyā — tarpaṇam and mantra japa; and Thelema, under the O.T.O. They are not an aesthetic blend. They converge on one thing, and the software is built around it: the twilight junctures, <em lang="sa">sandhyā</em> — dawn and dusk.</p>
        <p lang="el">Μιλάω αγγλικά και ελληνικά στα streams· τα σχόλια στον κώδικα είναι δίγλωσσα κι αυτά.</p>
        <hr/>
        <h3>The two names</h3>
        <p><strong>Shruti</strong> — Shruti Swara — is my real name, and the name everything public lives under. I am part Indian and part Greek: the Sanskrit name and the Greek theurgy are not two themes in tension — they are one person. श्रुति, <em>“that which is heard”</em>.</p>
        <p><span className="seal">Soror Eu.&#8202;A.</span> is a magickal motto, and it signs the magickal work: journal entries about practice, and the software written as practice. Two instruments, the same hand — you will find it on bylines and nowhere else.</p>
      </Prose>
      <div style={{display:'grid',gap:'var(--space-6)'}}>
        <div>
          <h3 style={{font:'600 var(--text-micro) var(--font-body)',letterSpacing:'var(--tracking-eyebrow)',textTransform:'uppercase',color:'var(--ink-faint)',margin:'0 0 10px'}}>Profile</h3>
          <ProfileFieldTable columns={1} fields={[
            {label:'Birthday',value:'21 June'},{label:'Height',value:'163 cm'},
            {label:'Debut',value:'14 Jan 2024'},{label:'Fan name',value:'Shrutinauts'},
            {label:'Traditions',value:'Hellenic · Śākta · Thelemic'},
            {label:'Oshi mark',value:'— (to be chosen)'},{label:'Stream tag',value:'#ShrutiLive'},{label:'Fan-art tag',value:'#ShrutiArt'}]}/>
        </div>
        <div>
          <h3 style={{font:'600 var(--text-micro) var(--font-body)',letterSpacing:'var(--tracking-eyebrow)',textTransform:'uppercase',color:'var(--ink-faint)',margin:'0 0 4px'}}>Credits</h3>
          <CreditList dense credits={[
            {role:'Illustrator',name:'—',note:'commission in progress'},
            {role:'Rigger',name:'—',note:'commission in progress'},
            {role:'3D model',name:'—',note:'planned'},
            {role:'Logo',name:'Studio ——',href:'#'},
            {role:'BGM',name:'——',href:'#'}]}/>
        </div>
      </div>
    </div>
    <section className="section" style={{marginTop:'var(--space-7)'}}>
      <div className="section-head">
        <SectionHeader glyph="✶" eyebrow="Costumes" title="Outfits" body="Art arrives incrementally — empty slots are part of the design."/>
        <Badge tone="rose">3 commissions open</Badge>
      </div>
      <div className="grid-3">
        <FanArtCard image={null} artist="base model" platform="in progress"/>
        <FanArtCard image={null} artist="festival outfit" platform="planned"/>
        <FanArtCard image={null} artist="dev-stream hoodie" platform="planned"/>
      </div>
    </section>
  </main>;
}
Object.assign(window,{AboutScreen});
