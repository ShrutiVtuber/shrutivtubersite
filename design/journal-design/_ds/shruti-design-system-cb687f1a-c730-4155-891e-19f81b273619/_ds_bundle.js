/* @ds-bundle: {"format":4,"namespace":"ShrutiDesignSystem_cb687f","components":[{"name":"Hero","sourcePath":"components/brand/Hero.jsx"},{"name":"LanguageSwitcher","sourcePath":"components/brand/LanguageSwitcher.jsx"},{"name":"LegalImprint","sourcePath":"components/brand/LegalImprint.jsx"},{"name":"LiveBadge","sourcePath":"components/brand/LiveBadge.jsx"},{"name":"SectionHeader","sourcePath":"components/brand/SectionHeader.jsx"},{"name":"SocialIcon","sourcePath":"components/brand/SocialLinkRow.jsx"},{"name":"SocialLinkRow","sourcePath":"components/brand/SocialLinkRow.jsx"},{"name":"SubscribeBlock","sourcePath":"components/brand/SubscribeBlock.jsx"},{"name":"AssetDownloadCard","sourcePath":"components/cards/AssetDownloadCard.jsx"},{"name":"FanArtCard","sourcePath":"components/cards/FanArtCard.jsx"},{"name":"ProjectCard","sourcePath":"components/cards/ProjectCard.jsx"},{"name":"StatBlock","sourcePath":"components/cards/StatBlock.jsx"},{"name":"VideoCard","sourcePath":"components/cards/VideoCard.jsx"},{"name":"VideoCardSkeleton","sourcePath":"components/cards/VideoCard.jsx"},{"name":"Prose","sourcePath":"components/content/Prose.jsx"},{"name":"EmptyState","sourcePath":"components/feedback/EmptyState.jsx"},{"name":"Modal","sourcePath":"components/feedback/Modal.jsx"},{"name":"Skeleton","sourcePath":"components/feedback/Skeleton.jsx"},{"name":"Toast","sourcePath":"components/feedback/Toast.jsx"},{"name":"Button","sourcePath":"components/forms/Button.jsx"},{"name":"ConsentCheckbox","sourcePath":"components/forms/ConsentCheckbox.jsx"},{"name":"SelectField","sourcePath":"components/forms/SelectField.jsx"},{"name":"TextArea","sourcePath":"components/forms/TextArea.jsx"},{"name":"TextField","sourcePath":"components/forms/TextField.jsx"},{"name":"Badge","sourcePath":"components/navigation/Badge.jsx"},{"name":"Breadcrumb","sourcePath":"components/navigation/Breadcrumb.jsx"},{"name":"Pagination","sourcePath":"components/navigation/Pagination.jsx"},{"name":"PeriodSwitcher","sourcePath":"components/navigation/PeriodSwitcher.jsx"},{"name":"SIGNS","sourcePath":"components/navigation/SignPicker.jsx"},{"name":"SignPicker","sourcePath":"components/navigation/SignPicker.jsx"},{"name":"Tag","sourcePath":"components/navigation/Tag.jsx"},{"name":"CreditList","sourcePath":"components/tables/CreditList.jsx"},{"name":"ExportBlock","sourcePath":"components/tables/ExportBlock.jsx"},{"name":"NextStation","sourcePath":"components/tables/NextStation.jsx"},{"name":"ProfileFieldTable","sourcePath":"components/tables/ProfileFieldTable.jsx"},{"name":"ScheduleItem","sourcePath":"components/tables/ScheduleItem.jsx"},{"name":"StationTable","sourcePath":"components/tables/StationTable.jsx"},{"name":"TimezoneToggle","sourcePath":"components/tables/TimezoneToggle.jsx"}],"sourceHashes":{"components/brand/Hero.jsx":"52bd39ac5ca7","components/brand/LanguageSwitcher.jsx":"b43c5e586f4d","components/brand/LegalImprint.jsx":"d4a646d949eb","components/brand/LiveBadge.jsx":"228e10578791","components/brand/SectionHeader.jsx":"3908986d8312","components/brand/SocialLinkRow.jsx":"42612c653c5b","components/brand/SubscribeBlock.jsx":"65df6f6f0371","components/cards/AssetDownloadCard.jsx":"41be3ac4c5f6","components/cards/FanArtCard.jsx":"81aaea8bfcb4","components/cards/ProjectCard.jsx":"7a99600cbd63","components/cards/StatBlock.jsx":"9cb66388525b","components/cards/VideoCard.jsx":"c4c0b9efca7e","components/content/Prose.jsx":"d1e8add435a8","components/feedback/EmptyState.jsx":"a0e2989d1c59","components/feedback/Modal.jsx":"aab7bc9289c7","components/feedback/Skeleton.jsx":"856e13709781","components/feedback/Toast.jsx":"d2ef0d25ffe6","components/forms/Button.jsx":"0806eeb3b137","components/forms/ConsentCheckbox.jsx":"710ff57bc3d1","components/forms/SelectField.jsx":"aa793bea716b","components/forms/TextArea.jsx":"7aa16508de6a","components/forms/TextField.jsx":"17df7e3b3ac4","components/navigation/Badge.jsx":"458ac69097c4","components/navigation/Breadcrumb.jsx":"4e7422715e28","components/navigation/Pagination.jsx":"ab872cd79c90","components/navigation/PeriodSwitcher.jsx":"86344829b4b7","components/navigation/SignPicker.jsx":"a49cc8b1f586","components/navigation/Tag.jsx":"12883e7bc0c0","components/tables/CreditList.jsx":"064df6230b2b","components/tables/ExportBlock.jsx":"8441a299b167","components/tables/NextStation.jsx":"4de0faa4770b","components/tables/ProfileFieldTable.jsx":"2d355a976e47","components/tables/ScheduleItem.jsx":"528cc1ba56ff","components/tables/StationTable.jsx":"77180c300ce0","components/tables/TimezoneToggle.jsx":"845622a08138","tailwind.preset.js":"2f5e3b184cd4","ui_kits/signs.js":"4dc82e78d0bc","ui_kits/site/About.jsx":"f7b1e007bd74","ui_kits/site/Account.jsx":"a966049fbb27","ui_kits/site/App.jsx":"95be04cd7476","ui_kits/site/Auth.jsx":"610fabad9f56","ui_kits/site/Chrome.jsx":"6c2ba5f3349b","ui_kits/site/Contact.jsx":"08392a28227c","ui_kits/site/FanWorks.jsx":"2441365cbaaf","ui_kits/site/Guidelines.jsx":"e8f025870cdd","ui_kits/site/Home.jsx":"404755e9eb51","ui_kits/site/Horoscopes.jsx":"ac170918aa66","ui_kits/site/Journal.jsx":"88fb28062c17","ui_kits/site/Legal.jsx":"7f0f2436a3a9","ui_kits/site/Newsletter.jsx":"e7bffeaa24b7","ui_kits/site/Press.jsx":"ec1adfe6354a","ui_kits/site/Schedule.jsx":"f7508c58fa9d","ui_kits/site/Stations.jsx":"56732c6315fa","ui_kits/site/Support.jsx":"05280d16f669","ui_kits/site/Today.jsx":"cf4f569d0bed","ui_kits/site/Videos.jsx":"be20f0a18465","ui_kits/site/Work.jsx":"f9b4e8f44092"},"inlinedExternals":[],"unexposedExports":[{"name":"fieldCss","sourcePath":"components/forms/TextField.jsx"}]} */

(() => {

const __ds_ns = (window.ShrutiDesignSystem_cb687f = window.ShrutiDesignSystem_cb687f || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/brand/Hero.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Hero({
  greeting,
  title,
  subtitle,
  actions,
  footnote,
  art,
  artAlt = '',
  clouds,
  minHeight = 420
}) {
  css('sh-hero', `.sh-hero{position:relative;border-radius:var(--radius-lg);overflow:hidden;background:linear-gradient(180deg,var(--sky-zenith) 0%,var(--sky-mid) 58%,var(--sky-horizon) 100%);transition:background var(--dur-3) var(--ease-in-out);display:flex;align-items:flex-end}.sh-hero .sh-hero-horizon{position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--horizon-line)}.sh-hero .sh-hero-clouds{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.28;mix-blend-mode:luminosity;pointer-events:none}.sh-hero .sh-hero-stars{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity var(--dur-3) var(--ease-in-out);background-image:radial-gradient(1px 1px at 12% 22%,rgba(233,230,240,.9) 50%,transparent 51%),radial-gradient(1px 1px at 28% 8%,rgba(233,230,240,.7) 50%,transparent 51%),radial-gradient(1.5px 1.5px at 44% 30%,rgba(233,230,240,.8) 50%,transparent 51%),radial-gradient(1px 1px at 61% 12%,rgba(233,230,240,.6) 50%,transparent 51%),radial-gradient(1px 1px at 73% 26%,rgba(233,230,240,.85) 50%,transparent 51%),radial-gradient(1.5px 1.5px at 86% 9%,rgba(233,230,240,.7) 50%,transparent 51%),radial-gradient(1px 1px at 93% 41%,rgba(233,230,240,.6) 50%,transparent 51%)}
[data-theme=dark] .sh-hero .sh-hero-stars{opacity:1}@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .sh-hero .sh-hero-stars{opacity:1}}
.sh-hero .sh-hero-inner{position:relative;z-index:2;display:grid;gap:16px;padding:clamp(24px,5vw,56px);max-width:60ch}
.sh-hero .sh-hero-greet{font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-soft)}
.sh-hero .sh-hero-title{font-family:var(--font-display);font-size:var(--text-hero);line-height:var(--leading-display);font-weight:500;letter-spacing:-0.01em;color:var(--ink);margin:0;text-wrap:balance}
.sh-hero .sh-hero-sub{font-family:var(--font-body);font-size:var(--text-h4);line-height:var(--leading-body);color:var(--ink-soft);margin:0;max-width:46ch}
.sh-hero .sh-hero-actions{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:4px}
.sh-hero .sh-hero-foot{margin-top:8px}
.sh-hero .sh-hero-art{position:absolute;right:clamp(16px,5vw,64px);bottom:0;z-index:1;width:clamp(200px,30%,340px);aspect-ratio:1;object-fit:cover;border-radius:var(--radius-lg) var(--radius-lg) 0 0;border:var(--border-w) solid color-mix(in srgb,var(--ink) 18%,transparent);border-bottom:0;box-shadow:var(--shadow-2)}
.sh-hero[data-art=present] .sh-hero-inner{max-width:min(56ch,58%)}
.sh-hero .sh-hero-moon{position:absolute;z-index:1;right:clamp(24px,8vw,96px);top:18%;width:clamp(56px,9vw,96px);aspect-ratio:1;border-radius:50%;border:1px solid color-mix(in srgb,var(--ink) 22%,transparent);background:color-mix(in srgb,var(--surface-card) 14%,transparent);pointer-events:none}
@media (max-width:720px){.sh-hero{align-items:flex-start}.sh-hero .sh-hero-art{position:relative;right:auto;display:block;margin:0 auto;width:min(70%,300px);order:2}.sh-hero[data-art=present]{flex-direction:column;align-items:stretch}.sh-hero[data-art=present] .sh-hero-inner{max-width:100%}}`);
  return /*#__PURE__*/React.createElement("section", {
    className: "sh-hero",
    "data-art": art ? 'present' : 'absent',
    style: {
      minHeight
    }
  }, clouds && /*#__PURE__*/React.createElement("img", {
    className: "sh-hero-clouds",
    src: clouds,
    alt: "",
    "aria-hidden": "true"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sh-hero-stars",
    "aria-hidden": "true"
  }), !art && /*#__PURE__*/React.createElement("div", {
    className: "sh-hero-moon",
    "aria-hidden": "true"
  }), /*#__PURE__*/React.createElement("div", {
    className: "sh-hero-inner"
  }, greeting && /*#__PURE__*/React.createElement("span", {
    className: "sh-hero-greet"
  }, greeting), /*#__PURE__*/React.createElement("h1", {
    className: "sh-hero-title"
  }, title), subtitle && /*#__PURE__*/React.createElement("p", {
    className: "sh-hero-sub"
  }, subtitle), actions && /*#__PURE__*/React.createElement("div", {
    className: "sh-hero-actions"
  }, actions), footnote && /*#__PURE__*/React.createElement("div", {
    className: "sh-hero-foot"
  }, footnote)), art && /*#__PURE__*/React.createElement("img", {
    className: "sh-hero-art",
    src: art,
    alt: artAlt
  }), /*#__PURE__*/React.createElement("div", {
    className: "sh-hero-horizon",
    "aria-hidden": "true"
  }));
}
Object.assign(__ds_scope, { Hero });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Hero.jsx", error: String((e && e.message) || e) }); }

// components/brand/LanguageSwitcher.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
const LANGS = {
  en: {
    code: 'EN',
    name: 'English'
  },
  el: {
    code: 'ΕΛ',
    name: 'Ελληνικά'
  },
  hi: {
    code: 'हि',
    name: 'हिन्दी'
  },
  fr: {
    code: 'FR',
    name: 'Français'
  }
};
function LanguageSwitcher({
  current = 'en',
  languages = ['en', 'el', 'hi', 'fr'],
  onChange,
  hrefFor
}) {
  css('sh-langsw', `.sh-lang{display:inline-flex;align-items:center;border:var(--border-w) solid var(--line);border-radius:var(--radius-full);padding:2px;background:var(--surface-card);gap:2px}.sh-lang [data-l]{appearance:none;border:0;background:transparent;font-family:var(--font-body);font-size:var(--text-xs);font-weight:600;letter-spacing:.04em;color:var(--ink-faint);padding:6px 11px;border-radius:var(--radius-full);cursor:pointer;text-decoration:none;line-height:1;transition:color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}.sh-lang [data-l]:hover{color:var(--ink)}.sh-lang [data-l][aria-current=true],.sh-lang [data-l][aria-pressed=true]{background:var(--surface-veil);color:var(--ink)}`);
  return /*#__PURE__*/React.createElement("nav", {
    className: "sh-lang",
    "aria-label": "Language"
  }, languages.map(l => {
    const L = LANGS[l] || {
      code: l.toUpperCase(),
      name: l
    };
    return hrefFor ? /*#__PURE__*/React.createElement("a", {
      key: l,
      "data-l": true,
      href: hrefFor(l),
      lang: l,
      hrefLang: l,
      title: L.name,
      "aria-current": l === current
    }, L.code) : /*#__PURE__*/React.createElement("button", {
      key: l,
      "data-l": true,
      type: "button",
      lang: l,
      title: L.name,
      "aria-pressed": l === current,
      onClick: () => onChange && onChange(l)
    }, L.code);
  }));
}
Object.assign(__ds_scope, { LanguageSwitcher });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/LanguageSwitcher.jsx", error: String((e && e.message) || e) }); }

// components/brand/LegalImprint.jsx
try { (() => {
function LegalImprint({
  entity = 'ShrutiVTuber, LLC',
  street = '[street, no.]',
  postcode = '[postcode]',
  city = 'Athens',
  country = 'GR',
  email = 'business@shrutivtuber.com',
  registry = 'GEMI [000000000000]',
  vat = 'VAT EL[000000000]',
  layout = 'stacked'
}) {
  const inline = layout === 'inline';
  const wrap = {
    margin: 0,
    font: `400 var(--text-xs)/${inline ? '1.7' : '1.9'} var(--font-mono)`,
    color: 'var(--ink-faint)',
    maxWidth: inline ? '68ch' : '40ch'
  };
  const sep = inline ? ' · ' : null;
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("p", {
    className: "t-eyebrow",
    style: {
      margin: '0 0 8px'
    }
  }, "Imprint"), /*#__PURE__*/React.createElement("p", {
    style: wrap
  }, entity, sep || /*#__PURE__*/React.createElement("br", null), "Registered office (virtual): ", street, " \xB7 ", postcode, " ", city, ", ", country, sep || /*#__PURE__*/React.createElement("br", null), /*#__PURE__*/React.createElement("a", {
    href: `mailto:${email}`,
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, email), sep || /*#__PURE__*/React.createElement("br", null), registry, " \xB7 ", vat));
}
Object.assign(__ds_scope, { LegalImprint });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/LegalImprint.jsx", error: String((e && e.message) || e) }); }

// components/brand/LiveBadge.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function LiveBadge({
  status = 'unknown',
  title,
  game,
  viewers,
  nextStream,
  href,
  compact = false
}) {
  css('sh-livebadge', `.sh-live{display:inline-flex;align-items:center;gap:10px;min-height:40px;padding:6px 14px 6px 10px;border-radius:var(--radius-full);border:var(--border-w) solid var(--line);background:var(--surface-card);font-family:var(--font-body);font-size:var(--text-sm);color:var(--ink-soft);text-decoration:none;max-width:100%;transition:border-color var(--dur-1) var(--ease-out)}a.sh-live:hover{border-color:var(--line-strong);color:var(--ink-soft)}.sh-live .sh-dot{width:8px;height:8px;border-radius:99px;flex:none}.sh-live[data-status=live]{border-color:color-mix(in srgb,var(--live) 45%,transparent);background:var(--live-wash)}.sh-live[data-status=live] .sh-dot{background:var(--live);animation:sh-pulse 2s var(--ease-in-out) infinite}.sh-live[data-status=offline] .sh-dot{background:var(--ink-faint);opacity:.5}.sh-live[data-status=unknown] .sh-dot{background:transparent;border:1.5px dashed var(--ink-faint);width:7px;height:7px}.sh-live .sh-word{font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:var(--text-micro)}.sh-live[data-status=live] .sh-word{color:var(--live)}.sh-live .sh-meta{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sh-live .sh-meta b{font-weight:600;color:var(--ink)}.sh-live .sh-count{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:var(--text-xs);color:var(--ink-faint);flex:none}@keyframes sh-pulse{0%,100%{opacity:1}50%{opacity:.35}}`);
  const Tag = href ? 'a' : 'span';
  const word = status === 'live' ? 'Live' : status === 'offline' ? 'Offline' : 'Status unavailable';
  return /*#__PURE__*/React.createElement(Tag, {
    className: "sh-live",
    "data-status": status,
    href: href,
    role: "status",
    "aria-live": "polite"
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-dot",
    "aria-hidden": "true"
  }), /*#__PURE__*/React.createElement("span", {
    className: "sh-word"
  }, word), !compact && status === 'live' && (title || game) && /*#__PURE__*/React.createElement("span", {
    className: "sh-meta"
  }, /*#__PURE__*/React.createElement("b", null, title), game ? /*#__PURE__*/React.createElement(React.Fragment, null, " \xB7 ", game) : null), !compact && status === 'live' && viewers != null && /*#__PURE__*/React.createElement("span", {
    className: "sh-count"
  }, Intl.NumberFormat().format(viewers), " watching"), !compact && status === 'offline' && /*#__PURE__*/React.createElement("span", {
    className: "sh-meta"
  }, nextStream ? /*#__PURE__*/React.createElement(React.Fragment, null, "next: ", /*#__PURE__*/React.createElement("b", null, nextStream)) : 'streams announced on Discord'), !compact && status === 'unknown' && /*#__PURE__*/React.createElement("span", {
    className: "sh-meta"
  }, "check Twitch directly"));
}
Object.assign(__ds_scope, { LiveBadge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/LiveBadge.jsx", error: String((e && e.message) || e) }); }

// components/brand/SectionHeader.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function SectionHeader({
  eyebrow,
  title,
  body,
  action,
  align = 'left',
  glyph,
  as: Tag = 'h2'
}) {
  css('sh-sectionheader', `.sh-sechead{display:grid;gap:10px;max-width:var(--measure-ui)}.sh-sechead[data-align=center]{justify-items:center;text-align:center;margin-inline:auto}.sh-sechead .sh-eyebrow{font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint);display:inline-flex;align-items:center;gap:8px}.sh-sechead .sh-eyebrow .sh-glyph{font-family:var(--font-display);font-size:1.1em;color:var(--rose);text-transform:none;letter-spacing:0}.sh-sechead .sh-title{font-family:var(--font-display);font-size:var(--text-h2);line-height:var(--leading-heading);font-weight:600;color:var(--ink);margin:0}.sh-sechead .sh-body{font-family:var(--font-body);font-size:var(--text-body);line-height:var(--leading-body);color:var(--ink-soft);margin:0}.sh-sechead .sh-action{margin-top:2px}`);
  return /*#__PURE__*/React.createElement("header", {
    className: "sh-sechead",
    "data-align": align
  }, eyebrow && /*#__PURE__*/React.createElement("span", {
    className: "sh-eyebrow"
  }, glyph && /*#__PURE__*/React.createElement("span", {
    className: "sh-glyph",
    "aria-hidden": "true"
  }, glyph), eyebrow), /*#__PURE__*/React.createElement(Tag, {
    className: "sh-title"
  }, title), body && /*#__PURE__*/React.createElement("p", {
    className: "sh-body"
  }, body), action && /*#__PURE__*/React.createElement("div", {
    className: "sh-action"
  }, action));
}
Object.assign(__ds_scope, { SectionHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/SectionHeader.jsx", error: String((e && e.message) || e) }); }

// components/brand/SocialLinkRow.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
const SLUGS = {
  twitch: 'twitch',
  youtube: 'youtube',
  discord: 'discord',
  x: 'x',
  twitter: 'x',
  github: 'github',
  kofi: 'kofi',
  instagram: 'instagram',
  bluesky: 'bluesky',
  mastodon: 'mastodon'
};
const URLS = {
  linkedin: 'https://unpkg.com/lucide-static@0.454.0/icons/linkedin.svg'
};
const NAMES = {
  twitch: 'Twitch',
  youtube: 'YouTube',
  discord: 'Discord',
  x: 'X',
  twitter: 'X',
  github: 'GitHub',
  linkedin: 'LinkedIn',
  kofi: 'Ko-fi',
  instagram: 'Instagram',
  bluesky: 'Bluesky',
  mastodon: 'Mastodon'
};
function SocialIcon({
  platform,
  size = 18
}) {
  const u = URLS[platform] || `https://cdn.simpleicons.org/${SLUGS[platform] || platform}`;
  return /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      display: 'inline-block',
      width: size,
      height: size,
      background: 'currentColor',
      WebkitMask: `url(${u}) center/contain no-repeat`,
      mask: `url(${u}) center/contain no-repeat`,
      flex: 'none'
    }
  });
}
function SocialLinkRow({
  links = [],
  variant = 'row',
  size = 18
}) {
  css('sh-socialrow', `.sh-socials{display:flex;flex-wrap:wrap;gap:6px;padding:0;margin:0;list-style:none}.sh-socials a{display:inline-flex;align-items:center;gap:8px;color:var(--ink-soft);text-decoration:none;padding:8px;border-radius:var(--radius-sm);transition:color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}.sh-socials a:hover{color:var(--accent-hover);background:var(--surface-veil)}.sh-socials a:active{transform:translateY(1px)}.sh-socials[data-variant=pills] a{border:var(--border-w) solid var(--line);padding:8px 14px}.sh-socials[data-variant=pills] a:hover{border-color:var(--line-strong)}.sh-socials .sh-lbl{font-family:var(--font-body);font-size:var(--text-sm)}`);
  return /*#__PURE__*/React.createElement("ul", {
    className: "sh-socials",
    "data-variant": variant
  }, links.map(l => /*#__PURE__*/React.createElement("li", {
    key: l.platform + (l.href || '')
  }, /*#__PURE__*/React.createElement("a", {
    href: l.href,
    "aria-label": l.label || NAMES[l.platform] || l.platform,
    title: l.label || NAMES[l.platform] || l.platform
  }, /*#__PURE__*/React.createElement(SocialIcon, {
    platform: l.platform,
    size: size
  }), variant === 'pills' && /*#__PURE__*/React.createElement("span", {
    className: "sh-lbl"
  }, l.label || NAMES[l.platform] || l.platform)))));
}
Object.assign(__ds_scope, { SocialIcon, SocialLinkRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/SocialLinkRow.jsx", error: String((e && e.message) || e) }); }

// components/brand/SubscribeBlock.jsx
try { (() => {
const {
  useId
} = React;
function SubscribeBlock({
  variant = 'panel',
  heading = 'The monthly letter',
  body = 'Your horoscope, what I published and streamed, and a letter I write by hand. Once a month, from Athens.',
  state = 'idle',
  email = '',
  onEmailChange,
  onSubmit,
  consented = false,
  onConsentChange,
  error
}) {
  const id = useId();
  const panel = variant === 'panel';
  const aside = variant === 'aside';
  if (state === 'sent') {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        background: 'var(--surface-card)',
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-1)',
        padding: panel ? 'var(--space-6) var(--space-5)' : 'var(--space-5)',
        display: 'grid',
        gap: 10
      }
    }, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        font: '400 1.5rem var(--font-display)',
        lineHeight: 1,
        color: 'var(--rose)'
      }
    }, "\u25D0"), /*#__PURE__*/React.createElement("h3", {
      style: {
        margin: 0,
        font: '600 var(--text-h3) var(--font-display)',
        color: 'var(--ink)'
      }
    }, "Check your email"), /*#__PURE__*/React.createElement("p", {
      style: {
        margin: 0,
        font: '400 var(--text-sm)/1.6 var(--font-body)',
        color: 'var(--ink-soft)',
        maxWidth: '52ch'
      }
    }, "A confirmation link is on its way to ", /*#__PURE__*/React.createElement("strong", {
      style: {
        fontWeight: 600,
        color: 'var(--ink)'
      }
    }, email || 'your address'), ". You are not subscribed until you click it \u2014 an unconfirmed address is not consent."), /*#__PURE__*/React.createElement("p", {
      style: {
        margin: 0,
        font: '400 var(--text-xs)/1.6 var(--font-mono)',
        color: 'var(--ink-faint)'
      }
    }, "Nothing arrives yet \xB7 the link expires in 24 hours \xB7 check spam if it does not appear"));
  }
  return /*#__PURE__*/React.createElement("form", {
    onSubmit: onSubmit,
    noValidate: true,
    style: {
      background: panel ? 'var(--surface-card)' : 'transparent',
      border: panel ? '1px solid var(--line)' : 'none',
      borderTop: panel ? undefined : '1px solid var(--line)',
      borderRadius: panel ? 'var(--radius-md)' : 0,
      boxShadow: panel ? 'var(--shadow-1)' : 'none',
      padding: panel ? 'var(--space-6) var(--space-5)' : 'var(--space-5) 0 0',
      display: 'grid',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)'
    }
  }, heading), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '56ch'
    }
  }, body)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-2)',
      flexWrap: aside ? 'wrap' : 'nowrap',
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement("label", {
    htmlFor: id,
    style: {
      position: 'absolute',
      width: 1,
      height: 1,
      overflow: 'hidden',
      clip: 'rect(0 0 0 0)'
    }
  }, "Email address"), /*#__PURE__*/React.createElement("input", {
    id: id,
    type: "email",
    inputMode: "email",
    autoComplete: "email",
    placeholder: "you@example.com",
    value: email,
    onChange: onEmailChange,
    "aria-invalid": error ? true : undefined,
    style: {
      flex: '1 1 200px',
      minWidth: 0,
      minHeight: 44,
      boxSizing: 'border-box',
      font: '400 var(--text-body) var(--font-mono)',
      color: 'var(--ink)',
      background: 'var(--surface-page)',
      padding: '10px 12px',
      border: '1px solid ' + (error ? 'var(--live)' : 'var(--line-strong)'),
      borderRadius: 'var(--radius-sm)'
    }
  }), /*#__PURE__*/React.createElement("button", {
    type: "submit",
    style: {
      flex: 'none',
      minHeight: 44,
      padding: '0 18px',
      cursor: 'pointer',
      font: '600 var(--text-sm) var(--font-body)',
      color: 'var(--on-accent)',
      background: 'var(--accent)',
      border: '1px solid var(--accent)',
      borderRadius: 'var(--radius-sm)'
    }
  }, "Subscribe")), error && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-sm) var(--font-body)',
      color: 'var(--live)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, "\u2715 "), error), /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'grid',
      gridTemplateColumns: '20px 1fr',
      gap: '2px 10px',
      padding: 'var(--space-3)',
      borderRadius: 'var(--radius-sm)',
      background: 'var(--surface-inset)',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: consented,
    onChange: onConsentChange,
    style: {
      width: 17,
      height: 17,
      margin: '2px 0 0',
      accentColor: 'var(--accent)',
      cursor: 'pointer'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Send me the monthly letter, ", /*#__PURE__*/React.createElement("strong", {
    style: {
      fontWeight: 600
    }
  }, "including offers for courses and services"), " when they open. I can unsubscribe in one click, and pause instead if I would rather.")), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-xs)/1.6 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "Double opt-in \xB7 one email a month \xB7 no tracking pixels \xB7 ", /*#__PURE__*/React.createElement("a", {
    href: "#privacy",
    style: {
      color: 'var(--accent)'
    }
  }, "what is stored")));
}
Object.assign(__ds_scope, { SubscribeBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/SubscribeBlock.jsx", error: String((e && e.message) || e) }); }

// components/cards/AssetDownloadCard.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function AssetDownloadCard({
  name,
  meta,
  preview,
  previewOn = 'checker',
  href,
  filename
}) {
  css('sh-assetcard', `.sh-asset{display:grid;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);overflow:hidden;font-family:var(--font-body);transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-asset:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-asset .sh-as-prev{height:120px;display:grid;place-items:center;border-bottom:var(--border-w) solid var(--line);padding:12px}
.sh-asset .sh-as-prev[data-on=checker]{background:repeating-conic-gradient(var(--surface-veil) 0 25%,var(--surface-card) 0 50%) 0 0/16px 16px}
.sh-asset .sh-as-prev[data-on=sky]{background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon))}
.sh-asset .sh-as-prev[data-on=ink]{background:var(--dusk-page)}
.sh-asset .sh-as-prev img{max-height:100%;max-width:100%}
.sh-asset .sh-as-prev [data-fallback]{font-family:var(--font-mono);font-size:11px;color:var(--ink-faint)}
.sh-asset .sh-as-body{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px}
.sh-asset .sh-as-name{font-size:var(--text-sm);font-weight:600;color:var(--ink);margin:0}
.sh-asset .sh-as-meta{font-family:var(--font-mono);font-size:10px;color:var(--ink-faint);letter-spacing:.02em}
.sh-asset .sh-as-dl{flex:none;display:inline-flex;align-items:center;gap:6px;font-size:var(--text-xs);font-weight:600;color:var(--accent);text-decoration:none;border:var(--border-w) solid color-mix(in srgb,var(--accent) 50%,transparent);border-radius:var(--radius-sm);padding:7px 12px;transition:background var(--dur-1) var(--ease-out)}
.sh-asset .sh-as-dl:hover{background:var(--accent-wash);color:var(--accent-hover)}
.sh-asset .sh-as-dl:active{transform:translateY(1px)}`);
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-asset"
  }, /*#__PURE__*/React.createElement("div", {
    className: "sh-as-prev",
    "data-on": previewOn
  }, preview || /*#__PURE__*/React.createElement("span", {
    "data-fallback": true
  }, "no preview")), /*#__PURE__*/React.createElement("div", {
    className: "sh-as-body"
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    className: "sh-as-name"
  }, name), meta && /*#__PURE__*/React.createElement("span", {
    className: "sh-as-meta"
  }, meta)), /*#__PURE__*/React.createElement("a", {
    className: "sh-as-dl",
    href: href,
    download: filename
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, "\u2913"), " Download")));
}
Object.assign(__ds_scope, { AssetDownloadCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/AssetDownloadCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/FanArtCard.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function FanArtCard({
  image,
  title,
  artist,
  artistHref,
  platform,
  onOpen
}) {
  css('sh-fanartcard', `.sh-fan{display:grid;gap:8px;font-family:var(--font-body)}
.sh-fan .sh-fan-img{position:relative;aspect-ratio:1;border-radius:var(--radius-md);border:var(--border-w) solid var(--line);overflow:hidden;background:var(--surface-veil);cursor:zoom-in;padding:0;appearance:none;display:block;width:100%;transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-fan .sh-fan-img:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-fan .sh-fan-img img{width:100%;height:100%;object-fit:cover;display:block}
.sh-fan .sh-fan-img[data-empty=true]{display:grid;place-items:center;cursor:default;background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon))}
.sh-fan .sh-fan-img [data-glyph]{font-family:var(--font-display);font-size:34px;color:color-mix(in srgb,var(--ink) 45%,transparent)}
.sh-fan .sh-fan-credit{display:flex;align-items:baseline;gap:6px;font-size:var(--text-sm)}
.sh-fan .sh-fan-by{color:var(--ink-faint);font-size:var(--text-xs)}
.sh-fan .sh-fan-artist{font-weight:600;color:var(--ink)}
.sh-fan a.sh-fan-artist{color:var(--ink);text-decoration-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.sh-fan a.sh-fan-artist:hover{color:var(--accent-hover)}
.sh-fan .sh-fan-title{font-size:var(--text-xs);color:var(--ink-soft);font-style:italic;font-family:var(--font-display);font-size:var(--text-sm)}`);
  return /*#__PURE__*/React.createElement("figure", {
    className: "sh-fan",
    style: {
      margin: 0
    }
  }, image ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "sh-fan-img",
    onClick: onOpen,
    "aria-label": `Open ${title || 'fan art'} by ${artist}`
  }, /*#__PURE__*/React.createElement("img", {
    src: image,
    alt: title || `Fan art by ${artist}`,
    loading: "lazy"
  })) : /*#__PURE__*/React.createElement("span", {
    className: "sh-fan-img",
    "data-empty": "true"
  }, /*#__PURE__*/React.createElement("span", {
    "data-glyph": true,
    "aria-hidden": "true"
  }, "\u2736")), /*#__PURE__*/React.createElement("figcaption", {
    className: "sh-fan-credit"
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-fan-by"
  }, "art by"), artistHref ? /*#__PURE__*/React.createElement("a", {
    className: "sh-fan-artist",
    href: artistHref
  }, artist) : /*#__PURE__*/React.createElement("span", {
    className: "sh-fan-artist"
  }, artist), platform && /*#__PURE__*/React.createElement("span", {
    className: "sh-fan-by"
  }, "on ", platform)), title && /*#__PURE__*/React.createElement("span", {
    className: "sh-fan-title"
  }, "\u201C", title, "\u201D"));
}
Object.assign(__ds_scope, { FanArtCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/FanArtCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/ProjectCard.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
const STATUS = {
  active: {
    word: 'Active',
    tone: 'accent'
  },
  maintained: {
    word: 'Maintained',
    tone: 'neutral'
  },
  archived: {
    word: 'Archived',
    tone: 'faint'
  }
};
function ProjectCard({
  name,
  tagline,
  description,
  status = 'active',
  repoHref,
  liveHref,
  screenshot,
  meta
}) {
  css('sh-projectcard', `.sh-proj{display:grid;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);box-shadow:var(--shadow-1);overflow:hidden;font-family:var(--font-body);transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-proj:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-proj .sh-proj-shot{aspect-ratio:16/9;background:var(--surface-inset);border-bottom:var(--border-w) solid var(--line);position:relative;overflow:hidden}
.sh-proj .sh-proj-shot img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
.sh-proj .sh-proj-shot[data-empty=true]{display:grid;place-items:center;background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon))}
.sh-proj .sh-proj-shot [data-plate]{font-family:var(--font-mono);font-size:11px;color:var(--ink-soft);background:color-mix(in srgb,var(--surface-page) 62%,transparent);backdrop-filter:blur(8px);border:var(--border-w) solid color-mix(in srgb,var(--line) 60%,transparent);border-radius:var(--radius-sm);padding:6px 12px}
.sh-proj .sh-proj-shot [data-horizon]{position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--horizon-line)}
.sh-proj .sh-proj-body{display:grid;gap:8px;padding:18px 20px 20px}
.sh-proj .sh-proj-top{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.sh-proj .sh-proj-name{font-family:var(--font-display);font-size:var(--text-h3);font-weight:600;color:var(--ink);margin:0}
.sh-proj .sh-proj-status{font-size:var(--text-micro);font-weight:600;letter-spacing:.06em;text-transform:uppercase;border-radius:var(--radius-full);padding:3px 9px;border:var(--border-w) solid}
.sh-proj .sh-proj-status[data-tone=accent]{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent);background:var(--accent-wash)}
.sh-proj .sh-proj-status[data-tone=neutral]{color:var(--ink-soft);border-color:var(--line);background:var(--surface-veil)}
.sh-proj .sh-proj-status[data-tone=faint]{color:var(--ink-faint);border-color:var(--line);background:transparent}
.sh-proj .sh-proj-tag{font-size:var(--text-sm);color:var(--ink-soft);font-style:italic;font-family:var(--font-display);font-size:var(--text-h4)}
.sh-proj .sh-proj-desc{font-size:var(--text-sm);line-height:var(--leading-body);color:var(--ink-soft);margin:0}
.sh-proj .sh-proj-meta{font-family:var(--font-mono);font-size:10.5px;color:var(--ink-faint);letter-spacing:.02em}
.sh-proj .sh-proj-links{display:flex;gap:14px;margin-top:6px;border-top:var(--border-w) solid var(--line);padding-top:12px}
.sh-proj .sh-proj-links a{font-size:var(--text-sm);font-weight:500}`);
  const st = STATUS[status] || STATUS.active;
  return /*#__PURE__*/React.createElement("article", {
    className: "sh-proj"
  }, /*#__PURE__*/React.createElement("div", {
    className: "sh-proj-shot",
    "data-empty": !screenshot
  }, screenshot ? /*#__PURE__*/React.createElement("img", {
    src: screenshot,
    alt: name + ' screenshot',
    loading: "lazy"
  }) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
    "data-plate": true
  }, "screenshot pending"), /*#__PURE__*/React.createElement("span", {
    "data-horizon": true,
    "aria-hidden": "true"
  }))), /*#__PURE__*/React.createElement("div", {
    className: "sh-proj-body"
  }, /*#__PURE__*/React.createElement("div", {
    className: "sh-proj-top"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "sh-proj-name"
  }, name), /*#__PURE__*/React.createElement("span", {
    className: "sh-proj-status",
    "data-tone": st.tone
  }, st.word)), tagline && /*#__PURE__*/React.createElement("p", {
    className: "sh-proj-tag"
  }, tagline), description && /*#__PURE__*/React.createElement("p", {
    className: "sh-proj-desc"
  }, description), meta && /*#__PURE__*/React.createElement("span", {
    className: "sh-proj-meta"
  }, meta), (repoHref || liveHref) && /*#__PURE__*/React.createElement("div", {
    className: "sh-proj-links"
  }, liveHref && /*#__PURE__*/React.createElement("a", {
    href: liveHref
  }, "Visit \u2197"), repoHref && /*#__PURE__*/React.createElement("a", {
    href: repoHref
  }, "Source \u2197"))));
}
Object.assign(__ds_scope, { ProjectCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/ProjectCard.jsx", error: String((e && e.message) || e) }); }

// components/cards/StatBlock.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function StatBlock({
  value,
  label,
  note,
  glyph
}) {
  css('sh-statblock', `.sh-stat{display:grid;gap:6px;padding:18px 20px;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);font-family:var(--font-body);position:relative}
.sh-stat .sh-st-value{font-family:var(--font-display);font-size:2.4rem;line-height:1;font-weight:500;color:var(--ink);font-variant-numeric:tabular-nums lining-nums}
.sh-stat .sh-st-label{font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint)}
.sh-stat .sh-st-note{font-size:var(--text-xs);color:var(--ink-soft)}
.sh-stat .sh-st-glyph{position:absolute;top:14px;right:16px;font-family:var(--font-display);font-size:18px;color:var(--rose)}`);
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-stat"
  }, glyph && /*#__PURE__*/React.createElement("span", {
    className: "sh-st-glyph",
    "aria-hidden": "true"
  }, glyph), /*#__PURE__*/React.createElement("span", {
    className: "sh-st-label"
  }, label), /*#__PURE__*/React.createElement("span", {
    className: "sh-st-value"
  }, value), note && /*#__PURE__*/React.createElement("span", {
    className: "sh-st-note"
  }, note));
}
Object.assign(__ds_scope, { StatBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/StatBlock.jsx", error: String((e && e.message) || e) }); }

// components/cards/VideoCard.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
const PLAT = {
  twitch: {
    name: 'Twitch',
    slug: 'twitch'
  },
  youtube: {
    name: 'YouTube',
    slug: 'youtube'
  }
};
function VideoCard({
  title,
  thumb,
  platform = 'twitch',
  duration,
  date,
  href = '#',
  loading = false
}) {
  css('sh-videocard', `.sh-vid{display:grid;gap:10px;text-decoration:none;color:inherit;font-family:var(--font-body);border-radius:var(--radius-md);outline-offset:4px}
.sh-vid .sh-vid-thumb{position:relative;aspect-ratio:16/9;border-radius:var(--radius-md);border:var(--border-w) solid var(--line);overflow:hidden;background:linear-gradient(180deg,var(--sky-zenith),var(--sky-mid) 58%,var(--sky-horizon));transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
.sh-vid .sh-vid-thumb img{width:100%;height:100%;object-fit:cover;display:block}
.sh-vid .sh-vid-play{position:absolute;inset:0;margin:auto;width:44px;height:44px;border-radius:99px;background:color-mix(in srgb,var(--surface-page) 72%,transparent);backdrop-filter:blur(6px);border:var(--border-w) solid color-mix(in srgb,var(--line) 70%,transparent);display:grid;place-items:center;color:var(--ink);font-size:15px;opacity:0;transition:opacity var(--dur-1) var(--ease-out)}
.sh-vid:hover .sh-vid-play,.sh-vid:focus-visible .sh-vid-play{opacity:1}
.sh-vid[data-noart=true] .sh-vid-play{opacity:1}
.sh-vid .sh-vid-dur{position:absolute;right:8px;bottom:8px;font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:10.5px;color:var(--ink);background:color-mix(in srgb,var(--surface-page) 80%,transparent);border:var(--border-w) solid color-mix(in srgb,var(--line) 60%,transparent);border-radius:4px;padding:2px 6px}
.sh-vid:hover .sh-vid-thumb{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-vid .sh-vid-title{font-size:var(--text-sm);font-weight:600;color:var(--ink);line-height:var(--leading-tight);margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color var(--dur-1) var(--ease-out)}
.sh-vid:hover .sh-vid-title{color:var(--accent-hover)}
.sh-vid .sh-vid-meta{display:flex;align-items:center;gap:8px;font-size:var(--text-xs);color:var(--ink-faint)}
.sh-vid .sh-vid-plat{display:inline-flex;align-items:center;gap:5px;font-weight:500}
.sh-vid .sh-vid-plat i{width:12px;height:12px;display:inline-block;background:currentColor}
.sh-vid .sh-vid-horizon{position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--horizon-line)}`);
  const p = PLAT[platform] || PLAT.twitch;
  if (loading) return /*#__PURE__*/React.createElement(VideoCardSkeleton, null);
  return /*#__PURE__*/React.createElement("a", {
    className: "sh-vid",
    href: href,
    "data-noart": !thumb
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-vid-thumb"
  }, thumb ? /*#__PURE__*/React.createElement("img", {
    src: thumb,
    alt: "",
    loading: "lazy"
  }) : /*#__PURE__*/React.createElement("span", {
    className: "sh-vid-horizon",
    "aria-hidden": "true"
  }), /*#__PURE__*/React.createElement("span", {
    className: "sh-vid-play",
    "aria-hidden": "true"
  }, "\u25B6"), duration && /*#__PURE__*/React.createElement("span", {
    className: "sh-vid-dur"
  }, duration)), /*#__PURE__*/React.createElement("h3", {
    className: "sh-vid-title"
  }, title), /*#__PURE__*/React.createElement("span", {
    className: "sh-vid-meta"
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-vid-plat"
  }, /*#__PURE__*/React.createElement("i", {
    "aria-hidden": "true",
    style: {
      WebkitMask: `url(https://cdn.simpleicons.org/${p.slug}) center/contain no-repeat`,
      mask: `url(https://cdn.simpleicons.org/${p.slug}) center/contain no-repeat`
    }
  }), p.name), date && /*#__PURE__*/React.createElement(React.Fragment, null, "\xB7", /*#__PURE__*/React.createElement("span", null, date))));
}
function VideoCardSkeleton() {
  css('sh-vidskel', '.sh-vid-skel{display:grid;gap:10px}.sh-vid-skel .sk{background:var(--surface-veil);border-radius:var(--radius-md);animation:sh-skel 1.6s var(--ease-in-out) infinite}.sh-vid-skel .sk-thumb{aspect-ratio:16/9}.sh-vid-skel .sk-t1{height:13px;width:82%;border-radius:4px}.sh-vid-skel .sk-t2{height:11px;width:40%;border-radius:4px}@keyframes sh-skel{0%,100%{opacity:1}50%{opacity:.55}}');
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-vid-skel",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("span", {
    className: "sk sk-thumb"
  }), /*#__PURE__*/React.createElement("span", {
    className: "sk sk-t1"
  }), /*#__PURE__*/React.createElement("span", {
    className: "sk sk-t2"
  }));
}
Object.assign(__ds_scope, { VideoCard, VideoCardSkeleton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/cards/VideoCard.jsx", error: String((e && e.message) || e) }); }

// components/content/Prose.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Prose({
  children,
  html,
  lang,
  byline,
  className = '',
  style
}) {
  css('sh-prose', `.sh-prose{font-family:var(--font-display);font-size:var(--text-prose);line-height:var(--leading-prose);color:var(--ink);max-width:var(--measure-prose)}
.sh-prose>*+*{margin-top:1em}
.sh-prose h2,.sh-prose h3{font-weight:600;line-height:var(--leading-heading);margin-top:1.6em}
.sh-prose h2{font-size:var(--text-h2)}.sh-prose h3{font-size:var(--text-h3)}
.sh-prose a{color:var(--accent)}.sh-prose a:hover{color:var(--accent-hover)}
.sh-prose strong{font-weight:600}
.sh-prose blockquote{margin:1.4em 0;padding:2px 0 2px 20px;border-left:2px solid var(--rose);font-style:italic;color:var(--ink-soft)}
.sh-prose code{font-family:var(--font-mono);font-size:.82em;background:var(--surface-veil);border:var(--border-w) solid var(--line);border-radius:4px;padding:1px 5px}
.sh-prose pre{font-family:var(--font-mono);font-size:.78em;line-height:1.6;background:var(--surface-inset);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);padding:16px 18px;overflow:auto}
.sh-prose pre code{background:none;border:0;padding:0}
.sh-prose hr{border:0;margin:2em 0;text-align:center}
.sh-prose hr::after{content:"⁂";font-size:.9em;color:var(--ink-faint);letter-spacing:.4em}
.sh-prose ul,.sh-prose ol{padding-left:1.3em}.sh-prose li+li{margin-top:.4em}
.sh-prose li::marker{color:var(--ink-faint)}
.sh-prose figure{margin:1.6em 0}.sh-prose figcaption{font-family:var(--font-body);font-size:var(--text-xs);color:var(--ink-faint);margin-top:8px}
.sh-prose img{border-radius:var(--radius-md);border:var(--border-w) solid var(--line)}
.sh-prose table{width:100%;border-collapse:collapse;font-family:var(--font-body);font-size:var(--text-sm)}
.sh-prose th{text-align:left;font-size:var(--text-micro);letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint);font-weight:600;padding:8px 12px 8px 0;border-bottom:var(--border-w) solid var(--line-strong)}
.sh-prose td{padding:10px 12px 10px 0;border-bottom:var(--border-w) solid var(--line)}
.sh-prose .sh-prose-byline{font-family:var(--font-body);font-size:var(--text-sm);color:var(--ink-faint);margin-top:2.4em;display:flex;align-items:center;gap:12px}`);
  return /*#__PURE__*/React.createElement("div", {
    className: 'sh-prose ' + className,
    lang: lang,
    style: style
  }, html ? /*#__PURE__*/React.createElement("div", {
    dangerouslySetInnerHTML: {
      __html: html
    }
  }) : children, byline && /*#__PURE__*/React.createElement("div", {
    className: "sh-prose-byline"
  }, /*#__PURE__*/React.createElement("span", {
    className: "seal seal-line"
  }, byline)));
}
Object.assign(__ds_scope, { Prose });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Prose.jsx", error: String((e && e.message) || e) }); }

// components/feedback/EmptyState.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function EmptyState({
  glyph = '○',
  title,
  body,
  action,
  compact = false
}) {
  css('sh-emptystate', `.sh-empty{display:grid;justify-items:center;text-align:center;gap:10px;padding:48px 24px;border:var(--border-w) dashed var(--line-strong);border-radius:var(--radius-md);font-family:var(--font-body);background:color-mix(in srgb,var(--surface-veil) 40%,transparent)}
.sh-empty[data-compact=true]{padding:28px 20px}
.sh-empty .sh-em-glyph{font-family:var(--font-display);font-size:30px;line-height:1;color:var(--ink-faint)}
.sh-empty .sh-em-title{font-family:var(--font-display);font-size:var(--text-h3);font-weight:600;color:var(--ink);margin:0}
.sh-empty .sh-em-body{font-size:var(--text-sm);color:var(--ink-soft);margin:0;max-width:44ch}
.sh-empty .sh-em-action{margin-top:8px}`);
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-empty",
    "data-compact": compact
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-em-glyph",
    "aria-hidden": "true"
  }, glyph), /*#__PURE__*/React.createElement("h3", {
    className: "sh-em-title"
  }, title), body && /*#__PURE__*/React.createElement("p", {
    className: "sh-em-body"
  }, body), action && /*#__PURE__*/React.createElement("div", {
    className: "sh-em-action"
  }, action));
}
Object.assign(__ds_scope, { EmptyState });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/EmptyState.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Modal.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  variant = 'panel',
  labelledBy
}) {
  css('sh-modal', `.sh-modal-ov{position:fixed;inset:0;z-index:80;display:grid;place-items:center;padding:24px;background:color-mix(in srgb,var(--surface-inset) 55%,transparent);backdrop-filter:var(--blur-veil);-webkit-backdrop-filter:var(--blur-veil);animation:sh-fade var(--dur-2) var(--ease-out)}
.sh-modal{background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-lg);box-shadow:var(--shadow-3);width:min(560px,100%);max-height:min(84vh,720px);display:flex;flex-direction:column;overflow:hidden;animation:sh-rise var(--dur-2) var(--ease-out);font-family:var(--font-body)}
.sh-modal[data-variant=lightbox]{width:auto;max-width:min(920px,100%);background:var(--surface-inset)}
.sh-modal .sh-mo-head{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 22px;border-bottom:var(--border-w) solid var(--line)}
.sh-modal[data-variant=lightbox] .sh-mo-head{border:0;position:absolute;inset:0 0 auto;z-index:2;background:linear-gradient(color-mix(in srgb,var(--surface-inset) 70%,transparent),transparent);padding:14px 18px}
.sh-modal .sh-mo-title{font-family:var(--font-display);font-size:var(--text-h3);font-weight:600;color:var(--ink);margin:0}
.sh-modal .sh-mo-x{appearance:none;border:var(--border-w) solid var(--line);background:var(--surface-card);color:var(--ink-soft);cursor:pointer;width:32px;height:32px;border-radius:var(--radius-full);display:grid;place-items:center;font-size:13px;flex:none;transition:color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out)}
.sh-modal .sh-mo-x:hover{color:var(--ink);border-color:var(--line-strong)}
.sh-modal .sh-mo-body{padding:20px 22px;overflow:auto}
.sh-modal[data-variant=lightbox] .sh-mo-body{padding:0;display:grid;place-items:center}
.sh-modal .sh-mo-foot{display:flex;justify-content:flex-end;gap:10px;padding:14px 22px;border-top:var(--border-w) solid var(--line);background:var(--surface-page)}
@keyframes sh-fade{from{opacity:0}}@keyframes sh-rise{from{opacity:0;transform:translateY(10px)}}`);
  React.useEffect(() => {
    if (!open) return;
    const h = e => {
      if (e.key === 'Escape') onClose && onClose();
    };
    document.addEventListener('keydown', h);
    return () => document.removeEventListener('keydown', h);
  }, [open, onClose]);
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-modal-ov",
    onMouseDown: e => {
      if (e.target === e.currentTarget && onClose) onClose();
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "sh-modal",
    "data-variant": variant,
    role: "dialog",
    "aria-modal": "true",
    "aria-labelledby": labelledBy,
    "aria-label": typeof title === 'string' ? title : undefined
  }, /*#__PURE__*/React.createElement("div", {
    className: "sh-mo-head"
  }, title ? /*#__PURE__*/React.createElement("h2", {
    className: "sh-mo-title"
  }, title) : /*#__PURE__*/React.createElement("span", null), /*#__PURE__*/React.createElement("button", {
    className: "sh-mo-x",
    type: "button",
    "aria-label": "Close",
    onClick: onClose
  }, "\u2715")), /*#__PURE__*/React.createElement("div", {
    className: "sh-mo-body"
  }, children), footer && /*#__PURE__*/React.createElement("div", {
    className: "sh-mo-foot"
  }, footer)));
}
Object.assign(__ds_scope, { Modal });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Modal.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Skeleton.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Skeleton({
  variant = 'line',
  width,
  height,
  lines = 1,
  style
}) {
  css('sh-skeleton', `.sh-skel{display:block;background:var(--surface-veil);border-radius:4px;animation:sh-skel-pulse 1.6s var(--ease-in-out) infinite}
.sh-skel[data-variant=rect]{border-radius:var(--radius-md)}
.sh-skel[data-variant=circle]{border-radius:999px}
.sh-skel-group{display:grid;gap:8px}
@keyframes sh-skel-pulse{0%,100%{opacity:1}50%{opacity:.55}}`);
  if (variant === 'text' && lines > 1) {
    return /*#__PURE__*/React.createElement("span", {
      className: "sh-skel-group",
      "aria-hidden": "true",
      style: style
    }, Array.from({
      length: lines
    }).map((_, i) => /*#__PURE__*/React.createElement("span", {
      key: i,
      className: "sh-skel",
      "data-variant": "line",
      style: {
        height: height || 12,
        width: i === lines - 1 ? '62%' : width || '100%'
      }
    })));
  }
  const dim = variant === 'circle' ? {
    width: width || 40,
    height: width || 40
  } : {
    width: width || (variant === 'rect' ? '100%' : '100%'),
    height: height || (variant === 'rect' ? 96 : 12)
  };
  return /*#__PURE__*/React.createElement("span", {
    className: "sh-skel",
    "data-variant": variant,
    "aria-hidden": "true",
    style: {
      ...dim,
      ...style
    }
  });
}
Object.assign(__ds_scope, { Skeleton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Skeleton.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Toast.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
const GLYPH = {
  info: '☾',
  success: '✓',
  error: '✕'
};
function Toast({
  tone = 'info',
  title,
  body,
  action,
  onDismiss
}) {
  css('sh-toast', `.sh-toast{display:flex;gap:12px;align-items:flex-start;width:min(380px,90vw);background:var(--surface-card);border:var(--border-w) solid var(--line);border-left:3px solid var(--accent);border-radius:var(--radius-md);box-shadow:var(--shadow-3);padding:14px 16px;font-family:var(--font-body);animation:sh-toast-in var(--dur-2) var(--ease-out)}
.sh-toast[data-tone=success]{border-left-color:var(--accent)}
.sh-toast[data-tone=error]{border-left-color:var(--live)}
.sh-toast .sh-to-glyph{font-family:var(--font-display);font-size:15px;color:var(--accent);flex:none;line-height:1.4}
.sh-toast[data-tone=error] .sh-to-glyph{color:var(--live)}
.sh-toast .sh-to-main{display:grid;gap:3px;flex:1;min-width:0}
.sh-toast .sh-to-title{font-size:var(--text-sm);font-weight:600;color:var(--ink);margin:0}
.sh-toast .sh-to-body{font-size:var(--text-xs);color:var(--ink-soft);margin:0}
.sh-toast .sh-to-action{margin-top:6px}
.sh-toast .sh-to-x{appearance:none;border:0;background:transparent;color:var(--ink-faint);cursor:pointer;font-size:13px;line-height:1;padding:4px;border-radius:var(--radius-sm);flex:none;transition:color var(--dur-1) var(--ease-out)}
.sh-toast .sh-to-x:hover{color:var(--ink)}
@keyframes sh-toast-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}`);
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-toast",
    "data-tone": tone,
    role: tone === 'error' ? 'alert' : 'status'
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-to-glyph",
    "aria-hidden": "true"
  }, GLYPH[tone] || GLYPH.info), /*#__PURE__*/React.createElement("div", {
    className: "sh-to-main"
  }, /*#__PURE__*/React.createElement("p", {
    className: "sh-to-title"
  }, title), body && /*#__PURE__*/React.createElement("p", {
    className: "sh-to-body"
  }, body), action && /*#__PURE__*/React.createElement("div", {
    className: "sh-to-action"
  }, action)), onDismiss && /*#__PURE__*/React.createElement("button", {
    className: "sh-to-x",
    type: "button",
    "aria-label": "Dismiss",
    onClick: onDismiss
  }, "\u2715"));
}
Object.assign(__ds_scope, { Toast });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Toast.jsx", error: String((e && e.message) || e) }); }

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
function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  href,
  type = 'button',
  onClick,
  iconLeft,
  iconRight,
  children,
  ...rest
}) {
  css('sh-button', `.sh-btn{--_bg:var(--accent);--_fg:var(--on-accent);--_bd:transparent;appearance:none;display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:var(--font-body);font-weight:600;border-radius:var(--radius-sm);border:var(--border-w) solid var(--_bd);background:var(--_bg);color:var(--_fg);cursor:pointer;text-decoration:none;line-height:1;white-space:nowrap;transition:background var(--dur-1) var(--ease-out),color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out);position:relative}
.sh-btn[data-size=sm]{font-size:var(--text-xs);padding:8px 14px;min-height:32px}.sh-btn[data-size=md]{font-size:var(--text-sm);padding:10px 18px;min-height:40px}.sh-btn[data-size=lg]{font-size:var(--text-body);padding:13px 24px;min-height:48px}
.sh-btn:hover{--_bg:var(--accent-hover)}.sh-btn:active{transform:translateY(1px)}
.sh-btn[data-variant=secondary]{--_bg:transparent;--_fg:var(--accent);--_bd:color-mix(in srgb,var(--accent) 55%,transparent)}.sh-btn[data-variant=secondary]:hover{--_bg:var(--accent-wash);--_fg:var(--accent-hover);--_bd:var(--accent-hover)}
.sh-btn[data-variant=ghost]{--_bg:transparent;--_fg:var(--accent);--_bd:transparent}.sh-btn[data-variant=ghost]:hover{--_bg:var(--surface-veil);--_fg:var(--accent-hover)}
.sh-btn[data-variant=live]{--_bg:var(--live);--_fg:var(--surface-card)}
.sh-btn[disabled],.sh-btn[data-disabled=true]{opacity:.45;cursor:not-allowed;pointer-events:none}
.sh-btn[data-loading=true]{color:transparent}.sh-btn[data-loading=true]>*{visibility:hidden}.sh-btn[data-loading=true]::after{content:"";visibility:visible;position:absolute;inset:0;margin:auto;width:14px;height:14px;border-radius:99px;border:2px solid color-mix(in srgb,var(--_fg) 30%,transparent);border-top-color:var(--_fg);animation:sh-spin .7s linear infinite}
.sh-btn[data-variant=secondary][data-loading=true]::after,.sh-btn[data-variant=ghost][data-loading=true]::after{border-color:color-mix(in srgb,var(--accent) 30%,transparent);border-top-color:var(--accent)}
@keyframes sh-spin{to{transform:rotate(360deg)}}`);
  const Tag = href && !disabled ? 'a' : 'button';
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: "sh-btn",
    "data-variant": variant,
    "data-size": size,
    "data-loading": loading || undefined,
    "data-disabled": disabled || undefined,
    href: href,
    type: Tag === 'button' ? type : undefined,
    disabled: Tag === 'button' ? disabled || loading : undefined,
    "aria-busy": loading || undefined,
    onClick: onClick
  }, rest), iconLeft, /*#__PURE__*/React.createElement("span", null, children), iconRight);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Button.jsx", error: String((e && e.message) || e) }); }

// components/forms/ConsentCheckbox.jsx
try { (() => {
const {
  useId
} = React;
function ConsentCheckbox({
  label,
  explanation,
  basis,
  required,
  error,
  checked,
  onChange,
  name,
  meta
}) {
  const id = useId();
  const descId = explanation ? id + '-d' : undefined;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '22px 1fr',
      gap: '4px 12px',
      padding: '14px 16px',
      borderRadius: 'var(--radius-md)',
      border: '1px solid ' + (error ? 'var(--live)' : 'var(--line)'),
      background: 'var(--surface-card)'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    id: id,
    name: name,
    checked: checked,
    onChange: onChange,
    "aria-describedby": descId,
    "aria-invalid": error ? true : undefined,
    style: {
      width: 18,
      height: 18,
      margin: '2px 0 0',
      accentColor: 'var(--accent)',
      cursor: 'pointer'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6,
      minWidth: 0
    }
  }, basis && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-micro) var(--font-mono)',
      letterSpacing: 'var(--tracking-caps)',
      textTransform: 'uppercase',
      color: required ? 'var(--ink-faint)' : 'var(--rose)'
    }
  }, basis, required ? ' · required' : ' · optional'), /*#__PURE__*/React.createElement("label", {
    htmlFor: id,
    style: {
      font: '400 var(--text-body)/1.5 var(--font-body)',
      color: 'var(--ink)',
      cursor: 'pointer'
    }
  }, label), explanation && /*#__PURE__*/React.createElement("p", {
    id: descId,
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '62ch'
    }
  }, explanation), meta && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, meta), error && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-sm) var(--font-body)',
      color: 'var(--live)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, "\u2715 "), error)));
}
Object.assign(__ds_scope, { ConsentCheckbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/ConsentCheckbox.jsx", error: String((e && e.message) || e) }); }

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
const fieldCss = `.sh-field{display:grid;gap:6px;font-family:var(--font-body);max-width:var(--measure-ui)}
.sh-field .sh-f-label{font-size:var(--text-sm);font-weight:600;color:var(--ink);display:flex;gap:6px;align-items:baseline}
.sh-field .sh-f-req{color:var(--rose)}
.sh-field .sh-f-optional{font-weight:400;font-size:var(--text-xs);color:var(--ink-faint)}
.sh-field .sh-f-ctrl{appearance:none;width:100%;box-sizing:border-box;font:inherit;font-size:var(--text-body);color:var(--ink);background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-sm);padding:10px 12px;min-height:44px;transition:border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-field .sh-f-ctrl::placeholder{color:var(--ink-faint)}
.sh-field .sh-f-ctrl:hover{border-color:var(--line-strong)}
.sh-field .sh-f-ctrl:focus-visible{outline:2px solid var(--focus-ring);outline-offset:1px;border-color:var(--accent)}
.sh-field[data-invalid=true] .sh-f-ctrl{border-color:var(--live);background:color-mix(in srgb,var(--live-wash) 55%,var(--surface-card))}
.sh-field[data-disabled=true]{opacity:.55}.sh-field[data-disabled=true] .sh-f-ctrl{background:var(--surface-inset);cursor:not-allowed}
.sh-field .sh-f-hint{font-size:var(--text-xs);color:var(--ink-faint)}
.sh-field .sh-f-error{font-size:var(--text-xs);color:var(--live);display:flex;gap:6px;align-items:baseline}
.sh-field .sh-f-error::before{content:"✕";font-size:.9em}
.sh-field .sh-f-ok{font-size:var(--text-xs);color:var(--accent);display:flex;gap:6px;align-items:baseline}.sh-field .sh-f-ok::before{content:"✓"}`;
let uid = 0;
function TextField({
  label,
  hint,
  error,
  success,
  required,
  optionalLabel,
  disabled,
  id,
  type = 'text',
  ...rest
}) {
  css('sh-field', fieldCss);
  const fid = id || 'sh-tf-' + ++uid;
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-field",
    "data-invalid": !!error,
    "data-disabled": !!disabled
  }, /*#__PURE__*/React.createElement("label", {
    className: "sh-f-label",
    htmlFor: fid
  }, label, required && /*#__PURE__*/React.createElement("span", {
    className: "sh-f-req",
    "aria-hidden": "true"
  }, "*"), !required && optionalLabel && /*#__PURE__*/React.createElement("span", {
    className: "sh-f-optional"
  }, "optional")), /*#__PURE__*/React.createElement("input", _extends({
    className: "sh-f-ctrl",
    id: fid,
    type: type,
    required: required,
    disabled: disabled,
    "aria-invalid": !!error,
    "aria-describedby": error ? fid + '-err' : hint ? fid + '-hint' : undefined
  }, rest)), error ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-error",
    id: fid + '-err',
    role: "alert"
  }, error) : success ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-ok"
  }, success) : hint ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-hint",
    id: fid + '-hint'
  }, hint) : null);
}
Object.assign(__ds_scope, { fieldCss, TextField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/TextField.jsx", error: String((e && e.message) || e) }); }

// components/forms/SelectField.jsx
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
let uid = 0;
function SelectField({
  label,
  hint,
  error,
  required,
  disabled,
  id,
  options = [],
  placeholder,
  value,
  onChange,
  ...rest
}) {
  css('sh-field', __ds_scope.fieldCss);
  css('sh-select', '.sh-f-selwrap{position:relative}.sh-f-selwrap select.sh-f-ctrl{padding-right:34px;cursor:pointer}.sh-f-selwrap::after{content:"▾";position:absolute;right:12px;top:50%;transform:translateY(-50%);color:var(--ink-faint);pointer-events:none;font-size:12px}');
  const fid = id || 'sh-sel-' + ++uid;
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-field",
    "data-invalid": !!error,
    "data-disabled": !!disabled
  }, /*#__PURE__*/React.createElement("label", {
    className: "sh-f-label",
    htmlFor: fid
  }, label, required && /*#__PURE__*/React.createElement("span", {
    className: "sh-f-req",
    "aria-hidden": "true"
  }, "*")), /*#__PURE__*/React.createElement("span", {
    className: "sh-f-selwrap"
  }, /*#__PURE__*/React.createElement("select", _extends({
    className: "sh-f-ctrl",
    id: fid,
    required: required,
    disabled: disabled,
    value: value,
    onChange: onChange,
    "aria-invalid": !!error,
    "aria-describedby": error ? fid + '-err' : hint ? fid + '-hint' : undefined
  }, rest), placeholder && /*#__PURE__*/React.createElement("option", {
    value: "",
    disabled: true
  }, placeholder), options.map(o => typeof o === 'string' ? /*#__PURE__*/React.createElement("option", {
    key: o,
    value: o
  }, o) : /*#__PURE__*/React.createElement("option", {
    key: o.value,
    value: o.value
  }, o.label)))), error ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-error",
    id: fid + '-err',
    role: "alert"
  }, error) : hint ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-hint",
    id: fid + '-hint'
  }, hint) : null);
}
Object.assign(__ds_scope, { SelectField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/SelectField.jsx", error: String((e && e.message) || e) }); }

// components/forms/TextArea.jsx
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
let uid = 0;
function TextArea({
  label,
  hint,
  error,
  success,
  required,
  optionalLabel,
  disabled,
  id,
  rows = 5,
  maxLength,
  value,
  ...rest
}) {
  css('sh-field', __ds_scope.fieldCss);
  css('sh-textarea', '.sh-field textarea.sh-f-ctrl{resize:vertical;min-height:110px;line-height:var(--leading-body)}.sh-f-count{font-family:var(--font-mono);font-size:10.5px;color:var(--ink-faint);justify-self:end;font-variant-numeric:tabular-nums}');
  const fid = id || 'sh-ta-' + ++uid;
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-field",
    "data-invalid": !!error,
    "data-disabled": !!disabled
  }, /*#__PURE__*/React.createElement("label", {
    className: "sh-f-label",
    htmlFor: fid
  }, label, required && /*#__PURE__*/React.createElement("span", {
    className: "sh-f-req",
    "aria-hidden": "true"
  }, "*"), !required && optionalLabel && /*#__PURE__*/React.createElement("span", {
    className: "sh-f-optional"
  }, "optional")), /*#__PURE__*/React.createElement("textarea", _extends({
    className: "sh-f-ctrl",
    id: fid,
    rows: rows,
    required: required,
    disabled: disabled,
    maxLength: maxLength,
    value: value,
    "aria-invalid": !!error,
    "aria-describedby": error ? fid + '-err' : hint ? fid + '-hint' : undefined
  }, rest)), error ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-error",
    id: fid + '-err',
    role: "alert"
  }, error) : success ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-ok"
  }, success) : hint ? /*#__PURE__*/React.createElement("span", {
    className: "sh-f-hint",
    id: fid + '-hint'
  }, hint) : null, maxLength && typeof value === 'string' && /*#__PURE__*/React.createElement("span", {
    className: "sh-f-count"
  }, value.length, " / ", maxLength));
}
Object.assign(__ds_scope, { TextArea });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/TextArea.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Badge.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Badge({
  tone = 'neutral',
  dot = false,
  children
}) {
  css('sh-badge', `.sh-badge{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:.06em;text-transform:uppercase;border-radius:var(--radius-full);padding:3px 9px;border:var(--border-w) solid;line-height:1.4}
.sh-badge i{width:6px;height:6px;border-radius:99px;background:currentColor}
.sh-badge[data-tone=neutral]{color:var(--ink-soft);border-color:var(--line);background:var(--surface-veil)}
.sh-badge[data-tone=accent]{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent);background:var(--accent-wash)}
.sh-badge[data-tone=rose]{color:var(--rose);border-color:color-mix(in srgb,var(--rose) 45%,transparent);background:var(--rose-wash)}
.sh-badge[data-tone=live]{color:var(--live);border-color:color-mix(in srgb,var(--live) 45%,transparent);background:var(--live-wash)}
.sh-badge[data-tone=faint]{color:var(--ink-faint);border-color:var(--line);background:transparent}`);
  return /*#__PURE__*/React.createElement("span", {
    className: "sh-badge",
    "data-tone": tone
  }, dot && /*#__PURE__*/React.createElement("i", {
    "aria-hidden": "true"
  }), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Badge.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Breadcrumb.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Breadcrumb({
  items = []
}) {
  css('sh-breadcrumb', `.sh-bc{font-family:var(--font-body);font-size:var(--text-xs)}
.sh-bc ol{display:flex;flex-wrap:wrap;align-items:center;gap:8px;list-style:none;margin:0;padding:0}
.sh-bc li{display:inline-flex;align-items:center;gap:8px}
.sh-bc li+li::before{content:"›";color:var(--ink-faint)}
.sh-bc a{color:var(--ink-faint);text-decoration:none;transition:color var(--dur-1) var(--ease-out)}
.sh-bc a:hover{color:var(--accent-hover);text-decoration:underline}
.sh-bc [aria-current=page]{color:var(--ink-soft);font-weight:500}`);
  return /*#__PURE__*/React.createElement("nav", {
    className: "sh-bc",
    "aria-label": "Breadcrumb"
  }, /*#__PURE__*/React.createElement("ol", null, items.map((it, i) => /*#__PURE__*/React.createElement("li", {
    key: i
  }, i === items.length - 1 ? /*#__PURE__*/React.createElement("span", {
    "aria-current": "page"
  }, it.label) : /*#__PURE__*/React.createElement("a", {
    href: it.href
  }, it.label)))));
}
Object.assign(__ds_scope, { Breadcrumb });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Breadcrumb.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Pagination.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function pages(cur, total) {
  if (total <= 7) return Array.from({
    length: total
  }, (_, i) => i + 1);
  const set = new Set([1, total, cur - 1, cur, cur + 1]);
  const arr = [...set].filter(p => p >= 1 && p <= total).sort((a, b) => a - b);
  const out = [];
  let prev = 0;
  for (const p of arr) {
    if (p - prev > 1) out.push('…');
    out.push(p);
    prev = p;
  }
  return out;
}
function Pagination({
  page,
  pageCount,
  onChange,
  hrefFor,
  label = 'Pagination'
}) {
  css('sh-pagination', `.sh-pag{display:flex;align-items:center;gap:4px;font-family:var(--font-body)}
.sh-pag [data-p]{appearance:none;border:var(--border-w) solid transparent;background:transparent;min-width:36px;height:36px;padding:0 8px;border-radius:var(--radius-sm);font-size:var(--text-sm);font-variant-numeric:tabular-nums;color:var(--ink-soft);cursor:pointer;display:inline-grid;place-items:center;text-decoration:none;line-height:1;transition:color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-pag [data-p]:hover{color:var(--ink);border-color:var(--line-strong)}
.sh-pag [data-p]:active{transform:translateY(1px)}
.sh-pag [data-p][aria-current=page]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 50%,transparent);color:var(--accent);font-weight:600}
.sh-pag [data-p][aria-disabled=true]{opacity:.4;pointer-events:none}
.sh-pag .sh-pag-gap{color:var(--ink-faint);min-width:24px;text-align:center}`);
  const go = p => e => {
    if (!hrefFor) {
      e.preventDefault();
      onChange && onChange(p);
    }
  };
  const Item = ({
    p,
    children,
    disabled,
    current,
    aria
  }) => {
    const Tg = hrefFor ? 'a' : 'button';
    return /*#__PURE__*/React.createElement(Tg, {
      "data-p": true,
      href: hrefFor ? hrefFor(p) : undefined,
      type: hrefFor ? undefined : 'button',
      onClick: go(p),
      "aria-current": current ? 'page' : undefined,
      "aria-disabled": disabled || undefined,
      "aria-label": aria
    }, children);
  };
  return /*#__PURE__*/React.createElement("nav", {
    className: "sh-pag",
    "aria-label": label
  }, /*#__PURE__*/React.createElement(Item, {
    p: page - 1,
    disabled: page <= 1,
    aria: "Previous page"
  }, "\u2190"), pages(page, pageCount).map((p, i) => p === '…' ? /*#__PURE__*/React.createElement("span", {
    key: 'g' + i,
    className: "sh-pag-gap",
    "aria-hidden": "true"
  }, "\u2026") : /*#__PURE__*/React.createElement(Item, {
    key: p,
    p: p,
    current: p === page
  }, p)), /*#__PURE__*/React.createElement(Item, {
    p: page + 1,
    disabled: page >= pageCount,
    aria: "Next page"
  }, "\u2192"));
}
Object.assign(__ds_scope, { Pagination });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Pagination.jsx", error: String((e && e.message) || e) }); }

// components/navigation/PeriodSwitcher.jsx
try { (() => {
const PERIODS = [{
  key: 'daily',
  name: 'Daily'
}, {
  key: 'monthly',
  name: 'Monthly'
}, {
  key: 'seasonal',
  name: 'Seasonal'
}, {
  key: 'yearly',
  name: 'Yearly'
}];
function PeriodSwitcher({
  current,
  available = ['monthly'],
  onChange,
  hrefFor,
  label
}) {
  const shown = PERIODS.filter(p => available.indexOf(p.key) >= 0);
  // A single available period still renders — the switcher is the layout, not the choice.
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 'var(--space-3)',
      flexWrap: 'wrap',
      paddingBottom: 'var(--space-3)',
      borderBottom: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    role: "group",
    "aria-label": "Reading period",
    style: {
      display: 'flex',
      gap: 'var(--space-1)'
    }
  }, shown.map(p => {
    const on = current === p.key;
    const style = {
      padding: '7px 13px',
      minHeight: 36,
      borderRadius: 'var(--radius-sm)',
      border: '1px solid ' + (on ? 'var(--line-strong)' : 'transparent'),
      background: on ? 'var(--surface-card)' : 'transparent',
      color: on ? 'var(--ink)' : 'var(--ink-soft)',
      font: (on ? '600' : '500') + ' var(--text-sm) var(--font-body)',
      textDecoration: 'none',
      cursor: 'pointer'
    };
    return hrefFor ? /*#__PURE__*/React.createElement("a", {
      key: p.key,
      href: hrefFor(p.key),
      "aria-current": on ? 'page' : undefined,
      style: style
    }, p.name) : /*#__PURE__*/React.createElement("button", {
      key: p.key,
      type: "button",
      "aria-pressed": on,
      onClick: () => onChange && onChange(p.key),
      style: style
    }, p.name);
  })), label && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      marginLeft: 'auto',
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, label));
}
Object.assign(__ds_scope, { PeriodSwitcher });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/PeriodSwitcher.jsx", error: String((e && e.message) || e) }); }

// components/navigation/SignPicker.jsx
try { (() => {
const SIGNS = [{
  key: 'aries',
  name: 'Aries',
  glyph: '♈︎',
  dates: '21 Mar – 19 Apr'
}, {
  key: 'taurus',
  name: 'Taurus',
  glyph: '♉︎',
  dates: '20 Apr – 20 May'
}, {
  key: 'gemini',
  name: 'Gemini',
  glyph: '♊︎',
  dates: '21 May – 20 Jun'
}, {
  key: 'cancer',
  name: 'Cancer',
  glyph: '♋︎',
  dates: '21 Jun – 22 Jul'
}, {
  key: 'leo',
  name: 'Leo',
  glyph: '♌︎',
  dates: '23 Jul – 22 Aug'
}, {
  key: 'virgo',
  name: 'Virgo',
  glyph: '♍︎',
  dates: '23 Aug – 22 Sep'
}, {
  key: 'libra',
  name: 'Libra',
  glyph: '♎︎',
  dates: '23 Sep – 22 Oct'
}, {
  key: 'scorpio',
  name: 'Scorpio',
  glyph: '♏︎',
  dates: '23 Oct – 21 Nov'
}, {
  key: 'sagittarius',
  name: 'Sagittarius',
  glyph: '♐︎',
  dates: '22 Nov – 21 Dec'
}, {
  key: 'capricorn',
  name: 'Capricorn',
  glyph: '♑︎',
  dates: '22 Dec – 19 Jan'
}, {
  key: 'aquarius',
  name: 'Aquarius',
  glyph: '♒︎',
  dates: '20 Jan – 18 Feb'
}, {
  key: 'pisces',
  name: 'Pisces',
  glyph: '♓︎',
  dates: '19 Feb – 20 Mar'
}];
function SignPicker({
  current,
  onChange,
  hrefFor,
  ownSign,
  layout = 'grid'
}) {
  const row = layout === 'row';
  const wrap = row ? {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 'var(--space-2)'
  } : {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill,minmax(150px,1fr))',
    gap: 'var(--space-3)'
  };
  return /*#__PURE__*/React.createElement("div", {
    role: "group",
    "aria-label": "Choose a sign",
    style: wrap
  }, SIGNS.map(s => {
    const on = current === s.key;
    const mine = ownSign === s.key;
    const style = row ? {
      display: 'inline-flex',
      alignItems: 'baseline',
      gap: 6,
      padding: '7px 12px',
      border: '1px solid ' + (on ? 'var(--accent)' : 'var(--line)'),
      background: on ? 'var(--accent-wash)' : 'transparent',
      color: on ? 'var(--accent)' : 'var(--ink-soft)',
      borderRadius: 'var(--radius-full)',
      font: '500 var(--text-sm) var(--font-body)',
      textDecoration: 'none',
      cursor: 'pointer',
      minHeight: 36
    } : {
      display: 'grid',
      gap: 2,
      padding: '14px 16px',
      textAlign: 'left',
      border: '1px solid ' + (on ? 'var(--accent)' : 'var(--line)'),
      background: on ? 'var(--accent-wash)' : 'var(--surface-card)',
      borderRadius: 'var(--radius-md)',
      boxShadow: on ? 'none' : 'var(--shadow-1)',
      textDecoration: 'none',
      cursor: 'pointer',
      minHeight: 44,
      transition: 'border-color var(--dur-1) var(--ease-out)'
    };
    const inner = row ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      className: "t-glyph",
      style: {
        font: '400 15px var(--font-display)',
        color: on ? 'var(--accent)' : 'var(--rose)'
      }
    }, s.glyph), /*#__PURE__*/React.createElement("span", null, s.name), mine && /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        font: '600 9px var(--font-mono)',
        letterSpacing: '.08em',
        color: 'var(--rose)'
      }
    }, "YOURS")) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("span", {
      style: {
        display: 'flex',
        alignItems: 'baseline',
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      className: "t-glyph",
      style: {
        font: '400 1.5rem var(--font-display)',
        lineHeight: 1,
        color: 'var(--rose)'
      }
    }, s.glyph), /*#__PURE__*/React.createElement("span", {
      style: {
        font: '600 var(--text-h4) var(--font-display)',
        color: on ? 'var(--accent)' : 'var(--ink)'
      }
    }, s.name), mine && /*#__PURE__*/React.createElement("span", {
      style: {
        marginLeft: 'auto',
        font: '600 9px var(--font-mono)',
        letterSpacing: '.08em',
        color: 'var(--rose)'
      }
    }, "YOURS")), /*#__PURE__*/React.createElement("span", {
      className: "t-tabular",
      style: {
        font: '400 var(--text-xs) var(--font-mono)',
        color: 'var(--ink-faint)'
      }
    }, s.dates));
    const aria = mine ? s.name + ' — your sign' : s.name;
    return hrefFor ? /*#__PURE__*/React.createElement("a", {
      key: s.key,
      href: hrefFor(s.key),
      "aria-current": on ? 'page' : undefined,
      "aria-label": aria,
      style: style
    }, inner) : /*#__PURE__*/React.createElement("button", {
      key: s.key,
      type: "button",
      "aria-pressed": on,
      "aria-label": aria,
      onClick: () => onChange && onChange(s.key),
      style: style
    }, inner);
  }));
}
Object.assign(__ds_scope, { SIGNS, SignPicker });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/SignPicker.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tag.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function Tag({
  label,
  href,
  active = false,
  count,
  onClick
}) {
  css('sh-tag', `.sh-tagc{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-body);font-size:var(--text-xs);font-weight:500;color:var(--ink-soft);background:var(--surface-veil);border:var(--border-w) solid transparent;border-radius:var(--radius-full);padding:5px 12px;text-decoration:none;cursor:pointer;line-height:1;transition:color var(--dur-1) var(--ease-out),border-color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-tagc:hover{color:var(--accent-hover);border-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.sh-tagc:active{transform:translateY(1px)}
.sh-tagc[data-active=true]{background:var(--accent-wash);border-color:color-mix(in srgb,var(--accent) 50%,transparent);color:var(--accent)}
.sh-tagc .sh-tag-n{font-family:var(--font-mono);font-size:10px;color:var(--ink-faint);font-variant-numeric:tabular-nums}`);
  const Tg = href ? 'a' : 'button';
  return /*#__PURE__*/React.createElement(Tg, {
    className: "sh-tagc",
    "data-active": active,
    href: href,
    type: href ? undefined : 'button',
    onClick: onClick,
    "aria-pressed": href ? undefined : active || undefined
  }, label, count != null && /*#__PURE__*/React.createElement("span", {
    className: "sh-tag-n"
  }, count));
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tag.jsx", error: String((e && e.message) || e) }); }

// components/tables/CreditList.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function CreditList({
  credits = [],
  dense = false
}) {
  css('sh-creditlist', `.sh-credits{display:grid;padding:0;margin:0;list-style:none}
.sh-credits li{display:grid;grid-template-columns:140px 1fr;gap:16px;align-items:baseline;padding:14px 0;border-bottom:var(--border-w) solid var(--line)}
.sh-credits[data-dense=true] li{padding:8px 0}
.sh-credits .sh-cr-role{font-family:var(--font-body);font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint)}
.sh-credits .sh-cr-name{font-family:var(--font-display);font-size:var(--text-h4);color:var(--ink)}
.sh-credits .sh-cr-name a{color:inherit;text-decoration-color:color-mix(in srgb,var(--accent) 40%,transparent)}
.sh-credits .sh-cr-name a:hover{color:var(--accent-hover)}
.sh-credits .sh-cr-note{font-family:var(--font-body);font-size:var(--text-xs);color:var(--ink-faint);margin-left:10px}
@media (max-width:480px){.sh-credits li{grid-template-columns:1fr;gap:2px}}`);
  return /*#__PURE__*/React.createElement("ul", {
    className: "sh-credits",
    "data-dense": dense
  }, credits.map((c, i) => /*#__PURE__*/React.createElement("li", {
    key: i
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-cr-role"
  }, c.role), /*#__PURE__*/React.createElement("span", {
    className: "sh-cr-name"
  }, c.href ? /*#__PURE__*/React.createElement("a", {
    href: c.href
  }, c.name) : c.name, c.note && /*#__PURE__*/React.createElement("span", {
    className: "sh-cr-note"
  }, c.note)))));
}
Object.assign(__ds_scope, { CreditList });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/CreditList.jsx", error: String((e && e.message) || e) }); }

// components/tables/ExportBlock.jsx
try { (() => {
function ExportBlock({
  feedHref,
  fileHref,
  fileName = 'stations.ics',
  fileScope,
  googleLinks = [],
  meta,
  onCopyFeed,
  copyLabel = 'Copy feed URL'
}) {
  const secondary = {
    display: 'inline-flex',
    alignItems: 'center',
    minHeight: 40,
    padding: '0 14px',
    font: '600 var(--text-sm) var(--font-body)',
    color: 'var(--ink)',
    textDecoration: 'none',
    background: 'transparent',
    border: '1px solid var(--line-strong)',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer'
  };
  return /*#__PURE__*/React.createElement("section", {
    className: "export-block",
    style: {
      display: 'grid',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("p", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Take it with you"), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line-strong)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      padding: 'var(--space-4)',
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: '600 var(--text-h4) var(--font-display)',
      color: 'var(--ink)'
    }
  }, "Subscribe to the feed"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 .625rem var(--font-mono)',
      letterSpacing: 'var(--tracking-caps)',
      textTransform: 'uppercase',
      color: 'var(--rose)'
    }
  }, "stays correct \xB7 notifies")), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '58ch'
    }
  }, "Your calendar re-reads this as the year turns, so the times keep matching the sky and your reminders keep arriving. This is the one that becomes a habit."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-2)',
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: feedHref,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      minHeight: 44,
      padding: '0 18px',
      font: '600 var(--text-sm) var(--font-body)',
      color: 'var(--on-accent)',
      textDecoration: 'none',
      background: 'var(--accent)',
      border: '1px solid var(--accent)',
      borderRadius: 'var(--radius-sm)'
    }
  }, "Subscribe in my calendar"), /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onCopyFeed,
    style: secondary
  }, copyLabel)), /*#__PURE__*/React.createElement("code", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)',
      wordBreak: 'break-all'
    }
  }, feedHref), meta && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, meta)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)',
      gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8,
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: '600 var(--text-body) var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Download a snapshot"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, "A fixed ", /*#__PURE__*/React.createElement("code", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)'
    }
  }, ".ics"), " file of the range shown. It does not update \u2014 ", /*#__PURE__*/React.createElement("strong", {
    style: {
      fontWeight: 600,
      color: 'var(--ink)'
    }
  }, "it will go stale"), ", so take it only if you want exactly these dates and nothing more."), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("a", {
    href: fileHref,
    download: fileName,
    style: secondary
  }, "Download .ics")), fileScope && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, fileScope)), googleLinks.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8,
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: '600 var(--text-body) var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Add one station to Google"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, "A single event for a single station, if you only keep one of the four."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-2)',
      flexWrap: 'wrap'
    }
  }, googleLinks.map(g => /*#__PURE__*/React.createElement("a", {
    key: g.label,
    href: g.href,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      minHeight: 36,
      padding: '0 12px',
      font: '500 var(--text-sm) var(--font-body)',
      color: 'var(--accent)',
      textDecoration: 'none',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-full)'
    }
  }, g.glyph && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      color: 'var(--rose)'
    }
  }, g.glyph), g.label))))));
}
Object.assign(__ds_scope, { ExportBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/ExportBlock.jsx", error: String((e && e.message) || e) }); }

// components/tables/NextStation.jsx
try { (() => {
function NextStation({
  name,
  glyph,
  at,
  inLabel,
  currentName,
  currentSince,
  attribution,
  progress = 0,
  size = 'hero',
  undefinedReason
}) {
  const hero = size === 'hero';
  if (undefinedReason) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-md)',
        background: 'var(--surface-card)',
        padding: hero ? 'var(--space-5)' : 'var(--space-4)',
        display: 'grid',
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      className: "t-eyebrow",
      style: {
        margin: 0,
        color: 'var(--rose)'
      }
    }, "\u25CB No station to count to"), /*#__PURE__*/React.createElement("p", {
      style: {
        margin: 0,
        font: '400 var(--text-sm)/1.6 var(--font-body)',
        color: 'var(--ink-soft)',
        maxWidth: '48ch'
      }
    }, undefinedReason));
  }
  return /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      background: 'var(--surface-card)',
      boxShadow: 'var(--shadow-1)',
      padding: hero ? 'var(--space-5)' : 'var(--space-4)',
      display: 'grid',
      gap: hero ? 14 : 10
    }
  }, currentName && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 8,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Now"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-sm) var(--font-body)',
      color: 'var(--ink)'
    }
  }, currentName), currentSince && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "since ", currentSince)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: hero ? 14 : 10,
      flexWrap: 'wrap'
    }
  }, glyph && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: `400 ${hero ? '2.25rem' : '1.5rem'} var(--font-display)`,
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, glyph), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 2,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: `600 ${hero ? 'var(--text-h3)' : 'var(--text-body)'} var(--font-display)`,
      color: 'var(--ink)'
    }
  }, name), attribution && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-body)',
      color: 'var(--rose)'
    }
  }, attribution)), /*#__PURE__*/React.createElement("div", {
    style: {
      marginLeft: 'auto',
      textAlign: 'right',
      display: 'grid',
      gap: 2
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: `500 ${hero ? 'clamp(1.75rem,5vw,2.5rem)' : '1.375rem'} var(--font-mono)`,
      lineHeight: 1,
      color: 'var(--ink)'
    }
  }, "in ", inLabel), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-soft)'
    }
  }, "at ", at, " your time"))), /*#__PURE__*/React.createElement("div", {
    "aria-hidden": "true",
    style: {
      height: 2,
      background: 'var(--line)',
      borderRadius: 2,
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: Math.max(0, Math.min(1, progress)) * 100 + '%',
      height: '100%',
      background: 'var(--rose)',
      transition: 'width var(--dur-2) var(--ease-out)'
    }
  })));
}
Object.assign(__ds_scope, { NextStation });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/NextStation.jsx", error: String((e && e.message) || e) }); }

// components/tables/ProfileFieldTable.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function ProfileFieldTable({
  fields = [],
  columns = 2
}) {
  css('sh-profiletable', `.sh-pft{display:grid;gap:0 40px;font-family:var(--font-body)}
.sh-pft[data-cols="2"]{grid-template-columns:1fr 1fr}
.sh-pft .sh-pft-row{display:flex;align-items:baseline;gap:10px;padding:10px 0;border-bottom:var(--border-w) solid var(--line)}
.sh-pft .sh-pft-label{font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint);flex:none}
.sh-pft .sh-pft-dots{flex:1;border-bottom:1px dotted var(--line-strong);transform:translateY(-4px);min-width:24px}
.sh-pft .sh-pft-value{font-family:var(--font-display);font-size:var(--text-h4);color:var(--ink);text-align:right}
@media (max-width:560px){.sh-pft[data-cols="2"]{grid-template-columns:1fr}}`);
  return /*#__PURE__*/React.createElement("dl", {
    className: "sh-pft",
    "data-cols": columns
  }, fields.map((f, i) => /*#__PURE__*/React.createElement("div", {
    className: "sh-pft-row",
    key: i
  }, /*#__PURE__*/React.createElement("dt", {
    className: "sh-pft-label"
  }, f.label), /*#__PURE__*/React.createElement("span", {
    className: "sh-pft-dots",
    "aria-hidden": "true"
  }), /*#__PURE__*/React.createElement("dd", {
    className: "sh-pft-value",
    style: {
      margin: 0
    }
  }, f.value))));
}
Object.assign(__ds_scope, { ProfileFieldTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/ProfileFieldTable.jsx", error: String((e && e.message) || e) }); }

// components/tables/ScheduleItem.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
const fmt = (d, tz, opts) => new Intl.DateTimeFormat('en-GB', {
  ...opts,
  timeZone: tz
}).format(d);
function ScheduleItem({
  title,
  startISO,
  durationMin,
  topic,
  status = 'upcoming',
  tz = 'local',
  href
}) {
  css('sh-scheditem', `.sh-sched{display:grid;grid-template-columns:64px 1fr auto;gap:18px;align-items:center;padding:16px 18px;background:var(--surface-card);border:var(--border-w) solid var(--line);border-radius:var(--radius-md);font-family:var(--font-body);text-decoration:none;color:inherit;transition:border-color var(--dur-1) var(--ease-out),box-shadow var(--dur-1) var(--ease-out)}
a.sh-sched:hover{border-color:var(--line-strong);box-shadow:var(--shadow-2)}
.sh-sched[data-status=live]{border-color:color-mix(in srgb,var(--live) 40%,transparent);background:color-mix(in srgb,var(--live-wash) 40%,var(--surface-card))}
.sh-sched[data-status=past]{opacity:.6}
.sh-sched .sh-sc-date{display:grid;justify-items:center;gap:2px;border-right:var(--border-w) solid var(--line);padding-right:16px}
.sh-sched .sh-sc-dow{font-size:var(--text-micro);font-weight:600;letter-spacing:var(--tracking-eyebrow);text-transform:uppercase;color:var(--ink-faint)}
.sh-sched .sh-sc-day{font-family:var(--font-display);font-size:28px;font-weight:600;color:var(--ink);line-height:1;font-variant-numeric:tabular-nums}
.sh-sched .sh-sc-main{display:grid;gap:4px;min-width:0}
.sh-sched .sh-sc-title{font-family:var(--font-display);font-size:var(--text-h4);font-weight:600;color:var(--ink);margin:0}
.sh-sched .sh-sc-topic{font-size:var(--text-xs);color:var(--ink-faint)}
.sh-sched .sh-sc-time{display:grid;gap:3px;justify-items:end;text-align:right}
.sh-sched .sh-sc-t1{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:var(--text-sm);color:var(--ink)}
.sh-sched .sh-sc-t2{font-family:var(--font-mono);font-variant-numeric:tabular-nums;font-size:10.5px;color:var(--ink-faint)}
.sh-sched .sh-sc-live{font-size:var(--text-micro);font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--live)}
@media (max-width:560px){.sh-sched{grid-template-columns:56px 1fr}.sh-sched .sh-sc-time{grid-column:2;justify-items:start;text-align:left}}`);
  const d = new Date(startISO);
  const localTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const primTz = tz === 'athens' ? 'Europe/Athens' : localTz;
  const secTz = tz === 'athens' ? localTz : 'Europe/Athens';
  const t = z => fmt(d, z, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
  const Tag = href ? 'a' : 'article';
  return /*#__PURE__*/React.createElement(Tag, {
    className: "sh-sched",
    "data-status": status,
    href: href
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-date"
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-dow"
  }, fmt(d, primTz, {
    weekday: 'short'
  })), /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-day"
  }, fmt(d, primTz, {
    day: '2-digit'
  })), /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-dow",
    style: {
      letterSpacing: '.06em'
    }
  }, fmt(d, primTz, {
    month: 'short'
  }))), /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-main"
  }, status === 'live' && /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-live"
  }, "\u25CF Live now"), /*#__PURE__*/React.createElement("h3", {
    className: "sh-sc-title"
  }, title), topic && /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-topic"
  }, topic, durationMin ? ` · ~${Math.round(durationMin / 60 * 10) / 10}h` : '')), /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-time"
  }, /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-t1"
  }, t(primTz), " ", tz === 'athens' ? 'Athens' : 'your time'), /*#__PURE__*/React.createElement("span", {
    className: "sh-sc-t2"
  }, t(secTz), " ", tz === 'athens' ? 'your time' : 'Athens')));
}
Object.assign(__ds_scope, { ScheduleItem });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/ScheduleItem.jsx", error: String((e && e.message) || e) }); }

// components/tables/StationTable.jsx
try { (() => {
function StationTable({
  stations,
  glyphs = [],
  attributions = [],
  rows,
  absentLabel = 'none today',
  undefinedReason,
  caption
}) {
  if (undefinedReason) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        background: 'var(--surface-card)',
        border: '1px solid var(--line)',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-1)',
        padding: 'clamp(28px,5vw,44px) clamp(20px,4vw,32px)'
      }
    }, /*#__PURE__*/React.createElement("p", {
      className: "t-eyebrow",
      style: {
        margin: '0 0 10px',
        color: 'var(--rose)'
      }
    }, "\u25CB Cannot be reckoned"), /*#__PURE__*/React.createElement("div", {
      style: {
        font: '400 1.0625rem/1.7 var(--font-display)',
        color: 'var(--ink)',
        maxWidth: '52ch'
      }
    }, undefinedReason));
  }
  const hasPhase = rows.some(r => r.phase);
  const cell = {
    padding: '10px 8px',
    borderBottom: '1px solid var(--line)',
    textAlign: 'right'
  };
  const head = {
    padding: '0 8px 8px',
    borderBottom: '1px solid var(--line-strong)',
    textAlign: 'right',
    font: '600 var(--text-micro) var(--font-body)',
    letterSpacing: 'var(--tracking-eyebrow)',
    textTransform: 'uppercase',
    color: 'var(--ink-faint)',
    verticalAlign: 'bottom'
  };
  return /*#__PURE__*/React.createElement("div", {
    className: "station-table",
    style: {
      overflowX: 'auto'
    }
  }, /*#__PURE__*/React.createElement("table", {
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      minWidth: 460
    }
  }, caption && /*#__PURE__*/React.createElement("caption", {
    style: {
      captionSide: 'top',
      textAlign: 'left',
      paddingBottom: 12,
      font: '400 var(--text-xs)/1.6 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, caption), /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: {
      ...head,
      textAlign: 'left'
    }
  }, "Day"), stations.map((s, i) => /*#__PURE__*/React.createElement("th", {
    key: s,
    scope: "col",
    style: head
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      gap: 3,
      justifyItems: 'end'
    }
  }, glyphs[i] && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 1.0625rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)',
      letterSpacing: 0
    }
  }, glyphs[i]), /*#__PURE__*/React.createElement("span", null, s), attributions[i] && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-micro) var(--font-body)',
      letterSpacing: 0,
      textTransform: 'none',
      color: 'var(--rose)'
    }
  }, attributions[i])))), hasPhase && /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: head
  }, "Moon"))), /*#__PURE__*/React.createElement("tbody", null, rows.map(r => /*#__PURE__*/React.createElement("tr", {
    key: r.date,
    className: "station-row",
    style: r.today ? {
      background: 'var(--accent-wash)'
    } : undefined
  }, /*#__PURE__*/React.createElement("th", {
    scope: "row",
    style: {
      ...cell,
      textAlign: 'left',
      font: (r.today ? '600' : '400') + ' var(--text-sm) var(--font-body)',
      color: 'var(--ink)',
      whiteSpace: 'nowrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-tabular"
  }, r.date), r.weekday && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, " ", r.weekday), r.today && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 .625rem var(--font-mono)',
      letterSpacing: 'var(--tracking-caps)',
      textTransform: 'uppercase',
      color: 'var(--accent)'
    }
  }, " today")), r.times.map((t, i) => {
    const isNow = r.today && r.currentIndex === i;
    return /*#__PURE__*/React.createElement("td", {
      key: i,
      className: "t-tabular",
      style: {
        ...cell,
        /* Times are the reason the table exists: mono, tabular, and large enough to read
           on a phone at dawn in poor light. */
        font: (isNow ? '600' : '400') + ' 1.0625rem var(--font-mono)',
        color: t === null ? 'var(--ink-faint)' : 'var(--ink)',
        whiteSpace: 'nowrap'
      }
    }, t === null ? /*#__PURE__*/React.createElement("span", {
      style: {
        font: '400 var(--text-xs) var(--font-body)',
        fontStyle: 'italic'
      }
    }, absentLabel) : t, isNow && /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        color: 'var(--accent)'
      }
    }, " \xB7"));
  }), hasPhase && /*#__PURE__*/React.createElement("td", {
    className: "t-tabular",
    style: {
      ...cell,
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      whiteSpace: 'nowrap'
    }
  }, r.phase || ''))))));
}
Object.assign(__ds_scope, { StationTable });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/StationTable.jsx", error: String((e && e.message) || e) }); }

// components/tables/TimezoneToggle.jsx
try { (() => {
function css(id, txt) {
  if (typeof document !== 'undefined' && !document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = txt;
    document.head.appendChild(s);
  }
}
function TimezoneToggle({
  value = 'local',
  onChange
}) {
  css('sh-tztoggle', `.sh-tz{display:inline-flex;border:var(--border-w) solid var(--line);border-radius:var(--radius-full);padding:2px;background:var(--surface-card);gap:2px;font-family:var(--font-body)}
.sh-tz button{appearance:none;border:0;background:transparent;font-size:var(--text-xs);font-weight:600;color:var(--ink-faint);padding:6px 12px;border-radius:var(--radius-full);cursor:pointer;line-height:1;display:inline-flex;gap:6px;align-items:center;transition:color var(--dur-1) var(--ease-out),background var(--dur-1) var(--ease-out)}
.sh-tz button:hover{color:var(--ink)}
.sh-tz button[aria-pressed=true]{background:var(--surface-veil);color:var(--ink)}
.sh-tz .sh-tz-zone{font-family:var(--font-mono);font-weight:400;font-size:10px;color:var(--ink-faint)}`);
  const local = Intl.DateTimeFormat().resolvedOptions().timeZone.split('/').pop().replace('_', ' ');
  return /*#__PURE__*/React.createElement("div", {
    className: "sh-tz",
    role: "group",
    "aria-label": "Timezone"
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": value === 'local',
    onClick: () => onChange && onChange('local')
  }, "Your time ", /*#__PURE__*/React.createElement("span", {
    className: "sh-tz-zone"
  }, local)), /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": value === 'athens',
    onClick: () => onChange && onChange('athens')
  }, "Athens ", /*#__PURE__*/React.createElement("span", {
    className: "sh-tz-zone"
  }, "GMT+3")));
}
Object.assign(__ds_scope, { TimezoneToggle });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/tables/TimezoneToggle.jsx", error: String((e && e.message) || e) }); }

// tailwind.preset.js
try { (() => {
/** Shruti — Tailwind v3 preset. Wire into tailwind.config.js: `presets: [require('./tailwind.preset')]`.
 * Colours reference the CSS custom properties from tokens/colors.css, so the
 * three theme states (light / dark / system) keep working without `dark:` variants. */
const shrutiPreset = {
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        page: 'var(--surface-page)',
        card: 'var(--surface-card)',
        veil: 'var(--surface-veil)',
        inset: 'var(--surface-inset)',
        ink: {
          DEFAULT: 'var(--ink)',
          soft: 'var(--ink-soft)',
          faint: 'var(--ink-faint)'
        },
        line: {
          DEFAULT: 'var(--line)',
          strong: 'var(--line-strong)'
        },
        accent: {
          DEFAULT: 'var(--accent)',
          hover: 'var(--accent-hover)',
          wash: 'var(--accent-wash)',
          on: 'var(--on-accent)'
        },
        rose: {
          DEFAULT: 'var(--rose)',
          hover: 'var(--rose-hover)',
          wash: 'var(--rose-wash)'
        },
        live: {
          DEFAULT: 'var(--live)',
          wash: 'var(--live-wash)'
        },
        sky: {
          zenith: 'var(--sky-zenith)',
          mid: 'var(--sky-mid)',
          horizon: 'var(--sky-horizon)',
          line: 'var(--horizon-line)'
        }
      },
      fontFamily: {
        display: ['"EB Garamond"', '"Noto Serif Devanagari"', 'Georgia', 'serif'],
        body: ['Commissioner', 'Mukta', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Noto Sans Devanagari"', 'ui-monospace', 'monospace']
      },
      fontSize: {
        hero: ['var(--text-hero)', {
          lineHeight: '1.08',
          letterSpacing: '-0.01em'
        }],
        h1: ['2.25rem', {
          lineHeight: '1.2'
        }],
        h2: ['1.75rem', {
          lineHeight: '1.2'
        }],
        h3: ['1.375rem', {
          lineHeight: '1.2'
        }],
        prose: ['1.1875rem', {
          lineHeight: '1.72'
        }],
        micro: ['.75rem', {
          lineHeight: '1',
          letterSpacing: '.14em'
        }]
      },
      spacing: {
        1: '4px',
        2: '8px',
        3: '12px',
        4: '16px',
        5: '24px',
        6: '32px',
        7: '48px',
        8: '64px',
        9: '96px'
      },
      borderRadius: {
        sm: '4px',
        md: '10px',
        lg: '16px',
        full: '999px'
      },
      boxShadow: {
        1: 'var(--shadow-1)',
        2: 'var(--shadow-2)',
        3: 'var(--shadow-3)'
      },
      transitionTimingFunction: {
        out: 'cubic-bezier(.2,.7,.3,1)',
        'in-out': 'cubic-bezier(.45,0,.25,1)'
      },
      transitionDuration: {
        1: '120ms',
        2: '240ms',
        3: '600ms'
      },
      maxWidth: {
        page: '1120px',
        prose: '66ch'
      },
      backgroundImage: {
        sky: 'linear-gradient(180deg,var(--sky-zenith) 0%,var(--sky-mid) 58%,var(--sky-horizon) 100%)'
      }
    }
  }
};
if (typeof module !== "undefined" && module.exports) module.exports = shrutiPreset;else if (typeof window !== "undefined") window.shrutiTailwindPreset = shrutiPreset;
})(); } catch (e) { __ds_ns.__errors.push({ path: "tailwind.preset.js", error: String((e && e.message) || e) }); }

// ui_kits/signs.js
try { (() => {
// Shared sign data for pages that need it outside the component bundle.
// Loaded as a plain global script by ui_kits/site/index.html and ui_kits/admin/index.html.
window.SHRUTI_SIGNS = [{
  key: 'aries',
  name: 'Aries',
  glyph: '♈︎',
  dates: '21 Mar – 19 Apr'
}, {
  key: 'taurus',
  name: 'Taurus',
  glyph: '♉︎',
  dates: '20 Apr – 20 May'
}, {
  key: 'gemini',
  name: 'Gemini',
  glyph: '♊︎',
  dates: '21 May – 20 Jun'
}, {
  key: 'cancer',
  name: 'Cancer',
  glyph: '♋︎',
  dates: '21 Jun – 22 Jul'
}, {
  key: 'leo',
  name: 'Leo',
  glyph: '♌︎',
  dates: '23 Jul – 22 Aug'
}, {
  key: 'virgo',
  name: 'Virgo',
  glyph: '♍︎',
  dates: '23 Aug – 22 Sep'
}, {
  key: 'libra',
  name: 'Libra',
  glyph: '♎︎',
  dates: '23 Sep – 22 Oct'
}, {
  key: 'scorpio',
  name: 'Scorpio',
  glyph: '♏︎',
  dates: '23 Oct – 21 Nov'
}, {
  key: 'sagittarius',
  name: 'Sagittarius',
  glyph: '♐︎',
  dates: '22 Nov – 21 Dec'
}, {
  key: 'capricorn',
  name: 'Capricorn',
  glyph: '♑︎',
  dates: '22 Dec – 19 Jan'
}, {
  key: 'aquarius',
  name: 'Aquarius',
  glyph: '♒︎',
  dates: '20 Jan – 18 Feb'
}, {
  key: 'pisces',
  name: 'Pisces',
  glyph: '♓︎',
  dates: '19 Feb – 20 Mar'
}];
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/signs.js", error: String((e && e.message) || e) }); }

// ui_kits/site/About.jsx
try { (() => {
const {
  SectionHeader,
  ProfileFieldTable,
  CreditList,
  FanArtCard,
  Prose,
  Badge
} = window.ShrutiDesignSystem_cb687f;
function AboutScreen() {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263E",
    eyebrow: "About",
    title: "Shruti",
    body: "VTuber \xB7 theurgist \xB7 toolmaker. Athens, GMT+3."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1.4fr 1fr',
      gap: 'var(--space-7)',
      alignItems: 'start'
    },
    className: "about-cols"
  }, /*#__PURE__*/React.createElement(Prose, null, /*#__PURE__*/React.createElement("p", null, "I stream the building of software for magickal and astrological practice \u2014 not a variety stream with an occult skin, but the actual work: ephemeris math, calendar systems, divination engines, and the unglamorous plumbing that makes a grimoire searchable."), /*#__PURE__*/React.createElement("p", null, "Three initiatory lineages, held at once: Hellenic theurgy under Hekate and the Attic lunisolar calendar; \u015A\u0101kta Tantra, initiated into the Mah\u0101vidy\u0101 \u2014 tarpa\u1E47am and mantra japa; and Thelema, under the O.T.O. They are not an aesthetic blend. They converge on one thing, and the software is built around it: the twilight junctures, ", /*#__PURE__*/React.createElement("em", {
    lang: "sa"
  }, "sandhy\u0101"), " \u2014 dawn and dusk."), /*#__PURE__*/React.createElement("p", {
    lang: "el"
  }, "\u039C\u03B9\u03BB\u03AC\u03C9 \u03B1\u03B3\u03B3\u03BB\u03B9\u03BA\u03AC \u03BA\u03B1\u03B9 \u03B5\u03BB\u03BB\u03B7\u03BD\u03B9\u03BA\u03AC \u03C3\u03C4\u03B1 streams\xB7 \u03C4\u03B1 \u03C3\u03C7\u03CC\u03BB\u03B9\u03B1 \u03C3\u03C4\u03BF\u03BD \u03BA\u03CE\u03B4\u03B9\u03BA\u03B1 \u03B5\u03AF\u03BD\u03B1\u03B9 \u03B4\u03AF\u03B3\u03BB\u03C9\u03C3\u03C3\u03B1 \u03BA\u03B9 \u03B1\u03C5\u03C4\u03AC."), /*#__PURE__*/React.createElement("hr", null), /*#__PURE__*/React.createElement("h3", null, "The two names"), /*#__PURE__*/React.createElement("p", null, /*#__PURE__*/React.createElement("strong", null, "Shruti"), " \u2014 Shruti Swara \u2014 is my real name, and the name everything public lives under. I am part Indian and part Greek: the Sanskrit name and the Greek theurgy are not two themes in tension \u2014 they are one person. \u0936\u094D\u0930\u0941\u0924\u093F, ", /*#__PURE__*/React.createElement("em", null, "\u201Cthat which is heard\u201D"), "."), /*#__PURE__*/React.createElement("p", null, /*#__PURE__*/React.createElement("span", {
    className: "seal"
  }, "Soror Eu.\u200AA."), " is a magickal motto, and it signs the magickal work: journal entries about practice, and the software written as practice. Two instruments, the same hand \u2014 you will find it on bylines and nowhere else.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '600 var(--text-micro) var(--font-body)',
      letterSpacing: 'var(--tracking-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-faint)',
      margin: '0 0 10px'
    }
  }, "Profile"), /*#__PURE__*/React.createElement(ProfileFieldTable, {
    columns: 1,
    fields: [{
      label: 'Birthday',
      value: '21 June'
    }, {
      label: 'Height',
      value: '163 cm'
    }, {
      label: 'Debut',
      value: '14 Jan 2024'
    }, {
      label: 'Fan name',
      value: 'Shrutinauts'
    }, {
      label: 'Traditions',
      value: 'Hellenic · Śākta · Thelemic'
    }, {
      label: 'Oshi mark',
      value: '— (to be chosen)'
    }, {
      label: 'Stream tag',
      value: '#ShrutiLive'
    }, {
      label: 'Fan-art tag',
      value: '#ShrutiArt'
    }]
  })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '600 var(--text-micro) var(--font-body)',
      letterSpacing: 'var(--tracking-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-faint)',
      margin: '0 0 4px'
    }
  }, "Credits"), /*#__PURE__*/React.createElement(CreditList, {
    dense: true,
    credits: [{
      role: 'Illustrator',
      name: '—',
      note: 'commission in progress'
    }, {
      role: 'Rigger',
      name: '—',
      note: 'commission in progress'
    }, {
      role: '3D model',
      name: '—',
      note: 'planned'
    }, {
      role: 'Logo',
      name: 'Studio ——',
      href: '#'
    }, {
      role: 'BGM',
      name: '——',
      href: '#'
    }]
  })))), /*#__PURE__*/React.createElement("section", {
    className: "section",
    style: {
      marginTop: 'var(--space-7)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    glyph: "\u2736",
    eyebrow: "Costumes",
    title: "Outfits",
    body: "Art arrives incrementally \u2014 empty slots are part of the design."
  }), /*#__PURE__*/React.createElement(Badge, {
    tone: "rose"
  }, "3 commissions open")), /*#__PURE__*/React.createElement("div", {
    className: "grid-3"
  }, /*#__PURE__*/React.createElement(FanArtCard, {
    image: null,
    artist: "base model",
    platform: "in progress"
  }), /*#__PURE__*/React.createElement(FanArtCard, {
    image: null,
    artist: "festival outfit",
    platform: "planned"
  }), /*#__PURE__*/React.createElement(FanArtCard, {
    image: null,
    artist: "dev-stream hoodie",
    platform: "planned"
  }))));
}
Object.assign(window, {
  AboutScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/About.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Account.jsx
try { (() => {
const {
  SectionHeader,
  TextField,
  SelectField,
  Button,
  ConsentCheckbox,
  Badge,
  Modal,
  Toast,
  EmptyState,
  ProfileFieldTable
} = window.ShrutiDesignSystem_cb687f;
function NativityForm({
  onSaved
}) {
  const [f, setF] = React.useState({
    date: '1996-06-21',
    time: '04:12',
    place: 'Athens, GR'
  });
  const [unknown, setUnknown] = React.useState(false);
  const [resolved, setResolved] = React.useState({
    name: 'Athens, Attica, Greece',
    lat: '37.9838°N',
    lon: '23.7275°E',
    tz: 'Europe/Athens · EEST (GMT+3)'
  });
  const set = k => e => setF(s => ({
    ...s,
    [k]: e.target.value
  }));
  return /*#__PURE__*/React.createElement("form", {
    onSubmit: e => {
      e.preventDefault();
      onSaved && onSaved();
    },
    style: {
      display: 'grid',
      gap: 'var(--space-5)',
      maxWidth: 620
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(TextField, {
    label: "Birth date",
    type: "date",
    required: true,
    value: f.date,
    onChange: set('date')
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Birth time",
    type: "time",
    optionalLabel: true,
    disabled: unknown,
    value: unknown ? '' : f.time,
    onChange: set('time'),
    hint: unknown ? 'Left out — see below.' : 'Local clock time at the place of birth.'
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-4)',
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'grid',
      gridTemplateColumns: '20px 1fr',
      gap: '2px 10px',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: unknown,
    onChange: e => setUnknown(e.target.checked),
    style: {
      width: 17,
      height: 17,
      margin: '2px 0 0',
      accentColor: 'var(--accent)',
      cursor: 'pointer'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-body)/1.5 var(--font-body)',
      color: 'var(--ink)'
    }
  }, "I don\u2019t know my birth time")), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '62ch'
    }
  }, "That is a perfectly ordinary answer, and it is not an error. Here is what it costs: the ascendant moves a degree every four minutes, so without a time the ", /*#__PURE__*/React.createElement("strong", {
    style: {
      fontWeight: 600,
      color: 'var(--ink)'
    }
  }, "ascendant, midheaven, houses and sect are undefined"), ". Planets stay where they were, give or take the Moon, which can cross half a sign in a day."), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "You still get: sign positions, aspects, your horoscope sign. You do not get: houses, angles, sect, anything timed to the ascendant.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(TextField, {
    label: "Birth place",
    required: true,
    value: f.place,
    onChange: set('place'),
    hint: "Search a town or city \u2014 this resolves to coordinates and the timezone that applied on that date."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-inset)',
      borderRadius: 'var(--radius-sm)',
      padding: 'var(--space-3) var(--space-4)',
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Resolved to"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-sm) var(--font-body)',
      color: 'var(--ink)'
    }
  }, resolved.name), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-soft)'
    }
  }, resolved.lat, " ", resolved.lon, " \xB7 ", resolved.tz), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-body)',
      color: 'var(--ink-faint)'
    }
  }, "Check this. A chart cast for the wrong city is indistinguishable from a right one. ", /*#__PURE__*/React.createElement("a", {
    href: "#nativity",
    style: {
      color: 'var(--accent)'
    }
  }, "Not this place?")))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(SelectField, {
    label: "Preferred tradition",
    options: [{
      value: 'hel',
      label: 'Hellenistic'
    }, {
      value: 'ved',
      label: 'Vedic'
    }],
    defaultValue: "hel"
  }), /*#__PURE__*/React.createElement(SelectField, {
    label: "House system",
    options: ['Whole sign', 'Placidus', 'Equal', 'Porphyry', 'Regiomontanus', 'Campanus'],
    defaultValue: "Whole sign"
  }), /*#__PURE__*/React.createElement(SelectField, {
    label: "Ayan\u0101\u1E41\u015Ba",
    hint: "Used when you read sidereally.",
    options: ['Lahiri · Chitrapakṣa', 'B. V. Raman', 'Krishnamurti', 'Fagan–Bradley', 'Yukteshwar', 'True Citrā'],
    defaultValue: "Lahiri \xB7 Chitrapak\u1E63a"
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      maxWidth: '70ch'
    }
  }, "This is everything the ephemeris needs and nothing more. No address, no phone number, no gender field \u2014 the calculation does not use them, so they are not asked for."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    type: "submit"
  }, "Save nativity"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#account"
  }, "Cancel")));
}
function AccountScreen({
  tab,
  go
}) {
  const [toast, setToast] = React.useState(null);
  const [confirmDelete, setConfirmDelete] = React.useState(false);
  const [c, setC] = React.useState({
    birth: true,
    letter: true
  });
  const T = [['profile', 'Profile'], ['nativity', 'Nativity'], ['consents', 'Consents & data']];
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263E",
    eyebrow: "Your account",
    title: "Settings",
    body: "Small on purpose. There are no public profiles here and nothing to decorate \u2014 this holds how you read, and what you have agreed to."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap',
      paddingBottom: 'var(--space-4)',
      borderBottom: '1px solid var(--line)'
    }
  }, T.map(([k, l]) => /*#__PURE__*/React.createElement(Button, {
    key: k,
    variant: tab === k ? 'secondary' : 'ghost',
    onClick: () => go(k)
  }, l))), tab === 'profile' && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)',
      maxWidth: 620
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(TextField, {
    label: "Display name",
    defaultValue: "Ariadne",
    hint: "Only ever shown back to you."
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Email",
    type: "email",
    defaultValue: "reader@example.com"
  }), /*#__PURE__*/React.createElement(SelectField, {
    label: "Timezone",
    options: ['Europe/Athens (GMT+3)', 'Europe/London (GMT+1)', 'America/New_York (GMT−4)', 'Asia/Kolkata (GMT+5:30)'],
    defaultValue: "Europe/Athens (GMT+3)"
  }), /*#__PURE__*/React.createElement(SelectField, {
    label: "Reading language",
    options: ['English', 'Ελληνικά', 'हिन्दी', 'Français'],
    defaultValue: "English"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Button, {
    onClick: () => setToast('Profile saved.')
  }, "Save")), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '60ch'
    }
  }, "There is no profile picture, no bio, no follower count and no public page. This is not that kind of site, and adding those is scope it does not have."))), tab === 'nativity' && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, "Saved nativity"), /*#__PURE__*/React.createElement(Badge, {
    tone: "rose"
  }, "stored with your explicit consent")), /*#__PURE__*/React.createElement(NativityForm, {
    onSaved: () => setToast('Nativity saved. Your chart and horoscope now use it.')
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-4)',
      display: 'grid',
      gap: 8,
      maxWidth: 620
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "More than one"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "One saved chart is enough to begin. If you keep more later, each one is named \u2014 this slot is \u201CMine\u201D."))), tab === 'consents' && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-6)',
      maxWidth: 680
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)',
      margin: '0 0 6px'
    }
  }, "What you have agreed to"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '62ch'
    }
  }, "The same three decisions from sign-up, revisitable. Withdrawing is exactly as easy as giving \u2014 untick and save.")), /*#__PURE__*/React.createElement(ConsentCheckbox, {
    basis: "contract",
    required: true,
    checked: true,
    label: "My account exists",
    meta: "Given 12 Aug 2026",
    explanation: "Withdrawing this means deleting the account \u2014 the control for that is below."
  }), /*#__PURE__*/React.createElement(ConsentCheckbox, {
    basis: "explicit consent \xB7 GDPR Art. 9",
    checked: c.birth,
    onChange: e => setC(s => ({
      ...s,
      birth: e.target.checked
    })),
    label: "Store my birth data for astrological readings",
    meta: "Given 12 Aug 2026 \xB7 withdraw any time",
    explanation: "Untick and save, and the saved nativity is deleted with it. Your account stays; your horoscope goes back to whichever sign you pick by hand."
  }), /*#__PURE__*/React.createElement(ConsentCheckbox, {
    basis: "consent \xB7 marketing",
    checked: c.letter,
    onChange: e => setC(s => ({
      ...s,
      letter: e.target.checked
    })),
    label: "Send me the monthly letter, including offers",
    meta: "Given 12 Aug 2026 \xB7 withdraw any time",
    explanation: "Untick to come off the list entirely. To keep it but hear less, pause it instead in the letter\u2019s preference centre."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    onClick: () => setToast('Consents updated.')
  }, "Save consents"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#newsletter-preferences"
  }, "Letter preferences"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, "Your data"), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      padding: 'var(--space-4)',
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-body) var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Export everything"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '58ch'
    }
  }, "A JSON file with your profile, your saved nativity, your consent history and the dates, and which letters were sent to you. It downloads here \u2014 no email, no waiting on a request."), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: () => setToast('Export ready — check your downloads.')
  }, "Download my data"))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      padding: 'var(--space-4)',
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-body) var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Delete my account"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '58ch'
    }
  }, "Everything above goes, including the saved nativity, and your address comes off the letter list at the same time \u2014 not just the account."), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: () => setConfirmDelete(true)
  }, "Delete my account"))))), /*#__PURE__*/React.createElement(Modal, {
    open: confirmDelete,
    onClose: () => setConfirmDelete(false),
    title: "Delete your account",
    footer: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 10,
        justifyContent: 'flex-end',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      onClick: () => setConfirmDelete(false)
    }, "Keep my account"), /*#__PURE__*/React.createElement(Button, {
      variant: "live",
      onClick: () => {
        setConfirmDelete(false);
        setToast('Account deleted. The letter list has been updated too.');
      }
    }, "Delete everything"))
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 14
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-body)/1.6 var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Plainly, so there is no surprise afterwards:"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "What goes"), /*#__PURE__*/React.createElement("ul", {
    style: {
      margin: 0,
      paddingLeft: 18,
      display: 'grid',
      gap: 4,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, /*#__PURE__*/React.createElement("li", null, "Your email, display name and preferences"), /*#__PURE__*/React.createElement("li", null, "Your saved nativity \u2014 date, time, place, coordinates"), /*#__PURE__*/React.createElement("li", null, "Your subscription to the monthly letter"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "What is kept, and why"), /*#__PURE__*/React.createElement("ul", {
    style: {
      margin: 0,
      paddingLeft: 18,
      display: 'grid',
      gap: 4,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, /*#__PURE__*/React.createElement("li", null, "A record that consent was given and withdrawn, with dates and nothing else \u2014 that record is the proof the law asks for, and it holds no birth data"), /*#__PURE__*/React.createElement("li", null, "Any invoice, if you ever bought something, for as long as tax law requires"))), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "Immediate and not reversible. There is no thirty-day grace period holding your data hostage."))), toast && /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'fixed',
      right: 18,
      bottom: 70,
      zIndex: 60
    }
  }, /*#__PURE__*/React.createElement(Toast, {
    tone: "success",
    title: toast,
    onDismiss: () => setToast(null)
  })));
}
Object.assign(window, {
  AccountScreen,
  NativityForm
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Account.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/App.jsx
try { (() => {
const {
  Button,
  EmptyState
} = window.ShrutiDesignSystem_cb687f;
function NotFoundScreen() {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page",
    style: {
      minHeight: '52vh',
      display: 'grid',
      placeItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      display: 'grid',
      gap: 18,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 72px var(--font-display)',
      color: 'var(--ink)',
      lineHeight: 1
    },
    "aria-hidden": "true"
  }, "4\u25CB4"), /*#__PURE__*/React.createElement("h1", {
    style: {
      font: '600 var(--text-h2) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, "This page is in another sky."), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-body) var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '40ch'
    }
  }, "The address may have moved when the site was rebuilt \u2014 the almanac below will get you home."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Button, {
    href: "#home"
  }, "Back home"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    href: "#journal"
  }, "Read the journal"))));
}
function ServerErrorScreen({
  onHome
}) {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page",
    style: {
      minHeight: '52vh',
      display: 'grid',
      placeItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      display: 'grid',
      gap: 18,
      justifyItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 72px var(--font-display)',
      color: 'var(--ink)',
      lineHeight: 1
    },
    "aria-hidden": "true"
  }, "5\u25CB\u25CB"), /*#__PURE__*/React.createElement("h1", {
    style: {
      font: '600 var(--text-h2) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, "The instrument slipped."), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-body) var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '40ch'
    }
  }, "Something failed on my side, not yours. It's being looked at \u2014 try again in a moment."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Button, {
    href: "#home",
    onClick: onHome
  }, "Back home"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: () => location.reload()
  }, "Try again")), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "error 500 \xB7 if it persists, hello@shrutivtuber.com")));
}
function App() {
  const read = () => location.hash.replace('#', '') || 'home';
  const [route, setRoute] = React.useState(read());
  const [theme, setTheme] = React.useState('system');
  const [withArt, setWithArt] = React.useState(true);
  const [liveOn, setLiveOn] = React.useState(true);
  const [scheduleEmpty, setScheduleEmpty] = React.useState(false);
  const [tz, setTz] = React.useState('local');
  const [article, setArticle] = React.useState(false);
  const [broken, setBroken] = React.useState(false);
  const [signedIn, setSignedIn] = React.useState(false);
  const [sign, setSign] = React.useState('virgo');
  const [period, setPeriod] = React.useState('monthly');
  const [authMethod, setAuthMethod] = React.useState('link');
  const [acctTab, setAcctTab] = React.useState('profile');
  const [polar, setPolar] = React.useState(false);
  const [birthTime, setBirthTime] = React.useState(true);
  React.useEffect(() => {
    const on = () => {
      setRoute(read());
      setArticle(false);
      setBroken(false);
      window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', on);
    return () => window.removeEventListener('hashchange', on);
  }, []);
  React.useEffect(() => {
    const el = document.documentElement;
    if (theme === 'system') el.removeAttribute('data-theme');else el.setAttribute('data-theme', theme);
  }, [theme]);
  const live = liveOn ? {
    status: 'live',
    title: 'Building the sigil compiler',
    game: 'Software & Game Dev',
    viewers: 214
  } : {
    status: 'offline'
  };
  const known = ['home', 'about', 'work', 'schedule', 'videos', 'journal', 'press', 'fanworks', 'guidelines', 'contact', 'support', 'privacy', 'terms', 'signup', 'signin', 'account', 'nativity', 'horoscopes', 'horoscope', 'newsletter', 'newsletter-archive', 'newsletter-preferences', 'newsletter-confirm', 'newsletter-unsubscribed', 'today', 'solar-stations', 'lunar-stations'];
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(SiteHeader, {
    route: route,
    live: live,
    withArt: withArt,
    signedIn: signedIn
  }), broken && /*#__PURE__*/React.createElement(ServerErrorScreen, {
    onHome: () => setBroken(false)
  }), route === 'home' && !broken && /*#__PURE__*/React.createElement(HomeScreen, {
    live: live,
    withArt: withArt,
    tz: tz
  }), route === 'about' && !broken && /*#__PURE__*/React.createElement(AboutScreen, null), route === 'work' && !broken && /*#__PURE__*/React.createElement(WorkScreen, null), route === 'schedule' && !broken && /*#__PURE__*/React.createElement(ScheduleScreen, {
    tz: tz,
    setTz: setTz,
    empty: scheduleEmpty
  }), route === 'videos' && !broken && /*#__PURE__*/React.createElement(VideosScreen, {
    loading: false
  }), route === 'journal' && !broken && /*#__PURE__*/React.createElement(JournalScreen, {
    article: article,
    openArticle: setArticle
  }), route === 'press' && !broken && /*#__PURE__*/React.createElement(PressScreen, null), route === 'fanworks' && !broken && /*#__PURE__*/React.createElement(FanWorksScreen, null), route === 'guidelines' && !broken && /*#__PURE__*/React.createElement(GuidelinesScreen, null), route === 'contact' && !broken && /*#__PURE__*/React.createElement(ContactScreen, null), route === 'support' && !broken && /*#__PURE__*/React.createElement(SupportScreen, null), (route === 'privacy' || route === 'terms') && !broken && /*#__PURE__*/React.createElement(LegalScreen, {
    doc: route
  }), (route === 'signup' || route === 'signin') && !broken && /*#__PURE__*/React.createElement(AuthScreen, {
    mode: route,
    go: r => {
      location.hash = r;
    },
    method: authMethod,
    setMethod: setAuthMethod
  }), route === 'account' && !broken && /*#__PURE__*/React.createElement(AccountScreen, {
    tab: acctTab,
    go: setAcctTab
  }), route === 'nativity' && !broken && /*#__PURE__*/React.createElement(AccountScreen, {
    tab: "nativity",
    go: setAcctTab
  }), route === 'horoscopes' && !broken && /*#__PURE__*/React.createElement(HoroscopeIndex, {
    sign: sign,
    setSign: s => {
      setSign(s);
      location.hash = 'horoscope';
    },
    ownSign: signedIn ? 'virgo' : null,
    signedIn: signedIn
  }), route === 'horoscope' && !broken && /*#__PURE__*/React.createElement(HoroscopeReading, {
    sign: sign,
    setSign: setSign,
    period: period,
    setPeriod: setPeriod,
    ownSign: signedIn ? 'virgo' : null
  }), route === 'newsletter' && !broken && /*#__PURE__*/React.createElement(NewsletterScreen, {
    view: "subscribe"
  }), route === 'newsletter-archive' && !broken && /*#__PURE__*/React.createElement(NewsletterScreen, {
    view: "archive"
  }), route === 'newsletter-preferences' && !broken && /*#__PURE__*/React.createElement(NewsletterScreen, {
    view: "preferences"
  }), route === 'newsletter-confirm' && !broken && /*#__PURE__*/React.createElement(NewsletterScreen, {
    view: "confirm"
  }), route === 'newsletter-unsubscribed' && !broken && /*#__PURE__*/React.createElement(NewsletterScreen, {
    view: "unsubscribed"
  }), route === 'today' && !broken && /*#__PURE__*/React.createElement(TodayScreen, {
    signedIn: signedIn,
    birthTime: birthTime,
    polar: polar
  }), route === 'solar-stations' && !broken && /*#__PURE__*/React.createElement(StationsScreen, {
    kind: "solar",
    polar: polar
  }), route === 'lunar-stations' && !broken && /*#__PURE__*/React.createElement(StationsScreen, {
    kind: "lunar",
    polar: polar
  }), !known.includes(route) && !broken && /*#__PURE__*/React.createElement(NotFoundScreen, null), /*#__PURE__*/React.createElement(SiteFooter, null), /*#__PURE__*/React.createElement("div", {
    className: "demo-bar",
    role: "group",
    "aria-label": "Demo controls (not part of the site)"
  }, /*#__PURE__*/React.createElement("span", {
    className: "demo-lbl"
  }, "demo"), /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => setTheme(t => t === 'system' ? 'light' : t === 'light' ? 'dark' : 'system')
  }, theme === 'system' ? '◐ system' : theme === 'light' ? '☀ dawn' : '☾ dusk'), /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": withArt,
    onClick: () => setWithArt(a => !a)
  }, "art ", withArt ? 'on' : 'off'), /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": liveOn,
    onClick: () => setLiveOn(l => !l)
  }, liveOn ? 'live' : 'offline'), route === 'schedule' && /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": scheduleEmpty,
    onClick: () => setScheduleEmpty(e => !e)
  }, "empty"), /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": signedIn,
    onClick: () => setSignedIn(s => !s)
  }, signedIn ? 'signed in' : 'signed out'), (route === 'today' || route === 'solar-stations' || route === 'lunar-stations') && /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": polar,
    onClick: () => setPolar(p => !p)
  }, polar ? 'polar' : 'athens'), route === 'today' && signedIn && /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": !birthTime,
    onClick: () => setBirthTime(b => !b)
  }, birthTime ? 'has birth time' : 'no birth time'), /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => {
      setBroken(false);
      location.hash = 'nowhere';
    }
  }, "404"), /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-pressed": broken,
    onClick: () => setBroken(b => !b)
  }, "500")));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(App, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Auth.jsx
try { (() => {
const {
  SectionHeader,
  TextField,
  Button,
  ConsentCheckbox,
  EmptyState,
  Badge
} = window.ShrutiDesignSystem_cb687f;
function AuthScreen({
  mode,
  go,
  method,
  setMethod
}) {
  const signUp = mode === 'signup';
  const [f, setF] = React.useState({
    email: '',
    pw: '',
    name: ''
  });
  const [c, setC] = React.useState({
    account: false,
    birth: false,
    letter: false
  });
  const [err, setErr] = React.useState({});
  const [sent, setSent] = React.useState(false);
  const set = k => e => {
    const v = e.target.value;
    setF(s => ({
      ...s,
      [k]: v
    }));
    setErr(s => ({
      ...s,
      [k]: undefined
    }));
  };
  const flip = k => e => {
    const v = e.target.checked;
    setC(s => ({
      ...s,
      [k]: v
    }));
    setErr(s => ({
      ...s,
      [k]: undefined
    }));
  };
  const submit = e => {
    e.preventDefault();
    const n = {};
    if (!/^\S+@\S+\.\S+$/.test(f.email)) n.email = 'That address doesn\u2019t look complete.';
    if (method === 'password' && f.pw.length < 10) n.pw = 'Ten characters or more, please — a phrase beats a password.';
    if (signUp && !c.account) n.account = 'This one is needed to make an account at all.';
    setErr(n);
    if (Object.keys(n).length === 0) setSent(true);
  };
  if (sent && method === 'link') return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25D0",
    title: "Check your email",
    body: `A sign-in link is on its way to ${f.email}. It expires in fifteen minutes, and it only works once. If it hasn't arrived in a minute, look in spam — the address it comes from is new.`,
    action: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 10,
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      onClick: () => setSent(false)
    }, "Use a different address"), /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      onClick: () => setSent(false)
    }, "Send it again"))
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: 0,
      textAlign: 'center'
    }
  }, "Opened the link on your phone but signed up on a laptop? Either works \u2014 the link signs in the device that opens it."));
  if (sent) return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u263E",
    title: signUp ? 'Account made' : 'Signed in',
    body: signUp ? 'Your consents are recorded and revisitable in settings. Next: a saved nativity, if you want your own chart and your own horoscope — it is optional and you can add it later.' : 'Welcome back.',
    action: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 10,
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(Button, {
      href: "#nativity"
    }, "Add my nativity"), /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      href: "#horoscopes"
    }, "Read this month"))
  }));
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263E",
    eyebrow: signUp ? 'Create an account' : 'Sign in',
    title: signUp ? 'Keep your own chart' : 'Welcome back',
    body: signUp ? 'An account holds one nativity and remembers how you like it reckoned. There are no public profiles here, no followers, and nothing to decorate — you sign up once and come back to read.' : 'Email and a link, or email and a password. Whichever you set up with.'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      padding: '0 0 var(--space-4)',
      borderBottom: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: method === 'link' ? 'secondary' : 'ghost',
    onClick: () => setMethod('link')
  }, "Email me a link"), /*#__PURE__*/React.createElement(Button, {
    variant: method === 'password' ? 'secondary' : 'ghost',
    onClick: () => setMethod('password')
  }, "Use a password")), /*#__PURE__*/React.createElement("form", {
    onSubmit: submit,
    noValidate: true,
    style: {
      display: 'grid',
      gap: 'var(--space-5)',
      maxWidth: 620
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-4)',
      maxWidth: 440
    }
  }, signUp && /*#__PURE__*/React.createElement(TextField, {
    label: "Display name",
    hint: "Only ever shown back to you.",
    optionalLabel: true,
    value: f.name,
    onChange: set('name'),
    placeholder: "What should the letter call you?"
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Email",
    type: "email",
    required: true,
    value: f.email,
    onChange: set('email'),
    error: err.email,
    placeholder: "you@example.com",
    hint: method === 'link' ? 'We send a sign-in link — no password to forget.' : undefined
  }), method === 'password' && /*#__PURE__*/React.createElement(TextField, {
    label: "Password",
    type: "password",
    required: true,
    value: f.pw,
    onChange: set('pw'),
    error: err.pw,
    hint: "Ten characters or more. A phrase you can remember beats a puzzle you cannot."
  })), signUp && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)',
      margin: '0 0 6px'
    }
  }, "Three separate decisions"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '62ch'
    }
  }, "Say yes to one and no to another \u2014 that is normal here, and the first is the only one needed to have an account. This form is longer than most sign-ups on purpose.")), /*#__PURE__*/React.createElement(ConsentCheckbox, {
    basis: "contract",
    required: true,
    checked: c.account,
    onChange: flip('account'),
    error: err.account,
    label: "Create my account",
    explanation: "Your email and display name are stored so you can sign in and so the site knows what to show you. This is the account itself \u2014 without it there is nothing to sign into."
  }), /*#__PURE__*/React.createElement(ConsentCheckbox, {
    basis: "explicit consent \xB7 GDPR Art. 9",
    checked: c.birth,
    onChange: flip('birth'),
    label: "Store my birth data so my chart and horoscope can be calculated",
    explanation: "Birth date, time and place, kept on your account and used only to compute your chart and to choose your horoscope. Because a reading arguably reveals philosophical belief, this may be special category data \u2014 so it is asked for separately and never assumed. Nothing is shared, sold, or used to train anything. Withdraw it in settings and the data goes with it."
  }), /*#__PURE__*/React.createElement(ConsentCheckbox, {
    basis: "consent \xB7 marketing",
    checked: c.letter,
    onChange: flip('letter'),
    label: "Send me the monthly letter, including offers",
    explanation: "One email a month: your horoscope, what I published and streamed, and a letter written by hand. It will also carry offers for astrological courses and magickal services when those open \u2014 saying so now is fairer than saying so later. One-click unsubscribe, or pause it instead."
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: 0
    }
  }, "No box here is pre-ticked, and none of them is bundled into another. All three are revisitable in settings.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      alignItems: 'center',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    type: "submit"
  }, signUp ? 'Create account' : method === 'link' ? 'Email me a link' : 'Sign in'), /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => go(signUp ? 'signin' : 'signup'),
    style: {
      appearance: 'none',
      border: 0,
      background: 'transparent',
      font: '500 var(--text-sm) var(--font-body)',
      color: 'var(--accent)',
      cursor: 'pointer',
      textDecoration: 'underline',
      textUnderlineOffset: 3
    }
  }, signUp ? 'I already have an account' : 'I need an account'))), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-4)',
      display: 'flex',
      gap: '8px 20px',
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "faint"
  }, "no cookie banner"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "Analytics here are cookieless, so there is nothing to consent to and no banner to dismiss.")));
}
Object.assign(window, {
  AuthScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Auth.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Chrome.jsx
try { (() => {
const DS = window.ShrutiDesignSystem_cb687f;
const {
  LiveBadge,
  LanguageSwitcher,
  SocialLinkRow,
  Button,
  LegalImprint
} = DS;
const ASSETS = {
  wordmark: '../../assets/wordmark-small.png',
  wordmarkHiRes: '../../assets/wordmark.png',
  clouds: '../../assets/clouds.png',
  avatar: '../../assets/avatar.png'
};
const SOCIALS = [{
  platform: 'twitch',
  href: '#'
}, {
  platform: 'youtube',
  href: '#'
}, {
  platform: 'discord',
  href: '#'
}, {
  platform: 'x',
  href: '#'
}, {
  platform: 'github',
  href: '#'
}, {
  platform: 'linkedin',
  href: '#'
}];
const NAV = [['home', 'Home'], ['today', 'Today'], ['about', 'About'], ['work', 'Work'], ['schedule', 'Schedule'], ['videos', 'Videos'], ['horoscopes', 'Horoscopes'], ['journal', 'Journal']];
function BrandMark({
  withArt
}) {
  const [err, setErr] = React.useState(false);
  return /*#__PURE__*/React.createElement("a", {
    className: "brand",
    href: "#home",
    "aria-label": "Shruti \u2014 home"
  }, withArt && !err ? /*#__PURE__*/React.createElement("img", {
    src: ASSETS.wordmark,
    alt: "Shruti",
    onError: () => setErr(true)
  }) : /*#__PURE__*/React.createElement("span", {
    className: "brand-word"
  }, "Shruti"));
}
function SiteHeader({
  route,
  live,
  withArt,
  signedIn
}) {
  const [scrolled, setScrolled] = React.useState(false);
  const [menu, setMenu] = React.useState(false);
  React.useEffect(() => {
    const on = () => setScrolled(window.scrollY > 8);
    on();
    window.addEventListener('scroll', on, {
      passive: true
    });
    return () => window.removeEventListener('scroll', on);
  }, []);
  React.useEffect(() => {
    setMenu(false);
  }, [route]);
  return /*#__PURE__*/React.createElement("header", {
    className: "site-header",
    "data-scrolled": scrolled
  }, /*#__PURE__*/React.createElement("div", {
    className: "page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "bar"
  }, /*#__PURE__*/React.createElement(BrandMark, {
    withArt: withArt
  }), /*#__PURE__*/React.createElement("nav", {
    className: "site-nav",
    "aria-label": "Primary"
  }, NAV.map(([r, l]) => /*#__PURE__*/React.createElement("a", {
    key: r,
    href: '#' + r,
    "aria-current": route === r ? 'page' : undefined
  }, l))), /*#__PURE__*/React.createElement("div", {
    className: "header-side"
  }, /*#__PURE__*/React.createElement(LiveBadge, {
    compact: true,
    status: live.status,
    href: "#videos"
  }), /*#__PURE__*/React.createElement(LanguageSwitcher, {
    current: "en",
    onChange: () => {}
  }), /*#__PURE__*/React.createElement("a", {
    className: "acct-link",
    href: signedIn ? '#account' : '#signin'
  }, signedIn ? 'Account' : 'Sign in'), /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "nav-toggle",
    "aria-expanded": menu,
    "aria-controls": "site-menu",
    onClick: () => setMenu(m => !m)
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, menu ? '×' : '≡'), " Menu"))), menu && /*#__PURE__*/React.createElement("nav", {
    id: "site-menu",
    className: "site-menu",
    "aria-label": "Primary, mobile"
  }, NAV.map(([r, l]) => /*#__PURE__*/React.createElement("a", {
    key: r,
    href: '#' + r,
    "aria-current": route === r ? 'page' : undefined
  }, l)), /*#__PURE__*/React.createElement("span", {
    className: "site-menu-rule"
  }), /*#__PURE__*/React.createElement("a", {
    href: "#solar-stations"
  }, "Solar stations"), /*#__PURE__*/React.createElement("a", {
    href: "#lunar-stations"
  }, "Lunar stations"), /*#__PURE__*/React.createElement("a", {
    href: "#newsletter"
  }, "The monthly letter"), /*#__PURE__*/React.createElement("a", {
    href: signedIn ? '#account' : '#signin'
  }, signedIn ? 'Account' : 'Sign in'), /*#__PURE__*/React.createElement("a", {
    href: "#support"
  }, "Support"), /*#__PURE__*/React.createElement("a", {
    href: "#contact"
  }, "Contact"))));
}
function SiteFooter() {
  return /*#__PURE__*/React.createElement("footer", {
    className: "site-footer"
  }, /*#__PURE__*/React.createElement("div", {
    className: "page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cols"
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("span", {
    className: "brand-word",
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 22,
      color: 'var(--ink)'
    }
  }, "Shruti"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.55 var(--font-body)',
      color: 'var(--ink-soft)',
      maxWidth: '34ch',
      margin: '10px 0 14px'
    }
  }, "Instruments for magick, built live from Athens."), /*#__PURE__*/React.createElement(SocialLinkRow, {
    links: SOCIALS,
    size: 16
  })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h4", null, "Site"), /*#__PURE__*/React.createElement("ul", null, /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#work"
  }, "Work")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#today"
  }, "Day at a glance")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#solar-stations"
  }, "Solar stations")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#lunar-stations"
  }, "Lunar stations")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#schedule"
  }, "Schedule")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#videos"
  }, "Videos")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#horoscopes"
  }, "Horoscopes")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#journal"
  }, "Journal")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#about"
  }, "About")))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h4", null, "Elsewhere"), /*#__PURE__*/React.createElement("ul", null, /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#newsletter"
  }, "The monthly letter")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#press"
  }, "Press & media kit")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#fanworks"
  }, "Fan works")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#guidelines"
  }, "Derivative work guidelines")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#support"
  }, "Support")), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("a", {
    href: "#contact"
  }, "Contact"))))), /*#__PURE__*/React.createElement("div", {
    style: {
      paddingTop: 'var(--space-5)',
      marginTop: 'var(--space-5)',
      borderTop: 'var(--border-w) solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement(LegalImprint, null)), /*#__PURE__*/React.createElement("div", {
    className: "legal"
  }, /*#__PURE__*/React.createElement("p", null, "\xA9 ShrutiVTuber, LLC \xB7 ", /*#__PURE__*/React.createElement("a", {
    href: "#privacy",
    style: {
      color: 'inherit'
    }
  }, "Privacy"), " \xB7 ", /*#__PURE__*/React.createElement("a", {
    href: "#terms",
    style: {
      color: 'inherit'
    }
  }, "Terms")), /*#__PURE__*/React.createElement("span", {
    className: "seal seal-ring",
    title: "Soror Eu. A."
  }, "S\u2234E.A."))));
}
Object.assign(window, {
  SiteHeader,
  SiteFooter,
  BrandMark,
  ASSETS,
  SOCIALS
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Chrome.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Contact.jsx
try { (() => {
const {
  SectionHeader,
  TextField,
  TextArea,
  SelectField,
  Button,
  EmptyState
} = window.ShrutiDesignSystem_cb687f;
function ContactScreen() {
  const [f, setF] = React.useState({
    topic: '',
    name: '',
    email: '',
    msg: ''
  });
  const [err, setErr] = React.useState({});
  const [sent, setSent] = React.useState(false);
  const set = k => e => {
    const v = e.target.value;
    setF(s => ({
      ...s,
      [k]: v
    }));
    setErr(s => ({
      ...s,
      [k]: undefined
    }));
  };
  const submit = e => {
    e.preventDefault();
    const n = {};
    if (!f.topic) n.topic = 'Pick a route so this lands in the right inbox.';
    if (!f.name.trim()) n.name = 'Please add a name — a handle is fine.';
    if (!/^\S+@\S+\.\S+$/.test(f.email)) n.email = 'That address doesn\u2019t look complete.';
    if (f.msg.trim().length < 10) n.msg = 'A sentence or two helps me reply well.';
    setErr(n);
    if (Object.keys(n).length === 0) setSent(true);
  };
  const Card = ({
    title,
    children
  }) => /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 10,
      boxShadow: 'var(--shadow-1)',
      padding: '20px',
      display: 'grid',
      gap: 8,
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3, 20px) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, title), children);
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263F",
    eyebrow: "Contact",
    title: "Two routes in",
    body: "Business goes to one inbox, everything else to another \u2014 pick the right one and it gets answered faster."
  }), /*#__PURE__*/React.createElement("div", {
    className: "grid-2"
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Business enquiries"
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.55 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "Sponsorships, events, press. The brand-safety statement and asset pack are in the press kit."), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink)'
    }
  }, "business@shrutivtuber.com"), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#press"
  }, "Open the press kit"))), /*#__PURE__*/React.createElement(Card, {
    title: "Everything else"
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.55 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "Fan works, questions, edge cases, hellos. Discord is fastest; the form below also works."), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink)'
    }
  }, "hello@shrutivtuber.com"), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#"
  }, "Join the Discord")))), sent ? /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u263E",
    title: "Sent \u2014 thank you.",
    body: "Replies come from hello@shrutivtuber.com, usually within two working days. Business mail may take one more.",
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      onClick: () => {
        setSent(false);
        setF({
          topic: '',
          name: '',
          email: '',
          msg: ''
        });
      }
    }, "Send another")
  }) : /*#__PURE__*/React.createElement("form", {
    onSubmit: submit,
    noValidate: true,
    style: {
      display: 'grid',
      gap: 18,
      maxWidth: 560
    }
  }, /*#__PURE__*/React.createElement(SelectField, {
    label: "What is this about?",
    placeholder: "Choose a route",
    options: ['Business enquiry', 'Press', 'Fan works submission', 'Something else'],
    value: f.topic,
    onChange: set('topic'),
    error: err.topic,
    required: true
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Name",
    placeholder: "How should I address you?",
    value: f.name,
    onChange: set('name'),
    error: err.name,
    required: true
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "Email",
    type: "email",
    placeholder: "you@example.com",
    hint: "Only used to reply.",
    value: f.email,
    onChange: set('email'),
    error: err.email,
    required: true
  }), /*#__PURE__*/React.createElement(TextArea, {
    label: "Message",
    rows: 6,
    maxLength: 800,
    value: f.msg,
    onChange: set('msg'),
    error: err.msg,
    required: true,
    placeholder: "For fan works: include a link and the credit you want shown."
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    type: "submit"
  }, "Send"))));
}
Object.assign(window, {
  ContactScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Contact.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/FanWorks.jsx
try { (() => {
const {
  SectionHeader,
  FanArtCard,
  Modal,
  Button,
  EmptyState,
  Pagination
} = window.ShrutiDesignSystem_cb687f;
function FanWorksScreen() {
  const [open, setOpen] = React.useState(null);
  const [page, setPage] = React.useState(1);
  const works = [{
    title: 'Dusk study',
    artist: '@aster_ink',
    platform: 'X'
  }, {
    title: 'Planetary hours, annotated',
    artist: '@heliakos',
    platform: 'Pixiv'
  }, {
    title: 'Shruti at the bench',
    artist: '@moth.tarpana',
    platform: 'Bluesky'
  }, {
    title: 'Sigil compiler fan animation',
    artist: '@vhs_seance',
    platform: 'YouTube'
  }, {
    title: 'Chibi — moonrise',
    artist: '@paperikon',
    platform: 'X'
  }, {
    title: 'Wordmark embroidery',
    artist: '@stitchfane',
    platform: 'Instagram'
  }];
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2736",
    eyebrow: "Fan works",
    title: "Made by you",
    body: "Curated fan art and derivative work, credited loudly and linked back. Everything here appears with the artist's permission \u2014 the tiles fill in as pieces arrive."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))',
      gap: 20
    }
  }, works.map(w => /*#__PURE__*/React.createElement(FanArtCard, {
    key: w.title,
    image: null,
    title: w.title,
    artist: w.artist,
    artistHref: "#",
    platform: w.platform,
    onOpen: () => setOpen(w)
  }))), /*#__PURE__*/React.createElement(Pagination, {
    page: page,
    pageCount: 3,
    onChange: setPage
  }), /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25D0",
    title: "Made something?",
    body: "Tag it #ShrutiArts so it can be found, or send it through the contact form with the credit you want shown. Read the derivative work guidelines first \u2014 they're short.",
    action: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 10
      }
    }, /*#__PURE__*/React.createElement(Button, {
      href: "#contact"
    }, "Submit a piece"), /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      href: "#guidelines"
    }, "Read the guidelines"))
  }), /*#__PURE__*/React.createElement(Modal, {
    open: !!open,
    onClose: () => setOpen(null),
    variant: "lightbox",
    title: open ? `${open.title} — ${open.artist}` : undefined
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      placeItems: 'center',
      minHeight: 320,
      background: 'var(--surface-card)',
      borderRadius: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      font: '500 44px var(--font-display)',
      color: 'var(--ink-soft)'
    }
  }, "\u2736")), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: '10px 0 0'
    }
  }, "Art slot \u2014 the piece opens here at full size. Credit: ", open && open.artist, " \xB7 ", open && open.platform)));
}
Object.assign(window, {
  FanWorksScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/FanWorks.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Guidelines.jsx
try { (() => {
const {
  SectionHeader,
  Button
} = window.ShrutiDesignSystem_cb687f;
function GuidelinesScreen() {
  const Rule = ({
    m,
    children
  }) => {
    const c = m === '●' ? 'var(--live)' : m === '◐' ? 'var(--rose)' : 'var(--accent)';
    const w = m === '●' ? 'Not permitted' : m === '◐' ? 'Ask first' : 'Permitted';
    return /*#__PURE__*/React.createElement("li", {
      style: {
        display: 'flex',
        gap: 12,
        alignItems: 'baseline',
        padding: '10px 0',
        borderBottom: '1px solid var(--line)'
      }
    }, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        color: c,
        fontFamily: 'var(--font-display)',
        fontSize: 15,
        flexShrink: 0
      }
    }, m), /*#__PURE__*/React.createElement("span", {
      style: {
        font: '400 var(--text-body)/1.6 var(--font-body)',
        color: 'var(--ink)'
      }
    }, /*#__PURE__*/React.createElement("strong", {
      style: {
        fontWeight: 600
      }
    }, w, " \u2014 "), children));
  };
  const H = ({
    t
  }) => /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3, 22px) var(--font-display)',
      color: 'var(--ink)',
      margin: '18px 0 2px'
    }
  }, t);
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u25D0",
    eyebrow: "Derivative work guidelines",
    title: "What you may make",
    body: "Fan works are welcome \u2014 this page exists so nobody has to guess. The short version: make things, credit yourself, don't sell the character, and keep machines from learning her."
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '500 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--accent)'
    }
  }, "\u25CB"), " permitted \xB7 ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--rose)'
    }
  }, "\u25D0"), " ask first \xB7 ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--live)'
    }
  }, "\u25CF"), " not permitted"), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(H, {
    t: "Fan art"
  }), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0
    }
  }, /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CB"
  }, "Drawing, writing, music, cosplay and edits of Shruti, posted anywhere, with your own credit. Tag #ShrutiArts so it can be found and featured."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25D0"
  }, "NSFW work \u2014 allowed for adults, clearly marked, and kept out of the main tag. Never present it as official."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CF"
  }, "Passing fan work off as official art, or removing another artist's credit."))), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(H, {
    t: "Commercial use"
  }), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0
    }
  }, /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CB"
  }, "Monetised platforms carrying your fan work \u2014 ad revenue on your own speedpaint or cover is yours."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25D0"
  }, "Small-batch prints or con merch of your own fan art \u2014 write first; the answer is usually yes."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CF"
  }, "Mass-produced merchandise of the character, or commercial use of the wordmark and official art, without a written agreement."))), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(H, {
    t: "AI"
  }), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0
    }
  }, /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CF"
  }, "Training generative models on her art, voice, streams or writing \u2014 including LoRAs and voice clones."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CF"
  }, "AI-generated images in the fan tags. The gallery is for made things."))), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(H, {
    t: "Clips & streams"
  }), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0
    }
  }, /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CB"
  }, "Clips, edits, translations and reaction content, with a link back to the stream or VOD."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CF"
  }, "Re-uploading full VODs or streams without permission."))), /*#__PURE__*/React.createElement("section", null, /*#__PURE__*/React.createElement(H, {
    t: "Voice & likeness"
  }), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0
    }
  }, /*#__PURE__*/React.createElement(Rule, {
    m: "\u25D0"
  }, "Soundboards and voice compilations \u2014 ask, with the clips you intend to use."), /*#__PURE__*/React.createElement(Rule, {
    m: "\u25CF"
  }, "Impersonation: accounts, bots or content presenting themselves as Shruti."))), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: '14px 0 0'
    }
  }, "Questions live in the contact form. Last updated 2026-08 \xB7 signed, Shruti"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    href: "#contact"
  }, "Ask about an edge case"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#fanworks"
  }, "See fan works")));
}
Object.assign(window, {
  GuidelinesScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Guidelines.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Home.jsx
try { (() => {
const {
  Hero,
  Button,
  SectionHeader,
  VideoCard,
  ProjectCard,
  ScheduleItem,
  LiveBadge,
  SocialLinkRow
} = window.ShrutiDesignSystem_cb687f;
function HomeScreen({
  live,
  withArt,
  tz
}) {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main"
  }, /*#__PURE__*/React.createElement("div", {
    className: "page"
  }, /*#__PURE__*/React.createElement(Hero, {
    greeting: "Welcome \xB7 \u039A\u03B1\u03BB\u03CE\u03C2 \u03AE\u03C1\u03B8\u03B1\u03C4\u03B5 \xB7 \u0938\u094D\u0935\u093E\u0917\u0924",
    title: "I build instruments for magick.",
    subtitle: "Software for astrology, theurgy and divination \u2014 built live on stream from Athens.",
    art: withArt ? window.ASSETS.avatar : null,
    artAlt: "Shruti",
    clouds: withArt ? window.ASSETS.clouds : null,
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, live.status === 'live' ? /*#__PURE__*/React.createElement(Button, {
      variant: "live",
      size: "lg",
      href: "#videos"
    }, "Watch live") : /*#__PURE__*/React.createElement(Button, {
      size: "lg",
      href: "#schedule"
    }, "Next stream"), /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      size: "lg",
      href: "#work"
    }, "See the work")),
    footnote: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 16,
        alignItems: 'center',
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(LiveBadge, {
      status: live.status,
      title: live.title,
      game: live.game,
      viewers: live.viewers,
      nextStream: "Thu 21:00 EEST",
      href: "#videos"
    }), /*#__PURE__*/React.createElement(SocialLinkRow, {
      links: window.SOCIALS,
      size: 16
    }))
  })), /*#__PURE__*/React.createElement("section", {
    className: "section page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    glyph: "\u25B6",
    eyebrow: "Latest",
    title: "Recent streams",
    body: "Auto-pulled from Twitch and YouTube."
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#videos"
  }, "All videos \u2192")), /*#__PURE__*/React.createElement("div", {
    className: "grid-3"
  }, /*#__PURE__*/React.createElement(VideoCard, {
    title: "Building the sigil compiler \u2014 part 3",
    platform: "twitch",
    duration: "2:04:11",
    date: "3 days ago",
    href: "#videos"
  }), /*#__PURE__*/React.createElement(VideoCard, {
    title: "Planetary hours, computed properly",
    platform: "youtube",
    duration: "24:08",
    date: "2 weeks ago",
    href: "#videos"
  }), /*#__PURE__*/React.createElement(VideoCard, {
    title: "Theourgia devlog \u2014 the offerings ledger",
    platform: "twitch",
    duration: "1:41:09",
    date: "3 weeks ago",
    href: "#videos"
  }))), /*#__PURE__*/React.createElement("section", {
    className: "section page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    glyph: "\u263E",
    eyebrow: "Next on the almanac",
    title: "Upcoming stream"
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#schedule"
  }, "Full schedule \u2192")), /*#__PURE__*/React.createElement(ScheduleItem, {
    tz: tz,
    title: "Theourgia dev \u2014 offerings ledger",
    topic: "Software & Game Dev",
    durationMin: 150,
    startISO: "2026-08-27T21:00:00+03:00",
    href: "#schedule"
  })), /*#__PURE__*/React.createElement("section", {
    className: "section page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    glyph: "\u2736",
    eyebrow: "The work",
    title: "A portfolio of instruments",
    body: "The proof behind the brand: real software for real practice."
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#work"
  }, "About the work \u2192")), /*#__PURE__*/React.createElement("div", {
    className: "grid-2"
  }, /*#__PURE__*/React.createElement(ProjectCard, {
    name: "Theourgia",
    tagline: "A practitioner's toolkit that takes the calendar seriously.",
    status: "active",
    meta: "open source \xB7 self-hosted \xB7 federation",
    liveHref: "https://theourgia.com",
    screenshot: null
  }), /*#__PURE__*/React.createElement(ProjectCard, {
    name: "BeeRanked",
    tagline: "An SEO CMS that earns its keep.",
    status: "active",
    meta: "commercial SaaS",
    liveHref: "https://beeranked.online",
    screenshot: null
  }))), /*#__PURE__*/React.createElement("section", {
    className: "section page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    glyph: "\u2042",
    eyebrow: "Journal",
    title: "Recent writing"
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#journal"
  }, "Read the journal \u2192")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("a", {
    className: "journal-row",
    href: "#journal"
  }, /*#__PURE__*/React.createElement("span", {
    className: "jr-date"
  }, "2026-08-12"), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("h3", {
    className: "jr-title"
  }, "On the hours of Hekate"), /*#__PURE__*/React.createElement("p", {
    className: "jr-sub"
  }, "Why a planetary hour is not sixty minutes, and what that means for scheduling rites.")), /*#__PURE__*/React.createElement("span", {
    className: "jr-side"
  }, /*#__PURE__*/React.createElement("span", {
    className: "seal",
    style: {
      fontSize: 13
    }
  }, "Soror Eu. A."))), /*#__PURE__*/React.createElement("a", {
    className: "journal-row",
    href: "#journal"
  }, /*#__PURE__*/React.createElement("span", {
    className: "jr-date"
  }, "2026-07-30"), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("h3", {
    className: "jr-title"
  }, "Shipping the Attic calendar"), /*#__PURE__*/React.createElement("p", {
    className: "jr-sub"
  }, "Engineering notes on lunisolar months, intercalation, and tests that fail at dusk.")), /*#__PURE__*/React.createElement("span", {
    className: "jr-side"
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 12px var(--font-body)',
      color: 'var(--ink-faint)'
    }
  }, "Shruti"))))));
}
Object.assign(window, {
  HomeScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Home.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Horoscopes.jsx
try { (() => {
const {
  SectionHeader,
  SignPicker,
  PeriodSwitcher,
  Prose,
  Button,
  Badge,
  EmptyState,
  SubscribeBlock,
  Breadcrumb
} = window.ShrutiDesignSystem_cb687f;
const SIGNS = window.SHRUTI_SIGNS;
const READINGS = {
  virgo: {
    title: 'Virgo',
    glyph: '♍︎',
    lede: 'A month for finishing, which is not the same as a month for starting.',
    body: ['Mercury, your ruler, spends the first fortnight in your own sign and the second in Libra, which is the difference between thinking about your own work and thinking about someone else’s opinion of it. Do the private part first. The full moon on the 27th falls across the axis of what you own and what you owe, and it will make one of those two feel much larger than it is.', 'The stationary retrograde of Saturn on the 9th sits in your seventh, so an agreement you have been carrying alone stops being carryable alone. That is not a failure of yours; it is a fact about the arrangement. Say the true thing about it early in the month, while there is still room to alter terms rather than only to leave.', 'Toward the 22nd the Sun crosses into Libra and the season turns. Whatever you have been perfecting, ship it before then, imperfect. The instrument that exists is worth more than the one that would have been better.']
  },
  aries: {
    title: 'Aries',
    glyph: '♈︎',
    lede: 'The work comes back to you, and it comes back changed.',
    body: ['Mars leaves your twelfth this month, which is the astrological equivalent of a fever breaking. Energy you could not find in August is simply available in September, and the risk is spending all of it in the first week.', 'Saturn stations in your first. You are not being punished; you are being weighed. Answer the weighing honestly and it becomes a foundation.']
  }
};
const DEFAULT_READING = {
  lede: 'This month’s reading, written by hand.',
  body: ['Twelve are written each month, one per sign, in the last week of the month before. This one is here.', 'A second paragraph carries the timing — a station, an ingress, a lunation — and says plainly what it asks of you.']
};
function HoroscopeIndex({
  sign,
  setSign,
  ownSign,
  signedIn
}) {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2609",
    eyebrow: "Horoscopes",
    title: "September 2026",
    body: "Twelve readings, written by hand in the last week of August. Pick your sign \u2014 the choice is remembered."
  }), signedIn && ownSign ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      flexWrap: 'wrap',
      padding: 'var(--space-4)',
      background: 'var(--accent-wash)',
      borderRadius: 'var(--radius-md)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-glyph",
    style: {
      font: '400 1.5rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    },
    "aria-hidden": "true"
  }, "\u264D\uFE0E"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-body)/1.5 var(--font-body)',
      color: 'var(--ink)',
      flex: '1 1 240px'
    }
  }, "You read as ", /*#__PURE__*/React.createElement("strong", {
    style: {
      fontWeight: 600
    }
  }, "Virgo"), ", from your saved nativity \u2014 so it is open below without asking."), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    href: "#horoscope"
  }, "Read mine")) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      flexWrap: 'wrap',
      padding: 'var(--space-4)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm)/1.5 var(--font-body)',
      color: 'var(--ink-soft)',
      flex: '1 1 240px'
    }
  }, "With an account and a saved nativity, your sign opens first and arrives in the monthly letter. Reading without one works exactly the same otherwise."), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#signup"
  }, "Make an account")), /*#__PURE__*/React.createElement(SignPicker, {
    layout: "grid",
    current: sign,
    onChange: setSign,
    ownSign: ownSign
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, "The sky this month"), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "the same for everyone, whatever your sign")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))',
      gap: 'var(--space-3)'
    }
  }, [['♄', 'Saturn stations retrograde', '9 Sep · 04:12 EEST'], ['☉', 'Sun enters Libra', '22 Sep · 20:05 EEST'], ['☾', 'Full moon in Pisces', '27 Sep · 05:49 EEST'], ['☿', 'Mercury enters Libra', '14 Sep · 11:38 EEST']].map(([g, n, t]) => /*#__PURE__*/React.createElement("div", {
    key: n,
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      padding: 'var(--space-4)',
      display: 'grid',
      gap: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 1.25rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, g), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-sm) var(--font-body)',
      color: 'var(--ink)'
    }
  }, n), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-soft)'
    }
  }, t)))), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: 0
    }
  }, "Times from the ephemeris, in Athens, converted to your zone. ", /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      color: 'var(--accent)'
    }
  }, "Reckon it yourself"))), /*#__PURE__*/React.createElement(SubscribeBlock, {
    variant: "inline",
    heading: "Get it by email",
    body: "Your sign, monthly, with what I published and streamed and a letter written by hand."
  }));
}
function HoroscopeReading({
  sign,
  setSign,
  period,
  setPeriod,
  ownSign
}) {
  const r = READINGS[sign] || {
    ...DEFAULT_READING,
    title: (SIGNS.find(s => s.key === sign) || {}).name || 'Reading',
    glyph: (SIGNS.find(s => s.key === sign) || {}).glyph || '✶'
  };
  const mine = ownSign === sign;
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(Breadcrumb, {
    items: [{
      label: 'Horoscopes',
      href: '#horoscopes'
    }, {
      label: r.title
    }]
  }), /*#__PURE__*/React.createElement(PeriodSwitcher, {
    current: period,
    available: ['monthly'],
    onChange: setPeriod,
    label: "September 2026"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: 'var(--space-4)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 clamp(2.5rem,7vw,3.5rem) var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, r.glyph), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: '1 1 260px',
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      font: '500 var(--text-h1) var(--font-display)',
      letterSpacing: 'var(--tracking-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, r.title), mine && /*#__PURE__*/React.createElement(Badge, {
    tone: "rose"
  }, "your sign")), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-prose)/1.6 var(--font-display)',
      color: 'var(--ink-soft)',
      margin: '8px 0 0',
      maxWidth: '44ch'
    }
  }, r.lede))), /*#__PURE__*/React.createElement(Prose, {
    byline: "Soror Eu. A."
  }, r.body.map((p, i) => /*#__PURE__*/React.createElement("p", {
    key: i
  }, p))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap',
      alignItems: 'center',
      paddingTop: 'var(--space-4)',
      borderTop: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    href: "#horoscopes"
  }, "All twelve"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#"
  }, "Copy link"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-mono)',
      color: 'var(--ink-faint)',
      flex: '1 1 200px'
    }
  }, "Shareable, with a preview card for Discord and elsewhere.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Another sign"), /*#__PURE__*/React.createElement(SignPicker, {
    layout: "row",
    current: sign,
    onChange: setSign,
    ownSign: ownSign
  })), /*#__PURE__*/React.createElement(SubscribeBlock, {
    variant: "inline"
  }));
}
Object.assign(window, {
  HoroscopeIndex,
  HoroscopeReading
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Horoscopes.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Journal.jsx
try { (() => {
const {
  SectionHeader,
  Prose,
  Tag,
  Pagination,
  Breadcrumb,
  LanguageSwitcher,
  Badge
} = window.ShrutiDesignSystem_cb687f;
const POSTS = [{
  date: '2026-08-12',
  title: 'On the hours of Hekate',
  sub: 'Why a planetary hour is not sixty minutes, and what that means for scheduling rites.',
  by: 'soror',
  tags: ['theurgy', 'astrology'],
  langs: ['en', 'el']
}, {
  date: '2026-07-30',
  title: 'Shipping the Attic calendar',
  sub: 'Engineering notes on lunisolar months, intercalation, and tests that fail at dusk.',
  by: 'shruti',
  tags: ['engineering'],
  langs: ['en']
}, {
  date: '2026-07-11',
  title: 'Six divination systems, one schema',
  sub: 'Designing a data model that respects the differences instead of flattening them.',
  by: 'shruti',
  tags: ['engineering', 'divination'],
  langs: ['en', 'hi']
}, {
  date: '2026-06-24',
  title: 'Offerings, recorded',
  sub: 'A ledger is an act of attention. Notes on the offerings module.',
  by: 'soror',
  tags: ['theurgy'],
  langs: ['en', 'el', 'fr']
}];
function JournalScreen({
  article,
  openArticle
}) {
  if (article) return /*#__PURE__*/React.createElement(JournalArticle, {
    back: () => openArticle(false)
  });
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2042",
    eyebrow: "Journal",
    title: "Field notes",
    body: "Served from BeeRanked at /journal \u2014 engineering signed Shruti, magick signed Soror Eu. A."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Tag, {
    label: "all",
    active: true
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "theurgy",
    count: 7
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "astrology",
    count: 5
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "engineering",
    count: 12
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "divination",
    count: 4
  }))), /*#__PURE__*/React.createElement("div", null, POSTS.map((p, i) => /*#__PURE__*/React.createElement("a", {
    key: i,
    className: "journal-row",
    href: "#journal",
    onClick: e => {
      e.preventDefault();
      openArticle(true);
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "jr-date"
  }, p.date), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("h3", {
    className: "jr-title"
  }, p.title), /*#__PURE__*/React.createElement("p", {
    className: "jr-sub"
  }, p.sub), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      gap: 6,
      marginTop: 8,
      flexWrap: 'wrap'
    }
  }, p.tags.map(t => /*#__PURE__*/React.createElement(Tag, {
    key: t,
    label: t
  })))), /*#__PURE__*/React.createElement("span", {
    className: "jr-side"
  }, p.by === 'soror' ? /*#__PURE__*/React.createElement("span", {
    className: "seal",
    style: {
      fontSize: 13
    }
  }, "Soror Eu.\u200AA.") : /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 12px var(--font-body)',
      color: 'var(--ink-faint)'
    }
  }, "Shruti"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 10px var(--font-mono)',
      color: 'var(--ink-faint)',
      letterSpacing: '.06em'
    }
  }, p.langs.map(l => l.toUpperCase()).join(' · ')))))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement(Pagination, {
    page: 1,
    pageCount: 7,
    onChange: () => {}
  })));
}
function JournalArticle({
  back
}) {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page",
    style: {
      maxWidth: 820
    }
  }, /*#__PURE__*/React.createElement(Breadcrumb, {
    items: [{
      label: 'Journal',
      href: '#journal'
    }, {
      label: 'Theurgy',
      href: '#journal'
    }, {
      label: 'On the hours of Hekate'
    }]
  }), /*#__PURE__*/React.createElement("div", {
    className: "section-head",
    style: {
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      font: '600 var(--text-h1)/1.15 var(--font-display)',
      color: 'var(--ink)',
      margin: 0,
      maxWidth: '22ch',
      textWrap: 'balance'
    }
  }, "On the hours of Hekate"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12,
      alignItems: 'center',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "seal",
    style: {
      fontSize: 14
    }
  }, "Soror Eu.\u200AA."), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 11px var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "2026-08-12 \xB7 7 min"), /*#__PURE__*/React.createElement(Badge, {
    tone: "rose"
  }, "theurgy"))), /*#__PURE__*/React.createElement(LanguageSwitcher, {
    current: "en",
    hrefFor: l => '#journal',
    languages: ['en', 'el']
  })), /*#__PURE__*/React.createElement(Prose, {
    byline: "Soror Eu. A."
  }, /*#__PURE__*/React.createElement("p", null, "An hour here is not sixty minutes. Divide the arc of daylight by twelve, and each hour stretches in June and contracts in December \u2014 the almanac's kind of precision, where ", /*#__PURE__*/React.createElement("code", null, "sunrise(\u03C6, date)"), " is the first input of the day."), /*#__PURE__*/React.createElement("blockquote", null, "The instrument does not believe anything. It computes the sky as it is, and leaves the meaning to the practitioner."), /*#__PURE__*/React.createElement("p", null, "Theourgia treats this as a first-class primitive. Ask it for the ruler of the moment and it answers from the ephemeris, not from a lookup table of someone else's timezone."), /*#__PURE__*/React.createElement("hr", null), /*#__PURE__*/React.createElement("p", {
    lang: "el"
  }, "\u0397 \u03CE\u03C1\u03B1 \u03C4\u03BF\u03C5 \u0395\u03C1\u03BC\u03AE \u03B4\u03B5\u03BD \u03B5\u03AF\u03BD\u03B1\u03B9 \u03C0\u03BF\u03C4\u03AD \u03B5\u03BA\u03B5\u03AF \u03C0\u03BF\u03C5 \u03C4\u03B7 \u03C0\u03B5\u03C1\u03B9\u03BC\u03AD\u03BD\u03B5\u03B9\u03C2 \u03C4\u03BF\u03BD \u03C7\u03B5\u03B9\u03BC\u03CE\u03BD\u03B1 \u2014 \u03BA\u03B1\u03B9 \u03B1\u03C5\u03C4\u03CC \u03B5\u03AF\u03BD\u03B1\u03B9 \u03C4\u03BF \u03BD\u03CC\u03B7\u03BC\u03B1.")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("a", {
    href: "#journal",
    onClick: e => {
      e.preventDefault();
      back();
    }
  }, "\u2190 All field notes")));
}
Object.assign(window, {
  JournalScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Journal.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Legal.jsx
try { (() => {
const {
  SectionHeader,
  Prose,
  Button
} = window.ShrutiDesignSystem_cb687f;
const LEGAL = {
  privacy: {
    title: 'Privacy',
    intro: 'What this site knows about you — deliberately little.',
    secs: [{
      id: 'collection',
      h: 'What this site collects',
      p: ['This site sets no analytics cookies and runs no trackers. The server keeps standard access logs (IP address, user agent) for 14 days, for abuse prevention only, then deletes them.']
    }, {
      id: 'embeds',
      h: 'Embeds & third parties',
      p: ['Stream embeds and VOD thumbnails load from Twitch and YouTube, which see your requests under their own policies. The schedule\u2019s timezone conversion happens entirely in your browser \u2014 your timezone never leaves it.']
    }, {
      id: 'contact',
      h: 'Mail & submissions',
      p: ['Mail sent to the contact routes is kept as ordinary correspondence and is never added to a list. Fan-works submissions keep exactly the credit you asked for, and are removed on request.']
    }, {
      id: 'rights',
      h: 'Your rights',
      p: ['Under the GDPR you can ask what is held about you (usually: your own emails) and have it corrected or deleted \u2014 write to hello@shrutivtuber.com.']
    }, {
      id: 'controller',
      h: 'Controller',
      p: ['[Entity name] \u00b7 [virtual office address] \u00b7 Athens, Greece \u00b7 GEMI [no.] \u00b7 VAT [no.] \u2014 the controller for this site. The full imprint is in the footer.']
    }]
  },
  terms: {
    title: 'Terms',
    intro: 'Short, in plain language, and mostly common sense.',
    secs: [{
      id: 'content',
      h: 'Content & licence',
      p: ['Site text and original art are \u00a9 ShrutiVTuber, LLC. Theourgia is open source under its own licence \u2014 the repository speaks for itself. Quoting with attribution is welcome.']
    }, {
      id: 'fanworks',
      h: 'Derivative works',
      p: ['Fan works follow the derivative work guidelines, which are part of these terms. Where the two disagree, the guidelines win \u2014 they are the more generous document.']
    }, {
      id: 'asis',
      h: 'No warranty',
      p: ['The site, streams and software are offered as-is. Astrological and magickal content is practice and commentary, not professional, medical, legal or financial advice.']
    }, {
      id: 'law',
      h: 'Governing law',
      p: ['These terms are governed by Greek law; disputes go to the courts of Athens. If one clause fails, the rest stands.']
    }]
  }
};
function LegalScreen({
  doc
}) {
  const d = LEGAL[doc] || LEGAL.privacy;
  const go = id => e => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) window.scrollTo({
      top: el.getBoundingClientRect().top + window.scrollY - 84,
      behavior: 'smooth'
    });
  };
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2644",
    eyebrow: "Legal",
    title: d.title,
    body: d.intro
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: doc === 'privacy' ? 'secondary' : 'ghost',
    href: "#privacy"
  }, "Privacy"), /*#__PURE__*/React.createElement(Button, {
    variant: doc === 'terms' ? 'secondary' : 'ghost',
    href: "#terms"
  }, "Terms")), /*#__PURE__*/React.createElement("nav", {
    "aria-label": "On this page",
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 16,
      paddingBottom: 14,
      borderBottom: '1px solid var(--line)'
    }
  }, d.secs.map(s => /*#__PURE__*/React.createElement("a", {
    key: s.id,
    href: '#' + doc,
    onClick: go('leg-' + s.id),
    style: {
      font: '500 var(--text-sm) var(--font-mono)',
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, s.h))), /*#__PURE__*/React.createElement(Prose, null, d.secs.map(s => /*#__PURE__*/React.createElement(React.Fragment, {
    key: s.id
  }, /*#__PURE__*/React.createElement("h2", {
    id: 'leg-' + s.id
  }, s.h), s.p.map((t, i) => /*#__PURE__*/React.createElement("p", {
    key: i
  }, t))))), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "Last updated 2026-08 \xB7 earlier versions on request."));
}
Object.assign(window, {
  LegalScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Legal.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Newsletter.jsx
try { (() => {
const {
  SectionHeader,
  SubscribeBlock,
  Button,
  Badge,
  EmptyState,
  Toast,
  Pagination,
  LegalImprint
} = window.ShrutiDesignSystem_cb687f;
const ISSUES = [{
  no: '08',
  date: '2026-08-01',
  title: 'What the retrograde actually asks',
  blurb: 'Mercury back through Leo, the Attic month turning, and why I rewrote the sigil compiler twice.'
}, {
  no: '07',
  date: '2026-07-01',
  title: 'Building the calendar that argues with itself',
  blurb: 'Intercalation, two authorities, one date — and a stream schedule that finally held.'
}, {
  no: '06',
  date: '2026-06-01',
  title: 'On being weighed',
  blurb: 'Saturn, the offerings ledger, and the first six divination systems shipped.'
}, {
  no: '05',
  date: '2026-05-01',
  title: 'The hours are not sixty minutes',
  blurb: 'Planetary hours went live. Also: what I got wrong about sunrise.'
}];
function NewsletterScreen({
  view,
  go
}) {
  const [email, setEmail] = React.useState('');
  const [ok, setOk] = React.useState(false);
  const [err, setErr] = React.useState(null);
  const [sent, setSent] = React.useState(false);
  const [prefs, setPrefs] = React.useState({
    horoscope: true,
    videos: true,
    streams: true,
    articles: true,
    letter: true
  });
  const [cadence, setCadence] = React.useState('monthly');
  const [toast, setToast] = React.useState(null);
  const submit = e => {
    e.preventDefault();
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setErr('That address doesn’t look complete.');
      return;
    }
    if (!ok) {
      setErr('The consent box needs ticking — without it there is no lawful way to send you anything.');
      return;
    }
    setErr(null);
    setSent(true);
  };
  if (view === 'confirm') return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u263E",
    title: "You\u2019re on the list",
    body: "Confirmed. The next letter goes out on the first of the month, in the morning, Athens time. If you have an account with a saved nativity, your horoscope rides along with it.",
    action: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 10,
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(Button, {
      href: "#newsletter-archive"
    }, "Read a past issue"), /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      href: "#newsletter-preferences"
    }, "Choose what you get"))
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: 0,
      textAlign: 'center'
    }
  }, "Confirmed 24 Aug 2026 \xB7 this is the record of your consent, and you can withdraw it in one click from any letter."));
  if (view === 'unsubscribed') return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25CB",
    title: "Unsubscribed",
    body: "Done, immediately, and no sign-in was needed. You will get nothing further. If it was the frequency rather than the letter itself, a pause keeps your place instead.",
    action: /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 10,
        flexWrap: 'wrap'
      }
    }, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      href: "#newsletter-preferences"
    }, "Pause instead"), /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      href: "#home"
    }, "Back to the site"))
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: '0 auto',
      maxWidth: '52ch',
      textAlign: 'center'
    }
  }, "No survey, no \u201Care you sure\u201D, no offer to win you back. If you want to return, the subscribe form is where it always was."));
  if (view === 'preferences') return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u25D0",
    eyebrow: "The monthly letter",
    title: "What you get",
    body: "Turn sections off rather than the whole letter off. A pause keeps your place \u2014 it is not the same as leaving."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)',
      maxWidth: 620
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-2)'
    }
  }, [['horoscope', 'Your horoscope', 'Pulled from your saved nativity. Needs an account.'], ['videos', 'Videos since the last letter', 'Twitch and YouTube.'], ['streams', 'Streams since the last letter', 'What happened, and what got built in them.'], ['articles', 'Article summaries', 'A paragraph each, with links.'], ['letter', 'The letter itself', 'Written by hand. This is the part people subscribe for.']].map(([k, n, d]) => /*#__PURE__*/React.createElement("label", {
    key: k,
    style: {
      display: 'grid',
      gridTemplateColumns: '20px 1fr',
      gap: '2px 12px',
      padding: 'var(--space-3) var(--space-4)',
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: prefs[k],
    onChange: e => setPrefs(s => ({
      ...s,
      [k]: e.target.checked
    })),
    style: {
      width: 17,
      height: 17,
      margin: '2px 0 0',
      accentColor: 'var(--accent)',
      cursor: 'pointer'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'grid',
      gap: 2
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-body) var(--font-body)',
      color: 'var(--ink)'
    }
  }, n), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm)/1.5 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, d))))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Cadence"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap'
    }
  }, [['monthly', 'Monthly'], ['quarterly', 'Every third letter'], ['paused', 'Paused']].map(([k, l]) => /*#__PURE__*/React.createElement(Button, {
    key: k,
    variant: cadence === k ? 'secondary' : 'ghost',
    onClick: () => setCadence(k)
  }, l))), cadence === 'paused' && /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '56ch'
    }
  }, "Paused indefinitely. Nothing is sent, nothing is deleted, and one click here starts it again whenever you want it. Your address stays on the list with consent intact.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    onClick: () => setToast('Preferences saved.')
  }, "Save preferences"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#newsletter-unsubscribed"
  }, "Unsubscribe completely"))), toast && /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'fixed',
      right: 18,
      bottom: 70,
      zIndex: 60
    }
  }, /*#__PURE__*/React.createElement(Toast, {
    tone: "success",
    title: toast,
    onDismiss: () => setToast(null)
  })));
  if (view === 'archive') return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2042",
    eyebrow: "The monthly letter",
    title: "Past issues",
    body: "Every letter, public, so you can see exactly what you would be getting before you give an address."
  }), /*#__PURE__*/React.createElement("div", null, ISSUES.map(i => /*#__PURE__*/React.createElement("a", {
    key: i.no,
    href: "#newsletter-archive",
    style: {
      display: 'grid',
      gridTemplateColumns: '86px 1fr auto',
      gap: 'var(--space-4)',
      alignItems: 'baseline',
      padding: '18px 0',
      borderBottom: '1px solid var(--line)',
      textDecoration: 'none',
      color: 'inherit'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, i.date), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '600 var(--text-h4) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, i.title), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.55 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: '4px 0 0'
    }
  }, i.blurb)), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "\u2116 ", i.no)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement(Pagination, {
    page: 1,
    pageCount: 2,
    onChange: () => {}
  })), /*#__PURE__*/React.createElement(SubscribeBlock, {
    variant: "inline",
    heading: "Start with the next one",
    body: "Once a month. You have just seen four of them, so there are no surprises."
  }));
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263E",
    eyebrow: "The monthly letter",
    title: "Once a month, from Athens",
    body: "Your horoscope, the videos and streams since the last one, a paragraph on anything I published, and a letter written by hand. That last part is the reason to subscribe."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1.1fr 1fr',
      gap: 'var(--space-6)',
      alignItems: 'start'
    },
    className: "about-cols"
  }, /*#__PURE__*/React.createElement(SubscribeBlock, {
    email: email,
    onEmailChange: e => {
      setEmail(e.target.value);
      setErr(null);
    },
    consented: ok,
    onConsentChange: e => {
      setOk(e.target.checked);
      setErr(null);
    },
    onSubmit: submit,
    error: err,
    state: sent ? 'sent' : 'idle'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "What is in it"), /*#__PURE__*/React.createElement("ul", {
    style: {
      margin: 0,
      paddingLeft: 18,
      display: 'grid',
      gap: 6,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      fontWeight: 600,
      color: 'var(--ink)'
    }
  }, "Your horoscope"), ", automatically, if you have a saved nativity"), /*#__PURE__*/React.createElement("li", null, "Videos posted since the last issue"), /*#__PURE__*/React.createElement("li", null, "Streams since the last issue"), /*#__PURE__*/React.createElement("li", null, "Summaries of anything written on the site"), /*#__PURE__*/React.createElement("li", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      fontWeight: 600,
      color: 'var(--ink)'
    }
  }, "A letter written by hand")))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-inset)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-4)',
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Said plainly"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, "This list will eventually carry offers for astrological courses and magickal services. I would rather tell you that now than have you find out in issue four.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '8px 14px',
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "faint"
  }, "double opt-in"), /*#__PURE__*/React.createElement(Badge, {
    tone: "faint"
  }, "one click out"), /*#__PURE__*/React.createElement(Badge, {
    tone: "faint"
  }, "no tracking pixels")), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: 0
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#newsletter-archive",
    style: {
      color: 'var(--accent)'
    }
  }, "Read past issues"), " \xB7 ", /*#__PURE__*/React.createElement("a", {
    href: "#newsletter-preferences",
    style: {
      color: 'var(--accent)'
    }
  }, "Preferences"), " \xB7 ", /*#__PURE__*/React.createElement("a", {
    href: "#privacy",
    style: {
      color: 'var(--accent)'
    }
  }, "What is stored")))), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-5)',
      display: 'flex',
      gap: 'var(--space-5)',
      flexWrap: 'wrap',
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: '1 1 280px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: '0 0 8px',
      display: 'block'
    }
  }, "Who is sending it"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)',
      margin: 0,
      maxWidth: '46ch'
    }
  }, "Every letter carries the same imprint as this site, because a marketing email legally must.")), /*#__PURE__*/React.createElement(LegalImprint, null)));
}
Object.assign(window, {
  NewsletterScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Newsletter.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Press.jsx
try { (() => {
const {
  SectionHeader,
  StatBlock,
  AssetDownloadCard,
  EmptyState,
  Button
} = window.ShrutiDesignSystem_cb687f;
function PressScreen() {
  const A = window.ASSETS;
  const Sw = ({
    name,
    hex
  }) => /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      padding: '8px 0',
      borderBottom: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 18,
      height: 18,
      borderRadius: 4,
      background: hex,
      border: '1px solid var(--line)',
      flexShrink: 0
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm) var(--font-body)',
      color: 'var(--ink)',
      flex: 1
    }
  }, name), /*#__PURE__*/React.createElement("code", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)'
    }
  }, hex));
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263F",
    eyebrow: "Press & media kit",
    title: "Working with Shruti",
    body: "Numbers, brand rules and ready-to-use assets for sponsors, event organisers and press. Business enquiries get a reply within two working days."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(150px,1fr))',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(StatBlock, {
    value: "12.4k",
    label: "Followers",
    note: "all platforms",
    glyph: "\u263E"
  }), /*#__PURE__*/React.createElement(StatBlock, {
    value: "214",
    label: "Avg concurrent",
    note: "past 90 days"
  }), /*#__PURE__*/React.createElement(StatBlock, {
    value: "38%",
    label: "Returning viewers",
    note: "past 90 days"
  }), /*#__PURE__*/React.createElement(StatBlock, {
    value: "EN\xB7EL\xB7HI",
    label: "Stream languages"
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "Sample figures \u2014 live numbers come from the platform APIs on request."), /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h2",
    title: "Brand safety",
    body: "Streams are software and practice: no gambling segments, no sponsored financial or health claims, no undisclosed promotion. Occult subject matter is scholarly and practice-based \u2014 sponsors uncomfortable with that context should pass, and I'd rather they did. Every sponsorship is disclosed on stream and in the VOD description."
  }), /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h2",
    title: "Past collaborations"
  }), /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25CB",
    title: "The first collaboration slot is open",
    body: "Placements here list the partner, format and date \u2014 a record, not a wall of logos."
  }), /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h2",
    title: "Assets",
    body: "Transparent PNGs, current as of this kit. Keep clear space around the wordmark equal to the height of its 'S'; never recolour, stretch, or set it over busy art."
  }), /*#__PURE__*/React.createElement("div", {
    className: "grid-2"
  }, /*#__PURE__*/React.createElement(AssetDownloadCard, {
    name: "Wordmark \u2014 full",
    meta: "PNG \xB7 2778\xD71000 \xB7 transparent",
    preview: /*#__PURE__*/React.createElement("img", {
      src: A.wordmarkHiRes,
      alt: "Shruti wordmark"
    }),
    previewOn: "checker",
    href: A.wordmarkHiRes,
    filename: "shruti-wordmark.png"
  }), /*#__PURE__*/React.createElement(AssetDownloadCard, {
    name: "Wordmark \u2014 small",
    meta: "PNG \xB7 500\xD7180 \xB7 transparent",
    preview: /*#__PURE__*/React.createElement("img", {
      src: A.wordmark,
      alt: "Shruti wordmark, small"
    }),
    previewOn: "checker",
    href: A.wordmark,
    filename: "shruti-wordmark-small.png"
  }), /*#__PURE__*/React.createElement(AssetDownloadCard, {
    name: "Avatar",
    meta: "PNG \xB7 512\xD7512",
    preview: /*#__PURE__*/React.createElement("img", {
      src: A.avatar,
      alt: "Shruti avatar"
    }),
    previewOn: "ink",
    href: A.avatar,
    filename: "shruti-avatar.png"
  }), /*#__PURE__*/React.createElement(AssetDownloadCard, {
    name: "Clouds motif",
    meta: "PNG \xB7 2026\xD72837 \xB7 twilight sky",
    preview: /*#__PURE__*/React.createElement("img", {
      src: A.clouds,
      alt: "Clouds motif"
    }),
    previewOn: "sky",
    href: A.clouds,
    filename: "shruti-clouds.png"
  })), /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h2",
    title: "Colour",
    body: "One sky, two hours \u2014 dawn is the light theme, dusk the dark. Same palette, different hour."
  }), /*#__PURE__*/React.createElement("div", {
    className: "grid-2"
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '600 var(--text-sm) var(--font-ui, var(--font-body))',
      textTransform: 'uppercase',
      letterSpacing: '.14em',
      color: 'var(--ink-soft)',
      margin: '0 0 4px'
    }
  }, "Dawn"), /*#__PURE__*/React.createElement(Sw, {
    name: "Paper",
    hex: "#F8F6F3"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Ink",
    hex: "#26304A"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Accent blue",
    hex: "#33639C"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Rose",
    hex: "#A85A76"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Live red",
    hex: "#A62639"
  })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '600 var(--text-sm) var(--font-ui, var(--font-body))',
      textTransform: 'uppercase',
      letterSpacing: '.14em',
      color: 'var(--ink-soft)',
      margin: '0 0 4px'
    }
  }, "Dusk"), /*#__PURE__*/React.createElement(Sw, {
    name: "Page",
    hex: "#121829"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Ink",
    hex: "#E9E6F0"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Accent",
    hex: "#8FBEE8"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Rose",
    hex: "#E0A4BC"
  }), /*#__PURE__*/React.createElement(Sw, {
    name: "Live",
    hex: "#F07A8C"
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    href: "#contact"
  }, "Start a business enquiry"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)'
    }
  }, "business@shrutivtuber.com")));
}
Object.assign(window, {
  PressScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Press.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Schedule.jsx
try { (() => {
const {
  SectionHeader,
  ScheduleItem,
  TimezoneToggle,
  EmptyState,
  Button
} = window.ShrutiDesignSystem_cb687f;
function ScheduleScreen({
  tz,
  setTz,
  empty
}) {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u263E",
    eyebrow: "Schedule",
    title: "Upcoming streams",
    body: "Authored in Athens (GMT+3); times shown in your zone."
  }), /*#__PURE__*/React.createElement(TimezoneToggle, {
    value: tz,
    onChange: setTz
  })), empty ? /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25CB",
    title: "The sky is quiet",
    body: "Nothing scheduled yet \u2014 streams are announced on Discord first, and the calendar fills at the new moon.",
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "secondary"
    }, "Join the Discord")
  }) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(ScheduleItem, {
    tz: tz,
    status: "live",
    title: "Building the sigil compiler",
    topic: "Software & Game Dev",
    durationMin: 150,
    startISO: new Date(Date.now() - 35 * 60000).toISOString(),
    href: "#videos"
  }), /*#__PURE__*/React.createElement(ScheduleItem, {
    tz: tz,
    status: "upcoming",
    title: "Theourgia dev \u2014 offerings ledger",
    topic: "Software & Game Dev",
    durationMin: 150,
    startISO: "2026-08-27T21:00:00+03:00"
  }), /*#__PURE__*/React.createElement(ScheduleItem, {
    tz: tz,
    status: "upcoming",
    title: "Gematria deep-dive with viewers",
    topic: "Just Chatting \xB7 bilingual EN/\u0395\u039B",
    durationMin: 120,
    startISO: "2026-08-30T20:00:00+03:00"
  }), /*#__PURE__*/React.createElement(ScheduleItem, {
    tz: tz,
    status: "past",
    title: "Planetary hours, computed properly",
    topic: "Talk",
    startISO: "2026-08-18T20:00:00+03:00"
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-body)',
      color: 'var(--ink-faint)',
      margin: 0
    }
  }, "Subscribe: ", /*#__PURE__*/React.createElement("a", {
    href: "#"
  }, "iCal"), " \xB7 ", /*#__PURE__*/React.createElement("a", {
    href: "#"
  }, "Google Calendar"), " \u2014 conversions use your system timezone."));
}
Object.assign(window, {
  ScheduleScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Schedule.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Stations.jsx
try { (() => {
const {
  SectionHeader,
  NextStation,
  StationTable,
  ExportBlock,
  SelectField,
  TextField,
  Button,
  Badge
} = window.ShrutiDesignSystem_cb687f;
const SOLAR = {
  stations: ['Sunrise', 'Noon', 'Sunset', 'Midnight'],
  glyphs: ['☉︎', '☉︎', '☉︎', '☾︎'],
  presets: {
    hellenic: ['Hekate Phosphoros', 'Apollo', 'Hekate Enodia', 'Persephone'],
    thelemic: ['Liber Resh — Ra', 'Liber Resh — Ahathoor', 'Liber Resh — Tum', 'Liber Resh — Khephra'],
    none: null
  },
  times: [['06:52', '13:29', '20:05', '00:29'], ['06:53', '13:29', '20:03', '00:28'], ['06:54', '13:28', '20:02', '00:28'], ['06:55', '13:28', '20:00', '00:28'], ['06:56', '13:28', '19:58', '00:27'], ['06:57', '13:27', '19:57', '00:27'], ['06:58', '13:27', '19:55', '00:26'], ['06:59', '13:27', '19:53', '00:26']]
};
const LUNAR = {
  stations: ['Moonrise', 'Culmination', 'Moonset', 'Nadir'],
  glyphs: ['☾︎', '☽︎', '☾︎', '●'],
  // The Moon rises ~50 min later each day and skips a civil day now and then — nulls are real sky.
  times: [['17:41', '22:14', '03:22', '10:48'], ['18:29', '23:02', '04:11', '11:36'], ['19:14', '23:51', '05:02', '12:25'], ['19:57', null, '05:55', '13:15'], ['20:38', '00:41', '06:49', '14:06'], ['21:19', '01:33', '07:44', '14:58'], ['22:01', '02:26', '08:41', '15:51'], [null, '03:21', '09:39', '16:45']],
  phases: ['◐ 11.4 d', '◐ 12.4 d', '○ 13.4 d', '○ 14.4 d', '● 15.4 d', '● 16.4 d', '◑ 17.4 d', '◑ 18.4 d']
};
const DATES = ['7 Sep', '8 Sep', '9 Sep', '10 Sep', '11 Sep', '12 Sep', '13 Sep', '14 Sep'];
const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon'];
function StationsScreen({
  kind,
  polar
}) {
  const solar = kind === 'solar';
  const S = solar ? SOLAR : LUNAR;
  const [preset, setPreset] = React.useState('Hellenic');
  const [range, setRange] = React.useState('One month');
  const [copied, setCopied] = React.useState(false);
  const PRESET_KEY = {
    'Hellenic': 'hellenic',
    'Thelemic': 'thelemic',
    'None — times only': 'none'
  };
  const attributions = solar ? SOLAR.presets[PRESET_KEY[preset]] : null;
  const rows = S.times.map((t, i) => ({
    date: DATES[i],
    weekday: WEEKDAYS[i],
    times: t,
    today: i === 0,
    currentIndex: i === 0 ? solar ? 1 : 0 : undefined,
    phase: solar ? undefined : LUNAR.phases[i]
  }));
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: solar ? '☉︎' : '☾︎',
    eyebrow: 'Theourgia · ' + (solar ? 'solar' : 'lunar') + ' stations',
    title: solar ? 'Solar stations' : 'Lunar stations',
    body: solar ? 'Sunrise, noon, sunset, midnight — the four hinges a daily practice hangs on, for every day in the range you choose. The tool computes the times; which deity belongs to which station is yours to set or ignore.' : 'Moonrise, culmination, moonset, nadir. The Moon keeps its own calendar: it rises about fifty minutes later each day, and some days it does not rise at all.'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      padding: 'var(--space-5)',
      display: 'grid',
      gap: 'var(--space-4)'
    },
    className: "no-print"
  }, /*#__PURE__*/React.createElement("p", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Where and when"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(TextField, {
    label: "Place",
    defaultValue: polar ? 'Longyearbyen, SJ' : 'Athens, GR',
    hint: "Type a town, or use your location."
  }), /*#__PURE__*/React.createElement(TextField, {
    label: "From",
    type: "date",
    defaultValue: "2026-09-07"
  }), /*#__PURE__*/React.createElement(SelectField, {
    label: "Range",
    value: range,
    onChange: e => setRange(e.target.value),
    options: ['One day', 'One week', 'One month']
  }), solar && /*#__PURE__*/React.createElement(SelectField, {
    label: "Preset",
    value: preset,
    onChange: e => setPreset(e.target.value),
    options: ['Hellenic', 'Thelemic', 'None — times only']
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '8px 16px',
      flexWrap: 'wrap',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(Button, null, "Reckon"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Use my location"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "One month is the cap \u2014 ask for more and it is refused, not quietly trimmed.")), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-inset)',
      borderRadius: 'var(--radius-sm)',
      padding: 'var(--space-3) var(--space-4)',
      display: 'grid',
      gap: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, "Resolved to"), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink)'
    }
  }, polar ? 'Longyearbyen · 78.2232°N 15.6267°E · Arctic/Longyearbyen (GMT+2)' : 'Athens · 37.9838°N 23.7275°E · Europe/Athens · EEST (GMT+3)'), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-body)',
      color: 'var(--ink-faint)'
    }
  }, "Check it. A station table for the wrong city is indistinguishable from a right one until someone misses a dawn."))), polar && solar ? /*#__PURE__*/React.createElement(NextStation, {
    name: "Sunrise",
    at: "\u2014",
    inLabel: "\u2014",
    undefinedReason: "The Sun does not rise here today, so there is no solar station to count toward. The lunar stations still hold, and the sky and the reckonings below are unaffected."
  }) : /*#__PURE__*/React.createElement(NextStation, {
    glyph: solar ? '☉︎' : '☾︎',
    name: solar ? 'Sunset' : 'Moonrise',
    at: solar ? '20:05' : '17:41',
    inLabel: solar ? '2h 14m' : '41m',
    currentName: solar ? 'Noon' : 'Nadir',
    currentSince: solar ? '13:29' : '10:48',
    attribution: solar && attributions ? attributions[2] : undefined,
    progress: solar ? 0.62 : 0.88
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, range === 'One day' ? 'Today' : range === 'One week' ? 'This week' : 'The month'), /*#__PURE__*/React.createElement(Badge, {
    tone: "faint"
  }, "prints on one sheet"), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    className: "no-print",
    onClick: () => window.print()
  }, "Print")), polar && solar ? /*#__PURE__*/React.createElement(StationTable, {
    stations: SOLAR.stations,
    rows: [],
    undefinedReason: /*#__PURE__*/React.createElement(React.Fragment, null, "At ", /*#__PURE__*/React.createElement("span", {
      className: "t-tabular",
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 'var(--text-sm)'
      }
    }, "78.22\xB0N"), " the Sun neither rises nor sets on these dates, so sunrise, noon, sunset and midnight have no times to give. They are undefined here, not zero \u2014 and the planetary hours that divide them are undefined with them. The lunar stations are unaffected: the Moon still rises, most days.")
  }) : /*#__PURE__*/React.createElement(StationTable, {
    stations: S.stations,
    glyphs: S.glyphs,
    attributions: attributions || [],
    rows: rows,
    absentLabel: solar ? 'none today' : 'no moonrise today',
    caption: (polar ? 'Longyearbyen · 78.22°N 15.63°E' : 'Athens · 37.98°N 23.73°E') + ' · shown in your local time · Swiss Ephemeris 2.10.03'
  }), !solar && /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: 0,
      maxWidth: '74ch'
    }
  }, "A cell reading \u201Cno moonrise today\u201D is the sky, not a gap in the data. The Moon rises about fifty minutes later each day, so now and then it skips a civil day entirely \u2014 and at high latitude whole weeks can pass without one.")), /*#__PURE__*/React.createElement(ExportBlock, {
    feedHref: 'webcal://theourgia.com/stations/ical?kind=' + kind + '&place=athens' + (solar ? '&preset=' + PRESET_KEY[preset] : ''),
    fileHref: '/stations/ical?kind=' + kind + '&place=athens&from=2026-09-07&to=2026-10-06',
    fileName: kind + '-stations-athens-2026-09.ics',
    fileScope: "7 Sep \u2013 6 Oct 2026 \xB7 120 events",
    googleLinks: S.stations.map((s, i) => ({
      label: s,
      glyph: S.glyphs[i],
      href: '#'
    })),
    meta: 'Athens · ' + (solar ? preset === 'None — times only' ? 'times only' : preset.toLowerCase() + ' preset' : 'lunar') + ' · your local time',
    onCopyFeed: () => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    },
    copyLabel: copied ? 'Copied' : 'Copy feed URL'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-4)',
      display: 'flex',
      gap: '8px 22px',
      flexWrap: 'wrap',
      fontSize: 'var(--text-sm)'
    },
    className: "no-print"
  }, /*#__PURE__*/React.createElement("a", {
    href: "#today",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "\u25D0 Day at a glance"), /*#__PURE__*/React.createElement("a", {
    href: solar ? '#lunar-stations' : '#solar-stations',
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, solar ? '☾︎ Lunar stations' : '☉︎ Solar stations'), /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "\u2609 Planetary hours"), /*#__PURE__*/React.createElement("a", {
    href: "#work",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "All instruments")));
}
Object.assign(window, {
  StationsScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Stations.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Support.jsx
try { (() => {
const {
  SectionHeader,
  Button,
  Badge,
  EmptyState
} = window.ShrutiDesignSystem_cb687f;
function SupportScreen() {
  const Tier = ({
    name,
    price,
    note,
    items,
    badge,
    primary
  }) => /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 10,
      boxShadow: 'var(--shadow-1)',
      padding: '22px 20px',
      display: 'grid',
      gap: 12,
      alignContent: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 var(--text-h3, 20px) var(--font-display)',
      color: 'var(--ink)',
      margin: 0
    }
  }, name), badge), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 26px var(--font-mono)',
      color: 'var(--ink)',
      fontVariantNumeric: 'tabular-nums'
    }
  }, price, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm) var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, " ", note)), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0,
      display: 'grid',
      gap: 6
    }
  }, items.map(i => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      font: '400 var(--text-sm)/1.5 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, i))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: primary ? 'primary' : 'secondary',
    href: "#"
  }, primary ? 'Join on Ko-fi' : 'Open Ko-fi')));
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2644",
    eyebrow: "Support",
    title: "Keep the bench lit",
    body: "Streams are free and the tools are open source. Support pays for the ephemeris server, art commissions, and the hours the software takes."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))',
      gap: 20
    }
  }, /*#__PURE__*/React.createElement(Tier, {
    name: "One-off",
    price: "\u20AC3",
    note: "once, or any amount",
    items: ['A coffee for the bench', 'Name read on stream if you leave one', 'No account needed']
  }), /*#__PURE__*/React.createElement(Tier, {
    name: "Lamplighter",
    price: "\u20AC4",
    note: "/ month",
    badge: /*#__PURE__*/React.createElement(Badge, {
      tone: "rose"
    }, "Most common"),
    primary: true,
    items: ['Members channel on Discord', 'Schedule a day early', 'Name in the monthly credits roll']
  }), /*#__PURE__*/React.createElement(Tier, {
    name: "Almanac",
    price: "\u20AC9",
    note: "/ month",
    items: ['Everything in Lamplighter', 'Monthly practice notes, signed Soror Eu. A.', 'A vote on the next instrument']
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink-soft)',
      margin: 0
    }
  }, "Memberships are Ko-fi-hosted; cancel any time. Tiers ship only if memberships open \u2014 this is the design for that day."), /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h2",
    title: "Merch"
  }), /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25D0",
    title: "No merch yet",
    body: "Designs are commissioned before anything is printed \u2014 nothing exists that I wouldn't wear. Discord hears first when that changes."
  }));
}
Object.assign(window, {
  SupportScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Support.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Today.jsx
try { (() => {
const {
  SectionHeader,
  NextStation,
  Button,
  Badge,
  TextField,
  EmptyState
} = window.ShrutiDesignSystem_cb687f;
function Blk({
  title,
  note,
  children,
  span
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-1)',
      padding: 'var(--space-4) var(--space-4)',
      display: 'grid',
      gap: 10,
      alignContent: 'start',
      gridColumn: span ? 'span 2' : undefined
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 8,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    className: "t-eyebrow",
    style: {
      margin: 0
    }
  }, title), note && /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      marginLeft: 'auto',
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, note)), children);
}
function Row({
  k,
  v,
  sub
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-sm) var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, k), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      borderBottom: '1px dotted var(--line-strong)',
      transform: 'translateY(-3px)',
      minWidth: 12
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-sm) var(--font-mono)',
      color: 'var(--ink)'
    }
  }, v), sub && /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, sub));
}
function TodayScreen({
  signedIn,
  birthTime,
  polar
}) {
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      gap: 'var(--space-4)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u25D0",
    eyebrow: "Day at a glance",
    title: "The sky, here, now",
    body: polar ? 'Longyearbyen · 78.22°N 15.63°E · Monday 7 September 2026' : 'Athens · 37.98°N 23.73°E · Monday 7 September 2026 · your local time'
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginLeft: 'auto',
      display: 'flex',
      gap: 8,
      alignItems: 'flex-end'
    },
    className: "no-print"
  }, /*#__PURE__*/React.createElement(TextField, {
    label: "",
    defaultValue: polar ? 'Longyearbyen, SJ' : 'Athens, GR'
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Use my location"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(Blk, {
    title: "Sun and Moon",
    note: "right now"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 1.75rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, "\u2609"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-h4) var(--font-display)',
      color: 'var(--ink)'
    }
  }, "Virgo 14\xB052\u2032"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "tropical \xB7 Leo 20\xB038\u2032 sidereal"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 1.75rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, "\u263E"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-h4) var(--font-display)',
      color: 'var(--ink)'
    }
  }, "Aries 02\xB017\u2032"), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "moving 13\xB011\u2032 a day \xB7 Pisces 08\xB003\u2032 sidereal"))), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 2,
      background: 'var(--line)',
      borderRadius: 2,
      overflow: 'hidden'
    },
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: '18%',
      height: '100%',
      background: 'var(--rose)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.5 var(--font-body)',
      color: 'var(--ink-faint)'
    }
  }, "The Moon crosses about half a degree an hour \u2014 this bar is its progress through Aries."))), /*#__PURE__*/React.createElement(Blk, {
    title: "Stations"
  }, polar ? /*#__PURE__*/React.createElement(NextStation, {
    size: "block",
    name: "Sunrise",
    at: "\u2014",
    inLabel: "\u2014",
    undefinedReason: "No sunrise here today, so the solar stations are undefined. The lunar stations still hold."
  }) : /*#__PURE__*/React.createElement(NextStation, {
    size: "block",
    glyph: "\u2609\uFE0E",
    name: "Sunset",
    at: "20:05",
    inLabel: "2h 14m",
    currentName: "Noon",
    currentSince: "13:29",
    progress: 0.62
  }), /*#__PURE__*/React.createElement(NextStation, {
    size: "block",
    glyph: "\u263E\uFE0E",
    name: "Moonrise",
    at: "17:41",
    inLabel: "41m",
    currentName: "Nadir",
    currentSince: "10:48",
    progress: 0.88
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '8px 16px',
      flexWrap: 'wrap',
      fontSize: 'var(--text-sm)'
    },
    className: "no-print"
  }, /*#__PURE__*/React.createElement("a", {
    href: "#solar-stations",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "Solar tracker"), /*#__PURE__*/React.createElement("a", {
    href: "#lunar-stations",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "Lunar tracker"))), /*#__PURE__*/React.createElement(Blk, {
    title: "Planetary hour",
    note: polar ? 'undefined here' : 'unequal · 66 min'
  }, polar ? /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, "The hours divide sunrise to sunset. With no sunrise there is nothing to divide, so they are undefined today \u2014 not zero, and not clock hours pretending otherwise.") : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 1.5rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, "\u263F"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 var(--text-h4) var(--font-display)',
      color: 'var(--ink)'
    }
  }, "Hour of Mercury"), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "began 13:29 \xB7 ends 14:35"))), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 10,
      display: 'flex',
      alignItems: 'baseline',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    className: "t-glyph",
    style: {
      font: '400 1.25rem var(--font-display)',
      lineHeight: 1,
      color: 'var(--rose)'
    }
  }, "\u263E"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 var(--text-body) var(--font-body)',
      color: 'var(--ink)'
    }
  }, "Next \u2014 hour of the Moon"), /*#__PURE__*/React.createElement("span", {
    className: "t-tabular",
    style: {
      font: '400 var(--text-xs) var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "14:35 \u2013 15:41 \xB7 in 36m")), /*#__PURE__*/React.createElement(Badge, {
    tone: "rose"
  }, "plan against this")))), /*#__PURE__*/React.createElement(Blk, {
    title: "The sky over you",
    note: "now"
  }, /*#__PURE__*/React.createElement("div", {
    className: "sky",
    style: {
      borderRadius: 'var(--radius-sm)',
      padding: 0,
      overflow: 'hidden',
      border: '1px solid var(--line)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      aspectRatio: '4/3',
      display: 'grid',
      placeItems: 'center',
      textAlign: 'center',
      padding: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "sky-veil",
    style: {
      padding: '12px 16px',
      maxWidth: '30ch'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-xs)/1.7 var(--font-mono)',
      color: 'var(--ink-soft)',
      letterSpacing: '.04em'
    }
  }, "SKY CHART \xB7 rendered SVG", /*#__PURE__*/React.createElement("br", null), "visible chart for here and now"))))), /*#__PURE__*/React.createElement(Blk, {
    title: "Transits",
    note: signedIn ? birthTime ? 'to your nativity' : 'partial' : 'needs a nativity'
  }, !signedIn ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, "Everything else on this page works without an account, and always will. This one block needs to know where you were born \u2014 nothing else does."), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    href: "#signup"
  }, "Save a nativity")), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-mono)',
      color: 'var(--ink-faint)'
    }
  }, "No account? The page above is the whole page. This is an invitation, not a wall.")) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Row, {
    k: "\u2609 to your Moon",
    v: "square",
    sub: "2\xB014\u2032"
  }), /*#__PURE__*/React.createElement(Row, {
    k: "\u2644 to your Sun",
    v: "trine",
    sub: "0\xB041\u2032"
  }), /*#__PURE__*/React.createElement(Row, {
    k: "\u263F to your Mercury",
    v: "conjunct",
    sub: "1\xB002\u2032"
  }), birthTime ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Row, {
    k: "\u263E crossing your 7th",
    v: "today",
    sub: "17:41"
  }), /*#__PURE__*/React.createElement(Row, {
    k: "\u2642 on your ascendant",
    v: "in 3 days",
    sub: "\u2014"
  })) : /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 10,
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "t-eyebrow",
    style: {
      margin: 0,
      color: 'var(--rose)'
    }
  }, "\u25D0 Angular transits undefined"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: '400 var(--text-sm)/1.6 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, "Your nativity has no birth time, so the ascendant, midheaven and houses are undefined \u2014 and transits to them with it. The planetary transits above stand; the angular ones are not guessed."), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    href: "#nativity"
  }, "Add a birth time"))))), /*#__PURE__*/React.createElement(Blk, {
    title: "Today in every reckoning"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement(Row, {
    k: "Gregorian",
    v: "Mon 7 Sep 2026"
  }), /*#__PURE__*/React.createElement(Row, {
    k: "Attic",
    v: "\u03B4\u03C9\u03B4\u03B5\u03BA\u03AC\u03C4\u03B7 \u039C\u03B5\u03C4\u03B1\u03B3\u03B5\u03B9\u03C4\u03BD\u03B9\u1FF6\u03BD\u03BF\u03C2",
    sub: "12th"
  }), /*#__PURE__*/React.createElement(Row, {
    k: "Hindu \xB7 am\u0101nta",
    v: "Bh\u0101drapada k\u1E5B\u1E63\u1E47a 11",
    sub: "Vikrama 2083"
  }), /*#__PURE__*/React.createElement(Row, {
    k: "Thelemic",
    v: "Anno IVxxxiv \u2609 in \u264D",
    sub: "dies Lunae"
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 var(--text-xs)/1.5 var(--font-body)',
      color: 'var(--ink-faint)'
    }
  }, "Each links to the instrument that reckons it, with the rule it used."))), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--line)',
      paddingTop: 'var(--space-4)',
      display: 'flex',
      gap: '8px 22px',
      flexWrap: 'wrap',
      fontSize: 'var(--text-sm)'
    },
    className: "no-print"
  }, /*#__PURE__*/React.createElement("a", {
    href: "#solar-stations",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "\u2609\uFE0E Solar stations"), /*#__PURE__*/React.createElement("a", {
    href: "#lunar-stations",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "\u263E\uFE0E Lunar stations"), /*#__PURE__*/React.createElement("a", {
    href: "#horoscopes",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "\u264D\uFE0E Horoscopes"), /*#__PURE__*/React.createElement("a", {
    href: "#work",
    style: {
      color: 'var(--accent)',
      textDecoration: 'none'
    }
  }, "All instruments")));
}
Object.assign(window, {
  TodayScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Today.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Videos.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const {
  SectionHeader,
  VideoCard,
  VideoCardSkeleton,
  Tag,
  Pagination,
  EmptyState
} = window.ShrutiDesignSystem_cb687f;
function VideosScreen({
  loading
}) {
  const [filter, setFilter] = React.useState('all');
  const vids = [{
    title: 'Building the sigil compiler — part 3',
    platform: 'twitch',
    duration: '2:04:11',
    date: '3 days ago',
    kind: 'dev'
  }, {
    title: 'Planetary hours, computed properly',
    platform: 'youtube',
    duration: '24:08',
    date: '2 weeks ago',
    kind: 'talk'
  }, {
    title: 'Theourgia devlog — the offerings ledger',
    platform: 'twitch',
    duration: '1:41:09',
    date: '3 weeks ago',
    kind: 'dev'
  }, {
    title: 'Attic calendar Q&A · ΕΛ/EN',
    platform: 'twitch',
    duration: '1:12:44',
    date: '1 month ago',
    kind: 'chat'
  }, {
    title: 'Six divination systems, one schema',
    platform: 'youtube',
    duration: '31:02',
    date: '1 month ago',
    kind: 'talk'
  }, {
    title: 'BeeRanked: structured content for rank tracking',
    platform: 'youtube',
    duration: '18:26',
    date: '2 months ago',
    kind: 'dev'
  }].filter(v => filter === 'all' || v.kind === filter);
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "section-head"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u25B6",
    eyebrow: "Videos",
    title: "Streams & VODs",
    body: "Auto-pulled from Twitch and YouTube."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap'
    }
  }, [['all', 'All'], ['dev', 'Dev streams'], ['talk', 'Talks'], ['chat', 'Chatting']].map(([k, l]) => /*#__PURE__*/React.createElement(Tag, {
    key: k,
    label: l,
    active: filter === k,
    onClick: () => setFilter(k)
  })))), loading ? /*#__PURE__*/React.createElement("div", {
    className: "grid-3"
  }, /*#__PURE__*/React.createElement(VideoCardSkeleton, null), /*#__PURE__*/React.createElement(VideoCardSkeleton, null), /*#__PURE__*/React.createElement(VideoCardSkeleton, null), /*#__PURE__*/React.createElement(VideoCardSkeleton, null), /*#__PURE__*/React.createElement(VideoCardSkeleton, null), /*#__PURE__*/React.createElement(VideoCardSkeleton, null)) : vids.length === 0 ? /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25D0",
    title: "Nothing here yet",
    body: "No VODs match this filter \u2014 try another, or watch live on Thursdays."
  }) : /*#__PURE__*/React.createElement("div", {
    className: "grid-3"
  }, vids.map((v, i) => /*#__PURE__*/React.createElement(VideoCard, _extends({
    key: i
  }, v, {
    href: "#"
  })))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement(Pagination, {
    page: 1,
    pageCount: 4,
    onChange: () => {}
  })));
}
Object.assign(window, {
  VideosScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Videos.jsx", error: String((e && e.message) || e) }); }

// ui_kits/site/Work.jsx
try { (() => {
const {
  SectionHeader,
  ProjectCard,
  ProfileFieldTable,
  EmptyState,
  Button,
  Tag
} = window.ShrutiDesignSystem_cb687f;
function WorkScreen() {
  const Entry = ({
    card,
    credits,
    contributors
  }) => /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 'var(--space-5)',
      alignContent: 'start'
    }
  }, card, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '600 var(--text-micro) var(--font-body)',
      letterSpacing: 'var(--tracking-eyebrow)',
      textTransform: 'uppercase',
      color: 'var(--ink-faint)',
      margin: '0 0 10px'
    }
  }, "Credits"), /*#__PURE__*/React.createElement(ProfileFieldTable, {
    columns: 1,
    fields: credits
  }), contributors && /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 var(--text-xs)/1.6 var(--font-mono)',
      color: 'var(--ink-faint)',
      margin: '10px 0 0'
    }
  }, contributors)));
  return /*#__PURE__*/React.createElement("main", {
    className: "site-main page"
  }, /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h1",
    glyph: "\u2736",
    eyebrow: "The work",
    title: "A portfolio of instruments",
    body: "Not an app-store listing. Each of these is a working tool, shipped and maintained \u2014 most of it built live on stream. Every entry carries its role, stack, licence and status, because that is what another engineer wants to know."
  }), /*#__PURE__*/React.createElement("div", {
    className: "grid-2"
  }, /*#__PURE__*/React.createElement(Entry, {
    card: /*#__PURE__*/React.createElement(ProjectCard, {
      name: "Theourgia",
      tagline: "A practitioner's toolkit that takes the calendar seriously.",
      description: "Open-source magickal journal CMS: Attic lunar calendar, Swiss Ephemeris astrology, planetary hours, six divination systems, sigil generation, gematria, an offerings ledger, and federation. Authored under Soror Eu. A.",
      status: "active",
      meta: "AGPL-3.0 \xB7 self-hosted \xB7 federation",
      liveHref: "https://theourgia.com",
      repoHref: "#",
      screenshot: null
    }),
    credits: [{
      label: 'Name',
      value: 'Theourgia'
    }, {
      label: 'Role',
      value: 'Author · maintainer'
    }, {
      label: 'Stack',
      value: 'Astro · TypeScript · Postgres · Swiss Ephemeris'
    }, {
      label: 'Licence',
      value: 'AGPL-3.0'
    }, {
      label: 'Status',
      value: 'Active'
    }],
    contributors: "Ephemeris data \xA9 Astrodienst \xB7 translations by the Discord"
  }), /*#__PURE__*/React.createElement(Entry, {
    card: /*#__PURE__*/React.createElement(ProjectCard, {
      name: "BeeRanked",
      tagline: "An SEO CMS that earns its keep.",
      description: "Commercial SEO CMS SaaS \u2014 structured content, rank tracking, and the platform this site's journal is served from.",
      status: "active",
      meta: "Proprietary \xB7 commercial SaaS \xB7 hosts /journal",
      liveHref: "https://beeranked.online",
      screenshot: null
    }),
    credits: [{
      label: 'Name',
      value: 'BeeRanked'
    }, {
      label: 'Role',
      value: 'Founder · lead developer'
    }, {
      label: 'Stack',
      value: 'Next.js · Postgres · Redis · Cloudflare'
    }, {
      label: 'Licence',
      value: 'Proprietary'
    }, {
      label: 'Status',
      value: 'Active · commercial'
    }]
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement(Tag, {
    label: "ephemeris"
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "lunisolar calendars"
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "divination"
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "sigils"
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "gematria"
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "federation"
  }), /*#__PURE__*/React.createElement(Tag, {
    label: "astro.js"
  })), /*#__PURE__*/React.createElement(SectionHeader, {
    as: "h2",
    glyph: "\u263F",
    title: "Instruments you can run here",
    body: "Six of Theourgia's tools run in the browser on their own pages \u2014 the software demonstrating itself, no install."
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill,minmax(180px,1fr))',
      gap: 12
    }
  }, [['☉', 'Planetary hours', 'The day divided by its own light.'], ['☽', 'Attic calendar', 'The lunisolar month, kept current.'], ['◐', 'Pañcāṅga', 'The five limbs of the day.'], ['Σ', 'Isopsephy', 'Greek letter-reckoning.'], ['✶', 'Natal chart', 'A figure for a moment and a place.'], ['●', 'Sigil generator', 'Intent, reduced and drawn.']].map(([g, n, d]) => /*#__PURE__*/React.createElement("a", {
    key: n,
    href: "#",
    style: {
      display: 'block',
      background: 'var(--surface-card)',
      border: '1px solid var(--line)',
      borderRadius: 10,
      boxShadow: 'var(--shadow-1)',
      padding: 16,
      textDecoration: 'none'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      font: '400 1.25rem var(--font-display)',
      color: 'var(--rose)'
    }
  }, g), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      marginTop: 8,
      font: '600 var(--text-h4) var(--font-display)',
      color: 'var(--ink)'
    }
  }, n), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      marginTop: 4,
      font: '400 var(--text-xs)/1.5 var(--font-body)',
      color: 'var(--ink-soft)'
    }
  }, d)))), /*#__PURE__*/React.createElement(EmptyState, {
    glyph: "\u25D0",
    title: "What follows",
    body: "The next instrument is chosen on stream. Suggestions land in the Discord's #workbench channel.",
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "secondary"
    }, "Join the Discord")
  }));
}
Object.assign(window, {
  WorkScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/site/Work.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Hero = __ds_scope.Hero;

__ds_ns.LanguageSwitcher = __ds_scope.LanguageSwitcher;

__ds_ns.LegalImprint = __ds_scope.LegalImprint;

__ds_ns.LiveBadge = __ds_scope.LiveBadge;

__ds_ns.SectionHeader = __ds_scope.SectionHeader;

__ds_ns.SocialIcon = __ds_scope.SocialIcon;

__ds_ns.SocialLinkRow = __ds_scope.SocialLinkRow;

__ds_ns.SubscribeBlock = __ds_scope.SubscribeBlock;

__ds_ns.AssetDownloadCard = __ds_scope.AssetDownloadCard;

__ds_ns.FanArtCard = __ds_scope.FanArtCard;

__ds_ns.ProjectCard = __ds_scope.ProjectCard;

__ds_ns.StatBlock = __ds_scope.StatBlock;

__ds_ns.VideoCard = __ds_scope.VideoCard;

__ds_ns.VideoCardSkeleton = __ds_scope.VideoCardSkeleton;

__ds_ns.Prose = __ds_scope.Prose;

__ds_ns.EmptyState = __ds_scope.EmptyState;

__ds_ns.Modal = __ds_scope.Modal;

__ds_ns.Skeleton = __ds_scope.Skeleton;

__ds_ns.Toast = __ds_scope.Toast;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.ConsentCheckbox = __ds_scope.ConsentCheckbox;

__ds_ns.SelectField = __ds_scope.SelectField;

__ds_ns.TextArea = __ds_scope.TextArea;

__ds_ns.TextField = __ds_scope.TextField;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Breadcrumb = __ds_scope.Breadcrumb;

__ds_ns.Pagination = __ds_scope.Pagination;

__ds_ns.PeriodSwitcher = __ds_scope.PeriodSwitcher;

__ds_ns.SIGNS = __ds_scope.SIGNS;

__ds_ns.SignPicker = __ds_scope.SignPicker;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.CreditList = __ds_scope.CreditList;

__ds_ns.ExportBlock = __ds_scope.ExportBlock;

__ds_ns.NextStation = __ds_scope.NextStation;

__ds_ns.ProfileFieldTable = __ds_scope.ProfileFieldTable;

__ds_ns.ScheduleItem = __ds_scope.ScheduleItem;

__ds_ns.StationTable = __ds_scope.StationTable;

__ds_ns.TimezoneToggle = __ds_scope.TimezoneToggle;

})();
