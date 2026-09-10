/* Shared frame pieces for the Astrolabe kit. Not design-system components —
   just the scaffolding the recreation needs. */
const DS = window.AstrolabeDesignSystem_d3620a || {};
/* Any name not yet in the compiled bundle resolves to a visible stub rather than
   taking the whole screen down. */
const NEEDED = ['AppBar','TabBar','SegmentedControl','ListRow','ListGroup','Button','IconButton',
  'TextField','Chip','Switch','ChoiceRow','Card','Sheet','Dialog','DataTable','DataRow',
  'ChartWheel','CodeBlock','Glyph','Icon','MoonDisc','LiveBanner','HourChip','SectionHeader',
  'Masthead','DayArc','EmptyState','Banner','Snackbar','Progress','Skeleton','ContentCard',
  'WorkCard','OfferCard','VoteControl','Prose'];
const R = {};
NEEDED.forEach(n => { R[n] = DS[n] || function Pending(){ return <div style={{ padding:'10px 12px',
  border:'1px dashed var(--line-strong)', borderRadius:'var(--radius-sm)',
  font:'400 12px/1.4 var(--font-body)', color:'var(--faint)' }}>{n} is not in the compiled bundle
  yet \u2014 reload once the project has compiled.</div>; }; });
const { AppBar, TabBar, SegmentedControl, ListRow, ListGroup, Button, IconButton, TextField,
  Chip, Switch, ChoiceRow, Card, Sheet, Dialog, DataTable, DataRow, ChartWheel, CodeBlock,
  Glyph, Icon, MoonDisc, LiveBanner, HourChip, SectionHeader, Masthead, DayArc, EmptyState, Banner,
  Snackbar, Progress, Skeleton, ContentCard, WorkCard, OfferCard, VoteControl, Prose } = R;

/* ⚠ A phone shows no scrollbars, and nothing in this app scrolls sideways.
   Vertical overflow is indicated by a fade at the foot of the scroller instead. */
function kitChrome(){
  if (typeof document === 'undefined' || document.getElementById('as-kit-chrome')) return;
  const s = document.createElement('style'); s.id = 'as-kit-chrome';
  s.textContent = '.as-scroll{scrollbar-width:none;-ms-overflow-style:none}'
    + '.as-scroll::-webkit-scrollbar{width:0;height:0;display:none}'
    + '.as-fade{position:relative}'
    + '.as-fade::after{content:"";position:absolute;left:0;right:0;bottom:0;height:28px;'
    + 'pointer-events:none;background:linear-gradient(180deg,transparent,var(--page));'
    + 'opacity:var(--as-fade,1);transition:opacity 160ms var(--ease-out);z-index:5}';
  document.head.appendChild(s);
}

/* The scrolling body of a screen. No scrollbar, never sideways; the foot fades
   while there is more below and clears when you reach the end. */
function Body({ children, pad = 16, gap = 14, style }) {
  kitChrome();
  const ref = React.useRef(null);
  const [more, setMore] = React.useState(false);
  const check = React.useCallback(() => {
    const el = ref.current; if (!el) return;
    setMore(el.scrollHeight - el.clientHeight - el.scrollTop > 8);
  }, []);
  React.useEffect(() => { check(); const el = ref.current; if (!el) return;
    const ro = new ResizeObserver(check); ro.observe(el);
    return () => ro.disconnect(); }, [check, children]);
  return <div className="as-fade" style={{ flex:1, minHeight:0, minWidth:0, display:'flex',
    ['--as-fade']: more ? 1 : 0 }}>
    <div ref={ref} onScroll={check} className="as-scroll" style={{ flex:1, minWidth:0, minHeight:0,
      overflowY:'auto', overflowX:'hidden', overscrollBehavior:'contain',
      padding:`12px ${pad}px 20px`, display:'grid', gridTemplateColumns:'minmax(0,1fr)',
      gridAutoRows:'min-content', gap, alignContent:'start', ...style }}>{children}</div>
  </div>;
}
/* A row of chips that would otherwise scroll sideways. It wraps instead. */
function ChipRow({ children }) {
  return <div style={{ display:'flex', gap:8, flexWrap:'wrap', minWidth:0 }}>{children}</div>;
}
/* A phone status bar — chrome, not design system. */
function StatusBar({ time = '20:41', live }) {
  return <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between',
    padding:'0 18px', height:32, flex:'none', font:'600 12px/1 var(--font-body)',
    color:'var(--soft)', fontVariantNumeric:'tabular-nums', background:'var(--page)' }}>
    <span>{time}</span>
    <span style={{ display:'flex', gap:6, alignItems:'center', opacity:.8 }}>
      {live && <span style={{ width:6, height:6, borderRadius:99, background:'var(--live)' }}/>}
      <Icon name="signal_cellular_alt" size={14} tone="soft"/>
      <Icon name="wifi" size={14} tone="soft"/>
      <Icon name="battery_5_bar" size={14} tone="soft"/>
    </span>
  </div>;
}
/* Pull-to-refresh puck, shown while a screen refreshes something already on it. */
function Refreshing() { return <Progress kind="refresh"/>; }

/* A run of DataRows on a card. */
function FactCard({ title, rows, foot }) {
  return <Card>
    {title && <div className="t-eyebrow" style={{ marginBottom:8 }}>{title}</div>}
    {rows.map((r,i) => <DataRow key={i} mark={r.mark} label={r.label} value={r.value}
      tone={r.rose?'rose':'ink'} small={r.small}/>)}
    {foot && <div className="t-caption" style={{ marginTop:10, paddingTop:10,
      borderTop:'1px solid var(--line)' }}>{foot}</div>}
  </Card>;
}
/* Provenance: engine, the rule in force, licence. Every instrument carries one. */
function Provenance({ engine = 'Swiss Ephemeris 2.10.03', rule, extra }) {
  return <div style={{ display:'grid', gap:2, padding:'2px 2px 0' }}>
    {rule && <DataRow label="Rule in force" value={rule} small tone="faint"/>}
    <DataRow label="Engine" value={engine} small tone="faint"/>
    <DataRow label="Computed" value="On this device, offline" small tone="faint"/>
    {extra}
  </div>;
}
Object.assign(window, { DS, Body, ChipRow, StatusBar, Refreshing, FactCard, Provenance, kitChrome,
  AppBar, TabBar, SegmentedControl, ListRow, ListGroup, Button, IconButton, TextField,
  Chip, Switch, ChoiceRow, Card, Sheet, Dialog, DataTable, DataRow, ChartWheel, CodeBlock,
  Glyph, Icon, MoonDisc, LiveBanner, HourChip, SectionHeader, Masthead, DayArc, EmptyState, Banner,
  Snackbar, Progress, Skeleton, ContentCard, WorkCard, OfferCard, VoteControl, Prose });
