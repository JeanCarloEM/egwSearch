// Repository: https://github.com/JeanCarloEM/egwSearch
// License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import test from "node:test";

const root = process.cwd();
const normativePaths = [
  "RCF.md",
  ".RCFs/RCF.pesquisa.md",
  ".RCFs/RCF.publicacoes.md",
  ".RCFs/RCF.conversa.md",
  ".RCFs/RCF.epistemologia.md",
  "scripts/publications/RCF.md",
];

const read = (path) => readFileSync(resolve(root, path), "utf8");

function prose(markdown) {
  return markdown
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`[^`]*`/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "");
}

test("suíte RCF preserva uma única seção global de 1 a 58", () => {
  const sections = new Map();
  for (const path of normativePaths.slice(0, 4)) {
    for (const match of read(path).matchAll(/^## (\d+)\./gmu)) {
      const number = Number(match[1]);
      sections.set(number, [...(sections.get(number) ?? []), path]);
    }
  }
  assert.deepEqual([...sections.keys()].sort((a, b) => a - b),
    Array.from({ length: 58 }, (_, index) => index + 1));
  for (const [number, paths] of sections) {
    assert.equal(paths.length, 1, `seção global duplicada: ${number}`);
  }
});

test("RCFs declaram subordinação, precedência e links locais válidos", () => {
  for (const path of normativePaths) {
    const markdown = read(path);
    assert.doesNotMatch(markdown, /\uFFFD/u, `${path} contém UTF-8 inválido`);
    if (path !== "RCF.md") assert.match(markdown, /subordina-se|subordinado/iu);
    for (const match of markdown.matchAll(/\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)/gu)) {
      const target = match[1];
      if (/^(?:https?:|mailto:)/u.test(target)) continue;
      assert.ok(existsSync(resolve(root, dirname(path), target)),
        `${path} aponta para arquivo ausente: ${target}`);
    }
  }
});

test("documentação normativa não conserva grafias portuguesas sem acento", () => {
  const forbidden = [
    "nao", "publicacao", "publicacoes", "operacao", "implementacao",
    "repositorio", "indice", "configuracao", "extracao", "pagina",
    "paginas", "citacao", "citacoes", "referencia", "referencias",
    "traducao", "conclusao", "avaliacao", "validacao", "documentacao",
    "tecnico", "tecnica", "publico", "proposito", "catalogo",
    "automacao", "conteudo", "seguranca", "migracao", "execucao",
    "edicao", "titulo", "numero", "secao", "capitulo", "localizacao",
    "evidencia", "confianca", "analise", "normalizacao", "associacao",
    "diferenca", "diferencas", "tambem", "possivel",
  ];
  for (const path of normativePaths) {
    const text = prose(read(path));
    for (const word of forbidden) {
      assert.doesNotMatch(text,
        new RegExp(`(?<![\\p{L}\\p{N}_])${word}(?![\\p{L}\\p{N}_])`, "iu"),
        `${path} contém grafia sem acento: ${word}`);
    }
  }
});

test("RCF raiz e README distinguem finalidade, corpus e estado real", () => {
  const rcf = read("RCF.md");
  const readme = read("README.md");
  for (const text of [rcf, readme]) {
    assert.match(text, /Bíblia/u);
    assert.match(text, /Ellen G\. White/u);
    assert.match(text, /pioneiros\s+adventistas/iu);
    assert.match(text, /probatóri/iu);
    assert.match(text, /hermenêutic/iu);
    assert.match(text, /planejad/iu);
  }
  assert.match(rcf, /disponíveis:[\s\S]*parciais:[\s\S]*planejados:/iu);
  assert.match(readme, /\*\*Disponível:\*\*[\s\S]*\*\*Parcial:\*\*[\s\S]*\*\*Planejado:\*\*/u);
  assert.match(readme, /ainda não estão\s+disponíveis/iu);
});

test("página e configuração não posicionam o produto como acervo", () => {
  const landing = read("src/site/index.html");
  const config = JSON.parse(read("config/site.json"));
  assert.doesNotMatch(landing, /<title>[^<]*acervo/iu);
  assert.doesNotMatch(landing, /class="eyebrow">[^<]*acervo/iu);
  assert.doesNotMatch(config.description, /acervo/iu);
  assert.match(landing, /ferramenta planejada/iu);
  assert.match(landing, /ainda são planejadas/iu);
});
