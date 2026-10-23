"use strict";

// Default Gen2 protection is unchanged. X40-only observation mode is opt-in.
const OBSERVE_ONLY_ENV = "VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY";

function isObserveOnlyEnabled(env = process.env) {
    return env[OBSERVE_ONLY_ENV] === "1";
}

function shouldAutoDisableSmartHost(smartHostValue, robot) {
    return smartHostValue > 0 &&
        robot?.allowExperimentalCleanGenius !== true &&
        robot?.allowCleanGeniusObserveOnly !== true;
}

module.exports = {
    OBSERVE_ONLY_ENV,
    isObserveOnlyEnabled,
    shouldAutoDisableSmartHost
};
