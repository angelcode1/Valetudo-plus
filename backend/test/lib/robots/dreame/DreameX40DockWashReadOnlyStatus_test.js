"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const dock = require("../../../../lib/robots/dreame/DreameX40DockWashReadOnlyStatus");

test("records only changes while identical readings refresh age", () => {
    let observation = dock.observe(null, 0, 1000);
    observation = dock.observe(observation, 0, 1500);
    assert.equal(observation.transitions.length, 1);
    observation = dock.observe(observation, 1, 2000);
    observation = dock.observe(observation, 2, 2400);
    const result = dock.buildStatus(observation, 2500);
    assert.equal(result.current.state, "drying");
    assert.equal(result.current.raw, 2);
    assert.equal(result.ageMs, 100);
    assert.equal(result.transitions.length, 3);
    assert.deepEqual(result.transitions.map(t => t.state), ["idle", "cleaning", "drying"]);
});

test("uncertain and unsupported code values remain unknown", () => {
    assert.deepEqual(dock.decode(-1), {raw: -1, state: "unknown"});
    assert.deepEqual(dock.decode(3), {raw: 3, state: "cleaning_unverified_variant"});
    assert.deepEqual(dock.decode("1"), {raw: null, state: "unknown"});
    const state = dock.buildStatus(dock.observe(null, -1, 3000), 3000);
    assert.equal(state.current.raw, -1);
    assert.equal(state.current.state, "unknown");
});

test("rejects invalid and out-of-order observations", () => {
    assert.throws(() => dock.observe(null, "1", 1000), /Invalid/);
    assert.throws(() => dock.observe(null, 1.2, 1000), /Invalid/);
    assert.throws(() => dock.observe(null, 1, NaN), /Invalid/);
    assert.throws(() => dock.observe(dock.observe(null, 1, 2000), 2, 1000), /Out-of-order/);
});

test("bounds history and makes stale/unavailable explicit", () => {
    let observation = null;
    for (let i = 0; i < 30; i++) {
        observation = dock.observe(observation, i % 2, i * 1000);
    }
    assert.equal(dock.buildStatus(observation, 30000).transitions.length, dock.MAX_TRANSITIONS);
    const stale = dock.buildStatus(observation, observation.observedAtMs + dock.STALE_AFTER_MS + 1);
    assert.equal(stale.state, "stale");
    assert.equal(stale.stale, true);
    const unavailable = dock.buildStatus(null);
    assert.equal(unavailable.state, "unavailable");
    assert.equal(unavailable.current.state, "unavailable");
    assert.deepEqual(unavailable.transitions, []);
});

test("output is an allowlist without raw MIOT payloads", () => {
    const obj = dock.buildStatus(dock.observe(null, 5, 1000), 1000);
    assert.deepEqual(Object.keys(obj.current), ["raw", "state"]);
    assert.equal(obj.dataType, "dock_activity_not_dirtiness_or_rewash_reason");
    assert.equal(obj.transitions[0].raw, 5);
});


test("clock regression hides the apparent current dock state and transitions", () => {
    const snapshot = dock.observe(null, 1, 2000);
    const result = dock.buildStatus(snapshot, 1999);
    assert.equal(result.state, "unavailable");
    assert.deepEqual(result.current, {raw: null, state: "unavailable"});
    assert.deepEqual(result.transitions, []);
    assert.throws(() => dock.observe(null, 1, 8640000000000001), /Invalid/);
});
