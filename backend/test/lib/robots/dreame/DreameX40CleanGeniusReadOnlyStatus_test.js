"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const status = require("../../../../lib/robots/dreame/DreameX40CleanGeniusReadOnlyStatus");

test("parses a sanitized real X40 observation without inventing meanings", () => {
    const observation = status.observe(JSON.stringify([
        {k: "SmartHost", v: 0},
        {k: "SmartAutoMop", v: -1},
        {k: "SmartAutoWash", v: 0},
        {k: "StainIdentify", v: 1},
        {k: "HotWash", v: 1},
        {k: "MeticulousTwist", v: -7},
        {k: "secret_key", v: "never_reflect_this"}
    ]), 1000);
    const result = status.buildStatus(observation, {nowMs: 1000});
    assert.equal(result.readOnly, true);
    assert.equal(result.state, "observed");
    assert.deepEqual(result.settings.autoReclean, {value: -1, state: "unknown"});
    assert.deepEqual(result.settings.cleanGenius, {value: 0, state: "off"});
    assert.deepEqual(result.settings.autoRewash, {value: 0, state: "off"});
    assert.deepEqual(result.settings.stainIdentification, {value: 1, state: "on_setting"});
    assert.equal(JSON.stringify(result).includes("secret_key"), false);
    assert.equal(JSON.stringify(result).includes("MeticulousTwist"), false);
});

test("unknown, missing and non-integer values fail closed", () => {
    const observation = status.observe(JSON.stringify([
        {k: "SmartHost", v: 42},
        {k: "SmartAutoWash", v: "1"}
    ]), 2000);
    const result = status.buildStatus(observation, {nowMs: 2000});
    assert.deepEqual(result.settings.cleanGenius, {value: 42, state: "unknown"});
    assert.deepEqual(result.settings.autoRewash, {value: null, state: "unknown"});
    assert.deepEqual(result.settings.autoReclean, {value: null, state: "unavailable"});
    assert.deepEqual(status.buildStatus(null).settings.autoReclean, {value: null, state: "unavailable"});
});

test("rejects malformed, oversized, duplicate or ambiguous settings", () => {
    assert.throws(() => status.observe("not-json"), /Invalid/);
    assert.throws(() => status.observe("{}"), /Invalid/);
    assert.throws(() => status.observe(" ".repeat(32769)), /Invalid/);
    assert.throws(() => status.observe(JSON.stringify([
        {k: "SmartHost", v: 0},
        {k: "SmartHost", v: 1}
    ])), /Duplicate/);
});

test("stale data and Valetudo safety policy are explicit", () => {
    const observation = status.observe('[{"k":"SmartHost","v":1}]', 2000);
    assert.equal(status.buildStatus(observation, {nowMs: 2000 + status.STALE_AFTER_MS}).stale, false);
    const result = status.buildStatus(observation, {nowMs: 2001 + status.STALE_AFTER_MS});
    assert.equal(result.state, "stale");
    assert.equal(result.stale, true);
    assert.equal(result.valetudoPolicy, "auto_disable_smart_host_when_positive");
    assert.equal(status.buildStatus(observation, {experimentalEnabled: true}).valetudoPolicy, "experimental_controls_opted_in");
});


test("clock regression cannot make an old setting appear fresh", () => {
    const snapshot = status.observe('[{"k":"SmartHost","v":1}]', 2000);
    const result = status.buildStatus(snapshot, {nowMs: 1999});
    assert.equal(result.state, "unavailable");
    assert.equal(result.ageMs, null);
    assert.deepEqual(result.settings.cleanGenius, {value: null, state: "unavailable"});
    assert.throws(() => status.observe("[]", 8640000000000001), /timestamp/);
});
