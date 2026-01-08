# Dataset Profiling Workflow

This workflow orchestrates the profiling lifecycle of a dataset, from profile generation to metadata integration and cleanup.
It produces two complementary profiles— light and heavy— and ensures that both are correctly persisted before releasing profiling resources.

## Input

Initially, the workflow is provided with the following information:

| Parameter         | Type             | Special Format | Mandatory | Description                                                                                                                                                                                          |
| ----------------- | ---------------- | -------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id                | string           | uuid           | yes       | A globally unique identifier of the dataset to be profiled. This identifier links profiling results to the correct dataset entity in downstream systems.                                             |
| code              | string           |                | no        | An optional short or human-friendly code used to reference the dataset. Primarily intended for cataloging or internal identification.                                                                |
| name              | string           |                | no        | The human-readable name of the dataset. Used for identification and traceability throughout the profiling lifecycle.                                                                                 |
| description       | string           |                | no        | A detailed textual description of the dataset. Provides contextual information that may be associated with profiling results.                                                                        |
| headline          | string           |                | no        | A concise, high-level summary of the dataset. Typically used for display purposes in user interfaces.                                                                                                |
| fields_of_science | array of strings |                | no        | A list of scientific or domain classifications associated with the dataset. Used for categorization and analytical context.                                                                          |
| languages         | array of strings |                | no        | The languages represented in the dataset content. Relevant for interpreting profiling metrics, especially for textual data.                                                                          |
| keywords          | string           |                | no        | Free-form keywords associated with the dataset. Support discoverability and semantic interpretation of profiling results.                                                                            |
| countries         | array of strings |                | no        | A list of countries relevant to the dataset. May indicate geographic coverage, origin, or regulatory context.                                                                                        |
| publishedUrl      | string           | uri            | no        | A public or external URL where the dataset is described or published. May reference documentation, landing pages, or external repositories.                                                          |
| citeAs            | string           |                | no        | A recommended citation string for the dataset. Used to support attribution and reuse in publications.                                                                                                |
| conformsTo        | string           |                | no        | A reference to a standard, schema, or specification that the dataset adheres to. Provides structural or semantic context for profiling outputs.                                                      |
| license           | string           |                | no        | The license under which the dataset is distributed. Defines legal and usage constraints relevant to downstream consumers.                                                                            |
| size              | number           | integer        | no        | An approximate size indicator for the dataset. May represent file size, record count, or another agreed-upon metric.                                                                                 |
| version           | string           |                | no        | The version identifier of the dataset. Used to distinguish profiling results across different dataset revisions.                                                                                     |
| mime_type         | string           |                | no        | The MIME type describing the dataset's format (e.g. text/csv, application/json). Helps the profiling system select appropriate analysis strategies.                                                  |
| date_published    | string           | date           | no        | The publication date of the dataset. Used for provenance tracking and temporal context.                                                                                                              |
| userId            | string           |                | no        | An identifier representing the user or actor who initiated the profiling workflow. Used for attribution, auditing, and traceability.                                                                 |
| data_store_kind   | 0 or 1           |                | yes       | An indicator of how the dataset is physically stored. This value determines how the profiler accesses the dataset (e.g. file-based vs. database-backed) and influences profiling execution behavior. |
| archivedAt        | string           | path           | yes       | The path or location where the dataset is archived and accessed for profiling. This serves as the authoritative source from which profiling jobs read the dataset.                                   |

## Tasks

The workflow follows the diagram below, which illustrates parallel execution, synchronization points, and cleanup:

![alt text](images/profiling_flow.png)

#### Trigger Profiles

The execution is split in two parallel task instance queues, one for light profiling and one for heavy, as shown in the diagram. The first level of tasks ran in parallel get the corresponding authorization token and communicate with the Profiler service to trigger the generation of the profile.
This parallelization allows lightweight metadata extraction and more intensive analysis to proceed independently and efficiently.

#### Check if the Profiles are ready

Once profiling jobs have been triggered, each branch enters a polling phase. In this phase the workflow periodically checks the status of the corresponding profiling job. Execution is paused between checks to avoid unnecessary load. The workflow advances only when the profile has reached a "ready" state.
If a profiling job fails, or is cleaned up prematurely, the workflow terminates with a failure, ensuring that incomplete or invalid profiles are never propagated.
This step guarantees that downstream tasks only operate on fully generated and valid profiling results.

#### Fetch Profiles

After a profile is reported as ready, the workflow retrieves its contents from the Profiler service. For each profile (light and heavy) the complete profiling result is fetched with the data preserved in its original structured form, with no transformation or interpretation applied. This separation ensures that profiling generation and profiling consumption remain decoupled.

#### Update Data Management

Once profiling data has been retrieved, the workflow updates the dataset representation in the Data Model Management system. The light and heavy profiles are handled as distinct but complementary updates, allowing consumers to benefit from different levels of detail. Successful completion of this step means the dataset is now profile-aware within the platform.

#### Profile Cleanup

After both profiling branches have completed successfully, the workflow converges into a final cleanup step.
Cleanup is intentionally executed after all profiling data has been safely persisted, ensuring no loss of information.
