const DS=window.ShrutiDesignSystem_cb687f;
const {LiveBadge,LanguageSwitcher,SocialLinkRow,Button,LegalImprint}=DS;
const ASSETS={
  wordmark:'../../assets/wordmark-small.png',
  wordmarkHiRes:'../../assets/wordmark.png',
  clouds:'../../assets/clouds.png',
  avatar:'../../assets/avatar.png'
};
const SOCIALS=[{platform:'twitch',href:'#'},{platform:'youtube',href:'#'},{platform:'discord',href:'#'},{platform:'x',href:'#'},{platform:'github',href:'#'},{platform:'linkedin',href:'#'}];
const NAV=[['home','Home'],['today','Today'],['about','About'],['work','Work'],['schedule','Schedule'],['videos','Videos'],['horoscopes','Horoscopes'],['journal','Journal']];

function BrandMark({withArt}){
  const [err,setErr]=React.useState(false);
  return <a className="brand" href="#home" aria-label="Shruti — home">
    {withArt&&!err?<img src={ASSETS.wordmark} alt="Shruti" onError={()=>setErr(true)}/>:<span className="brand-word">Shruti</span>}
  </a>;
}
function SiteHeader({route,live,withArt,signedIn}){
  const [scrolled,setScrolled]=React.useState(false);
  const [menu,setMenu]=React.useState(false);
  React.useEffect(()=>{const on=()=>setScrolled(window.scrollY>8);on();window.addEventListener('scroll',on,{passive:true});return ()=>window.removeEventListener('scroll',on)},[]);
  React.useEffect(()=>{setMenu(false)},[route]);
  return <header className="site-header" data-scrolled={scrolled}>
    <div className="page"><div className="bar">
      <BrandMark withArt={withArt}/>
      <nav className="site-nav" aria-label="Primary">
        {NAV.map(([r,l])=><a key={r} href={'#'+r} aria-current={route===r?'page':undefined}>{l}</a>)}
      </nav>
      <div className="header-side">
        <LiveBadge compact status={live.status} href="#videos"/>
        <LanguageSwitcher current="en" onChange={()=>{}}/>
        <a className="acct-link" href={signedIn?'#account':'#signin'}>{signedIn?'Account':'Sign in'}</a>
        <button type="button" className="nav-toggle" aria-expanded={menu} aria-controls="site-menu" onClick={()=>setMenu(m=>!m)}>
          <span aria-hidden="true">{menu?'×':'≡'}</span> Menu
        </button>
      </div>
    </div>
    {menu&&<nav id="site-menu" className="site-menu" aria-label="Primary, mobile">
      {NAV.map(([r,l])=><a key={r} href={'#'+r} aria-current={route===r?'page':undefined}>{l}</a>)}
      <span className="site-menu-rule"></span>
      <a href="#solar-stations">Solar stations</a><a href="#lunar-stations">Lunar stations</a>
      <a href="#newsletter">The monthly letter</a><a href={signedIn?'#account':'#signin'}>{signedIn?'Account':'Sign in'}</a>
      <a href="#support">Support</a><a href="#contact">Contact</a>
    </nav>}
    </div>
  </header>;
}
function SiteFooter(){
  return <footer className="site-footer"><div className="page">
    <div className="cols">
      <div>
        <span className="brand-word" style={{fontFamily:'var(--font-display)',fontSize:22,color:'var(--ink)'}}>Shruti</span>
        <p style={{font:'400 var(--text-sm)/1.55 var(--font-body)',color:'var(--ink-soft)',maxWidth:'34ch',margin:'10px 0 14px'}}>Instruments for magick, built live from Athens.</p>
        <SocialLinkRow links={SOCIALS} size={16}/>
      </div>
      <div><h4>Site</h4><ul>
        <li><a href="#work">Work</a></li><li><a href="#today">Day at a glance</a></li><li><a href="#solar-stations">Solar stations</a></li><li><a href="#lunar-stations">Lunar stations</a></li><li><a href="#schedule">Schedule</a></li><li><a href="#videos">Videos</a></li><li><a href="#horoscopes">Horoscopes</a></li><li><a href="#journal">Journal</a></li><li><a href="#about">About</a></li>
      </ul></div>
      <div><h4>Elsewhere</h4><ul>
        <li><a href="#newsletter">The monthly letter</a></li><li><a href="#press">Press &amp; media kit</a></li><li><a href="#fanworks">Fan works</a></li><li><a href="#guidelines">Derivative work guidelines</a></li><li><a href="#support">Support</a></li><li><a href="#contact">Contact</a></li>
      </ul></div>
    </div>
    <div style={{paddingTop:'var(--space-5)',marginTop:'var(--space-5)',borderTop:'var(--border-w) solid var(--line)'}}><LegalImprint/></div>
    <div className="legal">
      <p>© ShrutiVTuber, LLC · <a href="#privacy" style={{color:'inherit'}}>Privacy</a> · <a href="#terms" style={{color:'inherit'}}>Terms</a></p>
      <span className="seal seal-ring" title="Soror Eu. A.">S∴E.A.</span>
    </div>
  </div></footer>;
}
Object.assign(window,{SiteHeader,SiteFooter,BrandMark,ASSETS,SOCIALS});
