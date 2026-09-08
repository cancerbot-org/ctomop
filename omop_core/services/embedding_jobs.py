"""Run candidate embedding maintenance after vocabulary and mapping loads."""
from django.conf import settings
from django.core.management import call_command
from django.db import transaction


def dispatch_suggest_embeddings():
    """Use Celery when configured, and inline execution otherwise, after commit."""
    def run():
        if getattr(settings, 'CELERY_BROKER_URL', ''):
            from omop_core.tasks import precompute_suggest_embeddings_task

            precompute_suggest_embeddings_task.delay()
        else:
            call_command('precompute_suggest_embeddings')

    transaction.on_commit(run)
