from airflow.sdk import Param

DAG_ID = "STREAMING_INTERVAL_PROFILING"

DAG_PARAMS = {
    "dataset_id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
}

DAG_TAGS = ["STREAMING_INTERVAL_PROFILING", ]

MINUTES_TIMEDELTA = 60
