"use strict";

const Preflight = require("./DreameX40CleanGeniusPreflight");

// Exactly one preflight request followed by one settings request. No caller can
// turn this adapter into a generic MIIO command client or issue a third read.
const REQUESTS = Object.freeze([
    ["4:1", "4:7", "3:2", "4:18", "4:25"],
    ["4:50"]
]);

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

module.exports = {createReadOnlyRobot: createReadOnlyRobot, readDiagnostic: readDiagnostic};
