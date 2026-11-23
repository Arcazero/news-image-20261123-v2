// main.ts — entry point for the make.fun news-image-20261123 entry.
// Copies the finished entry.png (drawn by draw.py) into the grader's
// output directory, byte for byte. Node 22, standard library only.
//
// Usage:
//   python3 draw.py
//   MAKEFUN_OUTPUT_DIR=out node main.ts
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

const SRC = "entry.png";

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

if (!existsSync(SRC)) {
  fail("entry.png not found — run `python3 draw.py` first.");
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });

const dest = join(outDir, "entry.png");
copyFileSync(SRC, dest);

// Confirm the grader receives the exact bytes draw.py produced.
if (statSync(dest).size !== statSync(SRC).size) {
  fail(`copied file size mismatch: ${SRC} vs ${dest}`);
}
console.log(`main.ts: copied ${SRC} -> ${dest}`);
