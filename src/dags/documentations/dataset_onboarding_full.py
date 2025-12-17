DAG_DISPLAY_NAME = "Dataset Onboarding Future"

DAG_DESCRIPTION = """
The Dataset Onboarding DAG orchestrates the end-to-end process of registering a user-provided dataset into the Data Management system, optionally staging the dataset files, and ensuring authenticated, traceable, and fault-safe execution. 
The workflow is fail-fast: any error in authentication, data staging, or dataset registration causes the DAG to terminate in an error state.
"""

STAGE_DATASET_FILES_ID = "stage_dataset_files"

STAGE_DATASET_FILES_DOC = """
# Stage Dataset Files

The _stage_dataset_files_ task is responsible for *normalizing dataset file locations* at the very beginning of the Dataset Onboarding workflow.
Its goal is to ensure that all dataset data locations are either:

* already usable as-is, or
* retrieved from external sources and staged locally in a controlled staging directory.

This task produces a *validated, homogeneous list of data locations* that downstream tasks can safely consume.
"""

REGISTER_DATASET_ID = "register_dataset"

REGISTER_DATASET_DOC = """
# Onboarding Request

The register_dataset task is responsible for formally registering the dataset into the Data Model Management (DMM) service after dataset files have been staged and validated.
This task translates user-provided metadata and workflow context into a graph-based registration payload and submits it to the Data Management API using an authenticated request.
"""

BRANCH_LOAD_DATASET_ID = "choose_if_the_dataset_will_be_loaded"

BRANCH_LOAD_DATASET_DOC = """
# Choose if the dataset will be loaded

The branch_load_dataset task is a branching decision point in the Dataset Onboarding DAG.
Its role is to determine whether a dataset must be physically loaded into the system based on the nature of its data locations.
This task does not perform any data movement or API calls; it only controls which downstream path the DAG should follow.
If the Dataset is stored in a relational database alone, the workflow ends here.
"""

LOAD_DATASET_ID = "load_dataset"

LOAD_DATASET_DOC = """
# Onboarding Request

The load_dataset task is responsible for transitioning a registered dataset into its loaded state within the Data Model Management (DMM) system.
This task signals that the dataset’s data has been physically placed in its final storage location (e.g. S3) and updates the dataset’s state accordingly in the DataGEMS data model.
It is executed only if selected by the branch_load_dataset task.
"""
