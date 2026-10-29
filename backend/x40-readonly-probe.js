"use strict";

const dgram = require("dgram");
const fs = require("fs");
const {once} = require("events");

const Probe = require("./lib/robots/dreame/DreameX40ReadOnlyProbe");

// The codec can log firmware packets and secrets on errors. A dedicated probe
// process suppresses all Logger output before importing the transport. Its only
// output is the fixed result envelope and the shared allowlisted status parsers.
const Logger = require("./lib/Logger");
Logger.log = () => {};
const createMiioHeader = require("./lib/miio/MiioHeader");
const MiioSocket = require("./lib/miio/MiioSocket");

function emit(value) {
    process.stdout.write(JSON.stringify(value) + "\n");
}

async function main() {
    if (process.argv.length !== 3 || process.argv[2] !== "--readonly-x40-probe") {
        emit({state: "refused", reason: "explicit_readonly_probe_argument_required"});
        process.exitCode = 2;
        return;
    }
    if (process.platform !== "linux" || process.arch !== "arm64") {
        emit({state: "refused", reason: "linux_arm64_required"});
        process.exitCode = 2;
        return;
    }
    let phase = "identity";
    let robot;
    const deadline = setTimeout(() => {
        emit({state: "failed", reason: "probe_deadline", nativeWritesRequested: 0});
        process.exit(3);
    }, 20000);
    let socket;
    try {
        const config = fs.readFileSync("/data/config/miio/device.conf", "utf8");
        const get = key => config.match(new RegExp(`^${key}=([^\\r\\n]+)`, "m"))?.[1];
        if (get("model") !== "dreame.vacuum.r2416") {
            throw new Error("Device identity unavailable");
        }
        const deviceId = Number(get("did"));
        const rawToken = fs.readFileSync("/data/config/miio/device.token");
        let token;
        if (rawToken.length >= 32 && /^[0-9a-fA-F]{32}$/.test(rawToken.toString().slice(0, 32))) {
            token = Buffer.from(rawToken.toString().slice(0, 32), "hex");
        } else if (rawToken.length === 16) {
            token = Buffer.from(rawToken);
        } else {
            throw new Error("Device identity unavailable");
        }
        if (!Number.isSafeInteger(deviceId) || deviceId <= 0 || deviceId >= 0xffffffff) {
            throw new Error("Device identity unavailable");
        }
        phase = "local_socket";
        socket = dgram.createSocket("udp4");
        socket.bind(0, "127.0.0.1");
        await once(socket, "listening");
        // A connected ephemeral UDP socket only accepts the local firmware peer.
        socket.connect(MiioSocket.PORT, "127.0.0.1");
        await once(socket, "connect");
        // MiioSocket.sendMessage supplies a destination, so use a send wrapper
        // compatible with connected dgram sockets while enforcing the same peer.
        const send = socket.send.bind(socket);
        socket.send = (buffer, offset, length, port, address) => {
            if (port !== MiioSocket.PORT || address !== "127.0.0.1") {
                throw new Error("Local peer scope refused");
            }
            send(buffer.subarray(offset, offset + length));
        };
        const transport = new MiioSocket({
            socket: socket,
            token: token,
            deviceId: deviceId,
            rinfo: {address: "127.0.0.1", port: MiioSocket.PORT},
            timeout: 3000,
            name: "x40-readonly-probe",
            isCloudSocket: false
        });
        phase = "handshake";
        // One local handshake. No RetryWrapper, cloud server, clock response,
        // state parser, scheduler, HTTP server, map action or setting writer.
        await new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error("Handshake unavailable")), 3000);
            transport.registerOnEmptyPacketHook(() => {
                clearTimeout(timer);
                resolve();
            });
            const packet = createMiioHeader();
            socket.send(packet, 0, packet.length, MiioSocket.PORT, "127.0.0.1");
        });
        phase = "native_reads";
        robot = Probe.createReadOnlyRobot(transport, deviceId);
        emit(await Probe.readDiagnostic(robot));
    } catch {
        emit({state: "failed", reason: "local_read_unavailable", phase: phase,
            getPropertiesRequests: robot?.requestsSent() ?? 0, nativeWritesRequested: 0});
        process.exitCode = 3;
    } finally {
        if (socket) {
            try {
                await new Promise(resolve => socket.close(resolve));
            } catch {
                // The deadline remains armed until cleanup is finished.
            }
        }
        clearTimeout(deadline);
    }
}

process.on("uncaughtException", () => {
    emit({state: "failed", reason: "probe_runtime_error", nativeWritesRequested: 0});
    process.exit(3);
});
process.on("unhandledRejection", () => {
    emit({state: "failed", reason: "probe_runtime_error", nativeWritesRequested: 0});
    process.exit(3);
});

main();
