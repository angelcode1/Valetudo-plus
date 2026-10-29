"use strict";

const assert = require("node:assert/strict");
const Preflight = require("../../../../lib/robots/dreame/DreameX40CleanGeniusPreflight");
const Research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");
const Status = require("../../../../lib/robots/dreame/DreameX40CleanGeniusReadOnlyStatus");
const test = require("node:test");

function fixture(overrides = {}) {
    const raw = {mode: 6, task: 0, charging: 1, error: "", dock: 0, ...overrides};
    const values = {"4:1": raw.mode, "4:7": raw.task, "3:2": raw.charging, "4:18": raw.error, "4:25": raw.dock};
    const settings = {SmartHost: 0, SmartAutoMop: -1, SmartAutoWash: 0, ...overrides.settings};
    const writes = [];
    const robot = {
        ephemeralState: {mode: raw.mode, taskStatus: raw.task},
        miotHelper: {
            readProperties: async props => props.map(p => ({...p, code: 0, value: values[`${p.siid}:${p.piid}`]})),
            readProperty: async () => JSON.stringify(Object.entries(settings).map(([k, v]) => ({k: k, v: v}))),
            writeProperty: async (siid, piid, value) => {
                writes.push([siid, piid, value]);
                const delta = JSON.parse(value);
                settings[delta.k] = delta.v;
            }
        }
    };
    return {robot: robot, settings: settings, writes: writes};
}

test("fresh preflight accepts a reordered complete response, never polls or writes", async () => {
    const {robot, writes} = fixture();
    const read = robot.miotHelper.readProperties;
    robot.miotHelper.readProperties = async props => (await read(props)).reverse();
    robot.pollState = () => {
        throw new Error("must not poll");
    };
    robot.parseAndUpdateState = () => {
        throw new Error("must not parse");
    };
    const fresh = await Preflight.readFresh(robot);
    assert.equal(fresh.activationAllowed, true);
    assert.equal(fresh.mode, 6);
    assert.equal(fresh.readOnly, true);
    assert.equal(fresh.blockedReason, null);
    assert.equal(writes.length, 0);
});

test("fresh preflight blocks powersave, tasks, noncharging, errors and dock activity", async () => {
    for (const change of [
        {mode: 14}, {mode: 2}, {mode: 15}, {task: 1}, {charging: 0},
        {error: "68"}, {error: "private credential text"}, {dock: 1}, {dock: 2}, {dock: 4}
    ]) {
        const {robot, writes} = fixture(change);
        const fresh = await Preflight.readFresh(robot);
        assert.equal(fresh.activationAllowed, false);
        assert.equal(typeof fresh.blockedReason, "string");
        assert.equal(JSON.stringify(fresh).includes("private credential"), false);
        await assert.rejects(() => Research.createQuirks(robot)[0].setter("routine"));
        assert.equal(writes.length, 0);
    }
});

test("invalid, duplicate, errored, missing and mistyped fresh observations fail closed", async () => {
    for (const mutate of [
        rows => rows.slice(1),
        rows => [rows[0], rows[0], ...rows.slice(2)],
        rows => rows.map((r, i) => i === 0 ? {...r, code: -1} : r),
        rows => rows.map((r, i) => i === 0 ? {...r, value: "6"} : r),
        rows => rows.map((r, i) => i === 0 ? {...r, piid: 999} : r),
        () => null
    ]) {
        const {robot, writes} = fixture();
        const read = robot.miotHelper.readProperties;
        robot.miotHelper.readProperties = async props => mutate(await read(props));
        await assert.rejects(() => Research.createQuirks(robot)[0].setter("routine"), /fresh MIOT read/);
        assert.equal(writes.length, 0);
    }
});

test("docked activation needs its own fresh safety read and strict single-key readback", async () => {
    const {robot, writes} = fixture();
    let reads = 0;
    const read = robot.miotHelper.readProperties;
    robot.miotHelper.readProperties = async props => {
        reads++;
        return read(props);
    };
    await Research.createQuirks(robot)[0].setter("routine");
    assert.equal(reads, 1);
    assert.deepEqual(writes, [[4, 50, '{"k":"SmartHost","v":1}']]);
});

test("fresh powersave overrides a stale cached idle pair", async () => {
    const {robot, writes} = fixture({mode: 14});
    robot.ephemeralState.mode = 0;
    await assert.rejects(() => Research.createQuirks(robot)[0].setter("routine"), /powersave/);
    assert.equal(writes.length, 0);
});

test("SmartHost recovery to off requires recognized fresh settings, not activation state", async () => {
    for (const mode of [2, 14]) {
        const {robot, writes} = fixture({mode: mode, task: 1, settings: {SmartHost: 1}});
        robot.miotHelper.readProperties = async () => {
            throw new Error("unrelated state unavailable");
        };
        await Research.createQuirks(robot)[0].setter("off");
        assert.deepEqual(writes, [[4, 50, '{"k":"SmartHost","v":0}']]);
    }
    const {robot, writes} = fixture({settings: {SmartHost: -1}});
    await assert.rejects(() => Research.createQuirks(robot)[0].setter("off"), /Unsupported/);
    assert.equal(writes.length, 0);
});

test("advanced signed protocol requires all deliberate environment opt-ins", () => {
    const main = {VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1"};
    const advanced = {...main, VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED: "1"};
    assert.equal(Research.isSignedEnabled({}), false);
    assert.equal(Research.isSignedEnabled({...main, VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED: "1"}), false);
    assert.equal(Research.isSignedEnabled(advanced), false);
    assert.equal(Research.isSignedEnabled({...advanced, VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED: "1"}), true);
});

test("signed off delta preserves positive selection and verifies exact negative readback", async () => {
    for (const key of ["SmartAutoMop", "SmartAutoWash"]) {
        for (const mode of [1, 2]) {
            const {robot, writes, settings} = fixture({settings: {[key]: mode}});
            const quirks = Research.createQuirks(robot, {advanced: true, signedProtocol: true});
            const quirk = quirks[key === "SmartAutoMop" ? 1 : 2];
            await quirk.setter("off");
            assert.deepEqual(writes, [[4, 50, JSON.stringify({k: key, v: -mode})]]);
            assert.equal(settings[key], -mode);
            const visible = await quirk.serialize();
            assert.equal(visible.readOnly, true);
            assert.equal(visible.value, "unsupported");
            assert.equal(visible.rawValue, -mode);
            await assert.rejects(() => quirk.setter("all_modes"), /Unsupported/);
            assert.equal(writes.length, 1);
        }
    }
});

test("unknown values remain visible/read-only and never become authorization to write", async () => {
    for (const value of [-2, -1, 77, null]) {
        const {robot, writes} = fixture({settings: {SmartAutoMop: value}});
        const quirk = Research.createQuirks(robot, {advanced: true, signedProtocol: true})[1];
        const visible = await quirk.serialize();
        assert.equal(visible.readOnly, true);
        assert.equal(visible.value, "unsupported");
        assert.equal(visible.rawValue, value);
        await assert.rejects(() => quirk.setter("deep_only"), /Unsupported/);
        assert.equal(writes.length, 0);
    }
});

test("advanced controls remain read-only without signed opt-in; errors disclose no secrets", async () => {
    const {robot, writes} = fixture({settings: {SmartAutoWash: 1}});
    const quirk = Research.createQuirks(robot, {advanced: true})[2];
    assert.equal((await quirk.serialize()).unavailableReason, "signed_protocol_not_opted_in");
    await assert.rejects(() => quirk.setter("off"), /not opted in/);
    robot.miotHelper.readProperty = async () => {
        throw new Error("private credential text");
    };
    const unavailable = await quirk.serialize();
    assert.equal(unavailable.readOnly, true);
    assert.equal(unavailable.rawValue, null);
    assert.equal(JSON.stringify(unavailable).includes("private credential"), false);
    assert.equal(writes.length, 0);
});

test("duplicate 4:50 keys cannot cause a write or expose an editable control", async () => {
    const {robot, writes} = fixture();
    robot.miotHelper.readProperty = async () => '[{"k":"SmartHost","v":0},{"k":"SmartHost","v":1}]';
    const quirk = Research.createQuirks(robot)[0];
    await assert.rejects(() => quirk.setter("routine"), /Duplicate/);
    assert.equal((await quirk.serialize()).readOnly, true);
    assert.equal(writes.length, 0);
});

test("observe-only preservation is explicit and does not imply writable opt-in", () => {
    const status = Status.buildStatus(null, {observeOnly: true});
    assert.equal(status.valetudoPolicy, "observe_only_preserve_smart_host");
    assert.equal(Status.buildStatus(null).valetudoPolicy, "auto_disable_smart_host_when_positive");
});
