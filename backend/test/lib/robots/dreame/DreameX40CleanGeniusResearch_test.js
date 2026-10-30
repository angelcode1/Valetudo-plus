"use strict";

const assert = require("node:assert/strict");
const research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");
const test = require("node:test");

test("experimental feature is opt-in", () => {
    assert.equal(research.isEnabled({}), false);
    assert.equal(research.isEnabled({VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "0"}), false);
    assert.equal(research.isEnabled({VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1"}), true);
});

test("first-trial UI exposes only the native CleanGenius mode", () => {
    const robot = {ephemeralState: {mode: 0, taskStatus: 0}};
    const quirks = research.createQuirks(robot);
    assert.equal(quirks.length, 1);
    assert.equal(quirks[0].id, research.SETTINGS[0].id);
    assert.deepEqual(quirks[0].options, ["off", "routine", "deep"]);
});

test("Auto Reclean and Auto Rewash need a separate advanced opt-in", () => {
    assert.equal(research.isAdvancedEnabled({}), false);
    assert.equal(research.isAdvancedEnabled({
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED: "1"
    }), false);
    assert.equal(research.isAdvancedEnabled({
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1"
    }), false);
    assert.equal(research.isAdvancedEnabled({
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "1",
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED: "1"
    }), true);
    assert.equal(research.createQuirks({}, {advanced: true}).length, 3);
});

test("rejects an unrecognized mode", () => {
    const definition = research.SETTINGS[0];
    assert.equal(research.decodeValue(1, definition), "routine");
    assert.throws(() => research.decodeValue(200, definition), /Unsupported/);
});

test("fails closed when task or mode is unknown/active", () => {
    assert.equal(research.isIdle({}), false);
    assert.equal(research.isIdle({ephemeralState: {mode: 0}}), false);
    assert.equal(research.isIdle({ephemeralState: {mode: 0, taskStatus: 0}}), true);
    assert.equal(research.isIdle({ephemeralState: {mode: 1, taskStatus: 0}}), false);
    assert.equal(research.isIdle({ephemeralState: {mode: 0, taskStatus: 1}}), false);
});


test("powersave cached mode remains blocked with bounded diagnostic, no MIOT calls", async () => {
    let calls = 0;
    const robot = {
        ephemeralState: {mode: 14, taskStatus: 0},
        miotHelper: {
            readProperty: async () => {
                calls++;
            },
            readProperties: async () => {
                calls++;
            },
            writeProperty: async () => {
                calls++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("routine"),
        /cached mode=14, taskStatus=0; no write attempted/
    );
    assert.equal(calls, 0);
});

test("string-typed cached status is reported but not accepted or written", async () => {
    let calls = 0;
    const robot = {
        ephemeralState: {mode: "0", taskStatus: "0"},
        miotHelper: {
            readProperty: async () => {
                calls++;
            },
            readProperties: async () => {
                calls++;
            },
            writeProperty: async () => {
                calls++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("routine"),
        /cached mode=0 \(string\), taskStatus=0 \(string\); no write attempted/
    );
    assert.equal(calls, 0);
});

test("quirk rejects active cleaning without writing", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 1, taskStatus: 1},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
            writeProperty: async () => {
                writes++;
            }
        }
    };
    const [quirk] = research.createQuirks(robot);
    await assert.rejects(() => quirk.setter("routine"), /idle/);
    assert.equal(writes, 0);
});

test("quirk writes one key only, verifies readback, and remains manual", async () => {
    const writes = [];
    let smartHost = 0;
    let reads = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => {
                reads++;
                return JSON.stringify([{k: "SmartHost", v: smartHost}]);
            },
            writeProperty: async (...args) => {
                writes.push(args);
                smartHost = JSON.parse(args[2]).v;
            }
        }
    };
    const [quirk] = research.createQuirks(robot);
    await quirk.setter("routine");
    assert.equal(reads, 2);
    assert.equal(smartHost, 1);
    assert.deepEqual(writes, [[4, 50, '{"k":"SmartHost","v":1}']]);

    await quirk.setter("routine");
    assert.equal(writes.length, 1, "already applied: no additional write");
});

test("MIOT accepted write without matching readback is an error; no retry", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
            writeProperty: async () => {
                writes++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("routine"),
        /readback mismatch/
    );
    assert.equal(writes, 1);
});

test("readback transport failure is surfaced without writing twice", async () => {
    let reads = 0;
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => {
                reads++;
                if (reads === 2) {
                    throw new Error("readback unavailable");
                }
                return JSON.stringify([{k: "SmartHost", v: 0}]);
            },
            writeProperty: async () => {
                writes++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("routine"),
        /readback unavailable/
    );
    assert.equal(writes, 1);
});

test("state changing during initial read blocks a write", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => {
                robot.ephemeralState.taskStatus = 1;
                return JSON.stringify([{k: "SmartHost", v: 0}]);
            },
            writeProperty: async () => {
                writes++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("deep"),
        /no longer idle/
    );
    assert.equal(writes, 0);
});

test("concurrent selector writes are blocked across all three X40 quirks", async () => {
    let releaseRead;
    const gate = new Promise(resolve => {
        releaseRead = resolve;
    });
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => {
                await gate;
                return JSON.stringify([
                    {k: "SmartHost", v: 0},
                    {k: "SmartAutoWash", v: 0}
                ]);
            },
            writeProperty: async () => {
                writes++;
            }
        }
    };
    const quirks = research.createQuirks(robot, {advanced: true, signedProtocol: true});
    const first = quirks[0].setter("routine");
    await assert.rejects(
        () => quirks[2].setter("all_modes"),
        /in progress/
    );
    releaseRead();
    await assert.rejects(first, /readback mismatch/);
    assert.equal(writes, 1);
});

test("absent setting cannot cause a write", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            readProperty: async () => JSON.stringify([{k: "CleanRoute", v: 1}]),
            writeProperty: async () => {
                writes++;
            }
        }
    };
    const [quirk] = research.createQuirks(robot);
    await assert.rejects(() => quirk.setter("routine"), /Unsupported/);
    assert.equal(writes, 0);
});

test("R2416 observed 4:50 sentinel values do not cause an accidental write", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperties: async properties => properties.map(p => ({...p, code: 0, value: p.siid === 3 ? 1 : 0})),
            // Sanitized read-only X40 observation from firmware 4.3.9_1782.
            readProperty: async () => JSON.stringify([
                {k: "SmartHost", v: 0},
                {k: "SmartAutoMop", v: -1},
                {k: "SmartAutoWash", v: 0},
                {k: "StainIdentify", v: 1},
                {k: "MeticulousTwist", v: -7}
            ]),
            writeProperty: async () => {
                writes++;
            }
        }
    };

    const [cleanGenius, autoReclean, autoRewash] = research.createQuirks(robot, {advanced: true, signedProtocol: true});
    assert.equal(await cleanGenius.getter(), "off");
    assert.equal(await autoRewash.getter(), "off");

    // -1 is not an established reclean mode. The control must fail closed.
    await assert.rejects(() => autoReclean.getter(), /Unsupported SmartAutoMop value: -1/);
    await assert.rejects(() => autoReclean.setter("all_modes"), /Unsupported SmartAutoMop value: -1/);
    assert.equal(writes, 0);
});

test("fresh status validation prevents writes from constructor's unobserved idle defaults", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
            readProperties: async properties => properties.map(p => ({
                ...p, code: 0, value: p.piid === 7 ? 1 : 0
            })),
            writeProperty: async () => {
                writes++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("routine"),
        /fresh MIOT read/
    );
    assert.equal(writes, 0);
});

test("unavailable fresh status aborts without modifying the robot", async () => {
    let writes = 0;
    const robot = {
        ephemeralState: {mode: 0, taskStatus: 0},
        miotHelper: {
            readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
            readProperties: async () => {
                throw new Error("get_properties unavailable");
            },
            writeProperty: async () => {
                writes++;
            }
        }
    };
    await assert.rejects(
        () => research.createQuirks(robot)[0].setter("routine"),
        /get_properties unavailable/
    );
    assert.equal(writes, 0);
});

test("malformed or mismatched fresh status response cannot enable SmartHost", async () => {
    const cases = [
        [{siid: 4, piid: 1, code: 0, value: 0}, {siid: 4, piid: 7, code: -1, value: 0}],
        [{siid: 4, piid: 1, code: 0, value: 0}, {siid: 4, piid: 7, code: 0, value: null}],
        [{siid: 4, piid: 7, code: 0, value: 0}, {siid: 4, piid: 1, code: 0, value: 0}],
        [{siid: 4, piid: 1, code: 0, value: 0}]
    ];
    for (const observations of cases) {
        let writes = 0;
        const robot = {
            ephemeralState: {mode: 0, taskStatus: 0},
            miotHelper: {
                readProperty: async () => JSON.stringify([{k: "SmartHost", v: 0}]),
                readProperties: async () => observations,
                writeProperty: async () => {
                    writes++;
                }
            }
        };
        await assert.rejects(
            () => research.createQuirks(robot)[0].setter("routine"),
            /fresh MIOT read/
        );
        assert.equal(writes, 0);
    }
});

