/* Sound for Swara Studio, synthesised in the browser: no samples, nothing
 * third-party, nothing fetched.
 *
 * - The tanpura drone: four strings plucked in turn, each rendered once into a
 *   buffer with the jawari's moving formant (the bright buzz that falls from
 *   high harmonics to low as the string rings), after instruments/tanpura.json
 *   (formant from harmonic ~17 down to ~5 over ~2 s; a 4.5 s cycle; slight
 *   detune between the jodi pair). Tuned in JUST INTONATION relative to Sa.
 * - Notes for phrases, exercises and songs: a soft, breathy tone, also in just
 *   intonation relative to Sa unless the visitor chose equal temperament.
 * - Tala sounds (docs: talas.json audio_cues): a clap is audible, a finger
 *   count a quiet tick pitched per finger, a wave a soft low tick, the samam
 *   a little brighter. No synthesised speech: konnakol is shown, not spoken,
 *   until the recorded voice exists (DECISIONS tala §10).
 */

let context: AudioContext | null = null;
let master: GainNode | null = null;

export function ctx(): AudioContext {
  if (!context) {
    const C = (window.AudioContext || (window as any).webkitAudioContext) as typeof AudioContext;
    context = new C({ latencyHint: "interactive" });
    master = context.createGain();
    master.gain.value = 0.9;
    master.connect(context.destination);
  }
  if (context.state === "suspended") void context.resume();
  return context;
}

function out(): GainNode {
  ctx();
  return master!;
}

/* ── the tanpura ─────────────────────────────────────────────────────────── */

const pluckCache = new Map<string, AudioBuffer>();

function renderPluck(hz: number, seconds = 4.2, detuneCents = 0): AudioBuffer {
  const key = `${hz.toFixed(3)}:${detuneCents}`;
  const hit = pluckCache.get(key);
  if (hit) return hit;
  const ac = ctx();
  const rate = ac.sampleRate;
  const n = Math.floor(rate * seconds);
  const buffer = ac.createBuffer(1, n, rate);
  const data = buffer.getChannelData(0);
  const f = hz * Math.pow(2, detuneCents / 1200);
  const nyquist = rate / 2;
  const harmonics = Math.min(28, Math.floor(nyquist / f) - 1);
  const sweep = 2.2;
  const phase = new Float64Array(harmonics + 1);
  for (let h = 1; h <= harmonics; h++) phase[h] = Math.random() * Math.PI * 2;
  /* The formant moves slowly, so the harmonic weights are worked out once per
     block of 128 samples rather than per sample. */
  const weights = new Float64Array(harmonics + 1);
  const inc = new Float64Array(harmonics + 1);
  for (let h = 1; h <= harmonics; h++) inc[h] = (2 * Math.PI * f * h) / rate;
  for (let start = 0; start < n; start += 128) {
    const t = start / rate;
    const centre = 5 + 12 * Math.exp(-t / (sweep / 2.5));          // 17 → 5
    for (let h = 1; h <= harmonics; h++) {
      const d = (h - centre) / 3.2;
      const weak = h === 1 ? 0.35 : 1;                               // the fundamental is weak (tanpura.json)
      weights[h] = (Math.exp(-d * d) * 0.9 + 0.35 / h) * weak / Math.sqrt(h);
    }
    const stop = Math.min(n, start + 128);
    for (let i = start; i < stop; i++) {
      const tt = i / rate;
      let s = 0;
      for (let h = 1; h <= harmonics; h++) {
        s += Math.sin(phase[h]) * weights[h];
        phase[h] += inc[h];
      }
      data[i] = s * Math.exp(-tt * 0.55) * Math.min(1, tt / 0.006) * 0.06;
    }
  }
  pluckCache.set(key, buffer);
  return buffer;
}

export type DroneTuning = "pa" | "ma" | "ni" | "mute";

/** The first string's ratio to madhya Sa: mandra Pa, mandra Ma, mandra Ni (all just), or silent. */
const FIRST: Record<DroneTuning, number | null> = { pa: 3 / 4, ma: 2 / 3, ni: 15 / 16, mute: null };

export class Drone {
  private timer: number | null = null;
  private gain: GainNode | null = null;
  private nextAt = 0;
  private step = 0;
  saHz = 261.63;
  tuning: DroneTuning = "pa";
  volume = 0.6;
  cycle = 4.5;
  get playing() { return this.timer !== null; }

  start(saHz: number, tuning: DroneTuning = this.tuning, volume = this.volume) {
    this.stop();
    const ac = ctx();
    this.saHz = saHz;
    this.tuning = tuning;
    this.volume = volume;
    this.gain = ac.createGain();
    this.gain.gain.value = volume;
    this.gain.connect(out());
    this.nextAt = ac.currentTime + 0.08;
    this.step = 0;
    const tick = () => {
      const now = ctx().currentTime;
      while (this.nextAt < now + 0.4) {
        this.pluck(this.step, this.nextAt);
        this.nextAt += this.cycle / 4;
        this.step = (this.step + 1) % 4;
      }
    };
    tick();
    this.timer = window.setInterval(tick, 100);
  }

  private pluck(i: number, when: number) {
    const ac = ctx();
    /* Strings 1–4: the variable string, the jodi pair (Sa, Sa), and low Sa.
       The drone sits in the singer's own octave: Sa itself and mandra Sa. */
    const ratios = [FIRST[this.tuning], 1, 1, 0.5];
    const ratio = ratios[i];
    if (ratio === null || !this.gain) return;
    /* Keep the drone in a comfortable register whatever Sa is: a flute's Sa
       (E5) is voiced an octave down, as a tanpura for a flautist is. */
    let base = this.saHz;
    while (base > 330) base /= 2;
    const detune = i === 2 ? 2 : 0;
    const src = ac.createBufferSource();
    src.buffer = renderPluck(base * ratio, 4.2, detune);
    const g = ac.createGain();
    g.gain.value = i === 3 ? 0.9 : 1;
    src.connect(g).connect(this.gain);
    src.start(when + (Math.random() * 0.04));
  }

  setVolume(v: number) {
    this.volume = v;
    if (this.gain) this.gain.gain.setTargetAtTime(v, ctx().currentTime, 0.05);
  }

  retune(saHz: number, tuning: DroneTuning) {
    if (this.playing) this.start(saHz, tuning, this.volume);
    else { this.saHz = saHz; this.tuning = tuning; }
  }

  stop() {
    if (this.timer !== null) window.clearInterval(this.timer);
    this.timer = null;
    if (this.gain) {
      const g = this.gain;
      g.gain.setTargetAtTime(0, ctx().currentTime, 0.15);
      window.setTimeout(() => g.disconnect(), 1200);
    }
    this.gain = null;
  }
}

/* ── notes ───────────────────────────────────────────────────────────────── */

let wave: PeriodicWave | null = null;
function voice(): PeriodicWave {
  if (!wave) {
    const ac = ctx();
    const real = new Float32Array([0, 1, 0.32, 0.12, 0.06, 0.03, 0.015]);
    wave = ac.createPeriodicWave(real, new Float32Array(real.length));
  }
  return wave;
}

export interface NoteEvent {
  hz: number;
  at: number;              // AudioContext time
  dur: number;             // seconds
  gamaka?: string | null;  // shapes the pitch (kampita oscillates, jaru slides in)
  fromHz?: number | null;  // the previous note, for a jaru
  upperHz?: number | null; // the note above, for kampita / nokku
  lowerHz?: number | null; // the note below, for odukkal / sphurita
  gain?: number;
}

export function playNote(e: NoteEvent) {
  const ac = ctx();
  const osc = ac.createOscillator();
  osc.setPeriodicWave(voice());
  const g = ac.createGain();
  const peak = (e.gain ?? 0.22);
  const end = e.at + Math.max(0.08, e.dur);
  g.gain.setValueAtTime(0.0001, e.at);
  g.gain.exponentialRampToValueAtTime(peak, e.at + Math.min(0.04, e.dur / 3));
  g.gain.setValueAtTime(peak, Math.max(e.at + 0.04, end - 0.06));
  g.gain.exponentialRampToValueAtTime(0.0001, end + 0.04);
  const f = osc.frequency;
  f.setValueAtTime(e.hz, e.at);
  const up = e.upperHz ?? e.hz * Math.pow(2, 2 / 12);
  const down = e.lowerHz ?? e.hz * Math.pow(2, -2 / 12);
  switch (e.gamaka) {
    case "kampita": {
      /* An oscillation towards the note above, landing where it started. */
      const turns = Math.max(1, Math.round(e.dur * 5));
      const span = (end - e.at) / turns;
      for (let i = 0; i < turns; i++) {
        f.setTargetAtTime(up, e.at + i * span + span * 0.1, span / 5);
        f.setTargetAtTime(e.hz, e.at + i * span + span * 0.55, span / 5);
      }
      break;
    }
    case "jaru-up":
    case "jaru-down":
      f.setValueAtTime(e.fromHz ?? (e.gamaka === "jaru-up" ? down : up), e.at);
      f.linearRampToValueAtTime(e.hz, e.at + Math.min(0.35, e.dur * 0.6));
      break;
    case "nokku":
      f.setValueAtTime(up, e.at);
      f.linearRampToValueAtTime(e.hz, e.at + 0.07);
      break;
    case "odukkal":
    case "sphurita":
      f.setValueAtTime(down, e.at);
      f.linearRampToValueAtTime(e.hz, e.at + 0.07);
      break;
    case "pratyahata":
    case "ravai":
      f.setValueAtTime(e.hz, e.at);
      f.linearRampToValueAtTime(up, e.at + 0.05);
      f.linearRampToValueAtTime(e.hz, e.at + 0.1);
      break;
    case "orikkai":
      f.setValueAtTime(e.hz, end - 0.09);
      f.linearRampToValueAtTime(up, end - 0.02);
      break;
  }
  osc.connect(g).connect(out());
  osc.start(e.at);
  osc.stop(end + 0.1);
}

/* ── tala sounds ─────────────────────────────────────────────────────────── */

const FINGER_PITCH: Record<string, number> = { little: 1320, ring: 1480, middle: 1660, index: 1760, thumb: 1980 };

export function talaSound(kind: "clap" | "finger" | "wave" | "silent", at: number, opts: { samam?: boolean; finger?: string } = {}) {
  if (kind === "silent") return;
  const ac = ctx();
  const g = ac.createGain();
  g.connect(out());
  if (kind === "clap") {
    const n = Math.floor(ac.sampleRate * 0.09);
    const buf = ac.createBuffer(1, n, ac.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (n / 6));
    const src = ac.createBufferSource();
    src.buffer = buf;
    const bp = ac.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = opts.samam ? 1600 : 1200;
    bp.Q.value = 0.9;
    g.gain.value = opts.samam ? 0.9 : 0.6;
    src.connect(bp).connect(g);
    src.start(at);
    return;
  }
  const osc = ac.createOscillator();
  osc.type = "sine";
  osc.frequency.value = kind === "wave" ? 420 : FINGER_PITCH[opts.finger ?? "little"] ?? 1400;
  g.gain.setValueAtTime(0.0001, at);
  g.gain.exponentialRampToValueAtTime(kind === "wave" ? 0.12 : 0.06, at + 0.005);
  g.gain.exponentialRampToValueAtTime(0.0001, at + (kind === "wave" ? 0.12 : 0.05));
  osc.connect(g);
  osc.start(at);
  osc.stop(at + 0.15);
}

/** A short pitch cue (the trainer's konnakol stand-in and the quiz's answer tone). */
export function blip(hz: number, at: number, dur = 0.08, level = 0.08) {
  const ac = ctx();
  const osc = ac.createOscillator();
  const g = ac.createGain();
  osc.frequency.value = hz;
  g.gain.setValueAtTime(0.0001, at);
  g.gain.exponentialRampToValueAtTime(level, at + 0.005);
  g.gain.exponentialRampToValueAtTime(0.0001, at + dur);
  osc.connect(g).connect(out());
  osc.start(at);
  osc.stop(at + dur + 0.02);
}
