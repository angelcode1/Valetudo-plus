"use strict";

const assert = require("node:assert/strict");
const Pet = require("../../../../lib/robots/dreame/capabilities/DreamePetObstacleAvoidanceControlCapability");
const Research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");
const test = require("node:test");

function fixture(options = {}) {
    const current = {ai: options.raw ?? 2};
    const status = {"4:1": 6, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0, ...options.status};
    const settings = {SmartHost: 0, SmartAutoMop: -1, SmartAutoWash: 0, StainIdentify: 1, HotWash: 1};
    const writes = [];
    const reads = [];
    const robot = {ephemeralState: {mode: 6, taskStatus: 0}, miotHelper: {
        readProperty: async (siid, piid) => {
            reads.push(`${siid}:${piid}`);
            assert.equal(siid, 4);
            if (piid === 22) {
                return current.ai;
            }
            assert.equal(piid, 50);
            return JSON.stringify(Object.entries(settings).map(([k, v]) => ({k: k, v: v})));
        },
        readProperties: async props => {
            reads.push("fresh_safety");
            return props.map(p => ({...p, code: 0, value: p.siid === 4 && p.piid === 22 ?
                current.ai : status[`${p.siid}:${p.piid}`]}));
        },
        writeProperty: async (siid, piid, value) => {
            writes.push([siid, piid, value]);
            if (piid === 22) {
                current.ai = value;
            } else {
                const delta = JSON.parse(value);
                settings[delta.k] = delta.v;
            }
        }
    }};
    const quirks = Research.createQuirks(robot, {fluidDetection: true,
        fluidDetectionModel: options.model === undefined ? "dreame.vacuum.r2416" : options.model,
        stainAvoidance: options.stainAvoidance === true});
    const fluid = quirks.find(quirk => quirk.title === "EXPERIMENTAL Fluid Detection");
    return {fluid: fluid, quirks: quirks, robot: robot, current: current, settings: settings, writes: writes, reads: reads};
}

test("fluid detection has its own exact opt-in and never follows another experimental flag", () => {
    const main = {VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1"};
    const fluid = {VALETUDO_X40_EXPERIMENTAL_FLUID_DETECTION: "1"};
    assert.equal(Research.isFluidDetectionEnabled({}), false);
    assert.equal(Research.isFluidDetectionEnabled(main), false);
    assert.equal(Research.isFluidDetectionEnabled(fluid), false);
    assert.equal(Research.isFluidDetectionEnabled({...main, ...fluid}), true);
    assert.equal(Research.isFluidDetectionEnabled({...main, VALETUDO_X40_EXPERIMENTAL_FLUID_DETECTION: "true"}), false);
    assert.equal(Research.isFluidDetectionEnabled({...main, VALETUDO_X40_EXPERIMENTAL_STAIN_AVOIDANCE: "1"}), false);
    assert.equal(Research.isFluidDetectionEnabled({...main, VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED: "1"}), false);
    assert.equal(Research.createQuirks({}).length, 1);
    assert.equal(Research.createQuirks({}, {advanced: true, stainAvoidance: true}).length, 4);
});

test("only the pinned R2416 model family gets an editable fluid control", async () => {
    for (const model of ["dreame.vacuum.r2416", "dreame.vacuum.r2416a", "dreame.vacuum.r2416c"]) {
        const {fluid} = fixture({model: model});
        assert(fluid);
        assert.equal((await fluid.serialize()).readOnly, false);
    }
    for (const model of [null, "", "r2416", "dreame.vacuum.r2416evil", "dreame.vacuum.r2449a"]) {
        const {fluid, reads, writes} = fixture({model: model});
        assert(fluid);
        assert.equal((await fluid.serialize()).unavailableReason, "model_capability_unverified");
        await assert.rejects(() => fluid.setter("enabled"), /model_capability_unverified/);
        assert.deepEqual(reads, []);
        assert.deepEqual(writes, []);
    }
});

test("fluid serialization is read-only and hides the full AI bitmask", async () => {
    const {fluid, reads, writes} = fixture({raw: 0x80000002});
    assert(fluid);
    const visible = await fluid.serialize();
    assert.equal(visible.value, "disabled");
    assert.equal(visible.rawValue, null);
    assert.equal(JSON.stringify(visible).includes("2147483650"), false);
    assert.deepEqual(reads, ["4:22"]);
    assert.deepEqual(writes, []);
});

test("fluid enable then disable changes only bit 8 and exactly reads back the whole target", async () => {
    const {fluid, current, settings, reads, writes} = fixture({raw: 0x800001f7});
    assert(fluid);
    const baseline = {...settings};
    await fluid.setter("enabled");
    assert.equal(current.ai, 0x800001ff);
    assert.deepEqual(reads, ["fresh_safety", "4:22"]);
    await fluid.setter("disabled");
    assert.equal(current.ai, 0x800001f7);
    assert.deepEqual(writes, [[4, 22, 0x800001ff], [4, 22, 0x800001f7]]);
    assert.deepEqual(settings, baseline);
});

test("unsupported AI values remain disabled and cannot be coerced into a writable bitmask", async () => {
    for (const raw of [null, undefined, "2", {}, -1, 0x100000000, NaN, 1.5]) {
        const {fluid, current, writes} = fixture();
        assert(fluid);
        current.ai = raw;
        const visible = await fluid.serialize();
        assert.equal(visible.readOnly, true);
        assert.equal(visible.unavailableReason, "ai_settings_format_unverified");
        await assert.rejects(() => fluid.setter("enabled"), /ai_settings_format_unverified/);
        assert.deepEqual(writes, []);
    }
});

test("both fluid directions require obstacle detection and never enable it implicitly", async () => {
    for (const raw of [0, 8]) {
        for (const value of ["enabled", "disabled"]) {
            const {fluid, writes} = fixture({raw: raw});
            assert(fluid);
            assert.equal((await fluid.serialize()).unavailableReason, "ai_obstacle_detection_disabled");
            await assert.rejects(() => fluid.setter(value), /ai_obstacle_detection_disabled/);
            assert.deepEqual(writes, []);
        }
    }
});

test("cached powersave blocks either fluid direction before any native read", async () => {
    for (const value of ["enabled", "disabled"]) {
        const {fluid, robot, reads, writes} = fixture({raw: value === "enabled" ? 2 : 10});
        assert(fluid);
        robot.ephemeralState.mode = 14;
        await assert.rejects(() => fluid.setter(value), /cached_state_not_idle/);
        assert.deepEqual(reads, []);
        assert.deepEqual(writes, []);
    }
});

test("both fluid directions repeat the full fresh safety gate", async () => {
    for (const status of [{"4:1": 14}, {"4:7": 1}, {"3:2": 0}, {"4:18": "68"}, {"4:25": 1}]) {
        for (const value of ["enabled", "disabled"]) {
            const {fluid, writes} = fixture({status: status, raw: value === "enabled" ? 2 : 10});
            assert(fluid);
            await assert.rejects(() => fluid.setter(value), /fresh_safety_not_confirmed/);
            assert.deepEqual(writes, []);
        }
    }
});

test("fluid changes do not reuse a successful UI read and catch tasks beginning during the AI read", async () => {
    const {fluid, current, robot, writes} = fixture();
    assert(fluid);
    assert.equal((await fluid.serialize()).readOnly, false);
    current.ai = 0;
    await assert.rejects(() => fluid.setter("enabled"), /ai_obstacle_detection_disabled/);
    current.ai = 2;
    const read = robot.miotHelper.readProperties;
    robot.miotHelper.readProperties = async (...args) => {
        robot.ephemeralState.taskStatus = 1;
        return read(...args);
    };
    await assert.rejects(() => fluid.setter("enabled"), /cached_state_not_idle/);
    assert.deepEqual(writes, []);
});

test("full readback mismatch catches a changed unrelated bit without retry or blind rollback", async () => {
    const {fluid, robot, writes} = fixture();
    assert(fluid);
    const read = robot.miotHelper.readProperty;
    robot.miotHelper.readProperty = async (...args) => {
        const raw = await read(...args);
        return writes.length ? raw ^ 64 : raw;
    };
    await assert.rejects(() => fluid.setter("enabled"), /ai_readback_mismatch/);
    assert.deepEqual(writes, [[4, 22, 10]]);
});

test("native read, safety and applied-write errors are fixed and never leak transport data", async () => {
    for (const phase of ["read", "safety", "write", "readback"]) {
        const {fluid, robot, writes} = fixture();
        assert(fluid);
        const read = robot.miotHelper.readProperty;
        const write = robot.miotHelper.writeProperty;
        if (phase === "safety" || phase === "read") {
            robot.miotHelper.readProperties = async () => {
                throw new Error("PRIVATE_FLUID_FIXTURE");
            };
            if (phase === "read") {
                robot.miotHelper.readProperty = async () => {
                    throw new Error("PRIVATE_FLUID_FIXTURE");
                };
            }
        } else if (phase === "write") {
            robot.miotHelper.writeProperty = async (...args) => {
                await write(...args);
                throw new Error("PRIVATE_FLUID_FIXTURE");
            };
        } else {
            robot.miotHelper.readProperty = async (...args) => {
                if (phase === "read" || writes.length) {
                    throw new Error("PRIVATE_FLUID_FIXTURE");
                }
                return read(...args);
            };
        }
        await assert.rejects(() => fluid.setter("enabled"), error => !error.message.includes("PRIVATE_FLUID"));
        assert.equal(writes.length, ["write", "readback"].includes(phase) ? 1 : 0);
        assert.equal(JSON.stringify(await fluid.serialize()).includes("PRIVATE_FLUID"), false);
    }
});

test("fluid and all other experimental selectors share one operation lock", async () => {
    const {fluid, quirks, robot, writes} = fixture({stainAvoidance: true});
    assert(fluid);
    let release;
    let entered;
    const paused = new Promise(resolve => {
        release = resolve;
    });
    const waiting = new Promise(resolve => {
        entered = resolve;
    });
    const write = robot.miotHelper.writeProperty;
    robot.miotHelper.writeProperty = async (...args) => {
        entered();
        await paused;
        return write(...args);
    };
    const pending = fluid.setter("enabled");
    await waiting;
    try {
        await assert.rejects(() => quirks[0].setter("routine"), /in progress/);
        await assert.rejects(() => quirks[1].setter("disabled"), /in progress/);
    } finally {
        release();
    }
    await pending;
    assert.deepEqual(writes, [[4, 22, 10]]);
});

test("an unchanged fluid selection still checks readiness and performs no write", async () => {
    const {fluid, reads, writes} = fixture();
    assert(fluid);
    await fluid.setter("disabled");
    assert.deepEqual(reads, ["fresh_safety"]);
    assert.deepEqual(writes, []);
    await assert.rejects(() => fluid.setter("off"), /Invalid fluid detection selection/);
});

test("incomplete, duplicated, errored or mistyped six-property replies cannot authorize fluid writes", async () => {
    for (const mutate of [
        rows => rows.slice(0, -1),
        rows => [rows[5], ...rows.slice(1)],
        rows => rows.map((row, i) => i === 5 ? {...row, code: -1} : row),
        rows => rows.map((row, i) => i === 0 ? {...row, value: "6"} : row),
        rows => [rows[1], ...rows.slice(1)],
        rows => [...rows, rows[0]]
    ]) {
        const {fluid, robot, writes} = fixture();
        assert(fluid);
        const read = robot.miotHelper.readProperties;
        robot.miotHelper.readProperties = async props => mutate(await read(props));
        await assert.rejects(() => fluid.setter("enabled"), /fresh_safety_not_confirmed/);
        assert.deepEqual(writes, []);
    }
});

test("fluid and ordinary AI controls cannot interleave their local read/modify/write operations", async () => {
    for (const owner of ["fluid", "pet"]) {
        const {fluid, robot, current, writes} = fixture();
        assert(fluid);
        const pet = Object.create(Pet.prototype);
        Object.assign(pet, {robot: robot, siid: 4, piid: 22});
        let entered;
        let release;
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
        const pending = owner === "fluid" ? fluid.setter("enabled") : pet.enable();
        await waiting;
        try {
            await assert.rejects(() => owner === "fluid" ? pet.enable() : fluid.setter("enabled"), /AI settings change is in progress/);
        } finally {
            release();
        }
        await pending;
        assert.equal(writes.length, 1);
        robot.miotHelper.writeProperty = write;
        await (owner === "fluid" ? pet.enable() : fluid.setter("enabled"));
        assert.equal(current.ai, 26);
        assert.equal(writes.length, 2);
    }
});

test("applied-write failure releases both locks for a later deliberate, freshly guarded reversal", async () => {
    const {fluid, robot, current, writes} = fixture();
    assert(fluid);
    const write = robot.miotHelper.writeProperty;
    robot.miotHelper.writeProperty = async (...args) => {
        await write(...args);
        throw new Error("PRIVATE_FLUID_FIXTURE");
    };
    await assert.rejects(() => fluid.setter("enabled"), /ai_write_unavailable_native_state_unverified/);
    assert.equal(current.ai, 10);
    assert.equal(writes.length, 1);
    robot.miotHelper.writeProperty = write;
    await fluid.setter("disabled");
    assert.deepEqual(writes, [[4, 22, 10], [4, 22, 2]]);
});

test("a task starting after an applied verified write is reported without a retry", async () => {
    const {fluid, robot, writes} = fixture();
    assert(fluid);
    const write = robot.miotHelper.writeProperty;
    robot.miotHelper.writeProperty = async (...args) => {
        await write(...args);
        robot.ephemeralState.taskStatus = 1;
    };
    await assert.rejects(() => fluid.setter("enabled"), /state_changed_after_verified_write/);
    assert.deepEqual(writes, [[4, 22, 10]]);
});
