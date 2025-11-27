from airflow.sdk import Variable


class DatasetOnboardingConfig:
    def __init__(self):
        self.local_staging_path = Variable.get("local_staging_path")
        self.local_dataset_path = Variable.get("local_dataset_path")