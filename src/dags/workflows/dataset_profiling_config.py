from airflow.models.param import Param
from airflow.sdk import Context

from configurations.dataset_profiler_config import ProfilerConfig

DAG_ID = "DATASET_PROFILING"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type="string", format="uuid"),
    "code": Param("", type="string"),
    "name": Param("", type="string"),
    "description": Param("", type="string"),
    "license": Param("", type="string"),
    "mime_type": Param("", type="string"),
    "size": Param(0, type="integer", minimum=0),
    "url": Param("", type="string", format="uri"),
    "version": Param("v1", type="string"),
    "headline": Param("", type="string"),
    "keywords": Param([], type="array"),
    "fields_of_science": Param([], type="array"),
    "languages": Param([], type="array"),
    "countries": Param([], type="array"),
    "date_published": Param("", type="string"),
}

DAG_TAGS = ["DatasetProfiling", ]


def config_profiling(auth_token: str, dag_context: Context, config: ProfilerConfig):
    profiler_url = config.options.base_url + config.options.profiler.trigger_profile + "/" + dag_context["params"]["id"]
    payload = {

    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return profiler_url, headers, payload
