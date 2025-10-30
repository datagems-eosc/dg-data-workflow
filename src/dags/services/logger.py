import logging

from airflow.sdk import get_current_context


class Logger:
    """
    Centralised logging service. Uses Python logging module to emit messages that will appear in the task logs.
    """

    def __init__(self):
        ctx = get_current_context()
        self.ti = ctx["ti"]
        self.dag_id = self.ti.dag_id
        self.task_id = self.ti.task_id
        self.logger = logging.getLogger(f"{self.dag_id}.{self.task_id}")

    def info(self, message: str):
        self.logger.info(self._format(message))

    def warning(self, message: str):
        self.logger.warning(self._format(message))

    def error(self, message: str):
        self.logger.error(self._format(message))

    def _format(self, message: str) -> str:
        # enrich return value for extra formatting
        return message
