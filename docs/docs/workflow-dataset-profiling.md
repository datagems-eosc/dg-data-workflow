# Dataset Profiling Workflow

This workflow orchestrates the profiling lifecycle of a dataset, from profile generation to metadata integration and cleanup.
It produces two complementary profiles—light and heavy—and ensures that both are correctly persisted before releasing profiling resources.

## Input

Initially, the workflow is provided with the following information:

| Parameter         | Type             | Special Format | Mandatory |
| ----------------- | ---------------- | -------------- | --------- |
| id                | string           | uuid           | yes       |
| code              | string           |                | no        |
| name              | string           |                | no        |
| description       | string           |                | no        |
| headline          | string           |                | no        |
| fields_of_science | array of strings |                | no        |
| languages         | array of strings |                | no        |
| keywords          | string           |                | no        |
| countries         | array of strings |                | no        |
| publishedUrl      | string           | uri            | no        |
| citeAs            | string           |                | no        |
| conformsTo        | string           |                | no        |
| license           | string           |                | no        |
| size              | number           | integer        | no        |
| version           | string           |                | no        |
| mime_type         | string           |                | no        |
| date_published    | string           | date           | no        |
| userId            | string           |                | no        |
| data_store_kind   | 0 or 1           |                | yes       |
| archivedAt        | string           | path           | yes       |

## Tasks

The workflow follows the diagram below, which illustrates parallel execution, synchronization points, and cleanup:

![alt text](images/profiling_flow.png)

#### Trigger Profiles

The execution is plit in two parallel task instance queues, one for light profiling and one for heavy, as shown in the diagram. The first level of tasks ran in parallel get the corresponding authorization token and communicate with the Profiler service to trigger the generation of the profile.
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
