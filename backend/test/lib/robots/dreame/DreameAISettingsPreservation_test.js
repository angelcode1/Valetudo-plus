"use strict";

const assert = require("node:assert/strict");
const Camera = require("../../../../lib/robots/dreame/capabilities/DreameAICameraObstacleAvoidanceControlCapability");
const Images = require("../../../../lib/robots/dreame/capabilities/DreameObstacleImagesCapability");
const Pet = require("../../../../lib/robots/dreame/capabilities/DreamePetObstacleAvoidanceControlCapability");
const test = require("node:test");
const Utils = require("../../../../lib/robots/dreame/DreameUtils");

function fixture(Capability, value) {
    // Exercise production capability methods without constructing a robot,
    // opening a socket or invoking unrelated capability setup.
    const capability = Object.create(Capability.prototype);
    const reads = [];
    const writes = [];
    capability.siid = 4;
    capability.piid = 22;
    capability.robot = {miotHelper: {
        readProperty: async (...args) => {
            reads.push(args);
            return value;
        },
        writeProperty: async (...args) => {
            writes.push(args);
        }
    }};
    return {capability: capability, reads: reads, writes: writes};
}

test("AI settings round-trip preserves every bit, including fluid and high unsigned bits", () => {
    for (const value of [0, 1, 8, 31, 255, 0x80000000, 0xffffffff]) {
        assert.equal(Utils.SERIALIZE_AI_SETTINGS(Utils.DESERIALIZE_AI_SETTINGS(value), value), value);
    }
});

for (const [name, Capability, bit] of [["camera", Camera, 2], ["images", Images, 4], ["pet", Pet, 16]]) {
    for (const method of ["enable", "disable"]) {
        test(`${name} ${method} changes only its requested bit and keeps unrelated AI settings`, async () => {
            // Bits outside the requested field include the reference fluid bit,
            // other supported fields and deliberately uninterpreted high bits.
            const original = method === "enable" ? (0x800001ff & ~bit) >>> 0 : 0x800001ff;
            const expected = method === "enable" ? (original | bit) >>> 0 : (original & ~bit) >>> 0;
            const {capability, reads, writes} = fixture(Capability, original);
            await capability[method]();
            assert.deepEqual(reads, [[4, 22]]);
            assert.deepEqual(writes, [[4, 22, expected]]);
            assert.equal((writes[0][2] & ~bit) >>> 0, (original & ~bit) >>> 0);
            assert.equal(writes[0][2] & 8, 8);
        });
    }
}

test("unsupported AI settings formats cannot cause any capability write", async () => {
    for (const Capability of [Camera, Images, Pet]) {
        for (const method of ["enable", "disable"]) {
            for (const raw of [undefined, null, "31", -1, 0x100000000, 1.5, NaN, Infinity, {}, true]) {
                const {capability, writes} = fixture(Capability, raw);
                await assert.rejects(() => capability[method](), /Unsupported AI settings bitmask/);
                assert.equal(writes.length, 0);
            }
        }
    }
});

test("fresh AI reads or writes failing never cause automatic retries", async () => {
    for (const Capability of [Camera, Images, Pet]) {
        const {capability, writes} = fixture(Capability, 255);
        capability.robot.miotHelper.readProperty = async () => {
            throw new Error("synthetic read failure");
        };
        await assert.rejects(() => capability.enable(), /synthetic read failure/);
        assert.equal(writes.length, 0);
        let calls = 0;
        capability.robot.miotHelper.readProperty = async () => 255;
        capability.robot.miotHelper.writeProperty = async () => {
            calls++;
            throw new Error("synthetic write failure");
        };
        await assert.rejects(() => capability.disable(), /synthetic write failure/);
        assert.equal(calls, 1);
    }
});
