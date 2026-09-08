"""Django system checks for patient_portal.

`redirect_uri_scheme_check` is registered with `deploy=True`, which means it
runs on `manage.py check --deploy` and on nothing else -- Django's own default
is `include_deployment_checks=False` (`core/management/base.py:486`), so
`migrate` and `collectstatic` never reach it. `start.sh` runs
`check --deploy --fail-level ERROR` before gunicorn; without that line this
module would be decoration, which is the failure mode #146 exists to fix.
"""
from urllib.parse import urlparse

from django.core.checks import Warning, register
from django.db import Error as DatabaseAccessError

# Numbering starts at W010 deliberately: `dev` already ships patient_portal
# checks E001-E003 and W005, and `cb` will eventually take them. Reusing a low
# number here would collide on that merge.
_SCHEME_WARNING_ID = 'patient_portal.W010'
_UNCHECKED_WARNING_ID = 'patient_portal.W011'

# The hint names offenders; cap it so one bad import cannot produce a
# thousand-line check output.
_MAX_REPORTED = 20


@register('security', deploy=True)
def redirect_uri_scheme_check(app_configs, **kwargs):
    """Name the Application rows that `ALLOWED_REDIRECT_URI_SCHEMES` will refuse.

    Tightening that setting is not only a registration-time change. At
    authorize time `AuthorizationView.redirect` (views/base.py:63-71) passes
    `application.get_allowed_schemes()` into `OAuth2ResponseRedirect`, whose
    `validate_redirect` (http.py:31-32) raises `DisallowedRedirect` -- HTTP 400
    -- for a scheme outside the list; RP-initiated logout does the same for
    `post_logout_redirect_uris` (views/oidc.py:458-465). A row written before
    the setting was tightened keeps matching -- `redirect_to_uri_allowed`
    compares the request's scheme against the stored one but never consults the
    allowlist -- and then fails at the response.

    So "sweep the rows before deploying" needs to be a condition something can
    observe, not a sentence in a comment: `render.yaml` sets `autoDeploy: true`,
    and nobody is necessarily watching (#146).
    """
    try:
        from oauth2_provider.models import get_application_model
    except ImportError:
        # `oauth2_provider` is a hard dependency, but a host that installs the
        # omop_* apps without it would otherwise crash `check` rather than skip.
        return []

    try:
        application_model = get_application_model()
    except LookupError:
        # Installed, but not in INSTALLED_APPS.
        return []

    # Same source the toolkit itself consults at redirect time, so a swappable
    # application model overriding `get_allowed_schemes` stays authoritative.
    allowed = {scheme.lower() for scheme in application_model().get_allowed_schemes()}

    redirect_offenders = []
    logout_offenders = []
    try:
        rows = application_model.objects.exclude(
            redirect_uris='', post_logout_redirect_uris=''
        ).values_list('client_id', 'redirect_uris', 'post_logout_redirect_uris')
        for client_id, redirect_uris, logout_uris in rows:
            for uris, bucket in (
                (redirect_uris, redirect_offenders),
                (logout_uris, logout_offenders),
            ):
                bad = sorted({
                    scheme for scheme in (
                        urlparse(uri).scheme.lower() for uri in uris.split()
                    )
                    if scheme not in allowed
                })
                if bad:
                    bucket.append(f'{client_id} ({", ".join(bad)})')
    except DatabaseAccessError as exc:
        # Reporting "nothing found" when the rows could not be read would turn a
        # missing answer into a green light -- the exact shape of failure this
        # check exists to prevent. Say so instead.
        return [
            Warning(
                'Could not check OAuth2 Application redirect URI schemes.',
                hint=(
                    'The rows were not read, so this is not a clean result. '
                    'Re-run once the database is reachable and migrated. '
                    'Underlying error: {}'.format(exc)
                ),
                id=_UNCHECKED_WARNING_ID,
            )
        ]

    if not redirect_offenders and not logout_offenders:
        return []

    parts = []
    if redirect_offenders:
        parts.append(
            'Authorization will fail with HTTP 400 at redirect time, after the '
            'grant has been minted, for: {}.'.format(_render(redirect_offenders))
        )
    if logout_offenders:
        parts.append(
            'RP-initiated logout will fail with HTTP 400 for: {}.'.format(
                _render(logout_offenders)
            )
        )
    parts.append('Allowed schemes: {}.'.format(', '.join(sorted(allowed))))

    return [
        Warning(
            'OAuth2 Application rows hold redirect URIs whose scheme is not in '
            'ALLOWED_REDIRECT_URI_SCHEMES.',
            hint=' '.join(parts),
            id=_SCHEME_WARNING_ID,
        )
    ]


def _render(offenders):
    shown = sorted(offenders)[:_MAX_REPORTED]
    remainder = len(offenders) - len(shown)
    rendered = '; '.join(shown)
    return f'{rendered} (and {remainder} more)' if remainder else rendered
