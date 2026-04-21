from airflow.sdk import Param

DAG_ID = "DATASET_PACKAGING"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
}

DAG_TAGS = ["DatasetPackaging", ]