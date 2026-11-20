const test = require('node:test');
const assert = require('node:assert/strict');

global.window = {};
require('./data.js');
require('./worldgeo.js');
const { buildAtlas, filterSchools, project, projectGeometry, computeViewBox, zoomCenter } = require('./model.js');
const atlas = buildAtlas(window.ATLAS);

test('only known cities become global markers; country totals stay intact', () => {
  assert.ok(atlas.cities.every(city => !city.name.includes('unspecified')));
  assert.equal(atlas.countries.find(country => country.name === 'China').count, 432);
  assert.ok(atlas.cities.filter(city => city.country === 'China').reduce((sum, city) => sum + city.count, 0) < 432);
});

test('school filters combine province, city and case-insensitive bilingual search', () => {
  const province = { province: '北京市', city: '北京' };
  for (const query of ['清华', '  TSINGHUA  ']) {
    assert.deepEqual(filterSchools(atlas.schools, { ...province, query }).map(school => school.zh), ['清华大学']);
  }
  assert.deepEqual(filterSchools(atlas.schools, { ...province, city: '杭州', query: '清华' }), []);
});

test('schools without usable city information stay unplotted', () => {
  const school = atlas.schools.find(school => school.en === 'University of Toronto');
  assert.equal(school.location, null);
  assert.ok(atlas.schools.some(school => school.location?.province === '浙江省'));
});

test('overseas schools appear at known cities and can be filtered by country', () => {
  const matches = filterSchools(atlas.schools, { country: 'United Kingdom', query: '帝国理工' });
  assert.equal(matches.length, 1);
  assert.equal(matches[0].location.label, '伦敦');
  assert.ok(matches[0].location.lng < 0);
  assert.deepEqual(filterSchools(atlas.schools, { country: 'China', query: '帝国理工' }), []);
});

test('projection preserves east and north directions', () => {
  const [west, south] = project(80, 25, 'schools');
  const [east, north] = project(115, 40, 'schools');
  assert.ok(west < east && north < south);
});

test('western hemisphere data renders on the west half of the world map', () => {
  const chicago = atlas.cities.find(city => city.name === 'Chicago');
  assert.ok(project(chicago.lng, chicago.lat, 'global')[0] < 480);
  const brazil = window.WORLD_GEO.features.find(feature => feature.id === 'BRA');
  assert.ok(projectGeometry(brazil, 'global').flat(2).every(([x]) => x > 24 && x < 480));
  const greenland = window.WORLD_GEO.features.find(feature => feature.id === 'GRL');
  assert.ok(projectGeometry(greenland, 'global').flat(2).every(([x]) => x > 24 && x < 480));
});

test('zoom keeps the point under the cursor fixed away from map edges', () => {
  const view = computeViewBox(1, [480, 250]);
  const cursor = [0.7, 0.3];
  const next = computeViewBox(2, zoomCenter(view, 2, cursor));
  assert.deepEqual([next.x + next.width * cursor[0], next.y + next.height * cursor[1]], [672, 150]);
});

test('panning clamps the viewport to the map bounds', () => {
  assert.deepEqual(computeViewBox(2, [-200, 800]), { x: 0, y: 250, width: 480, height: 250 });
});
