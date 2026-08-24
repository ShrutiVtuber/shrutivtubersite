const {SectionHeader,VideoCard,VideoCardSkeleton,Tag,Pagination,EmptyState}=window.ShrutiDesignSystem_cb687f;
function VideosScreen({loading}){
  const [filter,setFilter]=React.useState('all');
  const vids=[
    {title:'Building the sigil compiler — part 3',platform:'twitch',duration:'2:04:11',date:'3 days ago',kind:'dev'},
    {title:'Planetary hours, computed properly',platform:'youtube',duration:'24:08',date:'2 weeks ago',kind:'talk'},
    {title:'Theourgia devlog — the offerings ledger',platform:'twitch',duration:'1:41:09',date:'3 weeks ago',kind:'dev'},
    {title:'Attic calendar Q&A · ΕΛ/EN',platform:'twitch',duration:'1:12:44',date:'1 month ago',kind:'chat'},
    {title:'Six divination systems, one schema',platform:'youtube',duration:'31:02',date:'1 month ago',kind:'talk'},
    {title:'BeeRanked: structured content for rank tracking',platform:'youtube',duration:'18:26',date:'2 months ago',kind:'dev'}
  ].filter(v=>filter==='all'||v.kind===filter);
  return <main className="site-main page">
    <div className="section-head">
      <SectionHeader as="h1" glyph="▶" eyebrow="Videos" title="Streams & VODs" body="Auto-pulled from Twitch and YouTube."/>
      <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
        {[['all','All'],['dev','Dev streams'],['talk','Talks'],['chat','Chatting']].map(([k,l])=><Tag key={k} label={l} active={filter===k} onClick={()=>setFilter(k)}/>)}
      </div>
    </div>
    {loading
      ?<div className="grid-3"><VideoCardSkeleton/><VideoCardSkeleton/><VideoCardSkeleton/><VideoCardSkeleton/><VideoCardSkeleton/><VideoCardSkeleton/></div>
      :vids.length===0
        ?<EmptyState glyph="◐" title="Nothing here yet" body="No VODs match this filter — try another, or watch live on Thursdays."/>
        :<div className="grid-3">{vids.map((v,i)=><VideoCard key={i} {...v} href="#"/>)}</div>}
    <div style={{display:'flex',justifyContent:'center'}}><Pagination page={1} pageCount={4} onChange={()=>{}}/></div>
  </main>;
}
Object.assign(window,{VideosScreen});
