from airflow.sdk import Param

from configurations import DatasetLinkingConfig

DAG_ID = "DATASET_LINKING_REPORT"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
    "kw": Param(None, type=["number", "null"], description="Keyword contribution"),
    "desc": Param(None, type=["number", "null"], description="Description contribution"),
    "head": Param(None, type=["number", "null"], description="Headline contribution"),
    "th": Param(None, type=["number", "null"], minimum=0.0, maximum=100.0,
                description="Pair similarity threshold, percentage 0..100"),
    "keyword_method": Param(
        "jaccard",
        type="string",
        enum=["jaccard", "sbert"],
        values_display={
            "jaccard": "Jaccard",
            "sbert": "SBERT",
        },
        description="Keyword similarity method",
    ),
    "include_chunks": Param(None, type=["null", "boolean"], description="Include description-chunk evidence"),
    "include_graphs": Param(None, type=["null", "boolean"], description="Generate graphs while building the report"),
    "graphs_only_above_threshold": Param(None, type=["null", "boolean"],
                                         description="Generate graphs only for pairs passing th"),
    "workflow_process_step_information": Param(type="object")
}

DAG_TAGS = ["DatasetLinkingReport", ]

WAIT_FOR_COMPLETION_POKE_INTERVAL = DatasetLinkingConfig().options.report_poke_interval
