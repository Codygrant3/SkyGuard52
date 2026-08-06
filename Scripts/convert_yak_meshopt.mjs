
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const src = String.raw`D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit.glb`;
const dst = String.raw`D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit-raw.glb`;
const work = String.raw`D:\Skyguard52\Scripts\gltf-tools`;

function run(cmd, args, cwd) {
  console.log('RUN', cmd, args.join(' '));
  execFileSync(cmd, args, { cwd, stdio: 'inherit', shell: false });
}

fs.mkdirSync(work, { recursive: true });
const pkg = path.join(work, 'package.json');
if (!fs.existsSync(pkg)) {
  fs.writeFileSync(pkg, JSON.stringify({ name: 'skyguard-gltf-tools', private: true }, null, 2));
}

// install deps
run(String.raw`C:\Program Files\nodejs\npm.cmd`, ['install', '@gltf-transform/core@4.1.1', '@gltf-transform/extensions@4.1.1', '@gltf-transform/functions@4.1.1', 'meshoptimizer@0.22.0'], work);

const { NodeIO } = await import(pathToFileURL(path.join(work, 'node_modules/@gltf-transform/core/dist/index.modern.js')).href).catch(async () => {
  return await import(path.join(work, 'node_modules/@gltf-transform/core/dist/index.modern.js'));
}).catch(async () => {
  // fallback standard import after install
  return await import(path.join(work, 'node_modules/@gltf-transform/core/dist/index.modern.js').replace(/\\/g,'/'));
});
