"""An http redirect URI must not be usable outside DEBUG (#146).

`OAUTH2_PROVIDER['ALLOWED_REDIRECT_URI_SCHEMES']` used to read
`['https', 'http']` unconditionally, under a comment claiming https was
enforced in production. Nothing enforced it; the comment was the control.

django-oauth-toolkit consults the setting in two places, and this file pins
both because they have different blast radii:

1. **Registration.** `Application.clean` refuses to store a redirect URI whose
   scheme is not listed. That runs on every path calling `full_clean` -- the
   admin, `/o/applications/register/`, `/o/applications/<pk>/update/` -- but
   NOT on `Application.objects.update_or_create`, which is how
   `create_smart_app` writes. So the setting did not reach the command.
2. **Redirect construction.** `AuthorizationView.redirect` hands
   `application.get_allowed_schemes()` to `OAuth2ResponseRedirect`, whose
   `validate_redirect` raises `DisallowedRedirect` (HTTP 400) for a scheme not
   listed. This applies to rows ALREADY in the database, which is why
   tightening the setting is a breaking change for any Application still
   holding an http redirect URI -- `test_stored_http_row_is_refused_at_authorize_time`
   is that break, asserted rather than described.
"""
import importlib.util
import os
from unittest import mock

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings

from oauth2_provider.models import Application

from patient_portal.models import Identity


def _oauth2_provider_with(schemes):
    return {**settings.OAUTH2_PROVIDER, 'ALLOWED_REDIRECT_URI_SCHEMES': schemes}


def _load_settings_module_with_env(**env):
    """Import ctomop/settings.py fresh under a patched environment.

    Loading a NEW module object rather than reloading `ctomop.settings` keeps
    `sys.modules` and `django.conf.settings` untouched, so this cannot leak
    into other tests.
    """
    path = os.path.join(settings.BASE_DIR, 'ctomop', 'settings.py')
    spec = importlib.util.spec_from_file_location('_ctomop_settings_probe', path)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(os.environ, env, clear=False):
        spec.loader.exec_module(module)
    return module


class AllowedRedirectSchemesSettingTest(SimpleTestCase):
    """Assert BOTH branches in one run.

    CI runs the suite with DEBUG=True. A test that only checks the branch
    matching the ambient DEBUG would pass against the pre-fix hardcoded
    `['https', 'http']`, so it would not defend the setting at all.
    """

    _PROD_ENV = {
        'DEBUG': 'False',
        'SECRET_KEY': 'test-probe-key-long-enough-to-pass-the-guard',
        'DATABASE_URL': 'postgres://postgres@localhost:5432/probe',
        'ALLOWED_HOSTS': 'probe.example.invalid',
        'CORS_ALLOWED_ORIGINS': 'https://probe.example.invalid',
    }

    def test_outside_debug_only_https_is_allowed(self):
        module = _load_settings_module_with_env(**self._PROD_ENV)

        self.assertFalse(module.DEBUG)
        self.assertEqual(
            module.OAUTH2_PROVIDER['ALLOWED_REDIRECT_URI_SCHEMES'], ['https']
        )

    def test_under_debug_http_is_allowed_for_the_local_dev_server(self):
        module = _load_settings_module_with_env(DEBUG='True')

        self.assertTrue(module.DEBUG)
        self.assertEqual(
            module.OAUTH2_PROVIDER['ALLOWED_REDIRECT_URI_SCHEMES'],
            ['https', 'http'],
        )


class StoredHttpRedirectAtAuthorizeTimeTest(TestCase):
    """The break this change causes, asserted instead of described.

    A row written before the setting was tightened keeps its http redirect URI.
    `Application.redirect_uri_allowed` matches it -- it compares the request's
    URI against the stored one (`models.py:899` does check that the schemes
    agree) but never consults `ALLOWED_REDIRECT_URI_SCHEMES` -- so the grant is
    minted, and then the response refuses to redirect. The user gets a 400 and
    a grant row that can never be redeemed.
    """

    def setUp(self):
        self.identity = Identity.objects.create(
            issuer='urn:local',
            sub='authorize-time-user',
            email='authorize-time-user@example.invalid',
        )
        self.identity.set_password('probe-password')
        self.identity.save()
        # Written the way a pre-#146 row was: no full_clean, so no scheme check.
        self.application = Application.objects.create(
            name='legacy http client',
            client_id='legacy-http-client',
            client_secret='',
            user=self.identity,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://legacy.example.invalid/cb',
            skip_authorization=True,
        )

    def _authorize(self):
        self.client.force_login(self.identity)
        return self.client.get(
            '/o/authorize/',
            {
                'client_id': 'legacy-http-client',
                'response_type': 'code',
                'redirect_uri': 'http://legacy.example.invalid/cb',
                'scope': 'openid',
                'state': 'st',
                # PKCE_REQUIRED is on; 'plain' keeps the fixture readable.
                'code_challenge': 'a' * 43,
                'code_challenge_method': 'plain',
            },
        )

    def test_stored_http_row_still_redirects_while_http_is_allowed(self):
        with override_settings(
            OAUTH2_PROVIDER=_oauth2_provider_with(['https', 'http'])
        ):
            response = self._authorize()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response['Location'].startswith('http://legacy.example.invalid/cb')
        )

    def test_stored_http_row_is_refused_at_authorize_time(self):
        """https-only turns the same request into a 400. This is the break.

        The status code alone would not prove the cause -- a 400 could come
        from PKCE, scope or client validation. Django logs every
        `SuspiciousOperation` to `django.security.<ExceptionName>`, so
        asserting on `django.security.DisallowedRedirect` pins it to
        `OAuth2ResponseRedirect.validate_redirect` and nothing else. The
        sibling test above issues the identical request and gets a 302, which
        rules out the request itself being malformed.
        """
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            with self.assertLogs('django.security.DisallowedRedirect', 'WARNING') as logs:
                response = self._authorize()

        self.assertEqual(response.status_code, 400)
        self.assertIn("scheme 'http' is not permitted", '\n'.join(logs.output))


class HttpsRedirectAtAuthorizeTimeTest(TestCase):
    """The other half of the pair: https-only must not over-block https.

    Without this, `test_stored_http_row_is_refused_at_authorize_time` would be
    consistent with the redirect path being broken for every scheme.
    """

    def setUp(self):
        self.identity = Identity.objects.create(
            issuer='urn:local',
            sub='https-authorize-user',
            email='https-authorize-user@example.invalid',
        )
        self.identity.set_password('probe-password')
        self.identity.save()
        Application.objects.create(
            name='https client',
            client_id='https-client',
            client_secret='',
            user=self.identity,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='https://app.example.invalid/cb',
            skip_authorization=True,
        )

    def test_https_row_still_redirects_under_https_only(self):
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            self.client.force_login(self.identity)
            response = self.client.get(
                '/o/authorize/',
                {
                    'client_id': 'https-client',
                    'response_type': 'code',
                    'redirect_uri': 'https://app.example.invalid/cb',
                    'scope': 'openid',
                    'state': 'st',
                    'code_challenge': 'a' * 43,
                    'code_challenge_method': 'plain',
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response['Location'].startswith('https://app.example.invalid/cb')
        )


class CreateSmartAppSchemeTest(TestCase):
    """`create_smart_app` must honour the setting rather than bypass it."""

    def setUp(self):
        Identity.objects.create(
            issuer='urn:local',
            sub='smart-app-owner',
            email='smart-app-owner@example.invalid',
            is_staff=True,
        )

    def _create(self, client_id, redirect_uris, schemes):
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(schemes)):
            call_command(
                'create_smart_app',
                '--client-id', client_id,
                '--redirect-uris', redirect_uris,
            )

    def test_http_redirect_is_refused_when_only_https_is_allowed(self):
        with self.assertRaises(CommandError) as caught:
            self._create(
                'scheme-test-app', 'http://evil.example.invalid/callback', ['https']
            )

        self.assertIn('http://evil.example.invalid/callback', str(caught.exception))
        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app').exists(),
            'the Application must not be written when the scheme is refused',
        )

    def test_one_bad_uri_refuses_the_whole_registration(self):
        with self.assertRaises(CommandError):
            self._create(
                'scheme-test-app-mixed',
                'https://app.example.invalid/cb http://app.example.invalid/cb',
                ['https'],
            )

        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app-mixed').exists()
        )

    def test_malformed_absolute_uri_is_refused(self):
        """`https:/app` has an https scheme and is still not a usable URI.

        A scheme-only comparison accepts it. Borrowing the toolkit's own
        validator is what makes the command refuse it, as the admin does.
        """
        with self.assertRaises(CommandError):
            self._create(
                'scheme-test-app-malformed',
                'https:/app.example.invalid/callback',
                ['https'],
            )

        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app-malformed').exists()
        )

    def test_scheme_relative_uri_is_refused(self):
        with self.assertRaises(CommandError):
            self._create(
                'scheme-test-app-relative', '//app.example.invalid/callback', ['https']
            )

        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app-relative').exists()
        )

    def test_a_refusal_leaves_an_existing_row_untouched(self):
        """`update_or_create` updates as well as creates.

        Asserting only that nothing was *created* would miss the worse case:
        an existing, valid client being rewritten with a bad redirect URI.
        """
        self._create(
            'scheme-test-app-idem', 'https://good.example.invalid/cb', ['https']
        )

        with self.assertRaises(CommandError):
            self._create(
                'scheme-test-app-idem', 'http://bad.example.invalid/cb', ['https']
            )

        self.assertEqual(
            Application.objects.get(client_id='scheme-test-app-idem').redirect_uris,
            'https://good.example.invalid/cb',
        )

    def test_empty_redirect_uris_is_refused(self):
        """The admin refuses this too, via a different branch of `clean`.

        `Application.clean` raises "redirect_uris cannot be empty with
        grant_type authorization-code". The validator loop never sees an empty
        string, so without an explicit check the command would accept what the
        admin refuses -- and the comment claiming the two agree would be wrong.
        """
        with self.assertRaises(CommandError) as caught:
            self._create('scheme-test-app-empty', '', ['https'])

        self.assertIn('cannot be empty', str(caught.exception))
        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app-empty').exists()
        )

    def test_https_redirect_still_registers(self):
        self._create(
            'scheme-test-app-ok', 'https://app.example.invalid/callback', ['https']
        )

        self.assertTrue(
            Application.objects.filter(client_id='scheme-test-app-ok').exists()
        )

    def test_http_still_registers_where_the_setting_allows_it(self):
        """Local dev keeps working -- the guard follows the setting, not DEBUG."""
        self._create(
            'scheme-test-app-dev',
            'http://localhost:5173/auth/callback',
            ['https', 'http'],
        )

        self.assertTrue(
            Application.objects.filter(client_id='scheme-test-app-dev').exists()
        )


class RedirectUriSchemeSystemCheckTest(TestCase):
    """The deploy-time check that finds the rows this change breaks.

    "Sweep the rows before deploying" is an instruction in a comment, and
    `render.yaml` sets `autoDeploy: true`. This check puts the same condition
    in front of `manage.py check --deploy` -- and the change adds that command
    to `start.sh`, which did not run it before, so the check is reached on boot
    rather than only when someone thinks to type it.
    """

    def setUp(self):
        identity = Identity.objects.create(
            issuer='urn:local',
            sub='system-check-owner',
            email='system-check-owner@example.invalid',
        )
        Application.objects.create(
            name='legacy http client',
            client_id='system-check-http-client',
            client_secret='',
            user=identity,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://legacy.example.invalid/cb',
        )

    def test_http_row_is_reported_when_only_https_is_allowed(self):
        from patient_portal.checks import redirect_uri_scheme_check

        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            warnings = redirect_uri_scheme_check(None)

        self.assertEqual([w.id for w in warnings], ['patient_portal.W010'])
        self.assertIn('system-check-http-client', warnings[0].hint)
        self.assertIn('http', warnings[0].hint)

    def test_the_check_is_registered_as_a_deploy_check(self):
        """Otherwise the logic above would be correct and never run.

        Deployment checks are opt-in -- Django defaults to
        `include_deployment_checks=False` -- so a check registered without
        `deploy=True` is skipped everywhere, and one registered with it runs
        only where `check --deploy` is actually invoked.
        `test_start_sh_runs_the_deploy_checks` pins the other half.
        """
        from django.core.checks.registry import registry

        from patient_portal.checks import redirect_uri_scheme_check

        self.assertNotIn(redirect_uri_scheme_check, registry.get_checks())
        self.assertIn(
            redirect_uri_scheme_check,
            registry.get_checks(include_deployment_checks=True),
        )

    def test_start_sh_runs_the_deploy_checks(self):
        """A `deploy=True` check that nothing invokes is decoration.

        This was true of the first draft: `start.sh` on this branch ran
        `migrate`, `setup_admin` and gunicorn, and never `check`. The check
        would have been correct and unreachable -- the same shape as the
        comment #146 exists to delete.
        """
        from pathlib import Path

        from django.conf import settings

        start_sh = (Path(settings.BASE_DIR) / 'start.sh').read_text()

        self.assertIn('manage.py check --deploy', start_sh)
        self.assertLess(
            start_sh.index('manage.py check --deploy'),
            start_sh.index('gunicorn'),
            'the checks must run before the server accepts traffic',
        )

    def test_a_logout_only_offender_is_reported_as_a_logout_failure(self):
        """The consequence differs by field, so the hint must not flatten it.

        A row with no `redirect_uris` never reaches authorization at all; its
        failure is RP-initiated logout, and no grant is involved.
        """
        from patient_portal.checks import redirect_uri_scheme_check

        identity = Identity.objects.get(sub='system-check-owner')
        Application.objects.create(
            name='logout only',
            client_id='system-check-logout-only',
            client_secret='',
            user=identity,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
            redirect_uris='',
            post_logout_redirect_uris='http://logout.example.invalid/x',
        )

        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            hint = redirect_uri_scheme_check(None)[0].hint

        self.assertIn('RP-initiated logout will fail', hint)
        self.assertIn('system-check-logout-only', hint)
        # The authorize-time sentence belongs to the other client, not this one.
        authorize_sentence = hint.split('RP-initiated logout')[0]
        self.assertNotIn('system-check-logout-only', authorize_sentence)

    def test_an_unreadable_database_is_not_reported_as_clean(self):
        """Failing open silently is the failure mode this check exists to stop."""
        from django.db import Error as DatabaseAccessError

        from patient_portal.checks import redirect_uri_scheme_check

        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            with mock.patch.object(
                Application.objects.__class__,
                'exclude',
                side_effect=DatabaseAccessError('connection refused'),
            ):
                warnings = redirect_uri_scheme_check(None)

        self.assertEqual([w.id for w in warnings], ['patient_portal.W011'])
        self.assertIn('not a clean result', warnings[0].hint)
        self.assertIn('connection refused', warnings[0].hint)

    def test_nothing_is_reported_while_http_is_allowed(self):
        from patient_portal.checks import redirect_uri_scheme_check

        with override_settings(
            OAUTH2_PROVIDER=_oauth2_provider_with(['https', 'http'])
        ):
            self.assertEqual(redirect_uri_scheme_check(None), [])
