"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");
const p = require("../../../../lib/robots/dreame/DreameX40PassiveWashNotificationProbe");

test("no report means unknown, not a zero wash status", () => {
    assert.deepEqual(p.buildStatus(null).services, []);
    assert.equal(p.buildStatus(null).candidateIdentityVerified, false);
    assert.equal(p.buildStatus(null).compiledIdentityVerified, true);
    assert.equal(p.buildStatus(null).candidateSiid, 4);
    assert.equal(p.buildStatus(null).livePropertySupported, null);
    assert.equal(p.buildStatus(null).semanticMeaningVerified, false);
    assert.equal(p.buildStatus(null).observedNotificationPresence, false);
});

test("only candidate property identifiers are recorded", () => {
    const snapshot = p.observe(null, {method: "properties_changed", params: [
        {siid: 4, piid: 50, value: "DO_NOT_COPY"},
        {siid: 4, piid: 61, value: {private: "DO_NOT_COPY"}},
        {siid: 4, piid: 61, value: 12345},
        {siid: 9, piid: 61, value: -1} // unverified SIID must be ignored
    ]}, 1500);
    assert.deepEqual(p.buildStatus(snapshot, 1600).services, [
        {siid: 4, count: 2, lastObservedAt: "1970-01-01T00:00:01.500Z"}
    ]);
    assert.equal(JSON.stringify(snapshot).includes("DO_NOT_COPY"), false);
    assert.equal(JSON.stringify(p.buildStatus(snapshot)).includes("12345"), false);
});

test("does not access vendor value at all", () => {
    const e = {siid: 4, piid: 61};
    Object.defineProperty(e, "value", {get: () => {throw new Error("value accessed");}});
    const result = p.observe(null, {method:"properties_changed", params:[e]}, 100);
    assert.equal(p.buildStatus(result, 100).services[0].count, 1);
});

test("ignores unrelated methods and invalid property identifiers", () => {
    let a = p.observe(null, {method:"ignored",params:[{siid:4,piid:61}]}, 1);
    assert.equal(a, null);
    a = p.observe(a, {method:"properties_changed",params:[{siid:0,piid:61},{siid:"4",piid:61},{siid:4,piid:60}]}, 2);
    assert.equal(a, null);
});

test("bounds distinct services, counts and oversized messages", () => {
    let a = null;
    const entries=Array.from({length:15},(_,i)=>({siid:i+1,piid:61,value:"private"}));
    assert.equal(p.MAX_SERVICES, 1);
    a=p.observe(a,{method:"properties_changed",params:entries},100);
    assert.equal(a.services.length,p.MAX_SERVICES);
    assert.equal(p.observe(a,{method:"properties_changed",params:Array(129).fill(entries[0])},101),a);
    a.services[0].count=65535;
    a=p.observe(a,{method:"properties_changed",params:[entries[3]]},102);
    assert.equal(a.services[0].count,65535);
});

test("out-of-order time does not resurrect or refresh observations", () => {
    const a=p.observe(null,{method:"properties_changed",params:[{siid:4,piid:61}]},1000);
    assert.equal(p.observe(a,{method:"properties_changed",params:[{siid:4,piid:61}]},999),a);
    assert.equal(p.buildStatus(a,999).observedNotificationPresence,false);
    assert.equal(p.buildStatus(a,1000).observedNotificationPresence,true);
});

test("no robot commands, filesystem IO or timers in probe module", () => {
    const f=require("node:fs");
    const src=f.readFileSync(require.resolve("../../../../lib/robots/dreame/DreameX40PassiveWashNotificationProbe"),"utf8");
    assert.equal(/sendCommand|readProperty|writeProperty|set_properties|exec\(|spawn\(|fetch\(|http\./.test(src),false);
});
