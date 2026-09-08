"""
Management command to bootstrap a SMART on FHIR OAuth2 Application.

Usage:
    python manage.py create_smart_app                    # local dev defaults
    python manage.py create_smart_app --name "My App" \\
        --redirect-uris "https://myapp.example.com/callback" \\
        --client-id my-client-id

The command is idempotent: running it again updates the existing record.

Redirect URIs are validated against `ALLOWED_REDIRECT_URI_SCHEMES` before this
command writes anything, so outside DEBUG only https is accepted and the http
default above works for local development only (#146). This guards this command
only; a direct ORM write elsewhere still bypasses it, exactly as it bypasses
`Application.clean`.
"""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from patient_portal.models import Identity


class Command(BaseCommand):
    help = 'Bootstrap a SMART on FHIR OAuth2 Application for the React SPA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            default='PRomop SMART App',
            help='Application name (default: "PRomop SMART App")',
        )
        parser.add_argument(
            '--client-id',
            default='promop-smart-app',
            dest='client_id',
            help='OAuth2 client_id (default: promop-smart-app)',
        )
        parser.add_argument(
            '--redirect-uris',
            default='http://localhost:3000/auth/callback',
            dest='redirect_uris',
            help='Space-separated list of allowed redirect URIs',
        )
        parser.add_argument(
            '--owner-username',
            default=None,
            dest='owner_username',
            help='Django username to own the app (defaults to first superuser)',
        )

    def handle(self, *args, **options):
        # Import here so the command can be imported before migrations run
        from oauth2_provider.models import get_application_model
        from oauth2_provider.settings import oauth2_settings
        from oauth2_provider.validators import AllowedURIValidator

        Application = get_application_model()

        name = options['name']
        client_id = options['client_id']
        redirect_uris = options['redirect_uris']

        # django-oauth-toolkit checks the redirect scheme in `Application.clean`,
        # which runs on every path that calls `full_clean` -- the admin and the
        # `/o/applications/register|<pk>/update/` views. It does NOT run here:
        # this command writes through `Application.objects.update_or_create`,
        # and neither `update_or_create` nor `Model.save` calls `full_clean`.
        # So the one path that registers redirect URIs here was the one path the
        # setting did not reach (#146). (`create_service_client` also writes via
        # `update_or_create`, but never sets `redirect_uris`, and
        # `/o/applications/register/` does run `full_clean`.)
        #
        # Borrow the toolkit's own validator, with the same arguments
        # `Application.clean` passes it, rather than hand-rolling a scheme
        # comparison: that way this command and the admin refuse the same
        # non-empty URIs, including the malformed-absolute (`https:/host`) and
        # wildcard-host forms that comparing schemes alone lets through. The
        # empty case is checked separately below, because `Application.clean`
        # rejects it through a different branch.
        allowed_schemes = {
            scheme.lower() for scheme in Application().get_allowed_schemes()
        }
        validate_redirect_uri = AllowedURIValidator(
            allowed_schemes,
            name='redirect uri',
            allow_path=True,
            allow_query=True,
            allow_hostname_wildcard=oauth2_settings.ALLOW_URI_WILDCARDS,
        )
        # `Application.clean` refuses an empty `redirect_uris` for the
        # authorization-code grant (models.py:229-234). The validator loop below
        # never sees an empty string, so without this the command would accept
        # what the admin refuses.
        if not redirect_uris.split():
            raise CommandError(
                '--redirect-uris cannot be empty for the authorization-code grant.'
            )

        for uri in redirect_uris.split():
            try:
                validate_redirect_uri(uri)
            except ValidationError as exc:
                raise CommandError(
                    '{}: {} (allowed schemes: {}).'.format(
                        uri, '; '.join(exc.messages), ', '.join(sorted(allowed_schemes))
                    )
                ) from exc

        # Resolve owner
        owner = None
        if options['owner_username']:
            try:
                owner = Identity.objects.get(email=options['owner_username'])
            except Identity.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f"User '{options['owner_username']}' not found."
                ))
                return
        else:
            owner = Identity.objects.filter(is_staff=True).first()
            if not owner:
                self.stderr.write(self.style.WARNING(
                    'No staff user found. Create one first with: manage.py createsuperuser (or set is_staff=True on an existing user)'
                ))
                return

        app, created = Application.objects.update_or_create(
            client_id=client_id,
            defaults={
                'name': name,
                'user': owner,
                'client_type': Application.CLIENT_PUBLIC,
                'authorization_grant_type': Application.GRANT_AUTHORIZATION_CODE,
                'redirect_uris': redirect_uris,
                # Public clients do not have a secret; PKCE is required instead
                'client_secret': '',
                'skip_authorization': False,
            },
        )

        verb = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f"{verb} SMART on FHIR application:\n"
            f"  Name:          {app.name}\n"
            f"  client_id:     {app.client_id}\n"
            f"  Redirect URIs: {app.redirect_uris}\n"
            f"  Client type:   {app.client_type} (PKCE required)\n"
            f"  Owner:         {owner.username}\n\n"
            f"Authorization URL: /o/authorize/\n"
            f"Token URL:         /o/token/\n"
        ))
