const organizationLogos = {
  Alibaba: 'alibaba', AMD: 'amd', Huawei: 'huawei', Meituan: 'meituan', Samsung: 'samsung', SpaceX: 'spacex',
  Baidubce: 'baiducloud', CEA: 'cea', INRIA: 'inria', Tencent: 'tencent',
  GitHubDaily: 'github', 'Deepseek-Harness': 'deepseek',
};
const organizationWordmarks = new Set(['alibaba', 'inria', 'tencent']);
const countryMarkers = {
  China: ['China', '中国', 104.2, 35.9],
  Japan: ['Japan', '日本', 138.3, 36.2],
  'United States': ['United States', '美国', -98.6, 39.8],
};

function appendOrganizationName(parent, row) {
  const logo = organizationLogos[row.school.en];
  if (typeof logo === 'string') {
    const image = document.createElement('img');
    image.className = 'organization-logo';
    image.src = `organization-logos/${logo}.svg`;
    image.alt = '';
    image.width = 34;
    image.height = 34;
    parent.append(image);
    if (organizationWordmarks.has(logo)) {
      image.classList.add('organization-wordmark');
      image.alt = row.name;
      image.addEventListener('error', () => image.replaceWith(document.createTextNode(row.name)), { once: true });
      return;
    }
  }
  parent.append(document.createTextNode(row.name));
}

window.createOrganizationGlobe = function (section) {
  const canvas = section.querySelector('canvas');
  const context = canvas.getContext('2d');
  const destinations = section.querySelector('.globe-destinations');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const radians = Math.PI / 180;
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
  const vector = ([lng, lat]) => {
    const angle = lng * radians;
    const phi = lat * radians;
    return [Math.cos(phi) * Math.sin(angle), Math.sin(phi), Math.cos(phi) * Math.cos(angle)];
  };
  const polygons = window.WORLD_GEO.features.flatMap(({ geometry }) =>
    (geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates)
      .map(([exterior, ...holes]) => {
        const xs = exterior.map(point => point[0]);
        const ys = exterior.map(point => point[1]);
        return { exterior, holes, west: Math.min(...xs), east: Math.max(...xs),
          south: Math.min(...ys), north: Math.max(...ys) };
      }));
  function inside(x, y, ring) {
    let hit = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [ax, ay] = ring[i], [bx, by] = ring[j];
      if ((ay > y) !== (by > y) && x < (bx - ax) * (y - ay) / (by - ay) + ax) hit = !hit;
    }
    return hit;
  }
  let land;
  function landPoints() {
    const points = [];
    const samples = 16000;
    const goldenAngle = 180 * (3 - Math.sqrt(5));
    for (let index = 0; index < samples; index++) {
      const lat = Math.asin(1 - 2 * (index + .5) / samples) / radians;
      const lng = (index * goldenAngle) % 360 - 180;
      const candidates = polygons.filter(polygon => lat >= polygon.south && lat <= polygon.north);
      // Test the equivalent longitude in each polygon's original range.
      if (candidates.some(({ west, east, exterior, holes }) => {
        const equivalent = lng + 360 * Math.ceil((west - lng) / 360);
        return equivalent <= east && inside(equivalent, lat, exterior)
          && !holes.some(hole => inside(equivalent, lat, hole));
      })) {
        points.push(vector([lng, lat]));
      }
    }
    return points;
  }
  const grid = [];
  for (let lat = -60; lat <= 60; lat += 30) {
    grid.push(Array.from({ length: 121 }, (_, i) => vector([i * 3 - 180, lat])));
  }
  for (let lng = 0; lng < 360; lng += 30) {
    grid.push(Array.from({ length: 61 }, (_, i) => vector([lng, i * 3 - 90])));
  }

  let longitude = 104, latitude = 33, cities = [], language = 'zh-CN', active = null, expanded = null;
  let running = !motion.matches, visible = false, inView = false, frame = 0, last = 0, drag = null;
  const autoRotationSpeed = 7.5;
  let flight = null, holdUntil = 0;
  let zoom = 1;
  const globeRadius = (width, height) => Math.min(width, height / zoom) * .48 * zoom;
  const labelPositions = new WeakMap();
  let lastDraw = 0;
  const angularDelta = (target, current) => ((target - current + 540) % 360 + 360) % 360 - 180;
  const localized = (zh, en) => language === 'en' ? en : zh;

  function draw() {
    if (!visible || !context) return;
    const width = canvas.clientWidth, height = canvas.clientHeight;
    if (!width || !height) return;
    const now = performance.now();
    const easing = motion.matches || !running || drag ? 1 : 1 - Math.exp(-Math.min(now - lastDraw, 48) / 90);
    lastDraw = now;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    if (canvas.width !== Math.round(width * dpr) || canvas.height !== Math.round(height * dpr)) {
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
    }
    const cx = width / 2, cy = height / 2, radius = globeRadius(width, height);
    const lon = longitude * radians, lat = latitude * radians;
    const slon = Math.sin(lon), clon = Math.cos(lon), slat = Math.sin(lat), clat = Math.cos(lat);
    const project = ([x, y, z]) => {
      const horizontal = x * slon + z * clon;
      return [cx + radius * (x * clon - z * slon), cy - radius * (y * clat - horizontal * slat),
        y * slat + horizontal * clat];
    };
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, width, height);
    context.beginPath();
    context.arc(cx, cy, radius, 0, 2 * Math.PI);
    const shade = context.createRadialGradient(cx - radius * .35, cy - radius * .4, 0, cx, cy, radius);
    shade.addColorStop(0, '#fffefa');
    shade.addColorStop(.63, '#f3eee5');
    shade.addColorStop(1, '#d6cbbd');
    context.fillStyle = shade;
    context.shadowColor = '#9b806e55';
    context.shadowBlur = radius * .15;
    context.fill();
    context.shadowBlur = 0;
    context.strokeStyle = '#9a89745c';
    context.lineWidth = 1.3;
    context.stroke();

    function trace(lines, stroke) {
      context.beginPath();
      for (const line of lines) {
        let connected = false;
        for (const point of line) {
          const [x, y, depth] = project(point);
          if (depth > 0) {
            if (connected) context.lineTo(x, y);
            else context.moveTo(x, y);
          }
          connected = depth > 0;
        }
      }
      context.strokeStyle = stroke;
      context.stroke();
    }
    context.lineWidth = 1;
    trace(grid, '#957b6020');
    land ??= landPoints();
    context.fillStyle = '#73665e';
    for (const point of land) {
      const [x, y, depth] = project(point);
      if (depth <= .015) continue;
      context.globalAlpha = .18 + depth * .6;
      context.beginPath();
      context.arc(x, y, Math.max(.65, radius * .0062), 0, 2 * Math.PI);
      context.fill();
    }
    context.globalAlpha = 1;

    let candidate = null, best = 0;
    const points = cities.map(city => {
      const [x, y, depth] = project(city.vector);
      const offset = Math.abs(angularDelta(city.location.lng, longitude));
      if (depth > .46 && offset < (city === active ? 16 : 12)) {
        const score = depth - offset * .012 + (city === active ? .05 : 0);
        if (score > best) { best = score; candidate = city; }
      }
      return { city, x, y, depth };
    });
    if (candidate !== active) {
      active = candidate;

      for (const button of destinations.children) button.setAttribute('aria-pressed', button.dataset.city === active?.key);
    }
    const occupied = [];
    const markers = new Map(points.map(point => [point.city.key, point]));
    const labels = [...destinations.children].sort((a, b) =>
      Number(b.dataset.city === active?.key) - Number(a.dataset.city === active?.key)
      || Number(labelPositions.has(b)) - Number(labelPositions.has(a)));
    for (const button of labels) {
      const { city, x, y, depth } = markers.get(button.dataset.city);
      const w = button.offsetWidth, h = button.offsetHeight;
      const offsets = [[-w / 2, -h - 13], [12, -h / 2], [-w - 12, -h / 2], [-w / 2, 13]];
      const previous = labelPositions.get(button);
      let placement;
      const markerInFrame = x > 4 && x < width - 4 && y > 4 && y < height - 4;
      if (markerInFrame && depth > (previous ? .49 : .56) && occupied.length < (width < 560 ? 2 : 4)) {
        const order = [0, 1, 2, 3];
        if (previous) order.unshift(...order.splice(previous.slot, 1));
        placement = order.map(slot => ({
          x: clamp(x + offsets[slot][0], 3, width - w - 3),
          y: clamp(y + offsets[slot][1], 3, height - h - 3),
          w, h, slot,
        })).find(box => occupied.every(other =>
          box.x + box.w + 6 <= other.x || other.x + other.w + 6 <= box.x
          || box.y + box.h + 6 <= other.y || other.y + other.h + 6 <= box.y));
      }
      button.classList.toggle('is-facing', Boolean(placement));
      if (!placement) {
        labelPositions.delete(button);
        if (expanded === button) {
          button.setAttribute('aria-expanded', 'false');
          expanded = null;
        }
        continue;
      }

      occupied.push(placement);
      const px = previous ? previous.x + (placement.x - previous.x) * easing : placement.x;
      const py = previous ? previous.y + (placement.y - previous.y) * easing : placement.y;
      labelPositions.set(button, { x: px, y: py, slot: placement.slot });
      button.style.transform = `translate3d(${px.toFixed(2)}px, ${py.toFixed(2)}px, 0)`;
      const anchorX = clamp(x, px, px + w);
      const anchorY = clamp(y, py, py + h);
      context.beginPath();
      context.moveTo(anchorX, anchorY);
      context.lineTo(x, y);
      context.strokeStyle = city === active ? '#c45f40' : '#a178686f';
      context.stroke();
    }
    for (const { city, x, y, depth } of points) {
      if (depth <= 0) continue;
      const radius = city === active ? 10.5 : 6;
      context.beginPath();
      for (let tip = 0; tip < 10; tip++) {
        const angle = tip * Math.PI / 5 - Math.PI / 2;
        const length = radius * (tip % 2 === 0 ? 1 : .44);
        const px = x + Math.cos(angle) * length, py = y + Math.sin(angle) * length;
        if (tip === 0) context.moveTo(px, py);
        else context.lineTo(px, py);
      }
      context.closePath();
      context.fillStyle = city === active ? '#c7461b' : '#e47951';
      if (city.countryLevel) {
        context.strokeStyle = context.fillStyle;
        context.stroke();
      } else context.fill();
      if (city === active) {
        context.beginPath();
        context.arc(x, y, 13, 0, Math.PI * 2);
        context.strokeStyle = '#c7461b';
        context.stroke();
      }
    }
  }

  function tick(time) {
    frame = 0;
    const elapsed = last ? Math.min((time - last) / 1000, .05) : 0;
    last = time;
    if (flight) {
      const progress = clamp((time - flight.start) / 850, 0, 1);
      const eased = 1 - (1 - progress) ** 3;
      longitude = flight.lon + flight.delta * eased;
      latitude = flight.lat + (flight.targetLat - flight.lat) * eased;
      if (progress === 1) {
        active = flight.city;

        for (const button of destinations.children) button.setAttribute('aria-pressed', button.dataset.city === active.key);
        flight = null;
        holdUntil = time + 4500;
      }
    } else if (running && !drag && time >= holdUntil) {
      longitude = (longitude + autoRotationSpeed * elapsed) % 360;
    }
    draw();
    schedule();
  }

  function schedule() {
    if (visible && inView && (running || flight) && !drag && !frame) frame = requestAnimationFrame(tick);
  }

  function stop() {
    cancelAnimationFrame(frame);
    frame = 0;
    last = 0;
  }

  function labels() {
    canvas.setAttribute('aria-label', localized('可拖拽地球，也可用方向键旋转', 'Drag the globe or rotate it with arrow keys'));
  }

  function setRunning(next) {
    running = next;
    if (running) schedule();
    else stop();
  }

  motion.addEventListener('change', event => setRunning(!event.matches));
  canvas.parentElement.addEventListener('wheel', event => {
    if (event.ctrlKey || event.deltaY === 0) return;
    const { left, top, width, height } = canvas.getBoundingClientRect();
    if (Math.hypot(event.clientX - left - width / 2, event.clientY - top - height / 2) > globeRadius(width, height)) return;
    const units = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? height : 1;
    const next = clamp(zoom * Math.exp(-event.deltaY * units * .0015), 1, 1.6);
    event.preventDefault();
    if (next === zoom) return;
    zoom = next;
    canvas.style.setProperty('--globe-zoom', zoom);
    draw();
  }, { passive: false });
  canvas.onpointerdown = event => {
    if (drag || event.button !== 0) return;
    flight = null;
    holdUntil = 0;
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY };
    canvas.setPointerCapture(event.pointerId);
    stop();
  };
  canvas.onpointermove = event => {
    if (drag?.id !== event.pointerId) return;
    longitude = (longitude - (event.clientX - drag.x) * .5) % 360;
    latitude = clamp(latitude + (event.clientY - drag.y) * .4, -65, 65);
    drag.x = event.clientX;
    drag.y = event.clientY;
    draw();
  };
  canvas.onlostpointercapture = () => { drag = null; schedule(); };
  canvas.onkeydown = event => {
    const shift = { ArrowLeft: [-8, 0], ArrowRight: [8, 0], ArrowUp: [0, 6], ArrowDown: [0, -6] }[event.key];
    if (!shift) return;
    event.preventDefault();
    flight = null;
    holdUntil = 0;
    longitude = (longitude + shift[0]) % 360;
    latitude = clamp(latitude + shift[1], -65, 65);
    draw();
  };
  new ResizeObserver(draw).observe(canvas);
  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    if (inView) { draw(); schedule(); }
    else stop();
  }).observe(section);

  function flyTo(city) {
    if (motion.matches) {
      longitude = city.location.lng;
      latitude = city.location.lat;
      draw();
      return;
    }
    flight = { start: performance.now(), lon: longitude, delta: angularDelta(city.location.lng, longitude),
      lat: latitude, targetLat: city.location.lat, city };
    schedule();
  }

  return {
    setVisible(next) {
      visible = next;
      section.hidden = !next;
      if (!next) stop();
      else schedule();
    },
    update(rows, locale) {
      language = locale;
      const grouped = new Map();
      for (const row of rows) {
        const country = row.school.countryOnly;
        const marker = Object.hasOwn(countryMarkers, country) ? countryMarkers[country] : null;
        if (!row.location && !marker) continue;
        const location = row.location ?? { name: marker[0], label: marker[1], lng: marker[2], lat: marker[3], country };
        const key = row.location ? location.country + '/' + location.name : 'country/' + country;
        if (!grouped.has(key)) grouped.set(key, { location, countryLevel: !row.location,
          vector: vector([location.lng, location.lat]), rows: [] });
        grouped.get(key).rows.push(row);
      }
      flight = null;
      cities = [...grouped.entries()].map(([key, city]) => ({ ...city, key }));
      destinations.replaceChildren();
      expanded = null;
      const stops = [...cities].sort((a, b) =>
        Number(b.rows.some(row => row.featured)) - Number(a.rows.some(row => row.featured)) ||
        b.rows.length - a.rows.length);
      for (const city of stops) {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.city = city.key;
        const label = document.createElement('span');
        label.className = 'globe-location';
        label.textContent = localized(city.location.label, city.location.name);
        button.setAttribute('aria-pressed', 'false');
        button.append(label);
        const name = document.createElement('span');
        name.className = 'globe-organization';
        const lead = city.rows.find(row => row.featured) ?? city.rows[0];
        appendOrganizationName(name, lead);
        button.append(name);
        const others = city.rows.filter(row => row !== lead);
        if (others.length) {
          const names = document.createElement('span');
          names.className = 'globe-more-organizations';
          for (const row of others) {
            const entry = document.createElement('span');
            entry.className = 'globe-organization';
            appendOrganizationName(entry, row);
            names.append(entry);
          }
          button.append(names);
          button.setAttribute('aria-expanded', 'false');
        }
        button.onclick = () => {
          const wasExpanded = expanded === button;
          expanded?.setAttribute('aria-expanded', 'false');
          expanded = !wasExpanded && others.length ? button : null;
          expanded?.setAttribute('aria-expanded', 'true');
          flyTo(city);
        };
        destinations.append(button);
      }
      active = null;
      labels();

      draw();
    },
  };
};
