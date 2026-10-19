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
    robot.x40DockWashObservation = {observedAtMs: 1, value: {raw: 1, state: "cleaning"}, transitions: []};
    robot.miotHelper = {
        readProperties: async () => {
            throw new Error("Simulated MIOT transport failure");
        }
    };

    await assert.rejects(() => robot.pollState(), /Simulated MIOT transport failure/);
    const status = robot.getCleanGeniusReadOnlyStatus(1000);

    assert.equal(status.state, "unavailable");
    assert.equal(status.dockWashActivity.state, "unavailable");
    assert.deepEqual(status.dockWashActivity.transitions, []);
});

test("successful MIOT poll does not discard read-only observations", async () => {
    const robot = Object.create(DreameX40UltraValetudoRobot.prototype);
    robot.state = {attributes: []};
    robot.statePropertiesToPoll = [];
    robot.x40CleanGeniusObservation = {observedAtMs: 1000, fields: {}};
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
});
