"use strict";

const fs = require("node:fs");
const path = require("node:path");
const {createRequire} = require("node:module");

// Resolve the dependency through the same Express router used by the backend.
const backendRequire = createRequire(path.resolve(__dirname, "../backend/package.json"));
const expressRequire = createRequire(backendRequire.resolve("express"));
const routerRequire = createRequire(expressRequire.resolve("router"));
const source = fs.readFileSync(routerRequire.resolve("path-to-regexp"), "utf8");

// The embedded Node runtime cannot compile Unicode property escapes. The
// dependency patch applied by postinstall replaces them in path-to-regexp.
if (/\\[pP]\{/.test(source)) {
    throw new Error("The packaged router is missing its path-to-regexp patch. Run npm run postinstall at the repository root before building.");
}
