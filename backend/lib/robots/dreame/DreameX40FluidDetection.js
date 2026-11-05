"use strict";

const DreameMiotServices = require("./DreameMiotServices");
const DreameUtils = require("./DreameUtils");
const Preflight = require("./DreameX40CleanGeniusPreflight");
const Quirk = require("../../core/Quirk");

const MIOT = DreameMiotServices.GEN2.VACUUM_2;
const SIID = MIOT.SIID;
const PIID = MIOT.PROPERTIES.AI_CAMERA_SETTINGS.PIID;
// Pinned reference DEVICE_INFO entries have FLUID_DETECTION (27), minimum 1.
// Do not extend this to other models merely because the same driver handles them.
const MODELS = Object.freeze(["dreame.vacuum.r2416", "dreame.vacuum.r2416a", "dreame.vacuum.r2416c"]);

class FluidError extends Error {
    constructor(reason) {
        super(`X40 fluid detection: ${reason}`);
        this.reason = reason;
    }
}

function validateAI(raw) {
    if (!Number.isSafeInteger(raw) || raw < 0 || raw > 0xffffffff) {
        throw new FluidError("ai_settings_format_unverified");
    }
    return raw;
}

async function readAI(robot) {
    let raw;
    try {
        raw = await robot.miotHelper.readProperty(SIID, PIID, {retry: false, interface: "local", strict: true, timeout: 3000});
    } catch {
        throw new FluidError("ai_settings_unavailable");
    }
    return validateAI(raw);
}

async function readFreshSafetyAndAI(robot) {
    // One fixed six-property response supplies both the safety observations
    // and the complete AI snapshot to edit. No cached UI reading is reused.
    let values;
    try {
        values = await robot.miotHelper.readProperties([
            ...Preflight.getStatusProperties(), {siid: SIID, piid: PIID}
        ], {retry: false, interface: "local", strict: true, timeout: 3000});
    } catch {
        throw new FluidError("fresh_safety_not_confirmed");
    }
    const ai = Array.isArray(values) ? values.filter(v => v?.siid === SIID && v?.piid === PIID) : [];
    if (!Array.isArray(values) || values.length !== 6 || ai.length !== 1 || ai[0].code !== 0) {
        throw new FluidError("fresh_safety_not_confirmed");
    }
    const raw = validateAI(ai[0].value);
    let fresh;
    try {
        fresh = Preflight.parseFreshResponse(values.filter(v => v !== ai[0]));
    } catch {
        throw new FluidError("fresh_safety_not_confirmed");
    }
    if (!fresh.activationAllowed) {
        throw new FluidError("fresh_safety_not_confirmed");
    }
    return raw;
}

function createQuirk(robot, options) {
    const requireModel = () => {
        if (!MODELS.includes(options.model)) {
            throw new FluidError("model_capability_unverified");
        }
    };
    const requireCachedIdle = () => {
        if (!options.isIdle(robot)) {
            throw new FluidError("cached_state_not_idle");
        }
    };
    const quirk = new Quirk({
        id: "13419f65-e106-47ca-a0a7-0a64f1c82a1a",
        title: "EXPERIMENTAL Fluid Detection",
        description: "Detect fluid with the AI camera. Separate from stain avoidance. Firmware acceptance is unverified; change only while idle.",
        options: ["disabled", "enabled"],
        getter: async () => {
            requireModel();
            return ((await readAI(robot)) & 8) !== 0 ? "enabled" : "disabled";
        },
        setter: async value => {
            if (!["disabled", "enabled"].includes(value)) {
                throw new Error("Invalid fluid detection selection");
            }
            requireModel();
            requireCachedIdle();
            await options.withLock(() => DreameUtils.WITH_AI_SETTINGS_LOCK(robot, async () => {
                const raw = await readFreshSafetyAndAI(robot);
                if ((raw & 2) === 0) {
                    throw new FluidError("ai_obstacle_detection_disabled");
                }
                requireCachedIdle();
                const target = (value === "enabled" ? raw | 8 : raw & ~8) >>> 0;
                if (target === raw) {
                    return;
                }
                try {
                    await robot.miotHelper.writeProperty(SIID, PIID, target,
                        {retry: false, interface: "local", strict: true, timeout: 3000});
                } catch {
                    throw new FluidError("ai_write_unavailable_native_state_unverified");
                }
                // Compare the complete target, not just the requested bit.
                // Failure may follow an applied write: never retry or roll back blindly.
                let observed;
                try {
                    observed = await readAI(robot);
                } catch {
                    throw new FluidError("ai_readback_unavailable_native_state_unverified");
                }
                if (observed !== target) {
                    throw new FluidError("ai_readback_mismatch_native_state_unverified");
                }
                if (!options.isIdle(robot)) {
                    throw new FluidError("state_changed_after_verified_write");
                }
            }));
        }
    });
    quirk.serialize = async () => {
        let value = "unavailable";
        let reason = null;
        try {
            requireModel();
            const raw = await readAI(robot);
            value = (raw & 8) !== 0 ? "enabled" : "disabled";
            if ((raw & 2) === 0) {
                reason = "ai_obstacle_detection_disabled";
            }
        } catch (error) {
            reason = error instanceof FluidError ? error.reason : "ai_settings_unavailable";
        }
        return {id: quirk.id, title: quirk.title, description: quirk.description,
            options: reason ? [value] : quirk.options, value: value,
            readOnly: reason !== null, rawValue: null, unavailableReason: reason};
    };
    return quirk;
}

module.exports = {createQuirk: createQuirk};
