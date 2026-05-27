from airflow.sdk import Param

from configurations import DatasetDiscoveryConfig

DAG_ID = "CDD_INGEST"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
}

DAG_TAGS = ["CDD_Ingest", ]

MINUTES_TIMEDELTA = 10

WAIT_FOR_COMPLETION_POKE_INTERVAL = DatasetDiscoveryConfig().options.poke_interval