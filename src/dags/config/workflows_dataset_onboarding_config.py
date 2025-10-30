from utils.configurations import get as fetch


class DatasetOnboardingConfig:
    def __init__(self):
        self.local_staging_path = fetch("local_staging_path")