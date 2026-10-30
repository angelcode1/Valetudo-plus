"use strict";

const Settings = require("./DreameX40CleanGeniusReadOnlyStatus");

// Fixed MIOT allowlist. These direct reads never invoke pollState/state parsing.
const FIELDS = Object.freeze([
    {siid: 4, piid: 1}, // Mode
    {siid: 4, piid: 7}, // Task
    {siid: 3, piid: 2}, // Charging
    {siid: 4, piid: 18}, // Error
    {siid: 4, piid: 25} // Dock activity
]);

async function readFresh(robot) {
    const values = await robot.miotHelper.readProperties(FIELDS.map(p => ({...p})));
    if (!Array.isArray(values) || values.length !== FIELDS.length ||
        !FIELDS.every(p => values.filter(v => v?.siid === p.siid && v?.piid === p.piid).length === 1) ||
        values.some(v => v?.code !== 0)) {
        throw new Error("The X40 did not return complete successful observations in a fresh MIOT read");
    }
    const raw = FIELDS.map(p => values.find(v => v.siid === p.siid && v.piid === p.piid).value);
    const [mode, taskStatus, chargeCode, errorCode, dockWashCode] = raw;
    if (![mode, taskStatus, chargeCode, dockWashCode].every(Number.isSafeInteger)) {
        throw new Error("The X40 returned invalid status types in a fresh MIOT read");
    }
    const errorClear = errorCode === 0 || errorCode === "0" || errorCode === "";
    let blockedReason = null;
    if (mode === 14) {
        blockedReason = "powersave_requires_awake_idle_observation";
    } else if (![0, 6].includes(mode)) {
        blockedReason = "mode_not_idle_or_docked";
    } else if (taskStatus !== 0) {
        blockedReason = "task_active";
    } else if (chargeCode !== 1) {
        blockedReason = "charging_not_confirmed";
    } else if (!errorClear) {
        blockedReason = "error_not_clear";
    } else if (dockWashCode !== 0) {
        blockedReason = "dock_not_idle";
    }
    return {
        source: "native_miot_direct_preflight",
        readOnly: true,
        observedAt: new Date().toISOString(),
        mode: mode,
        taskStatus: taskStatus,
        chargeCode: chargeCode,
        errorClear: errorClear,
        dockWashCode: dockWashCode,
        // Information only. A setter must obtain its own fresh observations.
        activationAllowed: blockedReason === null,
        blockedReason: blockedReason
    };
}

async function readSettings(robot) {
    const raw = await robot.miotHelper.readProperty(4, 50);
    return {
        source: "native_miot_direct_settings",
        readOnly: true,
        observedAt: new Date().toISOString(),
        settings: Settings.parseSettings(raw)
    };
}

async function readStainAvoidancePrerequisites(robot) {
    // Reference integer AI protocol, not a proof of model capability. Never
    // write AI flags to satisfy this gate or expose the complete AI bitmask.
    const result = {
        source: "native_miot_direct_ai_settings",
        readOnly: true,
        observedAt: null,
        obstacleDetection: null,
        fluidDetection: null,
        prerequisitesMatch: false,
        blockedReason: "ai_settings_unavailable"
    };
    let raw;
    try {
        raw = await robot.miotHelper.readProperty(4, 22);
    } catch {
        return result;
    }
    result.observedAt = new Date().toISOString();
    if (!Number.isSafeInteger(raw) || raw < 0 || raw > 0xffffffff) {
        result.blockedReason = "ai_settings_format_unverified";
        return result;
    }
    result.obstacleDetection = (raw & 2) !== 0;
    result.fluidDetection = (raw & 8) !== 0;
    result.blockedReason = !result.obstacleDetection ? "ai_obstacle_detection_disabled" :
        !result.fluidDetection ? "ai_fluid_detection_disabled" : null;
    result.prerequisitesMatch = result.blockedReason === null;
    return result;
}

module.exports = {readFresh: readFresh, readSettings: readSettings,
    readStainAvoidancePrerequisites: readStainAvoidancePrerequisites};
