import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MindARThree } from "mindar-image-three";
import { sfx, unlockAudio, vibrate } from "./sfx.js";

// ---------------------------------------------------------------- reglas del juego
const GAME_TIME = 45;     // segundos
const LIVES = 3;
const POINTS = 10;
const HOLE_X = [-0.3, 0, 0.3];   // igual que en blender/build_models.py
const CHAR_HEIGHT = 0.3;
const UP_Y = -0.04, DOWN_Y = -0.36;

const $ = (id) => document.getElementById(id);
const ui = {
  hud: $("hud"), score: $("score"), time: $("time"), lives: $("lives"), combo: $("combo"),
  pads: $("pads"), hint: $("hint"), intro: $("intro"), over: $("over"), play: $("play"),
  again: $("again"), status: $("status"),
};

// ---------------------------------------------------------------- escena AR
const mindar = new MindARThree({
  container: $("ar"),
  imageTargetSrc: "./assets/marker/marker.mind",
  uiScanning: "no",
  uiLoading: "no",
  filterMinCF: 0.0001, // suavizado del rastreo (menos temblor)
  filterBeta: 0.001,
});
const { renderer, scene, camera } = mindar;
scene.add(new THREE.HemisphereLight(0xffffff, 0x556655, 2.4));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(0.5, 1, 1.2);
scene.add(sun);

const anchor = mindar.addAnchor(0);
const world = new THREE.Group();       // la isla "se para" sobre el marcador
world.rotation.x = Math.PI / 2;
world.position.y = -0.05;
anchor.group.add(world);

let tracking = false;
anchor.onTargetFound = () => { tracking = true; refreshHint(); };
anchor.onTargetLost = () => { tracking = false; refreshHint(); };

// ?demo: muestra la isla frente a la camara sin marcador (para probar en la compu y tomar capturas)
if (new URLSearchParams(location.search).has("demo")) {
  const demo = new THREE.Group();
  demo.scale.setScalar(1000);              // MindAR trabaja en pixeles del marcador (near = 10)
  demo.position.set(0, -120, -2600);
  demo.rotation.x = -1.05;
  demo.add(world);
  scene.add(demo);
  tracking = true;
  anchor.onTargetLost = () => {};
}

// ---------------------------------------------------------------- modelos
const loader = new GLTFLoader();
const load = (url) => loader.loadAsync(url);

function fitHeight(obj, h) {
  const size = new THREE.Box3().setFromObject(obj).getSize(new THREE.Vector3());
  obj.scale.multiplyScalar(h / size.y);
}

const slots = [];      // un hoyo = un slot
const mixers = [];
let hammer;

async function loadModels() {
  const [island, tnt, ham, ...chars] = await Promise.all([
    load("assets/models/island.glb"),
    load("assets/models/tnt.glb"),
    load("assets/models/hammer.glb"),
    load("assets/models/kenney/character-a.glb"),
    load("assets/models/kenney/character-e.glb"),
    load("assets/models/kenney/character-k.glb"),
  ]);
  world.add(island.scene);

  hammer = ham.scene;
  hammer.visible = false;
  world.add(hammer);

  HOLE_X.forEach((x, i) => {
    const slot = { i, x, kind: null, obj: null, phase: "down", t: 0, upTime: 1, hit: false, chars: [] };

    for (const gltf of chars) {
      const c = gltf.scene.clone();
      fitHeight(c, CHAR_HEIGHT);
      c.position.set(x, DOWN_Y, 0);
      c.visible = false;
      const mixer = new THREE.AnimationMixer(c);
      const clip = (name) => mixer.clipAction(THREE.AnimationClip.findByName(gltf.animations, name));
      c.userData.anim = { idle: clip("idle"), die: clip("die"), yes: clip("emote-yes") };
      c.userData.anim.die.setLoop(THREE.LoopOnce).clampWhenFinished = true;
      mixers.push(mixer);
      world.add(c);
      slot.chars.push(c);
    }

    slot.tnt = tnt.scene.clone();
    fitHeight(slot.tnt, 0.2);
    slot.tnt.position.set(x, DOWN_Y, 0);
    slot.tnt.visible = false;
    world.add(slot.tnt);

    // caja invisible para que sea facil tocar el hoyo
    const hit = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.4, 0.3), new THREE.MeshBasicMaterial({ visible: false }));
    hit.position.set(x, 0.12, 0);
    hit.userData.slot = i;
    world.add(hit);
    slot.hitbox = hit;

    slots.push(slot);
  });
}

// ---------------------------------------------------------------- particulas
const particles = [];
const partGeo = new THREE.BoxGeometry(0.025, 0.025, 0.025);
for (let i = 0; i < 80; i++) {
  const m = new THREE.Mesh(partGeo, new THREE.MeshBasicMaterial());
  m.visible = false;
  world.add(m);
  particles.push({ m, v: new THREE.Vector3(), life: 0 });
}

function burst(x, y, colors, n = 14, speed = 0.9) {
  let made = 0;
  for (const p of particles) {
    if (p.life > 0) continue;
    p.life = 0.5 + Math.random() * 0.3;
    p.m.visible = true;
    p.m.position.set(x, y, 0);
    p.m.scale.setScalar(1);
    p.m.material.color.set(colors[made % colors.length]);
    p.v.set((Math.random() - 0.5) * speed, Math.random() * speed + 0.4, (Math.random() - 0.5) * speed);
    if (++made >= n) break;
  }
}

function updateParticles(dt) {
  for (const p of particles) {
    if (p.life <= 0) continue;
    p.life -= dt;
    p.v.y -= 2.2 * dt;
    p.m.position.addScaledVector(p.v, dt);
    p.m.rotation.x += dt * 8;
    p.m.scale.setScalar(Math.max(p.life * 2, 0.01));
    if (p.life <= 0) p.m.visible = false;
  }
}

// ---------------------------------------------------------------- martillo
let hammerT = -1, hammerX = 0;
function swingHammer(x) {
  hammerX = x;
  hammerT = 0;
  hammer.visible = true;
}
function updateHammer(dt) {
  if (hammerT < 0) return;
  hammerT += dt;
  const k = Math.min(hammerT / 0.1, 1);              // 0.1 s de golpe
  hammer.position.set(hammerX + 0.24, 0.02, 0.02);
  hammer.rotation.z = THREE.MathUtils.lerp(0.2, 1.35, k * k);
  if (hammerT > 0.3) { hammer.visible = false; hammerT = -1; }
}

// ---------------------------------------------------------------- texto flotante (DOM)
const tmp = new THREE.Vector3();
function floatText(slot, text, color) {
  tmp.set(slot.x, 0.25, 0);
  world.localToWorld(tmp).project(camera);
  const r = renderer.domElement.getBoundingClientRect();
  const el = document.createElement("div");
  el.className = "float";
  el.textContent = text;
  el.style.color = color;
  el.style.left = `${r.left + (tmp.x + 1) / 2 * r.width - 30}px`;
  el.style.top = `${r.top + (1 - tmp.y) / 2 * r.height}px`;
  document.body.append(el);
  setTimeout(() => el.remove(), 800);
}

// ---------------------------------------------------------------- estado del juego
let state = "intro";   // intro | playing | over
let game;

function newGame() {
  game = { time: GAME_TIME, score: 0, lives: LIVES, combo: 0, hits: 0, taps: 0, escapes: 0, spawn: 0.8 };
  for (const s of slots) clearSlot(s);
  renderHud();
}

function clearSlot(s) {
  if (s.obj) s.obj.visible = false;
  Object.assign(s, { kind: null, obj: null, phase: "down", t: 0, hit: false });
}

function spawn() {
  const free = slots.filter((s) => s.phase === "down");
  if (!free.length) return;
  const s = free[Math.floor(Math.random() * free.length)];
  const progress = 1 - game.time / GAME_TIME;
  const isTnt = Math.random() < 0.18 + 0.12 * progress;
  s.kind = isTnt ? "tnt" : "char";
  s.obj = isTnt ? s.tnt : s.chars[Math.floor(Math.random() * s.chars.length)];
  s.obj.visible = true;
  s.obj.position.y = DOWN_Y;
  s.phase = "rising";
  s.t = 0;
  s.hit = false;
  s.upTime = 1.4 - 0.65 * progress;
  if (s.kind === "char") {
    const a = s.obj.userData.anim;
    a.die.stop();
    a.idle.reset().play();
  }
  sfx.pop();
}

function updateSlots(dt) {
  for (const s of slots) {
    if (s.phase === "down") continue;
    s.t += dt;
    const top = s.kind === "tnt" ? 0 : UP_Y;
    if (s.phase === "rising") {
      s.obj.position.y = THREE.MathUtils.lerp(DOWN_Y, top, Math.min(s.t / 0.15, 1));
      if (s.t >= 0.15) { s.phase = "up"; s.t = 0; }
    } else if (s.phase === "up") {
      if (s.t >= s.upTime) {
        if (s.kind === "char" && !s.hit) { game.escapes++; game.combo = 0; renderHud(); }
        s.phase = "sinking"; s.t = 0;
      }
    } else if (s.phase === "sinking") {
      s.obj.position.y = THREE.MathUtils.lerp(top, DOWN_Y, Math.min(s.t / 0.2, 1));
      if (s.t >= 0.2) clearSlot(s);
    }
  }
}

function hitSlot(i) {
  if (state !== "playing" || !tracking) return;
  const s = slots[i];
  const pad = ui.pads.children[i];
  game.taps++;

  if (s.kind && (s.phase === "rising" || s.phase === "up") && !s.hit) {
    s.hit = true;
    if (s.kind === "char") {
      game.combo++;
      game.hits++;
      const mult = Math.min(1 + Math.floor(game.combo / 5), 4);
      game.score += POINTS * mult;
      const a = s.obj.userData.anim;
      a.idle.stop();
      a.die.reset().play();
      s.phase = "up";
      s.t = s.upTime - 0.35;    // se queda un momento "noqueado" y se hunde
      swingHammer(s.x);
      burst(s.x, 0.15, ["#ffc93c", "#ffffff", "#ff4fa3"]);
      sfx.bonk(Math.min(game.combo, 10));
      vibrate(35);
      floatText(s, `+${POINTS * mult}`, "#ffc93c");
      flash(pad, "hit");
    } else {
      game.lives--;
      game.combo = 0;
      s.phase = "sinking";
      s.t = 0;
      burst(s.x, 0.1, ["#ff3b3b", "#ff9f1c", "#222222"], 30, 1.4);
      sfx.boom();
      vibrate([90, 40, 90]);
      floatText(s, "💥 -❤️", "#ff3b3b");
      flash(pad, "bad");
      document.body.classList.add("shake");
      setTimeout(() => document.body.classList.remove("shake"), 350);
      if (game.lives <= 0) endGame();
    }
  } else {
    game.combo = 0;
    sfx.whiff();
    vibrate(10);
    flash(pad, "bad");
  }
  renderHud();
}

function flash(el, cls) {
  el.classList.remove(cls);
  void el.offsetWidth; // reinicia la animacion CSS
  el.classList.add(cls);
  setTimeout(() => el.classList.remove(cls), 300);
}

function renderHud() {
  ui.score.textContent = game.score;
  ui.time.textContent = Math.ceil(game.time);
  ui.time.classList.toggle("low", game.time <= 10);
  ui.lives.textContent = "❤️".repeat(Math.max(game.lives, 0)) + "🖤".repeat(LIVES - Math.max(game.lives, 0));
  const mult = Math.min(1 + Math.floor(game.combo / 5), 4);
  ui.combo.hidden = game.combo < 3;
  ui.combo.textContent = `COMBO ${game.combo}${mult > 1 ? `  ·  x${mult}` : ""}`;
}

function refreshHint() {
  ui.hint.hidden = !(state === "playing" && !tracking);
}

function startGame() {
  unlockAudio();
  sfx.start();
  newGame();
  state = "playing";
  ui.intro.hidden = ui.over.hidden = true;
  ui.hud.hidden = ui.pads.hidden = false;
  refreshHint();
}

function endGame() {
  state = "over";
  sfx.end();
  vibrate([60, 60, 200]);
  for (const s of slots) clearSlot(s);
  ui.hud.hidden = ui.pads.hidden = ui.combo.hidden = true;
  refreshHint();

  let best = 0;
  try {
    best = Math.max(Number(localStorage.getItem("bonk-best")) || 0, game.score);
    localStorage.setItem("bonk-best", best);
  } catch { best = game.score; }

  const acc = game.taps ? Math.round((game.hits / game.taps) * 100) : 0;
  $("over-title").textContent = game.lives <= 0 ? "¡BOOM! SIN CORAZONES" : "¡TIEMPO!";
  $("final-score").textContent = game.score;
  $("final-stats").textContent = `Golpes: ${game.hits} · Precisión: ${acc}% · Se escaparon: ${game.escapes}`;
  $("best").textContent = game.score >= best && game.score > 0 ? "🏆 ¡Nuevo récord!" : `Récord: ${best}`;
  ui.over.hidden = false;
}

function update(dt) {
  if (state !== "playing" || !tracking) return;  // si se pierde el marcador, el juego se pausa
  game.time -= dt;
  game.spawn -= dt;
  if (game.spawn <= 0) {
    spawn();
    const progress = 1 - game.time / GAME_TIME;
    game.spawn = 1.1 - 0.55 * progress;
  }
  updateSlots(dt);
  renderHud();
  if (game.time <= 0) { game.time = 0; endGame(); }
}

// ---------------------------------------------------------------- entrada tactil
for (const pad of ui.pads.children) {
  pad.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    sfx.click();
    hitSlot(Number(pad.dataset.hole));
  });
}

const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
window.addEventListener("pointerdown", (e) => {
  if (state !== "playing" || e.target.closest("button")) return;
  const r = renderer.domElement.getBoundingClientRect();
  ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
  const [hit] = raycaster.intersectObjects(slots.map((s) => s.hitbox));
  if (hit) hitSlot(hit.object.userData.slot);
});

ui.play.addEventListener("click", startGame);
ui.again.addEventListener("click", startGame);

// ---------------------------------------------------------------- arranque
const clock = new THREE.Clock();
try {
  await Promise.all([loadModels(), mindar.start()]);
  ui.status.textContent = "Listo ✔";
  ui.play.disabled = false;
} catch (err) {
  console.error(err);
  ui.status.textContent = "No se pudo abrir la cámara. Abre la página con HTTPS y da permiso de cámara.";
}

renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.1);
  update(dt);
  updateHammer(dt);
  updateParticles(dt);
  for (const m of mixers) m.update(dt);
  renderer.render(scene, camera);
});
