from typing import Any

from airflow.sdk import Context

from common.extensions.xcom_logging import TASK_LOGS_XCOM_KEY
from services.logging import Logger


def pull_task_logs(context: dict[str, Any]) -> list[dict[str, Any]]:
    records = context["ti"].xcom_pull(
        task_ids=context["task"].task_id,
        key=TASK_LOGS_XCOM_KEY,
    )
    return records if isinstance(records, list) else []


def build_callback_payload(context: Context, event: str,) -> dict[str, Any]:
    task = context["task"]
    task_instance = context["ti"]
    exception = context.get("exception")

    return {
        "event": event,
        "dag_id": getattr(task_instance, "dag_id", None),
        "task_id": task.task_id,
        "run_id": context.get("run_id"),
        "try_number": context.get(
            "try_number",
            getattr(task_instance, "try_number", None),
        ),
        "map_index": getattr(task_instance, "map_index", -1),
        "exception": (
            {
                "type": type(exception).__name__,
                "message": str(exception),
            }
            if exception is not None
            else None
        ),
        "logs": pull_task_logs(context),
    }


def on_execute_callback(context) -> None:
    payload = build_callback_payload(context, "execute")


def on_retry_callback(context) -> None:
    payload = build_callback_payload(context, "retry")


def on_success_callback(context) -> None:
    payload = build_callback_payload(context, "success")


def on_failure_callback(context) -> None:
    payload = build_callback_payload(context, "failure")


def on_skipped_callback(context) -> None:
    payload = build_callback_payload(context, "skipped")
