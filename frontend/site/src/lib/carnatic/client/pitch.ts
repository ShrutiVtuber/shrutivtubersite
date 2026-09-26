/* Pitch from the microphone: the YIN estimator (de Cheveigné & Kawahara
 * 2002) on the analyser's time-domain frames. Enough for a voice or a flute
 * against a drone; the design asks for a trace that shows the gamaka, not a
 * needle that calls a kampita out of tune.
 *
 * The readout is the swara relative to the visitor's Sa. The cents are small
 * and secondary, and measured against EQUAL TEMPERAMENT, labelled as such
 * (DECISIONS §13) — the drone and playback use just intonation.
 */
import { ctx } from "./audio";

export type MicState = "idle" | "asking" | "working" | "denied";

export function yin(buf: Float32Array, rate: number, threshold = 0.12): number | null {
  const half = Math.floor(buf.length / 2);
  let energy = 0;
  for (let i = 0; i < buf.length; i++) energy += buf[i] * buf[i];
  if (energy / buf.length < 1e-5) return null;              // silence
  const d = new Float32Array(half);
  for (let tau = 1; tau < half; tau++) {
    let sum = 0;
    for (let i = 0; i < half; i++) {
      const delta = buf[i] - buf[i + tau];
      sum += delta * delta;
    }
    d[tau] = sum;
  }
  // cumulative mean normalised difference
  let running = 0;
  d[0] = 1;
  for (let tau = 1; tau < half; tau++) {
    running += d[tau];
    d[tau] = running ? (d[tau] * tau) / running : 1;
  }
  const minTau = Math.floor(rate / 1400);                   // ~1.4 kHz ceiling (tara register of a flute)
  const maxTau = Math.min(half - 1, Math.floor(rate / 60));
  let tau = -1;
  for (let t = minTau; t < maxTau; t++) {
    if (d[t] < threshold) {
      while (t + 1 < maxTau && d[t + 1] < d[t]) t++;
      tau = t;
      break;
    }
  }
  if (tau < 0) return null;
  const x0 = d[tau - 1] ?? d[tau], x2 = d[tau + 1] ?? d[tau];
  const denom = 2 * (2 * d[tau] - x2 - x0);
  const better = denom ? tau + (x2 - x0) / denom : tau;
  return rate / better;
}

export class Mic {
  state: MicState = "idle";
  private analyser: AnalyserNode | null = null;
  private stream: MediaStream | null = null;
  private frame = new Float32Array(2048);

  async start(): Promise<MicState> {
    if (!navigator.mediaDevices?.getUserMedia) return (this.state = "denied");
    this.state = "asking";
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false },
      });
    } catch {
      return (this.state = "denied");
    }
    const ac = ctx();
    const src = ac.createMediaStreamSource(this.stream);
    this.analyser = ac.createAnalyser();
    this.analyser.fftSize = 2048;
    src.connect(this.analyser);                               // never to the speakers
    return (this.state = "working");
  }

  read(): number | null {
    if (!this.analyser) return null;
    this.analyser.getFloatTimeDomainData(this.frame);
    return yin(this.frame, this.analyser.context.sampleRate);
  }

  stop() {
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    this.analyser = null;
    this.state = "idle";
  }
}

/* Names by semitone above Sa, the common enharmonic first. */
export const SEMITONE_NAMES = ["S", "R1", "R2", "G2", "G3", "M1", "M2", "P", "D1", "D2", "N2", "N3"];
export const ENHARMONIC: Record<number, string> = { 2: "G1", 3: "R3", 9: "N1", 10: "D3" };
const OCTAVE = ["anumandra", "mandra", "madhya", "tara", "ati-tara"];

export function readSwara(hz: number, saHz: number) {
  const semis = 12 * Math.log2(hz / saHz);
  const nearest = Math.round(semis);
  const cents = Math.round((semis - nearest) * 100);         // vs equal temperament
  const within = ((nearest % 12) + 12) % 12;
  const octave = Math.floor(nearest / 12);
  return { semis, nearest, within, name: SEMITONE_NAMES[within], octave, octaveWord: OCTAVE[octave + 2] ?? "", cents };
}
