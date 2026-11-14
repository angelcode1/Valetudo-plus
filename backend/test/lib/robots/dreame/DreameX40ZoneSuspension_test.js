"use strict";

const assert = require("node:assert/strict");
const Research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");
const test = require("node:test");

function fixture(smartHost = 1, startFails = false) {
    const settings = {SmartHost: smartHost, SmartAutoMop: -1, SmartAutoWash: 0};
    const status = {"4:1": 6, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0};
    const events = [];
    const robot = {
        ephemeralState: {mode: 6, taskStatus: 0},
        x40DockWashObservation: {value: {raw: 0}},
        miotHelper: {
            readProperties: async props => props.map(p => ({...p, code: 0, value: status[`${p.siid}:${p.piid}`]})),
            readProperty: async () => JSON.stringify(Object.entries(settings).map(([k, v]) => ({k: k, v: v}))),
            writeProperty: async (siid, piid, value) => {
                events.push(value);
                const delta = JSON.parse(value);
                settings[delta.k] = delta.v;
            }
        }
    };
    const zone = {
        start: async options => {
            if (startFails) {
                throw new Error("action refused");
            }
            events.push("zone:" + options.id);
        }
    };
    const [quirk] = Research.createQuirks(robot);
    const afterUpdate = Research.suspendDuringZoneCleaning(robot, quirk, zone);
    const state = (mode, task, dock = 0) => {
        robot.ephemeralState = {mode: mode, taskStatus: task};
        status["4:1"] = mode;
        status["4:7"] = task;
        status["4:25"] = dock;
        robot.x40DockWashObservation = {value: {raw: dock}};
        afterUpdate();
    };
    const settle = () => new Promise(resolve => setImmediate(resolve));
    return {robot: robot, settings: settings, events: events, zone: zone, quirk: quirk, state: state, settle: settle};
}

test("zone cleanup with CleanGenius off starts unchanged, without any write", async () => {
    const f = fixture(0);
    await f.zone.start({id: 1});
    f.state(19, 1);
    f.state(6, 0);
    await f.settle();
    assert.deepEqual(f.events, ["zone:1"]);
});

test("zone cleanup turns a positive mode off first and restores it once when docked idle", async () => {
    for (const mode of [1, 2]) {
        const f = fixture(mode);
        await f.zone.start({id: 1});
        assert.deepEqual(f.events, ['{"k":"SmartHost","v":0}', "zone:1"]);

        f.state(6, 0); // The cleanup has not been observed yet.
        f.state(19, 1);
        f.state(3, 1);
        f.state(6, 0, 2); // Docked while the dock is still drying.
        await f.settle();
        assert.equal(f.events.length, 2);

        f.state(6, 0);
        await f.settle();
        assert.deepEqual(f.events.slice(2), [`{"k":"SmartHost","v":${mode}}`]);
        f.state(6, 0);
        await f.settle();
        assert.equal(f.events.length, 3);
    }
});

test("an unverified suspension leaves the zone cleanup unstarted", async () => {
    const f = fixture(1);
    f.robot.miotHelper.writeProperty = async (siid, piid, value) => {
        f.events.push(value);
    };
    await assert.rejects(() => f.zone.start({id: 1}), /readback/);
    assert.deepEqual(f.events, ['{"k":"SmartHost","v":0}']);
});

test("unreadable or unrecognized settings start the zone cleanup as before", async () => {
    const unreadable = fixture(1);
    unreadable.robot.miotHelper.readProperty = async () => {
        throw new Error("timeout");
    };
    await unreadable.zone.start({id: 1});
    assert.deepEqual(unreadable.events, ["zone:1"]);

    const unknown = fixture(7);
    await unknown.zone.start({id: 1});
    assert.deepEqual(unknown.events, ["zone:1"]);
});

test("a refused restore is attempted once and a failed start still restores", async () => {
    const refused = fixture(1);
    await refused.zone.start({id: 1});
    refused.state(19, 1);
    refused.robot.miotHelper.readProperties = async () => {
        throw new Error("timeout");
    };
    refused.state(6, 0);
    await refused.settle();
    refused.state(6, 0);
    await refused.settle();
    assert.deepEqual(refused.events, ['{"k":"SmartHost","v":0}', "zone:1"]);
    assert.equal(refused.settings.SmartHost, 0);

    const failed = fixture(2, true);
    await assert.rejects(() => failed.zone.start({id: 1}), /action refused/);
    failed.state(6, 0);
    await failed.settle();
    assert.deepEqual(failed.events, ['{"k":"SmartHost","v":0}', '{"k":"SmartHost","v":2}']);
});

test("a manual selection replaces the remembered restore", async () => {
    const f = fixture(2);
    await f.zone.start({id: 1});
    f.state(19, 1);
    f.state(6, 0, 2);
    await f.quirk.setter("off");
    f.state(6, 0);
    await f.settle();
    assert.deepEqual(f.events, ['{"k":"SmartHost","v":0}', "zone:1"]);
});
