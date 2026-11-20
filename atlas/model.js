(() => {
  const provinces = {
    北京市: '北京', 天津市: '天津', 上海市: '上海', 重庆市: '重庆',
    河北省: '石家庄 保定', 山西省: '大同', 内蒙古自治区: '呼和浩特',
    辽宁省: '沈阳 大连', 吉林省: '长春', 黑龙江省: '哈尔滨',
    江苏省: '南京 苏州 扬州 徐州 无锡 淮安', 浙江省: '杭州 宁波 温州 金华 湖州',
    安徽省: '合肥 淮南 芜湖 蚌埠', 福建省: '厦门 福州 莆田', 江西省: '南昌',
    山东省: '济南 青岛', 河南省: '郑州 洛阳', 湖北省: '武汉', 湖南省: '长沙 湘潭',
    广东省: '广州 深圳', 海南省: '海口', 四川省: '成都', 云南省: '昆明',
    陕西省: '西安', 甘肃省: '兰州', 新疆维吾尔自治区: '乌鲁木齐',
    香港特别行政区: '香港', 澳门特别行政区: '澳门', 台湾省: '台北',
  };
  const cityProvinces = new Map(Object.entries(provinces).flatMap(([province, cities]) =>
    cities.split(' ').map(city => [city, province])
  ));
  const countryCodes = {
    China: 'CN', 'United States': 'US', Australia: 'AU', 'United Kingdom': 'GB', Singapore: 'SG',
    Brazil: 'BR', Japan: 'JP', 'South Korea': 'KR', Germany: 'DE', Malaysia: 'MY', Spain: 'ES',
    Russia: 'RU', France: 'FR', 'Saudi Arabia': 'SA', Turkey: 'TR', India: 'IN', Greece: 'GR',
    Morocco: 'MA', Austria: 'AT', Thailand: 'TH', Switzerland: 'CH', Poland: 'PL', Indonesia: 'ID',
    Senegal: 'SN', Canada: 'CA', Namibia: 'NA', Czechia: 'CZ', Hungary: 'HU',
  };
  const regionNames = new Intl.DisplayNames(['zh-CN'], { type: 'region' });
  const normalize = value => String(value || '').normalize('NFKC').toLowerCase().trim();
  const normalizeLongitude = lng => lng > 180 ? lng - 360 : lng;
  const matches = (values, query) => normalize(query).split(/\s+/).every(term =>
    values.some(value => normalize(value).includes(term))
  );

  function buildAtlas(snapshot) {
    const countries = Object.entries(snapshot.countries).map(([name, count]) => ({
      name, count, label: countryCodes[name] ? regionNames.of(countryCodes[name]) : name,
    }));
    const cities = snapshot.cities.filter(city =>
      !city.name.includes('(city unspecified)') && Number.isFinite(city.lng) && Number.isFinite(city.lat)
    ).map(city => ({ ...city, lng: normalizeLongitude(city.lng), label: city.zh || city.name }));
    const countryLabels = new Map(countries.map(country => [country.name, country.label]));
    const campusCities = new Map();
    for (const city of cities.filter(city => city.zh)) {
      const location = { ...city, countryLabel: countryLabels.get(city.country) || city.country,
        province: city.country === 'China' ? cityProvinces.get(city.zh) : null };
      campusCities.set(city.zh, campusCities.has(city.zh) ? null : location);
    }
    const schools = snapshot.schools.map((school, id) => ({
      ...school, id, location: campusCities.get(school.city) || null,
    }));
    return { countries, cities, schools };
  }

  function filterSchools(schools, { country, province, city, query }) {
    return schools.filter(school =>
      (!country || school.location?.country === country) &&
      (!province || school.location?.province === province) &&
      (!city || school.location?.label === city) &&
      matches([school.en, school.zh, school.city, school.location?.province, school.location?.name,
        school.location?.country, school.location?.countryLabel], query)
    );
  }

  function project(lng, lat, mode) {
    const mercator = value => Math.log(Math.tan(Math.PI / 4 + Math.min(85, Math.max(-85, value)) * Math.PI / 360));
    if (mode === 'schools') return [86 + (lng - 73) * 12, 42 + (mercator(54) - mercator(lat)) * 510];
    return [24 + (lng + 180) * 2.5333, 45 + (82 - lat) * 3.09];
  }

  function projectGeometry(feature, mode) {
    const { type, coordinates } = feature.geometry;
    const polygons = type === 'Polygon' ? [coordinates] : coordinates;
    return polygons.map(polygon => {
      const offset = polygon[0].every(([lng]) => lng >= 180) ? 360 : 0;
      const mixed = !offset && polygon[0].some(([lng]) => lng > 180);
      return polygon.map(ring => ring.map(([lng, lat]) =>
        project(mixed ? normalizeLongitude(lng) : lng - offset, lat, mode)));
    });
  }

  function computeViewBox(zoom, center) {
    const width = 960 / zoom;
    const height = 500 / zoom;
    return {
      x: Math.max(0, Math.min(960 - width, center[0] - width / 2)),
      y: Math.max(0, Math.min(500 - height, center[1] - height / 2)),
      width, height,
    };
  }

  function zoomCenter(view, nextZoom, [horizontal, vertical]) {
    return [
      view.x + view.width * horizontal + (0.5 - horizontal) * 960 / nextZoom,
      view.y + view.height * vertical + (0.5 - vertical) * 500 / nextZoom,
    ];
  }

  const model = { buildAtlas, filterSchools, matches, project, projectGeometry, computeViewBox, zoomCenter };
  if (typeof module !== 'undefined') module.exports = model;
  else window.AtlasModel = model;
})();
