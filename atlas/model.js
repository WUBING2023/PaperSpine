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
  const organizationPlaceholders = new Set(['暂无', '无', 'none', 'n/a', 'empty', 'chongqing', 'nanjing']);
  const organizationCountries = new Map(Object.entries({
    'Deepseek-Harness': 'China',
    'Shanghai Innovation Institution': 'China',
    '自由研究の株式会社 サンダーワールド': 'Japan',
    'Integral Analytics': 'United States',
    'Ultra Heavy LLC': 'United States',
    Shanda: 'United States',
  }));
  // Organization locations apply only where the snapshot has no usable city.
  const organizationBases = new Map(Object.entries({
    Huawei: ['Shenzhen', '深圳', 'China', 114.06, 22.54, 'https://www.huawei.com/en/media-center/company-facts'],
    Baidubce: ['Beijing', '北京', 'China', 116.40, 39.90, 'https://cloud.baidu.com/doc/Agreements/s/Gm4ayxue1'],
    SpaceX: ['Starbase, Texas', '星港（德州）', 'United States', -97.16, 25.99, 'https://ir.spacex.com/faqs-and-contact/'],
    'WEX Inc': ['Portland, Maine', '波特兰（缅因州）', 'United States', -70.26, 43.66, 'https://www.sec.gov/Archives/edgar/data/1309108/000130910826000010/wex-20251231.htm'],
    'Carcinize Corp': ['Boise, Idaho', '博伊西（爱达荷州）', 'United States', -116.20, 43.62, 'https://www.carcinize.net/'],
    'Institut de Recherche sur les Phénomènes Hors Équilibre, AMU, CNRS': ['Marseille', '马赛', 'France', 5.37, 43.30, 'https://emploi.cnrs.fr/Unites/UMR7342/Default.aspx'],
  }));
  // University names and affiliations misclassified in the existing snapshot.
  const universityAliases = new Set([
    'anhui unversity', 'beijing intitute of technology', 'cau', 'cupk',
    'chongqing uninversity of technology', 'cvc,uab', 'isu', 'lzjtu', 'must',
    'monash centre for electron microscopy', 'njau', 'njust', 'nuist', 'nus',
    'swust', 'stanford', 'szu', 'tu münchen', 'utfpr', 'xdu', "xi'dian uiv",
    'yunnan unversity', 'bupt -> ntu', 'caras lab@tokyo tech', 'ccnu', 'cqu', 'cqupt',
    'cqupt-fusion lab', 'cuhk(sz)', 'cuhk', 'dianzikejidaxue', 'fiu', 'gdpu', 'glassgow,uestc',
    'hkust(gz)', 'inha', 'kaust', 'kcl', 'ku leuven', 'ncuhome', 'njupt-sast', 'scau', 'shu',
    'srl-ethz', 'sun yat-sen unviersity', 'polyu', 'tongji & sii', 'ustb', 'ut arlington',
    'ut health houston', 'uvic', 'udem', 'ustc & eit', 'virginia tech', 'xmu', 'zzu', 'cardiff',
    'uwc changshu china',
  ]);
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
    const locate = records => records.map((record, id) => ({
      ...record, id, location: campusCities.get(record.city) || null,
    }));
    const schoolNames = new Set(snapshot.schools.flatMap(school => [normalize(school.en), normalize(school.zh)]).filter(Boolean));
    const companies = (snapshot.companies ?? []).filter(record => [record.en, record.zh].some(name => {
      const key = normalize(name);
      return key && !organizationPlaceholders.has(key);
    }) && [record.en, record.zh].every(name => {
      const key = normalize(name);
      return !key.includes('@tongji.edu.cn') && key.split('|').every(part => {
        const alias = part.trim();
        return !schoolNames.has(alias) && !universityAliases.has(alias);
      });
    }));
    const organizations = locate(companies).map(record => {
      if (/^https:\/\/non-convex\.com\/?$/i.test(record.en)) {
        record = { ...record, en: 'Non-Convex', zh: 'Non-Convex' };
      }
      const base = organizationBases.get(record.en);
      if (record.location) return record;
      if (!base) {
        const statedCountry = countries.find(({ label }) => record.city === label + '·未注明城市');
        return { ...record, countryOnly: statedCountry?.name ?? organizationCountries.get(record.en),
          locationSource: record.en === 'Shanda' ? 'https://www.linkedin.com/company/shanda-group' : undefined };
      }
      const [name, label, country, lng, lat, source] = base;
      const location = campusCities.get(label) ?? { name, label, country, lng, lat,
        countryLabel: countryLabels.get(country) ?? country };
      return { ...record, location, locationSource: source };
    });
    return { countries, cities, schools: locate(snapshot.schools), companies: organizations };
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
