"""How a Code Mapping Suggest run gets executed.

A Suggest click costs ~3.5s per code and a tab holds dozens, so the synchronous
version could not finish inside a gunicorn worker's timeout — production's
``start.sh`` runs bare gunicorn, whose default is 30s. It is queued instead, and
the page polls a :class:`~omop_core.models.SuggestRun` row for progress.

The seam sits here rather than in the view, so a test can run the work without a
broker and without reaching into Celery. It deliberately mirrors
``omop_core/services/derivation_jobs.py``: same choice rule (Celery when a
broker is configured, inline otherwise), same reason for having no separate
setting — two settings that can disagree leave every job queued with nothing
consuming it.

Where this differs from derivation: the outcome is a database row, not a signed
id. Derivation only has to answer "did it finish", which an id issued after the
fact can encode. A Suggest run has to answer "how far has it got" *while it is
still running*, from whichever gunicorn worker the poll lands on, so the state
has to be somewhere both the runner and every poller can see.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Protocol

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from omop_core.models import SuggestRun

# How often the runner writes its progress back. Every code would be one UPDATE
# per ~3.5s of work, which is cheap, but the writing phase can move much faster
# than that and the page only polls every second or so.
PROGRESS_EVERY = 1


class SuggestDispatcher(Protocol):
    def dispatch(self, run: SuggestRun, params: dict) -> None:
        """Arrange for *run* to be executed."""


class CeleryDispatcher:
    """Queues the run on a worker."""

    def dispatch(self, run: SuggestRun, params: dict) -> None:
        from omop_core.tasks import suggest_mappings_task

        run_id = str(run.id)
        # Deferred to commit: a worker that starts inside the caller's open
        # transaction cannot see the SuggestRun row the caller just created and
        # fails looking it up.
        transaction.on_commit(
            lambda: suggest_mappings_task.apply_async(args=[run_id, params])
        )


class InlineDispatcher:
    """Runs it in the calling thread. What a machine with no broker gets.

    The wire contract is identical — the caller still gets a run id and still
    polls — so the page needs one code path either way. What it does not get is
    progress: the row goes from queued to success in one step, because nothing
    is reading it while the request is blocked.
    """

    def dispatch(self, run: SuggestRun, params: dict) -> None:
        execute_run(str(run.id), params)


class FakeDispatcher:
    """Records what it was asked to run, runs nothing. For tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def dispatch(self, run: SuggestRun, params: dict) -> None:
        self.calls.append((str(run.id), params))


_celery = CeleryDispatcher()
_inline = InlineDispatcher()
_override: SuggestDispatcher | None = None


def get_dispatcher() -> SuggestDispatcher:
    """Celery when a broker is configured, inline otherwise."""
    if _override is not None:
        return _override
    return _celery if getattr(settings, 'CELERY_BROKER_URL', '') else _inline


@contextmanager
def use_dispatcher(dispatcher: SuggestDispatcher) -> Iterator[SuggestDispatcher]:
    """Swap the dispatcher for the duration of a test."""
    global _override
    previous = _override
    _override = dispatcher
    try:
        yield dispatcher
    finally:
        _override = previous


def execute_run(run_id: str, params: dict) -> None:
    """Do the work for one SuggestRun and record how it went.

    Never raises: a failure belongs on the row, where the page is already
    looking, rather than in a worker log the curator cannot see.
    """
    from omop_core.mapping.suggestions import SUGGESTION_MODEL_VERSION, suggest_mappings

    run = SuggestRun.objects.filter(pk=run_id).first()
    if run is None:
        return

    SuggestRun.objects.filter(pk=run.pk).update(
        state=SuggestRun.RUNNING, model_version=SUGGESTION_MODEL_VERSION,
    )

    tables = params.get('tables') or []
    # Progress is reported across the whole run, not per table: the page shows
    # one bar and a tab can map to several clinical tables.
    offsets = {'retrieved': 0, 'done': 0, 'total': 0}

    def make_progress(table_total_seen):
        def progress(stage, done, total):
            if total and offsets['total'] < table_total_seen[0] + total:
                offsets['total'] = table_total_seen[0] + total
            field = 'retrieved' if stage == 'retrieving' else 'done'
            value = table_total_seen[0] + done
            if stage == 'writing':
                # Retrieval is finished for this table by the time writing
                # starts, so pin it rather than letting the bar go backwards.
                SuggestRun.objects.filter(pk=run.pk).update(
                    retrieved=offsets['total'], done=value, total=offsets['total'],
                )
            else:
                SuggestRun.objects.filter(pk=run.pk).update(
                    retrieved=value, total=offsets['total'],
                )
        return progress

    results = []
    seen = [0]
    try:
        for table in tables:
            table_results = suggest_mappings(
                table,
                min_occurrences=params['min_occurrences'],
                limit=params['limit'],
                dry_run=params['dry_run'],
                source_vocabulary_id=params['source_vocabulary_id'],
                strategies=params['strategies'],
                lexical_limit=params['lexical_limit'],
                resuggest=params['resuggest'],
                progress=make_progress(seen),
            )
            results.extend(table_results)
            seen[0] += len(table_results)
    except Exception as exc:                      # noqa: BLE001 - record, never crash the worker
        SuggestRun.objects.filter(pk=run.pk).update(
            state=SuggestRun.FAILURE, error=str(exc)[:2000],
            finished_at=timezone.now(),
        )
        return

    landed: dict[str, int] = {}
    strategy_counts: dict[str, int] = {}
    for entry in results:
        if entry.get('updated'):
            suggested = entry.get('suggested')
            vocab = (
                suggested['vocabulary_id'] if suggested
                else (params['source_vocabulary_id'] or '')
            )
            landed[vocab] = landed.get(vocab, 0) + 1
        strategy = entry.get('strategy_used')
        if strategy:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

    SuggestRun.objects.filter(pk=run.pk).update(
        state=SuggestRun.SUCCESS,
        total=len(results),
        retrieved=len(results),
        done=len(results),
        updated=sum(1 for r in results if r.get('updated')),
        ranked=sum(1 for r in results if r.get('suggested')),
        strategy_counts=strategy_counts,
        landed_in=landed,
        finished_at=timezone.now(),
    )
