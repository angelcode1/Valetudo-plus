const express = require("express");


const ValetudoRobot = require("../core/ValetudoRobot");

const CapabilitiesRouter = require("./CapabilitiesRouter");
const {SSEHub, SSEMiddleware} = require("./middlewares/sse");

class RobotRouter {
    /**
     *
     * @param {object} options
     * @param {import("../core/ValetudoRobot")} options.robot
     * @param {*} options.validator
     */
    constructor(options) {
        this.robot = options.robot;
        this.router = express.Router({mergeParams: true});

        this.validator = options.validator;

        this.initRoutes();
        this.initSSE();
    }


    initRoutes() {
        this.router.get("/", (req, res) => {
            res.json({
                manufacturer: this.robot.getManufacturer(),
                modelName: this.robot.getModelName(),
                modelDetails: this.robot.getModelDetails(),
                implementation: this.robot.constructor.name
            });
        });

        this.router.get("/properties", (req, res) => {
            res.json(this.robot.getProperties());
        });

        // X40-specific, strictly read-only status. Other robots have no such
        // method and therefore do not expose a vendor-specific API here.
        // Uses the existing periodic MIOT 4:50 poll cache, with no robot I/O.
        this.router.get("/clean-genius/status", (req, res) => {
            // Only the X40 implements this optional, read-only vendor endpoint.
            /** @type {ValetudoRobot & {getCleanGeniusReadOnlyStatus?: () => object}} */
            const statusRobot = this.robot;
            if (typeof statusRobot.getCleanGeniusReadOnlyStatus !== "function") {
                return res.sendStatus(404);
            }

            res.set("Cache-Control", "no-store");
            res.json(statusRobot.getCleanGeniusReadOnlyStatus());
        });

        // X40-only, fresh MIOT 4:50 read. Bypasses the state parser and its
        // SmartHost auto-disable write. No raw firmware data is returned.
        this.router.get("/clean-genius/native-settings", async (req, res) => {
            /** @type {ValetudoRobot & {getCleanGeniusNativeSettingsFreshReadOnly?: () => Promise<object>}} */
            const nativeRobot = this.robot;
            if (typeof nativeRobot.getCleanGeniusNativeSettingsFreshReadOnly !== "function") {
                return res.sendStatus(404);
            }

            res.set("Cache-Control", "no-store");
            try {
                res.json(await nativeRobot.getCleanGeniusNativeSettingsFreshReadOnly());
            } catch {
                // Do not leak private MIOT payloads or firmware error details.
                res.status(502).json({error: "X40 native settings read failed"});
            }
        });

        // X40-only native 4:50/4:1/4:7/3:2 preflight. Always read-only.
        this.router.get("/clean-genius/smart-host-test/preflight", async (req, res) => {
            /** @type {ValetudoRobot & {getCleanGeniusSmartHostPreflightReadOnly?: () => Promise<object>}} */
            const x40 = this.robot;
            if (typeof x40.getCleanGeniusSmartHostPreflightReadOnly !== "function") {
                return res.sendStatus(404);
            }
            res.set("Cache-Control", "no-store");
            try {
                res.json(await x40.getCleanGeniusSmartHostPreflightReadOnly());
            } catch {
                res.status(502).json({error: "Native X40 preflight read failed"});
            }
        });

        // Requires a separate, explicit opt-in env flag and strict body/header
        // confirmation. Never enabled merely by observe-only mode.
        this.router.post("/clean-genius/smart-host-test", async (req, res) => {
            /** @type {ValetudoRobot & {setCleanGeniusSmartHostOneKey?: (target: number) => Promise<object>}} */
            const x40 = this.robot;
            if (typeof x40.setCleanGeniusSmartHostOneKey !== "function") {
                return res.sendStatus(404);
            }
            res.set("Cache-Control", "no-store");
            const body = req.body;
            if (req.get("X-X40-Native-Test") !== "one-key-only" ||
                !req.is("application/json") || !body || Array.isArray(body) ||
                typeof body !== "object" ||
                Object.keys(body).sort().join(",") !== "confirm,target" ||
                (body.target !== 0 && body.target !== 1) ||
                body.confirm !== (body.target === 1 ?
                    "I_ACCEPT_UNVERIFIED_X40_SMARTHOST_1" :
                    "RESTORE_X40_SMARTHOST_0")) {
                return res.status(400).json({error: "Explicit single-key X40 confirmation required"});
            }
            try {
                res.json(await x40.setCleanGeniusSmartHostOneKey(body.target));
            } catch (err) {
                const httpStatus = [400, 403, 409, 502].includes(err.statusCode) ?
                    err.statusCode : 502;
                // Firmware errors and raw MIOT payloads must never be echoed.
                res.status(httpStatus).json({error: "X40 single-key SmartHost test refused or failed"});
            }
        });

        this.router.get("/state", async (req, res) => {
            try {
                const polledState = await this.robot.pollState();

                res.json(polledState);
            } catch (err) {
                res.status(500).send(err.toString());
            }
        });

        this.router.get("/state/attributes", async (req, res) => {
            try {
                const polledState = await this.robot.pollState();

                res.json(polledState.attributes);
            } catch (err) {
                res.status(500).send(err.toString());
            }
        });

        this.router.get("/state/map", async (req, res) => {
            try {
                res.json(this.robot.state.map);
            } catch (err) {
                res.status(500).send(err.toString());
            }
        });


        this.router.use("/capabilities/", new CapabilitiesRouter({
            robot: this.robot,
            validator: this.validator
        }).getRouter());
    }

    initSSE() {
        this.sseHubs = {
            state: new SSEHub({name: "State"}),
            attributes: new SSEHub({name: "Attributes"}),
            map: new SSEHub({name: "Map"})
        };

        this.robot.onStateUpdated(() => {
            this.sseHubs.state.event(
                ValetudoRobot.EVENTS.StateUpdated,
                JSON.stringify(this.robot.state)
            );
        });

        this.robot.onStateAttributesUpdated(() => {
            this.sseHubs.attributes.event(
                ValetudoRobot.EVENTS.StateAttributesUpdated,
                JSON.stringify(this.robot.state.attributes)
            );
        });

        this.robot.onMapUpdated(() => {
            this.sseHubs.map.event(
                ValetudoRobot.EVENTS.MapUpdated,
                JSON.stringify(this.robot.state.map)
            );
        });

        this.router.get(
            "/state/sse",
            SSEMiddleware({
                hub: this.sseHubs.state,
                keepAliveInterval: 5000,
                maxClients: 5
            }),
            (req, res) => {
                //Intentional, as the response will be handled by the SSEMiddleware
            }
        );

        this.router.get(
            "/state/attributes/sse",
            SSEMiddleware({
                hub: this.sseHubs.attributes,
                keepAliveInterval: 5000,
                maxClients: 5
            }),
            (req, res) => {
                //Intentional, as the response will be handled by the SSEMiddleware
            }
        );

        this.router.get(
            "/state/map/sse",
            SSEMiddleware({
                hub: this.sseHubs.map,
                keepAliveInterval: 5000,
                maxClients: 5
            }),
            (req, res) => {
                //Intentional, as the response will be handled by the SSEMiddleware
            }
        );
    }

    getRouter() {
        return this.router;
    }

    shutdown() {
        Object.values(this.sseHubs).forEach(hub => {
            hub.shutdown();
        });
    }
}

module.exports = RobotRouter;
