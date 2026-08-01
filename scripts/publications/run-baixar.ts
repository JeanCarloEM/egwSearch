/** Executa a CLI do coletor com o interpretador do ambiente local preparado. */
const { existsSync, readFileSync } = require("node:fs");
const { resolve, join, relative } = require("node:path");
const { spawnSync } = require("node:child_process");

const root = resolve(__dirname, "..", "..");
const configuration = JSON.parse(
  readFileSync(join(root, "config", "publications.json"), "utf8"),
);
const runtimeRoot = resolve(
  root,
  String(configuration.runtime_state_root || configuration.state_root || ""),
);
const runtimeRelation = relative(root, runtimeRoot);
if (!runtimeRelation || runtimeRelation.startsWith("..")) {
  process.stderr.write("runtime_state_root inválido.\n");
  process.exit(3);
}
const python = process.platform === "win32"
  ? join(runtimeRoot, "environments", "python", "Scripts", "python.exe")
  : join(runtimeRoot, "environments", "python", "bin", "python");

if (!existsSync(python)) {
  process.stderr.write("Ambiente Python ausente. Execute npm run publications:bootstrap.\n");
  process.exitCode = 3;
} else {
  const result = spawnSync(python, [join(root, "scripts", "publications", "baixar.py"), ...process.argv.slice(2)], {
    cwd: root,
    stdio: "inherit",
    shell: false,
  });
  if (result.error) {
    process.stderr.write(`${result.error.message}\n`);
    process.exitCode = 3;
  } else {
    process.exitCode = result.status ?? 3;
  }
}
