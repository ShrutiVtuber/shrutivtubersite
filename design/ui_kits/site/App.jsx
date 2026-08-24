const {Button,EmptyState}=window.ShrutiDesignSystem_cb687f;
function NotFoundScreen(){
  return <main className="site-main page" style={{minHeight:'52vh',display:'grid',placeItems:'center'}}>
    <div style={{textAlign:'center',display:'grid',gap:18,justifyItems:'center'}}>
      <span style={{font:'500 72px var(--font-display)',color:'var(--ink)',lineHeight:1}} aria-hidden="true">4○4</span>
      <h1 style={{font:'600 var(--text-h2) var(--font-display)',color:'var(--ink)',margin:0}}>This page is in another sky.</h1>
      <p style={{font:'400 var(--text-body) var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'40ch'}}>The address may have moved when the site was rebuilt — the almanac below will get you home.</p>
      <div style={{display:'flex',gap:10}}><Button href="#home">Back home</Button><Button variant="secondary" href="#journal">Read the journal</Button></div>
    </div>
  </main>;
}
function ServerErrorScreen({onHome}){
  return <main className="site-main page" style={{minHeight:'52vh',display:'grid',placeItems:'center'}}>
    <div style={{textAlign:'center',display:'grid',gap:18,justifyItems:'center'}}>
      <span style={{font:'500 72px var(--font-display)',color:'var(--ink)',lineHeight:1}} aria-hidden="true">5○○</span>
      <h1 style={{font:'600 var(--text-h2) var(--font-display)',color:'var(--ink)',margin:0}}>The instrument slipped.</h1>
      <p style={{font:'400 var(--text-body) var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'40ch'}}>Something failed on my side, not yours. It's being looked at — try again in a moment.</p>
      <div style={{display:'flex',gap:10}}><Button href="#home" onClick={onHome}>Back home</Button><Button variant="secondary" onClick={()=>location.reload()}>Try again</Button></div>
      <p style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:0}}>error 500 · if it persists, hello@shrutivtuber.com</p>
    </div>
  </main>;
}
function App(){
  const read=()=>location.hash.replace('#','')||'home';
  const [route,setRoute]=React.useState(read());
  const [theme,setTheme]=React.useState('system');
  const [withArt,setWithArt]=React.useState(true);
  const [liveOn,setLiveOn]=React.useState(true);
  const [scheduleEmpty,setScheduleEmpty]=React.useState(false);
  const [tz,setTz]=React.useState('local');
  const [article,setArticle]=React.useState(false);
  const [broken,setBroken]=React.useState(false);
  const [signedIn,setSignedIn]=React.useState(false);
  const [sign,setSign]=React.useState('virgo');
  const [period,setPeriod]=React.useState('monthly');
  const [authMethod,setAuthMethod]=React.useState('link');
  const [acctTab,setAcctTab]=React.useState('profile');
  const [polar,setPolar]=React.useState(false);
  const [birthTime,setBirthTime]=React.useState(true);
  React.useEffect(()=>{const on=()=>{setRoute(read());setArticle(false);setBroken(false);window.scrollTo(0,0)};window.addEventListener('hashchange',on);return ()=>window.removeEventListener('hashchange',on)},[]);
  React.useEffect(()=>{const el=document.documentElement;if(theme==='system')el.removeAttribute('data-theme');else el.setAttribute('data-theme',theme)},[theme]);
  const live=liveOn?{status:'live',title:'Building the sigil compiler',game:'Software & Game Dev',viewers:214}:{status:'offline'};
  const known=['home','about','work','schedule','videos','journal','press','fanworks','guidelines','contact','support','privacy','terms','signup','signin','account','nativity','horoscopes','horoscope','newsletter','newsletter-archive','newsletter-preferences','newsletter-confirm','newsletter-unsubscribed','today','solar-stations','lunar-stations'];
  return <>
    <SiteHeader route={route} live={live} withArt={withArt} signedIn={signedIn}/>
    {broken&&<ServerErrorScreen onHome={()=>setBroken(false)}/>}
    {route==='home'&&!broken&&<HomeScreen live={live} withArt={withArt} tz={tz}/>}
    {route==='about'&&!broken&&<AboutScreen/>}
    {route==='work'&&!broken&&<WorkScreen/>}
    {route==='schedule'&&!broken&&<ScheduleScreen tz={tz} setTz={setTz} empty={scheduleEmpty}/>}
    {route==='videos'&&!broken&&<VideosScreen loading={false}/>}
    {route==='journal'&&!broken&&<JournalScreen article={article} openArticle={setArticle}/>}
    {route==='press'&&!broken&&<PressScreen/>}
    {route==='fanworks'&&!broken&&<FanWorksScreen/>}
    {route==='guidelines'&&!broken&&<GuidelinesScreen/>}
    {route==='contact'&&!broken&&<ContactScreen/>}
    {route==='support'&&!broken&&<SupportScreen/>}
    {(route==='privacy'||route==='terms')&&!broken&&<LegalScreen doc={route}/>}
    {(route==='signup'||route==='signin')&&!broken&&<AuthScreen mode={route} go={r=>{location.hash=r}} method={authMethod} setMethod={setAuthMethod}/>}
    {route==='account'&&!broken&&<AccountScreen tab={acctTab} go={setAcctTab}/>}
    {route==='nativity'&&!broken&&<AccountScreen tab="nativity" go={setAcctTab}/>}
    {route==='horoscopes'&&!broken&&<HoroscopeIndex sign={sign} setSign={s=>{setSign(s);location.hash='horoscope'}} ownSign={signedIn?'virgo':null} signedIn={signedIn}/>}
    {route==='horoscope'&&!broken&&<HoroscopeReading sign={sign} setSign={setSign} period={period} setPeriod={setPeriod} ownSign={signedIn?'virgo':null}/>}
    {route==='newsletter'&&!broken&&<NewsletterScreen view="subscribe"/>}
    {route==='newsletter-archive'&&!broken&&<NewsletterScreen view="archive"/>}
    {route==='newsletter-preferences'&&!broken&&<NewsletterScreen view="preferences"/>}
    {route==='newsletter-confirm'&&!broken&&<NewsletterScreen view="confirm"/>}
    {route==='newsletter-unsubscribed'&&!broken&&<NewsletterScreen view="unsubscribed"/>}
    {route==='today'&&!broken&&<TodayScreen signedIn={signedIn} birthTime={birthTime} polar={polar}/>}
    {route==='solar-stations'&&!broken&&<StationsScreen kind="solar" polar={polar}/>}
    {route==='lunar-stations'&&!broken&&<StationsScreen kind="lunar" polar={polar}/>}
    {!known.includes(route)&&!broken&&<NotFoundScreen/>}
    <SiteFooter/>
    <div className="demo-bar" role="group" aria-label="Demo controls (not part of the site)">
      <span className="demo-lbl">demo</span>
      <button type="button" onClick={()=>setTheme(t=>t==='system'?'light':t==='light'?'dark':'system')}>{theme==='system'?'◐ system':theme==='light'?'☀ dawn':'☾ dusk'}</button>
      <button type="button" aria-pressed={withArt} onClick={()=>setWithArt(a=>!a)}>art {withArt?'on':'off'}</button>
      <button type="button" aria-pressed={liveOn} onClick={()=>setLiveOn(l=>!l)}>{liveOn?'live':'offline'}</button>
      {route==='schedule'&&<button type="button" aria-pressed={scheduleEmpty} onClick={()=>setScheduleEmpty(e=>!e)}>empty</button>}
      <button type="button" aria-pressed={signedIn} onClick={()=>setSignedIn(s=>!s)}>{signedIn?'signed in':'signed out'}</button>
      {(route==='today'||route==='solar-stations'||route==='lunar-stations')&&<button type="button" aria-pressed={polar} onClick={()=>setPolar(p=>!p)}>{polar?'polar':'athens'}</button>}
      {route==='today'&&signedIn&&<button type="button" aria-pressed={!birthTime} onClick={()=>setBirthTime(b=>!b)}>{birthTime?'has birth time':'no birth time'}</button>}
      <button type="button" onClick={()=>{setBroken(false);location.hash='nowhere'}}>404</button>
      <button type="button" aria-pressed={broken} onClick={()=>setBroken(b=>!b)}>500</button>
    </div>
  </>;
}
ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
