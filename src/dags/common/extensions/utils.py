from typing import Any


def normalize_keys(obj: Any):
    """Recursively remove leading '@' from dict keys."""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            k2 = k[1:] if isinstance(k, str) and k.startswith("@") else k
            new[k2] = normalize_keys(v)
        return new
    elif isinstance(obj, list):
        return [normalize_keys(x) for x in obj]
    else:
        return obj
