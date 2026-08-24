const {SectionHeader,Prose,Button}=window.ShrutiDesignSystem_cb687f;
const LEGAL={
  privacy:{title:'Privacy',intro:'What this site knows about you — deliberately little.',secs:[
    {id:'collection',h:'What this site collects',p:['This site sets no analytics cookies and runs no trackers. The server keeps standard access logs (IP address, user agent) for 14 days, for abuse prevention only, then deletes them.']},
    {id:'embeds',h:'Embeds & third parties',p:['Stream embeds and VOD thumbnails load from Twitch and YouTube, which see your requests under their own policies. The schedule\u2019s timezone conversion happens entirely in your browser \u2014 your timezone never leaves it.']},
    {id:'contact',h:'Mail & submissions',p:['Mail sent to the contact routes is kept as ordinary correspondence and is never added to a list. Fan-works submissions keep exactly the credit you asked for, and are removed on request.']},
    {id:'rights',h:'Your rights',p:['Under the GDPR you can ask what is held about you (usually: your own emails) and have it corrected or deleted \u2014 write to hello@shrutivtuber.com.']},
    {id:'controller',h:'Controller',p:['[Entity name] \u00b7 [virtual office address] \u00b7 Athens, Greece \u00b7 GEMI [no.] \u00b7 VAT [no.] \u2014 the controller for this site. The full imprint is in the footer.']}]},
  terms:{title:'Terms',intro:'Short, in plain language, and mostly common sense.',secs:[
    {id:'content',h:'Content & licence',p:['Site text and original art are \u00a9 ShrutiVTuber, LLC. Theourgia is open source under its own licence \u2014 the repository speaks for itself. Quoting with attribution is welcome.']},
    {id:'fanworks',h:'Derivative works',p:['Fan works follow the derivative work guidelines, which are part of these terms. Where the two disagree, the guidelines win \u2014 they are the more generous document.']},
    {id:'asis',h:'No warranty',p:['The site, streams and software are offered as-is. Astrological and magickal content is practice and commentary, not professional, medical, legal or financial advice.']},
    {id:'law',h:'Governing law',p:['These terms are governed by Greek law; disputes go to the courts of Athens. If one clause fails, the rest stands.']}]}
};
function LegalScreen({doc}){
  const d=LEGAL[doc]||LEGAL.privacy;
  const go=id=>e=>{e.preventDefault();const el=document.getElementById(id);if(el)window.scrollTo({top:el.getBoundingClientRect().top+window.scrollY-84,behavior:'smooth'})};
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="♄" eyebrow="Legal" title={d.title} body={d.intro}/>
    <div style={{display:'flex',gap:8}}>
      <Button variant={doc==='privacy'?'secondary':'ghost'} href="#privacy">Privacy</Button>
      <Button variant={doc==='terms'?'secondary':'ghost'} href="#terms">Terms</Button>
    </div>
    <nav aria-label="On this page" style={{display:'flex',flexWrap:'wrap',gap:16,paddingBottom:14,borderBottom:'1px solid var(--line)'}}>
      {d.secs.map(s=><a key={s.id} href={'#'+doc} onClick={go('leg-'+s.id)} style={{font:'500 var(--text-sm) var(--font-mono)',color:'var(--accent)',textDecoration:'none'}}>{s.h}</a>)}
    </nav>
    <Prose>
      {d.secs.map(s=><React.Fragment key={s.id}><h2 id={'leg-'+s.id}>{s.h}</h2>{s.p.map((t,i)=><p key={i}>{t}</p>)}</React.Fragment>)}
    </Prose>
    <p style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:0}}>Last updated 2026-08 · earlier versions on request.</p>
  </main>;
}
Object.assign(window,{LegalScreen});