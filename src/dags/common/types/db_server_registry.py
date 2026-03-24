from dataclasses import dataclass

@dataclass
class DbServerRegistry:
    name: str
    engine: str
    protocol: str
    host: str
    port: int
    datasets: list[str]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            engine=data["engine"],
            protocol=data["protocol"],
            host=data["host"],
            port=data["port"],
            datasets=data["datasets"]
        )