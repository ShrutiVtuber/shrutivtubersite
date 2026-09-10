import React from 'react';
export const SIGNS = ['\u2648','\u2649','\u264A','\u264B','\u264C','\u264D','\u264E','\u264F','\u2650','\u2651','\u2652','\u2653'];
export const SIGN_NAMES = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const ELEMENT = ['fire','earth','air','water'];
const ASPECT_COLOR = { conjunction:'var(--gilt)', opposition:'var(--rose)', trine:'var(--accent)',
  square:'var(--rose)', sextile:'var(--accent)' };
const ASPECT_DASH = { conjunction:'', opposition:'', trine:'', square:'4 3', sextile:'2 4' };

/* The wheel. The thing worth screenshotting, and the only drawing in the app the
   agent is allowed to make — it is an instrument, not artwork.
   mode="transit" one instant · mode="period" movement across a span, with the
   Moon's phase ring on the outside.
   ⚠ With no birth time the angles are undefined: pass housesKnown={false} and the
   wheel drops the house ring and the ASC/MC marks rather than guessing them. */
export function ChartWheel({ mode='transit', size=320, bodies=[], aspects=[], cusps, asc=0,
  mc, housesKnown=true, phases=[], span, label='Chart wheel' }) {
  const cx = size/2, cy = size/2;
  const R = size/2 - 1;
  const rSignOut = R, rSignIn = R - size*0.088;
  const rTick = rSignIn - size*0.012;
  const rHouse = housesKnown ? rSignIn - size*0.115 : rSignIn - size*0.05;
  const rBody = rSignIn - size*0.052;
  const rLeader = rHouse + size*0.006;
  const rot = housesKnown ? asc : 0;
  const pt = (lon, r) => {
    const a = (180 + (lon - rot)) * Math.PI/180;
    return [cx + r*Math.cos(a), cy - r*Math.sin(a)];
  };
  const ring = (r0, r1, from, to) => {
    const [x0,y0] = pt(from, r1), [x1,y1] = pt(to, r1);
    const [x2,y2] = pt(to, r0), [x3,y3] = pt(from, r0);
    const big = ((to - from + 360) % 360) > 180 ? 1 : 0;
    return `M${x0} ${y0}A${r1} ${r1} 0 ${big} 0 ${x1} ${y1}L${x2} ${y2}A${r0} ${r0} 0 ${big} 1 ${x3} ${y3}Z`;
  };
  /* de-collide body glyphs: nudge apart along the ring */
  const placed = [];
  const sorted = [...bodies].sort((a,b)=>a.lon-b.lon);
  sorted.forEach(b => {
    let l = b.lon;
    while (placed.some(p => Math.abs(((l-p.lon+540)%360)-180) > 180-7)) l += 0.6;
    placed.push({ ...b, lon:b.lon, slot:l });
  });
  return (
    <svg viewBox={`0 0 ${size} ${size}`} width="100%" role="img" aria-label={label}
      style={{ display:'block', maxWidth:size, margin:'0 auto', overflow:'visible' }}>
      <circle cx={cx} cy={cy} r={R} fill="var(--inset)"/>
      {/* sign sectors */}
      {SIGNS.map((g,i) => {
        const from = i*30, to = from+30;
        const [gx,gy] = pt(from+15, (rSignOut+rSignIn)/2);
        return <g key={i}>
          <path d={ring(rSignIn, rSignOut, from, to)}
            fill={i%2 ? 'rgba(201,161,91,.055)' : 'rgba(143,190,232,.035)'}/>
          <line {...lineProps(pt(from,rSignIn), pt(from,rSignOut))} stroke="var(--gilt-dim)" strokeWidth="1"/>
          <text x={gx} y={gy} fill="var(--gilt)" fontFamily="AstroSymbols, 'EB Garamond', serif"
            fontSize={size*0.05} textAnchor="middle" dominantBaseline="central">{g}</text>
        </g>;
      })}
      <circle cx={cx} cy={cy} r={rSignOut} fill="none" stroke="var(--gilt-dim)" strokeWidth="1"/>
      <circle cx={cx} cy={cy} r={rSignIn} fill="none" stroke="var(--gilt-dim)" strokeWidth="1"/>
      {/* degree ticks, every 5° */}
      {Array.from({length:72},(_,i)=>i*5).map(d => {
        const long = d%10===0, [a,b] = [pt(d, rSignIn), pt(d, rSignIn - (long?size*0.022:size*0.012))];
        return <line key={d} {...lineProps(a,b)} stroke="var(--line-strong)" strokeWidth={long?1:0.6} opacity={long?.9:.55}/>;
      })}
      {/* houses */}
      {housesKnown && cusps && <>
        <circle cx={cx} cy={cy} r={rHouse} fill="none" stroke="var(--line)" strokeWidth="1"/>
        {cusps.map((c,i) => {
          const angle = i===0 || i===9;
          const [p0,p1] = [pt(c, rHouse), pt(c, rSignIn)];
          const [tx,ty] = pt(c + halfHouse(cusps,i), rHouse + size*0.028);
          return <g key={i}>
            <line {...lineProps(p0,p1)} stroke={angle?'var(--soft)':'var(--line-strong)'}
              strokeWidth={angle?1.4:0.8} strokeDasharray={angle?'':'3 3'}/>
            <text x={tx} y={ty} fill="var(--faint)" fontFamily="Commissioner, sans-serif"
              fontSize={size*0.032} textAnchor="middle" dominantBaseline="central">{i+1}</text>
          </g>;
        })}
        {[['ASC',asc],['MC',mc]].filter(a=>a[1]!=null).map(([nm,lon]) => {
          const [x,y] = pt(lon, rSignOut + size*0.035);
          return <text key={nm} x={x} y={y} fill="var(--soft)" fontFamily="Commissioner, sans-serif"
            fontSize={size*0.032} fontWeight="600" letterSpacing="1" textAnchor="middle"
            dominantBaseline="central">{nm}</text>;
        })}
      </>}
      {/* the moon's phase ring — period wheel only */}
      {mode==='period' && phases.map((p,i) => {
        const [x,y] = pt(p.lon, rSignOut + size*0.045), r = size*0.017;
        return <g key={i}>
          <circle cx={x} cy={y} r={r} fill="var(--inset)" stroke="var(--gilt-dim)" strokeWidth="0.8"/>
          <path d={phasePath(x,y,r,p.phase)} fill="var(--gilt-bright)"/>
        </g>;
      })}
      {/* aspects */}
      <circle cx={cx} cy={cy} r={rHouse} fill="rgba(13,18,32,.55)"/>
      {aspects.map((a,i) => {
        const [x0,y0] = pt(a.from, rHouse-1), [x1,y1] = pt(a.to, rHouse-1);
        return <line key={i} x1={x0} y1={y0} x2={x1} y2={y1} stroke={ASPECT_COLOR[a.type]||'var(--line-strong)'}
          strokeWidth={a.type==='conjunction'?1.2:0.9} strokeDasharray={ASPECT_DASH[a.type]||''}
          opacity={a.applying===false?.4:.72}/>;
      })}
      {/* bodies */}
      {placed.map((b,i) => {
        const [gx,gy] = pt(b.slot, rBody);
        const [lx0,ly0] = pt(b.lon, rLeader), [lx1,ly1] = pt(b.lon, rLeader + size*0.018);
        const [dx,dy] = pt(b.slot, rBody - size*0.048);
        return <g key={b.name||i}>
          <line x1={lx0} y1={ly0} x2={lx1} y2={ly1} stroke={b.retro?'var(--rose)':'var(--soft)'} strokeWidth="0.9"/>
          <text x={gx} y={gy} fill={b.retro?'var(--rose)':'var(--ink)'} fontFamily="AstroSymbols, 'EB Garamond', serif"
            fontSize={size*0.052} textAnchor="middle" dominantBaseline="central">{b.mark}</text>
          <text x={dx} y={dy} fill={b.retro?'var(--rose)':'var(--faint)'} fontFamily="Commissioner, sans-serif"
            fontSize={size*0.03} textAnchor="middle" dominantBaseline="central" style={{ fontVariantNumeric:'tabular-nums' }}>
            {Math.floor(b.lon%30)}{'\u00B0'}{b.retro?' \u211E':''}</text>
        </g>;
      })}
      {mode==='period' && span && <text x={cx} y={cy} fill="var(--faint)" fontFamily="Commissioner, sans-serif"
        fontSize={size*0.034} textAnchor="middle" dominantBaseline="central">{span}</text>}
    </svg>
  );
}
function lineProps([x1,y1],[x2,y2]){ return { x1, y1, x2, y2 }; }
function halfHouse(cusps,i){ const n=cusps.length; return (((cusps[(i+1)%n]-cusps[i])+360)%360)/2; }
function phasePath(x,y,r,p){
  const k = Math.cos(2*Math.PI*p), waxing = p < 0.5, rx = Math.abs(k)*r;
  const so = waxing?1:0, si = waxing?(k>0?0:1):(k>0?1:0);
  return `M ${x} ${y-r} A ${r} ${r} 0 0 ${so} ${x} ${y+r} A ${rx} ${r} 0 0 ${si} ${x} ${y-r} Z`;
}
