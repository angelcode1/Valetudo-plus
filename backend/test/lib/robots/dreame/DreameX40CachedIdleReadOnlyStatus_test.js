"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const status = require("../../../../lib/robots/dreame/DreameX40CachedIdleReadOnlyStatus");

test("reports a valid raw docked-looking mode without declaring it idle", () => {
    const observation = status.observe([
        {siid: 4, piid: 1, code: 0, value: 6},
        {siid: 4, piid: 7, code: 0, value: 0}
    ], 1000);
    const report = status.buildStatus(observation, 1000);
    assert.equal(report.state, "observed");
    assert.equal(report.mode, 6);
    assert.equal(report.taskStatus, 0);
    assert.equal(report.cachedGuardMatch, false);
});

test("observed zero pair matches cache guard, but is not a fresh permission to write", () => {
    const observation = status.observe([
        {siid: 4, piid: 1, code: 0, value: 0},
        {siid: 4, piid: 7, code: 0, value: 0}
    ], 1000);
    const report = status.buildStatus(observation, 1000);
    assert.equal(report.cachedGuardMatch, true);
    const stale = status.buildStatus(observation, 1001 + status.STALE_AFTER_MS);
    assert.equal(stale.state, "stale");
    assert.equal(stale.mode, null);
    assert.equal(stale.taskStatus, null);
    assert.equal(stale.cachedGuardMatch, false);
});

test("missing, invalid, string, duplicate and errored pairs are not available", () => {
    const cases = [
        [{siid: 4, piid: 1, code: 0, value: 0}],
        [{siid: 4, piid: 1, code: 0, value: 0}, {siid: 4, piid: 7, code: -1, value: 0}],
        [{siid: 4, piid: 1, code: 0, value: "0"}, {siid: 4, piid: 7, code: 0, value: 0}],
        [{siid: 4, piid: 1, code: 0, value: 0}, {siid: 4, piid: 1, code: 0, value: 0},
            {siid: 4, piid: 7, code: 0, value: 0}]
    ];
    cases.forEach(entries => {
        assert.equal(status.observe(entries, 1000), null);
        assert.equal(status.buildStatus(status.observe(entries, 1000), 1000).state, "unavailable");
    });
    assert.equal(status.observe([], 1000), undefined);
    assert.equal(status.buildStatus(null).cachedGuardMatch, false);
});

test("clock regression makes a prior observation unavailable", () => {
    const obs = status.observe([
        {siid: 4, piid: 1, code: 0, value: 0},
        {siid: 4, piid: 7, code: 0, value: 0}
    ], 2000);
    const result = status.buildStatus(obs, 1999);
    assert.equal(result.state, "unavailable");
    assert.equal(result.cachedGuardMatch, false);
});
