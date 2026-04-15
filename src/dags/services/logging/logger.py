import json
import logging

from airflow.sdk import get_current_context, Context


class Logger:
    """
    Centralised logging service. Uses Python logging module to emit messages that will appear in the task logs.
    """

    def __init__(self, context: Context | None = None):
        if context is None:
            ctx = get_current_context()
        else:
            ctx = context
        self.ti = ctx["ti"]
        self.dag_id = self.ti.dag_id
        self.task_id = self.ti.task_id
        self.logger = logging.getLogger(f"{self.dag_id}.{self.task_id}")

    def info_payload(self, message: str, payload, serialize: bool = False) -> None:
        serialized = payload
        if serialize:
            serialized = json.dumps(payload)
        self.info(f"message\n{serialized}\n")

    def info(self, message: str) -> None:
        self.logger.info(self._format(message))

    def warning(self, message: str) -> None:
        self.logger.warning(self._format(message))

    def error(self, message: str) -> None:
        self.logger.error(self._format(message))

    def _format(self, message: str) -> str:
        # enrich return value for extra formatting
        return message
