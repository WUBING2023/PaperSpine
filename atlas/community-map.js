const zh = document.documentElement.lang === "zh-CN";
const format = new Intl.NumberFormat(document.documentElement.lang);
const names = new Map([["China", "中国"], ["United States", "美国"], ["United Kingdom", "英国"],
  ["Australia", "澳大利亚"], ["Japan", "日本"], ["South Korea", "韩国"], ["Singapore", "新加坡"],
  ["Germany", "德国"], ["France", "法国"], ["Brazil", "巴西"], ["Canada", "加拿大"],
  ["Spain", "西班牙"], ["Italy", "意大利"], ["India", "印度"], ["Russia", "俄罗斯"]]);
const countryName = (name) => zh ? (names.get(name) || name) : name;
const atlas = window.ATLAS;
const rank = document.querySelector("#rank");
const status = document.querySelector("#map-status");
const filter = document.querySelector("#region-search");
const tabs = [...document.querySelectorAll("[data-region-list]")];
const views = [...document.querySelectorAll("[data-map-view]")];
const map = document.querySelector("#map");
let list = "cities";
let selected = null;
let chart;

function buttonState(buttons, active) {
  buttons.forEach(button => button.setAttribute("aria-pressed", String(active(button))));
}

function locationName(city) {
  return zh ? city.zh : city.name;
}

function focusCity(city) {
  selected = city.name;
  const index = plottedCities.findIndex(candidate => candidate.name === city.name);
  if (chart && index !== -1) {
    chart.setOption({ geo: { center: [city.lng, city.lat], zoom: 3.4 } });
    chart.dispatchAction({ type: "downplay", seriesIndex: 0 });
    chart.dispatchAction({ type: "highlight", seriesIndex: 0, dataIndex: index });
    buttonState(views, () => false);
  }
  status.textContent = `${locationName(city)} · ${format.format(city.count)} ${zh ? "个星标" : "stargazers"}`;
}

const plottedCities = (atlas?.cities || []).filter(city => !city.name.endsWith("(city unspecified)"));

function renderList() {
  const matcher = filter.value.trim().toLowerCase();
  const sources = {
    cities: atlas.cities.map(city => ({ label: locationName(city), count: city.count,
      terms: `${city.name} ${city.zh} ${city.country} ${countryName(city.country)}`, city })),
    countries: Object.entries(atlas.countries).map(([name, count]) => ({
      label: countryName(name), count, terms: `${name} ${countryName(name)}`,
    })),
    schools: atlas.schools.map(org => ({ label: zh ? org.zh : org.en, count: org.count, terms: `${org.zh} ${org.en}` })),
    companies: atlas.companies.map(org => ({ label: zh ? org.zh : org.en, count: org.count, terms: `${org.zh} ${org.en}` })),
  };
  const items = sources[list].filter(item => item.terms.toLowerCase().includes(matcher));
  const fragment = document.createDocumentFragment();
  for (const item of items) {
    const row = document.createElement("li");
    const goto = item.city && !item.city.name.endsWith("(city unspecified)");
    const label = document.createElement("span");
    const count = document.createElement("span");
    const element = document.createElement(goto ? "button" : "div");
    element.className = "row";
    label.textContent = item.label;
    count.className = "count";
    count.textContent = format.format(item.count);
    if (goto) {
      element.type = "button";
      element.setAttribute("aria-pressed", String(selected === item.city.name));
      element.addEventListener("click", () => {
        focusCity(item.city);
        rank.querySelectorAll("button").forEach(button => button.setAttribute("aria-pressed", String(button === element)));
      });
    }
    element.append(label, count);
    row.append(element);
    fragment.append(row);
  }
  rank.replaceChildren(fragment);
  document.querySelector("#rank-empty").hidden = items.length > 0;
}

function setView(view) {
  selected = null;
  buttonState(views, button => button.dataset.mapView === view);
  status.textContent = status.dataset.hint;
  if (chart) {
    chart.dispatchAction({ type: "downplay", seriesIndex: 0 });
    chart.setOption({ geo: { center: view === "asia" ? [111, 31] : [142, 21],
      zoom: view === "asia" ? 3.1 : (map.clientWidth < 520 ? .91 : 1.06) } });
  }
  renderList();
}

if (atlas?.cities?.length && atlas.totalStars > 0) {
  for (const [field, value] of [["total", atlas.totalStars], ["located", atlas.located],
                              ["coverage", atlas.countryCount]]) {
    document.querySelector(`[data-stat="${field}"]`).textContent = format.format(value);
  }
  const stamp = document.querySelector("#data-date");
  stamp.dateTime = atlas.generated;
  stamp.textContent = atlas.generated;
  tabs.forEach(button => button.addEventListener("click", () => {
    list = button.dataset.regionList;
    buttonState(tabs, tab => tab === button);
    renderList();
  }));
  filter.addEventListener("input", renderList);
  renderList();
  if (window.echarts && window.WORLD_GEO) {
    const size = () => map.clientWidth > 600 ? "144%" : "117%";
    echarts.registerMap("world", window.WORLD_GEO);
    chart = echarts.init(map);
    chart.setOption({
      animation: false, backgroundColor: "transparent",
      geo: { map: "world", layoutCenter: ["50%", "50%"], layoutSize: size(), center: [142, 21], zoom: 1.06,
        roam: true, scaleLimit: { min: .65, max: 8 }, emphasis: { disabled: true },
        itemStyle: { areaColor: "#173b46", borderColor: "#46636a", borderWidth: .55 } },
      tooltip: { trigger: "item", renderMode: "richText",
        formatter: point => point.seriesType === "scatter" ? `${point.name} / ${format.format(point.value[2])}` : "" },
      series: [{ type: "scatter", coordinateSystem: "geo", z: 2, symbol: "circle",
        data: plottedCities.map(city => ({ name: locationName(city), value: [city.lng, city.lat, city.count] })),
        symbolSize: value => Math.min(30, 4 + 2.3 * Math.sqrt(value[2])),
        itemStyle: { color: "#ffdb83", opacity: .8, borderColor: "#ffe5a9", borderWidth: .6 },
        emphasis: { scale: 1.2, itemStyle: { color: "#ed9b59", opacity: 1 } } }],
    });
    chart.on("click", { seriesIndex: 0 }, event => {
      if (!plottedCities[event.dataIndex]) return;
      focusCity(plottedCities[event.dataIndex]);
      renderList();
    });
    views.forEach(button => button.addEventListener("click", () => setView(button.dataset.mapView)));
    let layoutSize = size();
    new ResizeObserver(() => {
      chart.resize();
      const updated = size();
      if (updated !== layoutSize) {
        chart.setOption({ geo: { layoutSize: updated } });
        layoutSize = updated;
      }
    }).observe(map);
    setView("world");
  }
} else {
  filter.disabled = true;
  [...tabs, ...views].forEach(button => { button.disabled = true; });
  status.textContent = status.dataset.error;
}
