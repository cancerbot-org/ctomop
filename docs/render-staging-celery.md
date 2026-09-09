# Render staging Celery

Suggest supports 50 codes when the web service has `CELERY_BROKER_URL` set.
Without it, the API deliberately limits synchronous requests to 3 codes.
Changing the number in the UI cannot enable background execution.

## Staging Blueprint

First identify the **existing** staging web service name and region in Render.
Do not use the production `render.yaml` to provision staging: it tracks `main`
and declares a database. Generate a staging-specific Blueprint using the actual
service identity (the arguments below are examples, not discovered resources):

```sh
python scripts/render_staging_blueprint.py \
  --web-service EXISTING-STAGING-NAME --region oregon > render.staging.yaml
```

The generated file tracks `dev`, adds a worker and a private Key Value broker,
and wires both web and worker to that broker. It reuses the web service's
existing `DATABASE_URL`, `SECRET_KEY`, `AUDIT_HMAC_KEY`, `EXPORT_SIGNING_KEY`,
and `ANTHROPIC_API_KEY`; it does not create a database or rotate signing keys.
Local staging database access uses `STAGING_DATABASE_URL` in `.env`; Render
processes use the existing web service's `DATABASE_URL` for that same database.
No secret values belong in the generated file or the repository.

The worker uses a 2 GB plan (`1c-2g`) with concurrency 1 and prefetch 1. This
avoids four processes independently loading the embedding model; it is not a
claim that the reported 2 GB memory failure has been diagnosed. The broker is
256 MB with `noeviction` so memory pressure cannot silently evict queued jobs.
These are additional paid Render resources. Measure worker memory on the real
vocabulary workload before increasing concurrency.

Review the generated web build/start commands against the existing service's
commands. If it already belongs to a Blueprint, incorporate these definitions
into that Blueprint instead of attaching it to a second one. Otherwise, commit
the generated file and configure Render to sync that path. The generator alone
and a normal code deployment do **not** sync infrastructure.

Keep all three services in the existing staging region/workspace/environment.
The generated configuration explicitly sets `CELERY_RESULT_BACKEND` to the
same broker on both services, replacing any stale override. If it has `CACHE_URL`, preserve it; otherwise Django uses the broker
for its shared cache. Any additional worker task credentials configured on the
web service must also be supplied to the worker.

Start the worker and verify its logs show it connected to the staging broker
and registered `omop_core.suggest_mappings`. Then activate the broker on the
web service and redeploy it. For dashboard-managed services, create the worker
and Key Value service using the generated definitions, and set the web's
`CELERY_BROKER_URL` to that Key Value service's internal connection string.
Worker secrets must match the existing web values.

## Verify live behavior

- The worker must respond to `celery -A ctomop inspect ping` from the Render shell.
- Authenticated `/api/v1/code-mappings/reference/` must return
  `suggest_max_per_run: 50`.
- Run Suggest on a curator-approved queue, and confirm the web request returns
  202 promptly, the worker receives the task, and the progress endpoint reaches
  success. A displayed 50 alone proves broker configuration, not worker health.
- Check web and worker memory metrics during that run. Do not run the full test
  suite against staging.

A rollback clears the web service's broker URL (and any explicit result backend
pointing at it) to restore inline execution. Drain running jobs before stopping
the worker; keep the broker until queued work is accounted for.

Local integration coverage in `tests/test_celery_e2e.py` uses isolated PostgreSQL
and Redis and a real Celery process. It verifies a 50-code Suggest run completes
without external model API calls, as well as asynchronous patient derivation.

Render reference: https://render.com/docs/blueprint-spec
