const {execFileSync} = require('child_process');
const fs = require('fs');
const path = require("path");


function GET_VALETUDO_VERSION() {
    let valetudoVersion = "unknown";

    try {
        const rootDirectory = path.resolve(__dirname, "..");
        const packageContent = fs.readFileSync(rootDirectory + "/package.json", {"encoding": "utf-8"});

        if (packageContent) {
            valetudoVersion = JSON.parse(packageContent.toString()).version;
        }
    } catch (e) {
        //intentional
    }

    return valetudoVersion;
}

function GET_COMMIT_ID() {
    try {
        return execFileSync("git", ["rev-parse", "--verify", "HEAD"], {
            cwd: path.resolve(__dirname, ".."),
            encoding: "utf-8",
            stdio: ["ignore", "pipe", "ignore"]
        }).trim();
    } catch (e) {
        return "unknown";
    }
}


const metadata = {
    version: GET_VALETUDO_VERSION(),
    commit:  GET_COMMIT_ID(),
    buildTimestamp: new Date().toISOString(),
};

fs.writeFileSync(
    path.join(__dirname, "../backend/lib/res/build_metadata.json"),
    JSON.stringify(metadata)
);
