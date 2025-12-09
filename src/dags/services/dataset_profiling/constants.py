from datetime import date

from airflow.sdk import Param

from common.enum import DataStoreKind
from configurations import ProfilerConfig

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
    "version": Param("", type="string"),
    "headline": Param("", type="string"),
    "keywords": Param([], type="array"),
    "fields_of_science": Param([], type="array"),
    "languages": Param([], type="array"),
    "countries": Param([], type="array"),
    "date_published": Param(f"{date.today()}", type="string", format="date"),
    "dataset_file_path": Param("", type="string"),
    "userId": Param("", type="string"),
    "citeAs": Param("", type="string"),
    "conformsTo": Param("", type="string"),
    "data_store_kind": Param(DataStoreKind.FileSystem.value, type="integer", enum=[c.value for c in DataStoreKind]),
}

DAG_TAGS = ["DatasetProfiling", ]

WAIT_FOR_COMPLETION_POKE_INTERVAL = ProfilerConfig().options.profiler.poke_interval
