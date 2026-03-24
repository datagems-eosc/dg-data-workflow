from airflow.sdk import Variable

from common.types import DbServerRegistry


class DbServerRegistryConfig:
    def __init__(self):
        options = Variable.get("db_server_registry", deserialize_json=True)
        self.instances: list[DbServerRegistry] = [DbServerRegistry.from_dict(instance) for instance in
                                                  options["instances"]]
        self.default_instance: str = options["defaultInstance"]
