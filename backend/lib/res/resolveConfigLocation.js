"use strict";

const os = require("os");
const path = require("path");
const env = require("./env");

/**
 * Preserve the installed X40's explicit config file path while retaining
 * upstream Valetudo's normal DataPath-based behavior on all other installs.
 * Never quietly fall back to defaults when an explicit path is malformed.
 *
 * @param {NodeJS.ProcessEnv} vars
 * @returns {string}
 */
function resolveConfigLocation(vars = process.env) {
    const explicitlyConfigured = vars[env.ConfigPath];
    if (explicitlyConfigured !== undefined) {
        if (typeof explicitlyConfigured !== "string" ||
            !path.isAbsolute(explicitlyConfigured)) {
            throw new Error("VALETUDO_CONFIG_PATH must be an absolute path");
        }
        return explicitlyConfigured;
    }

    return path.join(vars[env.DataPath] ?? os.tmpdir(), "valetudo_config.json");
}

module.exports = resolveConfigLocation;
