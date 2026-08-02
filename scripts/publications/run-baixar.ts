/** Executa uma CLI de publicações com o interpretador local preparado. */
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

const rawArguments = process.argv.slice(2);
const toolArgument = rawArguments[0]?.startsWith("--tool=") ? rawArguments.shift() : "";
const tool = toolArgument ? toolArgument.slice("--tool=".length) : "baixar.py";
const allowedTools = new Set([
  "baixar.py",
  "publication_analysis.py",
  "publication_covers.py",
  "publication_index.py",
]);

if (!allowedTools.has(tool)) {
  process.stderr.write("Ferramenta de publicações inválida.\n");
  process.exitCode = 2;
} else if (!existsSync(python)) {
  process.stderr.write("Ambiente Python ausente. Execute npm run publications:bootstrap.\n");
  process.exitCode = 3;
} else {
  const result = spawnSync(python, [join(root, "scripts", "publications", tool), ...rawArguments], {
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
