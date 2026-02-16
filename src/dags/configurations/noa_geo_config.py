from airflow.sdk import Variable


class NoaGeoConfig:
    class NoaGeoCoreConfig:
        class Endpoints:
            def __init__(self, data: dict):
                self.geojson = data["geo_json"]

        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.endpoints = self.Endpoints(data.get("endpoints"))

    def __init__(self):
        self.options = self.NoaGeoCoreConfig(
            Variable.get("noa_geo", deserialize_json=True))
