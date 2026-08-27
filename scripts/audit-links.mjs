import { readdirSync, readFileSync } from "node:fs";
import { join, dirname, resolve, sep } from "node:path";

const root = process.argv[2];
const docsDir = join(root, "src", "content", "docs");

function walk(dir, out = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith(".md") || e.name.endsWith(".mdx")) out.push(p);
  }
  return out;
}

const routes = new Set();
for (const file of walk(docsDir)) {
  let rel = file.slice(docsDir.length + 1).replace(/\.mdx?$/, "");
  const isIndex = rel.endsWith(sep + "index") || rel === "index";
  let route;
  if (isIndex) route = rel === "index" ? "" : rel.slice(0, -"index".length).replace(/\/$/, "");
  else route = rel;
  routes.add(("/" + route.replace(/\\/g, "/")).replace(/\/$/, ""));
}

function resolveRoute(sourceFile, raw) {
  const clean = raw.split(sep).join("/").split("#")[0].split("?")[0].replace(/\/$/, "");
  if (!clean) return null;
  if (/^[a-z]+:\/\//.test(clean) || /^mailto:|^tel:/.test(clean)) return "external";
  if (clean.startsWith("#")) return null;
  if (clean.startsWith("/")) return "/" + clean.replace(/^\/+/, "");
  // relative to source dir
  let absolute = resolve(dirname(sourceFile), clean);
  const rel = absolute.slice(docsDir.length + 1).replace(/\\/g, "/");
  return "/" + rel.replace(/\/$/, "");
}

const problems = [];
let internal = 0, external = 0;

function check(file, target, label) {
  if (!target || !target.trim()) return;
  const r = resolveRoute(file, target.trim());
  if (r === "external") { external++; return; }
  if (r === null) return;
  internal++;
  if (!routes.has(r)) {
    problems.push({ file: file.slice(docsDir.length + 1), target: target.trim(), route: r, label });
  }
}

for (const file of walk(docsDir)) {
  const src = readFileSync(file, "utf8");
  // inline markdown
  let m;
  const re1 = /\[[^\]]*\]\(([^)]+)\)/g;
  while ((m = re1.exec(src))) check(file, m[1], "md");
  // reference-style: [label]: url
  const re2 = /^\s*\[[^\]]+\]:\s*(\S+)\s*$/gm;
  while ((m = re2.exec(src))) check(file, m[1], "ref");
  // html <a href>
  const re3 = /<a\s+[^>]*href=["']([^"']+)["']/g;
  while ((m = re3.exec(src))) check(file, m[1], "html");
}

console.log(`External: ${external}, Internal checked: ${internal}, Broken: ${problems.length}`);
for (const p of problems) console.log(`  BROKEN (${p.label}) ${p.file} -> ${p.target}  [route=${p.route}]`);