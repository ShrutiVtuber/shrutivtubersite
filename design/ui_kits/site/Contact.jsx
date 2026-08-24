const {SectionHeader,TextField,TextArea,SelectField,Button,EmptyState}=window.ShrutiDesignSystem_cb687f;
function ContactScreen(){
  const [f,setF]=React.useState({topic:'',name:'',email:'',msg:''});
  const [err,setErr]=React.useState({});
  const [sent,setSent]=React.useState(false);
  const set=k=>e=>{const v=e.target.value;setF(s=>({...s,[k]:v}));setErr(s=>({...s,[k]:undefined}))};
  const submit=e=>{e.preventDefault();const n={};
    if(!f.topic)n.topic='Pick a route so this lands in the right inbox.';
    if(!f.name.trim())n.name='Please add a name — a handle is fine.';
    if(!/^\S+@\S+\.\S+$/.test(f.email))n.email='That address doesn\u2019t look complete.';
    if(f.msg.trim().length<10)n.msg='A sentence or two helps me reply well.';
    setErr(n);if(Object.keys(n).length===0)setSent(true)};
  const Card=({title,children})=><div style={{background:'var(--surface-card)',border:'1px solid var(--line)',borderRadius:10,boxShadow:'var(--shadow-1)',padding:'20px',display:'grid',gap:8,alignContent:'start'}}>
    <h2 style={{font:'600 var(--text-h3, 20px) var(--font-display)',color:'var(--ink)',margin:0}}>{title}</h2>{children}</div>;
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="☿" eyebrow="Contact" title="Two routes in" body="Business goes to one inbox, everything else to another — pick the right one and it gets answered faster."/>
    <div className="grid-2">
      <Card title="Business enquiries">
        <p style={{font:'400 var(--text-sm)/1.55 var(--font-body)',color:'var(--ink-soft)',margin:0}}>Sponsorships, events, press. The brand-safety statement and asset pack are in the press kit.</p>
        <span style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink)'}}>business@shrutivtuber.com</span>
        <div><Button variant="ghost" href="#press">Open the press kit</Button></div>
      </Card>
      <Card title="Everything else">
        <p style={{font:'400 var(--text-sm)/1.55 var(--font-body)',color:'var(--ink-soft)',margin:0}}>Fan works, questions, edge cases, hellos. Discord is fastest; the form below also works.</p>
        <span style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink)'}}>hello@shrutivtuber.com</span>
        <div><Button variant="ghost" href="#">Join the Discord</Button></div>
      </Card>
    </div>
    {sent?
      <EmptyState glyph="☾" title="Sent — thank you." body="Replies come from hello@shrutivtuber.com, usually within two working days. Business mail may take one more."
        action={<Button variant="secondary" onClick={()=>{setSent(false);setF({topic:'',name:'',email:'',msg:''})}}>Send another</Button>}/>
      :
      <form onSubmit={submit} noValidate style={{display:'grid',gap:18,maxWidth:560}}>
        <SelectField label="What is this about?" placeholder="Choose a route" options={['Business enquiry','Press','Fan works submission','Something else']} value={f.topic} onChange={set('topic')} error={err.topic} required/>
        <TextField label="Name" placeholder="How should I address you?" value={f.name} onChange={set('name')} error={err.name} required/>
        <TextField label="Email" type="email" placeholder="you@example.com" hint="Only used to reply." value={f.email} onChange={set('email')} error={err.email} required/>
        <TextArea label="Message" rows={6} maxLength={800} value={f.msg} onChange={set('msg')} error={err.msg} required placeholder="For fan works: include a link and the credit you want shown."/>
        <div><Button type="submit">Send</Button></div>
      </form>}
  </main>;
}
Object.assign(window,{ContactScreen});