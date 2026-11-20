const fs = require('node:fs');
const path = require('node:path');
const { project } = require('./model.js');

const source = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const provinces = source.features.filter(feature =>
  feature.properties.level === 'province' && ['Polygon', 'MultiPolygon'].includes(feature.geometry.type)
).map(feature => {
  const { name, centroid, center } = feature.properties;
  const { type, coordinates } = feature.geometry;
  const polygons = type === 'Polygon' ? [coordinates] : coordinates;
  const outline = polygons.map(polygon => polygon.map(ring =>
    ring.map(([lng, lat], index) => {
      const point = project(lng, lat, 'schools').map(value => value.toFixed(1));
      return (index ? 'L' : 'M') + point.join(',');
    }).join('') + 'Z'
  ).join('')).join('');
  return [name, outline, ...project(...(centroid || center), 'schools').map(Math.round)];
});
if (provinces.length < 30) throw new Error('Incomplete province geometry');
fs.writeFileSync(path.join(__dirname, 'china-provinces.js'), '// Province outlines derived from Alibaba Cloud DataV GeoAtlas (https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json).\n' + 'window.CHINA_PROVINCES = ' + JSON.stringify(provinces) + ';\n');
