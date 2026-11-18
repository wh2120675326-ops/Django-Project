"""Check environment-dependent settings without connecting to a cloud database."""
import json
import os
from pathlib import Path
import subprocess
import sys
from django.test import SimpleTestCase


class DeploymentSettingsTests(SimpleTestCase):
    def inspect_settings(self, **overrides):
        env = {key: value for key, value in os.environ.items() if key not in {
            'RENDER', 'RENDER_EXTERNAL_HOSTNAME', 'DJANGO_DEBUG', 'DJANGO_SECRET_KEY',
            'DATABASE_URL', 'DJANGO_ALLOWED_HOSTS',
        }}
        env.update(overrides)
        return subprocess.run(
            [sys.executable, '-c', '''
import json
from campus_skillswap import settings as s
print(json.dumps({'debug': s.DEBUG, 'engine': s.DATABASES['default']['ENGINE'],
'hosts': s.ALLOWED_HOSTS, 'csrf': getattr(s, 'CSRF_TRUSTED_ORIGINS', []),
'secure_cookie': getattr(s, 'SESSION_COOKIE_SECURE', False),
'proxy': getattr(s, 'SECURE_PROXY_SSL_HEADER', None)}))
'''], env=env, cwd=Path(__file__).resolve().parent.parent,
            capture_output=True, text=True, check=False,
        )

    def test_local_defaults_keep_sqlite(self):
        result = self.inspect_settings()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data['debug'])
        self.assertEqual(data['engine'], 'django.db.backends.sqlite3')
        self.assertFalse(data['secure_cookie'])

    def test_render_uses_postgres_and_its_exact_hostname(self):
        result = self.inspect_settings(RENDER='true', DJANGO_SECRET_KEY='test-only-key',
            DATABASE_URL='postgresql://test:test@localhost:5432/test',
            RENDER_EXTERNAL_HOSTNAME='campus-test.onrender.com')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data['debug'])
        self.assertEqual(data['engine'], 'django.db.backends.postgresql')
        self.assertIn('campus-test.onrender.com', data['hosts'])
        self.assertNotIn('*', data['hosts'])
        self.assertEqual(data['csrf'], ['https://campus-test.onrender.com'])
        self.assertTrue(data['secure_cookie'])
        self.assertEqual(data['proxy'], ['HTTP_X_FORWARDED_PROTO', 'https'])

    def test_production_requires_secret(self):
        result = self.inspect_settings(RENDER='true')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Set DJANGO_SECRET_KEY', result.stderr)

    def test_render_refuses_missing_or_sqlite_database(self):
        for url in ['', 'sqlite:///temporary.sqlite3']:
            result = self.inspect_settings(RENDER='true', DJANGO_SECRET_KEY='test-only-key', DATABASE_URL=url)
            self.assertNotEqual(result.returncode, 0)
