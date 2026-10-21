// Efectos de sonido sintetizados con Web Audio (sin archivos externos = sin problemas de licencia).
let ctx = null;

export function unlockAudio() {
  ctx ??= new (window.AudioContext || window.webkitAudioContext)();
  if (ctx.state === "suspended") ctx.resume();
}

function tone({ freq = 440, to = freq, type = "square", dur = 0.15, vol = 0.2, delay = 0 }) {
  if (!ctx) return;
  const t = ctx.currentTime + delay;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, t);
  osc.frequency.exponentialRampToValueAtTime(Math.max(to, 1), t + dur);
  gain.gain.setValueAtTime(vol, t);
  gain.gain.exponentialRampToValueAtTime(0.001, t + dur);
  osc.connect(gain).connect(ctx.destination);
  osc.start(t);
  osc.stop(t + dur + 0.02);
}

function noise({ dur = 0.4, vol = 0.4, cutoff = 900 }) {
  if (!ctx) return;
  const t = ctx.currentTime;
  const buf = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);
  const src = ctx.createBufferSource();
  src.buffer = buf;
  const filter = ctx.createBiquadFilter();
  filter.type = "lowpass";
  filter.frequency.value = cutoff;
  const gain = ctx.createGain();
  gain.gain.value = vol;
  src.connect(filter).connect(gain).connect(ctx.destination);
  src.start(t);
}

export const sfx = {
  click: () => tone({ freq: 660, to: 880, dur: 0.06, vol: 0.12 }),
  pop: () => tone({ freq: 300, to: 700, type: "triangle", dur: 0.12, vol: 0.15 }),
  bonk: (combo = 0) => {
    tone({ freq: 520 + combo * 30, to: 120, dur: 0.18, vol: 0.25 });
    tone({ freq: 1200 + combo * 60, to: 900, type: "triangle", dur: 0.08, vol: 0.1, delay: 0.02 });
  },
  whiff: () => tone({ freq: 240, to: 160, type: "sawtooth", dur: 0.12, vol: 0.08 }),
  boom: () => { noise({ dur: 0.6, vol: 0.6, cutoff: 700 }); tone({ freq: 120, to: 40, type: "sine", dur: 0.5, vol: 0.4 }); },
  start: () => [523, 659, 784, 1047].forEach((f, i) => tone({ freq: f, dur: 0.12, vol: 0.15, delay: i * 0.09 })),
  end: () => [784, 659, 523, 392].forEach((f, i) => tone({ freq: f, type: "triangle", dur: 0.2, vol: 0.18, delay: i * 0.14 })),
};

export function vibrate(pattern) {
  if (navigator.vibrate) navigator.vibrate(pattern);
}
