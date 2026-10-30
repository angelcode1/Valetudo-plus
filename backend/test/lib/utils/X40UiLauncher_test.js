"use strict";

const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawnSync} = require("node:child_process");
const {test} = require("node:test");

const launcher = path.resolve(__dirname, "../../../../util/x40/ui-launch.sh");
const quote = value => "'" + value.replace(/'/g, "'\\''") + "'";
const hash = file => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

function fixture(t) {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "x40-ui-launch-"));
    t.after(() => fs.rmSync(root, {recursive: true, force: true}));
    const state = path.join(root, "profile");
    const bin = path.join(root, "bin");
    const output = path.join(root, "application.out");
    const original = path.join(root, "original");
    const candidate = path.join(state, "valetudo");
    const release = "fixture-release";
    fs.mkdirSync(state);
    fs.mkdirSync(bin);
    fs.mkdirSync(path.join(state, "data"));
    fs.writeFileSync(path.join(state, "config.json"), "{}");
    fs.writeFileSync(path.join(state, "release"), release + "\n");
    fs.writeFileSync(path.join(state, "enabled"), release + "\n");

    const app = role => "#!/bin/sh\nprintf '%s\\n' " + quote(role) +
        " \"$VALETUDO_CONFIG_PATH\" \"$VALETUDO_DATA_PATH\"" +
        " \"$VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS\"" +
        " \"$VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY\"" +
        " \"${VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED-unset}\"" +
        " \"${VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED-unset}\"" +
        " \"${VALETUDO_X40_NATIVE_SMARTHOST_TEST-unset}\" > " + quote(output) + "\n";
    fs.writeFileSync(original, app("original"), {mode: 0o700});
    fs.writeFileSync(candidate, app("candidate"), {mode: 0o700});
    const hasher = path.join(root, "hash.js");
    fs.writeFileSync(hasher, "const fs=require('fs'),c=require('crypto');" +
        "console.log(c.createHash('sha256').update(fs.readFileSync(process.argv[2])).digest('hex')+'  '+process.argv[2]);");
    const tool = (name, body) => fs.writeFileSync(path.join(bin, name), "#!/bin/sh\n" + body, {mode: 0o700});
    tool("sha256sum", "exec " + quote(process.execPath) + " " + quote(hasher) + " \"$@\"\n");
    // Fake ONLY detached process creation. Production ownership/ready validation
    // and exec/env branches run unchanged. No SSH or real reboot occurs.
    tool("nohup", "[ \"${TEST_NO_READY-0}\" = 0 ] || exit 0\n" +
        "printf '%s\\n' \"$@\" > \"${5}/spawn.args\"\n" +
        "printf '%s\\n%s\\n' \"$PPID\" \"${9}\" > \"${5}/watch.ready\"\n");
    tool("sleep", "if [ \"$1\" = 900 ]; then\n" +
        " if [ \"${TEST_STALE_TEMP-0}\" = 1 ]; then printf stale > " + quote(state) + "/.rollback.$PPID; fi\n" +
        " exit 0\nfi\nexec /bin/sleep 0.01\n");
    tool("sync", "printf sync > " + quote(path.join(root, "sync.called")) + "\n");
    tool("reboot", "printf reboot > " + quote(path.join(root, "reboot.called")) + "\n");

    const candidateSha = hash(candidate);
    const originalSha = hash(original);
    const env = {...process.env, PATH: bin + path.delimiter + process.env.PATH,
        VALETUDO_CONFIG_PATH: path.join(root, "original.json"),
        VALETUDO_DATA_PATH: path.join(root, "original-data"),
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS: "0",
        VALETUDO_X40_CLEANGENIUS_OBSERVE_ONLY: "1",
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_ADVANCED: "1",
        VALETUDO_X40_EXPERIMENTAL_CLEANGENIUS_SIGNED: "1",
        VALETUDO_X40_NATIVE_SMARTHOST_TEST: "1"};
    return {root: root, state: state, original: original, candidate: candidate, release: release, candidateSha: candidateSha, originalSha: originalSha, env: env,
        mark: name => fs.writeFileSync(path.join(state, name), release + "\n"),
        exists: name => fs.existsSync(path.join(state, name)),
        run: (mode = "launch", overrides = {}) => {
            const result = spawnSync("sh", [launcher, mode, state, original, candidateSha, originalSha, release],
                {env: {...env, ...overrides}, encoding: "utf8", timeout: 10000});
            if (result.error) {
                throw result.error;
            }
            return result;
        },
        read: () => fs.readFileSync(output, "utf8").trim().split("\n")};
}

test("X40 launch: no enable marker keeps the original default-off environment", t => {
    const f = fixture(t);
    fs.unlinkSync(path.join(f.state, "enabled"));
    assert.equal(f.run().status, 0);
    assert.deepEqual(f.read(), ["original", f.env.VALETUDO_CONFIG_PATH, f.env.VALETUDO_DATA_PATH,
        "0", "1", "unset", "unset", "unset"]);
    assert.equal(f.exists("boot-attempt"), false);
});

test("X40 launch: accepted release exposes only the main control in its own profile", t => {
    const f = fixture(t);
    f.mark("accepted");
    assert.equal(f.run().status, 0);
    assert.deepEqual(f.read(), ["candidate", path.join(f.state, "config.json"), path.join(f.state, "data"),
        "1", "1", "0", "0", "0"]);
    assert.equal(f.exists("watch.ready"), false);
});

test("X40 launch: absent release metadata falls back to the pinned original", t => {
    const f = fixture(t);
    fs.unlinkSync(path.join(f.state, "release"));
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "original");
});

test("X40 watch: wrong release metadata cannot request a reboot", t => {
    const f = fixture(t);
    fs.writeFileSync(path.join(f.state, "release"), "different\n");
    assert.notEqual(f.run("watch").status, 0);
    assert.equal(fs.existsSync(path.join(f.root, "reboot.called")), false);
});

test("X40 launch: rollback wins over an accepted release", t => {
    const f = fixture(t);
    f.mark("accepted");
    f.mark("rollback");
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "original");
});

test("X40 launch: corrupt candidate falls back to the pinned original", t => {
    const f = fixture(t);
    f.mark("accepted");
    fs.appendFileSync(f.candidate, "# changed\n");
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "original");
});

test("X40 launch: corrupt original never runs either application", t => {
    const f = fixture(t);
    fs.appendFileSync(f.original, "# changed\n");
    assert.notEqual(f.run().status, 0);
    assert.throws(() => f.read(), {code: "ENOENT"});
});

test("X40 launch: malformed acceptance falls back instead of renewing a trial", t => {
    const f = fixture(t);
    fs.writeFileSync(path.join(f.state, "accepted"), "another-release\n");
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "original");
    assert.equal(f.exists("boot-attempt"), false);
});

test("X40 launch: linked candidate profile is refused", t => {
    const f = fixture(t);
    f.mark("accepted");
    const config = path.join(f.state, "config.json");
    fs.renameSync(config, path.join(f.root, "external.json"));
    fs.symlinkSync(path.join(f.root, "external.json"), config);
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "original");
});

test("X40 launch: first unconfirmed boot starts recovery before the candidate", t => {
    const f = fixture(t);
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "candidate");
    assert.equal(f.exists("boot-attempt"), true);
    assert.equal(f.exists("watch.ready"), true);
    assert.equal(f.exists("accepted"), false);
    const args = fs.readFileSync(path.join(f.state, "spawn.args"), "utf8").trim().split("\n");
    assert.deepEqual(args.slice(0, 4), ["setsid", "sh", launcher, "watch"]);
    assert.equal(args.at(-1), f.release);
});

test("X40 launch: another unconfirmed boot selects original without retrying candidate", t => {
    const f = fixture(t);
    fs.mkdirSync(path.join(f.state, "boot-attempt"));
    assert.equal(f.run().status, 0);
    assert.equal(f.read()[0], "original");
    assert.equal(f.exists("rollback"), true);
});

test("X40 launch: missing detached recovery proof prevents candidate execution", t => {
    const f = fixture(t);
    assert.equal(f.run("launch", {TEST_NO_READY: "1"}).status, 0);
    assert.equal(f.read()[0], "original");
    assert.equal(f.exists("rollback"), true);
});

test("X40 watch: expiry selects original for next boot before requesting normal reboot", t => {
    const f = fixture(t);
    assert.equal(f.run("watch").status, 0);
    assert.equal(f.exists("rollback"), true);
    assert.equal(fs.readFileSync(path.join(f.root, "sync.called"), "utf8"), "sync");
    assert.equal(fs.readFileSync(path.join(f.root, "reboot.called"), "utf8"), "reboot");
    assert.equal(f.exists("accepted"), false);
});

test("X40 watch: acceptance disarms the pending reboot", t => {
    const f = fixture(t);
    f.mark("accepted");
    assert.equal(f.run("watch").status, 0);
    assert.equal(f.exists("rollback"), false);
    assert.equal(fs.existsSync(path.join(f.root, "reboot.called")), false);
});

test("X40 watch: stale process-named temporary files cannot prevent fallback", t => {
    const f = fixture(t);
    assert.equal(f.run("watch", {TEST_STALE_TEMP: "1"}).status, 0);
    assert.equal(f.exists("rollback"), true);
    assert.equal(fs.readFileSync(path.join(f.root, "reboot.called"), "utf8"), "reboot");
});

test("X40 watch: existing rollback marker does not cause a second reboot", t => {
    const f = fixture(t);
    f.mark("rollback");
    assert.equal(f.run("watch").status, 0);
    assert.equal(fs.existsSync(path.join(f.root, "reboot.called")), false);
});

test("X40 launch: bad release and invalid hash arguments are refused", t => {
    const f = fixture(t);
    for (const [sha, release] of [["invalid", f.release], [f.candidateSha, "x;command"]]) {
        const r = spawnSync("sh", [launcher, "launch", f.state, f.original, sha, f.originalSha, release],
            {env: f.env, encoding: "utf8"});
        assert.notEqual(r.status, 0);
    }
    assert.throws(() => f.read(), {code: "ENOENT"});
});
