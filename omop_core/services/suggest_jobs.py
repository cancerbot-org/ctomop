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

# What a run may attempt when it is genuinely queued: bounded by
# CELERY_TASK_TIME_LIMIT (900s default) against ~3.5s per code, with wide margin.
QUEUED_MAX_CODES = 50

# What it may attempt when there is no broker and the "queue" is the request
# thread. Deliberately far smaller: `render.yaml` leaves CELERY_BROKER_URL
# dashboard-managed on the web service (`sync: false`), so a deployment that has
# not pasted the Redis URL in yet falls back to inline — and inline runs under
# `start.sh`'s bare gunicorn, whose default timeout is 30s. Fifty codes inline is
# 125s of serial retrieval and a 502: the exact failure this work removes.
# Measured: 5 codes 24.1s, 8 codes 28.7s.
INLINE_MAX_CODES = 5


class SuggestDispatcher(Protocol):
    #: Ceiling on the codes one run may attempt under this dispatcher.
    max_codes: int

    def dispatch(self, run: SuggestRun, params: dict) -> None:
        """Arrange for *run* to be executed."""


class CeleryDispatcher:
    """Queues the run on a worker."""

    max_codes = QUEUED_MAX_CODES

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

    It also gets a much smaller ceiling, because "inline" means "inside the
    request" and the request has a timeout. See INLINE_MAX_CODES.
    """

    max_codes = INLINE_MAX_CODES

    def dispatch(self, run: SuggestRun, params: dict) -> None:
        execute_run(str(run.id), params)


class FakeDispatcher:
    """Records what it was asked to run, runs nothing. For tests."""

    max_codes = QUEUED_MAX_CODES

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

    # The denominator the page was given in the 202, and the budget for the run.
    # Both have to span the tables, not repeat per table: a source vocabulary can
    # map to five clinical tables, and a per-table limit would let one run
    # attempt five times its own ceiling.
    budget = params['limit']
    total = run.total

    # Progress is reported across the whole run: the page shows one bar, and
    # `done` must never overtake a denominator the view already published.
    completed = {'retrieved': 0, 'written': 0}

    def make_progress(base):
        def progress(stage, done, _table_total):
            if stage == 'retrieving':
                completed['retrieved'] = base[0] + done
                SuggestRun.objects.filter(pk=run.pk).update(
                    retrieved=min(completed['retrieved'], total) if total else completed['retrieved'],
                )
            else:
                completed['written'] = base[0] + done
                SuggestRun.objects.filter(pk=run.pk).update(
                    done=min(completed['written'], total) if total else completed['written'],
                )
        return progress

    results = []
    seen = [0]
    try:
        for table in tables:
            if budget <= 0:
                break
            table_results = suggest_mappings(
                table,
                min_occurrences=params['min_occurrences'],
                limit=budget,
                dry_run=params['dry_run'],
                source_vocabulary_id=params['source_vocabulary_id'],
                strategies=params['strategies'],
                lexical_limit=params['lexical_limit'],
                resuggest=params['resuggest'],
                progress=make_progress(seen),
            )
            results.extend(table_results)
            seen[0] += len(table_results)
            budget -= len(table_results)
    except Exception as exc:                      # noqa: BLE001 - record, never crash the worker
        SuggestRun.objects.filter(pk=run.pk).update(
            state=SuggestRun.FAILURE, error=str(exc)[:2000],
            finished_at=timezone.now(),
        )
        return

    landed: dict[str, int] = {}
    strategy_counts: dict[str, int] = {}
    for entry in results:
        # Only rows that actually got a destination. `updated` means the row was
        # written -- which includes recording that the ranker declined -- so
        # counting that here would claim destinations nobody proposed.
        suggested = entry.get('suggested')
        if entry.get('updated') and suggested:
            vocab = suggested['vocabulary_id'] or (params['source_vocabulary_id'] or '')
            landed[vocab] = landed.get(vocab, 0) + 1
        strategy = entry.get('strategy_used')
        if strategy:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

    SuggestRun.objects.filter(pk=run.pk).update(
        state=SuggestRun.SUCCESS,
        total=len(results),
        retrieved=len(results),
        done=len(results),
        destinations=sum(1 for r in results if r.get('updated') and r.get('suggested')),
        strategy_counts=strategy_counts,
        landed_in=landed,
        finished_at=timezone.now(),
    )
