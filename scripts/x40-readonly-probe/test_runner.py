"""Offline host runner tests. No SSH or robot execution."""
import contextlib
import hashlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('runner', pathlib.Path(__file__).with_name('RUN.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_contract(self):
        runner.selftest()

    def test_mocked_runs(self):
        for scenario in ('success', 'native-failed', 'upload-mismatch', 'original-changed', 'cleanup-failed'):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temp:
                kit = pathlib.Path(temp)
                binary = b'\x7fELFfake offline fixture'
                sha = hashlib.sha256(binary).hexdigest()
                (kit / 'x40-readonly-probe').write_bytes(binary)
                (kit / 'manifest.json').write_text(json.dumps({'probeSha256': sha}))
                calls = []
                identity_reads = 0

                def fake(argv, timeout=40, input_data=None):
                    nonlocal identity_reads
                    cmd = argv[-1]
                    calls.append(cmd)
                    if cmd == 'sh -s':
                        identity_reads += 1
                        pid = '999' if scenario == 'original-changed' and identity_reads > 1 else '123'
                        body = ('PID\t'+pid+'\nSTART\t456\nHASH\t/data/valetudo\t'+runner.ORIGINAL+'\n' +
                                'HASH\t/data/valetudo_config.json\t'+'1'*64+'\n' +
                                'HASH\t/data/_root_postboot.sh\t'+'2'*64+'\n')
                        return 0, body.encode(), b''
                    if 'mktemp -d' in cmd:
                        return 0, b'/tmp/x40-ro-Ab1234\n', b''
                    if cmd.startswith('sha256sum '):
                        return 0, ((('0'*64) if scenario == 'upload-mismatch' else sha)+'  probe\n').encode(), b''
                    if 'env -i ' in cmd:
                        if scenario == 'native-failed':
                            return 3, json.dumps({'state': 'failed', 'reason': 'local_read_unavailable', 'nativeWritesRequested': 0}).encode(), b''
                        return 0, json.dumps({'state': 'read_only_observations_received', 'readOnly': True,
                            'nativeWritesRequested': 0, 'getPropertiesRequests': 2,
                            'preflight': {'readOnly': True, 'mode': 14},
                            'settings': {'readOnly': True}}).encode(), b''
                    if cmd.startswith('rm -f ') and scenario == 'cleanup-failed':
                        return 1, b'', b'fixture cleanup failure'
                    return 0, b'', b''

                original_kit, original_invoke, original_argv = runner.KIT, runner.invoke, sys.argv
                try:
                    runner.KIT, runner.invoke = kit, fake
                    sys.argv = ['RUN.py', '--out', temp]
                    with contextlib.redirect_stdout(io.StringIO()):
                        runner.main()
                    archive = next(kit.glob('x40-readonly-result-*.zip'))
                    with zipfile.ZipFile(archive) as z:
                        result = json.loads(z.read('result.json'))
                    self.assertEqual(result['state'], 'observed' if scenario == 'success' else 'blocked')
                    self.assertEqual(result['temporaryProbeRemoved'], scenario != 'cleanup-failed')
                    self.assertFalse(any('reboot' in cmd or 'kill ' in cmd for cmd in calls))
                    self.assertEqual(sum('env -i ' in cmd for cmd in calls), 0 if scenario == 'upload-mismatch' else 1)
                    if scenario != 'upload-mismatch':
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                            runner.main()
                finally:
                    runner.KIT, runner.invoke, sys.argv = original_kit, original_invoke, original_argv


if __name__ == '__main__':
    unittest.main()
