const {SectionHeader,TextField,Button,ConsentCheckbox,EmptyState,Badge}=window.ShrutiDesignSystem_cb687f;

function AuthScreen({mode,go,method,setMethod}){
  const signUp=mode==='signup';
  const [f,setF]=React.useState({email:'',pw:'',name:''});
  const [c,setC]=React.useState({account:false,birth:false,letter:false});
  const [err,setErr]=React.useState({});
  const [sent,setSent]=React.useState(false);
  const set=k=>e=>{const v=e.target.value;setF(s=>({...s,[k]:v}));setErr(s=>({...s,[k]:undefined}))};
  const flip=k=>e=>{const v=e.target.checked;setC(s=>({...s,[k]:v}));setErr(s=>({...s,[k]:undefined}))};
  const submit=e=>{e.preventDefault();const n={};
    if(!/^\S+@\S+\.\S+$/.test(f.email))n.email='That address doesn\u2019t look complete.';
    if(method==='password'&&f.pw.length<10)n.pw='Ten characters or more, please — a phrase beats a password.';
    if(signUp&&!c.account)n.account='This one is needed to make an account at all.';
    setErr(n);if(Object.keys(n).length===0)setSent(true)};

  if(sent&&method==='link')return <main className="site-main page">
    <EmptyState glyph="◐" title="Check your email"
      body={`A sign-in link is on its way to ${f.email}. It expires in fifteen minutes, and it only works once. If it hasn't arrived in a minute, look in spam — the address it comes from is new.`}
      action={<div style={{display:'flex',gap:10,flexWrap:'wrap'}}><Button variant="secondary" onClick={()=>setSent(false)}>Use a different address</Button><Button variant="ghost" onClick={()=>setSent(false)}>Send it again</Button></div>}/>
    <p style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',margin:0,textAlign:'center'}}>Opened the link on your phone but signed up on a laptop? Either works — the link signs in the device that opens it.</p>
  </main>;

  if(sent)return <main className="site-main page">
    <EmptyState glyph="☾" title={signUp?'Account made':'Signed in'}
      body={signUp?'Your consents are recorded and revisitable in settings. Next: a saved nativity, if you want your own chart and your own horoscope — it is optional and you can add it later.':'Welcome back.'}
      action={<div style={{display:'flex',gap:10,flexWrap:'wrap'}}><Button href="#nativity">Add my nativity</Button><Button variant="secondary" href="#horoscopes">Read this month</Button></div>}/>
  </main>;

  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☾" eyebrow={signUp?'Create an account':'Sign in'}
      title={signUp?'Keep your own chart':'Welcome back'}
      body={signUp?'An account holds one nativity and remembers how you like it reckoned. There are no public profiles here, no followers, and nothing to decorate — you sign up once and come back to read.':'Email and a link, or email and a password. Whichever you set up with.'}/>

    <div style={{display:'flex',gap:8,padding:'0 0 var(--space-4)',borderBottom:'1px solid var(--line)'}}>
      <Button variant={method==='link'?'secondary':'ghost'} onClick={()=>setMethod('link')}>Email me a link</Button>
      <Button variant={method==='password'?'secondary':'ghost'} onClick={()=>setMethod('password')}>Use a password</Button>
    </div>

    <form onSubmit={submit} noValidate style={{display:'grid',gap:'var(--space-5)',maxWidth:620}}>
      <div style={{display:'grid',gap:'var(--space-4)',maxWidth:440}}>
        {signUp&&<TextField label="Display name" hint="Only ever shown back to you." optionalLabel value={f.name} onChange={set('name')} placeholder="What should the letter call you?"/>}
        <TextField label="Email" type="email" required value={f.email} onChange={set('email')} error={err.email} placeholder="you@example.com" hint={method==='link'?'We send a sign-in link — no password to forget.':undefined}/>
        {method==='password'&&<TextField label="Password" type="password" required value={f.pw} onChange={set('pw')} error={err.pw} hint="Ten characters or more. A phrase you can remember beats a puzzle you cannot."/>}
      </div>

      {signUp&&<div style={{display:'grid',gap:'var(--space-3)'}}>
        <div>
          <h2 style={{font:'600 var(--text-h3) var(--font-display)',color:'var(--ink)',margin:'0 0 6px'}}>Three separate decisions</h2>
          <p style={{font:'400 var(--text-sm)/1.6 var(--font-body)',color:'var(--ink-soft)',margin:0,maxWidth:'62ch'}}>Say yes to one and no to another — that is normal here, and the first is the only one needed to have an account. This form is longer than most sign-ups on purpose.</p>
        </div>
        <ConsentCheckbox basis="contract" required checked={c.account} onChange={flip('account')} error={err.account}
          label="Create my account"
          explanation="Your email and display name are stored so you can sign in and so the site knows what to show you. This is the account itself — without it there is nothing to sign into."/>
        <ConsentCheckbox basis="explicit consent · GDPR Art. 9" checked={c.birth} onChange={flip('birth')}
          label="Store my birth data so my chart and horoscope can be calculated"
          explanation="Birth date, time and place, kept on your account and used only to compute your chart and to choose your horoscope. Because a reading arguably reveals philosophical belief, this may be special category data — so it is asked for separately and never assumed. Nothing is shared, sold, or used to train anything. Withdraw it in settings and the data goes with it."/>
        <ConsentCheckbox basis="consent · marketing" checked={c.letter} onChange={flip('letter')}
          label="Send me the monthly letter, including offers"
          explanation="One email a month: your horoscope, what I published and streamed, and a letter written by hand. It will also carry offers for astrological courses and magickal services when those open — saying so now is fairer than saying so later. One-click unsubscribe, or pause it instead."/>
        <p style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)',margin:0}}>No box here is pre-ticked, and none of them is bundled into another. All three are revisitable in settings.</p>
      </div>}

      <div style={{display:'flex',gap:12,alignItems:'center',flexWrap:'wrap'}}>
        <Button type="submit">{signUp?'Create account':(method==='link'?'Email me a link':'Sign in')}</Button>
        <button type="button" onClick={()=>go(signUp?'signin':'signup')} style={{appearance:'none',border:0,background:'transparent',font:'500 var(--text-sm) var(--font-body)',color:'var(--accent)',cursor:'pointer',textDecoration:'underline',textUnderlineOffset:3}}>
          {signUp?'I already have an account':'I need an account'}
        </button>
      </div>
    </form>

    <div style={{borderTop:'1px solid var(--line)',paddingTop:'var(--space-4)',display:'flex',gap:'8px 20px',flexWrap:'wrap',alignItems:'center'}}>
      <Badge tone="faint">no cookie banner</Badge>
      <span style={{font:'400 var(--text-xs)/1.7 var(--font-mono)',color:'var(--ink-faint)'}}>Analytics here are cookieless, so there is nothing to consent to and no banner to dismiss.</span>
    </div>
  </main>;
}
Object.assign(window,{AuthScreen});