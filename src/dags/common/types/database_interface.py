from typing import Dict, List, Tuple


class DatabaseInterface:
    """Abstract interface for database operations."""

    def insert_station(self, station_id: str, info: Dict) -> bool: raise NotImplementedError

    def insert_observations_batch(self, observations: List[Tuple]) -> int: raise NotImplementedError

    def log_collection(self, status: str, stations_count: int, obs_count: int,
                       message: str = ""): raise NotImplementedError

    def get_station_window(self, station_id: str, window_size: int = 6) -> List[Dict]: raise NotImplementedError

    def get_stats(self) -> Dict: raise NotImplementedError

    def close(self): raise NotImplementedError
