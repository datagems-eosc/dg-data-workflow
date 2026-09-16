from configurations import DatasetLinkingConfig

DAG_ID = "DATASET_LINKING_REPORT"

DAG_PARAMS = {
}

DAG_TAGS = ["DatasetLinkingReport", ]

WAIT_FOR_COMPLETION_POKE_INTERVAL = DatasetLinkingConfig().options.report_poke_interval