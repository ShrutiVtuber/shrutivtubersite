/* A small QR code encoder (ISO/IEC 18004): byte mode, error correction level
 * M, versions 1–10, one fixed mask chosen by the standard penalty rules. Just
 * enough for the app sign-in link (swarastudio://link?t=…), drawn as an SVG,
 * so no library and nothing third-party is loaded to show it. */

const EC_M: [number, number, number][] = [
  // [ec codewords per block, blocks in group 1, data codewords per block g1] ... simplified table for M
  [10, 1, 16], [16, 1, 28], [26, 1, 44], [18, 2, 32], [24, 2, 43],
  [16, 4, 27], [18, 4, 31], [22, 2, 38], [22, 3, 36], [26, 4, 43],
];
/* Group 2 (blocks, data per block) for versions with two groups, level M. */
const G2_M: Record<number, [number, number]> = { 8: [2, 39], 9: [2, 37], 10: [1, 44] };
const ALIGN: number[][] = [[], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50]];

const EXP = new Uint8Array(512), LOG = new Uint8Array(256);
(() => { let x = 1; for (let i = 0; i < 255; i++) { EXP[i] = x; LOG[x] = i; x <<= 1; if (x & 256) x ^= 0x11d; } for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255]; })();
const mul = (a: number, b: number) => (a && b ? EXP[LOG[a] + LOG[b]] : 0);

function rs(data: number[], n: number): number[] {
  let gen = [1];
  for (let i = 0; i < n; i++) {
    const next = new Array(gen.length + 1).fill(0);
    gen.forEach((g, j) => { next[j] ^= g; next[j + 1] ^= mul(g, EXP[i]); });
    gen = next;
  }
  const res = new Array(n).fill(0);
  for (const d of data) {
    const f = d ^ res.shift()!;
    res.push(0);
    for (let j = 0; j < n; j++) res[j] ^= mul(gen[j + 1], f);
  }
  return res;
}

function blocks(version: number) {
  const [ec, b1, d1] = EC_M[version - 1];
  const [b2, d2] = G2_M[version] ?? [0, 0];
  return { ec, list: [...Array(b1).fill(d1), ...Array(b2).fill(d2)] as number[] };
}

export function qrMatrix(text: string): boolean[][] {
  const bytes = [...new TextEncoder().encode(text)];
  let version = 1;
  for (; version <= 10; version++) {
    const cap = blocks(version).list.reduce((a, b) => a + b, 0);
    if (4 + (version < 10 ? 8 : 16) + bytes.length * 8 <= cap * 8) break;
  }
  if (version > 10) throw new Error("too long for this encoder");
  const { ec, list } = blocks(version);
  const capacity = list.reduce((a, b) => a + b, 0);
  const bits: number[] = [];
  const put = (v: number, n: number) => { for (let i = n - 1; i >= 0; i--) bits.push((v >> i) & 1); };
  put(0b0100, 4); put(bytes.length, version < 10 ? 8 : 16);
  bytes.forEach((b) => put(b, 8));
  put(0, Math.min(4, capacity * 8 - bits.length));
  while (bits.length % 8) bits.push(0);
  const data: number[] = [];
  for (let i = 0; i < bits.length; i += 8) data.push(parseInt(bits.slice(i, i + 8).join(""), 2));
  for (let pad = 0; data.length < capacity; pad++) data.push(pad % 2 ? 0x11 : 0xec);
  const dblocks: number[][] = [], eblocks: number[][] = [];
  let at = 0;
  for (const n of list) { const blk = data.slice(at, at + n); at += n; dblocks.push(blk); eblocks.push(rs(blk, ec)); }
  const out: number[] = [];
  for (let i = 0; i < Math.max(...list); i++) for (const b of dblocks) if (i < b.length) out.push(b[i]);
  for (let i = 0; i < ec; i++) for (const b of eblocks) out.push(b[i]);

  const size = version * 4 + 17;
  const m: (boolean | null)[][] = Array.from({ length: size }, () => Array(size).fill(null));
  const reserved: boolean[][] = Array.from({ length: size }, () => Array(size).fill(false));
  const set = (r: number, c: number, v: boolean) => { m[r][c] = v; reserved[r][c] = true; };
  const finder = (r: number, c: number) => {
    for (let i = -1; i <= 7; i++) for (let j = -1; j <= 7; j++) {
      const rr = r + i, cc = c + j;
      if (rr < 0 || cc < 0 || rr >= size || cc >= size) continue;
      const on = i >= 0 && i <= 6 && j >= 0 && j <= 6 && (i === 0 || i === 6 || j === 0 || j === 6 || (i >= 2 && i <= 4 && j >= 2 && j <= 4));
      set(rr, cc, on);
    }
  };
  finder(0, 0); finder(0, size - 7); finder(size - 7, 0);
  for (let i = 8; i < size - 8; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
  const al = ALIGN[version - 1];
  for (const r of al) for (const c of al) {
    if (reserved[r][c]) continue;
    for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) set(r + i, c + j, Math.max(Math.abs(i), Math.abs(j)) !== 1);
  }
  set(size - 8, 8, true);                                   // the dark module
  for (let i = 0; i < 9; i++) { reserved[8][i] = reserved[i][8] = true; }
  for (let i = 0; i < 8; i++) { reserved[8][size - 1 - i] = reserved[size - 1 - i][8] = true; }
  if (version >= 7) for (let i = 0; i < 6; i++) for (let j = 0; j < 3; j++) { reserved[i][size - 11 + j] = reserved[size - 11 + j][i] = true; }

  const dataBits: number[] = [];
  out.forEach((b) => { for (let i = 7; i >= 0; i--) dataBits.push((b >> i) & 1); });
  const MASK = 0; // (r + c) % 2 === 0
  let k = 0;
  for (let c = size - 1; c > 0; c -= 2) {
    if (c === 6) c--;
    for (let i = 0; i < size; i++) {
      const up = ((c + 1) & 2) === 0;
      const r = up ? size - 1 - i : i;
      for (const cc of [c, c - 1]) {
        if (reserved[r][cc]) continue;
        let bit = k < dataBits.length ? dataBits[k] === 1 : false;
        k++;
        if ((r + cc) % 2 === 0) bit = !bit;
        m[r][cc] = bit;
      }
    }
  }
  /* Format: level M (00), mask 0 → BCH-coded 15 bits. */
  let fmt = (0b00 << 3) | MASK;
  let v = fmt << 10;
  for (let i = 14; i >= 10; i--) if ((v >> i) & 1) v ^= 0x537 << (i - 10);
  fmt = ((fmt << 10) | v) ^ 0x5412;
  const bit = (i: number) => ((fmt >> i) & 1) === 1;
  for (let i = 0; i <= 5; i++) m[8][i] = bit(14 - i);
  m[8][7] = bit(8); m[8][8] = bit(7); m[7][8] = bit(6);
  for (let i = 9; i < 15; i++) m[14 - i][8] = bit(14 - i);
  for (let i = 0; i < 8; i++) m[size - 1 - i][8] = bit(i);
  for (let i = 8; i < 15; i++) m[8][size - 15 + i] = bit(i);
  if (version >= 7) {
    let vv = version << 12;
    for (let i = 17; i >= 12; i--) if ((vv >> i) & 1) vv ^= 0x1f25 << (i - 12);
    const vbits = (version << 12) | vv;
    for (let i = 0; i < 18; i++) { const b = ((vbits >> i) & 1) === 1; m[Math.floor(i / 3)][size - 11 + (i % 3)] = b; m[size - 11 + (i % 3)][Math.floor(i / 3)] = b; }
  }
  return m.map((row) => row.map((x) => Boolean(x)));
}

export function qrSvg(text: string, px = 4): string {
  const m = qrMatrix(text);
  const n = m.length + 8;
  let d = "";
  m.forEach((row, r) => row.forEach((on, c) => { if (on) d += `M${c + 4} ${r + 4}h1v1h-1z`; }));
  return `<svg viewBox="0 0 ${n} ${n}" width="${n * px}" height="${n * px}" role="img" aria-label="QR code" shape-rendering="crispEdges"><rect width="${n}" height="${n}" fill="#fff"/><path d="${d}" fill="#000"/></svg>`;
}
