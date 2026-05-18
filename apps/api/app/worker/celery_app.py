"""Celery worker entrypoint. Bound to Redis (queue + backend).

Tasks live in `app.worker.tasks.*` and are autodiscovered. Master Spec §4.4
mandates real/fixture mode on every LLM call — `SHIELD_LLM_MODE=fixture`
makes worker tasks read from `apps/api/tests/fixtures/llm/` instead of
issuing live calls.
"""

from __future__ import annotations

from celery import Celery

from app.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "shield",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        # Task modules will be enabled as services land.
        # "app.worker.tasks.extract_capability_list",
        # "app.worker.tasks.score_zt_question",
        # "app.worker.tasks.propose_csf_narrative",
        # "app.worker.tasks.analyze_attack_coverage",
    ],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=30,
    task_max_retries=3,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="shield.ping")
def ping() -> str:
    """Smoke task — confirms the worker is reachable."""
    return "pong"
