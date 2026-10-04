// @sournd/assets: the brand kit's tokens and file paths, for Node and bundlers.
//
//   import { tokens, mark, icon } from '@sournd/assets';
//   tokens.colour.petrol.light          // '#3A97A3'
//   mark('dark')                         // absolute path to marks/sournd-wordmark-dark.svg
//   icon(32)                             // the cut the brand uses at 32px (small)
//   import '@sournd/assets/tokens.css';  // CSS custom properties, --sournd-*
//   import '@sournd/assets/fonts.css';   // Bricolage Grotesque + Instrument Sans

import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));

export const tokens = JSON.parse(readFileSync(join(root, 'tokens/tokens.json'), 'utf8'));

/** Brand kit version (semver). The major version is the brand generation. */
export const version = tokens.$version;

/** Absolute path of a file inside the package, e.g. path('web/favicon.ico'). */
export const path = (relative) => join(root, relative);

/** The wordmark SVG for a theme: 'light' (on paper) or 'dark' (on night). */
export const mark = (theme = 'light') => path(`marks/sournd-wordmark-${theme}.svg`);

/** The icon cut for a pixel size: tiny below 20px, small up to 32px, full above. */
export const iconCut = (px) => (px < 20 ? 'tiny' : px <= 32 ? 'small' : 'full');

/** The icon SVG for a cut name or a pixel size. */
export const icon = (sizeOrCut = 'full') =>
  path(`marks/sournd-icon-${typeof sizeOrCut === 'number' ? iconCut(sizeOrCut) : sizeOrCut}.svg`);

if (process.argv[1] === fileURLToPath(import.meta.url) && process.argv.includes('--check')) {
  const expected = [
    'tokens/tokens.json', 'tokens/tokens.css', 'fonts/fonts.css',
    'marks/sournd-wordmark-light.svg', 'marks/sournd-wordmark-dark.svg',
    'marks/sournd-icon-full.svg', 'marks/sournd-icon-small.svg', 'marks/sournd-icon-tiny.svg',
    'web/favicon.ico', 'web/favicon.svg', 'web/apple-touch-icon.png', 'web/icon-192.png', 'web/icon-512.png',
  ];
  const missing = expected.filter((f) => !existsSync(path(f)));
  if (missing.length) {
    console.error(`missing: ${missing.join(', ')}`);
    process.exit(1);
  }
  // Every package must carry the same version as tokens.json.
  const read = (f) => readFileSync(path(f), 'utf8');
  const versions = {
    'tokens.json': version,
    'package.json': JSON.parse(read('package.json')).version,
    'pyproject.toml': read('pyproject.toml').match(/^version = "([^"]+)"/m)?.[1],
    'python': read('python/sournd_assets/__init__.py').match(/__version__ = "([^"]+)"/)?.[1],
    'rust/Cargo.toml': read('rust/Cargo.toml').match(/^version = "([^"]+)"/m)?.[1],
    'swift': read('swift/SourndAssets/SourndAssets.swift').match(/version = "([^"]+)"/)?.[1],
    'php': read('src/Assets.php').match(/VERSION = '([^']+)'/)?.[1],
  };
  const wrong = Object.entries(versions).filter(([, v]) => v !== version);
  if (wrong.length) {
    console.error(`version mismatch (tokens.json says ${version}): ${wrong.map(([k, v]) => `${k}=${v}`).join(', ')}`);
    process.exit(1);
  }
  console.log(`ok: ${expected.length} files, version ${version} everywhere`);
}
