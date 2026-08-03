// Repository: https://github.com/JeanCarloEM/egwSearch
// License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
// This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const landing = readFileSync("src/site/index.html", "utf8");
const workflow = readFileSync(".github/workflows/pages.yml", "utf8");
const packageDocument = JSON.parse(readFileSync("package.json", "utf8"));

test("página institucional não revela nem vincula o acervo", () => {
  assert.doesNotMatch(landing, /<a\b/i);
  assert.doesNotMatch(
    landing,
    /\/publications|index\.json|\.epub|\.pdf|cover\.png/i,
  );
  assert.match(landing, /<main\b/);
  assert.match(landing, /lang="pt-BR"/);
  assert.match(landing, /name="viewport"/);
  assert.doesNotMatch(landing, /<title>[^<]*acervo/i);
  assert.doesNotMatch(landing, /class="eyebrow">[^<]*acervo/i);
});

test("página distingue finalidade, corpus e estado real", () => {
  assert.match(landing, /ferramenta planejada/i);
  assert.match(landing, /pesquisar conceitos/i);
  assert.match(landing, /conversar de forma probatória/i);
  assert.match(landing, /Bíblia/);
  assert.match(landing, /Ellen G\. White/);
  assert.match(landing, /pioneiros adventistas/i);
  assert.match(landing, /preparação documental está funcional/i);
  assert.match(landing, /pesquisa e conversa probatória ainda são planejadas/i);
});

test("workflow usa Pages dedicado, Node 24 e permissões mínimas", () => {
  assert.match(workflow, /node-version:\s*24/);
  assert.match(workflow, /actions\/upload-pages-artifact@v4/);
  assert.match(workflow, /actions\/deploy-pages@v4/);
  assert.match(workflow, /pages:\s*write/);
  assert.match(workflow, /id-token:\s*write/);
  assert.match(workflow, /cancel-in-progress:\s*false/);
  assert.match(workflow, /npm run site:build/);
});

test("comandos públicos compõem uma única cadeia de build", () => {
  const scripts = packageDocument.scripts;
  assert.equal(typeof scripts["site:compile"], "string");
  assert.match(scripts["site:refresh"], /publications:covers/);
  assert.match(scripts["site:refresh"], /publications:index/);
  assert.match(scripts["site:build"], /site:compile/);
  assert.match(scripts["site:build"], /build-site\.js build/);
  assert.equal(scripts["site:validate"], "node scripts/site/build-site.js validate");
  assert.match(workflow, /npm run site:refresh[\s\S]*npm run site:build/);
});
