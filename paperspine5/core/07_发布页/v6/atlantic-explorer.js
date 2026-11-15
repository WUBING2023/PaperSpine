const EARLY = "#82d7ef";
const LATE = "#ffad7c";
const PERIOD_COLORS = [EARLY, LATE];
const TRACKS = "#e6f6f4";
const MINIMUM = 15;
const MAXIMUM = 55;
const STEP = 5;
const STEP_COUNT = (MAXIMUM - MINIMUM) / STEP;

const TEXT = {
  en: {
    all: "Both periods", periods: "Periods shown on the map", threshold: "Minimum wind gain in 24 h",
    map: "North Atlantic cyclone tracks", hint: "Select a track or use the arrow keys.",
    chart: "The estimated difference by threshold. Select a point or use the threshold slider.",
    difference: "Late minus early", interval: "95% interval", coverage: "windows",
    clear: "Clear selected track", gain: "Wind gain", start: "Start time", wind: "Wind at each fix (kt)",
  },
  zh: {
    all: "两期叠加", periods: "地图显示的时期", threshold: "24 小时风速增量阈值",
    map: "北大西洋气旋轨迹", hint: "点选轨迹，或用方向键查看记录。",
    chart: "各阈值下的估计差值。点选数据点，或使用阈值滑块。",
    difference: "后期减前期", interval: "95% 区间", coverage: "个窗口",
    clear: "取消选中的轨迹", gain: "风速增量", start: "起始时间", wind: "各时点风速（节）",
  },
};

function mapProjection() {
  // Lambert conformal conic, with standard parallels at 15°N and 35°N.
  const rad = Math.PI / 180;
  const tangent = (degrees) => Math.tan(Math.PI / 4 + degrees * rad / 2);
  const n = Math.log(Math.cos(15 * rad) / Math.cos(35 * rad))
    / Math.log(tangent(35) / tangent(15));
  const f = Math.cos(15 * rad) * tangent(15) ** n / n;
  return (lon, lat) => {
    const rho = f / tangent(lat) ** n;
    const angle = n * (lon + 59) * rad;
    return [rho * Math.sin(angle), -rho * Math.cos(angle)];
  };
}

function pairs(values, project) {
  const points = [];
  for (let index = 0; index < values.length; index += 2) {
    points.push(project(values[index], values[index + 1]));
  }
  return points;
}

function prepareMap(data) {
  const project = mapProjection();
  const tracks = data.tracks.map(([id, name, time, gain, winds, fixes]) => ({
    id, name: name === "Unnamed" ? id : name, time, gain, winds,
    era: Number(time.slice(0, 4) >= "2003"), path: pairs(fixes, project),
  }));
  const land = data.land.map((polygon) => polygon.map((ring) => pairs(ring, project)));
  const graticule = [];
  for (let latitude = 10; latitude <= 50; latitude += 10) {
    const points = [];
    for (let longitude = -108; longitude <= -8; longitude += 4) points.push(project(longitude, latitude));
    graticule.push(points);
  }
  for (let longitude = -100; longitude <= -20; longitude += 20) {
    const points = [];
    for (let latitude = 0; latitude <= 52; latitude += 2) points.push(project(longitude, latitude));
    graticule.push(points);
  }
  const anchors = [
    ["100°W", project(-100, 3)], ["80°W", project(-80, 3)], ["60°W", project(-60, 3)],
    ["40°W", project(-40, 3)], ["20°W", project(-20, 3)],
    ["10°N", project(-105, 10)], ["30°N", project(-105, 30)],
  ];
  const pathPoints = tracks.flatMap((track) => track.path);
  const bbox = [...pathPoints, ...anchors.map(([, point]) => point), project(-68, 44)];
  const xs = bbox.map(([x]) => x);
  const ys = bbox.map(([, y]) => y);
  return {
    tracks, land, graticule, anchors, oceanLabel: project(-47, 35),
    extent: [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)],
  };
}

function canvasFrame(canvas) {
  const { width, height } = canvas.getBoundingClientRect();
  if (!width || !height) return null;
  const density = Math.min(window.devicePixelRatio || 1, 2);
  const w = Math.round(width * density);
  const h = Math.round(height * density);
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }
  const context = canvas.getContext("2d");
  context.setTransform(density, 0, 0, density, 0, 0);
  context.clearRect(0, 0, width, height);
  return { context, width, height };
}

function trace(context, points, transform) {
  const [start, ...remaining] = points;
  context.moveTo(...transform(start));
  for (const point of remaining) context.lineTo(...transform(point));
}

function fitMap(map, width, height) {
  const [left, right, bottom, top] = map.extent;
  const scale = Math.min((width - 25) / (right - left), (height - 23) / (top - bottom));
  const centerX = (left + right) / 2;
  const centerY = (bottom + top) / 2;
  return ([x, y]) => [width / 2 + (x - centerX) * scale, height / 2 - (y - centerY) * scale];
}

function dot(context, x, y, radius, fill) {
  context.beginPath();
  context.arc(x, y, radius, 0, 2 * Math.PI);
  context.fillStyle = fill;
  context.fill();
}

function drawMap(canvas, map, visible, focus, chinese) {
  const frame = canvasFrame(canvas);
  if (!frame) return null;
  const { context: ctx, width, height } = frame;
  const transform = fitMap(map, width, height);
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.fillStyle = "#254342";
  ctx.strokeStyle = "#50706f";
  ctx.lineWidth = .65;
  ctx.beginPath();
  for (const polygon of map.land) {
    for (const ring of polygon) {
      trace(ctx, ring, transform);
      ctx.closePath();
    }
  }
  ctx.fill("evenodd");
  ctx.stroke();

  ctx.lineWidth = .57;
  ctx.strokeStyle = "#81a9b23d";
  ctx.beginPath();
  for (const line of map.graticule) trace(ctx, line, transform);
  ctx.stroke();
  ctx.fillStyle = "#a8c2c4";
  ctx.font = '9px ui-monospace, "Consolas", monospace';
  ctx.textBaseline = "bottom";
  ctx.textAlign = "center";
  for (const [label, point] of map.anchors) ctx.fillText(label, ...transform(point));
  ctx.fillStyle = "#b1cecf9c";
  ctx.font = "10px system-ui, sans-serif";
  ctx.fillText(chinese ? "北 大 西 洋" : "N O R T H   A T L A N T I C", ...transform(map.oceanLabel));

  for (const [era, color] of PERIOD_COLORS.entries()) {
    ctx.strokeStyle = color;
    ctx.globalAlpha = focus ? .15 : .54;
    ctx.lineWidth = .86;
    ctx.beginPath();
    for (const track of visible) if (track.era === era) trace(ctx, track.path, transform);
    ctx.stroke();
    ctx.globalAlpha = focus ? .20 : .72;
    for (const track of visible) {
      if (track.era === era) dot(ctx, ...transform(track.path[0]), 1.12, color);
    }
  }
  ctx.globalAlpha = 1;
  if (focus) {
    const color = PERIOD_COLORS[focus.era];
    ctx.lineWidth = 2.6;
    ctx.strokeStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 10;
    ctx.beginPath();
    trace(ctx, focus.path, transform);
    ctx.stroke();
    ctx.shadowBlur = 0;
    for (const point of focus.path) dot(ctx, ...transform(point), 2.2, "#e5f6f6");
    dot(ctx, ...transform(focus.path[0]), 4, color);
  }
  return transform;
}

function distanceToPath(x, y, points, transform) {
  let closest = Infinity;
  let [lastX, lastY] = transform(points[0]);
  for (const point of points.slice(1)) {
    const [nextX, nextY] = transform(point);
    const dx = nextX - lastX;
    const dy = nextY - lastY;
    const length = dx * dx + dy * dy;
    const t = length ? Math.max(0, Math.min(1, ((x - lastX) * dx + (y - lastY) * dy) / length)) : 0;
    const hitX = lastX + t * dx;
    const hitY = lastY + t * dy;
    closest = Math.min(closest, (x - hitX) ** 2 + (y - hitY) ** 2);
    lastX = nextX;
    lastY = nextY;
  }
  return closest;
}

const chartX = (value, width) => 22 + (value - MINIMUM) * (width - 36) / (MAXIMUM - MINIMUM);

function drawProfile(canvas, profile, selected) {
  const frame = canvasFrame(canvas);
  if (!frame) return;
  const { context: ctx, width, height } = frame;
  const x = (point) => chartX(point.threshold, width);
  const y = (value) => 7 + (5 - value) * (height - 27) / 10;
  const boundary = (point, index) => [x(point), y(point.intervals_pp[0][index])];

  ctx.beginPath();
  ctx.moveTo(...boundary(profile[0], 0));
  for (const point of profile.slice(1)) ctx.lineTo(...boundary(point, 0));
  for (const point of [...profile].reverse()) ctx.lineTo(...boundary(point, 1));
  ctx.closePath();
  ctx.fillStyle = "#9cd5e548";
  ctx.fill();
  ctx.font = '9px ui-monospace, "Consolas", monospace';
  ctx.fillStyle = "#a9c1c4";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (const value of [-4, 0, 4]) {
    ctx.fillText(value > 0 ? `+${value}` : String(value), 16, y(value));
    ctx.strokeStyle = value === 0 ? "#a3c1c58c" : "#a3c1c536";
    ctx.lineWidth = .75;
    ctx.beginPath();
    ctx.moveTo(22, y(value));
    ctx.lineTo(width - 10, y(value));
    ctx.stroke();
  }
  ctx.lineWidth = 1.45;
  ctx.strokeStyle = TRACKS;
  ctx.beginPath();
  trace(ctx, profile.map((point) => [x(point), y(point.effects_pp[0])]), (point) => point);
  ctx.stroke();
  for (const point of profile) dot(ctx, x(point), y(point.effects_pp[0]), 1.65, TRACKS);
  ctx.strokeStyle = "#ecbb7caa";
  ctx.lineWidth = .8;
  ctx.setLineDash([2, 3]);
  ctx.beginPath();
  ctx.moveTo(x(selected), 3);
  ctx.lineTo(x(selected), height - 17);
  ctx.stroke();
  ctx.setLineDash([]);
  dot(ctx, x(selected), y(selected.effects_pp[0]), 4.25, "#f4bf85");
  ctx.textAlign = "center";
  for (const cutoff of [15, 25, 35, 45, 55]) {
    ctx.fillStyle = selected.threshold === cutoff ? "#ffd3a0" : "#adc6c6";
    ctx.fillText(String(cutoff), chartX(cutoff, width), height - 8);
  }
}

function markup(copy) {
  return `
    <div class="atlantic-map-frame">
      <div class="atlantic-map-heading">
        <h3>${copy.map}</h3>
        <div class="atlantic-period" role="group" aria-label="${copy.periods}">
          <button type="button" data-era="all" aria-pressed="true">${copy.all}</button>
          <button type="button" data-era="0" aria-pressed="false"><i></i>1982–2002</button>
          <button type="button" data-era="1" aria-pressed="false"><i></i>2003–2023</button>
        </div>
      </div>
      <canvas data-field="map" tabindex="0" role="img" aria-label="${copy.map}" aria-describedby="atlantic-map-hint"></canvas>
      <div class="atlantic-map-footer">
        <p id="atlantic-map-hint">${copy.hint}</p>
        <p data-field="track-count"></p>
      </div>
      <div class="atlantic-window" data-field="window" role="status" hidden>
        <div><strong data-field="name"></strong><span data-field="time"></span></div>
        <p data-field="gain"></p>
        <div class="atlantic-window-fixes" aria-label="${copy.wind}">
          ${[0, 6, 12, 18, 24].map((hour) => `<div><span>${hour} h</span><b data-fix></b></div>`).join("")}
        </div>
        <button type="button" data-field="clear" aria-label="${copy.clear}">×</button>
      </div>
    </div>
    <div class="atlantic-evidence">
      <div class="atlantic-cutoff">
        <label for="atlantic-threshold">${copy.threshold}</label>
        <output for="atlantic-threshold" data-field="threshold-value"></output>
        <input id="atlantic-threshold" data-field="slider" type="range" min="15" max="55" step="5" value="30">
        <div class="atlantic-period-results">
          <p data-era-result="0"><span></span><strong></strong></p>
          <p data-era-result="1"><span></span><strong></strong></p>
        </div>
      </div>
      <div class="atlantic-contrast">
        <p class="atlantic-estimate">
          <span>${copy.difference}</span>
          <strong data-field="effect"></strong>
          <span data-field="interval"></span>
        </p>
        <canvas data-field="curve" role="img" aria-label="${copy.chart}"></canvas>
      </div>
    </div>`;
}

function signed(value) {
  return `${value < 0 ? "−" : "+"}${Math.abs(value).toFixed(2)}`;
}

function initExplorer(root, data, chinese) {
  const copy = chinese ? TEXT.zh : TEXT.en;
  root.innerHTML = markup(copy);
  const fields = Object.fromEntries([...root.querySelectorAll("[data-field]")]
    .map((element) => [element.dataset.field, element]));
  const eraButtons = [...root.querySelectorAll("[data-era]")];
  const eraResults = [...root.querySelectorAll("[data-era-result]")];
  const windFixes = [...root.querySelectorAll("[data-fix]")];
  const number = new Intl.NumberFormat(chinese ? "zh-CN" : "en-US");
  const map = prepareMap(data);
  let period = "all";
  let point = data.profile.find((estimate) => estimate.threshold === 30);
  let visible = [];
  let pinned = null;
  let hover = null;
  let project = null;
  let pendingDraw = 0;

  function draw() {
    pendingDraw = 0;
    project = drawMap(fields.map, map, visible, pinned || hover, chinese);
    drawProfile(fields.curve, data.profile, point);
  }

  function scheduleDraw() {
    if (!pendingDraw) pendingDraw = requestAnimationFrame(draw);
  }

  function showTrack() {
    const focus = pinned || hover;
    fields.window.hidden = !focus;
    if (!focus) return;
    fields.window.setAttribute("aria-live", pinned ? "polite" : "off");
    fields.name.textContent = focus.name;
    fields.time.textContent = `${copy.start} ${focus.time.slice(0, 10)} · ${focus.time.slice(11, 16)} UTC`;
    fields.gain.textContent = `${copy.gain} +${focus.gain} kt · ${copy.wind}`;
    windFixes.forEach((element, index) => {
      element.textContent = String(focus.winds[index]);
    });
    fields.clear.hidden = !pinned;
  }

  function update() {
    const cutoff = point.threshold;
    visible = map.tracks.filter((track) => track.gain >= cutoff
      && (period === "all" || String(track.era) === period));
    if (!visible.includes(pinned)) pinned = null;
    hover = null;
    fields.slider.value = String(cutoff);
    fields.slider.setAttribute("aria-valuetext", `${cutoff} ${chinese ? "节" : "knots"}`);
    fields.slider.style.setProperty("--track-percent", `${100 * (cutoff - MINIMUM) / (MAXIMUM - MINIMUM)}%`);
    fields["threshold-value"].textContent = `≥${cutoff} kt`;
    fields["track-count"].textContent = `${number.format(visible.length)} ${copy.coverage}`;
    fields.effect.textContent = `${signed(point.effects_pp[0])} pp`;
    fields.effect.dataset.sign = point.effects_pp[0] >= 0 ? "positive" : "negative";
    fields.interval.textContent = `${copy.interval} ${point.intervals_pp[0].map(signed).join(" / ")}`;
    eraButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.era === period)));
    eraResults.forEach((result, era) => {
      result.dataset.visible = String(period === "all" || String(era) === period);
      result.querySelector("span").textContent = `${number.format(point.events[era])} / ${number.format(data.totals[era])}`;
      result.querySelector("strong").textContent = `${point.rates_pct[era].toFixed(2)}%`;
    });
    showTrack();
    scheduleDraw();
  }

  function choose(cutoff) {
    const next = data.profile.find((estimate) => estimate.threshold === cutoff);
    if (next && next !== point) {
      point = next;
      update();
    }
  }

  function nearest(event) {
    if (!project) return null;
    const box = fields.map.getBoundingClientRect();
    const x = event.clientX - box.left;
    const y = event.clientY - box.top;
    let closest = event.pointerType === "touch" ? 180 : 65;
    let hit = null;
    for (const track of visible) {
      const distance = distanceToPath(x, y, track.path, project);
      if (distance < closest) {
        closest = distance;
        hit = track;
      }
    }
    return hit;
  }

  fields.slider.addEventListener("input", () => choose(Number(fields.slider.value)));
  for (const button of eraButtons) button.addEventListener("click", () => {
    period = button.dataset.era;
    update();
  });
  function scrubProfile(event) {
    const { left, width } = fields.curve.getBoundingClientRect();
    const fraction = (event.clientX - left - chartX(MINIMUM, width))
      / (chartX(MAXIMUM, width) - chartX(MINIMUM, width));
    choose(MINIMUM + STEP * Math.max(0, Math.min(STEP_COUNT, Math.round(fraction * STEP_COUNT))));
  }
  fields.curve.addEventListener("pointerdown", (event) => {
    fields.curve.setPointerCapture(event.pointerId);
    scrubProfile(event);
  });
  fields.curve.addEventListener("pointermove", (event) => {
    if (fields.curve.hasPointerCapture(event.pointerId)) scrubProfile(event);
  });
  fields.map.addEventListener("pointermove", (event) => {
    if (pinned || event.pointerType === "touch") return;
    const track = nearest(event);
    if (track === hover) return;
    hover = track;
    showTrack();
    scheduleDraw();
  });
  fields.map.addEventListener("pointerleave", () => {
    hover = null;
    showTrack();
    scheduleDraw();
  });
  fields.map.addEventListener("click", (event) => {
    const track = nearest(event);
    pinned = track === pinned ? null : track;
    hover = null;
    showTrack();
    scheduleDraw();
  });
  fields.map.addEventListener("keydown", (event) => {
    if (event.key === "Escape") pinned = null;
    else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      if (!visible.length) return;
      event.preventDefault();
      const index = pinned ? visible.indexOf(pinned) : -1;
      const next = index < 0 ? 0 : (index + (event.key === "ArrowLeft" ? -1 : 1) + visible.length) % visible.length;
      pinned = visible[next];
    } else return;
    hover = null;
    showTrack();
    scheduleDraw();
  });
  fields.clear.addEventListener("click", () => {
    pinned = null;
    showTrack();
    fields.map.focus();
    scheduleDraw();
  });

  const size = new ResizeObserver(scheduleDraw);
  size.observe(fields.map);
  size.observe(fields.curve);
  update();
  return scheduleDraw;
}

export function connectAtlanticExplorer(root, url, chinese, changeVisibility) {
  let active = false;
  let request;
  let redraw;
  return async (wanted) => {
    active = wanted;
    if (!active) {
      changeVisibility(false);
      return;
    }
    try {
      request ??= fetch(url).then((response) => {
        if (!response.ok) throw new Error("Explorer data did not load");
        return response.json();
      });
      const data = await request;
      if (!active) return;
      redraw ??= initExplorer(root, data, chinese);
      changeVisibility(true);
      redraw();
    } catch {
      request = undefined;
      changeVisibility(false);
    }
  };
}
