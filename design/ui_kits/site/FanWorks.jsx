const {SectionHeader,FanArtCard,Modal,Button,EmptyState,Pagination}=window.ShrutiDesignSystem_cb687f;
function FanWorksScreen(){
  const [open,setOpen]=React.useState(null);
  const [page,setPage]=React.useState(1);
  const works=[
    {title:'Dusk study',artist:'@aster_ink',platform:'X'},
    {title:'Planetary hours, annotated',artist:'@heliakos',platform:'Pixiv'},
    {title:'Shruti at the bench',artist:'@moth.tarpana',platform:'Bluesky'},
    {title:'Sigil compiler fan animation',artist:'@vhs_seance',platform:'YouTube'},
    {title:'Chibi — moonrise',artist:'@paperikon',platform:'X'},
    {title:'Wordmark embroidery',artist:'@stitchfane',platform:'Instagram'}
  ];
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="✶" eyebrow="Fan works" title="Made by you" body="Curated fan art and derivative work, credited loudly and linked back. Everything here appears with the artist's permission — the tiles fill in as pieces arrive."/>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(240px,1fr))',gap:20}}>
      {works.map(w=><FanArtCard key={w.title} image={null} title={w.title} artist={w.artist} artistHref="#" platform={w.platform} onOpen={()=>setOpen(w)}/>)}
    </div>
    <Pagination page={page} pageCount={3} onChange={setPage}/>
    <EmptyState glyph="◐" title="Made something?" body="Tag it #ShrutiArts so it can be found, or send it through the contact form with the credit you want shown. Read the derivative work guidelines first — they're short."
      action={<div style={{display:'flex',gap:10}}><Button href="#contact">Submit a piece</Button><Button variant="secondary" href="#guidelines">Read the guidelines</Button></div>}/>
    <Modal open={!!open} onClose={()=>setOpen(null)} variant="lightbox" title={open?`${open.title} — ${open.artist}`:undefined}>
      <div style={{display:'grid',placeItems:'center',minHeight:320,background:'var(--surface-card)',borderRadius:12}}>
        <span aria-hidden="true" style={{font:'500 44px var(--font-display)',color:'var(--ink-soft)'}}>✶</span>
      </div>
      <p style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:'10px 0 0'}}>Art slot — the piece opens here at full size. Credit: {open&&open.artist} · {open&&open.platform}</p>
    </Modal>
  </main>;
}
Object.assign(window,{FanWorksScreen});