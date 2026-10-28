"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const DreameX40UltraValetudoRobot = require("../../../../lib/robots/dreame/DreameX40UltraValetudoRobot");

test("MIOT transport failure invalidates both X40 read-only snapshots", async () => {
    // Avoid starting the actual robot or any network client. The inherited
    // polling implementation needs only the stubbed MIOT helper and poll list.
    const robot = Object.create(DreameX40UltraValetudoRobot.prototype);
    robot.statePropertiesToPoll = [];
    robot.x40CleanGeniusObservation = {observedAtMs: 1, fields: {}};
    robot.x40CachedIdleObservation = {observedAtMs: 1, mode: 6, taskStatus: 0};
    robot.x40DockWashObservation = {observedAtMs: 1, value: {raw: 1, state: "cleaning"}, transitions: []};
    robot.miotHelper = {
        readProperties: async () => {
            throw new Error("Simulated MIOT transport failure");
        }
    };

    await assert.rejects(() => robot.pollState(), /Simulated MIOT transport failure/);
    const status = robot.getCleanGeniusReadOnlyStatus(1000);

    assert.equal(status.state, "unavailable");
    assert.equal(status.pollHealth.state, "failed");
    assert.equal(typeof status.pollHealth.lastAttemptAt, "string");
    assert.equal(status.cachedIdle.state, "unavailable");
    assert.equal(status.cachedIdle.cachedGuardMatch, false);
    assert.equal(status.dockWashActivity.state, "unavailable");
    assert.deepEqual(status.dockWashActivity.transitions, []);
});

test("successful MIOT poll does not discard read-only observations", async () => {
    const robot = Object.create(DreameX40UltraValetudoRobot.prototype);
    robot.state = {attributes: []};
    robot.statePropertiesToPoll = [];
    robot.x40CleanGeniusObservation = {observedAtMs: 1000, fields: {}};
    robot.x40CachedIdleObservation = {observedAtMs: 1000, mode: 6, taskStatus: 0};
    robot.x40DockWashObservation = {observedAtMs: 1000, value: {raw: 1, state: "cleaning"}, transitions: []};
    robot.miotHelper = {
        readProperties: async () => []
    };
    // Focus on the inherited poll orchestration, not unrelated state decoding.
    robot.parseAndUpdateState = () => {};

    const result = await robot.pollState();
    assert.equal(result, robot.state);
    assert.equal(robot.x40CleanGeniusObservation.observedAtMs, 1000);
    assert.equal(robot.x40DockWashObservation.value.raw, 1);
    assert.equal(robot.x40CachedIdleObservation.mode, 6);
    assert.equal(robot.getCleanGeniusReadOnlyStatus().pollHealth.state, "succeeded");
});

test("X40 read-only status distinguishes no poll from a completed poll missing observations", async () => {
    const robot = Object.create(DreameX40UltraValetudoRobot.prototype);
    robot.state = {attributes: []};
    robot.statePropertiesToPoll = [];
    robot.x40CleanGeniusObservation = null;
    robot.x40DockWashObservation = null;
    robot.x40CachedIdleObservation = null;
    const before = robot.getCleanGeniusReadOnlyStatus();
    assert.equal(before.pollHealth.state, "not_started");
    assert.equal(before.pollHealth.lastAttemptAt, null);
    assert.equal(before.cachedIdle.cachedGuardMatch, false);

    // A resolved poll with no useful response must not be mistaken for idle.
    robot.miotHelper = {readProperties: async () => []};
    const result = await robot.pollState();
    assert.equal(result, robot.state);
    const after = robot.getCleanGeniusReadOnlyStatus();
    assert.equal(after.pollHealth.state, "succeeded");
    assert.equal(typeof after.pollHealth.lastAttemptAt, "string");
    assert.equal(after.state, "unavailable");
    assert.equal(after.cachedIdle.state, "unavailable");
    assert.equal(after.cachedIdle.cachedGuardMatch, false);
});

test("X40 read-only status shows poll in progress without a second MIOT request", async () => {
    const robot = Object.create(DreameX40UltraValetudoRobot.prototype);
    robot.state = {attributes: []};
    robot.statePropertiesToPoll = [];
    robot.x40CleanGeniusObservation = null;
    robot.x40DockWashObservation = null;
    robot.x40CachedIdleObservation = null;
    let calls = 0;
    let release;
    const gated = new Promise(resolve => {
        release = resolve;
    });
    robot.miotHelper = {readProperties: async () => {
        calls++;
        await gated;
        return [];
    }};
    const pending = robot.pollState();
    const during = robot.getCleanGeniusReadOnlyStatus();
    assert.equal(during.pollHealth.state, "in_progress");
    assert.equal(typeof during.pollHealth.lastAttemptAt, "string");
    assert.equal(calls, 1);
    assert.equal(during.cachedIdle.cachedGuardMatch, false);
    release();
    await pending;
    assert.equal(calls, 1);
    assert.equal(robot.getCleanGeniusReadOnlyStatus().pollHealth.state, "succeeded");
});

test("X40 poll failure after a success clears prior readings and reports failed", async () => {
    const robot = Object.create(DreameX40UltraValetudoRobot.prototype);
    robot.state = {attributes: []};
    robot.statePropertiesToPoll = [];
    robot.x40CleanGeniusObservation = null;
    robot.x40DockWashObservation = null;
    robot.x40CachedIdleObservation = null;
    robot.miotHelper = {readProperties: async () => []};
    await robot.pollState();
    assert.equal(robot.getCleanGeniusReadOnlyStatus().pollHealth.state, "succeeded");

    robot.miotHelper = {readProperties: async () => {
        throw new Error("PRIVATE_DEVICE_FAILURE");
    }};
    await assert.rejects(() => robot.pollState(), /PRIVATE_DEVICE_FAILURE/);
    const output = robot.getCleanGeniusReadOnlyStatus();
    assert.equal(output.pollHealth.state, "failed");
    assert.equal(output.cachedIdle.cachedGuardMatch, false);
    assert.equal(JSON.stringify(output).includes("PRIVATE_DEVICE_FAILURE"), false);
});
