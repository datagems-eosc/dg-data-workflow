import json
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from airflow.exceptions import AirflowSkipException
from airflow.sdk import get_current_context, Context

from services.logging import Logger

TASK_LOGS_XCOM_KEY = "task_logs"


def _make_json_serializable(value: Any) -> Any:
    if value is None:
        return None

    serialized = json.dumps(value, default=str, ensure_ascii=False, )
    return json.loads(serialized)


class XComTaskLogger:
    @property
    def context(self) -> Context:
        return self._context

    def __init__(self) -> None:
        self._logger = Logger()
        self._context = get_current_context()
        self._task_instance = self._context["ti"]
        self._task_id = self._context["task"].task_id
        existing_logs = self._task_instance.xcom_pull(task_ids=self._task_id, key=TASK_LOGS_XCOM_KEY, )
        self._records: list[dict[str, Any]] = list(existing_logs) if isinstance(existing_logs, list) else []

    def info_payload(self, message: str, payload: Any, *logger_args: Any, **logger_kwargs: Any, ) -> None:
        self._logger.info_payload(message, payload, *logger_args, **logger_kwargs, )
        self._append(level="INFO", message=message, payload=payload, )

    def error(self, message: str, payload: Any = None, ) -> None:
        self._logger.error(message)
        self._append(level="ERROR", message=message, payload=payload, )

    def exception(self, exception: Exception, message: str | None = None, ) -> None:
        error_message = message or str(exception) or type(exception).__name__
        self._logger.error(error_message)
        self._append(level="ERROR", message=error_message,
                     payload={
                         "exception_type": type(exception).__name__,
                         "exception_message": str(exception),
                         "traceback": traceback.format_exc(),
                     },
                     )

    def skipped(self, exception: AirflowSkipException) -> None:
        message = str(exception) or "Task skipped"
        self._logger.info_payload("task skipped", {"reason": message}, )
        self._append(level="SKIPPED", message=message, payload={
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        },
                     )

    def _append(self, level: str, message: str, payload: Any = None, ) -> None:
        task_instance = self._task_instance
        record = {
            "sequence": len(self._records) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "payload": _make_json_serializable(payload),
            "dag_id": getattr(task_instance, "dag_id", None),
            "task_id": self._task_id,
            "run_id": self._context.get("run_id"),
            "try_number": self._context.get(
                "try_number",
                getattr(task_instance, "try_number", None),
            ),
            "map_index": getattr(task_instance, "map_index", -1),
            "task_reschedule_count": self._context.get(
                "task_reschedule_count",
                0,
            ),
        }

        self._records.append(record)

        try:
            task_instance.xcom_push(key=TASK_LOGS_XCOM_KEY, value=self._records, )
        except Exception as xcom_exception:
            self._logger.error(f"Could not push task logs to XCom: {xcom_exception}")


@contextmanager
def xcom_task_logging() -> Iterator[XComTaskLogger]:
    log = XComTaskLogger()

    try:
        yield log
    except AirflowSkipException as exception:
        log.skipped(exception)
        raise
    except Exception as exception:
        log.exception(exception)
        raise
