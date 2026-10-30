"use strict";

const DreameMiotServices = require("./DreameMiotServices");
const Preflight = require("./DreameX40CleanGeniusPreflight");
const Quirk = require("../../core/Quirk");

const MIOT = DreameMiotServices.GEN2.VACUUM_2;
const SIID = MIOT.SIID;
const PIID = MIOT.PROPERTIES.MISC_TUNABLES.PIID;

// An experimental X40-specific controller, deliberately outside upstream's
// generic capabilities. No setting is modified on boot or when this is disabled.
const EXPERIMENTAL_ENV = "VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS";
const ADVANCED_ENV = "VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED";
const SIGNED_ENV = "VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED";
const STAIN_AVOIDANCE_ENV = "VALETUDO_X40_EXPERIMENTAL_STAIN_AVOIDANCE";

const SETTINGS = Object.freeze([
    Object.freeze({
        id: "f7bba2a1-2d89-4f8f-a404-b3ea031eec41",
        title: "EXPERIMENTAL CleanGenius",
        description: "Unverified X40 native CleanGenius mode. Manual cleaning controls may be ignored in Routine/Deep. Change only while idle.",
        key: "SmartHost",
        signed: false,
        values: Object.freeze({off: 0, routine: 1, deep: 2})
    }),
    Object.freeze({
        id: "c0d24419-6d57-48b0-a14b-129be1b83a3c",
        title: "EXPERIMENTAL Auto Reclean",
        description: "Native SmartAutoMop setting, if exposed by the firmware. The robot must be idle to change it.",
        key: "SmartAutoMop",
        signed: true,
        values: Object.freeze({off: 0, deep_only: 1, all_modes: 2})
    }),
    Object.freeze({
        id: "b7079e4c-69d6-4d66-8c64-ce61fe55a853",
        title: "EXPERIMENTAL Auto Rewash",
        description: "Native SmartAutoWash setting, if exposed by the firmware. The robot must be idle to change it.",
        key: "SmartAutoWash",
        signed: true,
        values: Object.freeze({off: 0, deep_only: 1, all_modes: 2})
    })
]);

// Reference integration uses StainIdentify for stain avoidance, with 1/2
// meaning disabled/enabled. This is not a boolean stain-identification switch.
// Keep this protocol separate from the main mode and signed auto-mode opt-ins.
const STAIN_AVOIDANCE = Object.freeze({
    id: "d14996e9-e8da-4cc4-9a67-1c52b07b83c5",
    title: "EXPERIMENTAL Stain Avoidance",
    description: "Reference stain-avoidance setting; X40 acceptance is unverified. AI obstacle and fluid detection must already be enabled. Change only while idle. This does not enable CleanGenius or confirm stain detection.",
    key: "StainIdentify",
    signed: false,
    values: Object.freeze({disabled: 1, enabled: 2})
});

function isEnabled(env = process.env) {
    return env[EXPERIMENTAL_ENV] === "1";
}

// Auto Reclean/Rewash controls are never offered in the initial trial.
// They require a second deliberate opt-in and remain hardware-unverified.
function isAdvancedEnabled(env = process.env) {
    return isEnabled(env) && env[ADVANCED_ENV] === "1";
}

function isSignedEnabled(env = process.env) {
    return isAdvancedEnabled(env) && env[SIGNED_ENV] === "1";
}

function isStainAvoidanceEnabled(env = process.env) {
    return isEnabled(env) && env[STAIN_AVOIDANCE_ENV] === "1";
}

function isIdle(robot) {
    // Cached eligibility alone never authorizes a write. The full fresh gate follows.
    return [0, 6].includes(robot.ephemeralState?.mode) && robot.ephemeralState?.taskStatus === 0;
}

// Diagnostic text only. Values come from the existing cached MIOT state;
// never query the robot or weaken the idle guard just to format an error.
function describeCachedIdleState(robot) {
    const describe = value => {
        if (typeof value === "number" && Number.isSafeInteger(value)) {
            return String(value);
        }
        if (typeof value === "string" && /^-?\d{1,6}$/.test(value)) {
            return `${value} (string)`;
        }
        return "unavailable";
    };

    return `cached mode=${describe(robot.ephemeralState?.mode)}, taskStatus=${describe(robot.ephemeralState?.taskStatus)}`;
}

function decodeValue(raw, definition) {
    const matchingName = Object.keys(definition.values).find(name => {
        return definition.values[name] === raw;
    });

    if (!matchingName) {
        throw new Error(`Unsupported ${definition.key} value: ${raw}`);
    }

    return matchingName;
}

async function readSettings(robot) {
    const snapshot = await Preflight.readSettings(robot);
    return {
        SmartHost: snapshot.settings.cleanGenius.value,
        SmartAutoMop: snapshot.settings.autoReclean.value,
        SmartAutoWash: snapshot.settings.autoRewash.value,
        StainIdentify: snapshot.settings.stainIdentification.value
    };
}

async function requireFreshIdle(robot) {
    const fresh = await Preflight.readFresh(robot);
    if (!fresh.activationAllowed) {
        throw new Error(`The X40 did not confirm safe idle state in a fresh MIOT read: ${fresh.blockedReason}`);
    }
}

function createQuirks(robot, options = {}) {
    // All selectors share one MIOT 4:50 property; serialize UI writes.
    // This is a manual, supervised operation. It never runs at startup.
    let changeInProgress = false;

    const definitions = [
        ...(options.advanced === true ? SETTINGS : SETTINGS.slice(0, 1)),
        ...(options.stainAvoidance === true ? [STAIN_AVOIDANCE] : [])
    ];
    return definitions.map(definition => {
        const quirk = new Quirk({
            id: definition.id,
            title: definition.title,
            description: definition.description,
            options: Object.keys(definition.values),
            getter: async () => {
                const data = await readSettings(robot);

                return decodeValue(data[definition.key], definition);
            },
            setter: async value => {
                if (!Object.prototype.hasOwnProperty.call(definition.values, value)) {
                    throw new Error(`Invalid ${definition.key} selection: ${value}`);
                }
                const recovery = definition.key === "SmartHost" && value === "off";
                if (!recovery && !isIdle(robot)) {
                    throw new Error(`The X40 must be idle before changing ${definition.key}; ${describeCachedIdleState(robot)}; no write attempted`);
                }
                if (definition.signed === true && options.signedProtocol !== true) {
                    throw new Error("Signed Reclean/Rewash protocol is not opted in; no write attempted");
                }
                if (changeInProgress) {
                    throw new Error("Another X40 CleanGenius setting change is in progress");
                }

                changeInProgress = true;
                try {
                    // Do not write unsupported firmware values (including -1
                    // SmartAutoMop) or an absent setting.
                    const current = await readSettings(robot);
                    decodeValue(current[definition.key], definition);

                    // Polls are asynchronous: a cleaning task may begin during
                    // the MIOT read. Re-check immediately before the write.
                    if (!recovery && !isIdle(robot)) {
                        throw new Error(`The X40 is no longer idle; ${definition.key} was not written; ${describeCachedIdleState(robot)}`);
                    }
                    if (definition.key === "StainIdentify") {
                        const prerequisites = await Preflight.readStainAvoidancePrerequisites(robot);
                        if (!prerequisites.prerequisitesMatch) {
                            throw new Error(`X40 stain avoidance prerequisites were not confirmed: ${prerequisites.blockedReason}; no write attempted`);
                        }
                    }
                    if (!recovery) {
                        await requireFreshIdle(robot);
                    }
                    if (!recovery && !isIdle(robot)) {
                        throw new Error(`The X40 is no longer idle; ${definition.key} was not written; ${describeCachedIdleState(robot)}`);
                    }

                    // Reference protocol: disabling a positive auto mode preserves
                    // its selection as a signed negative. Still separately opted in
                    // and hardware-unverified. Unknown current values stay blocked.
                    const target = definition.signed === true && value === "off" && current[definition.key] > 0 ?
                        -current[definition.key] : definition.values[value];
                    if (current[definition.key] === target) {
                        return;
                    }

                    // Never send a whole AutoSwitch blob or retry on error.
                    await robot.miotHelper.writeProperty(
                        SIID,
                        PIID,
                        JSON.stringify({k: definition.key, v: target})
                    );

                    // A MIOT transport acknowledgement is not confirmation
                    // that the new setting has actually persisted.
                    // If readback fails, the write may still have applied;
                    // do not retry automatically or attempt blind rollback.
                    const observed = await readSettings(robot);
                    if (observed[definition.key] !== target) {
                        throw new Error(
                            `X40 ${definition.key} readback mismatch after write; ` +
                            "actual firmware setting is unverified"
                        );
                    }
                    if (!recovery && !isIdle(robot)) {
                        throw new Error(
                            `X40 ${definition.key} read back, but task state changed; ` +
                            "check the robot before continuing"
                        );
                    }
                } finally {
                    changeInProgress = false;
                }
            }
        });
        // An unsupported setting must remain visible instead of being silently
        // dropped by QuirksCapability. Never expose firmware/transport error text.
        quirk.serialize = async () => {
            let raw = null;
            let value = "unavailable";
            let reason = "settings_unavailable";
            try {
                const current = await readSettings(robot);
                raw = current[definition.key];
                try {
                    value = decodeValue(raw, definition);
                    reason = definition.signed === true && options.signedProtocol !== true ?
                        "signed_protocol_not_opted_in" : null;
                    if (reason === null && definition.key === "StainIdentify") {
                        reason = (await Preflight.readStainAvoidancePrerequisites(robot)).blockedReason;
                    }
                } catch {
                    value = "unsupported";
                    reason = "native_value_unverified";
                }
            } catch {
                // A failed read produces a disabled control, never a stale value.
            }
            return {
                id: quirk.id,
                title: quirk.title,
                description: quirk.description,
                options: reason ? [value] : quirk.options,
                value: value,
                readOnly: reason !== null,
                rawValue: Number.isSafeInteger(raw) ? raw : null,
                unavailableReason: reason
            };
        };
        return quirk;
    });
}

module.exports = {
    EXPERIMENTAL_ENV: EXPERIMENTAL_ENV,
    ADVANCED_ENV: ADVANCED_ENV,
    SIGNED_ENV: SIGNED_ENV,
    STAIN_AVOIDANCE_ENV: STAIN_AVOIDANCE_ENV,
    isStainAvoidanceEnabled: isStainAvoidanceEnabled,
    isSignedEnabled: isSignedEnabled,
    isAdvancedEnabled: isAdvancedEnabled,
    SETTINGS: SETTINGS,
    isEnabled: isEnabled,
    isIdle: isIdle,
    decodeValue: decodeValue,
    createQuirks: createQuirks
};
