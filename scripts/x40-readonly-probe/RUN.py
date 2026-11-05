#!/usr/bin/env python3
"""Run one bounded X40 native read-only probe over SSH; original Valetudo stays up."""
import argparse
import hashlib
import json
import pathlib
import re
import shlex
import subprocess
import tempfile
import zipfile

KIT = pathlib.Path(__file__).resolve().parent
ORIGINAL = 'e1a29c9d01c9c196add05ca391c553a587146d2122d154f221dd323c5a6cfb45'
IDENTITY = r'''
set -eu
[ "$(uname -m)" = aarch64 ]
pids=''
for pid in $(pidof valetudo 2>/dev/null); do
  if [ "$(readlink /proc/$pid/exe)" = /data/valetudo ]; then
    pids="$pids $pid"
  fi
done
set -- $pids
[ "$#" -eq 1 ]
printf 'PID\t%s\n' "$1"
printf 'START\t%s\n' "$(awk '{print $22}' /proc/$1/stat)"
for file in /data/valetudo /data/valetudo_config.json /data/_root_postboot.sh; do
  [ -f "$file" ]
  printf 'HASH\t%s\t%s\n' "$file" "$(sha256sum "$file" | awk '{print $1}')"
done
'''


def invoke(argv, timeout=40, input_data=None):
    try:
        p = subprocess.run(argv, input=input_data, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 125, b'', type(e).__name__.encode()


def identity(body):
    result = {'hashes': {}}
    for line in body.decode().splitlines():
        p = line.split('\t')
        if len(p) == 2 and p[0] in ('PID', 'START') and p[1].isdigit():
            result[p[0].lower()] = p[1]
        elif len(p) == 3 and p[0] == 'HASH' and re.fullmatch('[0-9a-f]{64}', p[2]):
            result['hashes'][p[1]] = p[2]
    if not all(x in result for x in ('pid', 'start')) or set(result['hashes']) != {'/data/valetudo', '/data/valetudo_config.json', '/data/_root_postboot.sh'}:
        raise ValueError('Original Valetudo identity is incomplete')
    if result['hashes'].get('/data/valetudo') != ORIGINAL:
        raise ValueError('Installed Valetudo hash differs; stop for review')
    return result


def parse_result(body):
    value = json.loads(body)
    if value.get('state') == 'read_only_observations_received':
        if value.get('readOnly') is not True or value.get('nativeWritesRequested') != 0 or value.get('getPropertiesRequests') != 2:
            raise ValueError('Unexpected probe result contract')
        for key in ('preflight', 'settings'):
            if not isinstance(value.get(key), dict) or value[key].get('readOnly') is not True:
                raise ValueError('Unexpected probe observation contract')
    elif value.get('state') != 'failed' or value.get('nativeWritesRequested') != 0:
        raise ValueError('Unexpected probe failure contract')
    return value


def selftest():
    good = {'state': 'read_only_observations_received', 'readOnly': True,
            'nativeWritesRequested': 0, 'getPropertiesRequests': 2,
            'preflight': {'readOnly': True}, 'settings': {'readOnly': True}}
    assert parse_result(json.dumps(good)) == good
    for field, bad in [('nativeWritesRequested', 1), ('getPropertiesRequests', 3), ('readOnly', False)]:
        try:
            parse_result(json.dumps({**good, field: bad}))
        except ValueError:
            pass
        else:
            raise AssertionError('Unsafe contract accepted')
    fixture = ('PID\t123\nSTART\t456\nHASH\t/data/valetudo\t' + ORIGINAL + '\n' +
               'HASH\t/data/valetudo_config.json\t' + '1'*64 + '\n' +
               'HASH\t/data/_root_postboot.sh\t' + '2'*64 + '\n').encode()
    assert identity(fixture)['pid'] == '123'
    try:
        identity(fixture.replace(ORIGINAL.encode(), b'0'*64))
    except ValueError:
        pass
    else:
        raise AssertionError('Changed original accepted')
    print('HOST_SELFTEST_PASS: result scope and original identity checks')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--robot', default='root@192.168.8.149')
    ap.add_argument('--out', type=pathlib.Path, default=pathlib.Path.home() / 'Downloads')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    selftest()
    if args.self_test:
        return
    if not re.fullmatch(r'(?:[A-Za-z0-9_.-]+@)?[A-Za-z0-9][A-Za-z0-9.-]*', args.robot):
        ap.error('Use [user@]hostname or IPv4')
    receipt = KIT / 'probe-attempted.json'
    if receipt.exists():
        ap.error('This kit already attempted its one hardware read. Send the existing result for review; do not retry.')
    manifest = json.loads((KIT / 'manifest.json').read_text())
    binary = KIT / 'x40-readonly-probe'
    blob = binary.read_bytes()
    if hashlib.sha256(blob).hexdigest() != manifest['probeSha256']:
        ap.error('Probe binary SHA-256 mismatch')
    args.out.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(tempfile.mkdtemp(prefix='x40-readonly-result-', dir=args.out))
    out.chmod(0o700)
    ssh = ['ssh', '-T', '-o', 'ConnectTimeout=10', args.robot]
    stage = None
    report = {'state': 'not_run', 'originalUnchanged': None,
              'probeSha256': manifest['probeSha256'], 'issues': []}
    before = None
    def call(label, command, data=None, timeout=40):
        rc, body, errors = invoke(ssh + [command], input_data=data, timeout=timeout)
        (out / (label + '.ssh-errors.txt')).write_bytes(errors)
        return rc, body
    try:
        print('Checking the running original and file identities...', flush=True)
        rc, body = call('before', 'sh -s', IDENTITY.encode())
        if rc:
            raise ValueError('Original identity check failed; probe not started')
        before = identity(body)
        report['before'] = before
        rc, body = call('stage', 'umask 077; mktemp -d /tmp/x40-ro-XXXXXX')
        text = body.decode().strip()
        if rc or not re.fullmatch(r'/tmp/x40-ro-[A-Za-z0-9]{6}', text):
            raise ValueError('Unique staging directory unavailable')
        stage = text
        remote = shlex.quote(stage + '/probe')
        print('Staging the separate diagnostic executable...', flush=True)
        rc, _ = call('upload', 'umask 077; cat > ' + remote, blob, timeout=60)
        if rc:
            raise ValueError('Diagnostic upload failed')
        rc, body = call('hash', 'sha256sum ' + remote)
        if rc or body.decode().split()[0] != manifest['probeSha256']:
            raise ValueError('Remote diagnostic SHA-256 mismatch; not executed')
        rc, _ = call('permissions', 'chmod 500 ' + remote)
        if rc:
            raise ValueError('Diagnostic permissions failed')
        # Reserve a single attempt immediately before starting native reads.
        with receipt.open('x') as f:
            json.dump({'probeSha256': manifest['probeSha256'], 'resultDirectory': str(out)}, f)
        print('Running one bounded read-only probe; original Valetudo stays running...', flush=True)
        rc, body = call('probe', 'env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin ' + remote + ' --readonly-x40-probe', timeout=35)
        (out / 'probe-stdout.txt').write_bytes(body)
        result = parse_result(body)
        report['probeExitCode'] = rc
        report['observations'] = result
        report['state'] = 'observed' if rc == 0 and result['state'] == 'read_only_observations_received' else 'blocked'
    except Exception as e:
        report['state'] = 'blocked'
        report['issues'].append(str(e))
    finally:
        if stage:
            remote = shlex.quote(stage + '/probe')
            rc, _ = call('cleanup', 'rm -f ' + remote + '; rmdir ' + shlex.quote(stage))
            report['temporaryProbeRemoved'] = rc == 0
            if rc:
                report['state'] = 'blocked'
                report['issues'].append('Temporary diagnostic cleanup incomplete: ' + stage)
        if before:
            try:
                rc, body = call('after', 'sh -s', IDENTITY.encode())
                after = identity(body) if rc == 0 else None
                report['after'] = after
                report['originalUnchanged'] = before == after
            except Exception:
                report['originalUnchanged'] = False
            if not report['originalUnchanged']:
                report['state'] = 'blocked'
                report['issues'].append('Original process/files could not be confirmed unchanged; no automatic restore/restart attempted')
        (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        archive = out.with_suffix('.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out.iterdir()):
                if p.is_file():
                    z.write(p, p.name)
        print('RESULT:', report['state'])
        print('ORIGINAL_UNCHANGED:', report['originalUnchanged'])
        print('Upload:', archive)


if __name__ == '__main__':
    main()
