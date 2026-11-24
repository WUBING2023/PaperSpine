(() => {
  const palette = ".,'\":-^=+";
  const topographyPalette = ' .:-=+*#%@';
  const frameInterval = 1000 / 24;
  const phaseRate = 1.4;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');

  // Value noise breaks up the spiral arms, as in the original ASCII demo.
  function hash(x, y) {
    const value = Math.sin(x * 127.1 + y * 311.7) * 43758.5453123;
    return value - Math.floor(value);
  }

  function valueNoise(x, y) {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    const fx = x - ix;
    const fy = y - iy;
    const u = fx * fx * (3 - 2 * fx);
    const v = fy * fy * (3 - 2 * fy);
    return (hash(ix, iy) * (1 - u) + hash(ix + 1, iy) * u) * (1 - v)
      + (hash(ix, iy + 1) * (1 - u) + hash(ix + 1, iy + 1) * u) * v;
  }

  function drawVortex(vortex) {
    const { context, width, height, phase } = vortex;
    context.clearRect(0, 0, width, height);
    context.font = '10px Consolas, monospace';
    context.textBaseline = 'top';

    const centerX = width * 0.66;
    const centerY = height * 0.47;
    const scale = Math.min(width, height) * 0.55;
    const threshold = 0.51;

    for (let y = 0; y < height; y += 10) {
      for (let x = 0; x < width; x += 7) {
        const dx = (x - centerX) / scale;
        const dy = (y - centerY) / scale;
        const radius = Math.hypot(dx, dy);
        const angle = Math.atan2(dy, dx);
        const logRadius = Math.log(radius + 0.06);
        const depth = logRadius + phase * (0.55 / 1.15);
        const arm = Math.sin(angle * 3 + logRadius * 3.4 + phase) * 0.5 + 0.5;
        const ring = Math.sin(depth * 4.2 - angle) * 0.5 + 0.5;
        const noise = valueNoise(Math.cos(angle) * 2.2 + depth * 1.4, Math.sin(angle) * 2.2 + depth * 1.4);
        const eye = Math.min(1, radius * 3.5);
        const density = (arm * 0.56 + ring * 0.22 + noise * 0.42) * (0.62 + 0.55 * noise) * eye;
        if (density <= threshold) continue;

        const intensity = Math.min(1, (density - threshold) / (1 - threshold));
        const index = Math.min(palette.length - 1, Math.floor(intensity * palette.length));
        context.fillStyle = `rgba(80, 80, 80, ${0.14 + intensity * 0.54})`;
        context.fillText(palette[index], x, y);
      }
    }
  }

  // The workshop's contour effect uses a radial wave across an ASCII grid.
  function drawTopography({ context, width, height, phase, pointer }) {
    context.clearRect(0, 0, width, height);
    context.font = '10px Consolas, monospace';
    context.textBaseline = 'top';

    const cellWidth = 9;
    const cellHeight = 12;
    const centerColumn = width / cellWidth * 0.68;
    const centerRow = height / cellHeight * 0.46;
    for (let y = 0; y < height; y += cellHeight) {
      for (let x = 0; x < width; x += cellWidth) {
        const radius = Math.hypot(x / cellWidth - centerColumn, (y / cellHeight - centerRow) * 1.4);
        let intensity = (Math.sin(radius * 0.48 - phase) + 1) * 0.5;
        if (pointer) {
          const distance = Math.hypot(x - pointer.x, y - pointer.y);
          intensity = Math.min(1, intensity + Math.max(0, 1 - distance / 80) * 0.35);
        }

        const index = Math.floor(intensity * (topographyPalette.length - 1));
        if (index === 0) continue;
        context.fillStyle = `rgba(72, 72, 72, ${0.10 + intensity * 0.42})`;
        context.fillText(topographyPalette[index], x, y);
      }
    }
  }

  function resize(effect) {
    const { canvas, context } = effect;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (!width || !height) return;
    effect.width = width;
    effect.height = height;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    effect.draw(effect);
  }

  window.mountContributorCardEffects = function mountContributorCardEffects(root) {
    const effects = new Map();
    const events = new AbortController();
    for (const canvas of root.querySelectorAll('.card-effect')) {
      const context = canvas.getContext('2d');
      if (!context) continue;
      const card = canvas.parentElement;
      const topography = canvas.dataset.cardEffect === 'topography';
      const effect = {
        canvas, card, context,
        phase: effects.size * 1.7,
        draw: topography ? drawTopography : drawVortex,
        speed: 1,
        visible: false,
        pointer: null
      };
      if (topography) {
        card.addEventListener('pointermove', event => {
          const bounds = canvas.getBoundingClientRect();
          effect.pointer = { x: event.clientX - bounds.left, y: event.clientY - bounds.top };
        }, { signal: events.signal });
        card.addEventListener('pointerleave', () => { effect.pointer = null; }, { signal: events.signal });
      }
      effects.set(canvas, effect);
      resize(effect);
    }
    if (!effects.size) return;

    let frame = 0;
    let lastDraw = null;
    function update(now) {
      frame = requestAnimationFrame(update);
      if (lastDraw === null) lastDraw = now - frameInterval;
      const elapsed = now - lastDraw;
      if (elapsed < frameInterval - 1) return;
      lastDraw = now;

      for (const effect of effects.values()) {
        if (!effect.visible || !effect.width) continue;
        const seconds = Math.min(elapsed / 1000, 0.08);
        const targetSpeed = effect.card.matches(':hover, :focus-visible') ? 2.8 : 1;
        effect.speed += (targetSpeed - effect.speed) * (1 - Math.exp(-seconds / 0.16));
        effect.phase += seconds * phaseRate * effect.speed;
        effect.draw(effect);
      }
    }

    function updatePlayback() {
      const shouldPlay = !motion.matches && [...effects.values()].some(effect => effect.visible);
      if (shouldPlay && !frame) frame = requestAnimationFrame(update);
      if (!shouldPlay && frame) {
        cancelAnimationFrame(frame);
        frame = 0;
        lastDraw = null;
      }
    }

    const visibility = new IntersectionObserver(entries => {
      for (const entry of entries) effects.get(entry.target).visible = entry.isIntersecting;
      updatePlayback();
    });
    const size = new ResizeObserver(entries => {
      for (const entry of entries) resize(effects.get(entry.target));
    });
    for (const canvas of effects.keys()) {
      visibility.observe(canvas);
      size.observe(canvas);
    }
    motion.addEventListener('change', updatePlayback);

    return () => {
      cancelAnimationFrame(frame);
      events.abort();
      visibility.disconnect();
      size.disconnect();
      motion.removeEventListener('change', updatePlayback);
    };
  };
})();
