"use strict";

const assert = require("node:assert/strict");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const resolveConfigLocation = require("../../../lib/res/resolveConfigLocation");

test("installed X40 explicit config path overrides DataPath", () => {
    assert.equal(resolveConfigLocation({
        VALETUDO_CONFIG_PATH: "/data/valetudo_config.json",
        VALETUDO_DATA_PATH: "/data/valetudo-x40-fork-stage14"
    }), "/data/valetudo_config.json");
});

test("without explicit override upstream DataPath layout is unchanged", () => {
    assert.equal(resolveConfigLocation({
        VALETUDO_DATA_PATH: "/data/valetudo"
    }), "/data/valetudo/valetudo_config.json");
});

test("without either path the existing OS temp fallback remains", () => {
    assert.equal(resolveConfigLocation({}), path.join(os.tmpdir(), "valetudo_config.json"));
});

test("invalid explicit path cannot silently create a different config", () => {
    for (const badValue of ["", "valetudo_config.json", "../other.json"]) {
        assert.throws(() => resolveConfigLocation({
            VALETUDO_CONFIG_PATH: badValue,
            VALETUDO_DATA_PATH: "/data/valetudo-x40-fork-stage14"
        }), /VALETUDO_CONFIG_PATH must be an absolute path/);
    }
});
