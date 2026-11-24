(() => {
  const find = id => document.getElementById(id);
  const options = new URLSearchParams(location.search);
  const embed = options.get('embed');
  if (['1', 'geography', 'organizations'].includes(embed)) document.documentElement.dataset.embed = embed;
  const { buildAtlas, filterSchools, matches, project, projectGeometry, computeViewBox, zoomCenter } = window.AtlasModel;
  let snapshot = window.ATLAS;
  const map = find('map');
  const card = find('map-card');
  const query = find('query');
  const country = find('country');
  const province = find('province');
  const city = find('city');
  const tooltip = find('tooltip');
  const mapSelection = find('map-selection');
  const selection = find('selection');
  const list = find('list');
  const svgNS = 'http://www.w3.org/2000/svg';
  let { cities, countries, schools, companies } = buildAtlas(snapshot);
  let countryMap = new Map(countries.map(country => [country.name, country]));
  const rowButtons = new Map();
  let cityMap = new Map(cities.map(item => [item.label, item]));
  let lang = 'zh-CN';
  let count = new Intl.NumberFormat(lang);
  let cols = new Intl.Collator(lang);
  const translate = label => {
    if (lang === 'zh-CN') return label;
    const english = window.AtlasEnglish[label] || label;
    return window.AtlasLocales?.[lang]?.[english] ?? english;
  };
  const countryLabel = item => lang !== 'zh-CN' ? item.name : item.label;
  const cityLabel = item => lang !== 'zh-CN' ? item.name : item.label;
  const provinceLabel = value => lang !== 'zh-CN' ? window.AtlasProvinceEnglish[value] || value : value;
  const stars = amount => count.format(amount) + (lang !== 'zh-CN' ? (amount === 1 ? ' star' : ' stars') : ' 个星标');
  const records = amount => mode === 'companies'
    ? count.format(amount) + (lang !== 'zh-CN' ? (amount === 1 ? ' organization record' : ' organization records') : ' 条组织记录')
    : universityRecords(amount);
  const universityRecords = amount => count.format(amount) + (lang !== 'zh-CN' ? (amount === 1 ? ' university record' : ' university records') : ' 条高校记录');
  const staticLabels = [...document.querySelectorAll('[data-text]')].map(node => [node, node.textContent]);
  const accessibleLabels = [...document.querySelectorAll('[aria-label]')].map(node => [node, node.getAttribute('aria-label')]);
  const defaultLanguage = document.documentElement.lang;
  const localizedLinks = [...document.querySelectorAll('[data-en-href]')].map(link => [link, link.getAttribute('href')]);
  const title = document.title;
  const description = document.querySelector('meta[name="description"]');
  const originalDescription = description.content;
  const organizationGlobe = window.createOrganizationGlobe(find('organization-globe'));
  const states = Object.fromEntries(['global', 'schools', 'companies'].map(key => [key, { query: '', selected: null }]));
  const view = options.get('view');
  let mode = 'global';
  if (embed === 'organizations') mode = 'companies';
  else if (embed !== 'geography' && (view === 'schools' || view === 'companies')) mode = view;
  let zoom = 1;
  let center = [480, 250];
  let drag = null;
  let calloutLocation = null;
  let dragged = false;
  let previousCity;
  const activeRecords = () => mode === 'companies' ? companies : schools;
  const mapScope = () => mode !== 'global' && country.value === 'China' ? 'schools' : 'global';

  function svg(tag, attrs, parent) {
    const node = document.createElementNS(svgNS, tag);
    for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value);
    parent.append(node);
    return node;
  }

  function html(tag, content, parent, className) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = content;
    parent.append(node);
    return node;
  }

  function updateOptions(select, label, values, display) {
    const current = select.value;
    const options = [...new Set(values.filter(Boolean))].sort((left, right) => cols.compare(display(left), display(right)));
    select.replaceChildren(new Option(translate(label), ''), ...options.map(value => new Option(display(value), value)));
    select.value = options.includes(current) ? current : '';
  }

  function updateCityOptions() {
    updateOptions(city, '全部城市', activeRecords().filter(school => school.location &&
      (!country.value || school.location.country === country.value) &&
      (!province.value || school.location.province === province.value)).map(school => school.location.label),
    value => cityLabel(cityMap.get(value)));
  }

  function updateView() {
    const { x, y, width, height } = computeViewBox(zoom, center);
    center = [x + width / 2, y + height / 2];
    map.setAttribute('viewBox', [x, y, width, height].join(' '));
    map.classList.toggle('can-pan', zoom > 1);
    tooltip.hidden = true;
    positionCallout();
  }

  function positionCallout() {
    if (!calloutLocation) {
      mapSelection.hidden = true;
      return;
    }
    const [x, y] = project(calloutLocation.lng, calloutLocation.lat, mapScope());
    const view = computeViewBox(zoom, center);
    const bounds = map.getBoundingClientRect();
    const left = (x - view.x) / view.width * bounds.width;
    const top = (y - view.y) / view.height * bounds.height;
    mapSelection.hidden = left < 0 || left > bounds.width || top < 0 || top > bounds.height;
    if (mapSelection.hidden) return;
    const gap = 8 + 25 * bounds.width / view.width;
    const width = mapSelection.offsetWidth;
    const height = mapSelection.offsetHeight;
    const fitsRight = left + gap + width <= bounds.width - 8;
    const fitsLeft = left - gap - width >= 8;
    const preferredLeft = fitsRight ? left + gap : fitsLeft ? left - gap - width : left - width / 2;
    const preferredTop = fitsRight || fitsLeft ? top - height / 2 : top + gap + height <= bounds.height ? top + gap : top - gap - height;
    mapSelection.style.left = Math.max(8, Math.min(bounds.width - width - 8, preferredLeft)) + 'px';
    mapSelection.style.top = Math.max(8, Math.min(bounds.height - height - 8, preferredTop)) + 'px';
  }

  function zoomAt(factor, cursor) {
    const next = Math.max(1, Math.min(3, zoom * factor));
    if (next === zoom) return;
    center = zoomCenter(computeViewBox(zoom, center), next, cursor);
    zoom = next;
    updateView();
  }

  map.addEventListener('wheel', event => {
    if (event.ctrlKey || !event.deltaY || drag?.moving) return;
    event.preventDefault();
    const bounds = map.getBoundingClientRect();
    const cursor = [(event.clientX - bounds.left) / bounds.width, (event.clientY - bounds.top) / bounds.height];
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? bounds.height : 1);
    zoomAt(Math.exp(-Math.max(-240, Math.min(240, delta)) * 0.003), cursor);
  }, { passive: false });

  map.addEventListener('pointerdown', event => {
    dragged = false;
    if (event.pointerType !== 'mouse' || event.button !== 0 || zoom <= 1) return;
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY, moving: false };
  });
  map.addEventListener('pointermove', event => {
    if (drag?.id !== event.pointerId || !(event.buttons & 1)) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (!drag.moving) {
      if (Math.hypot(dx, dy) < 4) return;
      map.setPointerCapture(event.pointerId);
      drag.moving = true;
      dragged = true;
      map.classList.add('dragging');
    }
    const bounds = map.getBoundingClientRect();
    const { width, height } = computeViewBox(zoom, center);
    center = [center[0] - dx * width / bounds.width, center[1] - dy * height / bounds.height];
    drag.x = event.clientX;
    drag.y = event.clientY;
    updateView();
  });

  function endDrag(event) {
    if (drag?.id !== event.pointerId) return;
    drag = null;
    map.classList.remove('dragging');
  }

  window.addEventListener('pointerup', endDrag);
  map.addEventListener('pointercancel', endDrag);
  map.addEventListener('lostpointercapture', endDrag);
  map.addEventListener('click', event => {
    if (dragged || event.target.closest('.pin') || !states[mode].selected) return;
    activate(null, false, undefined, true);
  });

  function pathData(feature, layer) {
    return projectGeometry(feature, layer).map(polygon => polygon.map(ring =>
      ring.map(([x, y], index) => (index ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1)).join('') + 'Z'
    ).join('')).join('');
  }

  function renderTerrain() {
    const terrain = find('terrain');
    terrain.replaceChildren();
    const scope = mapScope();
    for (const feature of window.WORLD_GEO.features) {
      if (feature.id === 'ATA' || (scope === 'schools' && ['CHN', 'TWN'].includes(feature.id))) continue;
      svg('path', { d: pathData(feature, scope), 'stroke-width': .8 }, terrain);
    }
    if (scope === 'global') return;
    for (const [name, path, x, y] of window.CHINA_PROVINCES) {
      svg('path', { d: path, class: 'province', 'stroke-width': 1, 'fill-rule': 'evenodd' }, terrain);
      if (!/香港|澳门|北京|天津|上海/.test(name)) {
        const label = svg('text', { x, y, 'font-size': 10, 'text-anchor': 'middle' }, terrain);
        label.textContent = lang !== 'zh-CN' ? provinceLabel(name) : name.replace(/(壮族自治区|回族自治区|维吾尔自治区|自治区|省|市)$/, '');
      }
    }
  }

  const featuredNames = new Set(['AMD', 'Alibaba', 'Baidubce', 'CEA', 'DP Technology', 'GitHubDaily',
    'Deepseek-Harness', 'Huawei', 'INRIA', 'Meituan', 'Samsung', 'Shanda', 'Shanghai Electric', 'SpaceX', 'Tencent', 'WEX Inc']);
  const brandNames = { Baidubce: ['Baidu AI Cloud', '百度智能云'], Tencent: ['Tencent', '腾讯'],
    'DP Technology': ['DP Technology', '深势科技'], 'Shanghai Electric': ['Shanghai Electric', '上海电气'] };
  const schoolRow = school => ({
    key: 'school-' + school.id,
    name: mode === 'companies' && Object.hasOwn(brandNames, school.en)
      ? brandNames[school.en][lang !== 'zh-CN' ? 0 : 1] : lang !== 'zh-CN' ? school.en : school.zh,
    count: school.count,
    sub: [school.location
      ? (lang !== 'zh-CN' ? school.location.country : school.location.countryLabel) + ' / ' + cityLabel(school.location)
      : lang === 'en' && school.city.includes('未注明') ? 'City unspecified' : school.city,
      lang !== 'en' && school.zh !== school.en ? school.en : ''].filter(Boolean).join(' · '),
    location: school.location, school, featured: mode === 'companies' && featuredNames.has(school.en),
  });
  const cityRow = item => ({
    key: 'city-' + item.name + '-' + item.country, name: cityLabel(item), count: item.count,
    sub: countryLabel(countryMap.get(item.country) || { name: item.country, label: item.country }), location: item, city: item,
  });
  const countryRow = item => ({
    key: 'country-' + item.name, name: countryLabel(item), count: item.count,
    sub: lang !== 'zh-CN' ? '' : item.name, country: item.name,
  });
  const clusterRow = (location, total, size) => ({
    key: 'campus-' + location.label, name: cityLabel(location), count: total, location, sub: records(size), size,
  });

  function activate(row, pan = false, focusKey, keepView = false) {
    if (!row && mode !== 'global' && previousCity !== undefined) {
      city.value = previousCity;
      previousCity = undefined;
    }
    states[mode].selected = row;
    if (pan && row?.location) {
      const { lng, lat } = row.location;
      center = project(lng, lat, mapScope());
      zoom = Math.max(zoom, 1.55);
    } else if ((!row && !keepView) || row?.country) {
      zoom = 1;
      center = [480, 250];
    }
    updateView();
    render();
    if (row) rowButtons.get(row.key)?.scrollIntoView({ block: 'nearest', inline: 'nearest', container: 'nearest' });
    if (focusKey) rowButtons.get(focusKey)?.focus({ preventScroll: true });
  }

  function showTooltip(pin, label) {
    tooltip.textContent = label;
    tooltip.hidden = false;
    const bounds = tooltip.parentElement.getBoundingClientRect();
    const point = pin.getBoundingClientRect();
    tooltip.style.left = Math.max(6, Math.min(bounds.width - tooltip.offsetWidth - 6, point.left - bounds.left + 12)) + 'px';
    tooltip.style.top = Math.max(5, Math.min(bounds.height - tooltip.offsetHeight - 5, point.top - bounds.top - 32)) + 'px';
  }

  function drawPin(layer, location, amount, label, active, handler, featured = false) {
    const [x, y] = project(location.lng, location.lat, mapScope());
    if (x < 0 || x > 960 || y < 0 || y > 500) return;
    const radius = featured ? 6 : Math.min(9, 3.3 + Math.sqrt(amount) * .65);
    const pin = svg('g', { transform: 'translate(' + x + ' ' + y + ')', class: 'pin', tabindex: 0,
      role: 'button', 'aria-label': label, 'aria-pressed': active }, layer);
    svg('circle', { r: Math.max(13, radius + 5), fill: 'transparent' }, pin);
    if (featured) svg('circle', { r: radius + 3, fill: 'none', class: 'pin-ring' }, pin);
    if (amount >= 3 || active) svg('circle', { r: radius + 3, class: 'pin-glow', opacity: .35, filter: 'url(#glow)' }, pin);
    if (active) {
      for (const offset of [5, 10, 16]) svg('circle', { r: radius + offset, fill: 'none', class: 'pin-ring', opacity: 1 - offset / 20, 'pointer-events': 'none' }, pin);
    }
    svg('circle', { r: radius + 5, fill: 'none', class: 'hover-ring' }, pin);
    svg('circle', { r: active ? radius + 1 : radius, class: featured ? 'pin-dot is-featured' : amount > 1 ? 'pin-dot is-dense' : 'pin-dot' }, pin);
    pin.addEventListener('pointerenter', () => { if (!active) showTooltip(pin, label); });
    pin.addEventListener('pointerleave', () => { tooltip.hidden = true; });
    pin.addEventListener('focus', () => { if (!active) showTooltip(pin, label); });
    pin.addEventListener('blur', () => { tooltip.hidden = true; });
    pin.addEventListener('click', handler);
    pin.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handler();
      }
    });
  }

  function raiseSelectedPin(layer) {
    const activePin = layer.querySelector('[aria-pressed=true]');
    if (activePin) layer.append(activePin);
  }

  let selectedOrganizationRegion;

  function renderOrganizations(rows) {
    organizationGlobe.update(rows, lang === 'zh-CN' ? 'zh-CN' : 'en');
    const directory = find('organizations');
    directory.replaceChildren();
    const featured = rows.filter(row => row.featured);
    if (featured.length) {
      const section = html('section', '', directory, 'featured-section');
      html('h3', lang !== 'zh-CN' ? 'Notable companies and organizations' : '知名企业/组织', section);
      const cards = html('div', '', section, 'organization-cards');
      for (const row of featured) {
        const card = html('article', '', cards, 'organization-card');
        appendOrganizationName(html('h4', '', card), row);
        const country = countryMap.get(row.school.countryOnly);
        html('p', row.sub || (country && countryLabel(country)) ||
          (lang !== 'zh-CN' ? 'City unavailable' : '未注明城市'), card);
      }
    }
    if (embed === 'organizations') return;
    const regionLabel = country => country
      ? countryLabel(countryMap.get(country) ?? { name: country, label: country })
      : (lang !== 'zh-CN' ? 'Other' : '其他');
    const groups = new Map();
    for (const row of rows) {
      const country = row.location?.country ?? row.school.countryOnly ?? '';
      const group = groups.get(country) ?? [];
      group.push(row);
      groups.set(country, group);
    }
    if (!groups.size) {
      html('p', translate('没有匹配结果，试试其他关键词或筛选条件。'), directory, 'empty');
      return;
    }
    const overview = html('section', '', directory, 'organization-overview');
    html('h3', lang !== 'zh-CN' ? 'Distribution by region' : '地区分布', overview);
    const bars = html('div', '', overview, 'organization-bars');
    const ranked = [...groups].sort(([a, left], [b, right]) => Number(!a) - Number(!b)
      || right.length - left.length || cols.compare(regionLabel(a), regionLabel(b)));
    const maxCount = Math.max(...ranked.map(([, group]) => group.length));
    const regions = html('div', '', directory, 'organization-regions');
    const section = html('section', '', regions, 'organization-region');
    section.id = 'organization-region-results';
    const heading = html('h3', '', section);
    heading.id = 'organization-region-heading';
    section.setAttribute('aria-labelledby', heading.id);
    const entries = html('ul', '', section);
    const regionButtons = new Map();
    for (const [region, group] of ranked) {
      const button = html('button', '', bars, 'organization-bar');
      button.type = 'button';
      button.setAttribute('aria-controls', section.id);
      regionButtons.set(region, button);
      html('span', regionLabel(region), button);
      const track = html('span', '', button, 'organization-bar-track');
      track.setAttribute('aria-hidden', 'true');
      html('span', '', track).style.width = (group.length / maxCount * 100) + '%';
      html('strong', count.format(group.length), button);
      button.onclick = () => showRegion(region);
    }
    function showRegion(region) {
      selectedOrganizationRegion = region;
      for (const [key, button] of regionButtons) button.setAttribute('aria-pressed', key === region);
      heading.textContent = regionLabel(region);
      entries.replaceChildren();
      for (const row of [...groups.get(region)].sort((a, b) => cols.compare(a.name, b.name))) {
        const entry = html('li', '', entries);
        appendOrganizationName(html('strong', '', entry), row);
        const city = row.location ? cityLabel(row.location) : row.school.countryOnly
          ? (lang !== 'zh-CN' ? 'City unspecified' : '城市未注明') : row.sub;
        if (city) html('small', city, entry);
      }
    }
    showRegion(groups.has(selectedOrganizationRegion) ? selectedOrganizationRegion : ranked[0][0]);
  }

  function render() {
    tooltip.hidden = true;
    const isDirectory = mode !== 'global';
    const isCompany = mode === 'companies';
    const state = states[mode];
    const rows = isCompany ? companies.map(schoolRow) : isDirectory
      ? filterSchools(activeRecords(), { country: country.value, province: province.value, city: city.value, query: query.value }).map(schoolRow)
      : countries.filter(country => matches([country.name, country.label], query.value)).map(countryRow);
    if (isCompany) {
      renderOrganizations(rows);
      return;
    }
    const matchingCities = cities.filter(item =>
      matches([item.label, item.name, item.country, countryMap.get(item.country)?.label], query.value));
    const displayedCities = state.selected?.country
      ? matchingCities.filter(item => item.country === state.selected.country) : matchingCities;
    if (!isDirectory && (query.value.trim() || state.selected?.country || state.selected?.city)) {
      const country = state.selected?.country || state.selected?.city?.country;
      rows.push(...matchingCities.filter(item => !country || item.country === country).map(cityRow));
    }
    if (state.selected?.school && !rows.some(row => row.key === state.selected.key)) state.selected = null;
    const chosen = state.selected;
    const current = chosen?.school ? schoolRow(chosen.school) : chosen?.city ? cityRow(chosen.city)
      : chosen?.country ? countryRow(countryMap.get(chosen.country))
      : chosen?.size ? clusterRow(chosen.location, chosen.count, chosen.size) : null;
    calloutLocation = current?.location || null;
    if (calloutLocation) {
      mapSelection.firstElementChild.textContent = isCompany ? current.name : current.name + ' · ' + stars(current.count);
      mapSelection.lastElementChild.textContent = current.school
        ? cityLabel(calloutLocation) + ' · ' + translate('城市级定位') : current.sub;
    }
    positionCallout();
    selection.replaceChildren();
    selection.hidden = !current;
    if (current) {
      const clear = html('button', '×', selection);
      clear.setAttribute('aria-label', translate('清除选择'));
      clear.onclick = () => { activate(null); query.focus(); };
      html('strong', current.name, selection);
      html('span', [current.sub, isCompany ? '' : stars(current.count),
        current.school && !current.location ? translate('未在此视图标点') : ''].filter(Boolean).join(' · '), selection);
    }
    find('results').textContent = isDirectory ? records(rows.length) : count.format(rows.length) +
      (lang !== 'zh-CN' ? (rows.length === 1 ? ' result' : ' results') : ' 项地域结果');
    rowButtons.clear();
    list.replaceChildren();
    list.scrollTop = 0;
    for (const row of rows) {
      const button = html('button', '', html('li', '', list));
      rowButtons.set(row.key, button);
      button.setAttribute('aria-pressed', current?.key === row.key);
      const title = html('span', row.name, button, 'row-name');
      if (row.sub) html('small', row.sub, title);
      if (row.featured) {
        button.classList.add('featured-organization');
        html('span', lang !== 'zh-CN' ? 'Featured' : '精选', button, 'featured-label');
      }
      if (!isCompany) html('span', count.format(row.count), button, 'count');
      button.onclick = () => activate(current?.key === row.key ? null : row, true, row.key);
    }
    if (!rows.length) html('li', translate('没有匹配结果，试试其他关键词或筛选条件。'), list, 'empty');
    const layer = find('markers');
    layer.replaceChildren();
    if (!isDirectory) {
      for (const item of [...displayedCities].sort((left, right) => left.count - right.count)) {
        const row = cityRow(item);
        drawPin(layer, item, item.count, cityLabel(item) + ' · ' + stars(item.count), current?.key === row.key,
          () => activate(row, false, row.key));
      }
      raiseSelectedPin(layer);
      return;
    }
    const clusters = new Map();
    for (const row of rows) {
      if (!row.location) continue;
      const cluster = clusters.get(row.location.label) || [];
      cluster.push(row);
      clusters.set(row.location.label, cluster);
    }
    for (const cluster of [...clusters.values()].sort((left, right) => left.length - right.length)) {
      const location = cluster[0].location;
      const total = cluster.reduce((sum, row) => sum + row.count, 0);
      const featured = cluster.filter(row => row.featured).map(row => row.name);
      const details = [cityLabel(location), records(cluster.length), ...featured];
      if (!isCompany) details.push(stars(total));
      drawPin(layer, location, isCompany ? cluster.length : total, details.join(' · '),
        current?.location?.label === location.label,
        () => {
          previousCity ??= city.value;
          city.value = location.label;
          if (cluster.length === 1) activate(cluster[0], false, cluster[0].key);
          else {
            activate(clusterRow(location, total, cluster.length));
            city.focus();
          }
        }, featured.length > 0);
    }
    raiseSelectedPin(layer);
  }

  function updateSchoolScope() {
    const isChina = mapScope() === 'schools';
    province.hidden = !isChina;
    find('map-title').textContent = translate(mode === 'companies'
      ? (isChina ? '中国公司与组织分布' : '全球公司与组织分布')
      : (isChina ? '中国高校分布' : '全球高校分布'));
  }

  function updateModeLabels() {
    const isDirectory = mode !== 'global';
    query.value = states[mode].query;
    query.placeholder = translate(mode === 'companies' ? '搜索公司、组织、国家或城市'
      : (isDirectory ? '搜索高校、国家或城市' : '搜索国家、地区或城市'));
    query.setAttribute('aria-label', query.placeholder);
    card.dataset.mode = mode;
    const isCompany = mode === 'companies';
    card.closest('.workspace').classList.toggle('organization-view', isCompany);
    card.hidden = isCompany;
    list.hidden = isCompany;
    list.closest('.directory').querySelector('.directory-head').hidden = isCompany;
    find('organizations').hidden = !isCompany;
    organizationGlobe.setVisible(isCompany);
    if (isCompany) selection.hidden = true;
    find('list-stars').hidden = mode === 'companies';
    find('results').closest('.list-head').hidden = isCompany;
    find('school-filters').hidden = !isDirectory;
    if (isDirectory) updateSchoolScope();
    else find('map-title').textContent = translate('全球星标分布');
    find('directory-title').textContent = translate(isCompany ? '公司 / 组织' : (isDirectory ? '高校筛选' : '地域概览'));
    find('source-note').textContent = translate(mode === 'companies'
      ? '组织名称来自 GitHub 公开资料。只有国家的记录归入地区目录。'
      : isDirectory
      ? '仅按快照中可关联的城市标点，不代表校区坐标。未标点的高校可在不限定地区时搜索。中国省级底图：阿里云 DataV。'
      : '数据来自 PaperSpine 的 GitHub 聚合快照。未注明城市的记录只计入国家与地区汇总，不在地图标点。');
    document.querySelectorAll('[data-mode][aria-pressed]').forEach(button =>
      button.setAttribute('aria-pressed', button.dataset.mode === mode));
  }

  function selectMode(next) {
    if (mode === next) return;
    const filters = states[mode];
    filters.country = country.value;
    filters.province = province.value;
    filters.city = previousCity ?? city.value;
    if (previousCity !== undefined) filters.selected = null;
    previousCity = undefined;
    mode = next;
    updateDirectoryOptions(states[mode]);
    updateModeLabels();
    zoom = 1;
    center = [480, 250];
    updateView();
    renderTerrain();
    render();
  }

  find('date').dateTime = snapshot.generated;
  find('date').textContent = snapshot.generated;
  function updateDirectoryOptions(filters) {
    if (mode === 'companies') return;
    const locations = activeRecords().flatMap(record => record.location ? [record.location] : []);
    updateOptions(country, '全部国家与地区', locations.map(location => location.country), value => countryLabel(countryMap.get(value) || { name: value, label: value }));
    country.value = filters.country ?? '';
    updateOptions(province, '全部省级地区', locations.map(location => location.province), provinceLabel);
    province.value = filters.province ?? '';
    updateCityOptions();
    city.value = filters.city ?? '';
  }
  let repoStats;

  function selectLanguage(next) {
    lang = next;
    count = new Intl.NumberFormat(lang);
    cols = new Intl.Collator(lang);
    document.documentElement.lang = lang;
    document.querySelector('[data-contributor-ledger]').href =
      'v6/contributors/?lang=' + (lang === 'zh-CN' ? 'zh-CN' : 'en');
    document.title = translate(title);
    description.content = translate(originalDescription);
    for (const [link, zhHref] of localizedLinks) {
      const href = lang === 'zh-CN' ? zhHref : lang === 'en' ? link.dataset.enHref : 'v6/' + lang + '/';
      link.setAttribute('href', href);
    }
    for (const [node, label] of staticLabels) node.textContent = translate(label);
    for (const [node, label] of accessibleLabels) node.setAttribute('aria-label', translate(label));
    showLanguageInMenu(lang);
    find('total').textContent = count.format(repoStats?.stargazers_count ?? snapshot.totalStars);
    find('sample').textContent = count.format(snapshot.totalStars);
    find('date').dateTime = snapshot.generated;
    find('date').textContent = snapshot.generated;
    find('regions').textContent = count.format(snapshot.countryCount);
    find('schools').textContent = count.format(snapshot.schoolCount);
    find('companies').textContent = count.format(companies.length);
    updateDirectoryOptions({ country: country.value, province: province.value, city: city.value });
    updateModeLabels();
    renderTerrain();
    const scrollTop = list.scrollTop;
    render();
    list.scrollTop = scrollTop;
  }
  document.querySelectorAll('button[data-mode]').forEach(button => button.onclick = () => selectMode(button.dataset.mode));
  query.oninput = () => { states[mode].query = query.value; activate(null); };
  country.onchange = () => {
    previousCity = undefined;
    province.value = '';
    city.value = '';
    updateCityOptions();
    updateSchoolScope();
    renderTerrain();
    activate(null);
  };
  province.onchange = () => { previousCity = undefined; city.value = ''; updateCityOptions(); activate(null); };
  city.onchange = () => { previousCity = undefined; activate(null); };
  new ResizeObserver(() => {
    list.parentElement.style.setProperty('--map-height', card.offsetHeight + 'px');
    positionCallout();
  }).observe(card);
  updateView();
  const requestedLanguage = options.get('lang');
  selectLanguage(requestedLanguage === 'en' || requestedLanguage === 'zh-CN' || Object.hasOwn(window.AtlasLocales || {}, requestedLanguage)
    ? requestedLanguage : defaultLanguage);
  window.PaperSpineLive?.repository(row => {
    repoStats = row;
    find('total').textContent = count.format(row.stargazers_count);
    find('total').title = row.retrieved_at;
  });
  window.PaperSpineLive?.atlas(row => {
    if (row.retrieved_at === (snapshot.retrieved_at || snapshot.generated)) return;
    if (Date.parse(row.retrieved_at) < Date.parse(snapshot.generated)) return;
    const next = buildAtlas(row);
    snapshot = row;
    ({ cities, countries, schools, companies } = next);
    countryMap = new Map(countries.map(item => [item.name, item]));
    cityMap = new Map(cities.map(item => [item.label, item]));
    states.global.selected = states.schools.selected = states.companies.selected = null;
    selectLanguage(lang);
  });
})();
