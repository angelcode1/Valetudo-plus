"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const research = require("../../../lib/robots/dreame/DreameX40CleanGeniusResearch");

test("experimental feature is opt-in", () => {
    assert.equal(research.isEnabled({}), false);
    assert.equal(research.isEnabled({VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "0"}), false);
    assert.equal(research.isEnabled({VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1"}), true);
});

test("rejects an unrecognized mode", () => {
    const definition = research.SETTINGS[0];
    assert.equal(research.decodeValue(1, definition), "routine");
    assert.throws(() => research.decodeValue(200, definition), /Unsupported/);
});

test("fails closed when task or mode is unknown/active", () => {
    assert.equal(research.isIdle({}), false);
    assert.equal(research.isIdle({ephemeralState: {mode: 0}}), false);
    assert.equal(research.isIdle({ephemeralState: {mode: 0, taskStatus: 0}}), true);
    assert.equal(research.isIdle({ephemeralState: {mode: 1, taskStatus: 0}}), false);
    assert.equal(research.isIdle({ephemeralState: {mode: 0, taskStatus: 1}}), false);
});

test("quirk rejects active cleaning without writing", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 1, taskStatus: 1},
        miotHelper: {
            readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
            writeProperty: async () => { writes++; }
        }
    };
    const [quirk] = research.createQuirks(robot);
    await assert.rejects(() => quirk.setter("routine"), /idle/);
    assert.equal(writes, 0);
});

test("quirk uses a single-key update only when idle and supported", async () => {
    const writes = [];
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
            writeProperty: async (...args) => { writes.push(args); }
        }
    };
    const [quirk] = research.createQuirks(robot);
    await quirk.setter("routine");
    assert.deepEqual(writes, [[4, 50, '{"k":"SmartHost","v":1}']]);
});

test("absent setting cannot cause a write", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperty: async () => JSON.stringify([{k: "CleanRoute", v: 1}]),
            writeProperty: async () => { writes++; }
        }
    };
    const [quirk] = research.createQuirks(robot);
    await assert.rejects(() => quirk.setter("routine"), /Unsupported/);
    assert.equal(writes, 0);
});
