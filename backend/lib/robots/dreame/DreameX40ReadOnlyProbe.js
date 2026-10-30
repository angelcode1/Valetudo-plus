"use strict";

const Preflight = require("./DreameX40CleanGeniusPreflight");

// Exactly one preflight request followed by one settings request. No caller can
// turn this adapter into a generic MIIO command client or issue a third read.
const REQUESTS = Object.freeze([
    ["4:1", "4:7", "3:2", "4:18", "4:25"],
    ["4:50"]
]);

const IDENTITY_FAILURES = Object.freeze([
    "identity_config_unavailable",
    "identity_model_invalid",
    "identity_device_id_invalid",
    "identity_token_unavailable",
    "identity_token_invalid"
]);

class IdentityError extends Error {
    constructor(reason) {
        super(reason);
        this.reason = reason;
    }
}

// Do not import the normal robot class: constructing a probe must not start its
// servers or polling lifecycle. These are the R2416 variants recognised by X40.
// Never return file contents, credentials or underlying filesystem error text.
function readIdentity(fs) {
    let reason = "identity_config_unavailable";
    try {
        const config = fs.readFileSync("/data/config/miio/device.conf", "utf8");
        const field = key => {
            const matches = config.split(/\r?\n/).map(line =>
                line.match(new RegExp(`^[ \\t]*${key}[ \\t]*=[ \\t]*(.*?)[ \\t]*$`))
            ).filter(Boolean);
            return matches.length === 1 ? matches[0][1] : undefined;
        };
        reason = "identity_model_invalid";
        if (!["dreame.vacuum.r2416", "dreame.vacuum.r2416a", "dreame.vacuum.r2416c"].includes(field("model"))) {
            throw new Error();
        }
        reason = "identity_device_id_invalid";
        const did = field("did");
        const deviceId = Number(did);
        if (!did || !/^[0-9]+$/.test(did) || !Number.isSafeInteger(deviceId) ||
            deviceId <= 0 || deviceId >= 0xffffffff) {
            throw new Error();
        }
        reason = "identity_token_unavailable";
        const rawToken = fs.readFileSync("/data/config/miio/device.token");
        reason = "identity_token_invalid";
        if (!Buffer.isBuffer(rawToken)) {
            throw new Error();
        }
        // Preserve exact binary bytes. Accept only one optional LF/CRLF after
        // the 16-byte or 32-hex representation; never truncate arbitrary suffixes.
        let tokenBytes = rawToken;
        if ([17, 33].includes(rawToken.length) && rawToken[rawToken.length - 1] === 10) {
            tokenBytes = rawToken.subarray(0, -1);
        } else if ([18, 34].includes(rawToken.length) &&
            rawToken[rawToken.length - 2] === 13 && rawToken[rawToken.length - 1] === 10) {
            tokenBytes = rawToken.subarray(0, -2);
        }
        let token;
        if (tokenBytes.length === 16) {
            token = Buffer.from(tokenBytes);
        } else if (tokenBytes.length === 32 && /^[0-9a-fA-F]{32}$/.test(tokenBytes.toString("ascii")) &&
            tokenBytes.every(byte => byte < 128)) {
            token = Buffer.from(tokenBytes.toString("ascii"), "hex");
        } else {
            throw new Error();
        }
        return {deviceId: deviceId, token: token};
    } catch {
        throw new IdentityError(reason);
    }
}

function identityFailureReason(error) {
    return error instanceof IdentityError && IDENTITY_FAILURES.includes(error.reason) ? error.reason : undefined;
}

function createReadOnlyRobot(transport, deviceId) {
    if (!Number.isSafeInteger(deviceId) || deviceId <= 0 || deviceId >= 0xffffffff) {
        throw new Error("Invalid local device identity");
    }
    let requestsSent = 0;
    return {
        miotHelper: {
            readProperties: async props => {
                const expected = REQUESTS[requestsSent];
                if (!expected || !Array.isArray(props) || props.length !== expected.length ||
                    !props.every((p, i) => p && `${p.siid}:${p.piid}` === expected[i] &&
                        Object.keys(p).every(k => k === "siid" || k === "piid"))) {
                    throw new Error("Read-only request scope refused");
                }
                // Consume the budget even when transport fails. Never retry.
                requestsSent++;
                const response = await transport.sendMessage({
                    method: "get_properties",
                    params: props.map(p => ({did: deviceId, siid: p.siid, piid: p.piid}))
                }, {timeout: 3000});
                return response;
            },
            readProperty: async (siid, piid) => {
                const expected = REQUESTS[requestsSent];
                if (!expected || expected.length !== 1 || expected[0] !== `${siid}:${piid}`) {
                    throw new Error("Read-only request scope refused");
                }
                requestsSent++;
                const response = await transport.sendMessage({
                    method: "get_properties",
                    params: [{did: deviceId, siid: siid, piid: piid}]
                }, {timeout: 3000});
                if (!Array.isArray(response) || response.length !== 1 ||
                    response[0]?.siid !== siid || response[0]?.piid !== piid || response[0]?.code !== 0) {
                    throw new Error("Invalid settings response");
                }
                return response[0].value;
            }
        },
        requestsSent: () => requestsSent
    };
}

async function readDiagnostic(robot) {
    const preflight = await Preflight.readFresh(robot);
    const settings = await Preflight.readSettings(robot);
    return {
        state: "read_only_observations_received",
        readOnly: true,
        nativeWritesRequested: 0,
        getPropertiesRequests: robot.requestsSent(),
        preflight: preflight,
        settings: settings
    };
}

module.exports = {
    createReadOnlyRobot: createReadOnlyRobot,
    readDiagnostic: readDiagnostic,
    readIdentity: readIdentity,
    identityFailureReason: identityFailureReason
};
