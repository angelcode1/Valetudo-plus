"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const policy = require("../../lib/robots/dreame/DreameX40CleanGeniusPolicy");
const {readFreshNativeSettings} = require("../../lib/robots/dreame/DreameX40NativeSettingsReadOnly");

function fakeRobot(value, options = {}) {
    const calls = [];
    return {
        calls,
        allowExperimentalCleanGenius: options.experimental === true,
        allowCleanGeniusObserveOnly: options.observeOnly === true,
        miotHelper: {
            async readProperty(siid, piid) {
                calls.push(["read", siid, piid]);
                return value;
            },
            async writeProperty() {
                throw new Error("DO_NOT_WRITE");
            }
        },
        async pollState() {
            throw new Error("DO_NOT_POLL_STATE");
        },
        parseAndUpdateState() {
            throw new Error("DO_NOT_PARSE_STATE");
        }
    };
}

test("fresh read calls MIOT 4:50 once without poll or parser", async () => {
    const robot = fakeRobot(JSON.stringify([
        {k: "SmartHost", v: 1},
        {k: "SmartAutoWash", v: -1},
        {k: "SmartAutoMop", v: -2},
        {k: "StainIdentify", v: 1},
        {k: "HotWash", v: 1},
        {k: "authSecret", v: "DO_NOT_LEAK"}
    ]));
    const status = await readFreshNativeSettings(robot);
    assert.deepEqual(robot.calls, [["read", 4, 50]]);
    assert.equal(status.state, "observed");
    assert.equal(status.stale, false);
    assert.equal(status.readOnly, true);
    assert.equal(status.ageMs, 0);
    assert.equal(status.settings.cleanGenius.value, 1);
    assert.equal(status.settings.autoRewash.value, -1);
    assert.equal(status.settings.autoRewash.state, "unknown");
    assert.equal(status.settings.autoReclean.value, -2);
    assert.equal(status.settings.autoReclean.state, "unknown");
    assert.equal(status.nativeEffectiveOperation, "unverified");
    assert.equal(JSON.stringify(status).includes("DO_NOT_LEAK"), false);
});

test("observe-only policy is explicit and defaults to legacy protection", () => {
    assert.equal(policy.isObserveOnlyEnabled({}), false);
    assert.equal(policy.isObserveOnlyEnabled({VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY: "0"}), false);
    assert.equal(policy.isObserveOnlyEnabled({VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY: "1"}), true);
    assert.equal(policy.shouldAutoDisableSmartHost(2, {}), true);
    assert.equal(policy.shouldAutoDisableSmartHost(2, {allowCleanGeniusObserveOnly: true}), false);
    assert.equal(policy.shouldAutoDisableSmartHost(2, {allowExperimentalCleanGenius: true}), false);
    assert.equal(policy.shouldAutoDisableSmartHost(0, {}), false);
    assert.equal(policy.shouldAutoDisableSmartHost(-1, {}), false);
});

test("fresh response distinguishes observe-only from active native controls", async () => {
    const status = await readFreshNativeSettings(fakeRobot('[{"k":"SmartHost","v":0}]', {observeOnly: true}));
    assert.equal(status.valetudoPolicy, "observe_only_preserve_smart_host");
});

test("invalid payload or failed transport cannot generate settings", async () => {
    await assert.rejects(() => readFreshNativeSettings(fakeRobot("{}")), /Invalid MIOT 4:50 settings collection/);
    await assert.rejects(() => readFreshNativeSettings(fakeRobot(77)), /not a string/);
    await assert.rejects(() => readFreshNativeSettings(fakeRobot("x".repeat(32769))), /payload length/);
    const robot = fakeRobot(null);
    robot.miotHelper.readProperty = async () => {throw new Error("robot read failed");};
    await assert.rejects(() => readFreshNativeSettings(robot), /robot read failed/);
});
