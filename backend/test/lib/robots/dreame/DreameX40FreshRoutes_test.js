"use strict";

const assert = require("node:assert/strict");
const express = require("express");
const RobotRouter = require("../../../../lib/webserver/RobotRouter");
const test = require("node:test");
const X40 = require("../../../../lib/robots/dreame/DreameX40UltraValetudoRobot");
const {once} = require("node:events");

test("fresh X40 HTTP routes are GET-only, no-store, optional and redact errors", async () => {
    let reads = 0;
    const robot = {
        onStateUpdated: () => {},
        onStateAttributesUpdated: () => {},
        onMapUpdated: () => {},
        capabilities: {},
        getCleanGeniusPreflightReadOnly: async () => {
            reads++;
            return {readOnly: true, mode: 14, activationAllowed: false};
        },
        getCleanGeniusNativeSettingsFreshReadOnly: async () => {
            reads++;
            throw new Error("private credentials must never leave this process");
        }
    };
    const router = new RobotRouter({robot: robot});
    const app = express();
    app.use(router.getRouter());
    const server = app.listen(0, "127.0.0.1");
    await once(server, "listening");
    const base = `http://127.0.0.1:${server.address().port}`;
    try {
        for (const path of ["preflight", "smart-host-test/preflight"]) {
            const res = await fetch(`${base}/clean-genius/${path}`);
            assert.equal(res.status, 200);
            assert.equal(res.headers.get("cache-control"), "no-store");
            assert.equal((await res.json()).mode, 14);
        }
        const error = await fetch(`${base}/clean-genius/native-settings`);
        assert.equal(error.status, 502);
        assert.deepEqual(await error.json(), {error: "Fresh X40 observation unavailable"});
        const before = reads;
        const post = await fetch(`${base}/clean-genius/preflight`, {method: "POST"});
        assert.equal(post.status, 404);
        assert.equal(reads, before);
        delete robot.getCleanGeniusPreflightReadOnly;
        assert.equal((await fetch(`${base}/clean-genius/preflight`)).status, 404);
        assert.equal(reads, before);
    } finally {
        server.closeAllConnections();
        await new Promise(resolve => server.close(resolve));
        router.shutdown();
    }
});

test("actual X40 fresh reader methods do not invoke normal parsing or change caches", async () => {
    const robot = Object.create(X40.prototype);
    robot.x40CleanGeniusObservation = {observedAtMs: 1, fields: {}};
    const before = robot.x40CleanGeniusObservation;
    robot.pollState = () => {
        throw new Error("must not poll");
    };
    robot.parseAndUpdateState = () => {
        throw new Error("must not parse");
    };
    robot.miotHelper = {
        readProperties: async props => props.map(p => ({...p, code: 0,
            value: p.siid === 3 ? 1 : (p.piid === 1 ? 14 : 0)})),
        readProperty: async () => '[{"k":"SmartAutoMop","v":-1}]',
        writeProperty: async () => {
            throw new Error("must not write");
        }
    };
    assert.equal((await robot.getCleanGeniusPreflightReadOnly()).blockedReason, "powersave_requires_awake_idle_observation");
    assert.equal((await robot.getCleanGeniusNativeSettingsFreshReadOnly()).settings.autoReclean.value, -1);
    assert.equal(robot.x40CleanGeniusObservation, before);
});

test("actual Gen2 parser preserves SmartHost only under explicit X40 policies", async () => {
    for (const [observe, experimental, expected] of [[false, false, 1], [true, false, 0], [false, true, 0]]) {
        const robot = Object.create(X40.prototype);
        robot.allowCleanGeniusObserveOnly = observe;
        robot.allowExperimentalCleanGenius = experimental;
        robot.emitStateAttributesUpdated = () => {};
        const writes = [];
        robot.miotHelper = {writeProperty: async (...args) => {
            writes.push(args);
        }};
        robot.parseAndUpdateState([{siid: 4, piid: 50, code: 0, value: '[{"k":"SmartHost","v":1}]'}]);
        assert.equal(writes.length, expected);
        if (expected) {
            assert.deepEqual(writes, [[4, 50, '{"k":"SmartHost","v":0}']]);
        }
    }
});
