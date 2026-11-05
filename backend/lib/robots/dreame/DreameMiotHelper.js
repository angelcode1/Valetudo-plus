const RobotFirmwareError = require("../../core/RobotFirmwareError");
const {sleep} = require("../../utils/misc");

function responseIdentitiesMatch(properties, response) {
    return Array.isArray(response) && response.length === properties.length &&
        properties.every(p => response.filter(row => row?.siid === p.siid && row?.piid === p.piid).length === 1);
}

class DreameMiotHelper {
    /**
     * @param {object} options
     * @param {import("./DreameValetudoRobot")} options.robot
     * @param {number} [options.postWriteDelay]
     */
    constructor(options) {
        this.robot = options.robot;
        this.postWriteDelay = options.postWriteDelay ?? null;
    }

    /**
     * @param {Array<{siid: number, piid: number}>} properties
     * @param {object} [options]
     * @param {boolean} [options.retry]
     * @param {boolean} [options.prepareStamp]
     * @param {boolean} [options.strict] Require complete unique successful property identities
     * @param {number} [options.timeout]
     * @param {"local"|"cloud"} [options.interface]
     * @returns {Promise<Array<*>>}
     */
    async readProperties(properties, options) {
        const res = await this.robot.sendCommand("get_properties", properties.map(p => {
            return {
                did: this.robot.deviceId,
                siid: p.siid,
                piid: p.piid
            };
        }), options ? {
            retry: options.retry, timeout: options.timeout, interface: options.interface,
            ...(options.prepareStamp === true ? {prepareStamp: true} : {})
        } : undefined);

        if (options?.strict === true && (!responseIdentitiesMatch(properties, res) ||
            res.some(row => row.code !== 0))) {
            throw Object.assign(new Error("Received invalid property response"), {code: "MIOT_RESPONSE_INVALID"});
        }
        if (res && res.length === properties.length) {
            return res;
        } else {
            throw new Error("Received invalid response");
        }
    }

    /**
     * @param {number} siid
     * @param {number} piid
     * @param {object} [options]
     * @param {boolean} [options.retry]
     * @param {boolean} [options.prepareStamp]
     * @param {boolean} [options.strict]
     * @param {number} [options.timeout]
     * @param {"local"|"cloud"} [options.interface]
     * @returns {Promise<*>}
     */
    async readProperty(siid, piid, options) {
        const res = await this.readProperties([{ siid: siid, piid: piid }], options);

        if (res[0].code === 0) {
            return res[0].value;
        } else {
            throw new RobotFirmwareError("Error code " + res[0].code);
        }
    }

    /**
     * @param {Array<{siid: number, piid: number, value: *}>} properties
     * @param {object} [options]
     * @param {number|null} [options.postWriteDelay]
     * @param {boolean} [options.retry]
     * @param {boolean} [options.strict]
     * @param {number} [options.timeout]
     * @param {"local"|"cloud"} [options.interface]
     * @returns {Promise<void>}
     */
    async writeProperties(properties, options) {
        const postWriteDelay = options?.postWriteDelay ?? this.postWriteDelay;
        const res = await this.robot.sendCommand("set_properties", properties.map(p => {
            return {
                did: this.robot.deviceId,
                siid: p.siid,
                piid: p.piid,
                value: p.value
            };
        }), options ? {retry: options.retry, timeout: options.timeout, interface: options.interface} : undefined);

        if (options?.strict === true && (!responseIdentitiesMatch(properties, res) ||
            res.some(row => !Number.isSafeInteger(row.code)))) {
            throw Object.assign(new Error("Received invalid property response"), {code: "MIOT_RESPONSE_INVALID"});
        }
        if (res && res.length === properties.length) {
            const errorItem = res.find(r => r.code !== 0);
            if (errorItem) {
                throw new RobotFirmwareError("Error code " + errorItem.code);
            }

            if (postWriteDelay) {
                await sleep(postWriteDelay); // Give the firmware some time to think
            }
        } else {
            throw new Error("Received invalid response");
        }
    }

    /**
     *
     * @param {number} siid
     * @param {number} piid
     * @param {*} value
     * @param {object} [options]
     * @param {number|null} [options.postWriteDelay]
     * @param {boolean} [options.retry]
     * @param {boolean} [options.strict]
     * @param {number} [options.timeout]
     * @param {"local"|"cloud"} [options.interface]
     * @returns {Promise<void>}
     */
    async writeProperty(siid, piid, value, options) {
        await this.writeProperties([
            {
                siid: siid,
                piid: piid,
                value: value
            }
        ], options);
    }

    /**
     *
     * @param {number} siid
     * @param {number} aiid
     * @param {Array<*>} [additionalParameters]
     * @returns {Promise<void>}
     */
    async executeAction(siid, aiid, additionalParameters) {
        const res = await this.robot.sendCommand("action", {
            did: this.robot.deviceId,
            siid: siid,
            aiid: aiid,
            in: additionalParameters ?? []
        });

        if (res.code !== 0) {
            throw new RobotFirmwareError("Error code " + res.code);
        }
    }
}

module.exports = DreameMiotHelper;
