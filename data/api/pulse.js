/*
 * Кардиомонитор группы: динозаврик бежит по линии пульса и прыгает через пики.
 *
 * Отдаётся сервером только по одноразовому токену (/miniapp/pulse/ecg.js?t=...),
 * поэтому в miniapp.html этого кода нет. Во время забега каждые BEAT_INTERVAL_MS
 * счёт уходит «ударом» на /miniapp/pulse/ecg/<токен>/beat: сервер сам замеряет время
 * между ударами и проверяет темп. Итог забега — на /miniapp/pulse/ecg/<токен>.
 */
(() => {
  const trace = new URL(document.currentScript.src).searchParams.get('t');
  const tg = window.Telegram?.WebApp;

  // === Константы мира (логические пиксели и миллисекунды) ===
  const W = 600;
  const H = 180;
  const GROUND = 140;
  const GRAVITY = 0.0028;
  const JUMP_VELOCITY = -0.82;
  const START_SPEED = 0.3;
  const MAX_SPEED = 0.6;
  // Очки за миллисекунду на стартовой скорости (~10 в секунду, сервер ждёт не больше 30)
  const POINTS_PER_MS = 0.01;
  // Шаг ударов кардиограммы; сервер обрывает забег после паузы дольше 6 секунд
  const BEAT_INTERVAL_MS = 2000;
  const PIXEL = 3;

  // Свой пиксельный динозавр, два кадра бега (# — закрашено)
  const DINO_FRAMES = [
    [
      '.....######',
      '....##.####',
      '....#######',
      '....####...',
      '#...######.',
      '##.#####...',
      '########...',
      '.#######...',
      '..#####....',
      '...#..##...',
      '...#.......',
      '...##......',
    ],
    [
      '.....######',
      '....##.####',
      '....#######',
      '....####...',
      '#...######.',
      '##.#####...',
      '########...',
      '.#######...',
      '..#####....',
      '...##.#....',
      '......#....',
      '......##...',
    ],
  ];
  const DINO_W = DINO_FRAMES[0][0].length * PIXEL;
  const DINO_H = DINO_FRAMES[0].length * PIXEL;
  const DINO_X = 48;

  // === Разметка монитора ===
  const overlay = document.createElement('div');
  overlay.id = 'pulse-monitor';
  overlay.style.cssText =
    'position:fixed;inset:0;z-index:9999;background:rgba(2,6,10,.94);display:flex;flex-direction:column;' +
    'align-items:center;justify-content:center;padding:16px;font-family:monospace;color:#22c55e;touch-action:none;';
  overlay.innerHTML = `
    <div style="width:100%;max-width:640px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
      <span style="font-size:12px;letter-spacing:2px;">МОНИТОР • 1-КПД-3</span>
      <button id="pulse-close" style="background:none;border:1px solid #14532d;color:#22c55e;border-radius:8px;padding:4px 10px;font-size:14px;">✕</button>
    </div>
    <canvas id="pulse-canvas" style="width:100%;max-width:640px;border:1px solid #14532d;border-radius:12px;background:#020a06;"></canvas>
    <div id="pulse-note" style="max-width:640px;margin-top:10px;font-size:12px;color:#4ade80;text-align:center;min-height:32px;">
      Тап или пробел — прыжок
    </div>`;
  document.body.appendChild(overlay);

  const canvas = overlay.querySelector('#pulse-canvas');
  const note = overlay.querySelector('#pulse-note');
  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 3);
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  ctx.scale(dpr, dpr);

  const best = () => Number(localStorage.getItem('para_pulse_best') || 0);

  // === Состояние забега ===
  let state = 'ready';
  let dino;
  let spikes;
  let speed;
  let score;
  let nextSpikeIn;
  let gridOffset;
  let deadAt = 0;
  let lastTs = 0;
  let lastBeatAt = 0;
  let rafId = 0;

  function resetRun() {
    dino = { y: GROUND - DINO_H, vy: 0, frameTime: 0, frame: 0 };
    spikes = [];
    speed = START_SPEED;
    score = 0;
    nextSpikeIn = 500;
    gridOffset = 0;
    lastBeatAt = performance.now();
  }

  // Пик кардиограммы: иногда сдвоенный, чтобы прыжки не были одинаковыми
  function spawnSpike() {
    const width = 14 + Math.random() * 10;
    const height = 28 + Math.random() * 28;
    spikes.push({ x: W + 10, width, height });
    if (Math.random() < 0.25) spikes.push({ x: W + 10 + width + 6, width: width * 0.8, height: height * 0.7 });
    nextSpikeIn = (520 + Math.random() * 520) * (START_SPEED / speed) + 200;
  }

  function jump() {
    if (state === 'ready') {
      state = 'running';
      note.textContent = '';
    }
    if (state === 'dead' && performance.now() - deadAt > 600) {
      resetRun();
      state = 'running';
      note.textContent = '';
      return;
    }
    if (state === 'running' && dino.y >= GROUND - DINO_H - 0.5) {
      dino.vy = JUMP_VELOCITY;
      if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
    }
  }

  // Хитбокс пика уже треугольника — чтобы задевание краем не казалось нечестным
  function hits(spike) {
    const dinoLeft = DINO_X + 6;
    const dinoRight = DINO_X + DINO_W - 6;
    const spikeLeft = spike.x + spike.width * 0.3;
    const spikeRight = spike.x + spike.width * 0.7;
    const overlapX = dinoRight > spikeLeft && dinoLeft < spikeRight;
    return overlapX && dino.y + DINO_H - 4 > GROUND - spike.height * 0.85;
  }

  function update(dt) {
    speed = Math.min(MAX_SPEED, speed + dt * 0.000004);
    score += dt * POINTS_PER_MS * (speed / START_SPEED);
    gridOffset = (gridOffset + speed * dt) % 20;
    dino.vy += GRAVITY * dt;
    dino.y = Math.min(GROUND - DINO_H, dino.y + dino.vy * dt);
    dino.frameTime += dt;
    if (dino.frameTime > 110) {
      dino.frameTime = 0;
      dino.frame ^= 1;
    }
    spikes.forEach((s) => (s.x -= speed * dt));
    spikes = spikes.filter((s) => s.x + s.width > -10);
    nextSpikeIn -= dt;
    if (nextSpikeIn <= 0) spawnSpike();
    if (spikes.some(hits)) die();
  }

  // === Отрисовка ===
  function drawGrid() {
    ctx.strokeStyle = 'rgba(34,197,94,0.08)';
    ctx.lineWidth = 1;
    for (let x = -gridOffset; x < W; x += 20) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (let y = 0; y < H; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
  }

  // Линия пульса: ровная изолиния, на которой пики — это и есть препятствия
  function drawTrace() {
    ctx.strokeStyle = state === 'dead' ? '#ef4444' : '#22c55e';
    ctx.lineWidth = 2;
    ctx.shadowColor = ctx.strokeStyle;
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.moveTo(0, GROUND);
    spikes.forEach((s) => {
      ctx.lineTo(s.x, GROUND);
      ctx.lineTo(s.x + s.width * 0.35, GROUND + 8);
      ctx.lineTo(s.x + s.width * 0.5, GROUND - s.height);
      ctx.lineTo(s.x + s.width * 0.65, GROUND + 12);
      ctx.lineTo(s.x + s.width, GROUND);
    });
    ctx.lineTo(W, GROUND);
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  function drawDino() {
    const rows = DINO_FRAMES[state === 'running' && dino.y >= GROUND - DINO_H - 0.5 ? dino.frame : 0];
    ctx.fillStyle = state === 'dead' ? '#f87171' : '#86efac';
    rows.forEach((row, ry) => {
      [...row].forEach((cell, rx) => {
        if (cell === '#') ctx.fillRect(DINO_X + rx * PIXEL, dino.y + ry * PIXEL, PIXEL, PIXEL);
      });
    });
  }

  function drawHud() {
    ctx.fillStyle = '#4ade80';
    ctx.font = '14px monospace';
    ctx.textAlign = 'right';
    ctx.fillText(`♥ ${String(Math.floor(score)).padStart(5, '0')}`, W - 12, 22);
    ctx.fillStyle = 'rgba(74,222,128,0.5)';
    ctx.fillText(`рекорд ${String(best()).padStart(5, '0')}`, W - 12, 40);
    if (state !== 'running') {
      ctx.textAlign = 'center';
      ctx.fillStyle = state === 'dead' ? '#ef4444' : '#4ade80';
      ctx.font = '16px monospace';
      ctx.fillText(state === 'dead' ? 'АСИСТОЛИЯ' : 'ПУЛЬС ПОТЕРЯН', W / 2, 60);
      ctx.font = '12px monospace';
      ctx.fillText(state === 'dead' ? 'тап — реанимация' : 'тап — запустить сердце', W / 2, 80);
    }
  }

  function render() {
    ctx.clearRect(0, 0, W, H);
    drawGrid();
    drawTrace();
    drawDino();
    drawHud();
  }

  // Удар идёт из цикла отрисовки, а не таймера: на свёрнутой вкладке игра стоит — и удары тоже
  function sendBeat(ts) {
    if (state !== 'running' || ts - lastBeatAt < BEAT_INTERVAL_MS) return;
    lastBeatAt = ts;
    fetch(`/miniapp/pulse/ecg/${encodeURIComponent(trace)}/beat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score: Math.floor(score) }),
      credentials: 'include',
    }).catch((err) => console.warn('pulse beat:', err));
  }

  function frame(ts) {
    const dt = Math.min(50, ts - (lastTs || ts));
    lastTs = ts;
    if (state === 'running') update(dt);
    sendBeat(ts);
    render();
    rafId = requestAnimationFrame(frame);
  }

  // === Итог забега ===
  function die() {
    state = 'dead';
    deadAt = performance.now();
    const final = Math.floor(score);
    if (final > best()) localStorage.setItem('para_pulse_best', String(final));
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('error');
    reportScore(final);
  }

  async function reportScore(final) {
    try {
      const resp = await fetch(`/miniapp/pulse/ecg/${encodeURIComponent(trace)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ score: final }),
        credentials: 'include',
      });
      if (!resp.ok) return;
      const res = await resp.json();
      if (res.unlocked) celebrate(res);
    } catch (err) {
      console.warn('pulse:', err);
    }
  }

  function celebrate(res) {
    note.innerHTML = `${res.icon} <b>${res.title}</b> — +${res.xp} XP<br>Об этом достижении не знает никто. Пусть так и останется 🤫`;
    if (typeof window.showToast === 'function') window.showToast(`${res.icon} <b>${res.title}</b> (+${res.xp} XP)`);
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
  }

  // === Управление и закрытие ===
  const onKey = (e) => {
    if (e.code === 'Space' || e.code === 'ArrowUp') {
      e.preventDefault();
      jump();
    }
    if (e.code === 'Escape') close();
  };
  const onPointer = (e) => {
    if (e.target.id !== 'pulse-close') jump();
  };

  function close() {
    cancelAnimationFrame(rafId);
    window.removeEventListener('keydown', onKey);
    overlay.remove();
    if (typeof window.restorePulse === 'function') window.restorePulse();
  }

  overlay.querySelector('#pulse-close').addEventListener('click', close);
  overlay.addEventListener('pointerdown', onPointer);
  window.addEventListener('keydown', onKey);

  resetRun();
  rafId = requestAnimationFrame(frame);
})();
