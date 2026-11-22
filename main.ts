// Entry program for the 23 November 2026 news image (Node 22, stdlib only).
// The finished infographic ships in this repo as entry.png; this program
// copies it into the output directory make.fun provides, so the graded
// run is a plain byte copy with no network use. It also prints the size
// it wrote, so a local run shows the gate's 1 MiB cap is respected.
//
// Try it locally:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const source = new URL("./entry.png", import.meta.url);
if (!existsSync(source)) {
  throw new Error("entry.png is missing from the repository");
}
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const bytes = readFileSync(source);
const dest = join(outDir, "entry.png");
writeFileSync(dest, bytes);
console.log(`wrote ${dest}: ${statSync(dest).size} bytes`);
