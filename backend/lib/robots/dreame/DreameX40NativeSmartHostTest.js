"use strict";

const CleanGeniusReadOnlyStatus = require("./DreameX40CleanGeniusReadOnlyStatus");
const DreameMiotServices = require("./DreameMiotServices");

const TEST_ENV = "VALETUDO_X40_NATIVE_SMARTHOST_TEST";
const MIOT = DreameMiotServices.GEN2;

const FIELDS = Object.freeze([
    Object.freeze({siid: MIOT.VACUUM_2.SIID, piid: MIOT.VACUUM_2.PROPERTIES.MODE.PIID}),
    Object.freeze({siid: MIOT.VACUUM_2.SIID, piid: MIOT.VACUUM_2.PROPERTIES.TASK_STATUS.PIID}),
    Object.freeze({siid: MIOT.BATTERY.SIID, piid: MIOT.BATTERY.PROPERTIES.CHARGING.PIID}),
    Object.freeze({siid: MIOT.VACUUM_2.SIID, piid: MIOT.VACUUM_2.PROPERTIES.ERROR_CODE.PIID}),
    Object.freeze({siid: MIOT.VACUUM_2.SIID, piid: MIOT.VACUUM_2.PROPERTIES.MOP_DOCK_STATUS.PIID}),
    Object.freeze({siid: MIOT.VACUUM_2.SIID, piid: MIOT.VACUUM_2.PROPERTIES.MISC_TUNABLES.PIID})
]);

class SmartHostGateError extends Error {
    constructor(message, statusCode = 409) {
        super(message);
        this.name = "SmartHostGateError";
        this.statusCode = statusCode;
    }
}

/**
 * @param {object} robot
 * @param {object} [env]
 * @returns {boolean}
 */
function isWriteGateOpen(robot, env = process.env) {
    return env[TEST_ENV] === "1" &&
        robot?.allowCleanGeniusObserveOnly === true &&
        robot?.allowExperimentalCleanGenius !== true;
}

/**
 * Read six native properties WITHOUT invoking pollState or parseAndUpdateState.
 * MIOT response and settings data are sanitized before returning to callers.
 *
 * @param {object} robot
 * @returns {Promise<object>}
 */
async function getFreshPreflight(robot) {
    const response = await robot.miotHelper.readProperties(FIELDS);
    if (!Array.isArray(response) || response.length !== FIELDS.length ||
        response.some((entry, index) => !entry || entry.code !== 0 ||
            entry.siid !== FIELDS[index].siid || entry.piid !== FIELDS[index].piid)) {
        throw new SmartHostGateError("Native preflight property read failed", 502);
    }

    const mode = response[0].value;
    const taskStatus = response[1].value;
    const chargeCode = response[2].value;
    const errorCode = response[3].value;
    const dockWashCode = response[4].value;
    const nativeSettings = CleanGeniusReadOnlyStatus.parseSettings(response[5].value);

    const modeValid = Number.isSafeInteger(mode);
    const taskValid = Number.isSafeInteger(taskStatus);
    const chargingValid = Number.isSafeInteger(chargeCode);
    // The existing Gen2 firmware parser treats an empty string and "0"
    // as no error. Keep unknown or reminder codes as blockers.
    const errorValid = errorCode === 0 || errorCode === "0" || errorCode === "";
    const dockWashValid = Number.isSafeInteger(dockWashCode);
    // Allow only a short numeric/error-list representation. Never echo
    // arbitrary firmware strings or objects in the read-only response.
    let safeErrorCode = null;
    if (errorCode === "") {
        safeErrorCode = "";
    } else if (Number.isSafeInteger(errorCode) && errorCode >= 0 && errorCode <= 999999) {
        safeErrorCode = String(errorCode);
    } else if (typeof errorCode === "string" && errorCode.length <= 48 &&
        /^[0-9]{1,6}(,[0-9]{1,6}){0,5}$/.test(errorCode)) {
        safeErrorCode = errorCode;
    }

    if (!modeValid || !taskValid || !chargingValid || !dockWashValid) {
        throw new SmartHostGateError("Native preflight did not return valid mode, task or dock states", 502);
    }

    // R2416 exact baseline currently observed by the operator.
    const baselineMatch = nativeSettings.cleanGenius.value === 0 &&
        nativeSettings.autoReclean.value === -1 &&
        nativeSettings.autoRewash.value === 0 &&
        nativeSettings.stainIdentification.value === 1 &&
        nativeSettings.hotWash.value === 1;

    // Dreame's existing STATUS_MAP maps 6 to DOCKED and 0 to IDLE.
    // Charging=1 and task=0 are still mandatory. In particular, a mop
    // dock that is drying (2) must not silently pass this safety gate.
    const idleAndDocked = (mode === 0 || mode === 6) &&
        taskStatus === 0 && chargeCode === 1 &&
        errorValid && dockWashCode === 0;
    return {
        source: "native_miot_direct_preflight",
        readOnly: true,
        mode: mode,
        taskStatus: taskStatus,
        chargeCode: chargeCode,
        errorClear: errorValid,
        errorCode: safeErrorCode,
        errorCodeFormatRecognized: safeErrorCode !== null,
        dockWashCode: dockWashCode,
        idleAndDocked: idleAndDocked,
        baselineMatch: baselineMatch,
        writeGateOpen: isWriteGateOpen(robot),
        canTestMode1: idleAndDocked && baselineMatch && isWriteGateOpen(robot),
        settings: nativeSettings
    };
}

/**
 * Exactly one native 4:50 SmartHost delta. No other tunable or action is sent.
 * Must be invoked only after an operator's explicit confirmed POST.
 *
 * @param {object} robot
 * @param {number} target
 * @returns {Promise<object>}
 */
async function writeSmartHostOneKey(robot, target) {
    if (target !== 0 && target !== 1) {
        throw new SmartHostGateError("Only native SmartHost 0 or 1 is permitted", 400);
    }
    if (!isWriteGateOpen(robot)) {
        throw new SmartHostGateError("X40 native SmartHost test is not opted in", 403);
    }
    if (robot.x40NativeSmartHostTestBusy === true) {
        throw new SmartHostGateError("Native SmartHost test already in progress", 409);
    }

    robot.x40NativeSmartHostTestBusy = true;
    try {
        let current;
        if (target === 1) {
            // Activation requires the complete, fresh safety preflight.
            const before = await getFreshPreflight(robot);
            if (!before.canTestMode1) {
                throw new SmartHostGateError("Mode 1 refused: robot not idle/docked or exact baseline changed");
            }
            current = before.settings.cleanGenius.value;
        } else {
            // Recovery must not depend on unrelated mode, dock or error sensors:
            // require only a fresh, validated native SmartHost readback.
            const raw = await robot.miotHelper.readProperty(
                MIOT.VACUUM_2.SIID,
                MIOT.VACUUM_2.PROPERTIES.MISC_TUNABLES.PIID
            );
            current = CleanGeniusReadOnlyStatus.parseSettings(raw).cleanGenius.value;
            if (current !== 0 && current !== 1 && current !== 2) {
                throw new SmartHostGateError("Restore refused: unrecognised current SmartHost value");
            }
        }

        if (current === target) {
            return {target: target, observed: current, changed: false, readbackVerified: true};
        }

        const writeValue = JSON.stringify({k: "SmartHost", v: target});
        await robot.miotHelper.writeProperty(
            MIOT.VACUUM_2.SIID,
            MIOT.VACUUM_2.PROPERTIES.MISC_TUNABLES.PIID,
            writeValue
        );

        // The write may have happened even if this verification fails.
        // Never retry automatically and never mask an uncertain outcome.
        const readback = await robot.miotHelper.readProperty(
            MIOT.VACUUM_2.SIID,
            MIOT.VACUUM_2.PROPERTIES.MISC_TUNABLES.PIID
        );
        const after = CleanGeniusReadOnlyStatus.parseSettings(readback);
        if (after.cleanGenius.value !== target) {
            throw new SmartHostGateError(
                "Native write returned but SmartHost readback differs; inspect before retrying",
                502
            );
        }
        return {
            target: target,
            observed: after.cleanGenius.value,
            changed: true,
            readbackVerified: true,
            settings: after
        };
    } finally {
        robot.x40NativeSmartHostTestBusy = false;
    }
}

module.exports = {
    TEST_ENV: TEST_ENV,
    SmartHostGateError: SmartHostGateError,
    isWriteGateOpen: isWriteGateOpen,
    getFreshPreflight: getFreshPreflight,
    writeSmartHostOneKey: writeSmartHostOneKey
};
