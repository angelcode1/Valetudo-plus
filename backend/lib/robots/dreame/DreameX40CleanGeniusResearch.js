"use strict";

const Quirk = require("../../core/Quirk");
const DreameMiotServices = require("./DreameMiotServices");
const DreameUtils = require("./DreameUtils");

const MIOT = DreameMiotServices.GEN2.VACUUM_2;
const SIID = MIOT.SIID;
const PIID = MIOT.PROPERTIES.MISC_TUNABLES.PIID;

// An experimental X40-specific controller, deliberately outside upstream's
// generic capabilities. No setting is modified on boot or when this is disabled.
const EXPERIMENTAL_ENV = "VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS";
const ADVANCED_ENV = "VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED";

const SETTINGS = Object.freeze([
    Object.freeze({
        id: "f7bba2a1-2d89-4f8f-a404-b3ea031eec41",
        title: "EXPERIMENTAL CleanGenius",
        description: "Unverified X40 native CleanGenius mode. Manual cleaning controls may be ignored in Routine/Deep. Change only while idle.",
        key: "SmartHost",
        values: Object.freeze({off: 0, routine: 1, deep: 2})
    }),
    Object.freeze({
        id: "c0d24419-6d57-48b0-a14b-129be1b83a3c",
        title: "EXPERIMENTAL Auto Reclean",
        description: "Native SmartAutoMop setting, if exposed by the firmware. The robot must be idle to change it.",
        key: "SmartAutoMop",
        values: Object.freeze({off: 0, deep_only: 1, all_modes: 2})
    }),
    Object.freeze({
        id: "b7079e4c-69d6-4d66-8c64-ce61fe55a853",
        title: "EXPERIMENTAL Auto Rewash",
        description: "Native SmartAutoWash setting, if exposed by the firmware. The robot must be idle to change it.",
        key: "SmartAutoWash",
        values: Object.freeze({off: 0, deep_only: 1, all_modes: 2})
    })
]);

function isEnabled(env = process.env) {
    return env[EXPERIMENTAL_ENV] === "1";
}

// Auto Reclean/Rewash controls are never offered in the initial trial.
// They require a second deliberate opt-in and remain hardware-unverified.
function isAdvancedEnabled(env = process.env) {
    return isEnabled(env) && env[ADVANCED_ENV] === "1";
}

function isIdle(robot) {
    // Fail closed until both the mode and task status have been polled.
    return robot.ephemeralState?.mode === 0 && robot.ephemeralState?.taskStatus === 0;
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
    const value = await robot.miotHelper.readProperty(SIID, PIID);

    if (typeof value !== "string") {
        throw new Error("The X40 did not return a valid AutoSwitch settings string");
    }

    return DreameUtils.DESERIALIZE_MISC_TUNABLES(value);
}

// Never infer idleness from Gen2's constructor defaults (mode=0, taskStatus=0).
// Verify both independently reported MIOT fields from a fresh device poll.
async function requireFreshIdle(robot) {
    const props = [MIOT.PROPERTIES.MODE, MIOT.PROPERTIES.TASK_STATUS].map(prop => ({
        siid: SIID, piid: prop.PIID
    }));
    const observations = await robot.miotHelper.readProperties(props);

    if (!Array.isArray(observations) || observations.length !== props.length ||
        !props.every((prop, index) => {
            const observed = observations[index];
            return observed?.siid === prop.siid &&
                observed?.piid === prop.piid &&
                observed?.code === 0 &&
                observed?.value === 0;
        })) {
        throw new Error("The X40 did not confirm idle mode and task status in a fresh MIOT read");
    }
}

function createQuirks(robot, options = {}) {
    // All three selectors share one MIOT 4:50 property; serialize UI writes.
    // This is a manual, supervised operation. It never runs at startup.
    let changeInProgress = false;

    const definitions = options.advanced === true ? SETTINGS : SETTINGS.slice(0, 1);
    return definitions.map(definition => {
        return new Quirk({
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
                if (!isIdle(robot)) {
                    throw new Error(`The X40 must be idle before changing ${definition.key}`);
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
                    if (!isIdle(robot)) {
                        throw new Error(`The X40 is no longer idle; ${definition.key} was not written`);
                    }
                    await requireFreshIdle(robot);
                    if (!isIdle(robot)) {
                        throw new Error(`The X40 is no longer idle; ${definition.key} was not written`);
                    }

                    const target = definition.values[value];
                    if (current[definition.key] === target) {
                        return;
                    }

                    // Never send a whole AutoSwitch blob or retry on error.
                    await robot.miotHelper.writeProperty(
                        SIID,
                        PIID,
                        DreameUtils.SERIALIZE_MISC_TUNABLES_SINGLE_TUNABLE({
                            [definition.key]: target
                        })
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
                    if (!isIdle(robot)) {
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
    });
}

module.exports = {
    EXPERIMENTAL_ENV: EXPERIMENTAL_ENV,
    ADVANCED_ENV: ADVANCED_ENV,
    isAdvancedEnabled: isAdvancedEnabled,
    SETTINGS: SETTINGS,
    isEnabled: isEnabled,
    isIdle: isIdle,
    decodeValue: decodeValue,
    createQuirks: createQuirks
};
