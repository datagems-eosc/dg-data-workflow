from datetime import date

from airflow.sdk import Param

from common.enum import DataStoreKind
from configurations import ProfilerConfig

DAG_ID = "DATASET_PROFILING"
DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
    "code": Param(None, type=["null","string"]),
    "name": Param(None, type=["null","string"]),
    "description": Param(None, type=["null","string"]),
    "license": Param(None, type=["null","string"]),
    "mime_type": Param(None, type=["null","string"]),
    "size": Param(None, type=["null","integer"], minimum=0),
    "url": Param(None, type=["null","string"], format="uri"),
    "version": Param(None, type=["null","string"]),
    "headline": Param(None, type=["null","string"]),
    "keywords": Param(None, type=["null","array"]),
    "fields_of_science": Param(None, type=["null","array"]),
    "languages": Param(None, type=["null","array"]),
    "countries": Param(None, type=["null","array"]),
    "date_published": Param(f"{date.today()}", type=["null","string"], format="date"),
    "dataset_file_path": Param("", type=["string"]),
    "userId": Param(None, type=["null","string"]),
    "citeAs": Param(None, type=["null","string"]),
    "conformsTo": Param(None, type=["null","string"]),
    "data_store_kind": Param(DataStoreKind.FileSystem.value, type="integer", enum=[c.value for c in DataStoreKind]),
    "archivedAt": Param(None, type=["null","string"]),
    "doi": Param(None, type=["null", "string"]),
    "database_name": Param(None, type=["null", "string"])
}

DAG_TAGS = ["DatasetProfiling", ]

WAIT_FOR_COMPLETION_POKE_INTERVAL = ProfilerConfig().options.profiler.poke_interval
