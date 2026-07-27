/**
 * Prepara o runtime Python isolado necessário ao coletor de publicações.
 * É acionado pelos ciclos npm e nunca executa a CLI, navegador ou coleta remota.
 */
const { createHash } = require("node:crypto");
const { existsSync, mkdirSync, readFileSync, writeFileSync } = require("node:fs");
const { join, resolve } = require("node:path");
const { spawnSync } = require("node:child_process");

const PROJECT_ROOT = resolve(__dirname, "..", "..");
const REQUIREMENTS = join(PROJECT_ROOT, "scripts", "publications", "requirements.txt");
const ENVIRONMENT = join(PROJECT_ROOT, "constructor", ".state", "publications-python");
const STATE_FILE = join(ENVIRONMENT, ".egw-bootstrap.json");
const PYTHON = process.platform === "win32"
  ? join(ENVIRONMENT, "Scripts", "python.exe")
  : join(ENVIRONMENT, "bin", "python");

type Result = { status: number | null; stdout: string; stderr: string; error?: Error };

function run(command: string, args: string[]): Result {
  const result = spawnSync(command, args, {
    cwd: PROJECT_ROOT,
    encoding: "utf8",
    shell: false,
  });
  return {
    status: result.status,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    error: result.error,
  };
}

function fail(message: string, detail = ""): never {
  const suffix = detail.trim() ? ` ${detail.trim()}` : "";
  throw new Error(`BOOTSTRAP_PYTHON_FALHOU: ${message}.${suffix}`);
}

function requirementHash(): string {
  if (!existsSync(REQUIREMENTS)) {
    fail(`arquivo de requisitos ausente em ${REQUIREMENTS}`);
  }
  return createHash("sha256").update(readFileSync(REQUIREMENTS)).digest("hex");
}

function discoverPython(): string {
  const requested = process.env.BOOTSTRAP_PYTHON;
  const candidates = requested ? [requested] : process.platform === "win32"
    ? ["python", "py"]
    : ["python3", "python"];

  for (const candidate of candidates) {
    const args = candidate === "py" ? ["-3", "--version"] : ["--version"];
    const result = run(candidate, args);
    if (result.status === 0 && /Python 3\./u.test(`${result.stdout}${result.stderr}`)) {
      return candidate;
    }
  }
  fail("Python 3 não encontrado", "Instale Python 3 ou defina BOOTSTRAP_PYTHON com o interpretador compatível");
}

function venvArguments(python: string): string[] {
  return python === "py" ? ["-3", "-m", "venv", ENVIRONMENT] : ["-m", "venv", ENVIRONMENT];
}

function execute(command: string, args: string[], description: string): void {
  const result = run(command, args);
  if (result.status !== 0) {
    fail(description, result.stderr || result.stdout || result.error?.message || "sem diagnóstico do processo");
  }
}

function readArgs(): { dryRun: boolean; check: boolean; json: boolean } {
  const allowed = new Set(["--dry-run", "--check", "--json"]);
  for (const argument of process.argv.slice(2)) {
    if (!allowed.has(argument)) {
      fail(`argumento não suportado ${argument}`);
    }
  }
  return {
    dryRun: process.argv.includes("--dry-run"),
    check: process.argv.includes("--check"),
    json: process.argv.includes("--json"),
  };
}

function report(payload: Record<string, unknown>, json: boolean): void {
  if (json) {
    process.stdout.write(`${JSON.stringify(payload)}\n`);
    return;
  }
  process.stdout.write(`[bootstrap:publications] ${payload.status}: ${payload.message}\n`);
}

function main(): void {
  const options = readArgs();
  const hash = requirementHash();
  const environmentExists = existsSync(PYTHON);

  if (options.dryRun) {
    report({
      status: "planned",
      message: "ambiente Python do coletor seria verificado ou criado; nenhuma instalação foi executada",
      environment: ENVIRONMENT,
      requirements: REQUIREMENTS,
      requirementsSha256: hash,
      environmentExists,
    }, options.json);
    return;
  }

  if (!environmentExists) {
    if (options.check) {
      fail(`ambiente Python ausente em ${ENVIRONMENT}`, "Execute npm run publications:bootstrap");
    }
    const python = discoverPython();
    mkdirSync(resolve(ENVIRONMENT, ".."), { recursive: true });
    execute(python, venvArguments(python), "não foi possível criar o ambiente Python local");
  }

  execute(PYTHON, ["-m", "pip", "--version"], "pip indisponível no ambiente Python local");
  if (!options.check) {
    execute(
      PYTHON,
      ["-m", "pip", "install", "--disable-pip-version-check", "--no-input", "--requirement", REQUIREMENTS],
      "não foi possível instalar os requisitos Python declarados",
    );
  }
  execute(PYTHON, ["-m", "pip", "check"], "dependências Python inconsistentes");

  writeFileSync(STATE_FILE, `${JSON.stringify({
    schema: 1,
    requirementsSha256: hash,
    python: PYTHON,
  }, null, 2)}\n`, "utf8");
  report({
    status: options.check ? "validated" : "ready",
    message: options.check
      ? "ambiente Python do coletor validado"
      : "ambiente Python do coletor preparado sem executar a CLI",
    environment: ENVIRONMENT,
    requirementsSha256: hash,
  }, options.json);
}

try {
  main();
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 3;
}
