(() => {
  const canvas = document.querySelector(".research-background");
  const context = canvas.getContext("2d");
  if (!context) return;

  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  const glyphs = "·.:+×*#▦";
  let width = 0;
  let height = 0;
  let time = 0;
  let previousFrame;
  let animationFrame;

  // The phase and domain warp come from the supplied PaperSpine background.
  function field(x, y) {
    const warpedX = x + 32 * Math.sin(y * .0049 + time * .47) + 19 * Math.sin(x * .005 + y * .009 - time * .39);
    const warpedY = y + 29 * Math.cos(x * .0055 - time * .42) + 22 * Math.sin(y * .006 - x * .004 + time * .32);
    return .4 * Math.sin(warpedX * .0121 + warpedY * .0081 + time * .82) * Math.cos(warpedY * .0114 - warpedX * .0055 - time * .45)
      + .31 * Math.sin(warpedX * .0073 - warpedY * .0147 - time * .58)
      + .21 * Math.cos(Math.hypot(warpedX - width * .66, warpedY - height * .78) * .017 - time * .64)
      + .14 * Math.sin(warpedX * .023 + warpedY * .021 + time * .31);
  }

  function draw() {
    context.clearRect(0, 0, width, height);
    context.font = "11px ui-monospace, Consolas, monospace";
    context.textAlign = "center";
    context.textBaseline = "middle";
    const stepX = width > 1600 ? 19 : 15.8;
    for (let y = 22; y < height; y += 19.6) {
      const lower = Math.max(0, Math.min(1, (y / height - .35) / .45));
      const upper = Math.max(0, Math.min(1, (.34 - y / height) / .35));
      for (let x = 12; x < width; x += stepX) {
        const value = field(x, y);
        const side = Math.min(1, Math.abs(x - width / 2) / (width * .395));
        const mask = Math.max(.045, Math.pow(side, 1.25) * .78 + lower * .77 + upper * .35);
        const band = Math.sin(x * .0037 + y * .0095 - time * .47);
        const activity = value * .57 + band * .2 + .35;
        const strength = Math.max(0, Math.min(1, (activity - .2) * 1.52)) * mask;
        if (strength < .13) continue;
        const orange = value > .51 && (x > width * .54 || y > height * .69);
        context.fillStyle = orange
          ? `rgba(219, 91, 42, ${Math.min(.35, strength * .31)})`
          : `rgba(87, 79, 67, ${Math.min(.23, strength * .23)})`;
        context.fillText(glyphs[Math.min(glyphs.length - 1, Math.floor(strength * 8))], x, y);
      }
    }
    if (!width || !height) return;
    const x = width * (.56 + .2 * Math.sin(time * .25));
    const y = height * (.79 + .09 * Math.sin(time * .3));
    const glow = context.createRadialGradient(x, y, 0, x, y, Math.max(160, width * .32));
    glow.addColorStop(0, "#ed6d330d");
    glow.addColorStop(.55, "#ed6d3305");
    glow.addColorStop(1, "#ed6d3300");
    context.fillStyle = glow;
    context.fillRect(0, 0, width, height);
  }

  function resize() {
    const bounds = canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    width = bounds.width;
    height = bounds.height;
    canvas.width = Math.ceil(width * ratio);
    canvas.height = Math.ceil(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    draw();
  }

  function frame(now) {
    previousFrame ??= now;
    const delta = now - previousFrame;
    if (delta >= 31) {
      time += Math.min(delta, 100) * .00085;
      previousFrame = now;
      draw();
    }
    animationFrame = requestAnimationFrame(frame);
  }

  function syncMotion() {
    if (!document.hidden && !reducedMotion.matches) {
      animationFrame ??= requestAnimationFrame(frame);
    } else if (animationFrame !== undefined) {
      cancelAnimationFrame(animationFrame);
      animationFrame = undefined;
      previousFrame = undefined;
    }
  }

  new ResizeObserver(resize).observe(canvas);
  document.addEventListener("visibilitychange", syncMotion);
  reducedMotion.addEventListener("change", syncMotion);
  resize();
  syncMotion();
})();
