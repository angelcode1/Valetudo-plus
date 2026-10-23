"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const SmartHostTest = require("../../lib/robots/dreame/DreameX40NativeSmartHostTest");

function makeFakeRobot(options = {}) {
    const writes = [];
    let current = options.smartHost ?? 0;
    const mode = options.mode ?? 0;
    const task = options.task ?? 0;
    const charge = options.charge ?? 1;
    const error = options.error ?? 0;
    const dockWash = options.dockWash ?? 0;
    const reclean = options.reclean ?? -1;
    const rewash = options.rewash ?? 0;
    const stateString = () => JSON.stringify([
        {k: "SmartHost", v: current},
        {k: "SmartAutoMop", v: reclean},
        {k: "SmartAutoWash", v: rewash},
        {k: "StainIdentify", v: 1},
        {k: "HotWash", v: 1},
        {k: "privateIdentifier", v: "NEVER_EXPOSE"}
    ]);
    return {
        writes: writes,
        allowCleanGeniusObserveOnly: true,
        allowExperimentalCleanGenius: false,
        miotHelper: {
            readProperties: async function readProperties() {
                return [
                    {siid: 4, piid: 1, code: 0, value: mode},
                    {siid: 4, piid: 7, code: 0, value: task},
                    {siid: 3, piid: 2, code: 0, value: charge},
                    {siid: 4, piid: 18, code: 0, value: error},
                    {siid: 4, piid: 25, code: 0, value: dockWash},
                    {siid: 4, piid: 50, code: 0, value: stateString()}
                ];
            },
            readProperty: async function readProperty(siid, piid) {
                assert.deepEqual([siid, piid], [4, 50]);
                return stateString();
            },
            writeProperty: async function writeProperty(siid, piid, value) {
                assert.deepEqual([siid, piid], [4, 50]);
                const decoded = JSON.parse(value);
                assert.deepEqual(Object.keys(decoded).sort(), ["k", "v"]);
                assert.equal(decoded.k, "SmartHost");
                writes.push(decoded);
                current = decoded.v;
            }
        }
    };
}

async function withGate(testBody) {
    const old = process.env[SmartHostTest.TEST_ENV];
    process.env[SmartHostTest.TEST_ENV] = "1";
    try {
        await testBody();
    } finally {
        if (old === undefined) {
            delete process.env[SmartHostTest.TEST_ENV];
        } else {
            process.env[SmartHostTest.TEST_ENV] = old;
        }
    }
}

test("preflight is read-only and keeps private data out of response", async () => {
    const robot = makeFakeRobot();
    const status = await SmartHostTest.getFreshPreflight(robot);
    assert.equal(status.idleAndDocked, true);
    assert.equal(status.baselineMatch, true);
    assert.equal(status.settings.autoReclean.value, -1);
    assert.equal(status.errorCode, "0");
    assert.equal(status.errorCodeFormatRecognized, true);
    assert.equal(JSON.stringify(status).includes("NEVER_EXPOSE"), false);
    assert.equal(robot.writes.length, 0);
});

test("mode six is docked, and empty error text is a clear status", async () => {
    const robot = makeFakeRobot({mode: 6, charge: 1, task: 0, error: "", dockWash: 0});
    const status = await SmartHostTest.getFreshPreflight(robot);
    assert.equal(status.idleAndDocked, true);
    assert.equal(status.errorClear, true);
    assert.equal(status.errorCode, "");
    assert.equal(status.writeGateOpen, false);
    assert.equal(robot.writes.length, 0);
});

test("mode six while drying is not eligible even when physically charging", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot({mode: 6, charge: 1, task: 0, error: "", dockWash: 2});
        const status = await SmartHostTest.getFreshPreflight(robot);
        assert.equal(status.errorClear, true);
        assert.equal(status.idleAndDocked, false);
        assert.equal(status.canTestMode1, false);
        await assert.rejects(() => SmartHostTest.writeSmartHostOneKey(robot, 1), /Mode 1 refused/);
        assert.equal(robot.writes.length, 0);
    });
});

test("docked mode six and clear empty error are eligible only with explicit gate", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot({mode: 6, task: 0, charge: 1, error: "", dockWash: 0});
        const status = await SmartHostTest.getFreshPreflight(robot);
        assert.equal(status.canTestMode1, true);
        assert.equal(robot.writes.length, 0);
        const result = await SmartHostTest.writeSmartHostOneKey(robot, 1);
        assert.equal(result.readbackVerified, true);
        assert.deepEqual(robot.writes, [{k: "SmartHost", v: 1}]);
    });
});

test("non-clear error code is sanitized and blocks activation", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot({mode: 6, error: "68,114"});
        const status = await SmartHostTest.getFreshPreflight(robot);
        assert.equal(status.errorCode, "68,114");
        assert.equal(status.errorClear, false);
        assert.equal(status.canTestMode1, false);
        assert.equal(robot.writes.length, 0);
    });
});

test("unsafe error strings are not exposed or treated as clear", async () => {
    const robot = makeFakeRobot({error: "secret-token\n432"});
    const status = await SmartHostTest.getFreshPreflight(robot);
    assert.equal(status.errorCode, null);
    assert.equal(status.errorCodeFormatRecognized, false);
    assert.equal(status.errorClear, false);
    assert.equal(JSON.stringify(status).includes("secret-token"), false);
});

test("write gate defaults closed and respects both existing safety policies", () => {
    const robot = makeFakeRobot();
    assert.equal(SmartHostTest.isWriteGateOpen(robot, {}), false);
    assert.equal(SmartHostTest.isWriteGateOpen(robot, {[SmartHostTest.TEST_ENV]: "1"}), true);
    robot.allowCleanGeniusObserveOnly = false;
    assert.equal(SmartHostTest.isWriteGateOpen(robot, {[SmartHostTest.TEST_ENV]: "1"}), false);
    robot.allowCleanGeniusObserveOnly = true;
    robot.allowExperimentalCleanGenius = true;
    assert.equal(SmartHostTest.isWriteGateOpen(robot, {[SmartHostTest.TEST_ENV]: "1"}), false);
});

test("explicit mode 1 writes only one SmartHost key and verifies readback", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot();
        const result = await SmartHostTest.writeSmartHostOneKey(robot, 1);
        assert.equal(result.changed, true);
        assert.equal(result.readbackVerified, true);
        assert.deepEqual(robot.writes, [{k: "SmartHost", v: 1}]);
        assert.equal(result.settings.autoReclean.value, -1);
        assert.equal(result.settings.autoRewash.value, 0);
    });
});

test("mode 1 refuses movement, task, not charging and changed native baseline", async () => {
    await withGate(async () => {
        for (const options of [
            {mode: 2},
            {task: 1},
            {charge: 2},
            {error: 2},
            {dockWash: 1},
            {mode: 6, dockWash: 2},
            {reclean: 0},
            {rewash: 1},
            {smartHost: 2}
        ]) {
            const robot = makeFakeRobot(options);
            await assert.rejects(
                () => SmartHostTest.writeSmartHostOneKey(robot, 1),
                /Mode 1 refused/
            );
            assert.equal(robot.writes.length, 0);
        }
    });
});

test("rollback only needs fresh 4:50, not other failing MIOT sensors", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot({smartHost: 1, mode: 2, charge: 2});
        robot.miotHelper.readProperties = async function readProperties() {
            throw new Error("unrelated native state sensor failed");
        };
        const result = await SmartHostTest.writeSmartHostOneKey(robot, 0);
        assert.equal(result.observed, 0);
        assert.deepEqual(robot.writes, [{k: "SmartHost", v: 0}]);
    });
});

test("restore refuses unknown SmartHost without writing", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot({smartHost: -1});
        await assert.rejects(() => SmartHostTest.writeSmartHostOneKey(robot, 0),
            /unrecognised current SmartHost value/);
        assert.equal(robot.writes.length, 0);
    });
});

test("restore already at SmartHost zero is a no-op", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot();
        const result = await SmartHostTest.writeSmartHostOneKey(robot, 0);
        assert.equal(result.changed, false);
        assert.equal(result.observed, 0);
        assert.equal(robot.writes.length, 0);
    });
});

test("invalid target, closed gate, and concurrent write refuse without changes", async () => {
    const robot = makeFakeRobot();
    await assert.rejects(() => SmartHostTest.writeSmartHostOneKey(robot, 1), /not opted in/);
    await withGate(async () => {
        await assert.rejects(() => SmartHostTest.writeSmartHostOneKey(robot, 2), /Only native/);
        robot.x40NativeSmartHostTestBusy = true;
        await assert.rejects(() => SmartHostTest.writeSmartHostOneKey(robot, 1), /already in progress/);
        robot.x40NativeSmartHostTestBusy = false;
    });
    assert.equal(robot.writes.length, 0);
});

test("invalid property response refuses before firmware write", async () => {
    await withGate(async () => {
        const robot = makeFakeRobot();
        robot.miotHelper.readProperties = async function readProperties() {
            return [{code: -1, siid: 4, piid: 1}];
        };
        await assert.rejects(() => SmartHostTest.writeSmartHostOneKey(robot, 1), /property read failed/);
        assert.equal(robot.writes.length, 0);
    });
});
