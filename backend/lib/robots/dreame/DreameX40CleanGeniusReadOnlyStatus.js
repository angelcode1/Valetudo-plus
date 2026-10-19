"use strict";

/**
 * Read-only, allowlisted interpretation of X40 MIOT 4:50 settings.
 *
 * These values are configuration observations, NOT native stain events,
 * measured turbidity, or evidence that an automatic cleaning action ran.
 * No native AVA messages are sent or subscribed to.
 */
const DEFINITIONS = Object.freeze({
    SmartHost: Object.freeze({name: "cleanGenius", known: Object.freeze({0: "off", 1: "mode_1_unverified", 2: "mode_2_unverified"})}),
    SmartAutoMop: Object.freeze({name: "autoReclean", known: Object.freeze({0: "off", 1: "mode_1_unverified", 2: "mode_2_unverified"})}),
    SmartAutoWash: Object.freeze({name: "autoRewash", known: Object.freeze({0: "off", 1: "mode_1_unverified", 2: "mode_2_unverified"})}),
    StainIdentify: Object.freeze({name: "stainIdentification", known: Object.freeze({0: "off", 1: "on_setting"})}),
    HotWash: Object.freeze({name: "hotWash", known: Object.freeze({0: "off", 1: "on_setting"})})
});
const MAX_PAYLOAD_LENGTH = 32768;
const MAX_ENTRIES = 128;
const STALE_AFTER_MS = 120000;

function unavailableFields() {
    return Object.fromEntries(Object.values(DEFINITIONS).map(def => [
        def.name, {value: null, state: "unavailable"}
    ]));
}

function parseSettings(value) {
    if (typeof value !== "string" || value.length > MAX_PAYLOAD_LENGTH) {
        throw new Error("Invalid MIOT 4:50 payload length or type");
    }

    let entries;
    try {
        entries = JSON.parse(value);
    } catch {
        throw new Error("Invalid MIOT 4:50 JSON");
    }
    if (!Array.isArray(entries) || entries.length > MAX_ENTRIES) {
        throw new Error("Invalid MIOT 4:50 settings collection");
    }

    const found = Object.create(null);
    for (const entry of entries) {
        if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
            continue;
        }
        if (typeof entry.k !== "string" || !Object.prototype.hasOwnProperty.call(DEFINITIONS, entry.k)) {
            continue;
        }
        if (Object.prototype.hasOwnProperty.call(found, entry.k)) {
            throw new Error("Duplicate MIOT 4:50 setting");
        }
        // Unknown types and sentinel values must not be coerced to false/off.
        found[entry.k] = Number.isSafeInteger(entry.v) ? entry.v : null;
    }

    const fields = unavailableFields();
    Object.keys(found).forEach(key => {
        const value = found[key];
        const definition = DEFINITIONS[key];
        const state = value === null ? "unknown" :
            (Object.prototype.hasOwnProperty.call(definition.known, value) ?
                definition.known[value] : "unknown");
        fields[definition.name] = {value, state};
    });
    return fields;
}

function observe(value, observedAtMs = Date.now()) {
    return {
        observedAtMs,
        fields: parseSettings(value)
    };
}

function buildStatus(observation, options = {}) {
    const nowMs = options.nowMs ?? Date.now();
    const ageMs = observation && Number.isFinite(observation.observedAtMs) ?
        Math.max(0, nowMs - observation.observedAtMs) : null;
    const stale = ageMs === null || ageMs > STALE_AFTER_MS;

    return {
        source: "miot_4_50",
        readOnly: true,
        dataType: "native_settings_not_sensor_measurements",
        state: ageMs === null ? "unavailable" : (stale ? "stale" : "observed"),
        observedAt: ageMs === null ? null : new Date(observation.observedAtMs).toISOString(),
        ageMs,
        stale,
        valetudoPolicy: options.experimentalEnabled === true ?
            "experimental_controls_opted_in" : "auto_disable_smart_host_when_positive",
        // The native controller may have been commanded off after this poll;
        // these are observed settings, not a verified effective cleaning mode.
        settings: observation?.fields ?? unavailableFields(),
        nativeMopDirtiness: "unavailable_no_verified_local_status_interface"
    };
}

module.exports = {
    observe,
    buildStatus,
    parseSettings,
    STALE_AFTER_MS
};
