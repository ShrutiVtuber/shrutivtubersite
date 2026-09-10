/* @ds-bundle: {"format":4,"namespace":"AstrolabeDesignSystem_d3620a","components":[{"name":"AppBar","sourcePath":"components/brand/AppBar.jsx"},{"name":"DayArc","sourcePath":"components/brand/DayArc.jsx"},{"name":"HOUR_RULERS","sourcePath":"components/brand/HourChip.jsx"},{"name":"HourChip","sourcePath":"components/brand/HourChip.jsx"},{"name":"LiveBanner","sourcePath":"components/brand/LiveBanner.jsx"},{"name":"Masthead","sourcePath":"components/brand/Masthead.jsx"},{"name":"SectionHeader","sourcePath":"components/brand/SectionHeader.jsx"},{"name":"ContentCard","sourcePath":"components/content/ContentCard.jsx"},{"name":"OfferCard","sourcePath":"components/content/OfferCard.jsx"},{"name":"Prose","sourcePath":"components/content/Prose.jsx"},{"name":"VoteControl","sourcePath":"components/content/VoteControl.jsx"},{"name":"WorkCard","sourcePath":"components/content/WorkCard.jsx"},{"name":"SIGNS","sourcePath":"components/data/ChartWheel.jsx"},{"name":"SIGN_NAMES","sourcePath":"components/data/ChartWheel.jsx"},{"name":"ChartWheel","sourcePath":"components/data/ChartWheel.jsx"},{"name":"CodeBlock","sourcePath":"components/data/CodeBlock.jsx"},{"name":"DataRow","sourcePath":"components/data/DataRow.jsx"},{"name":"DataTable","sourcePath":"components/data/DataTable.jsx"},{"name":"Banner","sourcePath":"components/feedback/Banner.jsx"},{"name":"EmptyState","sourcePath":"components/feedback/EmptyState.jsx"},{"name":"Progress","sourcePath":"components/feedback/Progress.jsx"},{"name":"Skeleton","sourcePath":"components/feedback/Progress.jsx"},{"name":"Snackbar","sourcePath":"components/feedback/Snackbar.jsx"},{"name":"Button","sourcePath":"components/forms/Button.jsx"},{"name":"Chip","sourcePath":"components/forms/Chip.jsx"},{"name":"ChoiceRow","sourcePath":"components/forms/ChoiceRow.jsx"},{"name":"IconButton","sourcePath":"components/forms/IconButton.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"TextField","sourcePath":"components/forms/TextField.jsx"},{"name":"MARKS","sourcePath":"components/marks/Glyph.jsx"},{"name":"Glyph","sourcePath":"components/marks/Glyph.jsx"},{"name":"Icon","sourcePath":"components/marks/Icon.jsx"},{"name":"MoonDisc","sourcePath":"components/marks/MoonDisc.jsx"},{"name":"ListRow","sourcePath":"components/navigation/ListRow.jsx"},{"name":"ListGroup","sourcePath":"components/navigation/ListRow.jsx"},{"name":"SegmentedControl","sourcePath":"components/navigation/SegmentedControl.jsx"},{"name":"TABS","sourcePath":"components/navigation/TabBar.jsx"},{"name":"TabBar","sourcePath":"components/navigation/TabBar.jsx"},{"name":"Card","sourcePath":"components/surfaces/Card.jsx"},{"name":"Dialog","sourcePath":"components/surfaces/Dialog.jsx"},{"name":"Sheet","sourcePath":"components/surfaces/Sheet.jsx"}],"sourceHashes":{"components/brand/AppBar.jsx":"fef3553f1d4a","components/brand/DayArc.jsx":"c1a4133d1ba9","components/brand/HourChip.jsx":"0cbbbef0e3cf","components/brand/LiveBanner.jsx":"144d1dc8fcaf","components/brand/Masthead.jsx":"bcc0d5d5fa99","components/brand/SectionHeader.jsx":"f886f08069d7","components/content/ContentCard.jsx":"e8bf3cd52cd7","components/content/OfferCard.jsx":"1b20de4d45df","components/content/Prose.jsx":"fc8d0dda1e9e","components/content/VoteControl.jsx":"979c3b41675d","components/content/WorkCard.jsx":"731bd98bd5bf","components/data/ChartWheel.jsx":"f0780ed7e336","components/data/CodeBlock.jsx":"28b8313cab9c","components/data/DataRow.jsx":"6716694e63ec","components/data/DataTable.jsx":"6668d1894847","components/feedback/Banner.jsx":"8a3dad21c675","components/feedback/EmptyState.jsx":"8aad82257e18","components/feedback/Progress.jsx":"c2e5cb6eb846","components/feedback/Snackbar.jsx":"580ad73595cb","components/forms/Button.jsx":"3648d0e0d698","components/forms/Chip.jsx":"970e424f29fb","components/forms/ChoiceRow.jsx":"e5c0bbc4dd4f","components/forms/IconButton.jsx":"562b31e29c13","components/forms/Switch.jsx":"2b668ed2548b","components/forms/TextField.jsx":"e0a251e74a1c","components/marks/Glyph.jsx":"564f8648482e","components/marks/Icon.jsx":"8e46769441c4","components/marks/MoonDisc.jsx":"5f2fa6e91048","components/navigation/ListRow.jsx":"e9e4b0d4749f","components/navigation/SegmentedControl.jsx":"b35f35a1fdaa","components/navigation/TabBar.jsx":"8d3e3517528b","components/surfaces/Card.jsx":"89bd88635556","components/surfaces/Dialog.jsx":"e47bda9f7081","components/surfaces/Sheet.jsx":"80cbae9170e2","ui_kits/astrolabe/App.jsx":"95b7cabbff84","ui_kits/astrolabe/Artwork.jsx":"4cbd429560a0","ui_kits/astrolabe/Kit.jsx":"754a621f8e9d","ui_kits/astrolabe/Screens1.jsx":"f94872cf22fc","ui_kits/astrolabe/Screens2.jsx":"e214cf23579d","ui_kits/astrolabe/Screens3.jsx":"57d09d220c94","ui_kits/astrolabe/Screens4.jsx":"d501c7c8f95a","ui_kits/astrolabe/States.jsx":"65ac9ff85352","ui_kits/astrolabe/data.js":"41430bf13703","ui_kits/astrolabe/image-slot.js":"fff26d081c8d"},"inlinedExternals":[],"unexposedExports":[{"name":"phaseName","sourcePath":"components/marks/MoonDisc.jsx"}]} */

(() => {

const __ds_ns = (window.AstrolabeDesignSystem_d3620a = window.AstrolabeDesignSystem_d3620a || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/brand/Masthead.jsx
try { (() => {
/* Home's one brand surface. Cloak navy with the light it catches in her
   artwork, a real scatter of stars, a gold hem top and bottom, and her
   portrait standing in the right third.

   Two honest portrait states, because she has one kind of art today and will
   draw the other:
     fit="cutout"  a transparent PNG, bottom-anchored, bleeding off the edge —
                   what artwork-spec.md #3 and #4 ask for
     fit="plate"   an opaque square (the existing painted references), framed
                   with a hairline. Never silhouetted, never faked.

   ⚠ Art-absent is a designed state, not a fallback: with no portrait the plate
   keeps its full height and the column holds a large gilt crescent set in
   AstroSymbols, so the composition is finished before a drawing arrives — and
   the drawing lands in exactly that box. */
function Masthead({
  greeting,
  line,
  portrait,
  portraitAlt = '',
  fit = 'cutout',
  live = false,
  children,
  height = 244,
  artSlot,
  col = 150
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: "plate scatter hem hem-strong",
    "data-live": live || undefined,
    style: {
      position: 'relative',
      minHeight: height,
      display: 'block',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden'
    }
  }, live && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      inset: 0,
      zIndex: 0,
      background: 'radial-gradient(140% 110% at 82% 100%,color-mix(in srgb,var(--live) 24%,transparent) 0%,transparent 60%)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    "aria-hidden": artSlot || portrait ? undefined : 'true',
    style: {
      position: 'absolute',
      right: 0,
      bottom: 0,
      top: 0,
      width: col,
      zIndex: 1,
      display: 'grid',
      alignItems: 'end',
      justifyItems: 'center',
      padding: fit === 'plate' ? '0 12px 14px 0' : 0
    }
  }, artSlot ? artSlot : portrait ? fit === 'plate' ? /*#__PURE__*/React.createElement("img", {
    src: portrait,
    alt: portraitAlt,
    style: {
      display: 'block',
      width: '100%',
      aspectRatio: '1/1',
      objectFit: 'cover',
      borderRadius: 'var(--radius-md)',
      border: '1px solid color-mix(in srgb,var(--gilt) 42%,transparent)',
      boxShadow: '0 10px 26px rgba(0,0,0,.5)'
    }
  }) : /*#__PURE__*/React.createElement("img", {
    src: portrait,
    alt: portraitAlt,
    style: {
      display: 'block',
      width: '100%',
      height: '100%',
      objectFit: 'cover',
      objectPosition: 'bottom center',
      filter: 'drop-shadow(0 8px 22px rgba(0,0,0,.5))'
    }
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      right: -10,
      bottom: -22,
      font: '400 176px/1 var(--font-glyph)',
      color: 'var(--gilt)',
      opacity: .3,
      textShadow: '0 0 40px color-mix(in srgb,var(--gilt) 30%,transparent)',
      pointerEvents: 'none',
      userSelect: 'none'
    }
  }, '\u263E\uFE0E')), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      zIndex: 2,
      minHeight: height,
      display: 'grid',
      gap: 12,
      alignContent: 'end',
      padding: '20px 16px 18px',
      paddingRight: col + 8,
      maxWidth: '100%',
      boxSizing: 'border-box'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, live && /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--live)',
      display: 'block',
      marginBottom: 7
    }
  }, "Live now"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: '500 var(--size-masthead)/var(--leading-display) var(--font-display)',
      color: 'var(--ink)',
      letterSpacing: 'var(--tracking-display)',
      overflowWrap: 'break-word',
      textWrap: 'balance',
      textShadow: '0 1px 14px rgba(11,15,26,.65)'
    }
  }, greeting), line && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: '7px 0 0',
      font: '400 var(--size-label)/1.5 var(--font-body)',
      color: 'var(--soft)',
      textWrap: 'pretty',
      textShadow: '0 1px 10px rgba(11,15,26,.6)'
    }
  }, line)), children));
}
Object.assign(__ds_scope, { Masthead });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Masthead.jsx", error: String((e && e.message) || e) }); }

// components/brand/SectionHeader.jsx
try { (() => {
/* An eyebrow that opens a section, with an optional action on the right and an
   optional rule beneath. Sentence case in the title, uppercase comes from CSS. */
function SectionHeader({
  eyebrow,
  title,
  action,
  onAction,
  rule = false,
  mark
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8,
      marginBottom: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12,
      minHeight: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0,
      display: 'grid',
      gap: 4
    }
  }, eyebrow && /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, eyebrow), title && /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: '600 var(--size-title)/var(--leading-title) var(--font-display)',
      color: 'var(--ink)'
    }
  }, title)), action && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onAction,
    style: {
      flex: 'none',
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: '6px 2px',
      minHeight: 32,
      color: 'var(--accent)',
      font: '500 var(--size-caption)/1 var(--font-body)',
      cursor: 'pointer'
    }
  }, action)), rule && /*#__PURE__*/React.createElement("div", {
    className: "rule"
  }, mark || '\u263E\uFE0E'));
}
Object.assign(__ds_scope, { SectionHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/SectionHeader.jsx", error: String((e && e.message) || e) }); }

// components/content/Prose.jsx
try { (() => {
/* Long-form: a reading, an article, a licence. EB Garamond at 17/1.65 with a
   38em measure, because these are read on a phone in bed. Glyphs inside prose
   keep their AstroSymbols face; blockquotes take a gilt hairline, not a box. */
function Prose({
  children,
  size = 'prose',
  drop = false
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: 'as-prose' + (drop ? ' as-prose-drop' : ''),
    style: {
      font: `400 ${size === 'small' ? '15px' : 'var(--size-prose)'}/var(--leading-prose) var(--font-display)`,
      color: 'var(--ink)',
      maxWidth: 'var(--measure-prose)'
    }
  }, /*#__PURE__*/React.createElement("style", null, `.as-prose>*{margin:0 0 1em}.as-prose>*:last-child{margin-bottom:0}
.as-prose h2{font:600 22px/1.3 var(--font-display);color:var(--ink);margin:1.6em 0 .5em}
.as-prose h3{font:600 var(--size-heading)/1.35 var(--font-body);color:var(--ink);margin:1.5em 0 .4em}
.as-prose strong{font-weight:600}
.as-prose em{font-style:italic;color:var(--soft)}
.as-prose a{color:var(--accent)}
.as-prose blockquote{margin:1.4em 0;padding-left:16px;border-left:1px solid color-mix(in srgb,var(--gilt) 45%,transparent);color:var(--soft);font-style:italic}
.as-prose ul,.as-prose ol{padding-left:1.3em}
.as-prose li{margin-bottom:.4em}
.as-prose code{font-family:var(--font-body);font-variant-numeric:tabular-nums;letter-spacing:.03em;background:var(--inset);border:1px solid var(--line);border-radius:4px;padding:1px 5px;font-size:.9em}
.as-prose hr{border:0;border-top:1px solid var(--line);margin:2em 0}
.as-prose .t-glyph{font-family:var(--font-glyph)}
.as-prose-drop>p:first-of-type::first-letter{float:left;font-size:3.1em;line-height:.82;padding:.06em .1em 0 0;color:var(--gilt);font-weight:500}`), children);
}
Object.assign(__ds_scope, { Prose });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Prose.jsx", error: String((e && e.message) || e) }); }

// components/data/ChartWheel.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const SIGNS = ['\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D', '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653'];
const SIGN_NAMES = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
const ELEMENT = ['fire', 'earth', 'air', 'water'];
const ASPECT_COLOR = {
  conjunction: 'var(--gilt)',
  opposition: 'var(--rose)',
  trine: 'var(--accent)',
  square: 'var(--rose)',
  sextile: 'var(--accent)'
};
const ASPECT_DASH = {
  conjunction: '',
  opposition: '',
  trine: '',
  square: '4 3',
  sextile: '2 4'
};

/* The wheel. The thing worth screenshotting, and the only drawing in the app the
   agent is allowed to make — it is an instrument, not artwork.
   mode="transit" one instant · mode="period" movement across a span, with the
   Moon's phase ring on the outside.
   ⚠ With no birth time the angles are undefined: pass housesKnown={false} and the
   wheel drops the house ring and the ASC/MC marks rather than guessing them. */
function ChartWheel({
  mode = 'transit',
  size = 320,
  bodies = [],
  aspects = [],
  cusps,
  asc = 0,
  mc,
  housesKnown = true,
  phases = [],
  span,
  label = 'Chart wheel'
}) {
  const cx = size / 2,
    cy = size / 2;
  const R = size / 2 - 1;
  const rSignOut = R,
    rSignIn = R - size * 0.088;
  const rTick = rSignIn - size * 0.012;
  const rHouse = housesKnown ? rSignIn - size * 0.115 : rSignIn - size * 0.05;
  const rBody = rSignIn - size * 0.052;
  const rLeader = rHouse + size * 0.006;
  const rot = housesKnown ? asc : 0;
  const pt = (lon, r) => {
    const a = (180 + (lon - rot)) * Math.PI / 180;
    return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  };
  const ring = (r0, r1, from, to) => {
    const [x0, y0] = pt(from, r1),
      [x1, y1] = pt(to, r1);
    const [x2, y2] = pt(to, r0),
      [x3, y3] = pt(from, r0);
    const big = (to - from + 360) % 360 > 180 ? 1 : 0;
    return `M${x0} ${y0}A${r1} ${r1} 0 ${big} 0 ${x1} ${y1}L${x2} ${y2}A${r0} ${r0} 0 ${big} 1 ${x3} ${y3}Z`;
  };
  /* de-collide body glyphs: nudge apart along the ring */
  const placed = [];
  const sorted = [...bodies].sort((a, b) => a.lon - b.lon);
  sorted.forEach(b => {
    let l = b.lon;
    while (placed.some(p => Math.abs((l - p.lon + 540) % 360 - 180) > 180 - 7)) l += 0.6;
    placed.push({
      ...b,
      lon: b.lon,
      slot: l
    });
  });
  return /*#__PURE__*/React.createElement("svg", {
    viewBox: `0 0 ${size} ${size}`,
    width: "100%",
    role: "img",
    "aria-label": label,
    style: {
      display: 'block',
      maxWidth: size,
      margin: '0 auto',
      overflow: 'visible'
    }
  }, /*#__PURE__*/React.createElement("circle", {
    cx: cx,
    cy: cy,
    r: R,
    fill: "var(--inset)"
  }), SIGNS.map((g, i) => {
    const from = i * 30,
      to = from + 30;
    const [gx, gy] = pt(from + 15, (rSignOut + rSignIn) / 2);
    return /*#__PURE__*/React.createElement("g", {
      key: i
    }, /*#__PURE__*/React.createElement("path", {
      d: ring(rSignIn, rSignOut, from, to),
      fill: i % 2 ? 'rgba(201,161,91,.055)' : 'rgba(143,190,232,.035)'
    }), /*#__PURE__*/React.createElement("line", _extends({}, lineProps(pt(from, rSignIn), pt(from, rSignOut)), {
      stroke: "var(--gilt-dim)",
      strokeWidth: "1"
    })), /*#__PURE__*/React.createElement("text", {
      x: gx,
      y: gy,
      fill: "var(--gilt)",
      fontFamily: "AstroSymbols, 'EB Garamond', serif",
      fontSize: size * 0.05,
      textAnchor: "middle",
      dominantBaseline: "central"
    }, g));
  }), /*#__PURE__*/React.createElement("circle", {
    cx: cx,
    cy: cy,
    r: rSignOut,
    fill: "none",
    stroke: "var(--gilt-dim)",
    strokeWidth: "1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: cx,
    cy: cy,
    r: rSignIn,
    fill: "none",
    stroke: "var(--gilt-dim)",
    strokeWidth: "1"
  }), Array.from({
    length: 72
  }, (_, i) => i * 5).map(d => {
    const long = d % 10 === 0,
      [a, b] = [pt(d, rSignIn), pt(d, rSignIn - (long ? size * 0.022 : size * 0.012))];
    return /*#__PURE__*/React.createElement("line", _extends({
      key: d
    }, lineProps(a, b), {
      stroke: "var(--line-strong)",
      strokeWidth: long ? 1 : 0.6,
      opacity: long ? .9 : .55
    }));
  }), housesKnown && cusps && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("circle", {
    cx: cx,
    cy: cy,
    r: rHouse,
    fill: "none",
    stroke: "var(--line)",
    strokeWidth: "1"
  }), cusps.map((c, i) => {
    const angle = i === 0 || i === 9;
    const [p0, p1] = [pt(c, rHouse), pt(c, rSignIn)];
    const [tx, ty] = pt(c + halfHouse(cusps, i), rHouse + size * 0.028);
    return /*#__PURE__*/React.createElement("g", {
      key: i
    }, /*#__PURE__*/React.createElement("line", _extends({}, lineProps(p0, p1), {
      stroke: angle ? 'var(--soft)' : 'var(--line-strong)',
      strokeWidth: angle ? 1.4 : 0.8,
      strokeDasharray: angle ? '' : '3 3'
    })), /*#__PURE__*/React.createElement("text", {
      x: tx,
      y: ty,
      fill: "var(--faint)",
      fontFamily: "Commissioner, sans-serif",
      fontSize: size * 0.032,
      textAnchor: "middle",
      dominantBaseline: "central"
    }, i + 1));
  }), [['ASC', asc], ['MC', mc]].filter(a => a[1] != null).map(([nm, lon]) => {
    const [x, y] = pt(lon, rSignOut + size * 0.035);
    return /*#__PURE__*/React.createElement("text", {
      key: nm,
      x: x,
      y: y,
      fill: "var(--soft)",
      fontFamily: "Commissioner, sans-serif",
      fontSize: size * 0.032,
      fontWeight: "600",
      letterSpacing: "1",
      textAnchor: "middle",
      dominantBaseline: "central"
    }, nm);
  })), mode === 'period' && phases.map((p, i) => {
    const [x, y] = pt(p.lon, rSignOut + size * 0.045),
      r = size * 0.017;
    return /*#__PURE__*/React.createElement("g", {
      key: i
    }, /*#__PURE__*/React.createElement("circle", {
      cx: x,
      cy: y,
      r: r,
      fill: "var(--inset)",
      stroke: "var(--gilt-dim)",
      strokeWidth: "0.8"
    }), /*#__PURE__*/React.createElement("path", {
      d: phasePath(x, y, r, p.phase),
      fill: "var(--gilt-bright)"
    }));
  }), /*#__PURE__*/React.createElement("circle", {
    cx: cx,
    cy: cy,
    r: rHouse,
    fill: "rgba(13,18,32,.55)"
  }), aspects.map((a, i) => {
    const [x0, y0] = pt(a.from, rHouse - 1),
      [x1, y1] = pt(a.to, rHouse - 1);
    return /*#__PURE__*/React.createElement("line", {
      key: i,
      x1: x0,
      y1: y0,
      x2: x1,
      y2: y1,
      stroke: ASPECT_COLOR[a.type] || 'var(--line-strong)',
      strokeWidth: a.type === 'conjunction' ? 1.2 : 0.9,
      strokeDasharray: ASPECT_DASH[a.type] || '',
      opacity: a.applying === false ? .4 : .72
    });
  }), placed.map((b, i) => {
    const [gx, gy] = pt(b.slot, rBody);
    const [lx0, ly0] = pt(b.lon, rLeader),
      [lx1, ly1] = pt(b.lon, rLeader + size * 0.018);
    const [dx, dy] = pt(b.slot, rBody - size * 0.048);
    return /*#__PURE__*/React.createElement("g", {
      key: b.name || i
    }, /*#__PURE__*/React.createElement("line", {
      x1: lx0,
      y1: ly0,
      x2: lx1,
      y2: ly1,
      stroke: b.retro ? 'var(--rose)' : 'var(--soft)',
      strokeWidth: "0.9"
    }), /*#__PURE__*/React.createElement("text", {
      x: gx,
      y: gy,
      fill: b.retro ? 'var(--rose)' : 'var(--ink)',
      fontFamily: "AstroSymbols, 'EB Garamond', serif",
      fontSize: size * 0.052,
      textAnchor: "middle",
      dominantBaseline: "central"
    }, b.mark), /*#__PURE__*/React.createElement("text", {
      x: dx,
      y: dy,
      fill: b.retro ? 'var(--rose)' : 'var(--faint)',
      fontFamily: "Commissioner, sans-serif",
      fontSize: size * 0.03,
      textAnchor: "middle",
      dominantBaseline: "central",
      style: {
        fontVariantNumeric: 'tabular-nums'
      }
    }, Math.floor(b.lon % 30), '\u00B0', b.retro ? ' \u211E' : ''));
  }), mode === 'period' && span && /*#__PURE__*/React.createElement("text", {
    x: cx,
    y: cy,
    fill: "var(--faint)",
    fontFamily: "Commissioner, sans-serif",
    fontSize: size * 0.034,
    textAnchor: "middle",
    dominantBaseline: "central"
  }, span));
}
function lineProps([x1, y1], [x2, y2]) {
  return {
    x1,
    y1,
    x2,
    y2
  };
}
function halfHouse(cusps, i) {
  const n = cusps.length;
  return (cusps[(i + 1) % n] - cusps[i] + 360) % 360 / 2;
}
function phasePath(x, y, r, p) {
  const k = Math.cos(2 * Math.PI * p),
    waxing = p < 0.5,
    rx = Math.abs(k) * r;
  const so = waxing ? 1 : 0,
    si = waxing ? k > 0 ? 0 : 1 : k > 0 ? 1 : 0;
  return `M ${x} ${y - r} A ${r} ${r} 0 0 ${so} ${x} ${y + r} A ${rx} ${r} 0 0 ${si} ${x} ${y - r} Z`;
}
Object.assign(__ds_scope, { SIGNS, SIGN_NAMES, ChartWheel });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/ChartWheel.jsx", error: String((e && e.message) || e) }); }

// components/data/CodeBlock.jsx
try { (() => {
/* Monospace-ish block: isopsephy tables, offer codes, the wheel's SVG source.
   The app ships no mono face, so this is Commissioner locked to tabular figures
   with letter-spacing — close enough to read as data, and free. */
function CodeBlock({
  children,
  label,
  copyable = false,
  onCopy,
  wrap = false,
  align = 'left'
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "card-inset",
    style: {
      overflow: 'hidden'
    }
  }, label && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '8px 12px',
      borderBottom: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, label), copyable && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onCopy,
    style: {
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: 4,
      color: 'var(--accent)',
      font: '500 var(--size-caption)/1 var(--font-body)',
      cursor: 'pointer'
    }
  }, "Copy")), /*#__PURE__*/React.createElement("pre", {
    style: {
      margin: 0,
      padding: '12px',
      overflowX: 'hidden',
      textAlign: align,
      font: '400 var(--size-data-dense)/1.7 var(--font-body)',
      fontVariantNumeric: 'tabular-nums lining-nums',
      letterSpacing: '.04em',
      color: 'var(--ink)',
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-word'
    }
  }, children));
}
Object.assign(__ds_scope, { CodeBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/CodeBlock.jsx", error: String((e && e.message) || e) }); }

// components/data/DataRow.jsx
try { (() => {
/* A label and a value, joined by an almanac dotted leader. Used wherever the app
   states a fact: chart data, place, provenance, a licence version. */
function DataRow({
  label,
  value,
  mark,
  leader = true,
  mono = true,
  tone = 'ink',
  small = false
}) {
  const colors = {
    ink: 'var(--ink)',
    soft: 'var(--soft)',
    faint: 'var(--faint)',
    rose: 'var(--rose)',
    accent: 'var(--accent)',
    gilt: 'var(--gilt)'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 8,
      minHeight: small ? 24 : 30
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 'none',
      font: `400 ${small ? 'var(--size-caption)' : 'var(--size-label)'}/1.4 var(--font-body)`,
      color: 'var(--faint)',
      display: 'inline-flex',
      alignItems: 'baseline',
      gap: 5
    }
  }, mark && /*#__PURE__*/React.createElement("span", {
    className: "t-glyph",
    style: {
      fontSize: 13,
      color: 'var(--gilt)'
    },
    "aria-hidden": "true"
  }, mark), label), leader && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      flex: 1,
      minWidth: 12,
      alignSelf: 'center',
      height: 1,
      marginTop: 2,
      background: 'repeating-linear-gradient(90deg,var(--line) 0 1px,transparent 1px 5px)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: mono ? 't-tabular' : undefined,
    style: {
      flex: 'none',
      textAlign: 'right',
      font: `${small ? 400 : 500} ${small ? 'var(--size-caption)' : 'var(--size-data)'}/1.4 var(--font-body)`,
      color: colors[tone] || tone,
      maxWidth: '62%',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, value));
}
Object.assign(__ds_scope, { DataRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/DataRow.jsx", error: String((e && e.message) || e) }); }

// components/data/DataTable.jsx
try { (() => {
/* A reference table. ⚠ Dense on purpose — a practitioner reading a month wants
   the month on one screen, so rows are 30px, figures are 13px tabular, and the
   only padding is what keeps the columns apart.
   Retrograde is ℞ AND a rose tint; today is a wash AND a rule AND the word.
   Columns: {key,label,mark,align,width,numeric}. */
function DataTable({
  columns,
  rows,
  caption,
  stickyHead = true,
  zebra = false,
  onRowClick,
  emptyLabel = '—'
}) {
  /* ⚠ The table FITS. A reference table that scrolls sideways is a table a
     practitioner cannot read at a glance, so the columns share the width and the
     figures get tighter instead. If it will not fit, cut a column — never scroll. */
  const head = {
    position: stickyHead ? 'sticky' : 'static',
    top: 0,
    zIndex: 2,
    background: 'var(--inset)',
    padding: '7px 4px',
    borderBottom: '1px solid var(--line-strong)',
    textAlign: 'left',
    font: '600 9px/1.15 var(--font-body)',
    letterSpacing: '.08em',
    textTransform: 'uppercase',
    color: 'var(--faint)',
    overflow: 'hidden',
    verticalAlign: 'bottom'
  };
  return /*#__PURE__*/React.createElement("div", {
    className: "card-inset",
    style: {
      overflow: 'hidden',
      maxWidth: '100%'
    }
  }, /*#__PURE__*/React.createElement("table", {
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      tableLayout: 'fixed'
    }
  }, caption && /*#__PURE__*/React.createElement("caption", {
    style: {
      captionSide: 'top',
      textAlign: 'left',
      padding: '8px 10px 6px',
      font: '400 var(--size-caption)/1.5 var(--font-body)',
      color: 'var(--faint)'
    }
  }, caption), /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, columns.map(c => /*#__PURE__*/React.createElement("th", {
    key: c.key,
    scope: "col",
    style: {
      ...head,
      textAlign: c.align || (c.numeric ? 'right' : 'left'),
      width: c.width
    }
  }, c.mark ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      gap: 2,
      justifyItems: c.numeric ? 'end' : 'start'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-glyph",
    style: {
      fontSize: 13,
      color: 'var(--gilt)',
      letterSpacing: 0
    },
    "aria-hidden": "true"
  }, c.mark), /*#__PURE__*/React.createElement("span", null, c.label)) : c.label)))), /*#__PURE__*/React.createElement("tbody", null, rows.map((r, ri) => /*#__PURE__*/React.createElement("tr", {
    key: r.id || ri,
    onClick: onRowClick ? () => onRowClick(r) : undefined,
    style: {
      background: r.today ? 'var(--accent-wash)' : zebra && ri % 2 ? 'rgba(255,255,255,.015)' : 'transparent',
      cursor: onRowClick ? 'pointer' : 'default'
    }
  }, columns.map((c, ci) => {
    const cell = r[c.key];
    const v = cell && typeof cell === 'object' && !React.isValidElement(cell) ? cell : {
      value: cell
    };
    return /*#__PURE__*/React.createElement("td", {
      key: c.key,
      style: {
        padding: '6px 4px',
        borderBottom: '1px solid var(--line)',
        overflow: 'hidden',
        textAlign: c.align || (c.numeric ? 'right' : 'left'),
        font: `${v.strong || r.today && ci === 0 ? 600 : 400} var(--size-data-dense)/1.35 var(--font-body)`,
        fontVariantNumeric: c.numeric !== false ? 'tabular-nums lining-nums' : 'normal',
        color: v.retro ? 'var(--rose)' : v.muted ? 'var(--faint)' : 'var(--ink)',
        whiteSpace: 'nowrap',
        textOverflow: 'clip'
      }
    }, v.value == null || v.value === '' ? /*#__PURE__*/React.createElement("span", {
      style: {
        color: 'var(--faint)'
      }
    }, emptyLabel) : v.value, v.retro && /*#__PURE__*/React.createElement("span", {
      className: "t-glyph",
      style: {
        marginLeft: 3,
        fontSize: 12
      },
      title: "retrograde"
    }, '\u211E\uFE0E'), r.today && ci === 0 && /*#__PURE__*/React.createElement("span", {
      style: {
        marginLeft: 4,
        font: '600 8px/1 var(--font-body)',
        letterSpacing: '.06em',
        textTransform: 'uppercase',
        color: 'var(--accent)'
      }
    }, "now"));
  }))))));
}
Object.assign(__ds_scope, { DataTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/DataTable.jsx", error: String((e && e.message) || e) }); }

// components/feedback/EmptyState.jsx
try { (() => {
/* An authored empty state. Quiet and honest — never a shrug, never a fake.
   ⚠ The drawing is optional and its absence is designed: with no art the mark
   ring holds the space at the same height, so the screen never reflows when
   her artwork lands. */
function EmptyState({
  mark = '\u263E',
  art,
  artAlt = '',
  title,
  body,
  action,
  secondary,
  compact = false
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      justifyItems: 'center',
      gap: 14,
      textAlign: 'center',
      padding: compact ? '28px 20px' : '48px 24px',
      maxWidth: '38ch',
      margin: '0 auto'
    }
  }, art ? /*#__PURE__*/React.createElement("img", {
    src: art,
    alt: artAlt,
    style: {
      width: compact ? 96 : 148,
      height: 'auto',
      opacity: .95
    }
  }) : /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "scatter-faint scatter",
    style: {
      width: compact ? 56 : 72,
      height: compact ? 56 : 72,
      borderRadius: 'var(--radius-full)',
      display: 'grid',
      placeItems: 'center',
      border: '1px solid color-mix(in srgb,var(--gilt) 34%,transparent)',
      background: 'var(--inset)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-glyph",
    style: {
      fontSize: compact ? 22 : 28,
      color: 'var(--gilt)'
    }
  }, mark, '\uFE0E')), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 7
    }
  }, title && /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: '500 var(--size-title)/1.25 var(--font-display)',
      color: 'var(--ink)',
      textWrap: 'balance'
    }
  }, title), body && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--size-label)/1.55 var(--font-body)',
      color: 'var(--faint)',
      textWrap: 'pretty'
    }
  }, body)), (action || secondary) && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8,
      justifyItems: 'center',
      marginTop: 2
    }
  }, action, secondary));
}
Object.assign(__ds_scope, { EmptyState });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/EmptyState.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Progress.jsx
try { (() => {
/* Three shapes of waiting.
   bar        determinate — a pack downloading, a chart casting
   ring       indeterminate, inline — an instrument computing
   refresh    the pull-to-refresh puck: a gilt arc that turns, because the sky
              turning is the app's own idiom
   skeleton   the shape of the thing that is coming — never a grey box with no
              shape; the reading card's skeleton is a reading card. */
function Progress({
  kind = 'ring',
  value,
  size = 22,
  label = 'Working'
}) {
  if (kind === 'bar') return /*#__PURE__*/React.createElement("div", {
    role: "progressbar",
    "aria-valuenow": value,
    "aria-valuemin": 0,
    "aria-valuemax": 100,
    "aria-label": label,
    style: {
      height: 4,
      borderRadius: 99,
      background: 'var(--inset)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      height: '100%',
      width: (value ?? 0) + '%',
      background: 'var(--accent)',
      transition: 'width var(--dur-2) var(--ease-out)'
    }
  }));
  if (kind === 'refresh') return /*#__PURE__*/React.createElement("div", {
    role: "status",
    "aria-label": label,
    style: {
      display: 'grid',
      placeItems: 'center',
      padding: '10px 0'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 30,
      height: 30,
      borderRadius: 99,
      border: '2px solid var(--line)',
      borderTopColor: 'var(--gilt)',
      animation: 'as-spin 900ms linear infinite'
    }
  }), /*#__PURE__*/React.createElement("style", null, '@keyframes as-spin{to{transform:rotate(360deg)}}'));
  if (kind === 'skeleton') return /*#__PURE__*/React.createElement(Skeleton, null);
  return /*#__PURE__*/React.createElement("span", {
    role: "status",
    "aria-label": label,
    style: {
      display: 'inline-block',
      width: size,
      height: size,
      borderRadius: 99,
      border: '2px solid var(--line)',
      borderTopColor: 'var(--accent)',
      animation: 'as-spin 700ms linear infinite'
    }
  }, /*#__PURE__*/React.createElement("style", null, '@keyframes as-spin{to{transform:rotate(360deg)}}'));
}
function Skeleton({
  lines = 3,
  title = true,
  height
}) {
  return /*#__PURE__*/React.createElement("div", {
    "aria-hidden": "true",
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("style", null, '@keyframes as-shim{0%,100%{opacity:.5}50%{opacity:.85}}'), title && /*#__PURE__*/React.createElement(Bar, {
    w: "62%",
    h: 16
  }), height ? /*#__PURE__*/React.createElement(Bar, {
    w: "100%",
    h: height
  }) : Array.from({
    length: lines
  }, (_, i) => /*#__PURE__*/React.createElement(Bar, {
    key: i,
    w: i === lines - 1 ? '48%' : '100%',
    h: 11
  })));
}
function Bar({
  w,
  h
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      width: w,
      height: h,
      borderRadius: 4,
      background: 'var(--veil)',
      animation: 'as-shim 1.6s var(--ease-in-out) infinite'
    }
  });
}
Object.assign(__ds_scope, { Progress, Skeleton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Progress.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Snackbar.jsx
try { (() => {
/* A snackbar: something happened, here is the undo. Sits above the tab bar,
   never over it. One at a time, 4s, and it never carries an error a screen
   should be showing inline. */
function Snackbar({
  open = true,
  children,
  action,
  onAction,
  tone = 'neutral',
  above = true
}) {
  if (!open) return null;
  const fg = tone === 'error' ? 'var(--live)' : tone === 'good' ? 'var(--accent)' : 'var(--ink)';
  return /*#__PURE__*/React.createElement("div", {
    role: "status",
    "aria-live": "polite",
    style: {
      position: 'absolute',
      left: 12,
      right: 12,
      bottom: above ? 'calc(var(--tabbar-h) + 12px)' : 12,
      zIndex: 50,
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      background: 'var(--veil)',
      border: '1px solid var(--line-strong)',
      borderRadius: 'var(--radius-sm)',
      boxShadow: 'var(--shadow-2)',
      padding: '12px 14px',
      animation: 'as-snack var(--dur-2) var(--ease-out)'
    }
  }, /*#__PURE__*/React.createElement("style", null, '@keyframes as-snack{from{transform:translateY(8px);opacity:0}to{transform:none;opacity:1}}'), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      minWidth: 0,
      font: '400 var(--size-label)/1.4 var(--font-body)',
      color: fg,
      textWrap: 'pretty'
    }
  }, children), action && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onAction,
    style: {
      flex: 'none',
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: '4px 2px',
      minHeight: 32,
      color: 'var(--accent)',
      cursor: 'pointer',
      font: '600 var(--size-caption)/1 var(--font-body)',
      textTransform: 'none'
    }
  }, action));
}
Object.assign(__ds_scope, { Snackbar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Snackbar.jsx", error: String((e && e.message) || e) }); }

// components/forms/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
/* The app's button. Filled is the one action a screen is for; outlined is the
   alternative; text is everything else. Destructive is outlined-only — nothing
   irreversible gets a filled button. Press deepens and sinks 1px; it never scales. */
function Button({
  variant = 'filled',
  size = 'md',
  destructive = false,
  disabled = false,
  loading = false,
  full = false,
  external = false,
  iconLeft,
  iconRight,
  href,
  type = 'button',
  onClick,
  children,
  ...rest
}) {
  css('as-btn', `.as-btn{--_bg:var(--accent);--_fg:var(--on-accent);--_bd:transparent;appearance:none;display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:var(--font-body);font-weight:600;border-radius:var(--radius-sm);border:var(--border-w) solid var(--_bd);background:var(--_bg);color:var(--_fg);cursor:pointer;text-decoration:none;line-height:1;white-space:nowrap;position:relative;transition:background var(--dur-1) var(--ease-out),color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),transform var(--dur-1) var(--ease-out)}
.as-btn[data-size=sm]{font-size:var(--size-caption);padding:0 14px;min-height:36px}
.as-btn[data-size=md]{font-size:var(--size-label);padding:0 20px;min-height:48px}
.as-btn[data-size=lg]{font-size:var(--size-body);padding:0 24px;min-height:56px}
.as-btn[data-full=true]{display:flex;width:100%}
.as-btn:active{transform:translateY(1px)}
.as-btn:hover{--_bg:var(--accent-hover)}
.as-btn[data-variant=outlined]{--_bg:transparent;--_fg:var(--accent);--_bd:color-mix(in srgb,var(--accent) 55%,transparent)}
.as-btn[data-variant=outlined]:hover,.as-btn[data-variant=outlined]:active{--_bg:var(--accent-wash);--_bd:var(--accent)}
.as-btn[data-variant=text]{--_bg:transparent;--_fg:var(--accent);--_bd:transparent;padding:0 12px}
.as-btn[data-variant=text]:hover,.as-btn[data-variant=text]:active{--_bg:var(--veil)}
.as-btn[data-destructive=true][data-variant=outlined]{--_fg:var(--live);--_bd:color-mix(in srgb,var(--live) 55%,transparent)}
.as-btn[data-destructive=true][data-variant=outlined]:hover,.as-btn[data-destructive=true][data-variant=outlined]:active{--_bg:var(--live-wash);--_bd:var(--live)}
.as-btn[data-destructive=true][data-variant=text]{--_fg:var(--live)}
.as-btn[data-destructive=true][data-variant=filled]{--_bg:var(--live);--_fg:#2A0F16}
.as-btn[disabled],.as-btn[data-disabled=true]{opacity:.38;cursor:not-allowed;pointer-events:none}
.as-btn[data-loading=true]>*{visibility:hidden}
.as-btn[data-loading=true]::after{content:"";visibility:visible;position:absolute;inset:0;margin:auto;width:16px;height:16px;border-radius:99px;border:2px solid color-mix(in srgb,var(--_fg) 28%,transparent);border-top-color:var(--_fg);animation:as-spin .7s linear infinite}
@keyframes as-spin{to{transform:rotate(360deg)}}`);
  const Tag = href && !disabled ? 'a' : 'button';
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: "as-btn",
    "data-variant": variant,
    "data-size": size,
    "data-full": full || undefined,
    "data-destructive": destructive || undefined,
    "data-loading": loading || undefined,
    "data-disabled": disabled || undefined,
    href: href,
    target: external ? '_blank' : undefined,
    rel: external ? 'noreferrer' : undefined,
    type: Tag === 'button' ? type : undefined,
    disabled: Tag === 'button' ? disabled || loading : undefined,
    "aria-busy": loading || undefined,
    onClick: onClick
  }, rest), iconLeft, /*#__PURE__*/React.createElement("span", null, children), iconRight, external && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      opacity: .7,
      fontSize: '0.85em'
    }
  }, "\u2197"));
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Button.jsx", error: String((e && e.message) || e) }); }

// components/forms/Chip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
/* Chips. Three kinds and they do not mix on one row:
   choice  — pick one of a set (sign, house system)
   filter  — pick any number (feed filters); selected carries a tick, not just a tint
   meta    — not interactive; a fact with a size on it (language packs: "Greek · 2.1 MB") */
function Chip({
  kind = 'choice',
  selected = false,
  disabled = false,
  leading,
  trailing,
  meta,
  onClick,
  children,
  ...rest
}) {
  css('as-chip', `.as-chip{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:0 12px;border-radius:var(--radius-sm);border:var(--border-w) solid var(--line);background:transparent;color:var(--soft);font:500 var(--size-caption)/1 var(--font-body);cursor:pointer;white-space:nowrap;transition:background var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),color var(--dur-1) var(--ease-out)}
.as-chip:hover{border-color:var(--line-strong);color:var(--ink)}
.as-chip:active{background:var(--veil)}
.as-chip[data-selected=true]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 55%,transparent);color:var(--accent)}
.as-chip[data-kind=meta]{cursor:default;background:var(--inset);color:var(--faint)}
.as-chip[data-kind=meta]:hover{border-color:var(--line);color:var(--faint)}
.as-chip[disabled]{opacity:.38;cursor:not-allowed;pointer-events:none}
.as-chip .as-chip-meta{font-variant-numeric:tabular-nums;color:var(--faint);font-weight:400}
.as-chip[data-selected=true] .as-chip-meta{color:color-mix(in srgb,var(--accent) 75%,var(--faint))}
.as-chip .as-chip-tick{font:600 12px/1 var(--font-body)}`);
  const interactive = kind !== 'meta';
  return /*#__PURE__*/React.createElement("button", _extends({
    className: "as-chip",
    "data-kind": kind,
    "data-selected": selected || undefined,
    type: "button",
    disabled: disabled || !interactive,
    "aria-pressed": interactive ? selected : undefined,
    onClick: onClick
  }, rest), kind === 'filter' && selected && /*#__PURE__*/React.createElement("span", {
    className: "as-chip-tick",
    "aria-hidden": "true"
  }, "\u2713"), leading, /*#__PURE__*/React.createElement("span", null, children), meta && /*#__PURE__*/React.createElement("span", {
    className: "as-chip-meta"
  }, meta), trailing);
}
Object.assign(__ds_scope, { Chip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Chip.jsx", error: String((e && e.message) || e) }); }

// components/forms/ChoiceRow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
/* One row of a choice: a radio (pick one — the sunrise convention) or a checkbox
   (a consent). Both carry an optional `rule` line, because the app's disagreement
   controls are never bare labels: each option states the rule it applies.
   Consents are never pre-ticked and never bundled — one row, one decision. */
function ChoiceRow({
  type = 'radio',
  label,
  rule,
  checked = false,
  disabled = false,
  name,
  value,
  onChange,
  id,
  ...rest
}) {
  css('as-choice', `.as-choice{display:flex;gap:14px;width:100%;min-height:var(--tap-comfort);padding:12px 0;background:none;border:0;text-align:left;cursor:pointer;color:inherit;align-items:flex-start}
.as-choice:active{background:var(--veil)}
.as-choice-mark{flex:none;width:22px;height:22px;margin-top:1px;border:1.5px solid var(--line-strong);background:var(--inset);display:grid;place-items:center;transition:border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.as-choice[data-type=radio] .as-choice-mark{border-radius:99px}
.as-choice[data-type=checkbox] .as-choice-mark{border-radius:5px}
.as-choice-mark i{opacity:0;transition:opacity var(--dur-1) var(--ease-out);font-style:normal}
.as-choice[data-type=radio] .as-choice-mark i{width:10px;height:10px;border-radius:99px;background:var(--on-accent)}
.as-choice[data-type=checkbox] .as-choice-mark i{font:700 13px/1 var(--font-body);color:var(--on-accent)}
.as-choice[data-checked=true] .as-choice-mark{background:var(--accent);border-color:var(--accent)}
.as-choice[data-checked=true] .as-choice-mark i{opacity:1}
.as-choice-txt{flex:1;min-width:0;display:grid;gap:4px}
.as-choice-lab{font:400 var(--size-body)/1.35 var(--font-body);color:var(--ink)}
.as-choice[data-checked=true] .as-choice-lab{font-weight:500}
.as-choice-rule{font:400 var(--size-caption)/1.5 var(--font-body);color:var(--faint)}
.as-choice[disabled]{opacity:.38;cursor:not-allowed}`);
  const uid = id || React.useId();
  return /*#__PURE__*/React.createElement("button", _extends({
    className: "as-choice",
    "data-type": type,
    "data-checked": checked || undefined,
    role: type === 'radio' ? 'radio' : 'checkbox',
    "aria-checked": checked,
    type: "button",
    id: uid,
    disabled: disabled,
    onClick: () => onChange && onChange(type === 'radio' ? value : !checked)
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "as-choice-mark",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("i", null, type === 'checkbox' ? '✓' : '')), /*#__PURE__*/React.createElement("span", {
    className: "as-choice-txt"
  }, /*#__PURE__*/React.createElement("span", {
    className: "as-choice-lab"
  }, label), rule && /*#__PURE__*/React.createElement("span", {
    className: "as-choice-rule"
  }, rule)));
}
Object.assign(__ds_scope, { ChoiceRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/ChoiceRow.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
/* A settings switch on its own row. The whole row is the target (56px), the
   switch is the affordance. State is carried by position AND fill AND the
   knob's tick, so it survives a monochrome screen. */
function Switch({
  label,
  description,
  checked = false,
  disabled = false,
  onChange,
  id,
  ...rest
}) {
  css('as-switch', `.as-switch{display:flex;align-items:center;gap:16px;width:100%;min-height:var(--tap-comfort);padding:10px 0;background:none;border:0;text-align:left;cursor:pointer;color:inherit}
.as-switch:active{background:var(--veil)}
.as-switch-txt{flex:1;min-width:0;display:grid;gap:3px}
.as-switch-lab{font:400 var(--size-body)/1.35 var(--font-body);color:var(--ink)}
.as-switch-desc{font:400 var(--size-caption)/1.4 var(--font-body);color:var(--faint)}
.as-switch-track{flex:none;width:48px;height:28px;border-radius:99px;background:var(--inset);border:1.5px solid var(--line-strong);position:relative;transition:background var(--dur-2) var(--ease-out),border-color var(--dur-2) var(--ease-out)}
.as-switch-knob{position:absolute;top:3px;left:3px;width:19px;height:19px;border-radius:99px;background:var(--faint);display:grid;place-items:center;font:700 11px/1 var(--font-body);color:var(--inset);transition:transform var(--dur-2) var(--ease-out),background var(--dur-2) var(--ease-out),width var(--dur-2) var(--ease-out)}
.as-switch[data-checked=true] .as-switch-track{background:var(--accent);border-color:var(--accent)}
.as-switch[data-checked=true] .as-switch-knob{transform:translateX(20px);background:var(--on-accent)}
.as-switch[disabled]{opacity:.38;cursor:not-allowed}`);
  const uid = id || React.useId();
  return /*#__PURE__*/React.createElement("button", _extends({
    className: "as-switch",
    role: "switch",
    "aria-checked": checked,
    type: "button",
    "data-checked": checked || undefined,
    disabled: disabled,
    id: uid,
    onClick: () => onChange && onChange(!checked)
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "as-switch-txt"
  }, /*#__PURE__*/React.createElement("span", {
    className: "as-switch-lab"
  }, label), description && /*#__PURE__*/React.createElement("span", {
    className: "as-switch-desc"
  }, description)), /*#__PURE__*/React.createElement("span", {
    className: "as-switch-track",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("span", {
    className: "as-switch-knob"
  }, checked ? '✓' : '')));
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/forms/TextField.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
/* A text field. Inset well, hairline, label above — not a floating label: birth
   data and a 2,000-word reading both go in here and the label must stay put.
   An error is a message AND a colour AND a mark; never colour alone. */
function TextField({
  label,
  value,
  defaultValue,
  placeholder,
  helper,
  error,
  multiline = false,
  rows = 4,
  disabled = false,
  required = false,
  type = 'text',
  suffix,
  prefix,
  mono = false,
  maxLength,
  counter = false,
  onChange,
  id,
  ...rest
}) {
  css('as-field', `.as-field{display:grid;gap:6px}
.as-field-lab{font:600 var(--size-caption)/1.3 var(--font-body);color:var(--soft);display:flex;gap:5px;align-items:baseline}
.as-field-lab i{font-style:normal;color:var(--rose)}
.as-field-box{display:flex;align-items:center;gap:8px;background:var(--inset);border:var(--border-w) solid var(--line);border-radius:var(--radius-sm);padding:0 12px;min-height:48px;transition:border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.as-field-box:focus-within{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.as-field-box[data-multiline=true]{padding:10px 12px;align-items:flex-start}
.as-field-box[data-error=true]{border-color:var(--live)}
.as-field-box[data-error=true]:focus-within{box-shadow:0 0 0 1px var(--live)}
.as-field-box[data-disabled=true]{opacity:.45}
.as-field input,.as-field textarea{flex:1;min-width:0;appearance:none;background:none;border:0;outline:0;color:var(--ink);font:400 var(--size-body)/1.5 var(--font-body);padding:0;resize:vertical}
.as-field[data-mono=true] input,.as-field[data-mono=true] textarea{font-variant-numeric:tabular-nums lining-nums;letter-spacing:.02em}
.as-field input::placeholder,.as-field textarea::placeholder{color:var(--faint)}
.as-field-aff{font:400 var(--size-caption) var(--font-body);color:var(--faint);flex:none}
.as-field-help{font:400 var(--size-caption)/1.45 var(--font-body);color:var(--faint);display:flex;gap:6px;justify-content:space-between}
.as-field-help[data-error=true]{color:var(--live)}
.as-field-help b{font-weight:600}`);
  const uid = id || React.useId();
  const Input = multiline ? 'textarea' : 'input';
  return /*#__PURE__*/React.createElement("div", {
    className: "as-field",
    "data-mono": mono || undefined
  }, label && /*#__PURE__*/React.createElement("label", {
    className: "as-field-lab",
    htmlFor: uid
  }, label, required && /*#__PURE__*/React.createElement("i", {
    "aria-hidden": "true"
  }, "required")), /*#__PURE__*/React.createElement("div", {
    className: "as-field-box",
    "data-multiline": multiline || undefined,
    "data-error": !!error || undefined,
    "data-disabled": disabled || undefined
  }, prefix && /*#__PURE__*/React.createElement("span", {
    className: "as-field-aff"
  }, prefix), /*#__PURE__*/React.createElement(Input, _extends({
    id: uid,
    type: multiline ? undefined : type,
    rows: multiline ? rows : undefined,
    value: value,
    defaultValue: defaultValue,
    placeholder: placeholder,
    disabled: disabled,
    maxLength: maxLength,
    "aria-invalid": !!error || undefined,
    "aria-describedby": helper || error ? uid + '-h' : undefined,
    onChange: onChange
  }, rest)), suffix && /*#__PURE__*/React.createElement("span", {
    className: "as-field-aff"
  }, suffix)), (helper || error || counter) && /*#__PURE__*/React.createElement("div", {
    className: "as-field-help",
    id: uid + '-h',
    "data-error": !!error || undefined
  }, /*#__PURE__*/React.createElement("span", null, error ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("b", null, "Error \xB7"), " ", error) : helper), counter && maxLength && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular"
  }, String(value || '').length, "/", maxLength)));
}
Object.assign(__ds_scope, { TextField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/TextField.jsx", error: String((e && e.message) || e) }); }

// components/marks/Glyph.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* An astronomical mark, set in the bundled AstroSymbols cut. Type, never emoji:
   every glyph is emitted with U+FE0E so no colour-emoji font can claim it. */
const MARKS = {
  sun: '\u2609',
  moon: '\u263E',
  waxing: '\u263D',
  mercury: '\u263F',
  venus: '\u2640',
  mars: '\u2642',
  jupiter: '\u2643',
  saturn: '\u2644',
  uranus: '\u2645',
  neptune: '\u2646',
  pluto: '\u2647',
  node: '\u260A',
  southnode: '\u260B',
  retrograde: '\u211E',
  degree: '\u00B0',
  arcmin: '\u2032',
  arcsec: '\u2033',
  aries: '\u2648',
  taurus: '\u2649',
  gemini: '\u264A',
  cancer: '\u264B',
  leo: '\u264C',
  virgo: '\u264D',
  libra: '\u264E',
  scorpio: '\u264F',
  sagittarius: '\u2650',
  capricorn: '\u2651',
  aquarius: '\u2652',
  pisces: '\u2653'
};
const SIZES = {
  sm: 13,
  md: 16,
  lg: 22,
  xl: 34
};
function Glyph({
  name,
  char,
  size = 'md',
  tone = 'ink',
  label,
  style,
  ...rest
}) {
  const c = (char || MARKS[name] || '') + '\uFE0E';
  const color = {
    ink: 'var(--ink)',
    soft: 'var(--soft)',
    faint: 'var(--faint)',
    gilt: 'var(--gilt)',
    accent: 'var(--accent)',
    rose: 'var(--rose)',
    hour: 'var(--hour)',
    live: 'var(--live)',
    inherit: 'inherit'
  }[tone] || tone;
  return /*#__PURE__*/React.createElement("span", _extends({
    className: "t-glyph",
    role: label ? 'img' : undefined,
    "aria-label": label,
    "aria-hidden": label ? undefined : 'true',
    style: {
      fontFamily: 'var(--font-glyph)',
      fontSize: (SIZES[size] || size) + 'px',
      lineHeight: 1,
      color,
      fontVariantEmoji: 'text',
      display: 'inline-block',
      ...style
    }
  }, rest), c);
}
Object.assign(__ds_scope, { MARKS, Glyph });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/marks/Glyph.jsx", error: String((e && e.message) || e) }); }

// components/brand/HourChip.jsx
try { (() => {
const HOUR_RULERS = {
  sun: {
    mark: 'sun',
    name: 'Sun'
  },
  moon: {
    mark: 'moon',
    name: 'Moon'
  },
  mars: {
    mark: 'mars',
    name: 'Mars'
  },
  mercury: {
    mark: 'mercury',
    name: 'Mercury'
  },
  jupiter: {
    mark: 'jupiter',
    name: 'Jupiter'
  },
  venus: {
    mark: 'venus',
    name: 'Venus'
  },
  saturn: {
    mark: 'saturn',
    name: 'Saturn'
  }
};
/* The ruling planetary hour. Computed on device, so it is always there, even
   offline — which is exactly why it is allowed to be the app's one ambient
   signal. It tints itself and the hem above it, and nothing else.
   Always names the planet in words as well as the mark. */
function HourChip({
  ruler = 'sun',
  ends,
  ordinal,
  diurnal = true,
  onClick
}) {
  const r = HOUR_RULERS[ruler] || HOUR_RULERS.sun;
  const Tag = onClick ? 'button' : 'div';
  return /*#__PURE__*/React.createElement(Tag, {
    onClick: onClick,
    type: onClick ? 'button' : undefined,
    "data-hour": ruler,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8,
      minHeight: 36,
      padding: '0 12px',
      borderRadius: 'var(--radius-full)',
      background: 'var(--hour-wash)',
      border: '1px solid color-mix(in srgb,var(--hour) 40%,transparent)',
      color: 'var(--soft)',
      font: '500 var(--size-caption)/1 var(--font-body)',
      cursor: onClick ? 'pointer' : 'default',
      whiteSpace: 'nowrap',
      transition: 'background var(--dur-hour) var(--ease-in-out),border-color var(--dur-hour) var(--ease-in-out)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Glyph, {
    name: r.mark,
    tone: "hour",
    size: "sm"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--hour)',
      fontWeight: 600
    }
  }, "Hour of ", r.name), ordinal != null && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      color: 'var(--faint)'
    }
  }, ordinal, diurnal ? ' of day' : ' of night'), ends && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      color: 'var(--faint)'
    }
  }, "\xB7 until ", ends));
}
Object.assign(__ds_scope, { HOUR_RULERS, HourChip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/HourChip.jsx", error: String((e && e.message) || e) }); }

// components/brand/LiveBanner.jsx
try { (() => {
/* Live is a state the app is in, not a badge on a card.
   live      — the plate warms, the hem goes rose, the dot pulses, the title is the stream's
   offline   — a quiet line with the next stream, if one is known
   unknown   — we could not reach her side. Never says "offline"; never fakes liveness.
   Stamp data-live="true" on the shell to turn the whole app's ornament rose. */
function LiveBanner({
  status = 'offline',
  title,
  game,
  viewers,
  nextStream,
  onOpen,
  compact = false
}) {
  const live = status === 'live';
  const word = live ? 'Live now' : status === 'offline' ? 'Not live' : 'Status unavailable';
  const line = live ? [title, game].filter(Boolean).join(' · ') : status === 'offline' ? nextStream ? 'Next: ' + nextStream : 'Streams are announced on Discord first' : 'Could not reach Twitch — check directly';
  const Tag = onOpen ? 'button' : 'div';
  return /*#__PURE__*/React.createElement(Tag, {
    onClick: onOpen,
    type: onOpen ? 'button' : undefined,
    className: live ? 'hem hem-strong' : 'hem',
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      width: '100%',
      textAlign: 'left',
      cursor: onOpen ? 'pointer' : 'default',
      background: live ? 'linear-gradient(96deg,var(--live-wash) 0%,var(--card) 62%)' : 'var(--card)',
      border: '1px solid ' + (live ? 'color-mix(in srgb,var(--live) 42%,transparent)' : 'var(--line)'),
      borderRadius: 'var(--radius-md)',
      padding: compact ? '10px 14px' : '14px 16px',
      minHeight: 'var(--tap-comfort)',
      color: 'inherit',
      transition: 'background var(--dur-3) var(--ease-in-out),border-color var(--dur-3) var(--ease-in-out)'
    },
    role: "status",
    "aria-live": "polite"
  }, /*#__PURE__*/React.createElement(Dot, {
    status: status
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      minWidth: 0,
      display: 'grid',
      gap: 3
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: live ? 'var(--live)' : 'var(--faint)'
    }
  }, word), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-label)/1.35 var(--font-body)',
      color: live ? 'var(--ink)' : 'var(--soft)',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, line)), live && viewers != null && /*#__PURE__*/React.createElement("span", {
    className: "t-data",
    style: {
      color: 'var(--faint)',
      fontSize: 'var(--size-caption)',
      flex: 'none'
    }
  }, Intl.NumberFormat().format(viewers), /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, " watching")), !live && status === 'unknown' && /*#__PURE__*/React.createElement(__ds_scope.Glyph, {
    name: "moon",
    tone: "faint",
    size: "sm"
  }));
}
function Dot({
  status
}) {
  if (status === 'unknown') return /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      flex: 'none',
      width: 10,
      height: 10,
      borderRadius: 99,
      border: '1.5px dashed var(--faint)'
    }
  });
  if (status === 'offline') return /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      flex: 'none',
      width: 10,
      height: 10,
      borderRadius: 99,
      background: 'var(--faint)',
      opacity: .45
    }
  });
  return /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      flex: 'none',
      width: 10,
      height: 10,
      borderRadius: 99,
      background: 'var(--live)',
      boxShadow: 'var(--glow-live)',
      animation: 'as-live-pulse 2s var(--ease-in-out) infinite'
    }
  }, /*#__PURE__*/React.createElement("style", null, '@keyframes as-live-pulse{0%,100%{opacity:1}50%{opacity:.4}}'));
}
Object.assign(__ds_scope, { LiveBanner });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/LiveBanner.jsx", error: String((e && e.message) || e) }); }

// components/content/ContentCard.jsx
try { (() => {
/* One of her things: a reading or an article. Same card, two kinds.
   ⚠ Missing content is designed: no title falls back to the sign and date
   ("Scorpio · 9 Sep"), no opening line leaves the card at its shorter height
   rather than showing an empty paragraph. Nothing ever renders "Untitled". */
function ContentCard({
  kind = 'reading',
  title,
  sign,
  signMark,
  date,
  excerpt,
  readingTime,
  unread = false,
  onOpen,
  cover,
  coverAlt = ''
}) {
  const heading = title || (sign ? `${sign} · ${date}` : date);
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onOpen,
    className: "card card-tappable",
    style: {
      display: 'grid',
      gridTemplateColumns: cover ? '1fr 72px' : '1fr',
      gap: 14,
      width: '100%',
      textAlign: 'left',
      padding: 14,
      cursor: 'pointer',
      color: 'inherit',
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0,
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 7
    }
  }, signMark && /*#__PURE__*/React.createElement(__ds_scope.Glyph, {
    char: signMark,
    tone: "gilt",
    size: "sm"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, kind === 'reading' ? sign ? sign + ' · reading' : 'Reading' : 'Article'), unread && /*#__PURE__*/React.createElement("span", {
    "aria-label": "unread",
    style: {
      width: 6,
      height: 6,
      borderRadius: 99,
      background: 'var(--accent)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--size-heading)/1.35 var(--font-display)',
      color: 'var(--ink)',
      fontSize: 19,
      display: '-webkit-box',
      WebkitLineClamp: 2,
      WebkitBoxOrient: 'vertical',
      overflow: 'hidden',
      textWrap: 'pretty'
    }
  }, heading), excerpt && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-caption)/1.55 var(--font-body)',
      color: 'var(--faint)',
      display: '-webkit-box',
      WebkitLineClamp: 2,
      WebkitBoxOrient: 'vertical',
      overflow: 'hidden'
    }
  }, excerpt), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      display: 'flex',
      gap: 8,
      marginTop: 2
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-tabular"
  }, date), readingTime && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, "\xB7"), /*#__PURE__*/React.createElement("span", null, readingTime)))), cover && /*#__PURE__*/React.createElement("img", {
    src: cover,
    alt: coverAlt,
    style: {
      width: 72,
      height: 72,
      objectFit: 'cover',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--line)'
    }
  }));
}
Object.assign(__ds_scope, { ContentCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/ContentCard.jsx", error: String((e && e.message) || e) }); }

// components/marks/Icon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* A UI icon. Material Symbols Outlined — the set the Flutter app already uses. */
function Icon({
  name,
  size = 24,
  tone = 'soft',
  fill = 0,
  weight = 400,
  label,
  style,
  ...rest
}) {
  const color = {
    ink: 'var(--ink)',
    soft: 'var(--soft)',
    faint: 'var(--faint)',
    gilt: 'var(--gilt)',
    accent: 'var(--accent)',
    rose: 'var(--rose)',
    live: 'var(--live)',
    hour: 'var(--hour)',
    inherit: 'inherit'
  }[tone] || tone;
  return /*#__PURE__*/React.createElement("span", _extends({
    className: "material-symbols-outlined",
    role: label ? 'img' : undefined,
    "aria-label": label,
    "aria-hidden": label ? undefined : 'true',
    style: {
      fontSize: size + 'px',
      lineHeight: 1,
      color,
      flex: 'none',
      userSelect: 'none',
      fontVariationSettings: `'FILL' ${fill}, 'wght' ${weight}, 'GRAD' 0, 'opsz' ${size}`,
      ...style
    }
  }, rest), name);
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/marks/Icon.jsx", error: String((e && e.message) || e) }); }

// components/content/OfferCard.jsx
try { (() => {
/* An offer: a class, a reading slot, the shop, support.
   ⚠ Nothing takes money inside the app. Every offer leaves for her own checkout
   in a browser, and the card says so on its face — the arrow and the words
   "opens in your browser" are not optional decoration, they are the promise
   that the address bar will say whose it is.
   Members-only offers show the lock and stay tappable: tapping explains. */
function OfferCard({
  title,
  body,
  price,
  cadence,
  membersOnly = false,
  locked = false,
  href,
  onOpen,
  mark = '\u2609',
  soldOut = false
}) {
  return /*#__PURE__*/React.createElement("a", {
    href: locked ? undefined : href,
    target: locked ? undefined : '_blank',
    rel: "noreferrer",
    onClick: onOpen,
    className: "card hem card-tappable",
    style: {
      display: 'grid',
      gap: 10,
      padding: 14,
      textDecoration: 'none',
      color: 'inherit',
      background: 'linear-gradient(168deg,var(--gilt-wash) 0%,var(--card) 58%)',
      border: '1px solid color-mix(in srgb,var(--gilt) 38%,transparent)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      position: 'relative',
      opacity: soldOut ? .6 : 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-glyph",
    "aria-hidden": "true",
    style: {
      fontSize: 14,
      color: 'var(--gilt)'
    }
  }, mark, '\uFE0E'), /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--gilt)'
    }
  }, membersOnly ? 'Members' : 'Offer'), locked && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "lock",
    size: 14,
    tone: "gilt"
  }), soldOut && /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--faint)'
    }
  }, "\xB7 full")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 5
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 19px/1.3 var(--font-display)',
      color: 'var(--ink)',
      textWrap: 'pretty'
    }
  }, title), body && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-caption)/1.55 var(--font-body)',
      color: 'var(--soft)',
      textWrap: 'pretty'
    }
  }, body)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      justifyContent: 'space-between',
      gap: 10,
      borderTop: '1px solid color-mix(in srgb,var(--gilt) 22%,transparent)',
      paddingTop: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '600 var(--size-data)/1 var(--font-body)',
      color: 'var(--gilt)'
    }
  }, price, cadence && /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--faint)',
      fontWeight: 400,
      fontSize: 'var(--size-caption)'
    }
  }, " ", cadence)), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      font: '400 var(--size-caption)/1 var(--font-body)',
      color: 'var(--faint)'
    }
  }, locked ? 'Members only' : 'opens in your browser', !locked && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "open_in_new",
    size: 14,
    tone: "faint"
  }))));
}
Object.assign(__ds_scope, { OfferCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/OfferCard.jsx", error: String((e && e.message) || e) }); }

// components/content/VoteControl.jsx
try { (() => {
/* Up, down, or neither, with the running total between.
   A vote lands by scaling the arrow to 1.18 and back over 240ms and the count
   stepping — no toast, no confirmation. Under reduced-motion the arrow just
   fills. State is fill AND colour AND aria-pressed, never colour alone. */
function VoteControl({
  value = 0,
  mine = 0,
  onVote,
  disabled = false,
  compact = false
}) {
  const btn = dir => {
    const on = mine === dir;
    return /*#__PURE__*/React.createElement("button", {
      type: "button",
      disabled: disabled,
      "aria-pressed": on,
      "aria-label": dir > 0 ? 'Vote up' : 'Vote down',
      onClick: () => onVote && onVote(on ? 0 : dir),
      style: {
        appearance: 'none',
        background: 'none',
        border: 0,
        padding: 2,
        cursor: disabled ? 'not-allowed' : 'pointer',
        lineHeight: 0,
        opacity: disabled ? .38 : 1,
        transition: 'transform var(--dur-2) var(--ease-out)',
        transform: on ? 'scale(1.06)' : 'none'
      }
    }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
      name: dir > 0 ? 'keyboard_arrow_up' : 'keyboard_arrow_down',
      size: compact ? 20 : 24,
      weight: on ? 700 : 400,
      tone: on ? dir > 0 ? 'accent' : 'rose' : 'faint'
    }));
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      justifyItems: 'center',
      gap: 1,
      minWidth: 34,
      flex: 'none'
    }
  }, btn(1), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: `${mine ? 600 : 500} var(--size-caption)/1 var(--font-body)`,
      color: mine > 0 ? 'var(--accent)' : mine < 0 ? 'var(--rose)' : 'var(--soft)'
    }
  }, value), btn(-1));
}
Object.assign(__ds_scope, { VoteControl });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/VoteControl.jsx", error: String((e && e.message) || e) }); }

// components/content/WorkCard.jsx
try { (() => {
/* A community reading in the practice room. Somebody else's work, or your own.
   Own work carries its status: draft, posted, or corrected.
   ⚠ Long content is designed: the title clamps at two lines and the body at
   three; a forty-character name truncates from the middle of the row, not the
   card. Nothing here ever pushes the vote control off screen. */
const STATUS = {
  draft: {
    t: 'Draft',
    c: 'var(--faint)'
  },
  posted: {
    t: 'Posted',
    c: 'var(--accent)'
  },
  corrected: {
    t: 'Corrected',
    c: 'var(--gilt)'
  }
};
function WorkCard({
  title,
  author,
  avatar,
  date,
  excerpt,
  votes = 0,
  myVote = 0,
  comments = 0,
  status,
  mine = false,
  onOpen,
  onVote,
  sign
}) {
  const st = status && STATUS[status];
  return /*#__PURE__*/React.createElement("article", {
    className: "card card-tappable",
    style: {
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      gap: 12,
      padding: 14,
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.VoteControl, {
    value: votes,
    mine: myVote,
    onVote: onVote
  }), /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onOpen,
    style: {
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: 0,
      textAlign: 'left',
      minWidth: 0,
      display: 'grid',
      gap: 6,
      cursor: 'pointer',
      color: 'inherit'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 7,
      minWidth: 0
    }
  }, avatar ? /*#__PURE__*/React.createElement("img", {
    src: avatar,
    alt: "",
    style: {
      width: 18,
      height: 18,
      borderRadius: 99,
      flex: 'none'
    }
  }) : /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: 18,
      height: 18,
      borderRadius: 99,
      flex: 'none',
      background: 'var(--veil)',
      border: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      minWidth: 0,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap',
      color: 'var(--soft)'
    }
  }, mine ? 'You' : author), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    "aria-hidden": "true"
  }, "\xB7"), /*#__PURE__*/React.createElement("span", {
    className: "t-caption t-tabular",
    style: {
      flex: 'none'
    }
  }, date), st && /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 'none',
      font: '600 10px/1 var(--font-body)',
      letterSpacing: '.1em',
      textTransform: 'uppercase',
      color: st.c
    }
  }, st.t)), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 18px/1.3 var(--font-display)',
      color: 'var(--ink)',
      display: '-webkit-box',
      WebkitLineClamp: 2,
      WebkitBoxOrient: 'vertical',
      overflow: 'hidden',
      textWrap: 'pretty'
    }
  }, title), excerpt && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-caption)/1.55 var(--font-body)',
      color: 'var(--faint)',
      display: '-webkit-box',
      WebkitLineClamp: 3,
      WebkitBoxOrient: 'vertical',
      overflow: 'hidden'
    }
  }, excerpt), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      marginTop: 2
    }
  }, sign && /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, sign), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "mode_comment",
    size: 15,
    tone: "faint"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption t-tabular"
  }, comments)))));
}
Object.assign(__ds_scope, { WorkCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/WorkCard.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Banner.jsx
try { (() => {
/* An inline notice pinned under the app bar. Four tones, and the offline one is
   the important one:
   ⚠ offline does NOT mean broken. Every instrument still computes on device.
   The copy says which half is missing, never "no connection". */
const TONES = {
  offline: {
    icon: 'cloud_off',
    fg: 'var(--gilt)',
    bg: 'var(--gilt-wash)',
    bd: 'color-mix(in srgb,var(--gilt) 34%,transparent)'
  },
  error: {
    icon: 'error',
    fg: 'var(--live)',
    bg: 'var(--live-wash)',
    bd: 'color-mix(in srgb,var(--live) 40%,transparent)'
  },
  note: {
    icon: 'info',
    fg: 'var(--accent)',
    bg: 'var(--accent-wash)',
    bd: 'color-mix(in srgb,var(--accent) 34%,transparent)'
  },
  caution: {
    icon: 'priority_high',
    fg: 'var(--rose)',
    bg: 'var(--rose-wash)',
    bd: 'color-mix(in srgb,var(--rose) 38%,transparent)'
  }
};
function Banner({
  tone = 'note',
  title,
  children,
  action,
  onAction,
  onDismiss,
  icon
}) {
  const t = TONES[tone] || TONES.note;
  return /*#__PURE__*/React.createElement("div", {
    role: tone === 'error' ? 'alert' : 'status',
    style: {
      display: 'flex',
      gap: 11,
      alignItems: 'flex-start',
      background: t.bg,
      border: '1px solid ' + t.bd,
      borderRadius: 'var(--radius-md)',
      padding: '11px 13px'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon || t.icon,
    size: 19,
    tone: t.fg,
    style: {
      marginTop: 1
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0,
      display: 'grid',
      gap: 3
    }
  }, title && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--size-label)/1.35 var(--font-body)',
      color: t.fg
    }
  }, title), children && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-caption)/1.5 var(--font-body)',
      color: 'var(--soft)',
      textWrap: 'pretty'
    }
  }, children), action && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onAction,
    style: {
      justifySelf: 'start',
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: '6px 0 2px',
      color: t.fg,
      cursor: 'pointer',
      font: '600 var(--size-caption)/1 var(--font-body)'
    }
  }, action)), onDismiss && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onDismiss,
    "aria-label": "Dismiss",
    style: {
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: 2,
      cursor: 'pointer',
      color: 'var(--faint)',
      lineHeight: 0
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "close",
    size: 17,
    tone: "faint"
  })));
}
Object.assign(__ds_scope, { Banner });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Banner.jsx", error: String((e && e.message) || e) }); }

// components/forms/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
/* A tap target with an icon in it. Always 48px minimum even when the glyph is 20px —
   the ring, not the glyph, is the target. `label` is required: it is the only name
   a screen reader gets. */
function IconButton({
  icon,
  label,
  size = 24,
  variant = 'ghost',
  tone = 'soft',
  selected = false,
  disabled = false,
  badge,
  onClick,
  href,
  ...rest
}) {
  css('as-iconbtn', `.as-iconbtn{appearance:none;display:inline-grid;place-items:center;min-width:var(--tap-min);min-height:var(--tap-min);border-radius:var(--radius-full);border:var(--border-w) solid transparent;background:transparent;cursor:pointer;position:relative;padding:0;transition:background var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out)}
.as-iconbtn:hover,.as-iconbtn:active{background:var(--veil)}
.as-iconbtn[data-variant=outlined]{border-color:var(--line)}
.as-iconbtn[data-variant=outlined]:hover{border-color:var(--line-strong)}
.as-iconbtn[data-variant=filled]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.as-iconbtn[data-selected=true]{background:var(--accent-wash)}
.as-iconbtn[disabled]{opacity:.38;cursor:not-allowed;pointer-events:none}
.as-iconbtn .as-ib-badge{position:absolute;top:6px;right:6px;min-width:16px;height:16px;padding:0 4px;border-radius:99px;background:var(--live);color:#2A0F16;font:600 10px/16px var(--font-body);text-align:center;border:1.5px solid var(--card)}`);
  const Tag = href ? 'a' : 'button';
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: "as-iconbtn",
    "data-variant": variant,
    "data-selected": selected || undefined,
    href: href,
    type: Tag === 'button' ? 'button' : undefined,
    disabled: Tag === 'button' ? disabled : undefined,
    "aria-label": label,
    "aria-pressed": selected || undefined,
    onClick: onClick
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: size,
    tone: selected ? 'accent' : tone
  }), badge != null && /*#__PURE__*/React.createElement("span", {
    className: "as-ib-badge"
  }, badge));
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/brand/AppBar.jsx
try { (() => {
/* The top bar of a pushed or tabbed screen. Title in EB Garamond, because the
   app talks in her voice even in its chrome. The hem sits under it and takes
   the ruling hour's colour — the one place the sky tints the shell. */
function AppBar({
  title,
  subtitle,
  back,
  onBack,
  actions,
  hour = true,
  large = false,
  sticky = true
}) {
  return /*#__PURE__*/React.createElement("header", {
    className: 'hem hem-bottom' + (hour ? ' hem-hour' : ''),
    style: {
      position: sticky ? 'sticky' : 'relative',
      top: 0,
      zIndex: 20,
      background: 'var(--page)',
      display: 'grid',
      gridTemplateColumns: 'auto 1fr auto',
      alignItems: 'center',
      gap: 4,
      padding: '0 6px',
      minHeight: large ? 72 : 'var(--appbar-h)'
    }
  }, back ? /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "arrow_back",
    label: "Back",
    onClick: onBack,
    tone: "ink"
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0,
      padding: back ? '0' : '0 10px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: `${large ? 500 : 600} ${large ? '26px' : '19px'}/1.2 var(--font-display)`,
      color: 'var(--ink)',
      letterSpacing: '-0.01em',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 2,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, subtitle)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center'
    }
  }, actions));
}
Object.assign(__ds_scope, { AppBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/AppBar.jsx", error: String((e && e.message) || e) }); }

// components/marks/MoonDisc.jsx
try { (() => {
/* The drawn moon phase disc. A real drawing, not a glyph — it is correct for any
   fraction of the cycle and it reads at 16px. phase: 0=new, .25=first quarter,
   .5=full, .75=last quarter. Colour is never the only signal: pass `label`. */
function MoonDisc({
  phase = 0.5,
  size = 28,
  label,
  showLabel = false,
  tone = 'gilt'
}) {
  const r = size / 2,
    lit = {
      gilt: 'var(--gilt-bright)',
      ink: 'var(--ink)',
      soft: 'var(--soft)'
    }[tone] || tone;
  const p = (phase % 1 + 1) % 1;
  const k = Math.cos(2 * Math.PI * p); /* terminator half-width, -1..1 */
  const waxing = p < 0.5;
  const rx = Math.abs(k) * r;
  const sweepOuter = waxing ? 1 : 0;
  const sweepInner = waxing ? k > 0 ? 0 : 1 : k > 0 ? 1 : 0;
  const d = `M ${r} 0 A ${r} ${r} 0 0 ${sweepOuter} ${r} ${size} A ${rx} ${r} 0 0 ${sweepInner} ${r} 0 Z`;
  const name = label || phaseName(p);
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("svg", {
    width: size,
    height: size,
    viewBox: `0 0 ${size} ${size}`,
    role: "img",
    "aria-label": name,
    style: {
      flex: 'none',
      display: 'block'
    }
  }, /*#__PURE__*/React.createElement("circle", {
    cx: r,
    cy: r,
    r: r - 0.5,
    fill: "var(--inset)",
    stroke: "var(--line-strong)",
    strokeWidth: "1"
  }), p > 0.02 && p < 0.98 && /*#__PURE__*/React.createElement("path", {
    d: d,
    fill: lit
  }), p >= 0.98 || p <= 0.02 ? null : null, /*#__PURE__*/React.createElement("circle", {
    cx: r,
    cy: r,
    r: r - 0.5,
    fill: "none",
    stroke: "color-mix(in srgb,var(--gilt) 40%,transparent)",
    strokeWidth: "1"
  })), showLabel && /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      color: 'var(--soft)'
    }
  }, name));
}
function phaseName(p) {
  if (p < 0.03 || p > 0.97) return 'New moon';
  if (p < 0.22) return 'Waxing crescent';
  if (p < 0.28) return 'First quarter';
  if (p < 0.47) return 'Waxing gibbous';
  if (p < 0.53) return 'Full moon';
  if (p < 0.72) return 'Waning gibbous';
  if (p < 0.78) return 'Last quarter';
  return 'Waning crescent';
}
Object.assign(__ds_scope, { MoonDisc, phaseName });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/marks/MoonDisc.jsx", error: String((e && e.message) || e) }); }

// components/brand/DayArc.jsx
try { (() => {
/* The day, drawn. Sunrise to sunset as an arc, the Sun where it actually is,
   the night shaded either side, the Moon's phase at the end of it.

   This is Sky's header and it exists for one reason: the app knows what the sky
   is doing, on device, offline, and that is a signal almost no app has. It also
   stops every screen looking like the same stack of cards — Home has the plate,
   Sky has the arc, and neither borrows the other's surface.

   All four times are real inputs; nothing here is decorative. */
function DayArc({
  sunrise = '06:58',
  sunset = '19:51',
  now = '13:42',
  phase = 0.38,
  ruler = 'sun',
  height = 132,
  label
}) {
  const t = s => {
    const [h, m] = s.split(':').map(Number);
    return h * 60 + m;
  };
  const rise = t(sunrise),
    set = t(sunset),
    cur = t(now);
  const day = Math.max(1, set - rise);
  const frac = Math.min(1, Math.max(0, (cur - rise) / day));
  const isDay = cur >= rise && cur <= set;
  const W = 320,
    H = 92,
    pad = 26,
    span = W - pad * 2,
    base = H - 20;
  const peak = 18;
  const x = pad + span * frac;
  const y = base - Math.sin(Math.PI * frac) * (base - peak);
  const path = `M ${pad} ${base} Q ${W / 2} ${peak - (base - peak) * 0.32} ${W - pad} ${base}`;
  return /*#__PURE__*/React.createElement("section", {
    className: "scatter hem hem-hour",
    style: {
      position: 'relative',
      minHeight: height,
      background: 'linear-gradient(180deg,#0B1322 0%,#16203A 52%,#241E2E 100%)',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--line)',
      overflow: 'hidden',
      padding: '12px 0 0'
    }
  }, /*#__PURE__*/React.createElement("svg", {
    viewBox: `0 0 ${W} ${H}`,
    width: "100%",
    role: "img",
    "aria-label": label || `Sunrise ${sunrise}, sunset ${sunset}, now ${now}`,
    style: {
      display: 'block'
    },
    preserveAspectRatio: "none"
  }, /*#__PURE__*/React.createElement("defs", null, /*#__PURE__*/React.createElement("linearGradient", {
    id: "as-arc-h",
    x1: "0",
    x2: "1"
  }, /*#__PURE__*/React.createElement("stop", {
    offset: "0",
    stopColor: "var(--gilt)",
    stopOpacity: "0"
  }), /*#__PURE__*/React.createElement("stop", {
    offset: ".5",
    stopColor: "var(--gilt)",
    stopOpacity: ".55"
  }), /*#__PURE__*/React.createElement("stop", {
    offset: "1",
    stopColor: "var(--gilt)",
    stopOpacity: "0"
  }))), /*#__PURE__*/React.createElement("path", {
    d: path,
    fill: "none",
    stroke: "var(--gilt-dim)",
    strokeWidth: "1",
    strokeDasharray: "3 4"
  }), /*#__PURE__*/React.createElement("path", {
    d: `${path} L ${W - pad} ${base} L ${pad} ${base} Z`,
    fill: "var(--gilt)",
    opacity: ".07"
  }), /*#__PURE__*/React.createElement("line", {
    x1: "0",
    y1: base,
    x2: W,
    y2: base,
    stroke: "url(#as-arc-h)",
    strokeWidth: "1"
  }), /*#__PURE__*/React.createElement("line", {
    x1: pad,
    y1: base - 4,
    x2: pad,
    y2: base + 4,
    stroke: "var(--gilt-dim)",
    strokeWidth: "1"
  }), /*#__PURE__*/React.createElement("line", {
    x1: W - pad,
    y1: base - 4,
    x2: W - pad,
    y2: base + 4,
    stroke: "var(--gilt-dim)",
    strokeWidth: "1"
  }), isDay && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("line", {
    x1: x,
    y1: y,
    x2: x,
    y2: base,
    stroke: "var(--gilt)",
    strokeWidth: "0.8",
    opacity: ".45"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: x,
    cy: y,
    r: "9",
    fill: "var(--gilt)",
    opacity: ".16"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: x,
    cy: y,
    r: "4.5",
    fill: "var(--gilt-bright)"
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      gap: 10,
      padding: '0 14px 12px',
      marginTop: -6
    }
  }, /*#__PURE__*/React.createElement(Time, {
    mark: "\\u2609",
    label: "Rose",
    value: sunrise
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      justifyItems: 'center',
      gap: 4
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Glyph, {
    name: ruler,
    tone: "hour",
    size: "sm"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-data",
    style: {
      font: '600 15px/1 var(--font-body)',
      color: 'var(--ink)',
      fontVariantNumeric: 'tabular-nums'
    }
  }, now)), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      justifyItems: 'center',
      gap: 4
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.MoonDisc, {
    phase: phase,
    size: 18
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      fontSize: 11
    }
  }, Math.round(phase * 100), "%")), /*#__PURE__*/React.createElement(Time, {
    mark: "\\u2609",
    label: "Sets",
    value: sunset,
    align: "right"
  })));
}
function Time({
  mark,
  label,
  value,
  align = 'left'
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      justifyItems: align === 'right' ? 'end' : 'start',
      gap: 3
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      fontSize: 10
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 13px/1 var(--font-body)',
      color: 'var(--soft)',
      fontVariantNumeric: 'tabular-nums'
    }
  }, value));
}
Object.assign(__ds_scope, { DayArc });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/DayArc.jsx", error: String((e && e.message) || e) }); }

// components/navigation/ListRow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* A row in a list: settings, places, licences, a pushed destination.
   56px minimum. `value` sits right, `trailing` replaces the chevron when the
   row does something other than push. `danger` is for the one row that deletes. */
function ListRow({
  label,
  description,
  value,
  leading,
  trailing,
  chevron = true,
  danger = false,
  disabled = false,
  onClick,
  href,
  external = false,
  ...rest
}) {
  const Tag = href ? 'a' : onClick ? 'button' : 'div';
  const tappable = !!(href || onClick);
  return /*#__PURE__*/React.createElement(Tag, _extends({
    href: href,
    target: external ? '_blank' : undefined,
    rel: external ? 'noreferrer' : undefined,
    type: Tag === 'button' ? 'button' : undefined,
    disabled: Tag === 'button' ? disabled : undefined,
    onClick: onClick,
    className: tappable ? 'card-tappable' : undefined,
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      width: '100%',
      textAlign: 'left',
      minHeight: 'var(--tap-comfort)',
      padding: '12px 16px',
      background: 'none',
      border: 0,
      borderRadius: 0,
      cursor: tappable ? 'pointer' : 'default',
      textDecoration: 'none',
      opacity: disabled ? .38 : 1,
      color: 'inherit'
    }
  }, rest), leading && /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 'none',
      display: 'grid',
      placeItems: 'center',
      width: 24
    }
  }, leading), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      minWidth: 0,
      display: 'grid',
      gap: 3
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-body)/1.35 var(--font-body)',
      color: danger ? 'var(--live)' : 'var(--ink)',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, label), description && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--size-caption)/1.45 var(--font-body)',
      color: 'var(--faint)',
      textWrap: 'pretty'
    }
  }, description)), value && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      flex: 'none',
      font: '400 var(--size-caption) var(--font-body)',
      color: 'var(--soft)',
      maxWidth: '42%',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap',
      textAlign: 'right'
    }
  }, value), trailing ? /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 'none'
    }
  }, trailing) : tappable && chevron ? /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: external ? 'open_in_new' : 'chevron_right',
    size: 20,
    tone: "faint"
  }) : null);
}
/* A hairline-separated group of rows on a card. */
function ListGroup({
  children,
  inset = false
}) {
  const rows = React.Children.toArray(children).filter(Boolean);
  return /*#__PURE__*/React.createElement("div", {
    className: inset ? 'card-inset' : 'card',
    style: {
      overflow: 'hidden'
    }
  }, rows.map((c, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      borderTop: i ? '1px solid var(--line)' : 'none'
    }
  }, c)));
}
Object.assign(__ds_scope, { ListRow, ListGroup });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/ListRow.jsx", error: String((e && e.message) || e) }); }

// components/navigation/SegmentedControl.jsx
try { (() => {
/* Two or three segments, never more — beyond three it is a tab bar or a list.
   The selected segment is a filled pill that slides; the labels stay put so the
   row does not reflow. */
function SegmentedControl({
  segments,
  active,
  onChange,
  label = 'View'
}) {
  const i = Math.max(0, segments.findIndex(s => (s.id || s) === active));
  const n = segments.length;
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    "aria-label": label,
    style: {
      position: 'relative',
      display: 'grid',
      gridTemplateColumns: `repeat(${n},1fr)`,
      background: 'var(--inset)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-sm)',
      padding: 3,
      gap: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      top: 3,
      bottom: 3,
      left: 3,
      width: `calc((100% - 6px)/${n})`,
      transform: `translateX(${i * 100}%)`,
      background: 'var(--card)',
      border: '1px solid var(--line-strong)',
      borderRadius: 'calc(var(--radius-sm) - 2px)',
      transition: 'transform var(--dur-2) var(--ease-out)'
    }
  }), segments.map(s => {
    const id = s.id || s,
      lab = s.label || s,
      on = id === active;
    return /*#__PURE__*/React.createElement("button", {
      key: id,
      role: "tab",
      "aria-selected": on,
      type: "button",
      onClick: () => onChange && onChange(id),
      style: {
        position: 'relative',
        appearance: 'none',
        background: 'none',
        border: 0,
        cursor: 'pointer',
        minHeight: 40,
        padding: '0 6px',
        font: (on ? 600 : 400) + ' var(--size-caption)/1 var(--font-body)',
        color: on ? 'var(--ink)' : 'var(--faint)',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        transition: 'color var(--dur-2) var(--ease-out)'
      }
    }, lab);
  }));
}
Object.assign(__ds_scope, { SegmentedControl });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/SegmentedControl.jsx", error: String((e && e.message) || e) }); }

// components/navigation/TabBar.jsx
try { (() => {
const TABS = [{
  id: 'home',
  label: 'Home',
  icon: 'cottage'
}, {
  id: 'sky',
  label: 'Sky',
  icon: 'clear_night'
}, {
  id: 'chart',
  label: 'Chart',
  icon: 'target'
}, {
  id: 'letters',
  label: 'Letters',
  icon: 'text_fields_alt'
}, {
  id: 'practice',
  label: 'Practice',
  icon: 'group'
}, {
  id: 'settings',
  label: 'Settings',
  icon: 'tune'
}];
/* Six tabs. At 360px that is 60px each, so the icon carries the weight — but
   the label always stays: an unlabelled icon row is a memory test.

   Selection is four things at once, none of them colour alone: a gilt hem over
   the item, a warm wash behind the icon, the icon filled, and the label at full
   ink. The bar sits on the inset well rather than the card, so it reads as the
   floor of the app instead of another card. */
function TabBar({
  tabs = TABS,
  active = 'home',
  badges = {},
  onChange
}) {
  return /*#__PURE__*/React.createElement("nav", {
    "aria-label": "Sections",
    style: {
      position: 'relative',
      flex: 'none',
      display: 'grid',
      gridTemplateColumns: `repeat(${tabs.length},1fr)`,
      background: 'linear-gradient(180deg,var(--card) 0%,var(--inset) 100%)',
      borderTop: '1px solid var(--line)',
      minHeight: 'var(--tabbar-h)',
      paddingBottom: 'env(safe-area-inset-bottom,0)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: 1,
      background: 'linear-gradient(90deg,transparent,color-mix(in srgb,var(--ornament) 42%,transparent) 26%,color-mix(in srgb,var(--ornament) 42%,transparent) 74%,transparent)',
      transition: 'background var(--dur-3) var(--ease-in-out)'
    }
  }), tabs.map(t => {
    const on = t.id === active;
    return /*#__PURE__*/React.createElement("button", {
      key: t.id,
      type: "button",
      onClick: () => onChange && onChange(t.id),
      "aria-current": on ? 'page' : undefined,
      style: {
        position: 'relative',
        appearance: 'none',
        background: 'none',
        border: 0,
        cursor: 'pointer',
        display: 'grid',
        justifyItems: 'center',
        alignContent: 'center',
        gap: 5,
        padding: '9px 1px 8px',
        minHeight: 'var(--tabbar-h)',
        color: on ? 'var(--ink)' : 'var(--faint)',
        transition: 'color var(--dur-2) var(--ease-out)'
      }
    }, on && /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        position: 'absolute',
        top: 0,
        left: '18%',
        right: '18%',
        height: 2,
        borderRadius: '0 0 2px 2px',
        background: 'var(--ornament)',
        boxShadow: '0 0 10px color-mix(in srgb,var(--ornament) 55%,transparent)',
        transition: 'background var(--dur-3) var(--ease-in-out)'
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        position: 'relative',
        display: 'grid',
        placeItems: 'center',
        width: 44,
        height: 26,
        borderRadius: 'var(--radius-full)',
        background: on ? 'color-mix(in srgb,var(--ornament) 15%,transparent)' : 'transparent',
        transition: 'background var(--dur-2) var(--ease-out)'
      }
    }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
      name: t.icon,
      size: 21,
      fill: on ? 1 : 0,
      tone: on ? 'ink' : 'faint'
    }), badges[t.id] ? /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        position: 'absolute',
        top: -1,
        right: 6,
        width: 7,
        height: 7,
        borderRadius: 99,
        background: 'var(--live)',
        border: '1.5px solid var(--card)'
      }
    }) : null), /*#__PURE__*/React.createElement("span", {
      style: {
        font: (on ? 600 : 400) + ' 10px/1 var(--font-body)',
        letterSpacing: '.015em',
        whiteSpace: 'nowrap'
      }
    }, t.label));
  }));
}
Object.assign(__ds_scope, { TABS, TabBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/TabBar.jsx", error: String((e && e.message) || e) }); }

// components/surfaces/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* The app's surface. Four tones and no more:
   plain       a container
   tappable    it pushes somewhere — deepens and strengthens on press, never lifts
   highlighted an offer; gilt hairline + hem, because offers are the only place
               the brand ornament is allowed to sell something
   warning     something needs attention or cannot be reckoned; rose, with a mark */
function Card({
  tone = 'plain',
  onClick,
  href,
  hem = false,
  pad = 16,
  children,
  style,
  ...rest
}) {
  const Tag = href ? 'a' : onClick ? 'button' : 'div';
  const tappable = !!(href || onClick);
  const tones = {
    plain: {
      background: 'var(--card)',
      border: '1px solid var(--line)'
    },
    tappable: {
      background: 'var(--card)',
      border: '1px solid var(--line)'
    },
    highlighted: {
      background: 'linear-gradient(168deg,var(--gilt-wash) 0%,var(--card) 58%)',
      border: '1px solid color-mix(in srgb,var(--gilt) 38%,transparent)'
    },
    warning: {
      background: 'var(--rose-wash)',
      border: '1px solid color-mix(in srgb,var(--rose) 40%,transparent)'
    },
    inset: {
      background: 'var(--inset)',
      border: '1px solid var(--line)'
    }
  };
  return /*#__PURE__*/React.createElement(Tag, _extends({
    href: href,
    onClick: onClick,
    type: Tag === 'button' ? 'button' : undefined,
    className: (tappable ? 'card-tappable ' : '') + (hem || tone === 'highlighted' ? 'hem' : ''),
    style: {
      display: 'block',
      width: '100%',
      textAlign: 'left',
      position: 'relative',
      borderRadius: 'var(--radius-md)',
      padding: pad,
      color: 'inherit',
      textDecoration: 'none',
      boxShadow: 'var(--shadow-1)',
      cursor: tappable ? 'pointer' : 'default',
      overflow: 'hidden',
      ...tones[tone],
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/surfaces/Card.jsx", error: String((e && e.message) || e) }); }

// components/surfaces/Dialog.jsx
try { (() => {
/* Two dialogs.
   small      — a confirm. One question, two buttons, the destructive one outlined.
   fullscreen — the sky drawer: reference material that wants the whole screen but
                is not a place in the app, so it closes rather than pops. */
function Dialog({
  open = true,
  size = 'small',
  title,
  subtitle,
  onClose,
  actions,
  children
}) {
  if (!open) return null;
  const full = size === 'fullscreen';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: 0,
      zIndex: 70,
      display: 'grid',
      alignItems: full ? 'stretch' : 'center',
      justifyItems: 'center',
      padding: full ? 0 : 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: full ? undefined : onClose,
    style: {
      position: 'absolute',
      inset: 0,
      background: 'rgba(9,12,22,.7)',
      animation: 'as-fade var(--dur-2) var(--ease-out)'
    }
  }), /*#__PURE__*/React.createElement("section", {
    role: "dialog",
    "aria-modal": "true",
    "aria-label": title,
    className: full ? 'hem hem-hour' : 'hem',
    style: {
      position: 'relative',
      width: '100%',
      maxWidth: full ? 'none' : 400,
      background: 'var(--card)',
      border: full ? 'none' : '1px solid var(--line)',
      borderRadius: full ? 0 : 'var(--radius-lg)',
      boxShadow: 'var(--shadow-3)',
      display: 'grid',
      gridTemplateRows: 'auto 1fr auto',
      overflow: 'hidden',
      animation: full ? 'as-push var(--dur-2) var(--ease-sheet)' : 'as-pop var(--dur-2) var(--ease-out)'
    }
  }, /*#__PURE__*/React.createElement("style", null, '@keyframes as-pop{from{transform:scale(.97);opacity:0}to{transform:none;opacity:1}}@keyframes as-push{from{transform:translateY(24px);opacity:.5}to{transform:none;opacity:1}}@keyframes as-fade{from{opacity:0}to{opacity:1}}'), /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr auto',
      alignItems: 'center',
      gap: 8,
      padding: full ? '0 6px 0 16px' : '18px 18px 0',
      minHeight: full ? 'var(--appbar-h)' : 0,
      borderBottom: full ? '1px solid var(--line)' : 'none'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: `600 ${full ? '19px' : 'var(--size-title)'}/1.25 var(--font-display)`,
      color: 'var(--ink)'
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 3
    }
  }, subtitle)), (full || onClose) && /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "close",
    label: "Close",
    onClick: onClose
  })), /*#__PURE__*/React.createElement("div", {
    className: "as-scroll",
    style: {
      overflowY: 'auto',
      overflowX: 'hidden',
      scrollbarWidth: 'none',
      padding: full ? '12px 12px 20px' : '12px 18px 4px',
      font: '400 var(--size-body)/1.5 var(--font-body)',
      color: 'var(--soft)'
    }
  }, children), actions && /*#__PURE__*/React.createElement("footer", {
    style: {
      display: 'flex',
      gap: 10,
      justifyContent: 'flex-end',
      padding: '14px 18px 18px'
    }
  }, actions)));
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/surfaces/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/surfaces/Sheet.jsx
try { (() => {
/* A bottom sheet: the place picker, the sunrise convention, a share row.
   28px top corners, a grab handle, and a scrim you can tap. It never covers the
   whole screen — that is a full-screen Dialog, which is a different thing. */
function Sheet({
  open = true,
  title,
  onClose,
  actions,
  children,
  maxHeight = '72%'
}) {
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: 0,
      zIndex: 60,
      display: 'grid',
      alignItems: 'end'
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: onClose,
    style: {
      position: 'absolute',
      inset: 0,
      background: 'rgba(9,12,22,.62)',
      backdropFilter: 'blur(2px)',
      animation: 'as-fade var(--dur-2) var(--ease-out)'
    }
  }), /*#__PURE__*/React.createElement("section", {
    role: "dialog",
    "aria-modal": "true",
    "aria-label": title,
    className: "hem",
    style: {
      position: 'relative',
      background: 'var(--card)',
      borderTopLeftRadius: 'var(--radius-xl)',
      borderTopRightRadius: 'var(--radius-xl)',
      borderTop: '1px solid var(--line)',
      boxShadow: 'var(--shadow-3)',
      maxHeight,
      display: 'grid',
      gridTemplateRows: 'auto 1fr auto',
      animation: 'as-rise var(--dur-2) var(--ease-sheet)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("style", null, '@keyframes as-rise{from{transform:translateY(18px);opacity:.6}to{transform:none;opacity:1}}@keyframes as-fade{from{opacity:0}to{opacity:1}}'), /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'grid',
      justifyItems: 'center',
      gap: 10,
      padding: '10px 8px 6px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: 36,
      height: 4,
      borderRadius: 99,
      background: 'var(--line-strong)'
    }
  }), title && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr auto',
      alignItems: 'center',
      width: '100%',
      paddingLeft: 16
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: '600 var(--size-title)/1.25 var(--font-display)',
      color: 'var(--ink)'
    }
  }, title), /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "close",
    label: "Close",
    onClick: onClose
  }))), /*#__PURE__*/React.createElement("div", {
    className: "as-scroll",
    style: {
      overflowY: 'auto',
      overflowX: 'hidden',
      scrollbarWidth: 'none',
      padding: '0 16px 8px'
    }
  }, children), actions && /*#__PURE__*/React.createElement("footer", {
    style: {
      display: 'flex',
      gap: 10,
      padding: '12px 16px 20px',
      borderTop: '1px solid var(--line)'
    }
  }, actions)));
}
Object.assign(__ds_scope, { Sheet });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/surfaces/Sheet.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/App.jsx
try { (() => {
/* The Astrolabe kit shell: a phone, its six tabs, its pushed screens, and the
   switches that put every screen into every state the addendum asks for. */
const DEVICES = {
  small: {
    w: 360,
    h: 800,
    name: '360 × 800'
  },
  large: {
    w: 430,
    h: 930,
    name: '430 × 930'
  }
};
const HOURS = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn'];
const STATE_KEYS = [['live', 'Live'], ['offline', 'Offline'], ['loading', 'Loading'], ['empty', 'Empty'], ['error', 'Error'], ['signedIn', 'Signed in'], ['member', 'Member'], ['longContent', 'Long content'], ['missing', 'Missing content'], ['noBirthTime', 'No birth time'], ['art', 'Her artwork present'], ['reduceMotion', 'Reduce motion']];
function App() {
  const [device, setDevice] = React.useState('small');
  const [tab, setTab] = React.useState('home');
  const [pushed, setPushed] = React.useState(null);
  const [skySeg, setSkySeg] = React.useState('stations');
  const [lettersSeg, setLettersSeg] = React.useState('reckoning');
  const [practiceSeg, setPracticeSeg] = React.useState('read');
  const [cast, setCast] = React.useState(false);
  const [st, setSt] = React.useState({
    live: false,
    offline: false,
    loading: false,
    empty: false,
    error: false,
    signedIn: true,
    member: false,
    longContent: false,
    missing: false,
    noBirthTime: false,
    art: false,
    reduceMotion: false,
    place: 'Athens, Greece',
    sunrise: 'limb',
    hour: 'venus',
    confirmDelete: false
  });
  const s = {
    ...st,
    set: (k, v) => setSt(p => ({
      ...p,
      [k]: v
    }))
  };
  const d = DEVICES[device];
  const go = (dest, seg) => {
    if (dest === null) return setPushed(null);
    if (dest === 'sky') {
      setTab('sky');
      if (seg) setSkySeg(seg);
      return setPushed(null);
    }
    if (dest === 'sunrise') return setPushed('sunrise');
    setPushed(dest);
  };
  const screen = () => {
    if (pushed === 'work') return /*#__PURE__*/React.createElement(WorkScreen, {
      s: s,
      go: go
    });
    if (pushed === 'write') return /*#__PURE__*/React.createElement(WriteScreen, {
      s: s,
      go: go
    });
    if (pushed === 'account') return /*#__PURE__*/React.createElement(AccountScreen, {
      s: s,
      go: go
    });
    if (pushed === 'notifications') return /*#__PURE__*/React.createElement(NotificationsScreen, {
      s: s,
      go: go
    });
    if (pushed === 'licences') return /*#__PURE__*/React.createElement(LicencesScreen, {
      go: go
    });
    if (pushed === 'place') return /*#__PURE__*/React.createElement(PlacePickerScreen, {
      s: s,
      go: go
    });
    switch (tab) {
      case 'sky':
        return /*#__PURE__*/React.createElement(SkyScreen, {
          s: s,
          seg: skySeg,
          setSeg: setSkySeg,
          go: go
        });
      case 'chart':
        return /*#__PURE__*/React.createElement(ChartScreen, {
          s: s,
          cast: cast,
          setCast: setCast,
          go: go
        });
      case 'letters':
        return /*#__PURE__*/React.createElement(LettersScreen, {
          s: s,
          seg: lettersSeg,
          setSeg: setLettersSeg
        });
      case 'practice':
        return /*#__PURE__*/React.createElement(PracticeScreen, {
          s: s,
          seg: practiceSeg,
          setSeg: setPracticeSeg,
          go: go
        });
      case 'settings':
        return /*#__PURE__*/React.createElement(SettingsScreen, {
          s: s,
          go: go
        });
      default:
        return /*#__PURE__*/React.createElement(HomeScreen, {
          s: s,
          go: go
        });
    }
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 28,
      alignItems: 'flex-start',
      flexWrap: 'wrap',
      padding: 24,
      minHeight: '100vh',
      boxSizing: 'border-box'
    }
  }, /*#__PURE__*/React.createElement(Controls, {
    device,
    setDevice,
    tab,
    setTab,
    pushed,
    setPushed,
    s,
    st,
    setSt,
    cast,
    setCast,
    skySeg,
    setSkySeg,
    lettersSeg,
    setLettersSeg,
    practiceSeg,
    setPracticeSeg
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Phone, {
    w: d.w,
    h: d.h,
    s: s
  }, /*#__PURE__*/React.createElement(StatusBar, {
    live: s.live
  }), screen(), !pushed && /*#__PURE__*/React.createElement(TabBar, {
    active: tab,
    badges: s.signedIn ? {
      practice: 2
    } : {},
    onChange: t => {
      setTab(t);
      setPushed(null);
    }
  }), pushed === 'drawer' && /*#__PURE__*/React.createElement(SkyDrawer, {
    s: s,
    onClose: () => setPushed(null)
  }), /*#__PURE__*/React.createElement(Sheet, {
    open: pushed === 'sunrise',
    title: "Sunrise convention",
    onClose: () => setPushed(null),
    actions: /*#__PURE__*/React.createElement(Button, {
      full: true,
      onClick: () => setPushed(null)
    }, "Done")
  }, /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: '0 0 6px',
      lineHeight: 1.6
    }
  }, "Which moment begins the day. The two answers differ by about half an hour, and every planetary hour moves with them."), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "radio",
    label: "Sunrise",
    rule: "The Sun\u2019s upper limb clears the horizon.",
    checked: s.sunrise === 'limb',
    value: "limb",
    onChange: () => s.set('sunrise', 'limb')
  }), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "radio",
    label: "Civil dawn",
    rule: "The Sun is 6\xB0 below the horizon.",
    checked: s.sunrise === 'civil',
    value: "civil",
    onChange: () => s.set('sunrise', 'civil')
  }), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: '8px 0 0',
      lineHeight: 1.6,
      color: 'var(--faint)'
    }
  }, "Neither is the correct one. Pick the one your tradition uses."))), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 11px/1 var(--font-body)',
      color: 'var(--faint)',
      fontVariantNumeric: 'tabular-nums'
    }
  }, d.name)));
}
function Phone({
  w,
  h,
  s,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    "data-live": s.live ? 'true' : undefined,
    "data-hour": s.hour,
    style: {
      width: w,
      height: h,
      flex: 'none',
      position: 'relative',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--page)',
      borderRadius: 34,
      border: '1px solid var(--line-strong)',
      boxShadow: '0 24px 70px -20px rgba(0,0,0,.7)',
      overflow: 'hidden',
      transition: 'width var(--dur-2) var(--ease-out),height var(--dur-2) var(--ease-out)'
    }
  }, s.reduceMotion && /*#__PURE__*/React.createElement("style", null, '*{animation-duration:1ms!important;transition-duration:1ms!important}'), children);
}
function Controls(p) {
  const {
    s,
    st,
    setSt
  } = p;
  const box = {
    background: 'var(--card)',
    border: '1px solid var(--line)',
    borderRadius: 'var(--radius-md)',
    padding: 14,
    display: 'grid',
    gap: 10
  };
  const eyebrow = {
    font: '600 10px/1 var(--font-body)',
    letterSpacing: '.14em',
    textTransform: 'uppercase',
    color: 'var(--faint)'
  };
  const tabs = [['home', 'Home'], ['sky', 'Sky'], ['chart', 'Chart'], ['letters', 'Letters'], ['practice', 'Practice'], ['settings', 'Settings']];
  const pushes = [['work', 'One work'], ['write', 'Write'], ['account', 'Account'], ['notifications', 'Notifications'], ['licences', 'Licences'], ['place', 'Place picker'], ['drawer', 'Sky drawer'], ['sunrise', 'Sunrise sheet']];
  return /*#__PURE__*/React.createElement("aside", {
    style: {
      width: 288,
      flex: 'none',
      display: 'grid',
      gap: 12,
      position: 'sticky',
      top: 24
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: '500 26px/1.1 var(--font-display)',
      color: 'var(--ink)',
      letterSpacing: '-0.012em'
    }
  }, "Astrolabe"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 13px/1.5 var(--font-body)',
      color: 'var(--faint)'
    }
  }, "Her companion app. Eighteen screens, every state.")), /*#__PURE__*/React.createElement("div", {
    style: box
  }, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Tab"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 6
    }
  }, tabs.map(([id, lab]) => /*#__PURE__*/React.createElement(Chip, {
    key: id,
    kind: "choice",
    selected: p.tab === id && !p.pushed,
    onClick: () => {
      p.setTab(id);
      p.setPushed(null);
    }
  }, lab))), p.tab === 'sky' && !p.pushed && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Sky segment"), /*#__PURE__*/React.createElement(SegmentedControl, {
    active: p.skySeg,
    onChange: p.setSkySeg,
    label: "Sky segment",
    segments: [{
      id: 'stations',
      label: 'Stations'
    }, {
      id: 'hours',
      label: 'Hours'
    }, {
      id: 'coming',
      label: 'Coming'
    }]
  })), p.tab === 'letters' && !p.pushed && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Letters segment"), /*#__PURE__*/React.createElement(SegmentedControl, {
    active: p.lettersSeg,
    onChange: p.setLettersSeg,
    label: "Letters segment",
    segments: [{
      id: 'reckoning',
      label: 'Reckoning'
    }, {
      id: 'sigil',
      label: 'Sigil'
    }]
  })), p.tab === 'practice' && !p.pushed && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Practice segment"), /*#__PURE__*/React.createElement(SegmentedControl, {
    active: p.practiceSeg,
    onChange: p.setPracticeSeg,
    label: "Practice segment",
    segments: [{
      id: 'read',
      label: 'Read'
    }, {
      id: 'mine',
      label: 'Mine'
    }]
  })), p.tab === 'chart' && !p.pushed && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Chart"), /*#__PURE__*/React.createElement(SegmentedControl, {
    active: p.cast ? 'result' : 'form',
    onChange: v => p.setCast(v === 'result'),
    label: "Chart stage",
    segments: [{
      id: 'form',
      label: 'The form'
    }, {
      id: 'result',
      label: 'The result'
    }]
  }))), /*#__PURE__*/React.createElement("div", {
    style: box
  }, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Pushed and dialogs"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 6
    }
  }, pushes.map(([id, lab]) => /*#__PURE__*/React.createElement(Chip, {
    key: id,
    kind: "choice",
    selected: p.pushed === id,
    onClick: () => p.setPushed(p.pushed === id ? null : id)
  }, lab)))), /*#__PURE__*/React.createElement("div", {
    style: box
  }, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "States"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 6
    }
  }, STATE_KEYS.map(([k, lab]) => /*#__PURE__*/React.createElement(Chip, {
    key: k,
    kind: "filter",
    selected: !!st[k],
    onClick: () => setSt(prev => ({
      ...prev,
      [k]: !prev[k]
    }))
  }, lab)))), /*#__PURE__*/React.createElement("div", {
    style: box
  }, /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Ruling hour"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 6
    }
  }, HOURS.map(h => /*#__PURE__*/React.createElement(Chip, {
    key: h,
    kind: "choice",
    selected: s.hour === h,
    onClick: () => s.set('hour', h)
  }, h))), /*#__PURE__*/React.createElement("span", {
    style: eyebrow
  }, "Device"), /*#__PURE__*/React.createElement(SegmentedControl, {
    active: p.device,
    onChange: p.setDevice,
    label: "Device",
    segments: [{
      id: 'small',
      label: '360 × 800'
    }, {
      id: 'large',
      label: '430 × 930'
    }]
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 11px/1.6 var(--font-body)',
      color: 'var(--faint)'
    }
  }, "Sample data is plausible and internally consistent, not live computation. The reckoning a developer must write is described in the design system\u2019s readme."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "artwork.html",
    style: {
      font: '500 13px/1.5 var(--font-body)'
    }
  }, "Where your art goes \u2192"), /*#__PURE__*/React.createElement("a", {
    href: "states.html",
    style: {
      font: '500 13px/1.5 var(--font-body)'
    }
  }, "Every screen, every state \u2192")));
}
Object.assign(window, {
  App,
  Phone,
  Controls
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/Artwork.jsx
try { (() => {
/* "Where your art goes" — every slot from guidelines/artwork-spec.md, at its
   real size, inside the real screen, with a drop target in it.
   Drag a PNG onto any slot and it stays there; the app themes around it live. */

function Slot({
  id,
  w,
  h,
  shape = 'rounded',
  radius = 12,
  placeholder,
  src,
  style
}) {
  /* The component fills its container, so size the WRAPPER, never the slot. */
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      width: w,
      height: h,
      flex: 'none',
      ...style
    }
  }, /*#__PURE__*/React.createElement("image-slot", {
    id: id,
    shape: shape,
    radius: radius,
    placeholder: placeholder || '\u00a0',
    src: src,
    style: {
      position: 'absolute',
      inset: 0
    }
  }));
}
/* The Masthead's portrait column, at its real size: 150 × 244 logical. */
function FillSlot({
  id,
  placeholder
}) {
  return /*#__PURE__*/React.createElement(Slot, {
    id: id,
    w: "150px",
    h: "244px",
    shape: "rect",
    placeholder: placeholder
  });
}
function Spec({
  n,
  name,
  need,
  rows,
  note
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--gilt)'
    }
  }, n), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: '500 21px/1.25 var(--font-display)',
      color: 'var(--ink)'
    }
  }, name), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 10px/1 var(--font-body)',
      letterSpacing: '.12em',
      textTransform: 'uppercase',
      padding: '4px 8px',
      borderRadius: 'var(--radius-full)',
      color: need === 'Essential' ? 'var(--gilt)' : 'var(--faint)',
      background: need === 'Essential' ? 'var(--gilt-wash)' : 'transparent',
      border: '1px solid ' + (need === 'Essential' ? 'color-mix(in srgb,var(--gilt) 38%,transparent)' : 'var(--line)')
    }
  }, need)), /*#__PURE__*/React.createElement("div", {
    className: "card",
    style: {
      padding: '12px 14px'
    }
  }, rows.map((r, i) => /*#__PURE__*/React.createElement(DataRow, {
    key: i,
    label: r[0],
    value: r[1],
    small: r[2]
  }))), note && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 13px/1.6 var(--font-body)',
      color: 'var(--faint)',
      maxWidth: '46ch',
      textWrap: 'pretty'
    }
  }, note));
}

/* A phone, for showing a slot in situ. */
function Mini({
  children,
  h = 460,
  label,
  live,
  hour = 'venus',
  tab = 'home',
  chrome = true
}) {
  return /*#__PURE__*/React.createElement("figure", {
    style: {
      margin: 0,
      display: 'grid',
      gap: 8,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    "data-live": live ? 'true' : undefined,
    "data-hour": hour,
    style: {
      width: 360,
      height: h,
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden',
      background: 'var(--page)',
      border: '1px solid var(--line-strong)',
      borderRadius: 30,
      boxShadow: '0 18px 48px -18px rgba(0,0,0,.65)'
    }
  }, chrome && /*#__PURE__*/React.createElement(StatusBar, {
    live: live
  }), children, chrome && /*#__PURE__*/React.createElement(TabBar, {
    active: tab,
    onChange: () => {}
  })), label && /*#__PURE__*/React.createElement("figcaption", {
    style: {
      font: '400 12px/1.4 var(--font-body)',
      color: 'var(--faint)'
    }
  }, label));
}
function Section({
  children
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'minmax(300px,380px) minmax(280px,1fr)',
      gap: 32,
      alignItems: 'start',
      padding: '30px 0',
      borderTop: '1px solid var(--line)'
    }
  }, children);
}
function ArtworkDoc() {
  const A = window.AL;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 1080,
      margin: '0 auto',
      padding: '36px 28px 100px'
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'grid',
      gap: 12,
      maxWidth: '60ch'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Astrolabe \xB7 artwork"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: '500 40px/1.1 var(--font-display)',
      color: 'var(--ink)',
      letterSpacing: '-0.014em'
    }
  }, "Where your art goes"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 17px/1.65 var(--font-display)',
      color: 'var(--soft)',
      textWrap: 'pretty'
    }
  }, "Every drawing the app asks for, at its real size, inside the real screen.", /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--ink)',
      fontWeight: 500
    }
  }, " Drag a PNG onto any dotted slot"), " \u2014 it stays there, and the app themes around it immediately, so you can see how a piece sits before you finish it. Nothing here is required for the app to ship: every slot has a designed state without art, shown beside it."), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 13px/1.6 var(--font-body)',
      color: 'var(--faint)'
    }
  }, "Full written spec, including the AGPL licence question about your drawings:", /*#__PURE__*/React.createElement("code", {
    style: {
      color: 'var(--soft)'
    }
  }, " guidelines/artwork-spec.md")), /*#__PURE__*/React.createElement("div", {
    className: "rule",
    style: {
      maxWidth: 420,
      marginTop: 6
    }
  }, '\u263E\uFE0E')), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Essential \xB7 3",
    name: "Home portrait \u2014 offline",
    need: "Essential",
    rows: [['Canvas', '800 × 1200 px'], ['Used at', '150 × 244 logical (450 × 732 @3×)'], ['Transparency', 'Transparent PNG + layered source'], ['May be cropped', 'left 18%, bottom 12%'], ['Behind it', 'the plate: cloak navy → card, with the star scatter'], ['Seen', 'every open of the app', true]],
    note: "Three-quarter view, turned slightly away, looking down at something in her hands. Quiet, occupied, mid-thought \u2014 not addressing the viewer. She is doing her own work while you check the sky."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(Mini, {
    h: 430,
    label: "Drop the transparent portrait here"
  }, /*#__PURE__*/React.createElement(AppBar, {
    title: "Astrolabe",
    hour: true
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 14
  }, /*#__PURE__*/React.createElement(Masthead, {
    greeting: "Good evening",
    line: "A waxing gibbous moon, four days from full.",
    artSlot: /*#__PURE__*/React.createElement(FillSlot, {
      id: "portrait-offline",
      placeholder: "Portrait \u2014 offline"
    })
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(HourChip, {
    ruler: "venus",
    ordinal: 7,
    diurnal: true,
    ends: "14:12"
  }), /*#__PURE__*/React.createElement(MoonDisc, {
    phase: 0.38,
    size: 22
  })), /*#__PURE__*/React.createElement(ContentCard, {
    kind: "reading",
    sign: "Scorpio",
    signMark: A.S.scorpio,
    date: "9 Sep",
    readingTime: "2 min",
    excerpt: "Mercury is still in the shadow."
  }))), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: 0,
      textAlign: 'center'
    }
  }, "With no drawing at all, the same plate holds a gilt \u263E in that column \u2014 see the app kit."))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Essential \xB7 4",
    name: "Home portrait \u2014 live",
    need: "Essential",
    rows: [['Canvas', '800 × 1200 px, same crop rules as #3'], ['Transparency', 'Transparent PNG'], ['Behind it', 'the plate, warmed by a rose glow from the lower right'], ['Seen', 'every open during a stream', true]],
    note: "A second drawing, not a recolour. Facing out, mid-speech, hood back. Let the live rose #F07A8C appear somewhere small and real \u2014 a ribbon, the lining catching light \u2014 so the rose hem has something to answer."
  }), /*#__PURE__*/React.createElement(Mini, {
    h: 430,
    live: true,
    label: "Drop the live portrait here"
  }, /*#__PURE__*/React.createElement(AppBar, {
    title: "Astrolabe",
    hour: true
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 14
  }, /*#__PURE__*/React.createElement(Masthead, {
    live: true,
    greeting: "She is live",
    line: "Casting charts for the chat, since 20:04 Athens.",
    artSlot: /*#__PURE__*/React.createElement(FillSlot, {
      id: "portrait-live",
      placeholder: "Portrait \u2014 live"
    })
  }), /*#__PURE__*/React.createElement(LiveBanner, {
    status: "live",
    title: "Casting charts for the chat",
    game: "Just Chatting",
    viewers: 412
  })))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Essential \xB7 1",
    name: "App icon \u2014 adaptive",
    need: "Essential",
    rows: [['Canvas', 'two layers, 432 × 432 (also 1024 flat for iOS)'], ['Safe zone', '264 × 264 centred — the rest is cropped to a shape you cannot predict'], ['Foreground', 'transparent'], ['Background', 'fully opaque, edge to edge'], ['Seen', 'several times a day, for a fifth of a second', true]],
    note: "One mark, not a scene. The crescent-and-star clasp at the throat of your cloak reads at 48 px; a face does not. Background: flat #2B3450 with five or six stars, none crossing into the safe zone."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 18,
      justifyItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 22,
      alignItems: 'flex-end',
      flexWrap: 'wrap'
    }
  }, [['icon-108', 108, '108 px'], ['icon-72', 72, '72 px'], ['icon-48', 48, '48 px']].map(([id, px, lab]) => /*#__PURE__*/React.createElement("div", {
    key: id,
    style: {
      display: 'grid',
      gap: 8,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: id,
    w: px + 'px',
    h: px + 'px',
    shape: "rounded",
    radius: Math.round(px * 0.23),
    placeholder: px >= 72 ? 'Icon' : '\u00a0'
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, lab)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10,
      width: '100%'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "The two layers, at 216 with the safe zone drawn"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 18,
      flexWrap: 'wrap'
    }
  }, [['icon-bg', 'Background — opaque'], ['icon-fg', 'Foreground — transparent']].map(([id, lab]) => /*#__PURE__*/React.createElement("div", {
    key: id,
    style: {
      display: 'grid',
      gap: 8,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      width: 216,
      height: 216
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: id,
    w: "216px",
    h: "216px",
    shape: "rect",
    placeholder: lab
  }), /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      inset: '20.8%',
      border: '1px dashed color-mix(in srgb,var(--gilt) 65%,transparent)',
      borderRadius: 6,
      pointerEvents: 'none'
    }
  }), /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      inset: 0,
      borderRadius: '50%',
      border: '1px solid color-mix(in srgb,var(--accent) 40%,transparent)',
      pointerEvents: 'none'
    }
  })), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, lab)))), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: 0
    }
  }, "Gold dashed = the 264 safe zone. Blue circle = one of the shapes a launcher may crop to.")))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Essential \xB7 2",
    name: "Notification icon",
    need: "Essential",
    rows: [['Canvas', '96 × 96 (24 dp @4×); also 72 / 48 / 36 / 24'], ['Transparency', '⚠ transparent, and pure white at varying alpha ONLY'], ['Behind it', 'the system status bar, any wallpaper'], ['Seen', 'every time you go live', true]],
    note: "\u26A0 Android throws away every colour in this file and renders the alpha channel as a flat silhouette. A gold icon arrives as a white blob. Draw the clasp as a solid silhouette with no interior detail \u2014 at 24 dp the inner line becomes mud."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 14,
      justifyItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      padding: '10px 16px',
      background: 'var(--inset)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      width: 360,
      boxSizing: 'border-box'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '600 12px/1 var(--font-body)',
      color: 'var(--soft)'
    }
  }, "20:41"), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Slot, {
    id: "icon-notification",
    w: "18px",
    h: "18px",
    shape: "rect",
    placeholder: ""
  }), /*#__PURE__*/React.createElement(Icon, {
    name: "wifi",
    size: 14,
    tone: "soft"
  }), /*#__PURE__*/React.createElement(Icon, {
    name: "battery_5_bar",
    size: 14,
    tone: "soft"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 16,
      alignItems: 'flex-end'
    }
  }, [['notif-96', 96], ['notif-48', 48], ['notif-24', 24]].map(([id, px]) => /*#__PURE__*/React.createElement("div", {
    key: id,
    style: {
      display: 'grid',
      gap: 6,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: id,
    w: px + 'px',
    h: px + 'px',
    shape: "rect",
    placeholder: ""
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, px)))))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Essential \xB7 5",
    name: "Splash / launch mark",
    need: "Essential",
    rows: [['Canvas', '1152 × 1152 (288 dp); visible circle 768 × 768'], ['Safe zone', 'the centre 768 circle — everything outside is masked'], ['Transparency', 'transparent; the background is #121829 from the theme'], ['Seen', 'every cold start, for under a second', true]],
    note: "No text, no wordmark, no character \u2014 anything with detail in it flickers. Draw the crescent and the star on separate layers if you want the star to fade in 200 ms behind it."
  }), /*#__PURE__*/React.createElement(Mini, {
    h: 430,
    chrome: false,
    label: "Cold start"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      display: 'grid',
      placeItems: 'center',
      background: 'var(--page)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      width: 192,
      height: 192
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "splash-mark",
    w: "192px",
    h: "192px",
    shape: "circle",
    placeholder: "Splash mark"
  }), /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      inset: 0,
      borderRadius: '50%',
      border: '1px dashed color-mix(in srgb,var(--gilt) 55%,transparent)',
      pointerEvents: 'none'
    }
  }))))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Essential \xB7 6",
    name: "Wordmark, re-cut for the night",
    need: "Essential",
    rows: [['Format', 'SVG, plus PNG at 1500 × 540'], ['Transparency', 'transparent'], ['Behind it', '#121829 and #1A2138'], ['Seen', 'Settings, licences, the store listing', true]],
    note: "\u26A0 A re-cut of your existing wordmark, not a new logo. The current one is the WordPress-era pink and blue: on #121829 the pale pink vibrates and the outline disappears. Same letterforms, same Devanagari, re-coloured for night \u2014 ink with gilt accents, or a single gilt cut."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 14,
      width: '100%'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "card",
    style: {
      padding: 20,
      display: 'grid',
      gap: 6,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "wordmark-night",
    w: "280px",
    h: "100px",
    shape: "rect",
    placeholder: "Wordmark \u2014 night cut"
  })), /*#__PURE__*/React.createElement("div", {
    className: "card-inset",
    style: {
      padding: 20,
      display: 'grid',
      gap: 10,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/wordmark-small.png",
    alt: "The existing wordmark",
    style: {
      height: 64
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      color: 'var(--rose)'
    }
  }, "What exists today \u2014 off-palette on this page. Never redrawn here.")))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Nice to have \xB7 7\u20139",
    name: "Empty-state drawings",
    need: "Nice to have",
    rows: [['Canvas', '512 × 512 each'], ['Transparency', 'transparent'], ['Sits above', 'two lines of authored text and a button'], ['Behind it', '#121829'], ['Seen', 'often for a new user, rarely for an old one', true]],
    note: "\u26A0 The offline one is the hard brief and the important one: it is not an error drawing. The instruments all still work \u2014 what is missing is you. The cloak on a peg; a lit window seen from outside. An absence with a promise in it. Nothing red, no exclamation mark."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 20,
      flexWrap: 'wrap'
    }
  }, [['empty-practice', 'The room is quiet', 'Nobody has posted a reading this week. Yours would be the first.', 'Practice, empty'], ['empty-offline', 'Her half is out of reach', 'The instruments all still work — they compute on your phone.', 'Offline'], ['empty-unwritten', 'Nothing written yet', 'A reading here is a few hundred words on one chart. It does not have to be right.', 'Mine, empty']].map(([id, title, body, lab]) => /*#__PURE__*/React.createElement("figure", {
    key: id,
    style: {
      margin: 0,
      display: 'grid',
      gap: 8,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 280,
      background: 'var(--page)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      padding: '8px 0'
    }
  }, /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    art: undefined,
    title: title,
    body: body,
    action: /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: "outlined"
    }, "An action")
  })), /*#__PURE__*/React.createElement(Slot, {
    id: id,
    w: "148px",
    h: "148px",
    shape: "rounded",
    radius: 14,
    placeholder: "Drop the drawing"
  }), /*#__PURE__*/React.createElement("figcaption", {
    className: "t-caption"
  }, lab))))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Nice to have \xB7 10",
    name: "Motifs and dividers",
    need: "Nice to have",
    rows: [['Format', 'SVG, single colour — the app tints them'], ['Grids', '24 × 24 (crescent, star), 120 × 24 (divider), 72 × 24 (phase strip)'], ['Seen', 'section rules and empty states, constantly, small', true]],
    note: "Drawn on a pixel grid rather than scaled down from something larger \u2014 these are the pieces that break when they are shrunk. Today the app uses \u263E and \u2726 from the bundled glyph font, which is why the rules already look intentional."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 18,
      width: '100%'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "card",
    style: {
      padding: '18px 20px',
      display: 'grid',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "rule"
  }, '\u263E\uFE0E'), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      textAlign: 'center'
    }
  }, "The rule today, set in AstroSymbols")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 16,
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "motif-crescent",
    w: "72px",
    h: "72px",
    shape: "rect",
    placeholder: "\u263E"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, "crescent 24")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "motif-star",
    w: "72px",
    h: "72px",
    shape: "rect",
    placeholder: "\u2726"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, "star 24")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "motif-divider",
    w: "240px",
    h: "48px",
    shape: "rect",
    placeholder: "divider 120 \xD7 24"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, "divider")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "motif-phases",
    w: "144px",
    h: "48px",
    shape: "rect",
    placeholder: "phase strip"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, "phase strip 72 \xD7 24"))))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement(Spec, {
    n: "Nice to have \xB7 11",
    name: "Live-state ornament",
    need: "Nice to have",
    rows: [['Canvas', '1200 × 200'], ['Transparency', 'transparent'], ['Behind it', 'the live plate, behind the greeting'], ['Seen', 'during every stream', true]],
    note: "A thin band of the cloak's star scatter with the gold trim running through it, fading out at both ends. This is what makes live feel like an event rather than a colour change. If it competes with the rose hem, thin it."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10,
      width: 360
    }
  }, /*#__PURE__*/React.createElement("div", {
    "data-live": "true",
    className: "plate hem hem-strong",
    style: {
      position: 'relative',
      height: 150,
      display: 'grid',
      alignContent: 'end',
      padding: '0 16px 16px',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: '0 0 auto 0',
      height: 70
    }
  }, /*#__PURE__*/React.createElement(Slot, {
    id: "live-band",
    w: "100%",
    h: "70px",
    shape: "rect",
    placeholder: "Live band \u2014 1200 \xD7 200"
  })), /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--live)',
      position: 'relative'
    }
  }, "Live now"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 30px/1.1 var(--font-display)',
      color: 'var(--ink)',
      position: 'relative',
      marginTop: 6
    }
  }, "She is live")), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      textAlign: 'center'
    }
  }, "Live plate, band across the top"))), /*#__PURE__*/React.createElement("section", {
    style: {
      padding: '30px 0 0',
      borderTop: '1px solid var(--line)',
      display: 'grid',
      gap: 12,
      maxWidth: '62ch'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: '600 22px/1.25 var(--font-display)',
      color: 'var(--rose)'
    }
  }, "\u26A0 The licence question, before anything is committed"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 15px/1.7 var(--font-body)',
      color: 'var(--soft)',
      textWrap: 'pretty'
    }
  }, "Astrolabe is AGPL-3.0 and everything in the repository is published under it. That is fine for code and OFL fonts. It is ", /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--ink)'
    }
  }, "not automatically fine for your drawings"), " \u2014 under the AGPL anybody may fork the app, keep your face on it, and ship it. The three options, and what each costs you, are set out at the foot of", /*#__PURE__*/React.createElement("code", {
    style: {
      color: 'var(--ink)'
    }
  }, " guidelines/artwork-spec.md"), ". The design system assumes a dual licence (code AGPL, artwork yours) until you say otherwise.")));
}
Object.assign(window, {
  ArtworkDoc,
  Slot,
  FillSlot,
  Spec,
  Mini
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/Artwork.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/Kit.jsx
try { (() => {
/* Shared frame pieces for the Astrolabe kit. Not design-system components —
   just the scaffolding the recreation needs. */
const DS = window.AstrolabeDesignSystem_d3620a || {};
/* Any name not yet in the compiled bundle resolves to a visible stub rather than
   taking the whole screen down. */
const NEEDED = ['AppBar', 'TabBar', 'SegmentedControl', 'ListRow', 'ListGroup', 'Button', 'IconButton', 'TextField', 'Chip', 'Switch', 'ChoiceRow', 'Card', 'Sheet', 'Dialog', 'DataTable', 'DataRow', 'ChartWheel', 'CodeBlock', 'Glyph', 'Icon', 'MoonDisc', 'LiveBanner', 'HourChip', 'SectionHeader', 'Masthead', 'DayArc', 'EmptyState', 'Banner', 'Snackbar', 'Progress', 'Skeleton', 'ContentCard', 'WorkCard', 'OfferCard', 'VoteControl', 'Prose'];
const R = {};
NEEDED.forEach(n => {
  R[n] = DS[n] || function Pending() {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '10px 12px',
        border: '1px dashed var(--line-strong)',
        borderRadius: 'var(--radius-sm)',
        font: '400 12px/1.4 var(--font-body)',
        color: 'var(--faint)'
      }
    }, n, " is not in the compiled bundle yet \\u2014 reload once the project has compiled.");
  };
});
const {
  AppBar,
  TabBar,
  SegmentedControl,
  ListRow,
  ListGroup,
  Button,
  IconButton,
  TextField,
  Chip,
  Switch,
  ChoiceRow,
  Card,
  Sheet,
  Dialog,
  DataTable,
  DataRow,
  ChartWheel,
  CodeBlock,
  Glyph,
  Icon,
  MoonDisc,
  LiveBanner,
  HourChip,
  SectionHeader,
  Masthead,
  DayArc,
  EmptyState,
  Banner,
  Snackbar,
  Progress,
  Skeleton,
  ContentCard,
  WorkCard,
  OfferCard,
  VoteControl,
  Prose
} = R;

/* ⚠ A phone shows no scrollbars, and nothing in this app scrolls sideways.
   Vertical overflow is indicated by a fade at the foot of the scroller instead. */
function kitChrome() {
  if (typeof document === 'undefined' || document.getElementById('as-kit-chrome')) return;
  const s = document.createElement('style');
  s.id = 'as-kit-chrome';
  s.textContent = '.as-scroll{scrollbar-width:none;-ms-overflow-style:none}' + '.as-scroll::-webkit-scrollbar{width:0;height:0;display:none}' + '.as-fade{position:relative}' + '.as-fade::after{content:"";position:absolute;left:0;right:0;bottom:0;height:28px;' + 'pointer-events:none;background:linear-gradient(180deg,transparent,var(--page));' + 'opacity:var(--as-fade,1);transition:opacity 160ms var(--ease-out);z-index:5}';
  document.head.appendChild(s);
}

/* The scrolling body of a screen. No scrollbar, never sideways; the foot fades
   while there is more below and clears when you reach the end. */
function Body({
  children,
  pad = 16,
  gap = 14,
  style
}) {
  kitChrome();
  const ref = React.useRef(null);
  const [more, setMore] = React.useState(false);
  const check = React.useCallback(() => {
    const el = ref.current;
    if (!el) return;
    setMore(el.scrollHeight - el.clientHeight - el.scrollTop > 8);
  }, []);
  React.useEffect(() => {
    check();
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(check);
    ro.observe(el);
    return () => ro.disconnect();
  }, [check, children]);
  return /*#__PURE__*/React.createElement("div", {
    className: "as-fade",
    style: {
      flex: 1,
      minHeight: 0,
      minWidth: 0,
      display: 'flex',
      ['--as-fade']: more ? 1 : 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    ref: ref,
    onScroll: check,
    className: "as-scroll",
    style: {
      flex: 1,
      minWidth: 0,
      minHeight: 0,
      overflowY: 'auto',
      overflowX: 'hidden',
      overscrollBehavior: 'contain',
      padding: `12px ${pad}px 20px`,
      display: 'grid',
      gridTemplateColumns: 'minmax(0,1fr)',
      gridAutoRows: 'min-content',
      gap,
      alignContent: 'start',
      ...style
    }
  }, children));
}
/* A row of chips that would otherwise scroll sideways. It wraps instead. */
function ChipRow({
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap',
      minWidth: 0
    }
  }, children);
}
/* A phone status bar — chrome, not design system. */
function StatusBar({
  time = '20:41',
  live
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 18px',
      height: 32,
      flex: 'none',
      font: '600 12px/1 var(--font-body)',
      color: 'var(--soft)',
      fontVariantNumeric: 'tabular-nums',
      background: 'var(--page)'
    }
  }, /*#__PURE__*/React.createElement("span", null, time), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      gap: 6,
      alignItems: 'center',
      opacity: .8
    }
  }, live && /*#__PURE__*/React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: 99,
      background: 'var(--live)'
    }
  }), /*#__PURE__*/React.createElement(Icon, {
    name: "signal_cellular_alt",
    size: 14,
    tone: "soft"
  }), /*#__PURE__*/React.createElement(Icon, {
    name: "wifi",
    size: 14,
    tone: "soft"
  }), /*#__PURE__*/React.createElement(Icon, {
    name: "battery_5_bar",
    size: 14,
    tone: "soft"
  })));
}
/* Pull-to-refresh puck, shown while a screen refreshes something already on it. */
function Refreshing() {
  return /*#__PURE__*/React.createElement(Progress, {
    kind: "refresh"
  });
}

/* A run of DataRows on a card. */
function FactCard({
  title,
  rows,
  foot
}) {
  return /*#__PURE__*/React.createElement(Card, null, title && /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      marginBottom: 8
    }
  }, title), rows.map((r, i) => /*#__PURE__*/React.createElement(DataRow, {
    key: i,
    mark: r.mark,
    label: r.label,
    value: r.value,
    tone: r.rose ? 'rose' : 'ink',
    small: r.small
  })), foot && /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 10,
      paddingTop: 10,
      borderTop: '1px solid var(--line)'
    }
  }, foot));
}
/* Provenance: engine, the rule in force, licence. Every instrument carries one. */
function Provenance({
  engine = 'Swiss Ephemeris 2.10.03',
  rule,
  extra
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 2,
      padding: '2px 2px 0'
    }
  }, rule && /*#__PURE__*/React.createElement(DataRow, {
    label: "Rule in force",
    value: rule,
    small: true,
    tone: "faint"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Engine",
    value: engine,
    small: true,
    tone: "faint"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Computed",
    value: "On this device, offline",
    small: true,
    tone: "faint"
  }), extra);
}
Object.assign(window, {
  DS,
  Body,
  ChipRow,
  StatusBar,
  Refreshing,
  FactCard,
  Provenance,
  kitChrome,
  AppBar,
  TabBar,
  SegmentedControl,
  ListRow,
  ListGroup,
  Button,
  IconButton,
  TextField,
  Chip,
  Switch,
  ChoiceRow,
  Card,
  Sheet,
  Dialog,
  DataTable,
  DataRow,
  ChartWheel,
  CodeBlock,
  Glyph,
  Icon,
  MoonDisc,
  LiveBanner,
  HourChip,
  SectionHeader,
  Masthead,
  DayArc,
  EmptyState,
  Banner,
  Snackbar,
  Progress,
  Skeleton,
  ContentCard,
  WorkCard,
  OfferCard,
  VoteControl,
  Prose
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/Kit.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/Screens1.jsx
try { (() => {
/* Screens 1–4: Home, and the three Sky segments. */

function HomeScreen({
  s,
  go
}) {
  const A = window.AL;
  const live = s.live;
  const greeting = live ? 'She is live' : 'Good evening';
  const line = live ? 'Casting charts for the chat, since 20:04 Athens.' : 'A waxing gibbous moon, four days from full.';
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Astrolabe",
    hour: true,
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(IconButton, {
      icon: "notifications",
      label: "Notifications",
      badge: s.signedIn ? 2 : undefined,
      onClick: () => go('notifications')
    }))
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, s.offline && /*#__PURE__*/React.createElement(Banner, {
    tone: "offline",
    title: "Her half is out of reach"
  }, "The instruments all still work \u2014 they compute on your phone. Readings, offers and the practice room will come back when you do."), s.error && /*#__PURE__*/React.createElement(Banner, {
    tone: "error",
    title: "The site answered badly",
    action: "Try again",
    onAction: () => {}
  }, "Her readings could not be loaded. Everything below the sky line is still yours."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Masthead, {
    greeting: greeting,
    line: line,
    live: live,
    portrait: s.art ? '../../assets/reference-astrologer.jpeg' : undefined,
    fit: "plate",
    portraitAlt: ""
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(HourChip, {
    ruler: s.hour,
    ordinal: 7,
    diurnal: true,
    ends: "14:12",
    onClick: () => go('sky', 'hours')
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 7
    }
  }, /*#__PURE__*/React.createElement(MoonDisc, {
    phase: 0.38,
    size: 22
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      color: 'var(--soft)'
    }
  }, "Waxing gibbous")))), /*#__PURE__*/React.createElement(LiveBanner, {
    status: s.offline ? 'unknown' : live ? 'live' : 'offline',
    title: "Casting charts for the chat",
    game: "Just Chatting",
    viewers: 412,
    nextStream: "Thursday 20:00 Athens",
    onOpen: () => {}
  }), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(SectionHeader, {
    eyebrow: "From Shruti",
    title: "Latest readings",
    action: "All twelve",
    onAction: () => {}
  }), s.loading ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, [0, 1].map(i => /*#__PURE__*/React.createElement(Card, {
    key: i
  }, /*#__PURE__*/React.createElement(Skeleton, {
    lines: 2
  })))) : s.offline || s.error || s.empty ? /*#__PURE__*/React.createElement(Card, {
    tone: "plain",
    pad: 0
  }, /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    mark: A.G.moon,
    title: s.empty ? 'Nothing written yet this week' : 'Kept from last time',
    body: s.empty ? 'She writes the twelve on Sunday night. They will be here when she has.' : 'These are the readings you already had. New ones arrive when her side is reachable.'
  })) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, A.readings.slice(0, s.longContent ? 4 : 3).map(r => /*#__PURE__*/React.createElement(ContentCard, {
    key: r.id,
    kind: "reading",
    sign: r.sign,
    signMark: r.mark,
    date: r.date,
    readingTime: r.time,
    unread: r.unread,
    excerpt: s.missing && r.id === 'r1' ? undefined : r.excerpt,
    onOpen: () => go('work')
  })))), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(SectionHeader, {
    eyebrow: "Longer",
    title: "Latest articles",
    action: "All",
    onAction: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, A.articles.slice(0, 2).map(a => /*#__PURE__*/React.createElement(ContentCard, {
    key: a.id,
    kind: "article",
    title: a.title,
    date: a.date,
    readingTime: a.time,
    excerpt: a.excerpt,
    onOpen: () => go('work')
  })))), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(SectionHeader, {
    eyebrow: "Hers",
    title: "Offers",
    rule: true,
    mark: A.G.sun
  }), s.empty ? /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    mark: A.G.jupiter,
    title: "Nothing open just now",
    body: "Classes run in terms. The next one is announced on Discord first."
  }) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, A.offers.slice(0, 2).map(o => /*#__PURE__*/React.createElement(OfferCard, {
    key: o.id,
    title: o.title,
    body: o.body,
    price: o.price,
    cadence: o.cadence,
    mark: o.mark,
    membersOnly: o.membersOnly,
    locked: o.membersOnly && !s.member,
    soldOut: o.soldOut,
    href: o.href,
    onOpen: o.membersOnly && !s.member ? e => {
      e.preventDefault();
    } : undefined
  })))), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    eyebrow: "Elsewhere",
    title: "Her site"
  }), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "shrutivtuber.com",
    description: "Instruments for magick, built live from Athens.",
    href: "https://shrutivtuber.com",
    external: true
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Watch on Twitch",
    href: "https://twitch.tv",
    external: true,
    leading: /*#__PURE__*/React.createElement("img", {
      src: "../../assets/icons/twitch.svg",
      alt: "",
      width: "18",
      height: "18",
      style: {
        opacity: .72
      }
    })
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Discord",
    description: "Streams are announced here first",
    href: "#",
    external: true,
    leading: /*#__PURE__*/React.createElement("img", {
      src: "../../assets/icons/discord.svg",
      alt: "",
      width: "18",
      height: "18",
      style: {
        opacity: .72
      }
    })
  })), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: '2px 4px 0',
      color: 'var(--faint)'
    }
  }, "Support, the shop and classes open in your browser, where the address bar says whose they are."))));
}
function SkyScreen({
  s,
  seg,
  setSeg,
  go
}) {
  const A = window.AL;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Sky",
    subtitle: s.place,
    hour: true,
    actions: /*#__PURE__*/React.createElement(IconButton, {
      icon: "menu_book",
      label: "Sky drawer",
      onClick: () => go('drawer')
    })
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 12px 10px',
      flex: 'none'
    }
  }, /*#__PURE__*/React.createElement(SegmentedControl, {
    label: "Sky view",
    active: seg,
    onChange: setSeg,
    segments: [{
      id: 'stations',
      label: 'Stations'
    }, {
      id: 'hours',
      label: 'Hours'
    }, {
      id: 'coming',
      label: 'Coming'
    }]
  })), /*#__PURE__*/React.createElement(Body, {
    pad: 12,
    gap: 12
  }, /*#__PURE__*/React.createElement(DayArc, {
    sunrise: "06:58",
    sunset: "19:51",
    now: "13:42",
    phase: 0.38,
    ruler: s.hour
  }), s.offline && /*#__PURE__*/React.createElement(Banner, {
    tone: "note",
    title: "Still computing, still correct"
  }, "The sky does not need the network. Only her readings do."), s.loading && /*#__PURE__*/React.createElement(Refreshing, null), seg === 'stations' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(DataTable, {
    columns: A.stations.columns,
    rows: A.stations.rows,
    caption: `${s.place} · GMT+3 · geocentric, apparent · ${s.sunrise === 'civil' ? 'civil dawn' : 'sunrise'} convention`
  }), /*#__PURE__*/React.createElement(Card, {
    tone: "warning"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 9,
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement(Glyph, {
    name: "retrograde",
    tone: "rose",
    size: "md"
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 var(--size-label)/1.35 var(--font-body)',
      color: 'var(--rose)'
    }
  }, "Mercury is retrograde until Thursday"), /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 3
    }
  }, "Every affected figure carries \u211E as well as the tint.")))), /*#__PURE__*/React.createElement(Provenance, {
    rule: "Tropical zodiac, apparent positions"
  })), seg === 'hours' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement(HourChip, {
    ruler: s.hour,
    ordinal: 7,
    diurnal: true,
    ends: "14:12"
  }), /*#__PURE__*/React.createElement(DataRow, {
    mark: A.G.sun,
    label: "Sunrise",
    value: "06:58"
  }), /*#__PURE__*/React.createElement(DataRow, {
    mark: A.G.sun,
    label: "Sunset",
    value: "19:51"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Day hour",
    value: "62 minutes"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Night hour",
    value: "58 minutes"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      paddingTop: 8,
      borderTop: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => go('sunrise'),
    style: {
      appearance: 'none',
      background: 'none',
      border: 0,
      padding: 0,
      color: 'var(--accent)',
      font: '500 var(--size-caption)/1 var(--font-body)',
      cursor: 'pointer'
    }
  }, "Sunrise convention: ", s.sunrise === 'civil' ? 'civil dawn' : 'upper limb', " \u2014 change")))), /*#__PURE__*/React.createElement(DataTable, {
    columns: A.hours.columns,
    rows: A.hours.rows,
    caption: "Day hours \xB7 9 September"
  }), /*#__PURE__*/React.createElement(Provenance, {
    rule: s.sunrise === 'civil' ? 'Civil dawn: the Sun is 6° below the horizon' : 'Sunrise: the Sun’s upper limb clears the horizon'
  })), seg === 'coming' && /*#__PURE__*/React.createElement(React.Fragment, null, s.empty ? /*#__PURE__*/React.createElement(EmptyState, {
    mark: A.G.saturn,
    title: "Nothing in the next forty days",
    body: "The sky is quiet. That happens, and it is not an error."
  }) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, A.coming.map((c, i) => /*#__PURE__*/React.createElement(Card, {
    key: i,
    tone: c.tone === 'caution' ? 'warning' : 'plain'
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      gap: 12,
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      placeItems: 'center',
      width: 34,
      height: 34,
      borderRadius: 'var(--radius-full)',
      background: 'var(--inset)',
      border: '1px solid ' + (c.tone === 'caution' ? 'color-mix(in srgb,var(--rose) 40%,transparent)' : 'var(--line)')
    }
  }, /*#__PURE__*/React.createElement(Glyph, {
    char: c.mark,
    tone: c.tone === 'caution' ? 'rose' : 'gilt',
    size: "md"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      color: c.tone === 'caution' ? 'var(--rose)' : 'var(--faint)'
    }
  }, c.when), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 17px/1.3 var(--font-display)',
      color: 'var(--ink)',
      marginTop: 4
    }
  }, c.title), /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 3
    }
  }, c.detail)))))), /*#__PURE__*/React.createElement(Provenance, {
    rule: "Times in Athens, with your local conversion where they differ"
  }))));
}
Object.assign(window, {
  HomeScreen,
  SkyScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/Screens1.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/Screens2.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Screens 5–8: Chart (form and result), Letters (reckoning and sigil). */

function ChartScreen({
  s,
  cast,
  setCast,
  go
}) {
  const A = window.AL;
  const known = !s.noBirthTime;
  if (!cast) return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Cast a chart",
    hour: false
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, s.error && /*#__PURE__*/React.createElement(Banner, {
    tone: "error",
    title: "That place could not be resolved",
    action: "Choose from the list",
    onAction: () => go('place')
  }, "The name matched four places and none of them was obvious."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 14
    }
  }, /*#__PURE__*/React.createElement(TextField, {
    label: "Name",
    placeholder: "Whose chart is this?",
    defaultValue: s.longContent ? 'Anastasía Papadopoúlou-Georgiádis' : ''
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Date of birth",
    mono: true,
    placeholder: "14 \xB7 03 \xB7 1996"
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Time of birth",
    mono: true,
    placeholder: "14:05",
    disabled: !known,
    helper: known ? 'Local clock time at the place of birth.' : 'Left unknown — the angles will not be reckoned.'
  }), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "checkbox",
    label: "The time of birth is unknown",
    rule: "The chart is still cast. The ascendant, the midheaven and the houses are not.",
    checked: !known,
    onChange: () => s.set('noBirthTime', known)
  }), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Place of birth",
    value: s.place,
    onClick: () => go('place')
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Zodiac",
    value: "Tropical",
    onClick: () => {}
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Houses",
    value: known ? 'Whole sign' : 'Not reckoned',
    disabled: !known,
    onClick: () => {}
  }))), /*#__PURE__*/React.createElement(Card, {
    tone: "inset"
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      marginBottom: 8
    }
  }, "Two authorities, two charts"), /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      lineHeight: 1.6
    }
  }, "Tropical and sidereal disagree by about 24\xB0 and neither is a setting you should have to find. Change it here, on the chart, and it recomputes.")), /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    full: true,
    onClick: () => setCast(true),
    loading: s.loading
  }, "Cast the chart"), s.empty && /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    mark: A.G.mercury,
    title: "No saved charts",
    body: "Charts you cast are kept on this phone until you delete them."
  })));
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Anastas\xEDa",
    subtitle: `14 March 1996 · ${known ? '14:05' : 'time unknown'} · ${s.place}`,
    back: true,
    onBack: () => setCast(false),
    hour: false,
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(IconButton, {
      icon: "ios_share",
      label: "Share this chart"
    }), /*#__PURE__*/React.createElement(IconButton, {
      icon: "bookmark",
      label: "Save this chart"
    }))
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 12,
    gap: 14
  }, !known && /*#__PURE__*/React.createElement(Banner, {
    tone: "caution",
    title: "The angles are not reckoned"
  }, "With no birth time there is no ascendant and no midheaven, so this wheel has no houses. Everything drawn here is true; the things that are missing are missing on purpose."), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '4px 0 0'
    }
  }, /*#__PURE__*/React.createElement(ChartWheel, {
    size: 300,
    asc: 214.3,
    mc: 128.9,
    cusps: known ? A.cusps : undefined,
    housesKnown: known,
    bodies: A.bodies,
    aspects: A.aspects
  })), /*#__PURE__*/React.createElement(ChipRow, null, /*#__PURE__*/React.createElement(Chip, {
    kind: "choice",
    selected: true
  }, "Tropical"), /*#__PURE__*/React.createElement(Chip, {
    kind: "choice"
  }, "Sidereal \xB7 Lahiri"), /*#__PURE__*/React.createElement(Chip, {
    kind: "choice",
    disabled: !known
  }, "Whole sign"), /*#__PURE__*/React.createElement(Chip, {
    kind: "choice",
    disabled: !known
  }, "Placidus")), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      marginBottom: 8
    }
  }, "Positions"), A.chartTable.map((r, i) => /*#__PURE__*/React.createElement(DataRow, {
    key: i,
    mark: r.mark,
    label: r.label,
    value: r.value,
    tone: r.rose ? 'rose' : 'ink'
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 10,
      paddingTop: 10,
      borderTop: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement(DataRow, {
    label: "Ascendant",
    value: known ? '04\u00b0 18\u2032 \u264F' : 'Not reckoned',
    tone: known ? 'ink' : 'faint'
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Midheaven",
    value: known ? '08\u00b0 54\u2032 \u264C' : 'Not reckoned',
    tone: known ? 'ink' : 'faint'
  }))), /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      marginBottom: 8
    }
  }, "Aspects"), /*#__PURE__*/React.createElement(DataRow, {
    mark: A.G.sun,
    label: "Sun opposite Saturn",
    value: "3\\u00b0 06\\u2032 \\u00b7 separating"
  }), /*#__PURE__*/React.createElement(DataRow, {
    mark: A.G.moon,
    label: "Moon trine Venus",
    value: "1\\u00b0 12\\u2032 \\u00b7 applying"
  }), /*#__PURE__*/React.createElement(DataRow, {
    mark: A.G.venus,
    label: "Venus square Uranus",
    value: "2\\u00b0 00\\u2032 \\u00b7 applying"
  }), /*#__PURE__*/React.createElement(DataRow, {
    mark: A.G.mercury,
    label: "Mercury sextile Jupiter",
    value: "2\\u00b0 48\\u2032 \\u00b7 separating"
  })), /*#__PURE__*/React.createElement(Provenance, {
    rule: known ? 'Tropical zodiac, whole-sign houses' : 'Tropical zodiac, no houses reckoned'
  })));
}
const SCRIPTS = ['Greek', 'Hebrew', 'Arabic', 'Coptic', 'Devanagari', 'English'];
function LettersScreen({
  s,
  seg,
  setSeg
}) {
  const A = window.AL;
  const [script, setScript] = React.useState('Greek');
  const [method, setMethod] = React.useState('rose');
  const kata = script === 'Devanagari';
  const sum = A.isopsephy.reduce((n, r) => n + r.v, 0);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Letters",
    hour: true
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 12px 10px',
      flex: 'none'
    }
  }, /*#__PURE__*/React.createElement(SegmentedControl, {
    label: "Letters view",
    active: seg,
    onChange: setSeg,
    segments: [{
      id: 'reckoning',
      label: 'Reckoning'
    }, {
      id: 'sigil',
      label: 'Sigil'
    }]
  })), /*#__PURE__*/React.createElement(Body, {
    pad: 12,
    gap: 13
  }, seg === 'reckoning' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(ChipRow, null, SCRIPTS.map(x => /*#__PURE__*/React.createElement(Chip, {
    key: x,
    kind: "choice",
    selected: script === x,
    onClick: () => setScript(x)
  }, x))), /*#__PURE__*/React.createElement(TextField, {
    label: "Word or phrase",
    mono: true,
    defaultValue: kata ? '\u0915\u091f\u092a\u092f\u093e\u0926\u093f' : '\u03a3\u03bf\u03c6\u03af\u03b1',
    helper: kata ? 'Kaṭapayādi is place-value, so this is read right to left.' : 'Greek Milesian, with digamma, koppa and sampi.'
  }), kata ? /*#__PURE__*/React.createElement(Card, {
    tone: "warning"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 9,
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement(Glyph, {
    char: A.G.mercury,
    tone: "rose",
    size: "md"
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 var(--size-label)/1.35 var(--font-body)',
      color: 'var(--rose)'
    }
  }, "There is no sum to give you"), /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 4,
      lineHeight: 1.6
    }
  }, "Ka\u1E6Dapay\u0101di is a place-value notation, not a gematria. The app gives the digits, read right to left, and refuses to add them \u2014 a Greek sum and a Devanagari reading of equal value are not a correspondence.")))) : /*#__PURE__*/React.createElement(CodeBlock, {
    label: script + ' \u00b7 letter by letter',
    align: "right",
    copyable: true
  }, A.isopsephy.map(r => r.ch + '   ' + String(r.v).padStart(4, ' ')).join('\n') + '\n\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n    ' + sum), !kata && /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement(DataRow, {
    label: "Total",
    value: String(sum),
    tone: "gilt"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Digital root",
    value: "7"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Matches in this system",
    value: "4 words"
  })), /*#__PURE__*/React.createElement(Provenance, {
    engine: "Isopsephy tables 1.2",
    rule: kata ? 'Kaṭapayādi, place-value, right to left' : 'Milesian, finals unvalued',
    extra: /*#__PURE__*/React.createElement(DataRow, {
      label: "Matching",
      value: "Within one system only",
      small: true,
      tone: "faint"
    })
  })), seg === 'sigil' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(TextField, {
    label: "Statement of intent",
    multiline: true,
    rows: 3,
    defaultValue: "It is my will to finish the ephemeris before the equinox",
    helper: "Repeated letters are struck out before the figure is drawn."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8
    }
  }, [['rose', 'Rose cross'], ['kamea', 'Kamea'], ['letters', 'Letter path']].map(([id, lab]) => /*#__PURE__*/React.createElement(Chip, {
    key: id,
    kind: "choice",
    selected: method === id,
    onClick: () => setMethod(id)
  }, lab))), /*#__PURE__*/React.createElement(Card, {
    tone: "inset",
    pad: 12
  }, s.empty ? /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    mark: A.G.saturn,
    title: "Nothing left to draw",
    body: "Every letter in that statement repeats. Strike fewer, or write it another way."
  }) : /*#__PURE__*/React.createElement(SigilPlate, {
    method: method
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "outlined",
    full: true,
    iconLeft: /*#__PURE__*/React.createElement(Icon, {
      name: "download",
      size: 18,
      tone: "accent"
    })
  }, "Save as SVG"), /*#__PURE__*/React.createElement(Button, {
    variant: "outlined",
    full: true,
    iconLeft: /*#__PURE__*/React.createElement(Icon, {
      name: "ios_share",
      size: 18,
      tone: "accent"
    })
  }, "Share")), /*#__PURE__*/React.createElement(Provenance, {
    engine: "Sigil generator 1.0",
    rule: method === 'rose' ? 'Rose cross, Latin ring' : method === 'kamea' ? 'Kamea of Saturn, 3×3' : 'Letter path, struck repeats'
  }))));
}

/* The sigil is the instrument's own output — a figure drawn over the chosen
   grid, not artwork. Kamea and letter-path draw a real polyline; the rose cross
   is a ring with the path chorded across it. */
function SigilPlate({
  method
}) {
  const pts = {
    kamea: [[1, 0], [2, 2], [0, 1], [2, 0], [1, 2], [0, 0], [2, 1]],
    letters: [[0, 0], [2, 1], [1, 2], [0, 2], [2, 0], [1, 1]]
  }[method];
  const size = 240,
    m = 34,
    step = (size - m * 2) / 2;
  const xy = ([c, r]) => [m + c * step, m + r * step];
  if (method === 'rose') {
    const cx = size / 2,
      r1 = 96,
      r2 = 74;
    const ring = Array.from({
      length: 22
    }, (_, i) => {
      const a = i / 22 * 2 * Math.PI - Math.PI / 2;
      return [cx + r1 * Math.cos(a), cx + r1 * Math.sin(a)];
    });
    const path = [0, 7, 3, 15, 11, 19, 2].map(i => ring[i]);
    return /*#__PURE__*/React.createElement("svg", {
      viewBox: `0 0 ${size} ${size}`,
      width: "100%",
      style: {
        maxWidth: size,
        display: 'block',
        margin: '0 auto'
      },
      role: "img",
      "aria-label": "Sigil drawn on the rose cross"
    }, /*#__PURE__*/React.createElement("circle", {
      cx: cx,
      cy: cx,
      r: r1,
      fill: "none",
      stroke: "var(--gilt-dim)",
      strokeWidth: "1"
    }), /*#__PURE__*/React.createElement("circle", {
      cx: cx,
      cy: cx,
      r: r2,
      fill: "none",
      stroke: "var(--line)",
      strokeWidth: "1"
    }), ring.map(([x, y], i) => /*#__PURE__*/React.createElement("circle", {
      key: i,
      cx: x,
      cy: y,
      r: "2",
      fill: "var(--line-strong)"
    })), /*#__PURE__*/React.createElement("polyline", {
      points: path.map(p => p.join(',')).join(' '),
      fill: "none",
      stroke: "var(--gilt)",
      strokeWidth: "1.8",
      strokeLinejoin: "round",
      strokeLinecap: "round"
    }), /*#__PURE__*/React.createElement("circle", {
      cx: path[0][0],
      cy: path[0][1],
      r: "4",
      fill: "none",
      stroke: "var(--gilt-bright)",
      strokeWidth: "1.6"
    }), /*#__PURE__*/React.createElement("rect", {
      x: path[path.length - 1][0] - 4,
      y: path[path.length - 1][1] - 4,
      width: "8",
      height: "8",
      fill: "none",
      stroke: "var(--gilt-bright)",
      strokeWidth: "1.6"
    }));
  }
  return /*#__PURE__*/React.createElement("svg", {
    viewBox: `0 0 ${size} ${size}`,
    width: "100%",
    style: {
      maxWidth: size,
      display: 'block',
      margin: '0 auto'
    },
    role: "img",
    "aria-label": 'Sigil drawn on the ' + method + ' grid'
  }, [0, 1, 2].map(r => [0, 1, 2].map(c => {
    const [x, y] = xy([c, r]);
    return /*#__PURE__*/React.createElement("circle", {
      key: r + '-' + c,
      cx: x,
      cy: y,
      r: "2.5",
      fill: "var(--line-strong)"
    });
  })), method === 'kamea' && [0, 1, 2].map(i => /*#__PURE__*/React.createElement("g", {
    key: i
  }, /*#__PURE__*/React.createElement("line", {
    x1: m,
    y1: m + i * step,
    x2: size - m,
    y2: m + i * step,
    stroke: "var(--line)",
    strokeWidth: "0.8"
  }), /*#__PURE__*/React.createElement("line", {
    x1: m + i * step,
    y1: m,
    x2: m + i * step,
    y2: size - m,
    stroke: "var(--line)",
    strokeWidth: "0.8"
  }))), /*#__PURE__*/React.createElement("polyline", {
    points: pts.map(p => xy(p).join(',')).join(' '),
    fill: "none",
    stroke: "var(--gilt)",
    strokeWidth: "2",
    strokeLinejoin: "round",
    strokeLinecap: "round"
  }), /*#__PURE__*/React.createElement("circle", _extends({}, (() => {
    const [x, y] = xy(pts[0]);
    return {
      cx: x,
      cy: y
    };
  })(), {
    r: "5",
    fill: "none",
    stroke: "var(--gilt-bright)",
    strokeWidth: "1.6"
  })), (() => {
    const [x, y] = xy(pts[pts.length - 1]);
    return /*#__PURE__*/React.createElement("rect", {
      x: x - 5,
      y: y - 5,
      width: "10",
      height: "10",
      fill: "none",
      stroke: "var(--gilt-bright)",
      strokeWidth: "1.6"
    });
  })());
}
Object.assign(window, {
  ChartScreen,
  LettersScreen,
  SigilPlate
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/Screens2.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/Screens3.jsx
try { (() => {
/* Screens 9–10, 13: Practice (Read and Mine) and Settings. */

function PracticeScreen({
  s,
  seg,
  setSeg,
  go
}) {
  const A = window.AL;
  const [filter, setFilter] = React.useState('new');
  if (!s.signedIn && seg === 'mine') seg = 'read';
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Practice",
    large: true,
    hour: true,
    actions: /*#__PURE__*/React.createElement(IconButton, {
      icon: "edit_square",
      label: "Write a reading",
      onClick: () => go('write')
    })
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 12px 10px',
      flex: 'none',
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(SegmentedControl, {
    label: "Practice view",
    active: seg,
    onChange: setSeg,
    segments: [{
      id: 'read',
      label: 'Read'
    }, {
      id: 'mine',
      label: 'Mine'
    }]
  }), seg === 'read' && /*#__PURE__*/React.createElement(ChipRow, null, [['new', 'Newest'], ['unanswered', 'Unanswered'], ['week', 'This week'], ['mine-sign', 'My sign']].map(([id, lab]) => /*#__PURE__*/React.createElement(Chip, {
    key: id,
    kind: "filter",
    selected: filter === id,
    onClick: () => setFilter(filter === id ? '' : id)
  }, lab)))), /*#__PURE__*/React.createElement(Body, {
    pad: 12,
    gap: 10
  }, s.offline && /*#__PURE__*/React.createElement(Banner, {
    tone: "offline",
    title: "The room is not reachable"
  }, "Readings you have already opened are still here. Anything you write is kept as a draft and posted when you are back."), s.loading && [0, 1, 2].map(i => /*#__PURE__*/React.createElement(Card, {
    key: i
  }, /*#__PURE__*/React.createElement(Skeleton, {
    lines: 2
  }))), !s.loading && seg === 'read' && (s.empty ? /*#__PURE__*/React.createElement(EmptyState, {
    mark: A.G.saturn,
    title: "The room is quiet",
    body: "Nobody has posted a reading this week. Yours would be the first.",
    action: /*#__PURE__*/React.createElement(Button, {
      onClick: () => go('write')
    }, "Write one")
  }) : /*#__PURE__*/React.createElement(React.Fragment, null, A.feed.map(w => /*#__PURE__*/React.createElement(WorkCard, {
    key: w.id,
    title: w.title,
    author: w.author,
    date: w.date,
    excerpt: s.missing && w.id === 'w2' ? undefined : w.excerpt,
    votes: w.votes,
    myVote: w.myVote,
    comments: w.comments,
    sign: w.sign,
    onOpen: () => go('work'),
    onVote: s.signedIn ? () => {} : undefined
  })), !s.signedIn && /*#__PURE__*/React.createElement(Card, {
    tone: "inset"
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      lineHeight: 1.6
    }
  }, "You are reading as a guest. Sign in to vote, comment, or put your own reading in front of the room."), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 10,
      display: 'flex',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    onClick: () => go('account')
  }, "Sign in"), /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    variant: "text"
  }, "What signing in gets me"))))), !s.loading && seg === 'mine' && (!s.signedIn ? /*#__PURE__*/React.createElement(EmptyState, {
    mark: A.G.mercury,
    title: "Your work would live here",
    body: "Drafts are kept on this phone. Posting one needs an account, because the room needs to know who wrote it.",
    action: /*#__PURE__*/React.createElement(Button, {
      onClick: () => go('account')
    }, "Sign in"),
    secondary: /*#__PURE__*/React.createElement(Button, {
      variant: "text",
      onClick: () => go('write')
    }, "Write a draft first")
  }) : s.empty ? /*#__PURE__*/React.createElement(EmptyState, {
    mark: A.G.moon,
    title: "Nothing written yet",
    body: "A reading here is a few hundred words on one chart. It does not have to be right.",
    action: /*#__PURE__*/React.createElement(Button, {
      onClick: () => go('write')
    }, "Write your first")
  }) : A.mine.map(w => /*#__PURE__*/React.createElement(WorkCard, {
    key: w.id,
    mine: true,
    title: w.title,
    date: w.date,
    excerpt: w.excerpt,
    votes: w.votes,
    comments: w.comments,
    status: w.status,
    onOpen: () => go('work')
  })))));
}
function SettingsScreen({
  s,
  go
}) {
  const A = window.AL;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Settings",
    large: true,
    hour: false
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Account",
    description: s.signedIn ? 'soror@shrutivtuber.com' : 'Not signed in',
    value: s.signedIn ? s.member ? 'Member' : 'Free' : undefined,
    onClick: () => go('account')
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Notifications",
    value: s.signedIn ? '3 on' : 'Live only',
    onClick: () => go('notifications')
  })), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "The sky, where you are"), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Place",
    description: "Used for sunrise, sunset and the hours",
    value: s.place,
    onClick: () => go('place')
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Sunrise convention",
    description: "Which moment starts the day",
    value: s.sunrise === 'civil' ? 'Civil dawn' : 'Upper limb',
    onClick: () => go('sunrise')
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Zodiac",
    value: "Tropical",
    onClick: () => {}
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Show times in",
    value: "Athens and yours",
    onClick: () => {}
  }))), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "On this phone"), /*#__PURE__*/React.createElement(Card, {
    pad: 0
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '4px 16px'
    }
  }, /*#__PURE__*/React.createElement(Switch, {
    label: "Reduce motion",
    description: "Follows your system setting unless you change it here",
    checked: s.reduceMotion,
    onChange: v => s.set('reduceMotion', v)
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement(Switch, {
    label: "Keep readings offline",
    description: "About 4 MB. They are already downloaded.",
    checked: true,
    onChange: () => {}
  }))), /*#__PURE__*/React.createElement(ChipRow, null, /*#__PURE__*/React.createElement(Chip, {
    kind: "meta",
    meta: "2.1 MB"
  }, "Greek"), /*#__PURE__*/React.createElement(Chip, {
    kind: "meta",
    meta: "1.8 MB"
  }, "Devanagari"), /*#__PURE__*/React.createElement(Chip, {
    kind: "meta",
    meta: "1.4 MB"
  }, "Hebrew"), /*#__PURE__*/React.createElement(Chip, {
    kind: "meta",
    meta: "0.9 MB"
  }, "Coptic")), s.loading && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement(Progress, {
    kind: "bar",
    value: 62,
    label: "Greek pack"
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption"
  }, "Greek pack \xB7 1.3 of 2.1 MB")), s.error && /*#__PURE__*/React.createElement(Banner, {
    tone: "error",
    title: "The Hebrew pack did not finish",
    action: "Try again"
  }, "1.1 of 1.4 MB arrived. Nothing else was affected."), s.empty && /*#__PURE__*/React.createElement(Banner, {
    tone: "note",
    title: "No packs installed"
  }, "Reckoning works in Greek and English without a pack.")), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Hers"), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Support her work",
    description: "Opens your browser",
    href: "https://shrutivtuber.com/support",
    external: true
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "The shop",
    href: "https://shrutivtuber.com/shop",
    external: true
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Classes",
    href: "https://shrutivtuber.com/classes",
    external: true
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "shrutivtuber.com",
    href: "https://shrutivtuber.com",
    external: true
  })), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: '0 4px'
    }
  }, "Nothing is bought inside Astrolabe. These open your browser, where the address bar says whose checkout it is.")), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "About"), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Licences",
    description: "AGPL-3.0 \xB7 every asset ships in the public repo",
    onClick: () => go('licences')
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Source",
    description: "ShrutiVtuber/astrolabe",
    href: "#",
    external: true
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '2px 4px'
    }
  }, /*#__PURE__*/React.createElement(DataRow, {
    label: "Astrolabe",
    value: "1.0.0 (214)",
    small: true,
    tone: "faint"
  }), /*#__PURE__*/React.createElement(DataRow, {
    label: "Ephemeris",
    value: "Swiss Ephemeris 2.10.03",
    small: true,
    tone: "faint"
  })), /*#__PURE__*/React.createElement("div", {
    className: "rule",
    style: {
      marginTop: 6
    }
  }, A.G.moon, '\ufe0e'))));
}
Object.assign(window, {
  PracticeScreen,
  SettingsScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/Screens3.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/Screens4.jsx
try { (() => {
/* Screens 11–12, 14–18: one work, the writing screen, account, notifications,
   licences, the place picker and the sky drawer. */

function WorkScreen({
  s,
  go
}) {
  const A = window.AL;
  const [vote, setVote] = React.useState(1);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "A reading",
    back: true,
    onBack: () => go(null),
    hour: false,
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(IconButton, {
      icon: "ios_share",
      label: "Share"
    }), /*#__PURE__*/React.createElement(IconButton, {
      icon: "more_vert",
      label: "More"
    }))
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Practice \xB7 Capricorn"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: '500 26px/1.22 var(--font-display)',
      color: 'var(--ink)',
      textWrap: 'pretty'
    }
  }, "Saturn on the descendant, and what it asked of me"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: 24,
      height: 24,
      borderRadius: 99,
      background: 'var(--veil)',
      border: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      color: 'var(--soft)'
    }
  }, "korax"), /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    "aria-hidden": "true"
  }, "\xB7"), /*#__PURE__*/React.createElement("span", {
    className: "t-caption t-tabular"
  }, "9 September, 18:20 Athens"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      padding: '12px 14px',
      background: 'var(--inset)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)'
    }
  }, /*#__PURE__*/React.createElement(VoteControl, {
    value: 14 + (vote === 1 ? 0 : vote === -1 ? -2 : -1),
    mine: s.signedIn ? vote : 0,
    onVote: s.signedIn ? setVote : undefined,
    disabled: !s.signedIn
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      color: 'var(--soft)'
    }
  }, s.signedIn ? 'Your vote is counted and can be changed.' : 'Sign in to vote or comment.')), /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    variant: "outlined",
    onClick: () => {}
  }, "Comment")), /*#__PURE__*/React.createElement(Prose, {
    drop: true
  }, /*#__PURE__*/React.createElement("p", null, "I have had this transit for eleven months and I have spent most of them arguing with it. Saturn came to the seventh by whole sign last November, and the first thing it did was make every conversation take twice as long."), /*#__PURE__*/React.createElement("p", null, "What changed was not the transit. What changed was that I stopped treating the descendant as a place where other people happen to me."), /*#__PURE__*/React.createElement("blockquote", null, "Saturn does not ask. It invoices \u2014 and then it asks whether you were going to pay in instalments."), /*#__PURE__*/React.createElement("p", null, "The chart is tropical, whole sign, cast for 14:05 in Thessaloniki. I am not confident about the seventh-house ruler and I would like to be argued with about it."), s.longContent && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("h2", null, "The method, at length"), /*#__PURE__*/React.createElement("p", null, "What follows is the part nobody asked for. I looked at every ingress into the seventh for the last four years, and I logged what I noticed within the week either side."), /*#__PURE__*/React.createElement("p", null, "The pattern that survived the log is not the one I expected, and it is the only reason I am posting this rather than keeping it in the notes app where it has lived since March."))), /*#__PURE__*/React.createElement("div", {
    className: "rule"
  }, A.G.saturn, '\ufe0e'), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    eyebrow: `${A.comments.length} comments`,
    title: "The room"
  }), A.comments.map(c => /*#__PURE__*/React.createElement("div", {
    key: c.id,
    style: {
      display: 'grid',
      gridTemplateColumns: 'auto 1fr',
      gap: 12,
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement(VoteControl, {
    value: c.votes,
    compact: true,
    disabled: !s.signedIn
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0,
      display: 'grid',
      gap: 5
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-caption",
    style: {
      color: c.her ? 'var(--gilt)' : 'var(--soft)',
      fontWeight: c.her ? 600 : 400
    }
  }, c.author), c.her && /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      color: 'var(--gilt)'
    }
  }, "Hers"), /*#__PURE__*/React.createElement("span", {
    className: "t-caption t-tabular"
  }, c.date)), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '400 15px/1.6 var(--font-body)',
      color: 'var(--soft)',
      textWrap: 'pretty'
    }
  }, c.body)))), s.signedIn ? /*#__PURE__*/React.createElement(TextField, {
    label: "Add a comment",
    multiline: true,
    rows: 3,
    placeholder: "Argue with it."
  }) : /*#__PURE__*/React.createElement(Card, {
    tone: "inset"
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-caption"
  }, "Sign in to reply. The room keeps its own guidelines; they are two paragraphs long and worth reading.")))));
}
function WriteScreen({
  s,
  go
}) {
  const [saved, setSaved] = React.useState(false);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Write a reading",
    back: true,
    onBack: () => go(null),
    hour: false,
    actions: /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: "text",
      onClick: () => setSaved(true)
    }, "Save draft")
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 14
  }, s.offline && /*#__PURE__*/React.createElement(Banner, {
    tone: "offline",
    title: "You are writing offline"
  }, "Drafts live on this phone. This one will be posted when the room is reachable again."), s.error && /*#__PURE__*/React.createElement(Banner, {
    tone: "error",
    title: "That draft did not post",
    action: "Try again"
  }, "The room answered, but not with a receipt. Nothing was lost."), /*#__PURE__*/React.createElement(TextField, {
    label: "Title",
    placeholder: "What is this reading about?",
    defaultValue: s.longContent ? 'A very long title that runs on past the width of a phone and keeps going' : '',
    maxLength: 120,
    counter: true,
    value: s.longContent ? undefined : ''
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "The chart it is about"), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Attach a chart",
    description: "One of yours, or cast a new one",
    onClick: () => {}
  }))), /*#__PURE__*/React.createElement(TextField, {
    label: "The reading",
    multiline: true,
    rows: s.longContent ? 14 : 10,
    maxLength: 4000,
    counter: true,
    placeholder: "A few hundred words on one chart. It does not have to be right.",
    defaultValue: s.longContent ? 'I have had this transit for eleven months and I have spent most of them arguing with it. Saturn came to the seventh by whole sign last November, and the first thing it did was make every conversation take twice as long.\n\nWhat changed was not the transit.' : ''
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Before you post"), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "checkbox",
    label: "This is my own work",
    rule: "Readings are argued with by name. Quoting somebody else is fine; passing it off is not."
  }), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "checkbox",
    label: "Show my sign on it",
    rule: "Optional. It changes how the room reads you, which is sometimes the point."
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "outlined",
    full: true,
    onClick: () => setSaved(true)
  }, "Save draft"), /*#__PURE__*/React.createElement(Button, {
    full: true,
    disabled: !s.signedIn,
    onClick: () => go(null)
  }, "Post it")), !s.signedIn && /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: 0,
      textAlign: 'center'
    }
  }, "Drafts are kept without an account. Posting needs one."), /*#__PURE__*/React.createElement(Snackbar, {
    open: saved,
    action: "Undo",
    onAction: () => setSaved(false)
  }, "Draft saved.")));
}
function AccountScreen({
  s,
  go
}) {
  if (!s.signedIn) return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Account",
    back: true,
    onBack: () => go(null),
    hour: false
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8,
      marginTop: 8
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: '500 24px/1.25 var(--font-display)',
      color: 'var(--ink)'
    }
  }, "An account is only for the practice room"), /*#__PURE__*/React.createElement("p", {
    className: "t-body",
    style: {
      margin: 0,
      textWrap: 'pretty'
    }
  }, "Everything else \u2014 the sky, the hours, the chart, the letters \u2014 works without one, offline, and always will.")), s.error && /*#__PURE__*/React.createElement(Banner, {
    tone: "error",
    title: "Sign-in failed",
    action: "Try again"
  }, "The site answered, but not with a token."), /*#__PURE__*/React.createElement(TextField, {
    label: "Email",
    type: "email",
    placeholder: "you@example.com"
  }), /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    full: true,
    loading: s.loading,
    onClick: () => s.set('signedIn', true)
  }, "Send me a link"), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: '-4px 0 0'
    }
  }, "No password. A link arrives, you tap it, you are in. The link works once and lasts an hour."), /*#__PURE__*/React.createElement("div", {
    className: "rule rule-plain"
  }, "\xB7"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "If you make an account"), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "checkbox",
    label: "Email me her newsletter",
    rule: "About one a month. Unsubscribe in one tap, from any of them."
  }), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "checkbox",
    label: "Tell me when somebody replies to my work",
    rule: "Only replies to you. Never a digest."
  }), /*#__PURE__*/React.createElement(ChoiceRow, {
    type: "checkbox",
    label: "I have read the room\u2019s guidelines",
    rule: "Two paragraphs. Required, and not bundled with anything else."
  }))));
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Account",
    back: true,
    onBack: () => go(null),
    hour: false
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 14,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: 48,
      height: 48,
      borderRadius: 99,
      background: 'var(--veil)',
      border: '1px solid var(--line)',
      display: 'grid',
      placeItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Glyph, {
    name: "moon",
    tone: "gilt",
    size: "lg"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 18px/1.3 var(--font-display)',
      color: 'var(--ink)'
    }
  }, "soror@shrutivtuber.com"), /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 2
    }
  }, s.member ? 'Member since March · renews 4 October' : 'Free account · joined March')))), !s.member && /*#__PURE__*/React.createElement(OfferCard, {
    title: "Become a member",
    price: "\u20AC6",
    cadence: "a month",
    mark: window.AL.G.venus,
    body: "The chart clinic, the members\u2019 readings, and the archive.",
    href: "https://shrutivtuber.com/support"
  }), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Your data"), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Your sign",
    value: "Capricorn",
    onClick: () => {}
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Saved charts",
    value: "3 on this phone",
    onClick: () => {}
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Export everything",
    description: "A single JSON file, sent to your email",
    onClick: () => {}
  }))), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Consents"), /*#__PURE__*/React.createElement(Card, {
    pad: 0
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '2px 16px'
    }
  }, /*#__PURE__*/React.createElement(Switch, {
    label: "Her newsletter",
    description: "About one a month",
    checked: true,
    onChange: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement(Switch, {
    label: "Replies to my work",
    description: "Only replies to you",
    checked: true,
    onChange: () => {}
  })))), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Sign out",
    onClick: () => s.set('signedIn', false),
    chevron: false
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Delete this account",
    danger: true,
    description: "The readings you posted stay, without your name",
    onClick: () => s.set('confirmDelete', true),
    chevron: false
  }))), /*#__PURE__*/React.createElement(Dialog, {
    open: s.confirmDelete,
    title: "Delete this account?",
    subtitle: "Your drafts go with it. Posted readings stay, without your name.",
    onClose: () => s.set('confirmDelete', false),
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "text",
      onClick: () => s.set('confirmDelete', false)
    }, "Keep it"), /*#__PURE__*/React.createElement(Button, {
      variant: "outlined",
      destructive: true,
      onClick: () => {
        s.set('confirmDelete', false);
        s.set('signedIn', false);
      }
    }, "Delete"))
  }, "This cannot be undone, and it is not the same as signing out."));
}
function NotificationsScreen({
  s,
  go
}) {
  const A = window.AL;
  const icons = {
    live: 'sensors',
    reply: 'mode_comment',
    sky: 'clear_night',
    reading: 'auto_stories'
  };
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Notifications",
    back: true,
    onBack: () => go(null),
    hour: false
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 16
  }, /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Tell me about"), /*#__PURE__*/React.createElement(Card, {
    pad: 0
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '2px 16px'
    }
  }, /*#__PURE__*/React.createElement(Switch, {
    label: "When she goes live",
    description: "Within ninety seconds",
    checked: true,
    onChange: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement(Switch, {
    label: "New readings",
    description: "Sunday nights, twelve at once",
    checked: true,
    onChange: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement(Switch, {
    label: "Stations and ingresses",
    description: "Computed here, so these arrive offline too",
    checked: s.signedIn,
    onChange: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)'
    }
  }), /*#__PURE__*/React.createElement(Switch, {
    label: "Replies to my work",
    description: "Needs an account",
    checked: false,
    disabled: !s.signedIn,
    onChange: () => {}
  }))), /*#__PURE__*/React.createElement("p", {
    className: "t-caption",
    style: {
      margin: '0 4px'
    }
  }, "The sky notifications are worked out on this phone, so they still arrive with no network.")), /*#__PURE__*/React.createElement("section", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    eyebrow: "Recent"
  }), s.empty ? /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    mark: A.G.moon,
    title: "Nothing yet",
    body: "When she goes live, or the sky does something worth knowing, it will be here."
  }) : A.notifications.map(n => /*#__PURE__*/React.createElement(Card, {
    key: n.id,
    tone: "tappable",
    onClick: () => go(n.kind === 'reply' ? 'work' : null)
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'auto 1fr auto',
      gap: 12,
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: icons[n.kind],
    size: 20,
    tone: n.kind === 'live' ? 'live' : 'gilt'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 15px/1.35 var(--font-body)',
      color: 'var(--ink)'
    }
  }, n.title), /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      marginTop: 3,
      textWrap: 'pretty'
    }
  }, n.body), /*#__PURE__*/React.createElement("div", {
    className: "t-caption t-tabular",
    style: {
      marginTop: 5,
      opacity: .8
    }
  }, n.date)), n.unread && /*#__PURE__*/React.createElement("span", {
    "aria-label": "unread",
    style: {
      width: 7,
      height: 7,
      borderRadius: 99,
      background: 'var(--accent)',
      marginTop: 6
    }
  })))))));
}
function LicencesScreen({
  go
}) {
  const A = window.AL;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Licences",
    back: true,
    onBack: () => go(null),
    hour: false
  }), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 14
  }, /*#__PURE__*/React.createElement(Prose, {
    size: "small"
  }, /*#__PURE__*/React.createElement("p", null, "Astrolabe is AGPL-3.0. Every asset in it \u2014 including her artwork \u2014 ships in a public repository, so anything that cannot be published cannot be in the app.")), /*#__PURE__*/React.createElement(Card, null, A.licences.map((l, i) => /*#__PURE__*/React.createElement(DataRow, {
    key: i,
    label: l.name,
    value: l.licence,
    small: true
  }))), /*#__PURE__*/React.createElement(Card, {
    tone: "inset"
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      marginBottom: 8
    }
  }, "Versions"), A.licences.map((l, i) => /*#__PURE__*/React.createElement(DataRow, {
    key: i,
    label: l.name,
    value: l.version,
    small: true,
    tone: "faint"
  }))), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "The full AGPL-3.0 text",
    onClick: () => {}
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Source for this build",
    description: "ShrutiVtuber/astrolabe \xB7 1.0.0 (214)",
    href: "#",
    external: true
  }))));
}
function PlacePickerScreen({
  s,
  go
}) {
  const A = window.AL;
  const [q, setQ] = React.useState('Athens');
  const results = A.places.filter(p => (p.name + p.region).toLowerCase().includes(q.toLowerCase()));
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(AppBar, {
    title: "Place",
    back: true,
    onBack: () => go(null),
    hour: false
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 16px 12px',
      flex: 'none'
    }
  }, /*#__PURE__*/React.createElement(TextField, {
    placeholder: "Search for a city",
    value: q,
    onChange: e => setQ(e.target.value),
    prefix: /*#__PURE__*/React.createElement(Icon, {
      name: "search",
      size: 18,
      tone: "faint"
    })
  })), /*#__PURE__*/React.createElement(Body, {
    pad: 16,
    gap: 14
  }, /*#__PURE__*/React.createElement(Card, {
    tone: "inset"
  }, /*#__PURE__*/React.createElement("div", {
    className: "t-caption",
    style: {
      lineHeight: 1.6
    }
  }, "The place decides sunrise, sunset and the planetary hours. It is stored on this phone and never sent anywhere.")), s.loading && /*#__PURE__*/React.createElement(Refreshing, null), !s.loading && (results.length === 0 ? /*#__PURE__*/React.createElement(EmptyState, {
    compact: true,
    mark: A.G.saturn,
    title: 'Nothing called “' + q + '”',
    body: "Try the local spelling, or the nearest larger city \u2014 the hours will be within a minute or two.",
    action: /*#__PURE__*/React.createElement(Button, {
      size: "sm",
      variant: "outlined"
    }, "Enter coordinates instead")
  }) : /*#__PURE__*/React.createElement(ListGroup, null, results.map(p => /*#__PURE__*/React.createElement(ListRow, {
    key: p.id,
    label: p.name,
    description: p.region + ' · ' + p.coords,
    value: p.tz,
    onClick: () => {
      s.set('place', p.name + ', ' + p.region.split(',').pop().trim());
      go(null);
    }
  })))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow"
  }, "Recent"), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Athens, Greece",
    value: "GMT+3",
    onClick: () => go(null)
  }), /*#__PURE__*/React.createElement(ListRow, {
    label: "Thessaloniki, Greece",
    value: "GMT+3",
    onClick: () => go(null)
  }))), /*#__PURE__*/React.createElement(ListGroup, null, /*#__PURE__*/React.createElement(ListRow, {
    label: "Use my location",
    description: "Asked once, kept on this phone",
    leading: /*#__PURE__*/React.createElement(Icon, {
      name: "my_location",
      size: 20,
      tone: "accent"
    }),
    chevron: false,
    onClick: () => {}
  }))));
}
function SkyDrawer({
  s,
  onClose
}) {
  const A = window.AL;
  return /*#__PURE__*/React.createElement(Dialog, {
    size: "fullscreen",
    title: "Sky drawer",
    subtitle: "Ephemeris \xB7 September 2026 \xB7 Athens",
    onClose: onClose
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement(ChipRow, null, /*#__PURE__*/React.createElement(Chip, {
    kind: "choice",
    selected: true
  }, "September"), /*#__PURE__*/React.createElement(Chip, {
    kind: "choice"
  }, "October"), /*#__PURE__*/React.createElement(Chip, {
    kind: "choice"
  }, "November"), /*#__PURE__*/React.createElement(Chip, {
    kind: "filter"
  }, "Show \u211E only")), /*#__PURE__*/React.createElement(DataTable, {
    columns: A.stations.columns,
    rows: A.stations.rows,
    zebra: true,
    caption: "Geocentric, apparent \xB7 00:00 Athens \xB7 tropical"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10,
      gridTemplateColumns: '1fr'
    }
  }, /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement("div", {
    className: "t-eyebrow",
    style: {
      marginBottom: 10
    }
  }, "The month, drawn"), /*#__PURE__*/React.createElement(ChartWheel, {
    mode: "period",
    size: 240,
    span: "1\u201330 Sep",
    housesKnown: false,
    bodies: A.bodies.slice(0, 6),
    phases: Array.from({
      length: 10
    }, (_, i) => ({
      lon: i * 36 + 12,
      phase: (i / 10 + 0.35) % 1
    }))
  }))), /*#__PURE__*/React.createElement(Provenance, {
    rule: "Tropical zodiac, apparent positions, 00:00 Athens"
  })));
}
Object.assign(window, {
  WorkScreen,
  WriteScreen,
  AccountScreen,
  NotificationsScreen,
  LicencesScreen,
  PlacePickerScreen,
  SkyDrawer
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/Screens4.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/States.jsx
try { (() => {
/* The ordered states document: every screen, in every state that applies to it,
   rendered from the same components as the interactive kit. */
const FRAMES = [['1 · Home', 'home', {}, 'Signed in, not live, online'], ['1 · Home', 'home', {
  live: true
}, 'Live — the plate warms, the hem and tab bar go rose'], ['1 · Home', 'home', {
  art: true
}, 'Her portrait present'], ['1 · Home', 'home', {
  loading: true
}, 'Loading — her half only; the sky is already computed'], ['1 · Home', 'home', {
  offline: true
}, 'Offline — instruments intact, her half out of reach'], ['1 · Home', 'home', {
  error: true
}, 'Error — the site answered badly'], ['1 · Home', 'home', {
  empty: true
}, 'Empty — nothing written this week, no offers open'], ['1 · Home', 'home', {
  signedIn: false
}, 'Signed out'], ['1 · Home', 'home', {
  member: true
}, 'Member — the locked offer opens'], ['1 · Home', 'home', {
  missing: true
}, 'Missing content — a reading with no opening line'], ['2 · Sky · Stations', 'sky', {
  seg: 'stations'
}, 'The month, dense, with ℞ printed'], ['2 · Sky · Stations', 'sky', {
  seg: 'stations',
  offline: true
}, 'Offline — unchanged, and it says so'], ['3 · Sky · Hours', 'sky', {
  seg: 'hours'
}, 'The twelve day hours, current hour washed'], ['3 · Sky · Hours', 'sky', {
  seg: 'hours',
  sunrise: 'civil'
}, 'Civil-dawn convention in force'], ['4 · Sky · Coming', 'sky', {
  seg: 'coming'
}, 'Forty days ahead'], ['4 · Sky · Coming', 'sky', {
  seg: 'coming',
  empty: true
}, 'Empty — a quiet sky is not an error'], ['5 · Chart · form', 'chart', {}, 'Before casting'], ['5 · Chart · form', 'chart', {
  noBirthTime: true
}, 'Birth time unknown — the time field stands down'], ['5 · Chart · form', 'chart', {
  longContent: true
}, 'A forty-character name'], ['5 · Chart · form', 'chart', {
  error: true
}, 'Error — the place could not be resolved'], ['6 · Chart · result', 'chart', {
  cast: true
}, 'The wheel, houses known'], ['6 · Chart · result', 'chart', {
  cast: true,
  noBirthTime: true
}, 'Angles undefined — no house ring, and the app says why'], ['7 · Letters · Reckoning', 'letters', {
  seg: 'reckoning'
}, 'Greek Milesian, letter by letter'], ['8 · Letters · Sigil', 'letters', {
  seg: 'sigil'
}, 'The figure drawn on the rose cross'], ['8 · Letters · Sigil', 'letters', {
  seg: 'sigil',
  empty: true
}, 'Cannot compute — nothing left to draw'], ['9 · Practice · Read', 'practice', {
  seg: 'read'
}, 'The feed'], ['9 · Practice · Read', 'practice', {
  seg: 'read',
  signedIn: false
}, 'Signed out — votes visible, not operable'], ['9 · Practice · Read', 'practice', {
  seg: 'read',
  loading: true
}, 'Loading — skeletons shaped like work cards'], ['9 · Practice · Read', 'practice', {
  seg: 'read',
  empty: true
}, 'Empty — the room is quiet'], ['9 · Practice · Read', 'practice', {
  seg: 'read',
  offline: true
}, 'Offline — drafts still kept'], ['10 · Practice · Mine', 'practice', {
  seg: 'mine'
}, 'Draft, posted and corrected'], ['10 · Practice · Mine', 'practice', {
  seg: 'mine',
  signedIn: false
}, 'Signed out'], ['10 · Practice · Mine', 'practice', {
  seg: 'mine',
  empty: true
}, 'Nothing written yet'], ['11 · One work', 'work', {}, 'Readings, votes, comments — hers marked'], ['11 · One work', 'work', {
  signedIn: false
}, 'Signed out — no vote, no comment box'], ['11 · One work', 'work', {
  longContent: true
}, 'A 2,000-word reading'], ['12 · Write', 'write', {}, 'The writing screen'], ['12 · Write', 'write', {
  longContent: true
}, 'Long title and long body'], ['12 · Write', 'write', {
  offline: true
}, 'Offline — it becomes a draft'], ['12 · Write', 'write', {
  error: true,
  signedIn: false
}, 'Error, and signed out'], ['13 · Settings', 'settings', {}, 'Signed in, free'], ['13 · Settings', 'settings', {
  member: true
}, 'Member'], ['13 · Settings', 'settings', {
  loading: true
}, 'A language pack downloading'], ['13 · Settings', 'settings', {
  error: true
}, 'A pack that did not finish'], ['14 · Account', 'account', {
  signedIn: false
}, 'Signed out — the sign-in half'], ['14 · Account', 'account', {
  signedIn: false,
  error: true
}, 'Sign-in failed'], ['14 · Account', 'account', {}, 'Signed in, free'], ['14 · Account', 'account', {
  member: true
}, 'Member'], ['14 · Account', 'account', {
  confirmDelete: true
}, 'The delete confirm'], ['15 · Notifications', 'notifications', {}, 'Switches and recent'], ['15 · Notifications', 'notifications', {
  empty: true
}, 'Nothing yet'], ['15 · Notifications', 'notifications', {
  signedIn: false
}, 'Signed out — replies unavailable'], ['16 · Licences', 'licences', {}, 'AGPL-3.0 and every dependency'], ['17 · Place picker', 'place', {}, 'Search and choose'], ['17 · Place picker', 'place', {
  loading: true
}, 'Searching'], ['18 · Sky drawer', 'drawer', {}, 'The ephemeris as reference, full screen']];
function Frame({
  title,
  note,
  screen,
  over
}) {
  const base = {
    live: false,
    offline: false,
    loading: false,
    empty: false,
    error: false,
    signedIn: true,
    member: false,
    longContent: false,
    missing: false,
    noBirthTime: false,
    art: false,
    reduceMotion: false,
    place: 'Athens, Greece',
    sunrise: 'limb',
    hour: 'venus',
    confirmDelete: false
  };
  const [st, setSt] = React.useState({
    ...base,
    ...over
  });
  const s = {
    ...st,
    set: (k, v) => setSt(p => ({
      ...p,
      [k]: v
    }))
  };
  const seg = over.seg;
  const go = () => {};
  const noop = () => {};
  let inner;
  switch (screen) {
    case 'home':
      inner = /*#__PURE__*/React.createElement(HomeScreen, {
        s: s,
        go: go
      });
      break;
    case 'sky':
      inner = /*#__PURE__*/React.createElement(SkyScreen, {
        s: s,
        seg: seg,
        setSeg: noop,
        go: go
      });
      break;
    case 'chart':
      inner = /*#__PURE__*/React.createElement(ChartScreen, {
        s: s,
        cast: !!over.cast,
        setCast: noop,
        go: go
      });
      break;
    case 'letters':
      inner = /*#__PURE__*/React.createElement(LettersScreen, {
        s: s,
        seg: seg,
        setSeg: noop
      });
      break;
    case 'practice':
      inner = /*#__PURE__*/React.createElement(PracticeScreen, {
        s: s,
        seg: seg,
        setSeg: noop,
        go: go
      });
      break;
    case 'settings':
      inner = /*#__PURE__*/React.createElement(SettingsScreen, {
        s: s,
        go: go
      });
      break;
    case 'work':
      inner = /*#__PURE__*/React.createElement(WorkScreen, {
        s: s,
        go: go
      });
      break;
    case 'write':
      inner = /*#__PURE__*/React.createElement(WriteScreen, {
        s: s,
        go: go
      });
      break;
    case 'account':
      inner = /*#__PURE__*/React.createElement(AccountScreen, {
        s: s,
        go: go
      });
      break;
    case 'notifications':
      inner = /*#__PURE__*/React.createElement(NotificationsScreen, {
        s: s,
        go: go
      });
      break;
    case 'licences':
      inner = /*#__PURE__*/React.createElement(LicencesScreen, {
        go: go
      });
      break;
    case 'place':
      inner = /*#__PURE__*/React.createElement(PlacePickerScreen, {
        s: s,
        go: go
      });
      break;
    case 'drawer':
      inner = /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(HomeScreen, {
        s: s,
        go: go
      }), /*#__PURE__*/React.createElement(SkyDrawer, {
        s: s,
        onClose: noop
      }));
      break;
    default:
      inner = null;
  }
  const showTabs = ['home', 'sky', 'chart', 'letters', 'practice', 'settings', 'drawer'].includes(screen);
  const active = screen === 'drawer' ? 'home' : screen;
  return /*#__PURE__*/React.createElement("figure", {
    style: {
      margin: 0,
      display: 'grid',
      gap: 10,
      justifyItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("figcaption", {
    style: {
      display: 'grid',
      gap: 3,
      maxWidth: 360
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 11px/1 var(--font-body)',
      letterSpacing: '.13em',
      textTransform: 'uppercase',
      color: 'var(--gilt)'
    }
  }, title), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 13px/1.45 var(--font-body)',
      color: 'var(--faint)',
      textWrap: 'pretty'
    }
  }, note)), /*#__PURE__*/React.createElement("div", {
    "data-live": st.live ? 'true' : undefined,
    "data-hour": st.hour,
    style: {
      width: 360,
      height: 800,
      position: 'relative',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--page)',
      borderRadius: 30,
      border: '1px solid var(--line-strong)',
      overflow: 'hidden',
      boxShadow: '0 18px 48px -18px rgba(0,0,0,.65)'
    }
  }, /*#__PURE__*/React.createElement(StatusBar, {
    live: st.live
  }), inner, showTabs && /*#__PURE__*/React.createElement(TabBar, {
    active: active,
    badges: {
      practice: 2
    },
    onChange: noop
  })));
}
function StatesDoc() {
  const groups = [];
  FRAMES.forEach(f => {
    const g = groups.find(x => x.title === f[0]);
    (g || groups[groups.push({
      title: f[0],
      items: []
    }) - 1]).items.push(f);
  });
  return /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '32px 28px 80px',
      display: 'grid',
      gap: 44
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      display: 'grid',
      gap: 10,
      maxWidth: '62ch'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 11px/1 var(--font-body)',
      letterSpacing: '.14em',
      textTransform: 'uppercase',
      color: 'var(--faint)'
    }
  }, "Astrolabe \xB7 the whole app"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: '500 38px/1.1 var(--font-display)',
      color: 'var(--ink)',
      letterSpacing: '-0.012em'
    }
  }, "Every screen, every state"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 16px/1.6 var(--font-body)',
      color: 'var(--soft)',
      textWrap: 'pretty'
    }
  }, "Eighteen screens at 360 \xD7 800, in the states the addendum asks for: loading, empty, offline, error, signed out, live, member, long content and missing content. Frames are live components, not images \u2014 the interactive version, with a large-phone size, is in", /*#__PURE__*/React.createElement("a", {
    href: "index.html",
    style: {
      marginLeft: 4
    }
  }, "index.html"), "."), /*#__PURE__*/React.createElement("div", {
    className: "rule",
    style: {
      maxWidth: 420
    }
  }, '\u263E\ufe0e')), groups.map(g => /*#__PURE__*/React.createElement("section", {
    key: g.title,
    style: {
      display: 'grid',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: '600 22px/1.25 var(--font-display)',
      color: 'var(--ink)'
    }
  }, g.title), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 28,
      flexWrap: 'wrap'
    }
  }, g.items.map((f, i) => /*#__PURE__*/React.createElement(Frame, {
    key: i,
    title: f[0],
    screen: f[1],
    over: f[2],
    note: f[3]
  }))))));
}
Object.assign(window, {
  StatesDoc,
  Frame,
  FRAMES
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/States.jsx", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/data.js
try { (() => {
/* Sample data for the Astrolabe UI kit. Plausible and internally consistent —
   NOT live computation. The reckoning a developer must write is described in
   readme.md and guidelines/theme-flutter.md. */
window.AL = function () {
  const G = {
    sun: '\u2609\uFE0E',
    moon: '\u263E\uFE0E',
    mercury: '\u263F\uFE0E',
    venus: '\u2640\uFE0E',
    mars: '\u2642\uFE0E',
    jupiter: '\u2643\uFE0E',
    saturn: '\u2644\uFE0E',
    uranus: '\u2645\uFE0E',
    neptune: '\u2646\uFE0E',
    pluto: '\u2647\uFE0E',
    node: '\u260A\uFE0E',
    rx: '\u211E\uFE0E'
  };
  /* Every mark carries U+FE0E in the data itself, so it survives being copied out
     of the app into a message, a caption, or a printed table. */
  const S = {
    aries: '\u2648\uFE0E',
    taurus: '\u2649\uFE0E',
    gemini: '\u264A\uFE0E',
    cancer: '\u264B\uFE0E',
    leo: '\u264C\uFE0E',
    virgo: '\u264D\uFE0E',
    libra: '\u264E\uFE0E',
    scorpio: '\u264F\uFE0E',
    sagittarius: '\u2650\uFE0E',
    capricorn: '\u2651\uFE0E',
    aquarius: '\u2652\uFE0E',
    pisces: '\u2653\uFE0E'
  };
  const readings = [{
    id: 'r1',
    sign: 'Scorpio',
    mark: S.scorpio,
    date: '9 Sep',
    time: '2 min',
    unread: true,
    excerpt: 'Mercury is still in the shadow, so the thing you thought was settled on Friday is not settled. Leave it until the 18th.'
  }, {
    id: 'r2',
    sign: 'Capricorn',
    mark: S.capricorn,
    date: '9 Sep',
    time: '2 min',
    excerpt: 'Saturn is on your descendant and it is asking about one relationship in particular. You know which.'
  }, {
    id: 'r3',
    sign: 'Aries',
    mark: S.aries,
    date: '8 Sep',
    time: '1 min'
  }, {
    id: 'r4',
    sign: 'Virgo',
    mark: S.virgo,
    date: '8 Sep',
    time: '3 min',
    excerpt: 'The Sun is on your own degree this week, which is less dramatic than it sounds and more useful than you expect.'
  }];
  const articles = [{
    id: 'a1',
    title: 'What a station actually is',
    date: '4 Sep',
    time: '9 min',
    excerpt: 'Apparent motion, and why the word retrograde has survived the model that produced it.'
  }, {
    id: 'a2',
    title: 'Casting a chart with no birth time, honestly',
    date: '28 Aug',
    time: '12 min',
    excerpt: 'What you may still say, what you may not, and how the app refuses to guess for you.'
  }, {
    id: 'a3',
    title: 'The hours are not sixty minutes long',
    date: '21 Aug',
    time: '6 min'
  }];
  const offers = [{
    id: 'o1',
    title: 'Six weeks of Hellenistic basics',
    price: '\u20ac120',
    cadence: 'for six weeks',
    mark: G.jupiter,
    body: 'Live on Thursdays, recorded for members. Twelve places.',
    href: 'https://shrutivtuber.com/classes'
  }, {
    id: 'o2',
    title: 'Members\u2019 chart clinic',
    price: 'Included',
    membersOnly: true,
    mark: G.venus,
    body: 'One chart a month, read on stream, name withheld if you want it withheld.'
  }, {
    id: 'o3',
    title: 'A reading, written for you',
    price: '\u20ac65',
    mark: G.mercury,
    soldOut: true,
    body: 'Two thousand words on one question. Currently full until October.'
  }];
  const stations = {
    columns: [{
      key: 'date',
      label: 'Day',
      width: 64
    }, {
      key: 'sun',
      label: 'Sun',
      mark: G.sun,
      numeric: true
    }, {
      key: 'moon',
      label: 'Moon',
      mark: G.moon,
      numeric: true
    }, {
      key: 'mer',
      label: 'Mercury',
      mark: G.mercury,
      numeric: true
    }, {
      key: 'ven',
      label: 'Venus',
      mark: G.venus,
      numeric: true
    }, {
      key: 'mar',
      label: 'Mars',
      mark: G.mars,
      numeric: true
    }, {
      key: 'phase',
      label: 'Phase',
      numeric: true,
      width: 50
    }],
    rows: [{
      id: '5',
      date: '5 Sep',
      sun: '12\u00b0' + S.virgo,
      moon: '26\u00b0' + S.sagittarius,
      mer: {
        value: '04\u00b0' + S.libra,
        retro: true
      },
      ven: '26\u00b0' + S.leo,
      mar: '09\u00b0' + S.libra,
      phase: '\u25d0'
    }, {
      id: '6',
      date: '6 Sep',
      sun: '13\u00b0' + S.virgo,
      moon: '09\u00b0' + S.capricorn,
      mer: {
        value: '03\u00b0' + S.libra,
        retro: true
      },
      ven: '27\u00b0' + S.leo,
      mar: '10\u00b0' + S.libra,
      phase: '\u25d0'
    }, {
      id: '7',
      date: '7 Sep',
      sun: '14\u00b0' + S.virgo,
      moon: '21\u00b0' + S.capricorn,
      mer: {
        value: '02\u00b0' + S.libra,
        retro: true
      },
      ven: '28\u00b0' + S.leo,
      mar: '11\u00b0' + S.libra,
      phase: '\u25cf'
    }, {
      id: '8',
      date: '8 Sep',
      sun: '15\u00b0' + S.virgo,
      moon: '04\u00b0' + S.aquarius,
      mer: {
        value: '01\u00b0' + S.libra,
        retro: true
      },
      ven: '29\u00b0' + S.leo,
      mar: '12\u00b0' + S.libra,
      phase: '\u25cf'
    }, {
      id: '9',
      date: '9 Sep',
      today: true,
      sun: '16\u00b0' + S.virgo,
      moon: '17\u00b0' + S.aquarius,
      mer: {
        value: '00\u00b0' + S.libra,
        retro: true
      },
      ven: '00\u00b0' + S.virgo,
      mar: '12\u00b0' + S.libra,
      phase: '\u25cf'
    }, {
      id: '10',
      date: '10 Sep',
      sun: '17\u00b0' + S.virgo,
      moon: '00\u00b0' + S.pisces,
      mer: '29\u00b0' + S.virgo,
      ven: '01\u00b0' + S.virgo,
      mar: '13\u00b0' + S.libra,
      phase: '\u25d1'
    }, {
      id: '11',
      date: '11 Sep',
      sun: '18\u00b0' + S.virgo,
      moon: '13\u00b0' + S.pisces,
      mer: '29\u00b0' + S.virgo,
      ven: '02\u00b0' + S.virgo,
      mar: '14\u00b0' + S.libra,
      phase: '\u25d1'
    }, {
      id: '12',
      date: '12 Sep',
      sun: '19\u00b0' + S.virgo,
      moon: '26\u00b0' + S.pisces,
      mer: '29\u00b0' + S.virgo,
      ven: '03\u00b0' + S.virgo,
      mar: '14\u00b0' + S.libra,
      phase: '\u25d1'
    }, {
      id: '13',
      date: '13 Sep',
      sun: '20\u00b0' + S.virgo,
      moon: '09\u00b0' + S.aries,
      mer: '00\u00b0' + S.libra,
      ven: '04\u00b0' + S.virgo,
      mar: '15\u00b0' + S.libra,
      phase: '\u25d1'
    }, {
      id: '14',
      date: '14 Sep',
      sun: '21\u00b0' + S.virgo,
      moon: '22\u00b0' + S.aries,
      mer: '01\u00b0' + S.libra,
      ven: '05\u00b0' + S.virgo,
      mar: '16\u00b0' + S.libra,
      phase: '\u25cb'
    }, {
      id: '15',
      date: '15 Sep',
      sun: '22\u00b0' + S.virgo,
      moon: '05\u00b0' + S.taurus,
      mer: '02\u00b0' + S.libra,
      ven: '06\u00b0' + S.virgo,
      mar: '17\u00b0' + S.libra,
      phase: '\u25cb'
    }, {
      id: '16',
      date: '16 Sep',
      sun: '23\u00b0' + S.virgo,
      moon: '18\u00b0' + S.taurus,
      mer: '04\u00b0' + S.libra,
      ven: '07\u00b0' + S.virgo,
      mar: '17\u00b0' + S.libra,
      phase: '\u25cb'
    }]
  };
  const hours = {
    columns: [{
      key: 'n',
      label: '#',
      width: 30
    }, {
      key: 'from',
      label: 'From',
      numeric: true
    }, {
      key: 'to',
      label: 'To',
      numeric: true
    }, {
      key: 'ruler',
      label: 'Ruler'
    }, {
      key: 'len',
      label: 'Length',
      numeric: true
    }],
    rows: [{
      id: 1,
      n: '1',
      from: '06:58',
      to: '08:00',
      ruler: G.mercury + '\ufe0e Mercury',
      len: '62 m'
    }, {
      id: 2,
      n: '2',
      from: '08:00',
      to: '09:02',
      ruler: G.moon + '\ufe0e Moon',
      len: '62 m'
    }, {
      id: 3,
      n: '3',
      from: '09:02',
      to: '10:04',
      ruler: G.saturn + '\ufe0e Saturn',
      len: '62 m'
    }, {
      id: 4,
      n: '4',
      from: '10:04',
      to: '11:06',
      ruler: G.jupiter + '\ufe0e Jupiter',
      len: '62 m'
    }, {
      id: 5,
      n: '5',
      from: '11:06',
      to: '12:08',
      ruler: G.mars + '\ufe0e Mars',
      len: '62 m'
    }, {
      id: 6,
      n: '6',
      from: '12:08',
      to: '13:10',
      ruler: G.sun + '\ufe0e Sun',
      len: '62 m'
    }, {
      id: 7,
      n: '7',
      today: true,
      from: '13:10',
      to: '14:12',
      ruler: G.venus + '\ufe0e Venus',
      len: '62 m'
    }, {
      id: 8,
      n: '8',
      from: '14:12',
      to: '15:14',
      ruler: G.mercury + '\ufe0e Mercury',
      len: '62 m'
    }, {
      id: 9,
      n: '9',
      from: '15:14',
      to: '16:16',
      ruler: G.moon + '\ufe0e Moon',
      len: '62 m'
    }, {
      id: 10,
      n: '10',
      from: '16:16',
      to: '17:18',
      ruler: G.saturn + '\ufe0e Saturn',
      len: '62 m'
    }, {
      id: 11,
      n: '11',
      from: '17:18',
      to: '18:20',
      ruler: G.jupiter + '\ufe0e Jupiter',
      len: '62 m'
    }, {
      id: 12,
      n: '12',
      from: '18:20',
      to: '19:22',
      ruler: G.mars + '\ufe0e Mars',
      len: '62 m'
    }]
  };
  const coming = [{
    when: 'Thu 11 Sep',
    mark: G.mercury,
    title: 'Mercury stations direct',
    detail: '29\u00b0 Virgo, 04:12 Athens \u00b7 02:12 your time',
    tone: 'caution'
  }, {
    when: 'Sat 13 Sep',
    mark: G.moon,
    title: 'Last quarter',
    detail: '21\u00b0 Gemini, 12:31 Athens'
  }, {
    when: 'Mon 22 Sep',
    mark: G.sun,
    title: 'Equinox',
    detail: 'The Sun enters Libra, 21:19 Athens'
  }, {
    when: 'Wed 24 Sep',
    mark: G.venus,
    title: 'Venus enters Virgo',
    detail: '02:47 Athens'
  }, {
    when: 'Sun 5 Oct',
    mark: G.saturn,
    title: 'Saturn stations direct',
    detail: '25\u00b0 Pisces, 19:04 Athens',
    tone: 'caution'
  }];
  const bodies = [{
    name: 'Sun',
    mark: G.sun,
    lon: 166.7
  }, {
    name: 'Moon',
    mark: G.moon,
    lon: 317.2
  }, {
    name: 'Mercury',
    mark: G.mercury,
    lon: 180.9,
    retro: true
  }, {
    name: 'Venus',
    mark: G.venus,
    lon: 150.4
  }, {
    name: 'Mars',
    mark: G.mars,
    lon: 192.5
  }, {
    name: 'Jupiter',
    mark: G.jupiter,
    lon: 98.1
  }, {
    name: 'Saturn',
    mark: G.saturn,
    lon: 349.8,
    retro: true
  }, {
    name: 'Uranus',
    mark: G.uranus,
    lon: 62.4
  }, {
    name: 'Neptune',
    mark: G.neptune,
    lon: 359.1,
    retro: true
  }, {
    name: 'Pluto',
    mark: G.pluto,
    lon: 300.6,
    retro: true
  }];
  const aspects = [{
    from: 166.7,
    to: 349.8,
    type: 'opposition'
  }, {
    from: 317.2,
    to: 150.4,
    type: 'trine'
  }, {
    from: 150.4,
    to: 62.4,
    type: 'square'
  }, {
    from: 180.9,
    to: 98.1,
    type: 'sextile'
  }, {
    from: 166.7,
    to: 180.9,
    type: 'conjunction'
  }, {
    from: 192.5,
    to: 98.1,
    type: 'square'
  }];
  const cusps = [214.3, 244.3, 274.3, 304.3, 334.3, 4.3, 34.3, 64.3, 94.3, 124.3, 154.3, 184.3];
  const chartTable = [{
    mark: G.sun,
    label: 'Sun',
    value: '16\u00b0 42\u2032 ' + S.virgo + ' \u00b7 5th'
  }, {
    mark: G.moon,
    label: 'Moon',
    value: '17\u00b0 09\u2032 ' + S.aquarius + ' \u00b7 11th'
  }, {
    mark: G.mercury,
    label: 'Mercury',
    value: '00\u00b0 51\u2032 ' + S.libra + ' \u211e \u00b7 6th',
    rose: true
  }, {
    mark: G.venus,
    label: 'Venus',
    value: '00\u00b0 24\u2032 ' + S.virgo + ' \u00b7 5th'
  }, {
    mark: G.mars,
    label: 'Mars',
    value: '12\u00b0 30\u2032 ' + S.libra + ' \u00b7 6th'
  }, {
    mark: G.jupiter,
    label: 'Jupiter',
    value: '08\u00b0 06\u2032 ' + S.cancer + ' \u00b7 3rd'
  }, {
    mark: G.saturn,
    label: 'Saturn',
    value: '19\u00b0 48\u2032 ' + S.pisces + ' \u211e \u00b7 11th',
    rose: true
  }, {
    mark: G.uranus,
    label: 'Uranus',
    value: '02\u00b0 24\u2032 ' + S.gemini + ' \u00b7 2nd'
  }, {
    mark: G.neptune,
    label: 'Neptune',
    value: '29\u00b0 06\u2032 ' + S.pisces + ' \u211e \u00b7 11th',
    rose: true
  }, {
    mark: G.pluto,
    label: 'Pluto',
    value: '00\u00b0 36\u2032 ' + S.aquarius + ' \u211e \u00b7 10th',
    rose: true
  }, {
    mark: G.node,
    label: 'North node',
    value: '14\u00b0 12\u2032 ' + S.pisces + ' \u00b7 11th'
  }];
  const feed = [{
    id: 'w1',
    title: 'Saturn on the descendant, and what it asked of me',
    author: 'korax',
    date: '9 Sep',
    votes: 14,
    myVote: 0,
    comments: 6,
    sign: 'Capricorn',
    excerpt: 'I have had this transit for eleven months and I have spent most of them arguing with it. Here is what changed when I stopped.'
  }, {
    id: 'w2',
    title: 'A first attempt at the eclipse chart for Athens',
    author: 'thalassa',
    date: '9 Sep',
    votes: 9,
    myVote: 0,
    comments: 2,
    sign: 'Pisces',
    excerpt: 'Whole sign, tropical. I am not confident about the seventh house and would like to be argued with.'
  }, {
    id: 'w3',
    title: 'Why I stopped reading the outers in nativities',
    author: 'a very long username indeed',
    date: '8 Sep',
    votes: 31,
    myVote: 1,
    comments: 24,
    sign: 'Aquarius',
    excerpt: 'Not a purist position. A practical one, arrived at after four years of noticing what I was actually using.'
  }, {
    id: 'w4',
    title: 'Mercury retrograde is not about email',
    author: 'phos',
    date: '8 Sep',
    votes: 22,
    myVote: 0,
    comments: 11,
    sign: 'Virgo',
    excerpt: 'The shadow period is the interesting part and almost nobody talks about it.'
  }];
  const mine = [{
    id: 'm1',
    title: 'First pass at the eclipse',
    date: '8 Sep',
    status: 'draft',
    votes: 0,
    comments: 0,
    excerpt: 'Notes, mostly. The angles are doing something I do not understand yet.'
  }, {
    id: 'm2',
    title: 'Venus in the twelfth, read three ways',
    date: '2 Sep',
    status: 'posted',
    votes: 7,
    comments: 3,
    excerpt: 'Traditional, modern, and what I actually think.'
  }, {
    id: 'm3',
    title: 'On the hour of Saturn',
    date: '24 Aug',
    status: 'corrected',
    votes: 19,
    comments: 8,
    excerpt: 'Corrected 26 Aug: I had the sunrise convention wrong, which moved every hour by nine minutes.'
  }];
  const comments = [{
    id: 'c1',
    author: 'thalassa',
    date: '9 Sep',
    votes: 5,
    body: 'The eleventh-month framing is the part I want to argue with. Saturn does not ask; it invoices.'
  }, {
    id: 'c2',
    author: 'Shruti',
    date: '9 Sep',
    votes: 12,
    her: true,
    body: 'It invoices, and then it asks whether you were going to pay it in instalments. Good piece — the descendant reading is doing real work here.'
  }, {
    id: 'c3',
    author: 'korax',
    date: '9 Sep',
    votes: 2,
    body: 'Fair. I will rewrite the third paragraph and repost it as a correction rather than an edit.'
  }];
  const places = [{
    id: 'p1',
    name: 'Athens',
    region: 'Attica, Greece',
    coords: '37.98\u00b0 N \u00b7 23.73\u00b0 E',
    tz: 'GMT+3'
  }, {
    id: 'p2',
    name: 'Athens',
    region: 'Georgia, United States',
    coords: '33.96\u00b0 N \u00b7 83.38\u00b0 W',
    tz: 'GMT\u22124'
  }, {
    id: 'p3',
    name: 'Athina',
    region: 'Attica, Greece \u00b7 same place',
    coords: '37.98\u00b0 N \u00b7 23.73\u00b0 E',
    tz: 'GMT+3'
  }, {
    id: 'p4',
    name: 'Atherton',
    region: 'California, United States',
    coords: '37.46\u00b0 N \u00b7 122.20\u00b0 W',
    tz: 'GMT\u22127'
  }];
  const notifications = [{
    id: 'n1',
    kind: 'live',
    title: 'Shruti is live',
    body: 'Casting charts for the chat',
    date: '2 h ago',
    unread: true
  }, {
    id: 'n2',
    kind: 'reply',
    title: 'thalassa replied to your reading',
    body: 'The eleventh-month framing is the part I want to argue with.',
    date: '5 h ago',
    unread: true
  }, {
    id: 'n3',
    kind: 'sky',
    title: 'Mercury stations direct on Thursday',
    body: '29\u00b0 Virgo, 04:12 Athens',
    date: 'Yesterday'
  }, {
    id: 'n4',
    kind: 'reading',
    title: 'Your weekly readings are up',
    body: 'Twelve signs, written Sunday night',
    date: '2 days ago'
  }];
  const licences = [{
    name: 'Swiss Ephemeris',
    version: '2.10.03',
    licence: 'AGPL-3.0'
  }, {
    name: 'EB Garamond',
    version: '2.006',
    licence: 'OFL-1.1'
  }, {
    name: 'Commissioner',
    version: '2.000',
    licence: 'OFL-1.1'
  }, {
    name: 'AstroSymbols',
    version: '1.0 \u00b7 29 glyphs',
    licence: 'OFL-1.1'
  }, {
    name: 'Material Symbols',
    version: '4.0.0',
    licence: 'Apache-2.0'
  }, {
    name: 'Astrolabe',
    version: '1.0.0 (build 214)',
    licence: 'AGPL-3.0'
  }];
  const isopsephy = [{
    ch: '\u03a3',
    v: 200
  }, {
    ch: '\u03bf',
    v: 70
  }, {
    ch: '\u03c6',
    v: 500
  }, {
    ch: '\u03af',
    v: 10
  }, {
    ch: '\u03b1',
    v: 1
  }];
  return {
    G,
    S,
    readings,
    articles,
    offers,
    stations,
    hours,
    coming,
    bodies,
    aspects,
    cusps,
    chartTable,
    feed,
    mine,
    comments,
    places,
    notifications,
    licences,
    isopsephy
  };
}();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/data.js", error: String((e && e.message) || e) }); }

// ui_kits/astrolabe/image-slot.js
try { (() => {
// @ds-adherence-ignore -- omelette starter scaffold (raw elements/hex/px by design)
// Copied omelette starter. Re-running copy_starter_component with this kind overwrites this file with the latest version (page content is unaffected).
/* BEGIN USAGE */
/**
 * <image-slot> — user-fillable image placeholder.
 *
 * Drop this into a deck, mockup, or page wherever a design needs an image.
 * You control the slot's shape; it sizes to its container by default. When the search_stock_photos tool
 * is available, prefill the slot by default — write the photo's URL into
 * src (with credit/credit-href); the user can still fill or replace it
 * by dragging an image file onto it (or clicking to browse). The dropped
 * image persists across reloads via a .image-slots.state.json sidecar —
 * same read-via-fetch / write-via-window.omelette pattern as
 * design_canvas.jsx, so the filled slot shows on share links, downloaded
 * zips, and PPTX export. Outside the omelette runtime the slot is read-only.
 *
 * The sidecar is a SIBLING of the HTML file that uses this component: the
 * read is a document-relative fetch, and the host resolves the bridge's
 * sidecar writes into the previewed file's directory to match (same
 * contract as design_canvas.jsx). Pages in the same directory share one
 * sidecar; keep slot ids distinct across them.
 *
 * Attributes:
 *   id           Persistence key. REQUIRED for the drop to survive reload —
 *                every slot on the page needs a distinct id.
 *   shape        'rect' | 'rounded' | 'circle' | 'pill'   (default 'rounded')
 *                'circle' applies 50% border-radius; on a non-square slot
 *                that's an ellipse — set equal width and height for a true
 *                circle.
 *   radius       Corner radius in px for 'rounded'.       (default 12)
 *   mask         Any CSS clip-path value. Overrides `shape` — use this for
 *                hexagons, blobs, arbitrary polygons.
 *   fit          Initial framing baseline: cover | contain.   (default 'cover')
 *                cover starts the image filling the frame (overflow cropped);
 *                contain starts it fully visible (letterboxed). Either way the
 *                user can always pan/scale from there — double-click, or the
 *                Edit control, enters reframe mode (drag to move, scroll or
 *                corner-handles to scale; Escape / click-out commits). The
 *                crop persists alongside the image in the sidecar.
 *   placeholder  Empty-state caption.                      (default 'Drop an image')
 *   src          Optional initial/fallback image URL. Prefill it with a real
 *                photo via search_stock_photos when that tool is available
 *                (set credit/credit-href from the result). A user drop
 *                overrides it; clearing the drop reveals src again.
 *   credit       Attribution text shown as a small overlay at the
 *                bottom-left of the filled slot. REQUIRED whenever src
 *                points at any Unsplash host (images.unsplash.com,
 *                plus.unsplash.com, …): an Unsplash src with no credit
 *                renders an error tile INSTEAD of the photo (Unsplash
 *                terms forbid showing their photos unattributed). Use the
 *                exact form 'Photo by {photographer name} on Unsplash' —
 *                the overlay then links the name to credit-href and
 *                'Unsplash' to the Unsplash homepage, and links back to
 *                unsplash.com automatically get the required utm referral
 *                params appended at render time. The credit belongs to
 *                the src image, so it only shows while src is what's
 *                displayed — a user-dropped image hides it.
 *   credit-href  Link for the photographer's name in the credit overlay
 *                (their Unsplash profile URL from the stock-photo search
 *                results). http(s) URLs only — anything else renders the
 *                name as plain text.
 *
 * Sizing: the slot fills its container by default (width/height 100%).
 * Put it in a sized wrapper — absolutely positioned, a grid cell, a fixed
 * frame — and it takes exactly that box. When the parent's height is
 * indefinite (ordinary flow), it falls back to full width at a 3:2 aspect
 * ratio instead of collapsing. In a shrink-to-fit parent (a float,
 * width:max-content, an unsized absolute wrapper), percentages have
 * nothing to resolve against — size the slot or its wrapper explicitly
 * there. For a fixed-size slot, set
 * width/height on the element itself (inline style), which overrides the
 * default. When
 * layering content above a slot (full-bleed layouts), make the overlay
 * click-through — pointer-events: none on scrims/text plates, re-enabled
 * on interactive children — so the slot's hover controls stay reachable.
 * Keep the slot's bottom-left corner visually clear as well: the credit
 * overlay renders there, and a dark fade or text plate covering it hides
 * the attribution Unsplash's terms require — end the fade above that
 * corner, or keep it nearly transparent where the credit sits.
 *
 * Usage:
 *   <div style="position:relative;width:100%;height:100%">      <!-- full-bleed: -->
 *     <image-slot id="bg" shape="rect"></image-slot>            <!-- fills the wrapper -->
 *   </div>
 *   <image-slot id="hero"   style="width:800px;height:450px" shape="rounded" radius="20"
 *               placeholder="Drop a hero image"></image-slot>
 *   <image-slot id="avatar" style="width:120px;height:120px" shape="circle"></image-slot>
 *   <image-slot id="kite"   style="width:300px;height:300px"
 *               mask="polygon(50% 0, 100% 50%, 50% 100%, 0 50%)"></image-slot>
 */
/* END USAGE */

(() => {
  const STATE_FILE = '.image-slots.state.json';

  // Unsplash terms require visible attribution wherever their photos
  // display, and every link back to unsplash.com must carry utm referral
  // params. Two render-time rules enforce that here:
  //  - an Unsplash-src slot with NO credit attribute renders an error
  //    tile INSTEAD of the photo (an uncredited Unsplash photo on screen
  //    is itself the terms violation, so it never renders bare);
  //  - rendered credit links pointing at unsplash.com get the referral
  //    params appended when absent (credit-href values live in page
  //    content that can't be edited after the fact).
  // Keep the utm_source value in sync with UTM_SOURCE in
  // platform/web-agent/unsplash.ts — this file is a project-local
  // artifact and cannot import it (equality is pinned by tests).
  const UNSPLASH_HOMEPAGE_HREF = 'https://unsplash.com/?utm_source=claude_design&utm_medium=referral';
  // Host rule mirrors the hotlink validator that admits Unsplash srcs into
  // pages in the first place (cdn$ in unsplash.ts: apex or any subdomain)
  // — Unsplash+ results serve from plus.unsplash.com, not just images.*,
  // and an admitted-but-uncredited photo must error whatever unsplash
  // host it rides on.
  // Trailing-dot FQDNs (images.unsplash.com.) are the same host to the
  // browser but would miss the regex — strip one dot so the check fails
  // CLOSED (unrecognized-but-real Unsplash srcs must error, not render).
  const isUnsplashHost = u => {
    try {
      return /(^|\.)unsplash\.com$/.test(new URL(u, document.baseURI).hostname.replace(/\.$/, ''));
    } catch {
      return false;
    }
  };
  // Render-time referral normalization for links back to Unsplash:
  // appends utm_source/utm_medium when absent, preserves every existing
  // query param, never overwrites an existing utm_source, and passes
  // non-Unsplash URLs through untouched. Input is an ABSOLUTE validated
  // http(s) URL (the credit render funnel resolves + validates first).
  const withReferral = href => {
    try {
      const u = new URL(href);
      if (!/(^|\.)unsplash\.com$/.test(u.hostname.replace(/\.$/, ''))) {
        return href;
      }
      if (!u.searchParams.has('utm_source')) {
        u.searchParams.set('utm_source', 'claude_design');
      }
      if (!u.searchParams.has('utm_medium')) {
        u.searchParams.set('utm_medium', 'referral');
      }
      return u.toString();
    } catch (e) {
      return href;
    }
  };
  // 2× a ~600px slot in a 1920-wide deck — retina-sharp without making the
  // sidecar enormous. A 1200px WebP at q=0.85 is ~150-300KB.
  const MAX_DIM = 1200;
  // Raster formats only. SVG is excluded (can carry script; createImageBitmap
  // on SVG blobs is inconsistent). GIF is excluded because the canvas
  // re-encode keeps only the first frame, so an animated GIF would silently
  // go still — better to reject than surprise.
  const ACCEPT = ['image/png', 'image/jpeg', 'image/webp', 'image/avif'];

  // ── Shared sidecar store ────────────────────────────────────────────────
  // One fetch + immediate write-on-change for every <image-slot> on the
  // page. Reads via fetch() so viewing works anywhere the HTML and sidecar
  // are served together; writes go through window.omelette.writeFile, which
  // the host allowlists to *.state.json basenames only.
  const subs = new Set();
  let slots = {};
  // ids explicitly cleared before the sidecar fetch resolved — otherwise
  // the merge below can't tell "never set" from "just deleted" and would
  // resurrect the sidecar's stale value.
  const tombstones = new Set();
  let loaded = false;
  let loadP = null;
  function load() {
    if (loadP) return loadP;
    loadP = fetch(STATE_FILE).then(r => r.ok ? r.json() : null).then(j => {
      // Merge: sidecar loses to any in-memory change that raced ahead of
      // the fetch (drop or clear) so neither is clobbered by hydration.
      if (j && typeof j === 'object') {
        const merged = Object.assign({}, j, slots);
        // A framing-only write that raced ahead of hydration must not
        // drop a user image that's only on disk — inherit u from the
        // sidecar for any in-memory entry that lacks one.
        for (const k in slots) {
          if (merged[k] && !merged[k].u && j[k]) {
            merged[k].u = typeof j[k] === 'string' ? j[k] : j[k].u;
          }
        }
        for (const id of tombstones) delete merged[id];
        slots = merged;
      }
      tombstones.clear();
    }).catch(() => {}).then(() => {
      loaded = true;
      subs.forEach(fn => fn());
    });
    return loadP;
  }

  // Serialize writes so two near-simultaneous drops on different slots
  // can't reorder at the backend and leave the sidecar with only the
  // first. A save requested mid-flight just marks dirty and re-fires on
  // completion with the then-current slots.
  let saving = false;
  let saveDirty = false;
  // Unload-time flush: save()'s serialization defers a mid-RTT re-fire to a
  // .then that never runs in an unloading document, silently dropping a
  // pagehide commit. Post the current slots immediately instead — content
  // is a superset snapshot of any in-flight save's, the write is a
  // whole-file last-writer-wins replace, and postMessage FIFO delivers it
  // to the host after the in-flight one, so a backend-side reorder at
  // worst reproduces the dropped-commit outcome this flush improves on.
  // Guarded on the initial sidecar read: pre-hydration slots can miss
  // other slots' persisted entries, and flushing it would clobber them —
  // that narrow case stays best-effort (the in-memory merge in load()
  // cannot happen in an unloading document anyway).
  function flushNow() {
    if (!loaded) return;
    const w = window.omelette && window.omelette.writeFile;
    if (!w) return;
    try {
      Promise.resolve(w(STATE_FILE, JSON.stringify(slots))).catch(() => {});
    } catch (e) {}
  }
  function save() {
    if (saving) {
      saveDirty = true;
      return;
    }
    const w = window.omelette && window.omelette.writeFile;
    if (!w) return;
    saving = true;
    Promise.resolve(w(STATE_FILE, JSON.stringify(slots))).catch(() => {}).then(() => {
      saving = false;
      if (saveDirty) {
        saveDirty = false;
        save();
      }
    });
  }
  const S_MAX = 5;
  const clampS = s => Math.max(1, Math.min(S_MAX, s));

  // Normalize a stored slot value. Pre-reframe sidecars stored a bare
  // data-URL string; newer ones store {u, s, x, y}. Either shape is valid.
  function getSlot(id) {
    const v = slots[id];
    if (!v) return null;
    return typeof v === 'string' ? {
      u: v,
      s: 1,
      x: 0,
      y: 0
    } : v;
  }
  function setSlot(id, val) {
    if (!id) return;
    if (val) {
      slots[id] = val;
      tombstones.delete(id);
    } else {
      delete slots[id];
      if (!loaded) tombstones.add(id);
    }
    subs.forEach(fn => fn());
    // A drop is rare + high-value — write immediately so nav-away can't lose
    // it. Gate on the initial read so we don't overwrite a sidecar we haven't
    // merged yet; the merge in load() keeps this change once the read lands.
    if (loaded) save();else load().then(save);
  }

  // ── Image downscale ─────────────────────────────────────────────────────
  // Encode through a canvas so the sidecar carries resized bytes, not the
  // raw upload. Longest side is capped at 2× the slot's rendered width
  // (retina) and at MAX_DIM. WebP keeps alpha and is ~10× smaller than PNG
  // for photos, so there's no need for per-image format picking.
  async function toDataUrl(file, targetW) {
    const bitmap = await createImageBitmap(file);
    try {
      const cap = Math.min(MAX_DIM, Math.max(1, Math.round(targetW * 2)) || MAX_DIM);
      const scale = Math.min(1, cap / Math.max(bitmap.width, bitmap.height));
      const w = Math.max(1, Math.round(bitmap.width * scale));
      const h = Math.max(1, Math.round(bitmap.height * scale));
      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      canvas.getContext('2d').drawImage(bitmap, 0, 0, w, h);
      return canvas.toDataURL('image/webp', 0.85);
    } finally {
      bitmap.close && bitmap.close();
    }
  }

  // ── Custom element ──────────────────────────────────────────────────────
  const stylesheet =
  // Fill the container by default: slots are usually placed inside a
  // sized wrapper (a hero frame, a grid cell, an inset:0 layer) and are
  // expected to take that box — a fixed intrinsic size would render as
  // a small tile in the corner of a full-bleed wrapper instead.
  // aspect-ratio is the companion fallback that keeps a bare slot
  // visible when the parent's height is indefinite: height:100%
  // resolves to auto there, and the ratio then derives height from
  // width instead of letting the slot collapse to zero height.
  // Explicit width/height on the element override all of this.
  // color:inherit (not a fixed near-black): the placeholder chrome —
  // empty-state icon/caption (currentColor) and the dashed ring — must
  // read on dark decks too, and the slide's own text color is the one
  // color guaranteed to contrast with the slide background. The soft
  // look comes from opacity on those parts, not from a baked-in alpha.
  ':host{display:block;position:relative;' + '  font:13px/1.3 system-ui,-apple-system,sans-serif;' + '  width:100%;height:100%;aspect-ratio:3/2}' + '.empty .cap,.empty .sub{opacity:.75}' + '.frame{position:absolute;inset:0;overflow:hidden;background:rgba(127,127,127,.08)}' +
  // .frame img (clipped) and .spill (unclipped ghost + handles) share the
  // same left/top/width/height in frame-%, computed by _applyView(), so the
  // inside-mask crop and the outside-mask spill stay pixel-aligned.
  '.frame img{position:absolute;max-width:none;transform:translate(-50%,-50%);' + '  -webkit-user-drag:none;user-select:none;touch-action:none}' +
  // Reframe mode (double-click): the full image spills past the mask. The
  // spill layer is sized to the IMAGE bounds so its corners are where the
  // resize handles belong. The ghost <img> inside is translucent; the real
  // clipped <img> underneath shows the opaque in-mask crop.
  // popover=manual promotes the spill to the top layer on reframe, so it is
  // not clipped by any overflow:hidden / clip-path / scroll-container
  // ancestor (a plain z-index can't escape overflow clipping). UA popover
  // defaults (inset:0;margin:auto) are reset; _applyView sets viewport px.
  '.spill{position:fixed;margin:0;inset:auto;border:0;padding:0;background:transparent;' + '  overflow:visible;transform:translate(-50%,-50%);z-index:1;cursor:grab;touch-action:none}' + ':host([data-panning]) .spill{cursor:grabbing}' + '.spill .ghost{position:absolute;inset:0;width:100%;height:100%;opacity:.35;' + '  pointer-events:none;-webkit-user-drag:none;user-select:none;' + '  box-shadow:0 0 0 1px rgba(0,0,0,.2),0 12px 32px rgba(0,0,0,.2)}' + '.spill .handle{position:absolute;width:12px;height:12px;border-radius:50%;' + '  background:#fff;box-shadow:0 0 0 1.5px #c96442,0 1px 3px rgba(0,0,0,.3);' + '  transform:translate(-50%,-50%)}' + '.spill .handle[data-c=nw]{left:0;top:0;cursor:nwse-resize}' + '.spill .handle[data-c=ne]{left:100%;top:0;cursor:nesw-resize}' + '.spill .handle[data-c=sw]{left:0;top:100%;cursor:nesw-resize}' + '.spill .handle[data-c=se]{left:100%;top:100%;cursor:nwse-resize}' + ':host([data-reframe]){z-index:10}' + ':host([data-reframe]) .frame{box-shadow:0 0 0 2px #c96442}' + '.empty{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;' + '  justify-content:center;gap:6px;text-align:center;padding:12px;box-sizing:border-box;' + '  cursor:pointer;user-select:none}' + '.empty svg{opacity:.45}' + '.empty .cap{max-width:90%;font-weight:500;letter-spacing:.01em}' + '.empty .sub{font-size:11px}' + '.empty .sub u{text-underline-offset:2px}' + '.empty:hover .sub{opacity:1}' + ':host([data-over]) .frame{outline:2px solid #c96442;outline-offset:-2px;' + '  background:rgba(201,100,66,.10)}' + '.ring{position:absolute;inset:0;pointer-events:none;border:1.5px dashed currentColor;' + '  opacity:.35;transition:border-color .12s,opacity .12s}' + ':host([data-over]) .ring{border-color:#c96442;opacity:1}' + ':host([data-filled]) .ring{display:none}' +
  // Controls overlay INSIDE the frame, pinned to the top-right corner, so
  // a full-bleed slot in an overflow:hidden container still shows them
  // (the old below-mask placement got clipped). Credit sits bottom-left,
  // so top-right avoids collision. The blurred pill background keeps them
  // legible over the image.
  // The UA [popover] base rule styles the element in EVERY state (only
  // display:none is gated on :not(:popover-open), and the display:flex
  // below overrides that) — so the UA resets live HERE, like .spill's,
  // or the ordinary hover-state strip renders as a bordered Canvas box
  // centered by margin:auto. inset:auto precedes top/right (shorthand).
  '.ctl{position:absolute;inset:auto;top:8px;right:8px;margin:0;border:0;padding:0;' + '  background:transparent;overflow:visible;' + '  display:flex;gap:6px;opacity:0;pointer-events:none;transition:opacity .12s;z-index:2;' + '  white-space:nowrap}' +
  // While reframing, the spill owns the top layer and would swallow every
  // click on the in-frame controls. Promoting .ctl into the top layer
  // ABOVE the spill (shown after it — later popovers stack higher) keeps
  // Edit-as-toggle and Replace clickable mid-reframe. _applyView pins it
  // to the frame's top-right in viewport px (translateX(-100%)
  // right-aligns against the computed left edge); inset:auto clears the
  // base rule's top/right so the inline left/top position it alone.
  '.ctl:popover-open{position:fixed;inset:auto;transform:translateX(-100%)}' + ':host([data-filled][data-editable]:hover) .ctl,:host([data-reframe]) .ctl' + '  {opacity:1;pointer-events:auto}' + '.ctl button{appearance:none;border:0;border-radius:6px;padding:5px 10px;cursor:pointer;' + '  background:rgba(0,0,0,.65);color:#fff;font:11px/1 system-ui,-apple-system,sans-serif;' + '  backdrop-filter:blur(6px)}' + '.ctl button:hover{background:rgba(0,0,0,.8)}' + '.err{position:absolute;left:8px;bottom:8px;right:8px;color:#b3261e;font-size:11px;' + '  background:rgba(255,255,255,.85);padding:4px 6px;border-radius:5px;pointer-events:none}' +
  // Replacement in flight: after a src swap the browser keeps painting
  // the PREVIOUS image until the new one decodes, so a Replace would
  // flash the old photo and then pop. Hide the stale frame (visibility,
  // not display — _applyView geometry still applies) and spin until the
  // new image reports in (load/error clears data-swapping).
  ':host([data-swapping]) .frame img{visibility:hidden}' + '.loading{position:absolute;inset:0;display:none;align-items:center;' + '  justify-content:center;pointer-events:none}' + ':host([data-swapping]) .loading{display:flex}' + '.loading::after{content:"";width:22px;height:22px;border-radius:50%;' + '  border:2px solid rgba(127,127,127,.25);border-top-color:currentColor;' + '  animation:om-slot-spin .7s linear infinite}' + '@keyframes om-slot-spin{to{transform:rotate(360deg)}}' +
  // Reduced motion: the static two-tone ring still reads as "working".
  '@media (prefers-reduced-motion:reduce){.loading::after{animation:none}}' + '.credit{position:absolute;left:6px;bottom:6px;max-width:calc(100% - 12px);display:none;' + '  padding:3px 7px;border-radius:5px;background:rgba(0,0,0,.55);color:#fff;' + '  font:10px/1.2 system-ui,-apple-system,sans-serif;text-decoration:none;' + '  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;backdrop-filter:blur(6px)}' +
  // The credit is a SPAN holding one or two <a>s (Unsplash's prescribed
  // form links the photographer AND Unsplash) — anchors style inline so
  // the overlay reads as one line of text.
  '.credit a{color:inherit;text-decoration:none}' + '.credit a:hover,.credit a:focus-visible{text-decoration:underline}' + ':host([data-filled][data-credit]) .credit{display:block}' +
  // Exports must ship JUST the image — no hover controls, no credit chip
  // (the host marks <html data-om-exporting> for the capture window; the
  // page-level hide script can't reach shadow DOM, this rule can).
  ':host-context([data-om-exporting]) .ctl,' + ':host-context([data-om-exporting]) .credit{display:none !important}' +
  // Print must ship just the image too: the hover-gated controls can be
  // mid-hover when print() fires, and the credit chip is screen chrome —
  // the same rule the capture window gets, keyed on print media instead
  // of the host's data-om-exporting mark (the print path sets no mark).
  '@media print{.ctl,.credit{display:none !important}}' +
  // No export-window mask rules here on purpose: the export capture
  // releases the replacement mask by REMOVING data-swapping (the
  // shadow-root pass in pages/export/shared.ts HIDE_EXPORT_CHROME_SCRIPT)
  // — attribute removal works in every engine (:host-context is
  // Chromium-only), is scoped by construction to slots actually
  // mid-swap, and hides the spinner through the same gate. A masked img
  // would otherwise be silently dropped from PPTX decks (the capture
  // walk skips visibility:hidden imgs).
  // Attribution error tile: REPLACES the photo when an Unsplash src has
  // no credit attribute — rendering the photo uncredited is the terms
  // violation, so the photo must not appear at all.
  // Calm and neutral on purpose (review feedback): the tile informs the
  // user; the fix instructions are machine-facing (usage docblock, tool
  // description, and the turn-end scan's bounce copy name the attributes
  // for the agent).
  '.attr-error{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;' + '  justify-content:center;gap:6px;text-align:center;padding:12px;box-sizing:border-box;' + '  background:#f2f1ef;color:#6e6c66;user-select:none;' + '  font:13px/1.45 system-ui,-apple-system,sans-serif}' + '.attr-error svg{opacity:.55}' + '.attr-error .cap{max-width:92%;font-weight:500;letter-spacing:.01em}' + ':host([data-attribution-error]) .attr-error{display:flex}' + ':host([data-attribution-error]) .ring{display:none}';
  const icon = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' + 'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' + '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>' + '<path d="m21 15-5-5L5 21"/></svg>';
  const warnIcon = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' + 'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' + '<path d="m21.73 18-8-14a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>' + '<path d="M12 9v4"/><path d="M12 17h.01"/></svg>';
  class ImageSlot extends HTMLElement {
    static get observedAttributes() {
      return ['shape', 'radius', 'mask', 'fit', 'placeholder', 'src', 'id', 'credit', 'credit-href'];
    }

    /** Duplicate-slide hook (called by deck-stage, see its
     *  _remintDuplicateIds): copy this id's stored image, if any, under a
     *  freshly minted key and return that key — so a duplicated slide's
     *  slot keeps its dropped photo instead of reverting to the
     *  placeholder. 'isFree' is the caller's uniqueness check (document
     *  ids); candidates must ALSO be unused in the sidecar, which can
     *  hold keys from other pages sharing the project root. (An EMPTY
     *  slot on another page leaves no sidecar entry, so its id is not
     *  detectable here — a minted key can collide with it and that slot
     *  would show this photo. Same blast radius as two pages reusing an
     *  id by hand, which the shared sidecar already permits.) Returns null
     *  when no id could be minted (caller strips the id, today's
     *  behavior). */
    static cloneSlot(fromId, isFree) {
      if (typeof fromId !== 'string' || !fromId) return null;
      // Pre-hydration the store can't veto candidates or source the copy
      // — degrade to the strip (today's behavior) rather than mint
      // against keys we can't see yet. Any rendered (= droppable) slot
      // means load() has already settled.
      if (!loaded) return null;
      const stem = fromId.replace(/-\d+$/, '') || fromId;
      for (let n = 2; n < 100; n++) {
        const toId = stem + '-' + n;
        if (toId === fromId) continue;
        if (slots[toId] !== undefined) {
          // Reuse a key holding this exact value (bytes AND crop) if no
          // live element here owns it — a duplicate op the host refused
          // after minting leaves such a key behind, and reusing keeps
          // refused retries from accumulating one orphaned copy per
          // attempt. Full equality (not just bytes) so a byte-identical
          // key another PAGE owns with its own crop is stepped past, not
          // adopted or rewritten. (Entries without .u never match.)
          const prev = getSlot(toId);
          const cur = getSlot(fromId);
          if (!(prev && cur && prev.u && prev.u === cur.u && prev.s === cur.s && prev.x === cur.x && prev.y === cur.y && (typeof isFree !== 'function' || isFree(toId)))) continue;
          return toId;
        }
        if (typeof isFree === 'function' && !isFree(toId)) continue;
        const v = getSlot(fromId);
        if (v) setSlot(toId, Object.assign({}, v));
        return toId;
      }
      return null;
    }
    constructor() {
      super();
      // clonable: rail thumbnails deep-clone slides and carry this shadow
      // along; reuse an already-cloned root so upgrade-after-clone works.
      // (Deliberately NOT serializable — a getHTML consumer would embed
      // multi-MB sidecar data-URLs into serialized page HTML.)
      const root = this.shadowRoot || this.attachShadow({
        mode: 'open',
        clonable: true
      });
      // .spill and .ctl sit OUTSIDE .frame so overflow:hidden + border-radius
      // on the frame (circle, pill, rounded) can't clip them.
      root.innerHTML = '<style>' + stylesheet + '</style>' + '<div class="frame" part="frame">' + '  <img part="image" alt="" draggable="false" style="display:none">' + '  <div class="empty" part="empty">' + icon + '    <div class="cap"></div>' + '    <div class="sub">or <u>browse files</u></div></div>' + '  <div class="attr-error" part="attribution-error">' + warnIcon + '    <div class="cap">This photo needs attribution</div></div>' + '  <div class="loading" part="loading"></div>' + '  <div class="ring" part="ring"></div>' + '</div>' +
      // Outside .frame, like .spill/.ctl — the frame's overflow:hidden +
      // border-radius/clip-path would cut the credit off on circle/pill/mask.
      // A SPAN, not an <a>: the prescribed Unsplash credit holds two links
      // (photographer + Unsplash), built per-render in _render().
      '<span class="credit" part="credit"></span>' + '<div class="spill" popover="manual" data-dc-edit-transparent>' + '  <img class="ghost" alt="" draggable="false">' + '  <div class="handle" data-c="nw"></div><div class="handle" data-c="ne"></div>' + '  <div class="handle" data-c="sw"></div><div class="handle" data-c="se"></div>' + '</div>' +
      // data-dc-edit-transparent: the DC editor's edit-mode picker lets
      // clicks through for chrome marked with it (EDIT_TRANSPARENT_SEL)
      // — without it, Replace/Edit clicks in Edit mode are swallowed by
      // element selection and the controls look dead.
      '<div class="ctl" popover="manual" data-dc-edit-transparent><button data-act="replace" title="Replace image">Replace</button>' + '  <button data-act="edit" title="Reframe image">Edit</button></div>' + '<input type="file" accept="' + ACCEPT.join(',') + '" hidden>';
      this._frame = root.querySelector('.frame');
      this._ring = root.querySelector('.ring');
      this._img = root.querySelector('.frame img');
      this._empty = root.querySelector('.empty');
      this._cap = root.querySelector('.cap');
      this._sub = root.querySelector('.sub');
      this._spill = root.querySelector('.spill');
      this._ctl = root.querySelector('.ctl');
      this._credit = root.querySelector('.credit');
      this._attrError = root.querySelector('.attr-error');
      // Credit clicks open the link, not browse/reframe.
      this._credit.addEventListener('click', e => e.stopPropagation());
      this._credit.addEventListener('dblclick', e => e.stopPropagation());
      this._ghost = root.querySelector('.ghost');
      this._err = null;
      this._input = root.querySelector('input');
      this._depth = 0;
      this._gen = 0;
      // Encode-in-flight marker (the owning _ingest generation): while set,
      // the same-src "nothing in flight" clear in _render must not fire —
      // the stored value still points at the OLD image until the encode
      // lands, so that clear would unmask the stale image mid-replace.
      this._swapGen = 0;
      // Render-owned swap in flight: set when _render assigns a new src,
      // cleared only by the img's own load/error (or the empty branch).
      // img.complete CANNOT stand in for this — setting src only QUEUES
      // the current-request swap (a microtask), so synchronously after an
      // assignment, complete still reports the OLD settled request. The
      // pick path does exactly that: the host sets src, credit, and
      // credit-href back-to-back in one task, and renders #2/#3 would
      // read the stale complete === true and drop the mask one render
      // after it was set.
      this._loadPending = false;
      // See _render's empty branch: a transient attribution-error wipe of a
      // showing image must make the follow-up render a replacement (spinner),
      // not a first fill (blank frame).
      this._hidShowing = false;
      this._view = {
        s: 1,
        x: 0,
        y: 0
      };
      this._subFn = () => this._render();
      // Shadow-DOM listeners live with the shadow DOM — bound once here so
      // disconnect/reconnect (e.g. React remount) doesn't stack handlers.
      this._empty.addEventListener('click', () => this._input.click());
      root.addEventListener('click', e => {
        const act = e.target && e.target.getAttribute && e.target.getAttribute('data-act');
        if (!act) return;
        // The hidden controls are opacity-0 but still tabbable — without
        // this gate a keyboard user could drive them on a read-only share
        // link (mirrors the dblclick handler's editable gate).
        if (!this.hasAttribute('data-editable')) return;
        if (act === 'replace') {
          this._exitReframe(true);
          // Host-owned picker (Unsplash modal; it also offers local import).
          this.dispatchEvent(new CustomEvent('image-slot:pick', {
            bubbles: true,
            composed: true,
            detail: {
              id: this.id || null
            }
          }));
        }
        if (act === 'edit') {
          if (!this._reframes()) return;
          if (this.hasAttribute('data-reframe')) this._exitReframe(true);else this._enterReframe();
        }
      });
      this._input.addEventListener('change', () => {
        const f = this._input.files && this._input.files[0];
        if (f) this._ingest(f);
        this._input.value = '';
      });
      // naturalWidth/Height aren't known until load — re-apply so the cover
      // baseline is computed from real dimensions, not the 100%×100% fallback.
      // load/error also release the replacement-in-flight mask (via the
      // single discipline in _releaseMask): the swap is only revealed once
      // the new image can actually paint (on error the frame shows its
      // background, same as a fresh slot with a broken src).
      this._img.addEventListener('load', () => {
        this._loadPending = false;
        this._releaseMask(true);
        this._applyView();
      });
      this._img.addEventListener('error', () => {
        this._loadPending = false;
        this._releaseMask(true);
      });
      // Gated only on editable — any filled slot can be repositioned/scaled,
      // regardless of fit. Share links (no writeFile) stay static.
      this.addEventListener('dblclick', e => {
        if (!this.hasAttribute('data-editable') || !this._reframes()) return;
        e.preventDefault();
        if (this.hasAttribute('data-reframe')) this._exitReframe(true);else this._enterReframe();
      });
      // Pan + resize both originate on the spill layer. A handle pointerdown
      // drives an aspect-locked resize anchored at the opposite corner; any
      // other pointerdown on the spill pans. Offsets are frame-% so a
      // reframed slot survives responsive resize / PPTX export.
      this._spill.addEventListener('pointerdown', e => {
        if (e.button !== 0 || !this.hasAttribute('data-reframe')) return;
        e.preventDefault();
        e.stopPropagation();
        this._spill.setPointerCapture(e.pointerId);
        const rect = this.getBoundingClientRect();
        const fw = rect.width || 1,
          fh = rect.height || 1;
        const corner = e.target.getAttribute && e.target.getAttribute('data-c');
        let move;
        if (corner) {
          // Resize about the OPPOSITE corner. Viewport-px throughout (rect
          // fw/fh, not clientWidth) so the math survives a transform:scale()
          // ancestor — deck_stage renders slides scaled-to-fit.
          const iw = this._img.naturalWidth || 1,
            ih = this._img.naturalHeight || 1;
          const contain = (this.getAttribute('fit') || 'cover').toLowerCase() === 'contain';
          const base = contain ? Math.min(fw / iw, fh / ih) : Math.max(fw / iw, fh / ih);
          const sx = corner.includes('e') ? 1 : -1;
          const sy = corner.includes('s') ? 1 : -1;
          const s0 = this._view.s;
          const w0 = iw * base * s0,
            h0 = ih * base * s0;
          const cx0 = (50 + this._view.x) / 100 * fw;
          const cy0 = (50 + this._view.y) / 100 * fh;
          const ox = cx0 - sx * w0 / 2,
            oy = cy0 - sy * h0 / 2;
          const diag0 = Math.hypot(w0, h0);
          const ux = sx * w0 / diag0,
            uy = sy * h0 / diag0;
          move = ev => {
            const proj = (ev.clientX - rect.left - ox) * ux + (ev.clientY - rect.top - oy) * uy;
            const s = clampS(s0 * proj / diag0);
            const d = diag0 * s / s0;
            this._view.s = s;
            this._view.x = (ox + ux * d / 2) / fw * 100 - 50;
            this._view.y = (oy + uy * d / 2) / fh * 100 - 50;
            this._clampView();
            this._applyView();
          };
        } else {
          this.setAttribute('data-panning', '');
          const start = {
            px: e.clientX,
            py: e.clientY,
            x: this._view.x,
            y: this._view.y
          };
          move = ev => {
            this._view.x = start.x + (ev.clientX - start.px) / fw * 100;
            this._view.y = start.y + (ev.clientY - start.py) / fh * 100;
            this._clampView();
            this._applyView();
          };
        }
        const up = () => {
          try {
            this._spill.releasePointerCapture(e.pointerId);
          } catch {}
          this._spill.removeEventListener('pointermove', move);
          this._spill.removeEventListener('pointerup', up);
          this._spill.removeEventListener('pointercancel', up);
          this.removeAttribute('data-panning');
          this._dragUp = null;
        };
        // Stashed so _exitReframe (Escape / outside-click mid-drag) can
        // tear the capture + listeners down synchronously.
        this._dragUp = up;
        this._spill.addEventListener('pointermove', move);
        this._spill.addEventListener('pointerup', up);
        this._spill.addEventListener('pointercancel', up);
      });
      // Wheel zoom stays available inside reframe mode as a trackpad nicety —
      // zooms toward the cursor (offset' = cursor·(1-k) + offset·k).
      this.addEventListener('wheel', e => {
        if (!this.hasAttribute('data-reframe')) return;
        e.preventDefault();
        const r = this.getBoundingClientRect();
        const cx = (e.clientX - r.left) / r.width * 100 - 50;
        const cy = (e.clientY - r.top) / r.height * 100 - 50;
        const prev = this._view.s;
        const next = clampS(prev * Math.pow(1.0015, -e.deltaY));
        if (next === prev) return;
        const k = next / prev;
        this._view.s = next;
        this._view.x = cx * (1 - k) + this._view.x * k;
        this._view.y = cy * (1 - k) + this._view.y * k;
        this._clampView();
        this._applyView();
      }, {
        passive: false
      });
    }
    connectedCallback() {
      // Warn once per page — an id-less slot works for the session but
      // cannot persist, and two id-less slots would share nothing.
      if (!this.id && !ImageSlot._warned) {
        ImageSlot._warned = true;
        console.warn('<image-slot> without an id will not persist its dropped image.');
      }
      this.addEventListener('dragenter', this);
      this.addEventListener('dragover', this);
      this.addEventListener('dragleave', this);
      this.addEventListener('drop', this);
      subs.add(this._subFn);
      // The host may inject window.omelette.writeFile AFTER the first render;
      // re-render on hover so the editable-gated controls reliably appear.
      this.addEventListener('pointerenter', this._subFn);
      // width%/height% in _applyView encode the frame aspect at call time —
      // a host resize (responsive grid, pane divider) would stretch the
      // image until the next _render. Re-render on size change: _render()
      // re-seeds _view from stored before clamp/apply, so a shrink→grow
      // cycle round-trips instead of ratcheting x/y toward the narrower
      // frame's clamp range.
      this._ro = new ResizeObserver(() => this._render());
      this._ro.observe(this);
      load();
      this._render();
    }
    disconnectedCallback() {
      subs.delete(this._subFn);
      this.removeEventListener('pointerenter', this._subFn);
      this.removeEventListener('dragenter', this);
      this.removeEventListener('dragover', this);
      this.removeEventListener('dragleave', this);
      this.removeEventListener('drop', this);
      if (this._ro) {
        this._ro.disconnect();
        this._ro = null;
      }
      // commit=false: a disconnect is not a user intent — committing here
      // would persist whatever half-finished drag a React remount or DOM
      // splice happened to interrupt. Deliberate exits commit on their own
      // paths (Escape/click-out/toggle), and unloads commit via pagehide.
      this._exitReframe(false);
    }
    _enterReframe() {
      if (this.hasAttribute('data-reframe')) return;
      this.setAttribute('data-reframe', '');
      this._signalReframe(true);
      // Best-effort commit when the document unloads mid-reframe (a host
      // navigation racing the enter signal, a manual reload, tab close):
      // the sidecar write rides the host bridge, which outlives this
      // document, so the crop survives even though the mode dies with the
      // DOM. Held on the instance so _exitReframe detaches exactly what
      // was attached.
      this._pagehide = () => {
        this._exitReframe(true);
        flushNow();
      };
      window.addEventListener('pagehide', this._pagehide);
      // Promote spill to the top layer, then keep it pinned over the frame:
      // scroll/resize cover the common cases, and a per-frame rect check
      // catches layout shifts that fire neither (an image above finishing
      // load, streamed DOM pushing the slot down, an ancestor transform
      // change) so the overlay can't detach from the frame.
      try {
        this._spill.showPopover();
      } catch {}
      // After the spill, so the controls stack above it in the top layer.
      try {
        this._ctl.showPopover();
      } catch {}
      this._reposition = () => {
        if (this.hasAttribute('data-reframe')) this._applyView();
      };
      window.addEventListener('scroll', this._reposition, true);
      window.addEventListener('resize', this._reposition);
      this._lastRect = '';
      this._watch = () => {
        if (!this.hasAttribute('data-reframe')) return;
        const r = this.getBoundingClientRect();
        const key = r.left + ',' + r.top + ',' + r.width + ',' + r.height;
        if (key !== this._lastRect) {
          this._lastRect = key;
          this._applyView();
        }
        this._watchId = requestAnimationFrame(this._watch);
      };
      this._watchId = requestAnimationFrame(this._watch);
      this._applyView();
      // Close on click outside (the spill handler stopPropagation()s so
      // in-image drags don't reach this) and on Escape. Listeners are held
      // on the instance so _exitReframe / disconnectedCallback can detach
      // exactly what was attached.
      this._outside = e => {
        if (e.composedPath && e.composedPath().includes(this)) return;
        this._exitReframe(true);
      };
      this._esc = e => {
        if (e.key === 'Escape') this._exitReframe(true);
      };
      document.addEventListener('pointerdown', this._outside, true);
      document.addEventListener('keydown', this._esc, true);
    }
    _exitReframe(commit) {
      if (!this.hasAttribute('data-reframe')) return;
      if (this._dragUp) this._dragUp();
      this.removeAttribute('data-reframe');
      this.removeAttribute('data-panning');
      if (this._outside) document.removeEventListener('pointerdown', this._outside, true);
      if (this._esc) document.removeEventListener('keydown', this._esc, true);
      this._outside = this._esc = null;
      if (this._reposition) {
        window.removeEventListener('scroll', this._reposition, true);
        window.removeEventListener('resize', this._reposition);
        this._reposition = null;
      }
      if (this._watchId) {
        cancelAnimationFrame(this._watchId);
        this._watchId = 0;
      }
      if (this._pagehide) {
        window.removeEventListener('pagehide', this._pagehide);
        this._pagehide = null;
      }
      try {
        this._spill.hidePopover();
      } catch {}
      try {
        this._ctl.hidePopover();
      } catch {}
      this._ctl.style.left = '';
      this._ctl.style.top = '';
      if (commit) this._commitView();
      this._signalReframe(false);
    }

    // Reframe state lives only in this DOM until commit, invisible to the
    // host's dirty signals — announce enter/exit so the host can hold
    // auto-reloads for exactly the gesture (the guest bundle forwards
    // image-slot:reframe to the host as imageSlotReframe). Dispatched on
    // the element (composed, so it escapes shadow roots) while connected;
    // a disconnected exit (disconnectedCallback) falls back to document so
    // the host still hears it.
    _signalReframe(active) {
      const target = this.isConnected ? this : document;
      target.dispatchEvent(new CustomEvent('image-slot:reframe', {
        bubbles: true,
        composed: true,
        detail: {
          active: active,
          id: this.id || null
        }
      }));
    }

    // Public: host's "Import from computer" calls this to run local browse.
    openFilePicker() {
      this._exitReframe(true);
      this._input.click();
    }

    // A src write is a newer intent for this slot's content — the host
    // pick path (setImageSlotImage) or an agent edit — so it must win
    // over any encode still in flight from an earlier drop: left live,
    // that encode lands later, passes _ingest's gen guard, and its
    // setSlot silently overwrites the pick (the stored value shadows
    // src in _render). Bumping _gen kills the encode before its own
    // _swapGen clear runs, so clear the dead claim here too — otherwise
    // _releaseMask (gated on !_swapGen) never fires and the pick's
    // spinner is stranded. src ONLY: the pick sets credit/credit-href
    // in the same task, and clearing _swapGen on those would let the
    // same-src branch unmask the old image mid-encode.
    attributeChangedCallback(name, oldVal, newVal) {
      if (name === 'src' && oldVal !== newVal) {
        this._gen++;
        this._swapGen = 0;
      }
      if (this.shadowRoot) this._render();
    }

    // handleEvent — one listener object for all four drag events keeps the
    // add/remove symmetric and the depth counter correct.
    handleEvent(e) {
      if (e.type === 'dragenter' || e.type === 'dragover') {
        // Without preventDefault the browser never fires 'drop'.
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
        if (e.type === 'dragenter') this._depth++;
        this.setAttribute('data-over', '');
      } else if (e.type === 'dragleave') {
        // dragenter/leave fire for every descendant crossing — count depth
        // so hovering the icon inside the empty state doesn't flicker.
        if (--this._depth <= 0) {
          this._depth = 0;
          this.removeAttribute('data-over');
        }
      } else if (e.type === 'drop') {
        e.preventDefault();
        e.stopPropagation();
        this._depth = 0;
        this.removeAttribute('data-over');
        const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (f) this._ingest(f);
      }
    }
    async _ingest(file) {
      this._setError(null);
      if (!file || ACCEPT.indexOf(file.type) < 0) {
        this._setError('Drop a PNG, JPEG, WebP, or AVIF image.');
        return;
      }
      // toDataUrl can take hundreds of ms on a large photo. A Clear or a
      // newer drop during that window would be clobbered when this await
      // resumes — bump + capture a generation so stale encodes bail.
      const gen = ++this._gen;
      // Replacing a shown image: surface the swap through the encode too,
      // not just the decode — otherwise the old photo sits there with no
      // feedback while the canvas re-encode runs. An empty slot keeps its
      // placeholder (no spinner) until the encode lands, as before.
      // _swapGen guards the mask against re-renders DURING the encode
      // (pointerenter, ResizeObserver, another slot's store write): the
      // stored value still resolves to the old image there, so _render's
      // same-src clear would otherwise unmask it mid-replace.
      if (this.hasAttribute('data-filled')) {
        this.setAttribute('data-swapping', '');
        this._swapGen = gen;
      }
      try {
        const w = this.clientWidth || this.offsetWidth || MAX_DIM;
        const url = await toDataUrl(file, w);
        if (gen !== this._gen) return;
        // Only exit reframe once the new image is in hand — a rejected type
        // or decode failure leaves the in-progress crop untouched.
        this._exitReframe(false);
        // Clear BEFORE setSlot: its synchronous re-render must see no
        // pending encode, so a byte-identical re-upload (same data URL, no
        // load event coming) still clears the mask via the complete branch.
        this._swapGen = 0;
        const val = {
          u: url,
          s: 1,
          x: 0,
          y: 0
        };
        setSlot(this.id || '', val);
        // Keep a session-local copy for id-less slots so the drop still
        // shows, even though it cannot persist.
        if (!this.id) {
          this._local = val;
          this._render();
        }
      } catch (err) {
        if (gen !== this._gen) return;
        this._swapGen = 0;
        // Reveal the kept old image — unless another replacement (a
        // remote pick's src swap) is still in flight, in which case the
        // mask stays until THAT image settles (its load/error releases).
        this._releaseMask();
        this._setError('Could not read that image.');
        console.warn('<image-slot> ingest failed:', err);
      }
    }
    _setError(msg) {
      if (this._err) {
        this._err.remove();
        this._err = null;
      }
      if (!msg) return;
      const d = document.createElement('div');
      d.className = 'err';
      d.textContent = msg;
      this.shadowRoot.appendChild(d);
      this._err = d;
      setTimeout(() => {
        if (this._err === d) {
          d.remove();
          this._err = null;
        }
      }, 3000);
    }

    // Reframing (pan/resize) is available on any filled slot — the user can
    // always reposition/scale. `fit` only sets the initial baseline (see
    // _geom): contain starts fully-visible, cover starts frame-filling.
    _reframes() {
      return this.hasAttribute('data-filled');
    }

    // The single release discipline for the replacement-in-flight mask
    // (data-swapping). The mask comes off only when BOTH hold:
    //  - no encode is pending (_swapGen) — mid-encode the stored value
    //    still resolves to the old image, so any reveal paints it;
    //  - the frame img has settled on its current src — an unsettled src
    //    means some replacement is still in flight (e.g. a remote pick),
    //    whoever started it, and revealing would paint the previous
    //    frame. The load/error listeners pass settled=true (the event IS
    //    the settlement signal, per spec complete is true by then);
    //    other callers rely on the complete flag (covers loaded AND
    //    failed).
    // Every release path funnels through here EXCEPT _render's empty
    // branch (the img is being cleared — nothing will ever settle).
    _releaseMask(settled) {
      if (!this._swapGen && !this._loadPending && (settled || this._img.complete)) {
        this.removeAttribute('data-swapping');
      }
    }

    // Baseline geometry, shared by clamp/apply/resize. `base` is the scale at
    // view-scale s=1: cover = fill the frame (overflow on the looser axis),
    // contain = fit fully inside (letterboxed). Zooming a contain image past
    // s where it overflows naturally becomes a crop. Null until the img has
    // loaded (naturalWidth is 0 before that) or when the slot has no layout
    // box — ResizeObserver fires with a 0×0 rect under display:none, and
    // clamping against a degenerate 1×1 frame would silently pull the stored
    // pan toward zero.
    _geom() {
      const iw = this._img.naturalWidth,
        ih = this._img.naturalHeight;
      const fw = this.clientWidth,
        fh = this.clientHeight;
      if (!iw || !ih || !fw || !fh) return null;
      const contain = (this.getAttribute('fit') || 'cover').toLowerCase() === 'contain';
      const base = contain ? Math.min(fw / iw, fh / ih) : Math.max(fw / iw, fh / ih);
      return {
        iw,
        ih,
        fw,
        fh,
        base
      };
    }
    _clampView() {
      // Pan range on each axis is half the overflow past the frame edge.
      const g = this._geom();
      if (!g) return;
      const mx = Math.max(0, (g.iw * g.base * this._view.s / g.fw - 1) * 50);
      const my = Math.max(0, (g.ih * g.base * this._view.s / g.fh - 1) * 50);
      this._view.x = Math.max(-mx, Math.min(mx, this._view.x));
      this._view.y = Math.max(-my, Math.min(my, this._view.y));
    }
    _applyView() {
      const g = this._geom();
      // Top-layer controls: pin to the frame's top-right in viewport px
      // (the same 8px inset as the in-frame layout; unscaled — top-layer UI
      // reads as chrome, not page content). BEFORE the geometry branch:
      // placement needs only the frame rect, and a not-yet-loaded or broken
      // src must not leave the promoted strip floating unpositioned. Gated
      // on the popover actually being open: without the Popover API,
      // showPopover() threw (swallowed in _enterReframe), .ctl stays in
      // its in-frame absolute layout, and viewport-px coordinates would
      // shove it off-frame — and matches(':popover-open') itself throws
      // there (unknown pseudo-class), hence the try/catch.
      if (this.hasAttribute('data-reframe')) {
        let onTop = false;
        try {
          onTop = this._ctl.matches(':popover-open');
        } catch {}
        if (onTop) {
          const r = this.getBoundingClientRect();
          this._ctl.style.left = r.right - 8 + 'px';
          this._ctl.style.top = r.top + 8 + 'px';
        }
      }
      if (!g) {
        // Dimensions not known yet (before img load) — centered fit so there
        // is no flash of an unpositioned image before the geometry lands.
        const contain = (this.getAttribute('fit') || 'cover').toLowerCase() === 'contain';
        this._img.style.width = '100%';
        this._img.style.height = '100%';
        this._img.style.left = '50%';
        this._img.style.top = '50%';
        this._img.style.objectFit = contain ? 'contain' : 'cover';
        return;
      }
      // Baseline (cover-fill or contain-fit) × view scale. Width/height and
      // left/top are all frame-% — depends only on the frame aspect ratio, so
      // a responsive resize keeps the same crop. The spill layer mirrors the
      // same box so its corners = image corners.
      const k = g.base * this._view.s;
      const w = g.iw * k / g.fw * 100 + '%';
      const h = g.ih * k / g.fh * 100 + '%';
      const l = 50 + this._view.x + '%';
      const t = 50 + this._view.y + '%';
      this._img.style.width = w;
      this._img.style.height = h;
      this._img.style.left = l;
      this._img.style.top = t;
      this._img.style.objectFit = '';
      if (this.hasAttribute('data-reframe')) {
        // Top-layer spill: position in viewport px over the frame. The top
        // layer escapes ancestor transforms entirely, so EVERY term must be
        // in viewport units: getBoundingClientRect gives the frame's scaled
        // origin AND size, and the rect/layout ratio rescales the ghost —
        // sizing from layout px alone renders it 1/scale too large under a
        // scaled deck slide. Inner ghost + handles stay box-relative.
        const r = this.getBoundingClientRect();
        const sx = g.fw ? r.width / g.fw : 1;
        const sy = g.fh ? r.height / g.fh : 1;
        this._spill.style.width = g.iw * k * sx + 'px';
        this._spill.style.height = g.ih * k * sy + 'px';
        this._spill.style.left = r.left + (50 + this._view.x) / 100 * r.width + 'px';
        this._spill.style.top = r.top + (50 + this._view.y) / 100 * r.height + 'px';
      }
    }
    _commitView() {
      const v = {
        s: this._view.s,
        x: this._view.x,
        y: this._view.y
      };
      if (this._userUrl) v.u = this._userUrl;
      // Framing-only (no u) persists too so an author-src slot remembers its
      // crop; clearing the sidecar still falls through to src=.
      if (this.id) setSlot(this.id, v);else {
        this._local = v;
      }
    }
    _render() {
      // Shape / mask. Presets use border-radius so the dashed ring can
      // follow the rounded outline; clip-path is only applied for an
      // explicit `mask` (the ring is hidden there since a rectangle
      // dashed border chopped by an arbitrary polygon looks broken).
      const mask = this.getAttribute('mask');
      const shape = (this.getAttribute('shape') || 'rounded').toLowerCase();
      let radius = '';
      if (shape === 'circle') radius = '50%';else if (shape === 'pill') radius = '9999px';else if (shape === 'rounded') {
        const n = parseFloat(this.getAttribute('radius'));
        radius = (Number.isFinite(n) ? n : 12) + 'px';
      }
      this._frame.style.borderRadius = mask ? '' : radius;
      this._frame.style.clipPath = mask || '';
      this._ring.style.borderRadius = mask ? '' : radius;
      this._ring.style.display = mask ? 'none' : '';

      // Controls and reframe entry gate on this so share links stay read-only.
      const editable = !!(window.omelette && window.omelette.writeFile);
      this.toggleAttribute('data-editable', editable);
      this._sub.style.display = editable ? '' : 'none';

      // Content. The sidecar is also writable by the agent's write_file
      // tool, so its value isn't guaranteed canvas-originated — only accept
      // data:image/ URLs from it. The `src` attribute is author-controlled
      // (Claude wrote it into the HTML) so it passes through unchanged.
      let stored = this.id ? getSlot(this.id) : this._local;
      if (stored && stored.u && !/^data:image\//i.test(stored.u)) stored = null;
      const srcAttr = this.getAttribute('src') || '';
      this._userUrl = stored && stored.u || null;
      const url = this._userUrl || srcAttr;
      // Don't clobber an in-flight reframe with a store-triggered re-render.
      if (!this.hasAttribute('data-reframe')) {
        this._view = {
          s: stored && Number.isFinite(stored.s) ? clampS(stored.s) : 1,
          x: stored && Number.isFinite(stored.x) ? stored.x : 0,
          y: stored && Number.isFinite(stored.y) ? stored.y : 0
        };
      }
      this._cap.textContent = this.getAttribute('placeholder') || 'Drop an image';
      // Toggle via style.display — the [hidden] attribute alone loses to
      // the display:flex / display:block rules in the stylesheet above.
      // An Unsplash src with no credit attribute must NOT render — showing
      // the photo uncredited is the Unsplash-terms violation itself. The
      // error tile replaces the photo until the credit is written. A
      // user-dropped image is the user's own content and always renders.
      // Trimmed: credit is agent/user-editable content, and a whitespace-
      // only value must count as missing — otherwise it would suppress the
      // error tile AND render an empty credit box (no text, no links),
      // exactly the unattributed state this gate exists to prevent.
      const credit = (this.getAttribute('credit') || '').trim();
      const attrError = !!(!credit && !this._userUrl && srcAttr && isUnsplashHost(srcAttr));
      this.toggleAttribute('data-attribution-error', attrError);
      if (url && !attrError) {
        const prev = this._img.getAttribute('src');
        if (prev !== url) {
          // Replacing an already-shown image: mark the swap BEFORE setting
          // src so the stale frame is never revealed (see the data-swapping
          // stylesheet rules). First fill (prev empty) keeps the existing
          // placeholder-until-load behavior — no spinner. _hidShowing
          // covers the pick path's transient attribution-error wipe: prev
          // is gone, but an image WAS showing, so this is a replacement.
          if (prev || this._hidShowing) this.setAttribute('data-swapping', '');
          // Mark the swap BEFORE assigning src: complete keeps reporting
          // the old settled request until the browser's
          // update-the-image-data microtask runs, so same-task re-renders
          // (the pick path's credit/credit-href setAttributes) need this
          // flag, not complete, to know a load is in flight.
          this._loadPending = true;
          this._img.src = url;
          this._ghost.src = url;
        } else {
          // Same-src re-render — release if settled, so an ingest-set
          // spinner can't stick after a byte-identical re-upload (same
          // data URL, no further load event ever fires).
          this._releaseMask();
        }
        this._hidShowing = false;
        this._img.style.display = 'block';
        this._empty.style.display = 'none';
        this.setAttribute('data-filled', '');
        this._clampView();
        this._applyView();
      } else {
        this.removeAttribute('data-swapping');
        // The src is being removed — no load/error will ever fire for it.
        this._loadPending = false;
        // A transient attribution-error wipe of a showing image happens on
        // the pick path: the host sets src one setAttribute before credit,
        // so render N hides the old image (attrError) and render N+1
        // restores a URL. Remember the wipe so that restore renders as a
        // replacement (spinner), not a first fill (blank frame).
        this._hidShowing = attrError && !!this._img.getAttribute('src');
        this._img.style.display = 'none';
        this._img.removeAttribute('src');
        this._ghost.removeAttribute('src');
        // The error tile owns the blocked-photo state; .empty stays for
        // the genuinely-empty slot.
        this._empty.style.display = attrError ? 'none' : 'flex';
        this.removeAttribute('data-filled');
      }

      // Credit belongs to the author src, so a user drop hides it.
      // textContent + the http(s)-only funnel keep external strings inert.
      const showCredit = !!(url && credit && !this._userUrl && !attrError);
      this._credit.textContent = '';
      if (showCredit) {
        // Validate once (resolved against the document, http(s) only),
        // then append the terms-required utm referral params to links
        // that point back at unsplash.com.
        let href = '';
        const rawHref = this.getAttribute('credit-href') || '';
        if (rawHref) {
          try {
            const u = new URL(rawHref, document.baseURI);
            if (u.protocol === 'http:' || u.protocol === 'https:') {
              href = withReferral(u.href);
            }
          } catch {}
        }
        const mkLink = (text, linkHref) => {
          const a = document.createElement('a');
          a.setAttribute('target', '_blank');
          a.setAttribute('rel', 'noopener noreferrer');
          a.setAttribute('href', linkHref);
          a.textContent = text;
          return a;
        };
        // Unsplash's prescribed credit is TWO links — the photographer's
        // name to their profile (credit-href) and 'Unsplash' to the
        // homepage. Render that split whenever the text has the canonical
        // shape; other text keeps the legacy single-link rendering.
        const m = /^Photo by (.+) on Unsplash$/.exec(credit);
        if (m) {
          this._credit.appendChild(document.createTextNode('Photo by '));
          this._credit.appendChild(href ? mkLink(m[1], href) : document.createTextNode(m[1]));
          this._credit.appendChild(document.createTextNode(' on '));
          this._credit.appendChild(mkLink('Unsplash', UNSPLASH_HOMEPAGE_HREF));
        } else if (href) {
          this._credit.appendChild(mkLink(credit, href));
        } else {
          this._credit.textContent = credit;
        }
      }
      this.toggleAttribute('data-credit', showCredit);
    }
  }
  if (!customElements.get('image-slot')) {
    customElements.define('image-slot', ImageSlot);
  }
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/astrolabe/image-slot.js", error: String((e && e.message) || e) }); }

__ds_ns.AppBar = __ds_scope.AppBar;

__ds_ns.DayArc = __ds_scope.DayArc;

__ds_ns.HOUR_RULERS = __ds_scope.HOUR_RULERS;

__ds_ns.HourChip = __ds_scope.HourChip;

__ds_ns.LiveBanner = __ds_scope.LiveBanner;

__ds_ns.Masthead = __ds_scope.Masthead;

__ds_ns.SectionHeader = __ds_scope.SectionHeader;

__ds_ns.ContentCard = __ds_scope.ContentCard;

__ds_ns.OfferCard = __ds_scope.OfferCard;

__ds_ns.Prose = __ds_scope.Prose;

__ds_ns.VoteControl = __ds_scope.VoteControl;

__ds_ns.WorkCard = __ds_scope.WorkCard;

__ds_ns.SIGNS = __ds_scope.SIGNS;

__ds_ns.SIGN_NAMES = __ds_scope.SIGN_NAMES;

__ds_ns.ChartWheel = __ds_scope.ChartWheel;

__ds_ns.CodeBlock = __ds_scope.CodeBlock;

__ds_ns.DataRow = __ds_scope.DataRow;

__ds_ns.DataTable = __ds_scope.DataTable;

__ds_ns.Banner = __ds_scope.Banner;

__ds_ns.EmptyState = __ds_scope.EmptyState;

__ds_ns.Progress = __ds_scope.Progress;

__ds_ns.Skeleton = __ds_scope.Skeleton;

__ds_ns.Snackbar = __ds_scope.Snackbar;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Chip = __ds_scope.Chip;

__ds_ns.ChoiceRow = __ds_scope.ChoiceRow;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.TextField = __ds_scope.TextField;

__ds_ns.MARKS = __ds_scope.MARKS;

__ds_ns.Glyph = __ds_scope.Glyph;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.MoonDisc = __ds_scope.MoonDisc;

__ds_ns.ListRow = __ds_scope.ListRow;

__ds_ns.ListGroup = __ds_scope.ListGroup;

__ds_ns.SegmentedControl = __ds_scope.SegmentedControl;

__ds_ns.TABS = __ds_scope.TABS;

__ds_ns.TabBar = __ds_scope.TabBar;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.Sheet = __ds_scope.Sheet;

})();
