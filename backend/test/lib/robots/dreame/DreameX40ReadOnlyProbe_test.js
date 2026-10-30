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

function identityFiles(config = "model=dreame.vacuum.r2416\ndid=123\n", token = Buffer.alloc(16, 0x42)) {
    const calls = [];
    return {
        calls: calls,
        readFileSync: (file, encoding) => {
            calls.push(file);
            if (file === "/data/config/miio/device.conf") {
                assert.equal(encoding, "utf8");
                if (config instanceof Error) {
                    throw config;
                }
                return config;
            }
            assert.equal(file, "/data/config/miio/device.token");
            if (token instanceof Error) {
                throw token;
            }
            return token;
        }
    };
}

test("probe identity accepts R2416 regional models and preserves binary/hex tokens with bounded line endings", () => {
    const binary = Buffer.from([0, 255, 128, 66, 10, 13, 65, 66, 67, 68, 69, 70, 71, 72, 13, 10]);
    for (const model of ["r2416", "r2416a", "r2416c"]) {
        for (const representation of [binary, Buffer.from(binary.toString("hex").toUpperCase())]) {
            for (const suffix of ["", "\n", "\r\n"]) {
                const files = identityFiles(`model = dreame.vacuum.${model}\r\ndid = 123\r\n`,
                    Buffer.concat([representation, Buffer.from(suffix)]));
                const identity = Probe.readIdentity(files);
                assert.equal(identity.deviceId, 123);
                assert.deepEqual(identity.token, binary);
                assert.deepEqual(files.calls, ["/data/config/miio/device.conf", "/data/config/miio/device.token"]);
            }
        }
    }
});

test("probe identity rejects ambiguous models and device IDs before reading credentials", () => {
    const cases = [
        ["did=123\n", "identity_model_invalid"],
        ["model=dreame.vacuum.r2449a\ndid=123\n", "identity_model_invalid"],
        ["model=dreame.vacuum.r2416evil\ndid=123\n", "identity_model_invalid"],
        ["model=dreame.vacuum.r2416\nmodel=dreame.vacuum.r2416\ndid=123\n", "identity_model_invalid"],
        ["model=dreame.vacuum.r2416\ndid=123\ndid=124\n", "identity_device_id_invalid"]
    ];
    for (const did of ["", "0", "-1", "1.2", "1e3", "0x7b", "NaN", "4294967295", "9007199254740993", "123private"]) {
        cases.push([`model=dreame.vacuum.r2416\ndid=${did}\n`, "identity_device_id_invalid"]);
    }
    for (const [config, reason] of cases) {
        const files = identityFiles(config);
        assert.throws(() => Probe.readIdentity(files), error => Probe.identityFailureReason(error) === reason);
        assert.deepEqual(files.calls, ["/data/config/miio/device.conf"]);
    }
    for (const did of ["1", "4294967294"]) {
        assert.equal(Probe.readIdentity(identityFiles(`model=dreame.vacuum.r2416\ndid=${did}\n`)).deviceId, Number(did));
    }
});

test("probe identity sanitizes file failures and rejects malformed token suffixes rather than truncating them", () => {
    for (const [files, reason] of [
        [identityFiles(new Error("PRIVATE_FIXTURE")), "identity_config_unavailable"],
        [identityFiles(undefined, new Error("PRIVATE_FIXTURE")), "identity_token_unavailable"],
        ...[Buffer.alloc(0), Buffer.alloc(15), Buffer.alloc(17, 0x42), Buffer.alloc(32, 0xff),
            Buffer.from("z".repeat(32)), Buffer.from("a".repeat(32) + "private"),
            Buffer.from("a".repeat(32) + "\n\n"), Buffer.from("a".repeat(16) + "\nprivate")]
            .map(token => [identityFiles(undefined, token), "identity_token_invalid"])
    ]) {
        assert.throws(() => Probe.readIdentity(files), error => {
            assert.equal(Probe.identityFailureReason(error), reason);
            assert.equal(String(error).includes("PRIVATE_FIXTURE"), false);
            assert.equal(JSON.stringify(error).includes("PRIVATE_FIXTURE"), false);
            return true;
        });
    }
    assert.equal(Probe.identityFailureReason(new Error("PRIVATE_FIXTURE")), undefined);
    assert.equal(Probe.identityFailureReason({reason: "identity_token_invalid"}), undefined);
});

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
        Object.defineProperty(process, "platform", {value: "linux"});
        Object.defineProperty(process, "arch", {value: "arm64"});
        const fs = require("fs");
        const read = fs.readFileSync;
        fs.readFileSync = function(file, ...args) {
            if (file === "/data/config/miio/device.conf") return "model=dreame.vacuum.r2416a\\r\\ndid=123\\r\\n";
            if (file === "/data/config/miio/device.token") return Buffer.concat([Buffer.alloc(16, 0x42), Buffer.from("\\n")]);
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

test("actual CLI identity failures identify the failed check without opening a socket or printing private data", async () => {
    const entry = path.resolve(__dirname, "../../../../x40-readonly-probe.js");
    const validConfig = "model=dreame.vacuum.r2416\ndid=123\n";
    for (const [config, token, reason] of [
        [null, "B".repeat(16), "identity_config_unavailable"],
        ["model=PRIVATE_FIXTURE\ndid=123\n", "B".repeat(16), "identity_model_invalid"],
        ["model=dreame.vacuum.r2416\ndid=PRIVATE_FIXTURE\n", "B".repeat(16), "identity_device_id_invalid"],
        [validConfig, null, "identity_token_unavailable"],
        [validConfig, "PRIVATE_FIXTURE", "identity_token_invalid"]
    ]) {
        const code = `
            Object.defineProperty(process, "platform", {value: "linux"});
            Object.defineProperty(process, "arch", {value: "arm64"});
            require("dgram").createSocket = () => { throw new Error("SOCKET_MUST_NOT_OPEN"); };
            const fs = require("fs");
            const read = fs.readFileSync;
            fs.readFileSync = function(file, ...args) {
                if (file === "/data/config/miio/device.conf") {
                    if (${JSON.stringify(config)} === null) throw new Error("PRIVATE_FIXTURE");
                    return ${JSON.stringify(config)};
                }
                if (file === "/data/config/miio/device.token") {
                    if (${JSON.stringify(token)} === null) throw new Error("PRIVATE_FIXTURE");
                    return Buffer.from(${JSON.stringify(token)});
                }
                return read.call(this, file, ...args);
            };
            process.argv = [process.execPath, ${JSON.stringify(entry)}, "--readonly-x40-probe"];
            require(${JSON.stringify(entry)});
        `;
        const child = spawn(process.execPath, ["-e", code]);
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", d => {
            stdout += d;
        });
        child.stderr.on("data", d => {
            stderr += d;
        });
        const deadline = setTimeout(() => child.kill("SIGKILL"), 5000);
        try {
            const [exit] = await once(child, "close");
            assert.equal(exit, 3);
            assert.equal(stderr, "");
            assert.deepEqual(JSON.parse(stdout), {state: "failed", reason: reason, phase: "identity",
                getPropertiesRequests: 0, nativeWritesRequested: 0});
            assert.equal(stdout.includes("PRIVATE_FIXTURE"), false);
        } finally {
            clearTimeout(deadline);
            if (child.exitCode === null) {
                child.kill("SIGKILL");
            }
        }
    }
});

test("real CLI retains its Linux ARM64 requirement outside the simulated firmware fixtures", async () => {
    const entry = path.resolve(__dirname, "../../../../x40-readonly-probe.js");
    for (const [platform, arch] of [["darwin", "arm64"], ["linux", "x64"]]) {
        const code = `
            Object.defineProperty(process, "platform", {value: ${JSON.stringify(platform)}});
            Object.defineProperty(process, "arch", {value: ${JSON.stringify(arch)}});
            const fs = require("fs");
            const read = fs.readFileSync;
            fs.readFileSync = function(file, ...args) {
                if (String(file).startsWith("/data/config/miio/")) throw new Error("IDENTITY_MUST_NOT_LOAD");
                return read.call(this, file, ...args);
            };
            require("dgram").createSocket = () => { throw new Error("SOCKET_MUST_NOT_OPEN"); };
            process.argv = [process.execPath, ${JSON.stringify(entry)}, "--readonly-x40-probe"];
            require(${JSON.stringify(entry)});
        `;
        const child = spawn(process.execPath, ["-e", code]);
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", d => {
            stdout += d;
        });
        child.stderr.on("data", d => {
            stderr += d;
        });
        const deadline = setTimeout(() => child.kill("SIGKILL"), 5000);
        try {
            const [exit] = await once(child, "close");
            assert.equal(exit, 2);
            assert.equal(stderr, "");
            assert.deepEqual(JSON.parse(stdout), {state: "refused", reason: "linux_arm64_required"});
        } finally {
            clearTimeout(deadline);
            if (child.exitCode === null) {
                child.kill("SIGKILL");
            }
        }
    }
});
