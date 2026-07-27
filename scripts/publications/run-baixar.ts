/** Executa a CLI do coletor com o interpretador do ambiente local preparado. */
const { existsSync } = require("node:fs");
const { resolve, join } = require("node:path");
const { spawnSync } = require("node:child_process");

const root = resolve(__dirname, "..", "..");
const python = process.platform === "win32"
  ? join(root, "constructor", ".state", "publications-python", "Scripts", "python.exe")
  : join(root, "constructor", ".state", "publications-python", "bin", "python");

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
