from datetime import date

from airflow.sdk import Param

DAG_ID = "DATASET_ONBOARDING"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type="string", format="uuid"),
    "code": Param("", type="string"),
    "name": Param("", type="string"),
    "description": Param("", type="string"),
    "headline": Param("", type="string"),
    "fields_of_science": Param([], type="array"),
    "languages": Param([], type="array"),
    "keywords": Param([], type="array"),
    "countries": Param([], type="array"),
    "publishedUrl": Param("", type="string", format="uri"),
    "citeAs": Param("", type="string"),
    "conformsTo": Param("", type="string"),
    "license": Param("", type="string"),
    "size": Param(type="integer", minimum=0),
    "dataLocations": Param([], type="string"),
    "version": Param(type="string"),
    "mime_type": Param(type="string"),
    "date_published": Param(f"{date.today()}", type="string", format="date"),
    "userId": Param("", type="string")
}

DAG_TAGS = ["DatasetOnboarding", ]