"""An http redirect URI must not be registrable outside DEBUG (#146).

`OAUTH2_PROVIDER['ALLOWED_REDIRECT_URI_SCHEMES']` used to read
`['https', 'http']` unconditionally, under a comment claiming https was
enforced in production. Two separate things were wrong, and both are asserted
here:

1. the setting itself allowed http everywhere;
2. `create_smart_app` -- the only registration path in this repository --
   writes through `Application.objects.update_or_create`, which never calls
   `full_clean`, so django-oauth-toolkit's own scheme check in
   `Application.clean` never ran on it. Tightening the setting alone would
   have changed nothing for the command.

Scope note, so this file is not read as more than it proves: the setting is
consulted at *registration* time only. At authorize time
`Application.redirect_uri_allowed` exact-matches the stored `redirect_uris`
string and does not re-check the scheme, so an http row already in the
database keeps working. Sweeping existing rows is a separate, data-side task.
"""
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings

from oauth2_provider.models import Application
from oauth2_provider.settings import oauth2_settings

from patient_portal.models import Identity


def _oauth2_provider_with(schemes):
    return {**dict(settings.OAUTH2_PROVIDER), 'ALLOWED_REDIRECT_URI_SCHEMES': schemes}


class AllowedRedirectSchemesSettingTest(SimpleTestCase):
    def test_project_setting_is_derived_from_debug(self):
        """The value in ctomop.settings is computed, not a hardcoded pair.

        Read from the settings module rather than from `django.conf.settings`,
        because the test runner forces `DEBUG = False` at run time while the
        module-level value is whatever the environment produced at import.
        """
        import ctomop.settings as project_settings

        schemes = project_settings.OAUTH2_PROVIDER['ALLOWED_REDIRECT_URI_SCHEMES']

        self.assertIn('https', schemes)
        if project_settings.DEBUG:
            self.assertEqual(schemes, ['https', 'http'])
        else:
            self.assertEqual(schemes, ['https'])


class CreateSmartAppSchemeTest(TestCase):
    """`create_smart_app` must honour the setting rather than bypass it."""

    def setUp(self):
        Identity.objects.create(
            issuer='urn:local',
            sub='smart-app-owner',
            email='smart-app-owner@example.invalid',
            is_staff=True,
        )
        self.addCleanup(oauth2_settings.reload)

    def test_http_redirect_is_refused_when_only_https_is_allowed(self):
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            oauth2_settings.reload()
            with self.assertRaises(CommandError) as caught:
                call_command(
                    'create_smart_app',
                    '--client-id', 'scheme-test-app',
                    '--redirect-uris', 'http://evil.example.invalid/callback',
                )

        self.assertIn('http://evil.example.invalid/callback', str(caught.exception))
        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app').exists(),
            'the Application must not be written when the scheme is refused',
        )

    def test_one_bad_uri_refuses_the_whole_registration(self):
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            oauth2_settings.reload()
            with self.assertRaises(CommandError):
                call_command(
                    'create_smart_app',
                    '--client-id', 'scheme-test-app-mixed',
                    '--redirect-uris',
                    'https://app.example.invalid/cb http://app.example.invalid/cb',
                )

        self.assertFalse(
            Application.objects.filter(client_id='scheme-test-app-mixed').exists()
        )

    def test_malformed_absolute_uri_is_refused(self):
        """`https:/app` has an https scheme and is still not a usable URI.

        A scheme-only comparison accepts it. Borrowing the toolkit's own
        validator is what makes the command refuse it, the same way the admin
        form does.
        """
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            oauth2_settings.reload()
            with self.assertRaises(CommandError):
                call_command(
                    'create_smart_app',
                    '--client-id', 'scheme-test-app-malformed',
                    '--redirect-uris', 'https:/app.example.invalid/callback',
                )

        self.assertFalse(
            Application.objects.filter(
                client_id='scheme-test-app-malformed'
            ).exists()
        )

    def test_scheme_relative_uri_is_refused(self):
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            oauth2_settings.reload()
            with self.assertRaises(CommandError):
                call_command(
                    'create_smart_app',
                    '--client-id', 'scheme-test-app-relative',
                    '--redirect-uris', '//app.example.invalid/callback',
                )

        self.assertFalse(
            Application.objects.filter(
                client_id='scheme-test-app-relative'
            ).exists()
        )

    def test_https_redirect_still_registers(self):
        with override_settings(OAUTH2_PROVIDER=_oauth2_provider_with(['https'])):
            oauth2_settings.reload()
            call_command(
                'create_smart_app',
                '--client-id', 'scheme-test-app-ok',
                '--redirect-uris', 'https://app.example.invalid/callback',
            )

        self.assertTrue(
            Application.objects.filter(client_id='scheme-test-app-ok').exists()
        )

    def test_http_still_registers_where_the_setting_allows_it(self):
        """Local dev keeps working -- the guard follows the setting, not DEBUG."""
        with override_settings(
            OAUTH2_PROVIDER=_oauth2_provider_with(['https', 'http'])
        ):
            oauth2_settings.reload()
            call_command(
                'create_smart_app',
                '--client-id', 'scheme-test-app-dev',
                '--redirect-uris', 'http://localhost:5173/auth/callback',
            )

        self.assertTrue(
            Application.objects.filter(client_id='scheme-test-app-dev').exists()
        )
