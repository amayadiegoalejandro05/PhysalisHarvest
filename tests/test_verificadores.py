import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_repository
import check_git_context


def states(report):
    return {entry['id']: entry['status'] for entry in report.checks}


class RepositoryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        for name in check_repository.FILES:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('# Documento\n', encoding='utf-8')
        for name in check_repository.DIRS:
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def tearDown(self): self.temp.cleanup()

    def test_empty_ros_scaffold_is_skipped(self):
        result = states(check_repository.check(self.root))
        self.assertEqual(result['REP-STRUCTURE'], 'PASS')
        self.assertEqual(result['REP-ROS-MANIFEST'], 'SKIP')

    def test_invalid_inputs_and_broken_link(self):
        (self.root / 'bad.py').write_text('def invalid(\n')
        (self.root / 'bad.json').write_text('{')
        (self.root / 'README.md').write_text('[falta](ausente.md)')
        p = self.root / 'ros2_ws/src/robot_brazo/package.xml'
        p.write_text('<package><name>otro</name></package>')
        result = states(check_repository.check(self.root))
        for key in ('REP-PYTHON', 'REP-JSON', 'REP-LINKS', 'REP-ROS-MANIFEST'):
            self.assertEqual(result[key], 'FAIL')
        (self.root / 'bad.py').write_text('value = 1\n')
        (self.root / 'bad.json').write_text('{}')
        (self.root / 'README.md').write_text('[válido](CONTRIBUTING.md)', encoding='utf-8')
        p.write_text('<package><name>robot_brazo</name></package>')
        result = states(check_repository.check(self.root))
        for key in ('REP-PYTHON', 'REP-JSON', 'REP-LINKS', 'REP-ROS-MANIFEST'):
            self.assertEqual(result[key], 'PASS')

    def test_secrets_and_ai_missing_reference(self):
        (self.root / 'credentials.txt').write_text('password = "' + 'x' * 20 + '"')
        (self.root / 'docs/AI_USAGE.md').write_text('IA')
        (self.root / 'docs/ai_usage.json').write_text(json.dumps({'uses': [{'paths': ['no-existe']}]}))
        result = states(check_repository.check(self.root))
        self.assertEqual(result['REP-CONTENT'], 'FAIL')
        self.assertEqual(result['REP-AI'], 'FAIL')

    def test_valid_and_invalid_yaml_when_parser_available(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest('PyYAML no disponible')
        path = self.root / 'config.yaml'
        path.write_text('key: value\n')
        self.assertEqual(states(check_repository.check(self.root))['REP-YAML'], 'PASS')
        path.write_text('key: [\n')
        self.assertEqual(states(check_repository.check(self.root))['REP-YAML'], 'FAIL')


class GitChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.root / 'example').write_text('test')
        self.git('add', 'example')
        self.git('commit', '-qm', 'initial')
        self.git('remote', 'add', 'origin', 'https://github.com/amayadiegoalejandro05/Robot-Cosechador.git')
        self.git('update-ref', 'refs/remotes/origin/main', 'HEAD')

    def tearDown(self): self.temp.cleanup()
    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True, text=True)

    def test_target_not_required_to_equal_head(self):
        self.git('switch', '-qc', 'feature/vision-test')
        (self.root / 'example').write_text('changed')
        self.git('commit', '-qam', 'change')
        result = states(check_git_context.check(self.root, target='main', subsystem='vision', environ={}))
        self.assertEqual(result['GIT-TARGET-DIVERGENCE'], 'PASS')
        self.assertEqual(result['GIT-SUBSYSTEM'], 'PASS')
        self.assertEqual(result['GIT-UPSTREAM'], 'SKIP')

    def test_old_base_dirty_and_wrong_subsystem(self):
        self.git('switch', '-qc', 'feature/brazo-demo')
        old = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.root / 'example').write_text('new')
        self.git('commit', '-qam', 'new')
        self.git('update-ref', 'refs/remotes/origin/main', 'HEAD')
        self.git('switch', '--detach', old)
        (self.root / 'untracked').write_text('x')
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'pull_request', 'GITHUB_HEAD_REF': 'feature/brazo-demo', 'GITHUB_BASE_REF': 'main'}
        result = states(check_git_context.check(self.root, subsystem='vision', environ=env))
        self.assertEqual(result['GIT-BRANCH'], 'SKIP')
        self.assertEqual(result['GIT-TARGET-DIVERGENCE'], 'FAIL')
        self.assertEqual(result['GIT-WORKTREE'], 'FAIL')
        self.assertEqual(result['GIT-SUBSYSTEM'], 'FAIL')

    def test_wrong_remote(self):
        self.git('remote', 'set-url', 'origin', 'https://example.invalid/other.git')
        self.assertEqual(states(check_git_context.check(self.root, environ={}))['GIT-ORIGIN'], 'FAIL')

    def test_detached_pull_request_does_not_claim_source_is_current(self):
        self.git('switch', '--detach')
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'pull_request', 'GITHUB_HEAD_REF': 'feature/vision-test', 'GITHUB_BASE_REF': 'main'}
        result = states(check_git_context.check(self.root, environ=env))
        self.assertEqual(result['GIT-TARGET-DIVERGENCE'], 'SKIP')


class RosInventoryChecks(unittest.TestCase):
    def test_package_counts_and_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'ros2_ws/src/robot_brazo'
            package.mkdir(parents=True)
            (package / 'package.xml').write_text('<package><name>robot_brazo</name></package>')
            results = root / 'ros2_ws/build/robot_brazo/test_results'
            results.mkdir(parents=True)
            (results / 'result.xml').write_text('<testsuite><testcase name="one"/></testsuite>')
            script = Path(__file__).resolve().parents[1] / 'scripts/report_ros_packages.py'
            result = subprocess.run([sys.executable, str(script), str(root)], check=True, capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            self.assertIn('Paquetes ROS detectados: 1', result.stdout)
            self.assertIn('brazo: 1 paquetes', result.stdout)
            self.assertIn('1 casos con resultado', result.stdout)
            self.assertIn('visión: SKIP', result.stdout)


if __name__ == '__main__': unittest.main()
