const {SectionHeader,Button}=window.ShrutiDesignSystem_cb687f;
function GuidelinesScreen(){
  const Rule=({m,children})=>{
    const c=m==='●'?'var(--live)':m==='◐'?'var(--rose)':'var(--accent)';
    const w=m==='●'?'Not permitted':m==='◐'?'Ask first':'Permitted';
    return <li style={{display:'flex',gap:12,alignItems:'baseline',padding:'10px 0',borderBottom:'1px solid var(--line)'}}>
      <span aria-hidden="true" style={{color:c,fontFamily:'var(--font-display)',fontSize:15,flexShrink:0}}>{m}</span>
      <span style={{font:'400 var(--text-body)/1.6 var(--font-body)',color:'var(--ink)'}}><strong style={{fontWeight:600}}>{w} — </strong>{children}</span></li>;};
  const H=({t})=><h2 style={{font:'600 var(--text-h3, 22px) var(--font-display)',color:'var(--ink)',margin:'18px 0 2px'}}>{t}</h2>;
  return <main className="site-main page">
    <SectionHeader as="h1" glyph="◐" eyebrow="Derivative work guidelines" title="What you may make" body="Fan works are welcome — this page exists so nobody has to guess. The short version: make things, credit yourself, don't sell the character, and keep machines from learning her."/>
    <p style={{font:'500 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:0}}><span style={{color:'var(--accent)'}}>○</span> permitted · <span style={{color:'var(--rose)'}}>◐</span> ask first · <span style={{color:'var(--live)'}}>●</span> not permitted</p>
    <section><H t="Fan art"/><ul style={{listStyle:'none',margin:0,padding:0}}>
      <Rule m="○">Drawing, writing, music, cosplay and edits of Shruti, posted anywhere, with your own credit. Tag #ShrutiArts so it can be found and featured.</Rule>
      <Rule m="◐">NSFW work — allowed for adults, clearly marked, and kept out of the main tag. Never present it as official.</Rule>
      <Rule m="●">Passing fan work off as official art, or removing another artist's credit.</Rule></ul></section>
    <section><H t="Commercial use"/><ul style={{listStyle:'none',margin:0,padding:0}}>
      <Rule m="○">Monetised platforms carrying your fan work — ad revenue on your own speedpaint or cover is yours.</Rule>
      <Rule m="◐">Small-batch prints or con merch of your own fan art — write first; the answer is usually yes.</Rule>
      <Rule m="●">Mass-produced merchandise of the character, or commercial use of the wordmark and official art, without a written agreement.</Rule></ul></section>
    <section><H t="AI"/><ul style={{listStyle:'none',margin:0,padding:0}}>
      <Rule m="●">Training generative models on her art, voice, streams or writing — including LoRAs and voice clones.</Rule>
      <Rule m="●">AI-generated images in the fan tags. The gallery is for made things.</Rule></ul></section>
    <section><H t="Clips &amp; streams"/><ul style={{listStyle:'none',margin:0,padding:0}}>
      <Rule m="○">Clips, edits, translations and reaction content, with a link back to the stream or VOD.</Rule>
      <Rule m="●">Re-uploading full VODs or streams without permission.</Rule></ul></section>
    <section><H t="Voice &amp; likeness"/><ul style={{listStyle:'none',margin:0,padding:0}}>
      <Rule m="◐">Soundboards and voice compilations — ask, with the clips you intend to use.</Rule>
      <Rule m="●">Impersonation: accounts, bots or content presenting themselves as Shruti.</Rule></ul></section>
    <p style={{font:'400 var(--text-sm) var(--font-mono)',color:'var(--ink-soft)',margin:'14px 0 0'}}>Questions live in the contact form. Last updated 2026-08 · signed, Shruti</p>
    <div style={{display:'flex',gap:10}}><Button variant="secondary" href="#contact">Ask about an edge case</Button><Button variant="ghost" href="#fanworks">See fan works</Button></div>
  </main>;
}
Object.assign(window,{GuidelinesScreen});