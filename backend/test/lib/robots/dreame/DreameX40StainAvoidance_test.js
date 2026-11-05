"use strict";

const assert = require("node:assert/strict");
const Preflight = require("../../../../lib/robots/dreame/DreameX40CleanGeniusPreflight");
const Research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");
const Status = require("../../../../lib/robots/dreame/DreameX40CleanGeniusReadOnlyStatus");
const test = require("node:test");

function fixture(options = {}) {
    const settings = {SmartHost: 0, SmartAutoMop: -1, SmartAutoWash: 0, StainIdentify: 1, HotWash: 1,
        ...options.settings};
    const state = {"4:1": 6, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0, ...options.state};
    const writes = [];
    const reads = [];
    const ai = {value: 10};
    const robot = {
        ephemeralState: {mode: 6, taskStatus: 0},
        miotHelper: {
            readProperties: async props => {
                reads.push("fresh_safety");
                return props.map(p => ({...p, code: 0, value: state[`${p.siid}:${p.piid}`]}));
            },
            readProperty: async (siid, piid) => {
                reads.push(`${siid}:${piid}`);
                if (siid === 4 && piid === 22) {
                    return ai.value;
                }
                assert.deepEqual([siid, piid], [4, 50]);
                return JSON.stringify(Object.entries(settings).map(([k, v]) => ({k: k, v: v})));
            },
            writeProperty: async (siid, piid, value) => {
                writes.push([siid, piid, value]);
                const delta = JSON.parse(value);
                settings[delta.k] = delta.v;
            }
        }
    };
    const quirks = Research.createQuirks(robot, {stainAvoidance: true});
    return {robot: robot, quirks: quirks, stain: quirks[1], settings: settings, writes: writes, reads: reads, ai: ai};
}

test("stain avoidance requires main and separate exact opt-ins, never advanced alone", () => {
    const main = {VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1"};
    const stain = {VALETUDO_X40_EXPERIMENTAL_STAIN_AVOIDANCE: "1"};
    assert.equal(Research.isStainAvoidanceEnabled({}), false);
    assert.equal(Research.isStainAvoidanceEnabled(main), false);
    assert.equal(Research.isStainAvoidanceEnabled(stain), false);
    assert.equal(Research.isStainAvoidanceEnabled({...main, ...stain}), true);
    assert.equal(Research.isStainAvoidanceEnabled({...main, VALETUDO_X40_EXPERIMENTAL_STAIN_AVOIDANCE: "true"}), false);
    assert.equal(Research.isStainAvoidanceEnabled({...main, VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED: "1"}), false);
    assert.equal(Research.createQuirks({}).length, 1);
    assert.equal(Research.createQuirks({}, {advanced: true}).length, 3);
    assert.equal(Research.createQuirks({}, {advanced: true, stainAvoidance: true}).length, 4);
});

test("stain observations do not invent a boolean identification setting", () => {
    for (const [raw, expected] of [[0, "unknown"], [1, "mode_1_unverified"], [2, "mode_2_unverified"], [-1, "unknown"]]) {
        const parsed = Status.parseSettings(JSON.stringify([{k: "StainIdentify", v: raw}]));
        assert.deepEqual(parsed.stainIdentification, {value: raw, state: expected});
    }
});

test("stain selector registration and serialization perform no writes", async () => {
    const {stain, writes} = fixture();
    assert(stain, "separately opted-in stain selector must exist");
    const visible = await stain.serialize();
    assert.deepEqual(visible.options, ["disabled", "enabled"]);
    assert.equal(visible.value, "disabled");
    assert.equal(visible.rawValue, 1);
    assert.equal(visible.readOnly, false);
    assert.equal(writes.length, 0);
});

test("stain enable and disable use reference 2/1 deltas with exact readback and preserve other settings", async () => {
    const {stain, settings, writes} = fixture();
    assert(stain);
    const original = {...settings};
    await stain.setter("enabled");
    assert.equal((await stain.serialize()).value, "enabled");
    await stain.setter("disabled");
    assert.deepEqual(writes, [[4, 50, '{"k":"StainIdentify","v":2}'], [4, 50, '{"k":"StainIdentify","v":1}']]);
    assert.deepEqual(settings, original);
});

test("stain does not accept zero, missing, negative or mistyped current values", async () => {
    for (const raw of [0, -1, 3, "1", null, undefined]) {
        const {stain, writes} = fixture({settings: {StainIdentify: raw}});
        assert(stain);
        assert.equal((await stain.serialize()).readOnly, true);
        await assert.rejects(() => stain.setter("enabled"), /Unsupported StainIdentify/);
        assert.equal(writes.length, 0);
    }
});

test("both stain directions require cached and full fresh idle state; disabling is not recovery", async () => {
    for (const value of ["disabled", "enabled"]) {
        for (const state of [{"4:1": 14}, {"4:7": 1}, {"3:2": 0}, {"4:18": "68"}, {"4:25": 1}]) {
            const {stain, writes} = fixture({settings: {StainIdentify: value === "enabled" ? 1 : 2}, state: state});
            assert(stain);
            await assert.rejects(() => stain.setter(value), /fresh MIOT read/);
            assert.equal(writes.length, 0);
        }
        const {stain, robot, writes} = fixture();
        robot.ephemeralState.mode = 14;
        await assert.rejects(() => stain.setter(value), /cached mode=14/);
        assert.equal(writes.length, 0);
    }
});

test("stain invalid UI values and duplicate native keys cannot write", async () => {
    const {stain, robot, writes} = fixture();
    assert(stain);
    await assert.rejects(() => stain.setter("off"), /Invalid StainIdentify selection/);
    robot.miotHelper.readProperty = async () => '[{"k":"StainIdentify","v":1},{"k":"StainIdentify","v":2}]';
    await assert.rejects(() => stain.setter("enabled"), /Duplicate/);
    assert.equal((await stain.serialize()).readOnly, true);
    assert.equal(writes.length, 0);
});

test("stain mismatch and failed readback do not retry or issue rollback writes", async () => {
    for (const failure of ["mismatch", "unavailable"]) {
        const {stain, robot, writes} = fixture();
        assert(stain);
        const read = robot.miotHelper.readProperty;
        robot.miotHelper.readProperty = async (...args) => {
            if (writes.length) {
                if (failure === "unavailable") {
                    throw new Error("synthetic unavailable readback");
                }
                return '[{"k":"StainIdentify","v":1}]';
            }
            return read(...args);
        };
        await assert.rejects(() => stain.setter("enabled"), failure === "mismatch" ? /readback mismatch/ : /unavailable/);
        assert.deepEqual(writes, [[4, 50, '{"k":"StainIdentify","v":2}']]);
    }
});

test("stain and CleanGenius share the same in-flight write lock", async () => {
    const {stain, robot, quirks, writes} = fixture();
    assert(stain);
    let release;
    let entered;
    const waiting = new Promise(resolve => {
        entered = resolve;
    });
    const paused = new Promise(resolve => {
        release = resolve;
    });
    const write = robot.miotHelper.writeProperty;
    robot.miotHelper.writeProperty = async (...args) => {
        entered();
        await paused;
        return write(...args);
    };
    const pending = stain.setter("enabled");
    await waiting;
    try {
        await assert.rejects(() => quirks[0].setter("routine"), /in progress/);
    } finally {
        release();
    }
    await pending;
    assert.deepEqual(writes, [[4, 50, '{"k":"StainIdentify","v":2}']]);
});

test("fresh stain prerequisites expose only the reference obstacle/fluid flags, never the full AI bitmask", async () => {
    for (const raw of [10, 0x800001ff]) {
        const {robot, ai, reads, writes} = fixture();
        ai.value = raw;
        const result = await Preflight.readStainAvoidancePrerequisites(robot);
        assert.equal(result.readOnly, true);
        assert.equal(result.obstacleDetection, true);
        assert.equal(result.fluidDetection, true);
        assert.equal(result.prerequisitesMatch, true);
        assert.equal(result.blockedReason, null);
        assert.equal(Object.hasOwn(result, "rawValue"), false);
        assert.deepEqual(reads, ["4:22"]);
        assert.equal(writes.length, 0);
    }
});

test("both stain directions fail closed when reference AI prerequisites are absent or unsupported", async () => {
    for (const [raw, reason] of [
        [0, "ai_obstacle_detection_disabled"], [8, "ai_obstacle_detection_disabled"],
        [2, "ai_fluid_detection_disabled"], [null, "ai_settings_format_unverified"],
        ["10", "ai_settings_format_unverified"], [-1, "ai_settings_format_unverified"],
        [0x100000000, "ai_settings_format_unverified"], [undefined, "ai_settings_format_unverified"]
    ]) {
        for (const value of ["enabled", "disabled"]) {
            const {stain, ai, writes} = fixture({settings: {StainIdentify: value === "enabled" ? 1 : 2}});
            ai.value = raw;
            const visible = await stain.serialize();
            assert.equal(visible.readOnly, true);
            assert.equal(visible.unavailableReason, reason);
            assert.equal(visible.value, value === "enabled" ? "disabled" : "enabled");
            await assert.rejects(() => stain.setter(value), error => error.message.includes(reason));
            assert.equal(writes.length, 0);
        }
    }
});

test("unavailable AI reads use a fixed blocked reason without private errors or retries", async () => {
    const {stain, robot, writes} = fixture();
    const read = robot.miotHelper.readProperty;
    let attempts = 0;
    robot.miotHelper.readProperty = async (siid, piid) => {
        if (piid === 22) {
            attempts++;
            throw new Error("PRIVATE_AI_TRANSPORT_FIXTURE");
        }
        return read(siid, piid);
    };
    const visible = await stain.serialize();
    assert.equal(visible.readOnly, true);
    assert.equal(visible.unavailableReason, "ai_settings_unavailable");
    assert.equal(JSON.stringify(visible).includes("PRIVATE_AI"), false);
    await assert.rejects(() => stain.setter("enabled"), error => {
        assert.equal(error.message.includes("PRIVATE_AI"), false);
        return error.message.includes("ai_settings_unavailable");
    });
    assert.equal(attempts, 2); // One explicit serialize and one explicit setter.
    assert.equal(writes.length, 0);
});

test("a successful UI prerequisite read never authorizes the subsequent setter", async () => {
    const {stain, ai, writes} = fixture();
    assert.equal((await stain.serialize()).readOnly, false);
    ai.value = 2;
    await assert.rejects(() => stain.setter("enabled"), /ai_fluid_detection_disabled/);
    assert.equal(writes.length, 0);
    ai.value = 10;
    assert.equal((await stain.serialize()).readOnly, false);
});

test("stain obtains fresh AI prerequisites before its final fresh safety gate and one-key write", async () => {
    const {stain, reads, writes} = fixture();
    await stain.setter("enabled");
    assert.deepEqual(reads, ["4:50", "4:22", "fresh_safety", "4:50"]);
    assert.deepEqual(writes, [[4, 50, '{"k":"StainIdentify","v":2}']]);
});

test("a task starting while AI prerequisites are read still prevents a stain write", async () => {
    const {stain, robot, writes} = fixture();
    const read = robot.miotHelper.readProperty;
    robot.miotHelper.readProperty = async (siid, piid) => {
        if (piid === 22) {
            robot.ephemeralState.taskStatus = 1;
        }
        return read(siid, piid);
    };
    await assert.rejects(() => stain.setter("enabled"), /no longer idle/);
    assert.equal(writes.length, 0);
});

test("ordinary CleanGenius controls do not acquire AI-setting reads", async () => {
    const {robot, reads} = fixture();
    const main = Research.createQuirks(robot)[0];
    await main.serialize();
    await main.setter("routine");
    assert.equal(reads.includes("4:22"), false);
});
