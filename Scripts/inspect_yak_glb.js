const fs = require('fs');
const path = require('path');
const src = String.raw`D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit.glb`;
const b = fs.readFileSync(src);
const s = b.toString('latin1');
console.log('size', b.length);
console.log('meshopt', s.includes('EXT_meshopt_compression'));
console.log('draco', s.includes('KHR_draco_mesh_compression'));
console.log('magic', b.slice(0,4).toString());
