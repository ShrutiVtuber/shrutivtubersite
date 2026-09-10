/* Sample data for the Astrolabe UI kit. Plausible and internally consistent —
   NOT live computation. The reckoning a developer must write is described in
   readme.md and guidelines/theme-flutter.md. */
window.AL = (function () {
  const G = { sun:'\u2609\uFE0E', moon:'\u263E\uFE0E', mercury:'\u263F\uFE0E', venus:'\u2640\uFE0E',
    mars:'\u2642\uFE0E', jupiter:'\u2643\uFE0E', saturn:'\u2644\uFE0E', uranus:'\u2645\uFE0E',
    neptune:'\u2646\uFE0E', pluto:'\u2647\uFE0E', node:'\u260A\uFE0E', rx:'\u211E\uFE0E' };
  /* Every mark carries U+FE0E in the data itself, so it survives being copied out
     of the app into a message, a caption, or a printed table. */
  const S = { aries:'\u2648\uFE0E', taurus:'\u2649\uFE0E', gemini:'\u264A\uFE0E', cancer:'\u264B\uFE0E',
    leo:'\u264C\uFE0E', virgo:'\u264D\uFE0E', libra:'\u264E\uFE0E', scorpio:'\u264F\uFE0E',
    sagittarius:'\u2650\uFE0E', capricorn:'\u2651\uFE0E', aquarius:'\u2652\uFE0E', pisces:'\u2653\uFE0E' };

  const readings = [
    { id:'r1', sign:'Scorpio', mark:S.scorpio, date:'9 Sep', time:'2 min', unread:true,
      excerpt:'Mercury is still in the shadow, so the thing you thought was settled on Friday is not settled. Leave it until the 18th.' },
    { id:'r2', sign:'Capricorn', mark:S.capricorn, date:'9 Sep', time:'2 min',
      excerpt:'Saturn is on your descendant and it is asking about one relationship in particular. You know which.' },
    { id:'r3', sign:'Aries', mark:S.aries, date:'8 Sep', time:'1 min' },
    { id:'r4', sign:'Virgo', mark:S.virgo, date:'8 Sep', time:'3 min',
      excerpt:'The Sun is on your own degree this week, which is less dramatic than it sounds and more useful than you expect.' }
  ];
  const articles = [
    { id:'a1', title:'What a station actually is', date:'4 Sep', time:'9 min',
      excerpt:'Apparent motion, and why the word retrograde has survived the model that produced it.' },
    { id:'a2', title:'Casting a chart with no birth time, honestly', date:'28 Aug', time:'12 min',
      excerpt:'What you may still say, what you may not, and how the app refuses to guess for you.' },
    { id:'a3', title:'The hours are not sixty minutes long', date:'21 Aug', time:'6 min' }
  ];
  const offers = [
    { id:'o1', title:'Six weeks of Hellenistic basics', price:'\u20ac120', cadence:'for six weeks', mark:G.jupiter,
      body:'Live on Thursdays, recorded for members. Twelve places.', href:'https://shrutivtuber.com/classes' },
    { id:'o2', title:'Members\u2019 chart clinic', price:'Included', membersOnly:true, mark:G.venus,
      body:'One chart a month, read on stream, name withheld if you want it withheld.' },
    { id:'o3', title:'A reading, written for you', price:'\u20ac65', mark:G.mercury, soldOut:true,
      body:'Two thousand words on one question. Currently full until October.' }
  ];
  const stations = {
    columns:[{key:'date',label:'Day',width:64},{key:'sun',label:'Sun',mark:G.sun,numeric:true},
      {key:'moon',label:'Moon',mark:G.moon,numeric:true},{key:'mer',label:'Mercury',mark:G.mercury,numeric:true},
      {key:'ven',label:'Venus',mark:G.venus,numeric:true},{key:'mar',label:'Mars',mark:G.mars,numeric:true},
      {key:'phase',label:'Phase',numeric:true,width:50}],
    rows:[
      { id:'5', date:'5 Sep', sun:'12\u00b0'+S.virgo, moon:'26\u00b0'+S.sagittarius, mer:{value:'04\u00b0'+S.libra,retro:true}, ven:'26\u00b0'+S.leo, mar:'09\u00b0'+S.libra, phase:'\u25d0' },
      { id:'6', date:'6 Sep', sun:'13\u00b0'+S.virgo, moon:'09\u00b0'+S.capricorn, mer:{value:'03\u00b0'+S.libra,retro:true}, ven:'27\u00b0'+S.leo, mar:'10\u00b0'+S.libra, phase:'\u25d0' },
      { id:'7', date:'7 Sep', sun:'14\u00b0'+S.virgo, moon:'21\u00b0'+S.capricorn, mer:{value:'02\u00b0'+S.libra,retro:true}, ven:'28\u00b0'+S.leo, mar:'11\u00b0'+S.libra, phase:'\u25cf' },
      { id:'8', date:'8 Sep', sun:'15\u00b0'+S.virgo, moon:'04\u00b0'+S.aquarius, mer:{value:'01\u00b0'+S.libra,retro:true}, ven:'29\u00b0'+S.leo, mar:'12\u00b0'+S.libra, phase:'\u25cf' },
      { id:'9', date:'9 Sep', today:true, sun:'16\u00b0'+S.virgo, moon:'17\u00b0'+S.aquarius, mer:{value:'00\u00b0'+S.libra,retro:true}, ven:'00\u00b0'+S.virgo, mar:'12\u00b0'+S.libra, phase:'\u25cf' },
      { id:'10', date:'10 Sep', sun:'17\u00b0'+S.virgo, moon:'00\u00b0'+S.pisces, mer:'29\u00b0'+S.virgo, ven:'01\u00b0'+S.virgo, mar:'13\u00b0'+S.libra, phase:'\u25d1' },
      { id:'11', date:'11 Sep', sun:'18\u00b0'+S.virgo, moon:'13\u00b0'+S.pisces, mer:'29\u00b0'+S.virgo, ven:'02\u00b0'+S.virgo, mar:'14\u00b0'+S.libra, phase:'\u25d1' },
      { id:'12', date:'12 Sep', sun:'19\u00b0'+S.virgo, moon:'26\u00b0'+S.pisces, mer:'29\u00b0'+S.virgo, ven:'03\u00b0'+S.virgo, mar:'14\u00b0'+S.libra, phase:'\u25d1' },
      { id:'13', date:'13 Sep', sun:'20\u00b0'+S.virgo, moon:'09\u00b0'+S.aries, mer:'00\u00b0'+S.libra, ven:'04\u00b0'+S.virgo, mar:'15\u00b0'+S.libra, phase:'\u25d1' },
      { id:'14', date:'14 Sep', sun:'21\u00b0'+S.virgo, moon:'22\u00b0'+S.aries, mer:'01\u00b0'+S.libra, ven:'05\u00b0'+S.virgo, mar:'16\u00b0'+S.libra, phase:'\u25cb' },
      { id:'15', date:'15 Sep', sun:'22\u00b0'+S.virgo, moon:'05\u00b0'+S.taurus, mer:'02\u00b0'+S.libra, ven:'06\u00b0'+S.virgo, mar:'17\u00b0'+S.libra, phase:'\u25cb' },
      { id:'16', date:'16 Sep', sun:'23\u00b0'+S.virgo, moon:'18\u00b0'+S.taurus, mer:'04\u00b0'+S.libra, ven:'07\u00b0'+S.virgo, mar:'17\u00b0'+S.libra, phase:'\u25cb' }
    ]
  };
  const hours = {
    columns:[{key:'n',label:'#',width:30},{key:'from',label:'From',numeric:true},{key:'to',label:'To',numeric:true},
      {key:'ruler',label:'Ruler'},{key:'len',label:'Length',numeric:true}],
    rows:[
      { id:1, n:'1', from:'06:58', to:'08:00', ruler:G.mercury+'\ufe0e Mercury', len:'62 m' },
      { id:2, n:'2', from:'08:00', to:'09:02', ruler:G.moon+'\ufe0e Moon', len:'62 m' },
      { id:3, n:'3', from:'09:02', to:'10:04', ruler:G.saturn+'\ufe0e Saturn', len:'62 m' },
      { id:4, n:'4', from:'10:04', to:'11:06', ruler:G.jupiter+'\ufe0e Jupiter', len:'62 m' },
      { id:5, n:'5', from:'11:06', to:'12:08', ruler:G.mars+'\ufe0e Mars', len:'62 m' },
      { id:6, n:'6', from:'12:08', to:'13:10', ruler:G.sun+'\ufe0e Sun', len:'62 m' },
      { id:7, n:'7', today:true, from:'13:10', to:'14:12', ruler:G.venus+'\ufe0e Venus', len:'62 m' },
      { id:8, n:'8', from:'14:12', to:'15:14', ruler:G.mercury+'\ufe0e Mercury', len:'62 m' },
      { id:9, n:'9', from:'15:14', to:'16:16', ruler:G.moon+'\ufe0e Moon', len:'62 m' },
      { id:10, n:'10', from:'16:16', to:'17:18', ruler:G.saturn+'\ufe0e Saturn', len:'62 m' },
      { id:11, n:'11', from:'17:18', to:'18:20', ruler:G.jupiter+'\ufe0e Jupiter', len:'62 m' },
      { id:12, n:'12', from:'18:20', to:'19:22', ruler:G.mars+'\ufe0e Mars', len:'62 m' }
    ]
  };
  const coming = [
    { when:'Thu 11 Sep', mark:G.mercury, title:'Mercury stations direct', detail:'29\u00b0 Virgo, 04:12 Athens \u00b7 02:12 your time', tone:'caution' },
    { when:'Sat 13 Sep', mark:G.moon, title:'Last quarter', detail:'21\u00b0 Gemini, 12:31 Athens' },
    { when:'Mon 22 Sep', mark:G.sun, title:'Equinox', detail:'The Sun enters Libra, 21:19 Athens' },
    { when:'Wed 24 Sep', mark:G.venus, title:'Venus enters Virgo', detail:'02:47 Athens' },
    { when:'Sun 5 Oct', mark:G.saturn, title:'Saturn stations direct', detail:'25\u00b0 Pisces, 19:04 Athens', tone:'caution' }
  ];
  const bodies = [
    { name:'Sun', mark:G.sun, lon:166.7 }, { name:'Moon', mark:G.moon, lon:317.2 },
    { name:'Mercury', mark:G.mercury, lon:180.9, retro:true }, { name:'Venus', mark:G.venus, lon:150.4 },
    { name:'Mars', mark:G.mars, lon:192.5 }, { name:'Jupiter', mark:G.jupiter, lon:98.1 },
    { name:'Saturn', mark:G.saturn, lon:349.8, retro:true }, { name:'Uranus', mark:G.uranus, lon:62.4 },
    { name:'Neptune', mark:G.neptune, lon:359.1, retro:true }, { name:'Pluto', mark:G.pluto, lon:300.6, retro:true }
  ];
  const aspects = [
    { from:166.7, to:349.8, type:'opposition' }, { from:317.2, to:150.4, type:'trine' },
    { from:150.4, to:62.4, type:'square' }, { from:180.9, to:98.1, type:'sextile' },
    { from:166.7, to:180.9, type:'conjunction' }, { from:192.5, to:98.1, type:'square' }
  ];
  const cusps = [214.3, 244.3, 274.3, 304.3, 334.3, 4.3, 34.3, 64.3, 94.3, 124.3, 154.3, 184.3];
  const chartTable = [
    { mark:G.sun, label:'Sun', value:'16\u00b0 42\u2032 '+S.virgo+' \u00b7 5th' },
    { mark:G.moon, label:'Moon', value:'17\u00b0 09\u2032 '+S.aquarius+' \u00b7 11th' },
    { mark:G.mercury, label:'Mercury', value:'00\u00b0 51\u2032 '+S.libra+' \u211e \u00b7 6th', rose:true },
    { mark:G.venus, label:'Venus', value:'00\u00b0 24\u2032 '+S.virgo+' \u00b7 5th' },
    { mark:G.mars, label:'Mars', value:'12\u00b0 30\u2032 '+S.libra+' \u00b7 6th' },
    { mark:G.jupiter, label:'Jupiter', value:'08\u00b0 06\u2032 '+S.cancer+' \u00b7 3rd' },
    { mark:G.saturn, label:'Saturn', value:'19\u00b0 48\u2032 '+S.pisces+' \u211e \u00b7 11th', rose:true },
    { mark:G.uranus, label:'Uranus', value:'02\u00b0 24\u2032 '+S.gemini+' \u00b7 2nd' },
    { mark:G.neptune, label:'Neptune', value:'29\u00b0 06\u2032 '+S.pisces+' \u211e \u00b7 11th', rose:true },
    { mark:G.pluto, label:'Pluto', value:'00\u00b0 36\u2032 '+S.aquarius+' \u211e \u00b7 10th', rose:true },
    { mark:G.node, label:'North node', value:'14\u00b0 12\u2032 '+S.pisces+' \u00b7 11th' }
  ];
  const feed = [
    { id:'w1', title:'Saturn on the descendant, and what it asked of me', author:'korax', date:'9 Sep',
      votes:14, myVote:0, comments:6, sign:'Capricorn',
      excerpt:'I have had this transit for eleven months and I have spent most of them arguing with it. Here is what changed when I stopped.' },
    { id:'w2', title:'A first attempt at the eclipse chart for Athens', author:'thalassa', date:'9 Sep',
      votes:9, myVote:0, comments:2, sign:'Pisces',
      excerpt:'Whole sign, tropical. I am not confident about the seventh house and would like to be argued with.' },
    { id:'w3', title:'Why I stopped reading the outers in nativities', author:'a very long username indeed', date:'8 Sep',
      votes:31, myVote:1, comments:24, sign:'Aquarius',
      excerpt:'Not a purist position. A practical one, arrived at after four years of noticing what I was actually using.' },
    { id:'w4', title:'Mercury retrograde is not about email', author:'phos', date:'8 Sep',
      votes:22, myVote:0, comments:11, sign:'Virgo',
      excerpt:'The shadow period is the interesting part and almost nobody talks about it.' }
  ];
  const mine = [
    { id:'m1', title:'First pass at the eclipse', date:'8 Sep', status:'draft', votes:0, comments:0,
      excerpt:'Notes, mostly. The angles are doing something I do not understand yet.' },
    { id:'m2', title:'Venus in the twelfth, read three ways', date:'2 Sep', status:'posted', votes:7, comments:3,
      excerpt:'Traditional, modern, and what I actually think.' },
    { id:'m3', title:'On the hour of Saturn', date:'24 Aug', status:'corrected', votes:19, comments:8,
      excerpt:'Corrected 26 Aug: I had the sunrise convention wrong, which moved every hour by nine minutes.' }
  ];
  const comments = [
    { id:'c1', author:'thalassa', date:'9 Sep', votes:5, body:'The eleventh-month framing is the part I want to argue with. Saturn does not ask; it invoices.' },
    { id:'c2', author:'Shruti', date:'9 Sep', votes:12, her:true, body:'It invoices, and then it asks whether you were going to pay it in instalments. Good piece — the descendant reading is doing real work here.' },
    { id:'c3', author:'korax', date:'9 Sep', votes:2, body:'Fair. I will rewrite the third paragraph and repost it as a correction rather than an edit.' }
  ];
  const places = [
    { id:'p1', name:'Athens', region:'Attica, Greece', coords:'37.98\u00b0 N \u00b7 23.73\u00b0 E', tz:'GMT+3' },
    { id:'p2', name:'Athens', region:'Georgia, United States', coords:'33.96\u00b0 N \u00b7 83.38\u00b0 W', tz:'GMT\u22124' },
    { id:'p3', name:'Athina', region:'Attica, Greece \u00b7 same place', coords:'37.98\u00b0 N \u00b7 23.73\u00b0 E', tz:'GMT+3' },
    { id:'p4', name:'Atherton', region:'California, United States', coords:'37.46\u00b0 N \u00b7 122.20\u00b0 W', tz:'GMT\u22127' }
  ];
  const notifications = [
    { id:'n1', kind:'live', title:'Shruti is live', body:'Casting charts for the chat', date:'2 h ago', unread:true },
    { id:'n2', kind:'reply', title:'thalassa replied to your reading', body:'The eleventh-month framing is the part I want to argue with.', date:'5 h ago', unread:true },
    { id:'n3', kind:'sky', title:'Mercury stations direct on Thursday', body:'29\u00b0 Virgo, 04:12 Athens', date:'Yesterday' },
    { id:'n4', kind:'reading', title:'Your weekly readings are up', body:'Twelve signs, written Sunday night', date:'2 days ago' }
  ];
  const licences = [
    { name:'Swiss Ephemeris', version:'2.10.03', licence:'AGPL-3.0' },
    { name:'EB Garamond', version:'2.006', licence:'OFL-1.1' },
    { name:'Commissioner', version:'2.000', licence:'OFL-1.1' },
    { name:'AstroSymbols', version:'1.0 \u00b7 29 glyphs', licence:'OFL-1.1' },
    { name:'Material Symbols', version:'4.0.0', licence:'Apache-2.0' },
    { name:'Astrolabe', version:'1.0.0 (build 214)', licence:'AGPL-3.0' }
  ];
  const isopsephy = [
    { ch:'\u03a3', v:200 }, { ch:'\u03bf', v:70 }, { ch:'\u03c6', v:500 }, { ch:'\u03af', v:10 }, { ch:'\u03b1', v:1 }
  ];
  return { G, S, readings, articles, offers, stations, hours, coming, bodies, aspects, cusps,
    chartTable, feed, mine, comments, places, notifications, licences, isopsephy };
})();
