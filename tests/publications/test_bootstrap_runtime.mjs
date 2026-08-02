import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { resolve } from "node:path";
import { readFileSync } from "node:fs";

const root = resolve(import.meta.dirname, "..", "..");
const bootstrap = resolve(root, "scripts", "publications", "bootstrap-runtime.ts");

test("o plano do bootstrap não cria ambiente nem executa a CLI", () => {
  const result = spawnSync(process.execPath, [bootstrap, "--dry-run", "--json"], {
    cwd: root,
    encoding: "utf8",
  });

  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, "planned");
  assert.match(payload.requirements, /scripts[\\/]publications[\\/]requirements\.txt$/u);
  assert.match(
    payload.environment,
    /constructor[\\/]\.state[\\/]egwsearch[\\/]environments[\\/]python$/u,
  );
});

test("argumento desconhecido falha com diagnóstico próprio", () => {
  const result = spawnSync(process.execPath, [bootstrap, "--invalido"], {
    cwd: root,
    encoding: "utf8",
  });

  assert.equal(result.status, 3);
  assert.match(result.stderr, /BOOTSTRAP_PYTHON_FALHOU/u);
});

test("os ciclos npm expõem bootstrap para instalação e atualização", () => {
  const manifest = JSON.parse(readFileSync(resolve(root, "package.json"), "utf8"));
  assert.match(manifest.scripts.postinstall, /bootstrap-runtime\.ts/u);
  assert.match(manifest.scripts.dependencies, /bootstrap-runtime\.ts/u);
  assert.match(manifest.scripts.update, /publications:bootstrap/u);
  assert.match(manifest.scripts["publications:analyze"], /publication_analysis\.py/u);
  assert.match(manifest.scripts["publications:index"], /publication_index\.py/u);
});
