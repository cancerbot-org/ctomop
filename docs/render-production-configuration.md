# Render production configuration

Django combines `ALLOWED_HOSTS` (a comma-separated list of custom domains) with
Render's automatically supplied `RENDER_EXTERNAL_HOSTNAME`. A service using its
Render hostname can boot without a dashboard `ALLOWED_HOSTS` value. Custom
domains still need an explicit entry. This does not enable wildcard hosts.

For an **existing** Blueprint service, `sync: false` does not add a value or
prompt again during updates. Set missing values on the service's Environment
page. In particular, `CORS_ALLOWED_ORIGINS` must contain the frontend origins;
Render's backend hostname does not determine which external frontends to trust.

`start.sh` runs `check --deploy --fail-level ERROR` before migrations. This check
now applies the same production settings guard as the web process and the
Athena loader, so missing runtime configuration stops deployment before database
work. Build-time `collectstatic`, ordinary `check`, and standalone `migrate`
retain their existing import exemptions.

An Athena startup traceback beginning with `KeyError:
'load_athena_vocabularies'` can be command discovery failing to import settings.
Read the final exception: `Missing required production settings` means the
configuration must be fixed, not that the loader command needs reinstalling.
OpenAPI schema warnings earlier in the log do not cause a deployment using
`--fail-level ERROR` to fail.

Render references: [Blueprint environment variables](https://render.com/docs/blueprint-spec#setting-environment-variables)
and [default environment variables](https://render.com/docs/environment-variables).
