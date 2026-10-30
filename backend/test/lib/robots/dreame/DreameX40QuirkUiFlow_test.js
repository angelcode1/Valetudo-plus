"use strict";

const assert = require("node:assert/strict");
const express = require("express");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const vm = require("node:vm");
const {MutationObserver, QueryClient, QueryObserver} = require("@tanstack/query-core");
const {once} = require("node:events");

const QuirksCapability = require("../../../../lib/core/capabilities/QuirksCapability");
const QuirksRouter = require("../../../../lib/webserver/capabilityRouters/QuirksCapabilityRouter");
const Research = require("../../../../lib/robots/dreame/DreameX40CleanGeniusResearch");

function deferred() {
    let resolve;
    const promise = new Promise(done => {
        resolve = done;
    });
    return {promise: promise, resolve: resolve};
}

// Execute the production hook body, not a copy of its mutation callbacks.
// React bindings are replaced with real Query Core observers so this contract
// test needs no DOM. The real capability/router/controller serve loopback HTTP;
// only native MIOT and the hook's transport/error-notification bindings are fake.
function useProductionMutation(bindings) {
    const filename = path.resolve(__dirname, "../../../../../frontend/src/api/hooks.ts");
    const source = ts.createSourceFile(filename, fs.readFileSync(filename, "utf8"), ts.ScriptTarget.Latest, true);
    const declaration = source.statements.filter(ts.isVariableStatement)
        .flatMap(statement => [...statement.declarationList.declarations])
        .find(item => item.name.getText(source) === "useSetQuirkValueMutation");
    assert(declaration?.initializer, "production mutation hook must exist");
    const code = ts.transpileModule(`module.exports = ${declaration.initializer.getText(source)};`, {
        compilerOptions: {target: ts.ScriptTarget.ES2021, module: ts.ModuleKind.CommonJS}
    }).outputText;
    const module = {exports: null};
    vm.runInNewContext(code, {module: module, ...bindings});
    return module.exports();
}

async function fixture(options) {
    const writes = [];
    const requests = [];
    const errors = [];
    const refreshStarted = deferred();
    const releaseRefresh = deferred();
    const key = options.stainAvoidance ? "StainIdentify" : "SmartHost";
    let current = options.stainAvoidance ? 1 : 0;
    let readbackFailed = false;
    const robot = {
        ephemeralState: {mode: options.blocked ? 14 : 6, taskStatus: 0},
        miotHelper: {
            readProperties: async props => props.map(p => ({...p, code: 0,
                value: ({"4:1": 6, "4:7": 0, "3:2": 1, "4:18": "", "4:25": 0})[`${p.siid}:${p.piid}`]})),
            readProperty: async (siid, piid) => {
                if (siid === 4 && piid === 22 && options.stainAvoidance) {
                    if (options.aiReadFails) {
                        throw new Error("PRIVATE_AI_TRANSPORT_FIXTURE");
                    }
                    return options.aiBlocked ? 2 : 10;
                }
                assert.deepEqual([siid, piid], [4, 50]);
                if (writes.length && options.readbackFailure && !readbackFailed) {
                    readbackFailed = true;
                    throw new Error("Simulated post-write readback unavailable");
                }
                if (readbackFailed && options.nativeRefreshFailure) {
                    throw new Error("Simulated native settings unavailable");
                }
                return JSON.stringify([{k: key, v: current}]);
            },
            writeProperty: async (siid, piid, value) => {
                writes.push([siid, piid, value]);
                current = JSON.parse(value).v;
            }
        }
    };
    const quirks = Research.createQuirks(robot, {stainAvoidance: options.stainAvoidance === true});
    const capability = new QuirksCapability({robot: robot, quirks: quirks});
    const router = new QuirksRouter({capability: capability, validator: (req, res, next) => next()});
    const app = express();
    app.use(express.json());
    const route = "/api/v2/robot/capabilities/QuirksCapability";
    app.use(route, async (req, res, next) => {
        requests.push(req.method);
        if (req.method === "GET" && requests.filter(method => method === "GET").length > 1) {
            refreshStarted.resolve();
            await releaseRefresh.promise;
            if (options.httpRefreshFailure) {
                res.status(503).json("Simulated refresh unavailable");
                return;
            }
        }
        next();
    }, router.getRouter());
    const server = app.listen(0, "127.0.0.1");
    await once(server, "listening");
    const url = `http://127.0.0.1:${server.address().port}${route}`;
    const fetchQuirks = async () => {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error("Quirks refresh failed");
        }
        return response.json();
    };
    const client = new QueryClient({defaultOptions: {queries: {retry: false, staleTime: Infinity}, mutations: {retry: false}}});
    const queryKey = ["quirks"];
    await client.fetchQuery({queryKey: queryKey, queryFn: fetchQuirks});
    const query = new QueryObserver(client, {queryKey: queryKey, queryFn: fetchQuirks});
    const unsubscribe = query.subscribe(() => {});
    const mutation = useProductionMutation({
        useQuirksQuery: () => ({refetch: query.refetch.bind(query)}),
        useMutation: config => new MutationObserver(client, config),
        useOnCommandError: () => error => errors.push(error),
        Capability: {Quirks: "QuirksCapability"},
        sendSetQuirkValueCommand: async command => {
            const response = await fetch(url, {method: "PUT", headers: {"content-type": "application/json"},
                body: JSON.stringify(command)});
            if (!response.ok) {
                throw new Error(await response.json());
            }
        }
    });
    return {
        id: quirks[options.stainAvoidance ? 1 : 0].id,
        mutation: mutation,
        query: query,
        errors: errors,
        writes: writes,
        requests: requests,
        refreshStarted: refreshStarted,
        releaseRefresh: releaseRefresh,
        close: async () => {
            releaseRefresh.resolve();
            unsubscribe();
            query.destroy();
            client.clear();
            server.closeAllConnections();
            await new Promise(resolve => server.close(resolve));
        }
    };
}

for (const scenario of [
    {aiBlocked: true, reason: "ai_fluid_detection_disabled"},
    {aiReadFails: true, reason: "ai_settings_unavailable"}
]) {
    test(`X40 stain UI/API rejects bypassing the disabled selector: ${scenario.reason}`, {timeout: 5000}, async () => {
        const state = await fixture({stainAvoidance: true, ...scenario});
        const visible = () => state.query.getCurrentResult().data.find(item => item.id === state.id);
        try {
            assert.equal(visible().readOnly, true);
            assert.equal(visible().unavailableReason, scenario.reason);
            const completed = state.mutation.mutate({id: state.id, value: "enabled"}).then(
                () => ({ok: true, error: null}), error => ({ok: false, error: error})
            );
            await Promise.race([
                state.refreshStarted.promise,
                completed.then(() => assert.fail("The command settled before requesting a settings refresh"))
            ]);
            assert.equal(state.mutation.getCurrentResult().isPending, true);
            state.releaseRefresh.resolve();
            const outcome = await completed;
            assert.equal(outcome.ok, false);
            assert.equal(outcome.error.message.includes(scenario.reason), true);
            assert.equal(outcome.error.message.includes("PRIVATE_AI"), false);
            assert.equal(visible().readOnly, true);
            assert.equal(visible().unavailableReason, scenario.reason);
            assert.deepEqual(state.writes, []);
            assert.deepEqual(state.requests, ["GET", "PUT", "GET"]);
        } finally {
            await state.close();
        }
    });
}

for (const scenario of [
    {name: "applied write with failed readback refreshes the displayed native value without another write", readbackFailure: true},
    {name: "unavailable native refresh replaces an old value with a disabled control", readbackFailure: true, nativeRefreshFailure: true},
    {name: "failed HTTP refresh sets the query error flag instead of confirming cached settings", readbackFailure: true, httpRefreshFailure: true},
    {name: "blocked activation refreshes Off without sending any native write", blocked: true},
    {name: "successful change remains pending until its displayed settings refresh finishes"}
].flatMap(scenario => [scenario, {...scenario, stainAvoidance: true}])) {
    test(`X40 ${scenario.stainAvoidance ? "stain" : "mode"} UI/API flow: ${scenario.name}`, {timeout: 5000}, async () => {
        const state = await fixture(scenario);
        const before = scenario.stainAvoidance ? "disabled" : "off";
        const after = scenario.stainAvoidance ? "enabled" : "routine";
        const rawBefore = scenario.stainAvoidance ? 1 : 0;
        const rawAfter = scenario.stainAvoidance ? 2 : 1;
        const visibleSetting = result => result.data.find(item => item.id === state.id);
        try {
            assert.equal(visibleSetting(state.query.getCurrentResult()).value, before);
            const completed = state.mutation.mutate({id: state.id, value: after}).then(
                () => ({ok: true}), error => ({ok: false, error: error})
            );
            await Promise.race([
                state.refreshStarted.promise,
                completed.then(() => assert.fail("The command settled before requesting a settings refresh"))
            ]);
            assert.equal(state.mutation.getCurrentResult().isPending, true);
            assert.equal(visibleSetting(state.query.getCurrentResult()).value, before);
            state.releaseRefresh.resolve();
            const outcome = await completed;
            const expectedError = !!(scenario.readbackFailure || scenario.blocked);
            assert.equal(outcome.ok, !expectedError);
            assert.equal(state.errors.length, expectedError ? 1 : 0);
            assert.equal(state.mutation.getCurrentResult().status, expectedError ? "error" : "success");
            assert.deepEqual(state.requests, ["GET", "PUT", "GET"]);
            assert.deepEqual(state.writes, scenario.blocked ? [] : [[4, 50, JSON.stringify({
                k: scenario.stainAvoidance ? "StainIdentify" : "SmartHost", v: rawAfter
            })]]);

            const refreshed = state.query.getCurrentResult();
            if (scenario.httpRefreshFailure) {
                // Quirks.tsx uses isError to hide the list even if Query Core
                // retains old data after a refetch failure.
                assert.equal(refreshed.isError, true);
                assert.equal(refreshed.isRefetchError, true);
            } else {
                assert.equal(refreshed.isError, false);
                const visible = visibleSetting(refreshed);
                assert.equal(visible.value, scenario.nativeRefreshFailure ? "unavailable" : scenario.blocked ? before : after);
                assert.equal(visible.readOnly, !!scenario.nativeRefreshFailure);
                assert.equal(visible.rawValue, scenario.nativeRefreshFailure ? null : scenario.blocked ? rawBefore : rawAfter);
            }
        } finally {
            await state.close();
        }
    });
}
