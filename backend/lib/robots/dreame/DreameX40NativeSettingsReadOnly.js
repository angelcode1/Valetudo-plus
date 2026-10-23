"use strict";

const DreameMiotServices = require("./DreameMiotServices");
const CleanGeniusReadOnlyStatus = require("./DreameX40CleanGeniusReadOnlyStatus");

const MIOT = DreameMiotServices.GEN2.VACUUM_2;

/**
 * Fresh, on-demand read of one MIOT property. Unlike pollState(), this does
 * NOT enter Gen2.parseAndUpdateState(), whose legacy path can write SmartHost:0.
 * Background state polling is independent and retains its normal policy.
 *
 * Never return the raw settings blob or unrecognized keys.
 * Do not call writeProperty(), set_properties or action here.
 */
async function readFreshNativeSettings(robot) {
    const raw = await robot.miotHelper.readProperty(
        MIOT.SIID,
        MIOT.PROPERTIES.MISC_TUNABLES.PIID
    );
    if (typeof raw !== "string") {
        throw new Error("X40 native settings response is not a string");
    }

    const observedAtMs = Date.now();
    const observation = CleanGeniusReadOnlyStatus.observe(raw, observedAtMs);
    const status = CleanGeniusReadOnlyStatus.buildStatus(observation, {
        nowMs: observedAtMs,
        experimentalEnabled: robot.allowExperimentalCleanGenius === true,
        observeOnlyEnabled: robot.allowCleanGeniusObserveOnly === true
    });

    return {
        ...status,
        readMode: "on_demand_direct_miot_get_properties",
        nativeEffectiveOperation: "unverified"
    };
}

module.exports = {
    readFreshNativeSettings
};
