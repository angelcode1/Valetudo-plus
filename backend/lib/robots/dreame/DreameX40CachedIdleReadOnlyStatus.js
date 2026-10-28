"use strict";

// Read-only snapshot of the existing Gen2 MODE (4:1) and TASK_STATUS (4:7)
// poll. Never makes a new device request. Do not confuse a cached reading
// with the mandatory fresh read in the experimental SmartHost setter.
const DreameMiotServices = require("./DreameMiotServices");

const MIOT = DreameMiotServices.GEN2.VACUUM_2;
const SIID = MIOT.SIID;
const MODE_PIID = MIOT.PROPERTIES.MODE.PIID;
const TASK_PIID = MIOT.PROPERTIES.TASK_STATUS.PIID;
const STALE_AFTER_MS = 120000;

function observe(items, observedAtMs = Date.now()) {
    if (!Array.isArray(items)) {
        return null;
    }
    const relevant = items.filter(item => {
        return item?.siid === SIID && [MODE_PIID, TASK_PIID].includes(item?.piid);
    });
    if (relevant.length === 0) {
        // This was a different update; don't erase the last full pair.
        return undefined;
    }
    const mode = relevant.filter(item => item.piid === MODE_PIID);
    const task = relevant.filter(item => item.piid === TASK_PIID);
    if (mode.length !== 1 || task.length !== 1 ||
        mode[0].code !== 0 || task[0].code !== 0 ||
        !Number.isSafeInteger(mode[0].value) ||
        !Number.isSafeInteger(task[0].value) ||
        !Number.isSafeInteger(observedAtMs) || observedAtMs < 0) {
        // Partial/error/invalid paired reads must never look safely idle.
        return null;
    }
    return {
        mode: mode[0].value,
        taskStatus: task[0].value,
        observedAtMs: observedAtMs
    };
}

function buildStatus(observation, nowMs = Date.now()) {
    const valid = observation &&
        Number.isSafeInteger(observation.mode) &&
        Number.isSafeInteger(observation.taskStatus) &&
        Number.isSafeInteger(observation.observedAtMs) &&
        Number.isSafeInteger(nowMs) &&
        nowMs >= observation.observedAtMs && observation.observedAtMs >= 0;
    const ageMs = valid ? nowMs - observation.observedAtMs : null;
    const state = ageMs === null ? "unavailable" :
        (ageMs > STALE_AFTER_MS ? "stale" : "observed");
    const current = state === "observed";
    return {
        source: "cached_miot_4_1_4_7",
        state: state,
        observedAt: valid ? new Date(observation.observedAtMs).toISOString() : null,
        ageMs: ageMs,
        mode: current ? observation.mode : null,
        taskStatus: current ? observation.taskStatus : null,
        cachedGuardMatch: current &&
            observation.mode === 0 && observation.taskStatus === 0
    };
}

module.exports = {
    observe: observe,
    buildStatus: buildStatus,
    STALE_AFTER_MS: STALE_AFTER_MS
};
