import json
from typing import Optional, Any

from airflow.sdk import Variable
from airflow.sdk.execution_time.secrets_masker import mask_secret


def get(key: str, default: Optional[Any] = None, mask: bool = False, composite: bool = False) -> Any:
    raw = Variable.get(key, default)
    value = raw
    if composite:
        value = json.loads(raw)
    if mask and value:
        return mask_secret(value)
    return value
