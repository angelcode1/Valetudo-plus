"use strict";

// Research-only. R2416 static disassembly confirms compiled MIOT 4:61
// for StationAutoWashState; live accessibility and semantics are unverified.
// Do NOT read, save, log, classify, or expose vendor notification values.
const CANDIDATE_SIID = 4;
const CANDIDATE_PIID = 61;
const MAX_SERVICES = 1;
const MAX_PROPERTIES_PER_MESSAGE = 128;
const MAX_COUNT = 65535;
const MAX_TIMESTAMP = 8640000000000000;

function validTime(value) {
    return Number.isSafeInteger(value) && value >= 0 && value <= MAX_TIMESTAMP;
}

function validService(value) {
    return value === CANDIDATE_SIID;
}

function validEntry(e) {
    return e !== null && typeof e === "object" &&
        e.piid === CANDIDATE_PIID && validService(e.siid);
}

function observe(prior, message, nowMs = Date.now()) {
    if (!validTime(nowMs) || !message || message.method !== "properties_changed" ||
        !Array.isArray(message.params) || message.params.length > MAX_PROPERTIES_PER_MESSAGE) {
        return prior ?? null;
    }
    if (prior && validTime(prior.lastObservedMs) && nowMs < prior.lastObservedMs) {
        return prior;
    }

    const fresh = new Map();
    if (prior && Array.isArray(prior.services) && validTime(prior.lastObservedMs)) {
        for (const service of prior.services.slice(0, MAX_SERVICES)) {
            if (validService(service.siid) && Number.isSafeInteger(service.count) &&
                service.count >= 1 && service.count <= MAX_COUNT &&
                validTime(service.lastObservedMs) && service.lastObservedMs <= nowMs) {
                fresh.set(service.siid, {siid: service.siid, count: service.count,
                    lastObservedMs: service.lastObservedMs});
            }
        }
    }
    let changed = false;
    for (const e of message.params) {
        if (!validEntry(e)) {
            continue;
        }
        // Intentionally NEVER access e.value. The compiled SIID/PIID does not
        // establish runtime support or provide a status-value mapping.
        const previous = fresh.get(e.siid);
        if (!previous && fresh.size >= MAX_SERVICES) {
            continue;
        }
        fresh.set(e.siid, {
            siid: e.siid,
            count: Math.min((previous?.count ?? 0) + 1, MAX_COUNT),
            lastObservedMs: nowMs
        });
        changed = true;
    }
    if (!changed) {
        return prior ?? null;
    }
    return {lastObservedMs: nowMs, services: [...fresh.values()].sort((a, b) => a.siid - b.siid)};
}

function buildStatus(observation, nowMs = Date.now()) {
    const valid = observation && validTime(nowMs) && validTime(observation.lastObservedMs) &&
        nowMs >= observation.lastObservedMs && Array.isArray(observation.services);
    const services = valid ? observation.services.filter(x =>
        validService(x.siid) && Number.isSafeInteger(x.count) && x.count > 0 &&
        x.count <= MAX_COUNT && validTime(x.lastObservedMs) && x.lastObservedMs <= nowMs
    ).slice(0, MAX_SERVICES).map(x => ({
        siid: x.siid,
        count: x.count,
        lastObservedAt: new Date(x.lastObservedMs).toISOString()
    })) : [];
    return {
        source: "passive_miot_properties_changed",
        candidateSiid: CANDIDATE_SIID,
        candidatePiid: CANDIDATE_PIID,
        compiledIdentityVerified: true,
        livePropertySupported: null,
        candidateIdentityVerified: false,
        semanticMeaningVerified: false,
        observedNotificationPresence: services.length > 0,
        services: services,
        readOnly: true,
        valuesCollected: false,
        notDirtinessOrRewashEvidence: true
    };
}

module.exports = {CANDIDATE_SIID, CANDIDATE_PIID, MAX_SERVICES, observe, buildStatus};
