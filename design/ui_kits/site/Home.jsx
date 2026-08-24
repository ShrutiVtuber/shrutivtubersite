const {Hero,Button,SectionHeader,VideoCard,ProjectCard,ScheduleItem,LiveBadge,SocialLinkRow}=window.ShrutiDesignSystem_cb687f;
function HomeScreen({live,withArt,tz}){
  return <main className="site-main">
    <div className="page">
      <Hero greeting="Welcome · Καλώς ήρθατε · स्वागत"
        title="I build instruments for magick."
        subtitle="Software for astrology, theurgy and divination — built live on stream from Athens."
        art={withArt?window.ASSETS.avatar:null} artAlt="Shruti" clouds={withArt?window.ASSETS.clouds:null}
        actions={<>
          {live.status==='live'?<Button variant="live" size="lg" href="#videos">Watch live</Button>:<Button size="lg" href="#schedule">Next stream</Button>}
          <Button variant="secondary" size="lg" href="#work">See the work</Button>
        </>}
        footnote={<div style={{display:'flex',gap:16,alignItems:'center',flexWrap:'wrap'}}><LiveBadge status={live.status} title={live.title} game={live.game} viewers={live.viewers} nextStream="Thu 21:00 EEST" href="#videos"/><SocialLinkRow links={window.SOCIALS} size={16}/></div>}/>
    </div>
    <section className="section page">
      <div className="section-head">
        <SectionHeader glyph="▶" eyebrow="Latest" title="Recent streams" body="Auto-pulled from Twitch and YouTube."/>
        <Button variant="ghost" href="#videos">All videos →</Button>
      </div>
      <div className="grid-3">
        <VideoCard title="Building the sigil compiler — part 3" platform="twitch" duration="2:04:11" date="3 days ago" href="#videos"/>
        <VideoCard title="Planetary hours, computed properly" platform="youtube" duration="24:08" date="2 weeks ago" href="#videos"/>
        <VideoCard title="Theourgia devlog — the offerings ledger" platform="twitch" duration="1:41:09" date="3 weeks ago" href="#videos"/>
      </div>
    </section>
    <section className="section page">
      <div className="section-head">
        <SectionHeader glyph="☾" eyebrow="Next on the almanac" title="Upcoming stream"/>
        <Button variant="ghost" href="#schedule">Full schedule →</Button>
      </div>
      <ScheduleItem tz={tz} title="Theourgia dev — offerings ledger" topic="Software & Game Dev" durationMin={150} startISO="2026-08-27T21:00:00+03:00" href="#schedule"/>
    </section>
    <section className="section page">
      <div className="section-head">
        <SectionHeader glyph="✶" eyebrow="The work" title="A portfolio of instruments" body="The proof behind the brand: real software for real practice."/>
        <Button variant="ghost" href="#work">About the work →</Button>
      </div>
      <div className="grid-2">
        <ProjectCard name="Theourgia" tagline="A practitioner's toolkit that takes the calendar seriously." status="active" meta="open source · self-hosted · federation" liveHref="https://theourgia.com" screenshot={null}/>
        <ProjectCard name="BeeRanked" tagline="An SEO CMS that earns its keep." status="active" meta="commercial SaaS" liveHref="https://beeranked.online" screenshot={null}/>
      </div>
    </section>
    <section className="section page">
      <div className="section-head">
        <SectionHeader glyph="⁂" eyebrow="Journal" title="Recent writing"/>
        <Button variant="ghost" href="#journal">Read the journal →</Button>
      </div>
      <div>
        <a className="journal-row" href="#journal"><span className="jr-date">2026-08-12</span><span><h3 className="jr-title">On the hours of Hekate</h3><p className="jr-sub">Why a planetary hour is not sixty minutes, and what that means for scheduling rites.</p></span><span className="jr-side"><span className="seal" style={{fontSize:13}}>Soror Eu. A.</span></span></a>
        <a className="journal-row" href="#journal"><span className="jr-date">2026-07-30</span><span><h3 className="jr-title">Shipping the Attic calendar</h3><p className="jr-sub">Engineering notes on lunisolar months, intercalation, and tests that fail at dusk.</p></span><span className="jr-side"><span style={{font:'500 12px var(--font-body)',color:'var(--ink-faint)'}}>Shruti</span></span></a>
      </div>
    </section>
  </main>;
}
Object.assign(window,{HomeScreen});
