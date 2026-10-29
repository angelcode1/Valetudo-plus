"use strict";

const assert = require("node:assert/strict");
const dgram = require("node:dgram");
const path = require("node:path");
const test = require("node:test");
const {once} = require("node:events");
const {spawn} = require("node:child_process");

const Codec = require("../../../../lib/miio/Codec");
const createMiioHeader = require("../../../../lib/miio/MiioHeader");
const Probe = require("../../../../lib/robots/dreame/DreameX40ReadOnlyProbe");

function transport() {
    const calls = [];
    return {
        calls: calls,
        sendMessage: async msg => {
            calls.push(msg);
            const data = {"4:1": 14, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0,
                "4:50": '[{"k":"SmartAutoMop","v":-1},{"k":"secret","v":"PRIVATE_FIXTURE"}]'};
            return msg.params.map(p => ({...p, code: 0, value: data[`${p.siid}:${p.piid}`]}));
        }
    };
}

test("probe permits exactly the two fixed get_properties requests and retains signed raw values", async () => {
    const wire = transport();
    const robot = Probe.createReadOnlyRobot(wire, 123);
    const result = await Probe.readDiagnostic(robot);
    assert.equal(result.getPropertiesRequests, 2);
    assert.equal(result.nativeWritesRequested, 0);
    assert.equal(result.preflight.mode, 14);
    assert.equal(result.preflight.activationAllowed, false);
    assert.equal(result.settings.settings.autoReclean.value, -1);
    assert.equal(result.settings.settings.autoReclean.state, "unknown");
    assert.equal(JSON.stringify(result).includes("PRIVATE_FIXTURE"), false);
    assert.deepEqual(wire.calls.map(m => m.method), ["get_properties", "get_properties"]);
    await assert.rejects(() => robot.miotHelper.readProperty(4, 50), /scope refused/);
    assert.equal(wire.calls.length, 2);
    assert.equal(robot.miotHelper.writeProperty, undefined);
    assert.equal(robot.miotHelper.executeAction, undefined);
});

test("probe rejects reordered, duplicate, extra, wrong-key and out-of-sequence request scopes before sending", async () => {
    const good = [{siid: 4, piid: 1}, {siid: 4, piid: 7}, {siid: 3, piid: 2}, {siid: 4, piid: 18}, {siid: 4, piid: 25}];
    for (const input of [good.slice().reverse(), [...good, good[0]], [good[0]],
        good.map((p, i) => i === 0 ? {...p, value: 1} : p),
        good.map((p, i) => i === 0 ? {...p, piid: 50} : p)]) {
        const wire = transport();
        const robot = Probe.createReadOnlyRobot(wire, 123);
        await assert.rejects(() => robot.miotHelper.readProperties(input), /scope refused/);
        await assert.rejects(() => robot.miotHelper.readProperty(4, 50), /scope refused/);
        assert.equal(wire.calls.length, 0);
    }
    for (const id of [0, -1, 1.2, NaN, "123", 0xffffffff]) {
        assert.throws(() => Probe.createReadOnlyRobot(transport(), id), /identity/);
    }
});

test("probe consumes failed request budget without retrying", async () => {
    const wire = transport();
    const robot = Probe.createReadOnlyRobot(wire, 123);
    let sends = 0;
    wire.sendMessage = async () => {
        sends++; throw new Error("transport unavailable");
    };
    await assert.rejects(() => Probe.readDiagnostic(robot), /unavailable/);
    await assert.rejects(() => Probe.readDiagnostic(robot), /scope refused/);
    assert.equal(sends, 1);
});

test("actual probe CLI uses loopback encrypted reads only and suppresses private transport data", async () => {
    const server = dgram.createSocket("udp4");
    const token = Buffer.alloc(16, 0x42);
    const codec = new Codec({token: token});
    codec.updateStamp(100);
    const packets = [];
    server.on("message", (packet, peer) => {
        if (packet.length === 32) {
            packets.push("handshake");
            const reply = createMiioHeader({timestamp: 100, deviceId: 123, unknown: 0});
            server.send(reply, peer.port, peer.address);
            return;
        }
        const decoded = codec.decodeIncomingMiioPacket(packet);
        const msg = decoded.msg;
        packets.push(msg.method);
        assert.equal(msg.method, "get_properties");
        const data = {"4:1": 14, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0,
            "4:50": '[{"k":"SmartAutoMop","v":-1},{"k":"secret","v":"PRIVATE_FIXTURE"}]'};
        const result = msg.params.map(p => ({...p, code: 0, value: data[`${p.siid}:${p.piid}`]}));
        const reply = codec.encodeOutgoingMiioPacket({id: msg.id, result: result}, 123);
        server.send(reply, peer.port, peer.address);
    });
    server.bind(54321, "127.0.0.1");
    await once(server, "listening");
    const entry = path.resolve(__dirname, "../../../../x40-readonly-probe.js");
    // Fake only the machine identity and credential reads in this child. The
    // actual CLI, encrypted socket, bounded adapter and shared parsers execute.
    const code = `
        Object.defineProperty(process, "arch", {value: "arm64"});
        const fs = require("fs");
        const read = fs.readFileSync;
        fs.readFileSync = function(file, ...args) {
            if (file === "/data/config/miio/device.conf") return "model=dreame.vacuum.r2416\\ndid=123\\n";
            if (file === "/data/config/miio/device.token") return Buffer.alloc(16, 0x42);
            return read.call(this, file, ...args);
        };
        process.argv = [process.execPath, ${JSON.stringify(entry)}, "--readonly-x40-probe"];
        require(${JSON.stringify(entry)});
    `;
    let child;
    let deadline;
    try {
        child = spawn(process.execPath, ["-e", code]);
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", d => {
            stdout += d;
        });
        child.stderr.on("data", d => {
            stderr += d;
        });
        deadline = setTimeout(() => child.kill("SIGKILL"), 12000);
        const [exit] = await once(child, "close");
        assert.equal(exit, 0, stdout + stderr);
        assert.equal(stderr, "");
        const result = JSON.parse(stdout);
        assert.equal(result.state, "read_only_observations_received");
        assert.equal(result.settings.settings.autoReclean.value, -1);
        assert.equal(stdout.includes("PRIVATE_FIXTURE"), false);
        assert.deepEqual(packets, ["handshake", "get_properties", "get_properties"]);
    } finally {
        clearTimeout(deadline);
        if (child && child.exitCode === null) {
            child.kill("SIGKILL");
        }
        await new Promise(resolve => server.close(resolve));
    }
});
