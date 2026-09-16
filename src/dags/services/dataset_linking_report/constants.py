from airflow.sdk import Param

from configurations import DatasetLinkingConfig

DAG_ID = "DATASET_LINKING_REPORT"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
    "workflow_process_step_information": Param(type="object")
}

DAG_TAGS = ["DatasetLinkingReport", ]

WAIT_FOR_COMPLETION_POKE_INTERVAL = DatasetLinkingConfig().options.report_poke_interval