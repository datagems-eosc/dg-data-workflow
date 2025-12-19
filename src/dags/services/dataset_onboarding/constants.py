from datetime import date

from airflow.sdk import Param

DAG_ID = "DATASET_ONBOARDING"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type="string", format="uuid"),
    "code": Param(None, type=["null","string"]),
    "name": Param(None, type=["null","string"]),
    "description": Param(None, type=["null","string"]),
    "headline": Param(None, type=["null","string"]),
    "fields_of_science": Param(None, type=["null","array"]),
    "languages": Param(None, type=["null","array"]),
    "keywords": Param(None, type=["null","array"]),
    "countries": Param(None, type=["null","array"]),
    "publishedUrl": Param(None, type=["null","string"], format="uri"),
    "citeAs": Param(None, type=["null","string"]),
    "conformsTo": Param(None, type=["null","string"]),
    "license": Param(None, type=["null","string"]),
    "size": Param(type="integer", minimum=0),
    "dataLocations": Param([], type="string"),
    "version": Param(None, type=["null","string"]),
    "mime_type": Param(None, type=["null","string"]),
    "date_published": Param(f"{date.today()}", type=["null","string"], format="date"),
    "userId": Param(None, type=["null","string"])
}

DAG_TAGS = ["DatasetOnboarding", ]