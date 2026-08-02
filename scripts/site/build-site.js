"use strict";
// Repository: https://github.com/JeanCarloEM/egwSearch
// License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
// This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const node_crypto_1 = require("node:crypto");
const node_fs_1 = require("node:fs");
const node_path_1 = require("node:path");
const sass = __importStar(require("sass"));
const repositoryRoot = (0, node_path_1.resolve)(__dirname, "../..");
const forbiddenNames = new Set(["__pycache__"]);
const forbiddenSuffixes = [".pyc", ".tmp", ".partial", ".md"];
function within(root, candidate) {
    const rel = (0, node_path_1.relative)((0, node_path_1.resolve)(root), (0, node_path_1.resolve)(candidate));
    return rel === "" || (!rel.startsWith(`..${node_path_1.sep}`) && rel !== "..");
}
function configuredPath(root, value) {
    const target = (0, node_path_1.resolve)(root, value);
    if (!within(root, target))
        throw new Error(`path fora do repositório: ${value}`);
    return target;
}
function forbidden(path) {
    const name = path.split(/[\\/]/).at(-1) ?? "";
    return (forbiddenNames.has(name) ||
        forbiddenSuffixes.some((suffix) => name.endsWith(suffix)));
}
function walk(root, ignoreForbidden = false) {
    const result = [];
    for (const entry of (0, node_fs_1.readdirSync)(root, { withFileTypes: true })) {
        const path = (0, node_path_1.join)(root, entry.name);
        if (entry.isSymbolicLink())
            throw new Error(`symlink proibido: ${path}`);
        if (forbidden(path)) {
            if (ignoreForbidden)
                continue;
            throw new Error(`intermediário proibido: ${path}`);
        }
        if (entry.isDirectory())
            result.push(...walk(path, ignoreForbidden));
        else if (entry.isFile())
            result.push(path);
    }
    return result.sort();
}
function digests(path) {
    const payload = (0, node_fs_1.readFileSync)(path);
    return {
        sha256: (0, node_crypto_1.createHash)("sha256").update(payload).digest("hex"),
        sha512: (0, node_crypto_1.createHash)("sha512").update(payload).digest("hex"),
    };
}
function sha256(path) {
    return (0, node_crypto_1.createHash)("sha256").update((0, node_fs_1.readFileSync)(path)).digest("hex");
}
function renderTemplate(source, replacements) {
    let rendered = source;
    for (const [name, value] of Object.entries(replacements)) {
        rendered = rendered.replaceAll(`{{${name}}}`, value);
    }
    if (rendered.includes("{{"))
        throw new Error("template público não resolvido");
    return rendered.trimEnd() + "\n";
}
function loadConfiguration() {
    const config = JSON.parse((0, node_fs_1.readFileSync)((0, node_path_1.join)(repositoryRoot, "config/site.json"), "utf8"));
    if (config.schema_version !== 1)
        throw new Error("schema de site incompatível");
    if (!/^\/[A-Za-z0-9._~/-]*\/$/.test(config.base_path)) {
        throw new Error("base_path público inválido");
    }
    if (!/^[a-z0-9.-]+$/.test(config.custom_domain)) {
        throw new Error("domínio público inválido");
    }
    return config;
}
function validateLanding(html) {
    const forbidden = ["/publications", "index.json", ".epub", ".pdf", "cover.png"];
    for (const token of forbidden) {
        if (html.toLowerCase().includes(token)) {
            throw new Error(`página institucional expõe acervo: ${token}`);
        }
    }
    if (/<a\b/i.test(html))
        throw new Error("página institucional contém link");
    for (const required of ["<main", "<h1", "viewport", "lang=\"pt-BR\""]) {
        if (!html.includes(required))
            throw new Error(`HTML sem requisito: ${required}`);
    }
}
function validateIndex(publicationsRoot) {
    const indexPath = (0, node_path_1.join)(publicationsRoot, "index.json");
    const index = JSON.parse((0, node_fs_1.readFileSync)(indexPath, "utf8"));
    if (index.schema_version !== "publication-global-index/v1") {
        throw new Error("schema do índice público incompatível");
    }
    if (!Array.isArray(index.publications) || index.publications.length === 0) {
        throw new Error("índice público sem publicações");
    }
    const indexedAssets = new Set();
    for (const publication of index.publications) {
        if (!publication.cover)
            throw new Error(`publicação sem capa: ${publication.path}`);
        const records = [publication.metadata, publication.cover, ...publication.assets];
        if (publication.assets.length === 0) {
            throw new Error(`publicação sem EPUB/PDF: ${publication.path}`);
        }
        for (const record of records) {
            const path = configuredPath(publicationsRoot, record.path);
            if (!(0, node_fs_1.existsSync)(path) || !(0, node_fs_1.lstatSync)(path).isFile()) {
                throw new Error(`recurso público ausente: ${record.path}`);
            }
            if ("hashes" in record) {
                const hashed = record;
                const actual = digests(path);
                if (actual.sha256 !== hashed.hashes.sha256) {
                    throw new Error(`SHA-256 divergente: ${record.path}`);
                }
                if (actual.sha512 !== hashed.hashes.sha512) {
                    throw new Error(`SHA-512 divergente: ${record.path}`);
                }
                indexedAssets.add(record.path.replaceAll("/", node_path_1.sep));
            }
        }
    }
    return { index, indexedAssets };
}
function validateProjection(source, target, indexedAssets) {
    const sourceFiles = walk(source, true);
    const targetFiles = walk(target);
    const sourceRelative = sourceFiles.map((path) => (0, node_path_1.relative)(source, path));
    const targetRelative = targetFiles.map((path) => (0, node_path_1.relative)(target, path));
    if (JSON.stringify(sourceRelative) !== JSON.stringify(targetRelative)) {
        throw new Error("projeção pública não corresponde integralmente à origem");
    }
    for (let index = 0; index < sourceFiles.length; index += 1) {
        const original = sourceFiles[index];
        const published = targetFiles[index];
        if ((0, node_fs_1.statSync)(original).size !== (0, node_fs_1.statSync)(published).size) {
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
function build() {
    const config = loadConfiguration();
    const siteSource = configuredPath(repositoryRoot, config.source_root);
    const publicationsSource = configuredPath(repositoryRoot, config.publications_root);
    const output = configuredPath(repositoryRoot, config.output_root);
    if (output !== (0, node_path_1.join)(repositoryRoot, "dist"))
        throw new Error("output não autorizado");
    walk(publicationsSource, true);
    (0, node_fs_1.rmSync)(output, { recursive: true, force: true });
    (0, node_fs_1.mkdirSync)((0, node_path_1.join)(output, "assets"), { recursive: true });
    const css = sass.compile((0, node_path_1.join)(siteSource, "styles/main.scss"), {
        style: "compressed",
        sourceMap: false,
    }).css;
    (0, node_fs_1.writeFileSync)((0, node_path_1.join)(output, "assets/main.css"), css + "\n", "utf8");
    for (const page of ["index.html", "404.html"]) {
        const html = renderTemplate((0, node_fs_1.readFileSync)((0, node_path_1.join)(siteSource, page), "utf8"), page === "404.html"
            ? { INLINE_CSS: css }
            : { STYLESHEET_PATH: "assets/main.css" });
        if (page === "index.html")
            validateLanding(html);
        (0, node_fs_1.writeFileSync)((0, node_path_1.join)(output, page), html, "utf8");
    }
    (0, node_fs_1.writeFileSync)((0, node_path_1.join)(output, ".nojekyll"), "", "utf8");
    (0, node_fs_1.cpSync)(publicationsSource, (0, node_path_1.join)(output, "publications"), {
        recursive: true,
        preserveTimestamps: false,
        filter: (path) => !forbidden(path),
    });
    validate();
}
function validate() {
    const config = loadConfiguration();
    const source = configuredPath(repositoryRoot, config.publications_root);
    const output = configuredPath(repositoryRoot, config.output_root);
    if (!(0, node_fs_1.existsSync)((0, node_path_1.join)(output, ".nojekyll")))
        throw new Error(".nojekyll ausente");
    const html = (0, node_fs_1.readFileSync)((0, node_path_1.join)(output, "index.html"), "utf8");
    validateLanding(html);
    const validation = validateIndex((0, node_path_1.join)(output, "publications"));
    const files = validateProjection(source, (0, node_path_1.join)(output, "publications"), validation.indexedAssets);
    const bytes = walk(output).reduce((sum, path) => sum + (0, node_fs_1.statSync)(path).size, 0);
    console.log(`SITE_PUBLICATION_OK publications=${validation.index.publications.length} files=${files} bytes=${bytes}`);
}
const command = process.argv[2] ?? "build";
try {
    if (command === "build")
        build();
    else if (command === "validate")
        validate();
    else
        throw new Error(`comando inválido: ${command}`);
}
catch (error) {
    console.error(`SITE_PUBLICATION_ERROR ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
}
