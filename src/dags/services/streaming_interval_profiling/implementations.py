from airflow.sdk import Context

from configurations import StreamingIntervalProfilerConfig


def fetch_weather_builder(config: StreamingIntervalProfilerConfig, dag_context: Context, auth_token: str):
    url: str = config.options.base_url + config.options.endpoints.profile
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    body = {
        "dataset_id": dag_context["params"]["dataset_id"]
    }
    return url, headers, body
