"use strict";

const assert = require("node:assert/strict");
const Codec = require("../../../../lib/miio/Codec");
const dgram = require("node:dgram");
const DreameMiotHelper = require("../../../../lib/robots/dreame/DreameMiotHelper");
const Logger = require("../../../../lib/Logger");
const MiioSocket = require("../../../../lib/miio/MiioSocket");
const MiioTimeoutError = require("../../../../lib/miio/MiioTimeoutError");
const MiioValetudoRobot = require("../../../../lib/robots/MiioValetudoRobot");
const Research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");
const RetryWrapper = require("../../../../lib/miio/RetryWrapper");
const Semaphore = require("semaphore");
const test = require("node:test");
const {once} = require("node:events");

Logger.log = () => {};

function wrapper(socket) {
    // Avoid constructor handshake timers. Tests provide an explicitly known
    // synthetic stamp, then run the real queue/retry implementation.
    const result = Object.create(RetryWrapper.prototype);
    Object.assign(result, {miioSocket: socket, mutex: Semaphore(1), tokenProvider: () => Buffer.alloc(16, 0x42)});
    return result;
}

test("explicit no-retry stops after one transport timeout while default retry behavior remains", async () => {
    for (const noRetry of [false, true]) {
        let calls = 0;
        const transport = wrapper({codec: {stamp: {isValid: () => true}}, sendMessage: async msg => {
            calls++;
            if (calls === 1) {
                throw new MiioTimeoutError(msg);
            }
            return {ok: true};
        }});
        if (noRetry) {
            await assert.rejects(() => transport.sendMessage({method: "set_properties"}, {retry: false}), MiioTimeoutError);
        } else {
            assert.deepEqual(await transport.sendMessage({method: "get_properties"}), {ok: true});
        }
        assert.equal(calls, noRetry ? 1 : 2);
    }
});

test("an invalid stamp refuses a no-retry request before transmission or handshake recovery", async () => {
    const transport = wrapper({codec: {stamp: {isValid: () => false}}, sendMessage: async () => {
        assert.fail("No packet may be sent");
    }});
    transport.retryHandshakeHelper = async () => assert.fail("No handshake recovery may run");
    await assert.rejects(() => transport.sendMessage({method: "set_properties"}, {retry: false}), MiioTimeoutError);
});

test("MIOT helper forwards explicit local no-retry options and strictly validates property identities", async () => {
    const seen = [];
    const robot = {deviceId: 123, sendCommand: async (method, params, options) => {
        seen.push([method, options]);
        return [{siid: 4, piid: 999, code: 0, value: 10}];
    }};
    const helper = new DreameMiotHelper({robot: robot});
    const options = {retry: false, interface: "local", strict: true, timeout: 20};
    await assert.rejects(() => helper.readProperty(4, 22, options), /invalid property response/);
    await assert.rejects(() => helper.writeProperty(4, 22, 10, options), /invalid property response/);
    assert.deepEqual(seen, [["get_properties", {retry: false, timeout: 20, interface: "local"}],
        ["set_properties", {retry: false, timeout: 20, interface: "local"}]]);
    // The strict identity policy is opted in, preserving legacy helper behavior.
    assert.equal(await helper.readProperty(4, 22), 10);
});

for (const kind of ["mode", "fluid"]) {
    test(`real ${kind} controller/helper/transport sends one encrypted write when its acknowledgement is lost`, {timeout: 10000}, async () => {
        const token = Buffer.alloc(16, 0x42);
        const codec = new Codec({token: token});
        codec.updateStamp(100);
        const server = dgram.createSocket("udp4");
        const client = dgram.createSocket("udp4");
        const settings = {SmartHost: 0, SmartAutoMop: -1, SmartAutoWash: 0, StainIdentify: 1, HotWash: 1};
        let ai = 2;
        let writes = 0;
        let cloudCalls = 0;
        server.on("message", (packet, peer) => {
            const msg = codec.decodeIncomingMiioPacket(packet).msg;
            let result;
            if (msg.method === "get_properties") {
                const values = {"4:1": 6, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0,
                    "4:22": ai, "4:50": JSON.stringify(Object.entries(settings).map(([k, v]) => ({k: k, v: v})))};
                result = msg.params.map(p => ({...p, code: 0, value: values[`${p.siid}:${p.piid}`]}));
            } else {
                assert.equal(msg.method, "set_properties");
                assert.equal(msg.params.length, 1);
                writes++;
                const delta = msg.params[0];
                assert.equal(delta.siid, 4);
                if (kind === "fluid") {
                    assert.equal(delta.piid, 22);
                    ai = delta.value;
                } else {
                    assert.equal(delta.piid, 50);
                    const setting = JSON.parse(delta.value);
                    settings[setting.k] = setting.v;
                }
                // Apply the first write, then deliberately lose its ACK. An
                // erroneous replay would receive a reply and fail the test.
                if (writes === 1) {
                    return;
                }
                result = msg.params.map(p => ({did: p.did, siid: p.siid, piid: p.piid, code: 0}));
            }
            server.send(codec.encodeOutgoingMiioPacket({id: msg.id, result: result}, 123), peer.port, peer.address);
        });
        try {
            server.bind(0, "127.0.0.1");
            client.bind(0, "127.0.0.1");
            await Promise.all([once(server, "listening"), once(client, "listening")]);
            const socket = new MiioSocket({socket: client, token: token, deviceId: 123,
                rinfo: {address: "127.0.0.1", port: server.address().port}, name: "fixture", isCloudSocket: false});
            socket.codec.updateStamp(100);
            const robot = Object.create(MiioValetudoRobot.prototype);
            Object.defineProperty(robot, "deviceId", {value: 123});
            Object.assign(robot, {ephemeralState: {mode: 6, taskStatus: 0},
                localSocket: wrapper(socket), dummyCloud: {miioSocket: {connected: true, sendMessage: async () => {
                    cloudCalls++;
                    throw new Error("PRIVATE_CLOUD_FIXTURE");
                }}}});
            robot.miotHelper = new DreameMiotHelper({robot: robot});
            const quirks = Research.createQuirks(robot, {fluidDetection: kind === "fluid",
                fluidDetectionModel: "dreame.vacuum.r2416"});
            const control = quirks[kind === "fluid" ? 1 : 0];
            await assert.rejects(() => control.setter(kind === "fluid" ? "enabled" : "routine"), error => {
                assert.equal(error.message.includes("PRIVATE_CLOUD"), false);
                assert.equal(error.message.includes("\"did\""), false);
                return /write.*unavailable/.test(error.message);
            });
            assert.equal(writes, 1);
            assert.equal(cloudCalls, 0);
            const visible = await control.serialize();
            assert.equal(visible.value, kind === "fluid" ? "enabled" : "routine");
            assert.equal(writes, 1);
        } finally {
            await Promise.all([new Promise(resolve => client.close(resolve)), new Promise(resolve => server.close(resolve))]);
        }
    });
}
