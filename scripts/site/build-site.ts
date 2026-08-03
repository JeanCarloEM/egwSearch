// Repository: https://github.com/JeanCarloEM/egwSearch
// License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
// This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

import { createHash } from "node:crypto";
import {
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { join, relative, resolve, sep } from "node:path";
import * as sass from "sass";

type SiteConfig = {
  schema_version: number;
  source_root: string;
  publications_root: string;
  output_root: string;
  base_path: string;
  custom_domain: string;
};

type IndexAsset = {
  path: string;
  hashes: { sha256: string; sha512: string };
};

type IndexPublication = {
  path: string;
  metadata: { path: string };
  cover: IndexAsset | null;
  assets: IndexAsset[];
};

type GlobalIndex = {
  schema_version: string;
  publications: IndexPublication[];
};

const repositoryRoot = resolve(__dirname, "../..");
const forbiddenNames = new Set(["__pycache__"]);
const forbiddenSuffixes = [".pyc", ".tmp", ".partial", ".md"];

function within(root: string, candidate: string): boolean {
  const rel = relative(resolve(root), resolve(candidate));
  return rel === "" || (!rel.startsWith(`..${sep}`) && rel !== "..");
}

function configuredPath(root: string, value: string): string {
  const target = resolve(root, value);
  if (!within(root, target)) throw new Error(`path fora do repositório: ${value}`);
  return target;
}

function forbidden(path: string): boolean {
  const name = path.split(/[\\/]/).at(-1) ?? "";
  return (
    forbiddenNames.has(name) ||
    forbiddenSuffixes.some((suffix) => name.endsWith(suffix))
  );
}

function walk(root: string, ignoreForbidden = false): string[] {
  const result: string[] = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`symlink proibido: ${path}`);
    if (forbidden(path)) {
      if (ignoreForbidden) continue;
      throw new Error(`intermediário proibido: ${path}`);
    }
    if (entry.isDirectory()) result.push(...walk(path, ignoreForbidden));
    else if (entry.isFile()) result.push(path);
  }
  return result.sort();
}

function digests(path: string): { sha256: string; sha512: string } {
  const payload = readFileSync(path);
  return {
    sha256: createHash("sha256").update(payload).digest("hex"),
    sha512: createHash("sha512").update(payload).digest("hex"),
  };
}

function sha256(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function renderTemplate(
  source: string,
  replacements: Record<string, string>,
): string {
  let rendered = source;
  for (const [name, value] of Object.entries(replacements)) {
    rendered = rendered.replaceAll(`{{${name}}}`, value);
  }
  if (rendered.includes("{{")) throw new Error("template público não resolvido");
  return rendered.trimEnd() + "\n";
}

function loadConfiguration(): SiteConfig {
  const config = JSON.parse(
    readFileSync(join(repositoryRoot, "config/site.json"), "utf8"),
  ) as SiteConfig;
  if (config.schema_version !== 1) throw new Error("schema de site incompatível");
  if (!/^\/[A-Za-z0-9._~/-]*\/$/.test(config.base_path)) {
    throw new Error("base_path público inválido");
  }
  if (!/^[a-z0-9.-]+$/.test(config.custom_domain)) {
    throw new Error("domínio público inválido");
  }
  return config;
}

function validateLanding(html: string): void {
  const forbidden = ["/publications", "index.json", ".epub", ".pdf", "cover.png"];
  for (const token of forbidden) {
    if (html.toLowerCase().includes(token)) {
      throw new Error(`página institucional expõe acervo: ${token}`);
    }
  }
  if (/<a\b/i.test(html)) throw new Error("página institucional contém link");
  for (const required of ["<main", "<h1", "viewport", "lang=\"pt-BR\""]) {
    if (!html.includes(required)) throw new Error(`HTML sem requisito: ${required}`);
  }
  for (const required of [
    "ferramenta planejada",
    "Bíblia",
    "Ellen G. White",
    "pioneiros adventistas",
    "ainda são planejadas",
  ]) {
    if (!html.includes(required)) {
      throw new Error(`posicionamento público ausente: ${required}`);
    }
  }
  if (/<(?:title|p class="eyebrow")[^>]*>[^<]*acervo/i.test(html)) {
    throw new Error("página posiciona o produto como acervo");
  }
}

function validateIndex(publicationsRoot: string): {
  index: GlobalIndex;
  indexedAssets: Set<string>;
} {
  const indexPath = join(publicationsRoot, "index.json");
  const index = JSON.parse(readFileSync(indexPath, "utf8")) as GlobalIndex;
  if (index.schema_version !== "publication-global-index/v1") {
    throw new Error("schema do índice público incompatível");
  }
  if (!Array.isArray(index.publications) || index.publications.length === 0) {
    throw new Error("índice público sem publicações");
  }
  const indexedAssets = new Set<string>();
  for (const publication of index.publications) {
    if (!publication.cover) throw new Error(`publicação sem capa: ${publication.path}`);
    const records = [publication.metadata, publication.cover, ...publication.assets];
    if (publication.assets.length === 0) {
      throw new Error(`publicação sem EPUB/PDF: ${publication.path}`);
    }
    for (const record of records) {
      const path = configuredPath(publicationsRoot, record.path);
      if (!existsSync(path) || !lstatSync(path).isFile()) {
        throw new Error(`recurso público ausente: ${record.path}`);
      }
      if ("hashes" in record) {
        const hashed = record as IndexAsset;
        const actual = digests(path);
        if (actual.sha256 !== hashed.hashes.sha256) {
          throw new Error(`SHA-256 divergente: ${record.path}`);
        }
        if (actual.sha512 !== hashed.hashes.sha512) {
          throw new Error(`SHA-512 divergente: ${record.path}`);
        }
        indexedAssets.add(record.path.replaceAll("/", sep));
      }
    }
  }
  return { index, indexedAssets };
}

function validateProjection(
  source: string,
  target: string,
  indexedAssets: Set<string>,
): number {
  const sourceFiles = walk(source, true);
  const targetFiles = walk(target);
  const sourceRelative = sourceFiles.map((path) => relative(source, path));
  const targetRelative = targetFiles.map((path) => relative(target, path));
  if (JSON.stringify(sourceRelative) !== JSON.stringify(targetRelative)) {
    throw new Error("projeção pública não corresponde integralmente à origem");
  }
  for (let index = 0; index < sourceFiles.length; index += 1) {
    const original = sourceFiles[index];
    const published = targetFiles[index];
    if (statSync(original).size !== statSync(published).size) {
      throw new Error(`tamanho divergente: ${sourceRelative[index]}`);
    }
    const extension = sourceRelative[index].toLowerCase().match(/\.[^.]+$/)?.[0] ?? "";
    if ([".epub", ".pdf", ".png"].includes(extension)) {
      if (!indexedAssets.has(sourceRelative[index])) {
        throw new Error(`ativo binário não indexado: ${sourceRelative[index]}`);
      }
      continue;
    }
    if (sha256(original) !== sha256(published)) {
      throw new Error(`bytes divergentes: ${sourceRelative[index]}`);
    }
  }
  return sourceFiles.length;
}

function build(): void {
  const config = loadConfiguration();
  const siteSource = configuredPath(repositoryRoot, config.source_root);
  const publicationsSource = configuredPath(repositoryRoot, config.publications_root);
  const output = configuredPath(repositoryRoot, config.output_root);
  if (output !== join(repositoryRoot, "dist")) throw new Error("output não autorizado");
  walk(publicationsSource, true);
  rmSync(output, { recursive: true, force: true });
  mkdirSync(join(output, "assets"), { recursive: true });
  const css = sass.compile(join(siteSource, "styles/main.scss"), {
    style: "compressed",
    sourceMap: false,
  }).css;
  writeFileSync(join(output, "assets/main.css"), css + "\n", "utf8");
  for (const page of ["index.html", "404.html"]) {
    const html = renderTemplate(readFileSync(join(siteSource, page), "utf8"),
      page === "404.html"
        ? { INLINE_CSS: css }
        : { STYLESHEET_PATH: "assets/main.css" },
    );
    if (page === "index.html") validateLanding(html);
    writeFileSync(join(output, page), html, "utf8");
  }
  writeFileSync(join(output, ".nojekyll"), "", "utf8");
  cpSync(publicationsSource, join(output, "publications"), {
    recursive: true,
    preserveTimestamps: false,
    filter: (path) => !forbidden(path),
  });
  validate();
}

function validate(): void {
  const config = loadConfiguration();
  const source = configuredPath(repositoryRoot, config.publications_root);
  const output = configuredPath(repositoryRoot, config.output_root);
  if (!existsSync(join(output, ".nojekyll"))) throw new Error(".nojekyll ausente");
  const html = readFileSync(join(output, "index.html"), "utf8");
  validateLanding(html);
  const validation = validateIndex(join(output, "publications"));
  const files = validateProjection(
    source,
    join(output, "publications"),
    validation.indexedAssets,
  );
  const bytes = walk(output).reduce((sum, path) => sum + statSync(path).size, 0);
  console.log(
    `SITE_PUBLICATION_OK publications=${validation.index.publications.length} files=${files} bytes=${bytes}`,
  );
}

const command = process.argv[2] ?? "build";
try {
  if (command === "build") build();
  else if (command === "validate") validate();
  else throw new Error(`comando inválido: ${command}`);
} catch (error) {
  console.error(`SITE_PUBLICATION_ERROR ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
}
