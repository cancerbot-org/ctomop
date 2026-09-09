"""Service credentials must obey method scopes across every permission variant."""
from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.test import override_settings
from django.utils import timezone

from patient_portal.api.permissions import (
    SERVICE_TOKEN,
    LabSyncPermission,
    PatientCrudPermission,
    PatientDeletePermission,
    ScopedTokenPermission,
    VocabReadPermission,
)
from patient_portal.api.providers.base import TokenClaims


PERMISSIONS = (
    ScopedTokenPermission, VocabReadPermission, LabSyncPermission,
    PatientCrudPermission, PatientDeletePermission,
)
METHODS = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE')


@pytest.mark.parametrize('permission_class', PERMISSIONS)
@pytest.mark.parametrize('method', METHODS)
@pytest.mark.parametrize('scope,allowed_methods', (
    ('', ()),
    ('openid patient/Observation.read', ()),
    ('patient/*.read', ('GET', 'HEAD', 'OPTIONS')),
    ('user/*.read', ('GET', 'HEAD', 'OPTIONS')),
    ('patient/*.write', ('POST', 'PUT', 'PATCH', 'DELETE')),
    ('user/*.write', ('POST', 'PUT', 'PATCH', 'DELETE')),
    ('  patient/*.read\tpatient/*.write  ', METHODS),
    ('system/*.read', ('GET', 'HEAD', 'OPTIONS')),
))
def test_service_scopes(permission_class, method, scope, allowed_methods):
    # Staff status must not turn a scoped credential into unrestricted access.
    request = SimpleNamespace(
        auth=SERVICE_TOKEN, method=method,
        user=SimpleNamespace(is_authenticated=True, is_staff=True),
    )
    allowed = method in allowed_methods
    if scope == 'system/*.read' and permission_class is not VocabReadPermission:
        allowed = False
    with override_settings(SERVICE_AUTH_SCOPES=scope):
        assert permission_class().has_permission(request, None) is allowed


@pytest.mark.parametrize('permission_class', PERMISSIONS)
@pytest.mark.parametrize('method', METHODS)
def test_service_token_without_scopes_has_staff_rights(permission_class, method):
    # No SERVICE_AUTH_SCOPES set: the token is a backend service acting as
    # staff, so every method is allowed.
    request = SimpleNamespace(
        auth=SERVICE_TOKEN, method=method,
        user=SimpleNamespace(is_authenticated=True, is_staff=True),
    )
    with override_settings(SERVICE_AUTH_SCOPES=None):
        assert permission_class().has_permission(request, None) is True


@pytest.mark.parametrize('permission_class', PERMISSIONS)
@pytest.mark.parametrize('scope,method,expired,allowed', (
    ('patient/*.read', 'DELETE', False, False),
    ('patient/*.write', 'DELETE', False, True),
    ('patient/*.write', 'DELETE', True, False),
    ('patient/*.read', 'GET', True, False),
    ('system/*.read', 'GET', False, True),
    ('system/*.read', 'GET', True, False),
))
def test_oauth_scopes(permission_class, scope, method, expired, allowed):
    token = SimpleNamespace(
        scope=scope, expires=timezone.now() + timedelta(hours=-1 if expired else 1),
    )
    request = SimpleNamespace(
        auth=token, method=method,
        user=SimpleNamespace(is_authenticated=True, is_staff=True),
    )
    if scope == 'system/*.read' and permission_class is not VocabReadPermission:
        allowed = False
    assert permission_class().has_permission(request, None) is allowed


@pytest.mark.parametrize('auth', (
    None, TokenClaims(issuer='test', sub='patient', email='', name='', raw={}),
))
@pytest.mark.parametrize('authenticated', (True, False))
def test_patient_delete_exception_remains_for_end_users(auth, authenticated):
    request = SimpleNamespace(
        auth=auth, method='DELETE',
        user=SimpleNamespace(is_authenticated=authenticated, is_staff=False),
    )
    assert PatientDeletePermission().has_permission(request, None) is authenticated
