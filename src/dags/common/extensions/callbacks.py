from typing import Any

from airflow.sdk import Context

from authorization.gateway_auth import GatewayAuthService
from common.enum import WorkflowProcessStepExecutionStatus
from common.extensions.http_requests import http_post
from common.extensions.xcom_logging import TASK_LOGS_XCOM_KEY
from configurations import GatewayConfig


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
    config = GatewayConfig()
    auth = GatewayAuthService()
    url: str = config.options.base_url + config.options.endpoints.process_step_update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth.get_token()}",
               "Connection": "keep-alive"}
    payload = {
        "Id": context["params"]["workflow_process_step_information"]["id"],
        "ProcessId": context["params"]["workflow_process_step_information"]["process_id"],
        "StepId": context["params"]["workflow_process_step_information"]["step_id"],
        "WorkflowTaskInstanceDetails": build_callback_payload(context, "execute"),
        "Status": WorkflowProcessStepExecutionStatus.InProgress.value
    }
    _ = http_post(url=url, headers=headers, data=payload)


def on_retry_callback(context) -> None:
    config = GatewayConfig()
    auth = GatewayAuthService()
    url: str = config.options.base_url + config.options.endpoints.process_step_update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth.get_token()}",
               "Connection": "keep-alive"}
    payload = {
        "Id": context["params"]["workflow_process_step_information"]["id"],
        "ProcessId": context["params"]["workflow_process_step_information"]["process_id"],
        "StepId": context["params"]["workflow_process_step_information"]["step_id"],
        "WorkflowTaskInstanceDetails": build_callback_payload(context, "retry"),
        "Status": WorkflowProcessStepExecutionStatus.InProgress.value
    }
    _ = http_post(url=url, headers=headers, data=payload)


def on_success_callback(context) -> None:
    config = GatewayConfig()
    auth = GatewayAuthService()
    url: str = config.options.base_url + config.options.endpoints.process_step_update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth.get_token()}",
               "Connection": "keep-alive"}
    payload = {
        "Id": context["params"]["workflow_process_step_information"]["id"],
        "ProcessId": context["params"]["workflow_process_step_information"]["process_id"],
        "StepId": context["params"]["workflow_process_step_information"]["step_id"],
        "WorkflowTaskInstanceDetails": build_callback_payload(context, "success"),
        "Status": WorkflowProcessStepExecutionStatus.InProgress.value
    }
    _ = http_post(url=url, headers=headers, data=payload)


def on_failure_callback(context) -> None:
    config = GatewayConfig()
    auth = GatewayAuthService()
    url: str = config.options.base_url + config.options.endpoints.process_step_update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth.get_token()}",
               "Connection": "keep-alive"}
    payload = {
        "Id": context["params"]["workflow_process_step_information"]["id"],
        "ProcessId": context["params"]["workflow_process_step_information"]["process_id"],
        "StepId": context["params"]["workflow_process_step_information"]["step_id"],
        "WorkflowTaskInstanceDetails": build_callback_payload(context, "failure"),
        "Status": WorkflowProcessStepExecutionStatus.Failed.value
    }
    _ = http_post(url=url, headers=headers, data=payload)


def on_skipped_callback(context) -> None:
    config = GatewayConfig()
    auth = GatewayAuthService()
    url: str = config.options.base_url + config.options.endpoints.process_step_update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth.get_token()}",
               "Connection": "keep-alive"}
    payload = {
        "Id": context["params"]["workflow_process_step_information"]["id"],
        "ProcessId": context["params"]["workflow_process_step_information"]["process_id"],
        "StepId": context["params"]["workflow_process_step_information"]["step_id"],
        "WorkflowTaskInstanceDetails": build_callback_payload(context, "skipped"),
        "Status": WorkflowProcessStepExecutionStatus.InProgress.value
    }
    _ = http_post(url=url, headers=headers, data=payload)
