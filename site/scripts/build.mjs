import { copyFile, mkdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const target = resolve(root, 'dist');
await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
await copyFile(resolve(root, 'index.html'), resolve(target, 'index.html'));
console.log('Built self-contained BasketLens portfolio dossier in site/dist');
