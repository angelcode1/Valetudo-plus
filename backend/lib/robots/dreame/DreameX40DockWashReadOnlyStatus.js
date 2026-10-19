"use strict";

/**
 * Observes the already-polled native MIOT MOP_DOCK_STATUS property.
 * These are dock *activity* codes, not dirtiness, turbidity or rewash reasons.
 * No requests, writes, subscriptions or filesystem persistence.
 */
const MAX_TRANSITIONS = 12;
const STALE_AFTER_MS = 120000;

// Matches the existing DreameValetudoRobot.MOP_DOCK_STATUS_MAP.
// A cleaning value does NOT imply that CleanGenius requested the wash.
const STATES = Object.freeze({
    0: "idle",
    1: "cleaning",
    2: "drying",
    3: "cleaning_unverified_variant",
    4: "paused",
    5: "cleaning",
    6: "cleaning"
});

function decode(raw) {
    if (!Number.isSafeInteger(raw)) {
        return {raw: null, state: "unknown"};
    }
    const state = Object.prototype.hasOwnProperty.call(STATES, raw) ?
        STATES[raw] : "unknown";
    return {raw: raw, state: state};
}

/**
 * Pure immutable transition accumulator. Duplicate values refresh the
 * observation timestamp but do not create fake activity transitions.
 * @param {*} previous Prior observation, or null
 * @param {number} raw Native mop-dock status code
 * @param {number} [observedAtMs] Local timestamp in milliseconds
 */
function observe(previous, raw, observedAtMs = Date.now()) {
    if (!Number.isSafeInteger(raw) || !Number.isSafeInteger(observedAtMs) ||
        observedAtMs < 0 || observedAtMs > 8640000000000000) {
        throw new Error("Invalid MIOT mop-dock observation");
    }
    if (previous && observedAtMs < previous.observedAtMs) {
        throw new Error("Out-of-order MIOT mop-dock observation");
    }
    const value = decode(raw);
    const transitions = Array.isArray(previous?.transitions) ?
        previous.transitions.slice() : [];

    if (!previous || previous.value.raw !== value.raw) {
        transitions.push({
            ...value,
            atMs: observedAtMs
        });
    }

    return {
        value: value,
        observedAtMs: observedAtMs,
        transitions: transitions.slice(-MAX_TRANSITIONS)
    };
}

function buildStatus(observation, nowMs = Date.now()) {
    // System-clock regressions invalidate freshness; they are not age zero.
    const validTime = observation && Number.isSafeInteger(observation.observedAtMs) &&
        observation.observedAtMs >= 0 && observation.observedAtMs <= 8640000000000000 &&
        Number.isSafeInteger(nowMs) && nowMs >= observation.observedAtMs;
    const ageMs = validTime ? nowMs - observation.observedAtMs : null;
    const stale = ageMs === null || ageMs > STALE_AFTER_MS;

    return {
        source: "miot_mop_dock_status",
        dataType: "dock_activity_not_dirtiness_or_rewash_reason",
        state: ageMs === null ? "unavailable" : (stale ? "stale" : "observed"),
        observedAt: ageMs === null ? null : new Date(observation.observedAtMs).toISOString(),
        ageMs: ageMs,
        stale: stale,
        current: ageMs === null ? {raw: null, state: "unavailable"} :
            (observation?.value ?? {raw: null, state: "unavailable"}),
        // Bounded to 12 entries since this Valetudo process started.
        // A transition is only a changed native status code, not a proven cycle.
        transitions: (ageMs === null ? [] : (observation?.transitions ?? [])).map(e => ({
            raw: e.raw,
            state: e.state,
            at: new Date(e.atMs).toISOString()
        }))
    };
}

module.exports = {
    decode: decode,
    observe: observe,
    buildStatus: buildStatus,
    MAX_TRANSITIONS: MAX_TRANSITIONS,
    STALE_AFTER_MS: STALE_AFTER_MS
};
