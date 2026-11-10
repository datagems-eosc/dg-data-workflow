# Dataset Onboarding Workflow

The Dataset Onboarding Workflow (`DATASET_ONBOARDING`) provides a unified, controlled process for bringing a dataset into the platform, wherever it is originally stored.
It accepts the dataset's metadata together with one or more data locations, makes the data available in the platform's storage, and registers the dataset in the Data Model Management service.

## Input

The workflow accepts the following parameters:

| Parameter | Type | Format | Mandatory | Description |
| --------- | ---- | ------ | --------- | ----------- |
| id | string | uuid | yes | Globally unique identifier of the dataset. It's used throughout the workflow to associate metadata, stored files and lifecycle events with the same dataset. |
| dataLocations | string | JSON array | yes | JSON-encoded list of the locations where the dataset's data can be found. See [Data Locations](#data-locations). |
| name | string | | no | Human-readable name of the dataset. |
| description | string | | no | Detailed description of the dataset's contents, scope and purpose. |
| headline | string | | no | Short, high-level summary of the dataset, typically shown in listings. |
| fields_of_science | array of strings | | no | Scientific or domain classifications of the dataset. |
| languages | array of strings | | no | Languages represented in the dataset's content. |
| keywords | array of strings | | no | Free-form keywords that improve discoverability. |
| countries | array of strings | | no | Countries relevant to the dataset, such as its geographic coverage. |
| publishedUrl | string | uri | no | Public URL where the dataset is published or described. |
| citeAs | string | | no | Recommended citation for the dataset. |
| license | string | | no | License under which the dataset is distributed. |
| doi | string | | no | Digital Object Identifier of the dataset, if one exists. |
| date_published | string | date | no | Publication date of the dataset. Defaults to the current date. |
| userId | string | | no | Identifier of the user who requested the onboarding, used for attribution and provenance. |
| workflow_process_step_information | object | | yes | Tracking information for the platform process step that this run belongs to. Supplied automatically by the platform. See [Platform Integration](integration.md). |

### Data Locations

Each entry in `dataLocations` is an object with a `kind` and a `location`:

```json
[
  { "kind": "Http", "location": "https://example.org/data/measurements.csv" },
  { "kind": "Ftp",  "location": "ftp://ftp.example.org/pub/measurements.csv" }
]
```

`kind` can be given by name or by its numeric value:

| Kind | Value | Description |
| ---- | ----- | ----------- |
| File | 0 | The data is a file on a filesystem that's accessible to the orchestrator. |
| Http | 1 | The data can be downloaded from an HTTP(S) URL. |
| Ftp | 2 | The data can be downloaded from an FTP server. The location is an FTP URI. |
| Remote | 3 | The data is in a remote store that the platform accesses directly. |
| Staged | 4 | The data is already in the platform's storage. |
| Database | 5 | The data is in a relational database. The location identifies the database. |

## Tasks

```mermaid
flowchart LR
    A[Stage Dataset Files] --> B[Register Dataset]
    B --> C[Load Dataset]
    C --> D((Finish))
```

#### Stage Dataset Files

This task makes sure the dataset's data is available in the platform's storage area before the dataset is registered. Datasets come from many kinds of storage, so this step normalises them: downstream steps always work with locations that the platform controls.

All declared locations are processed in parallel:

- **File**, **Http** and **Ftp** locations are retrieved and stored in a staging area dedicated to the dataset. Each stored file gets a unique name, so files never collide.
- **Remote**, **Staged** and **Database** locations are already accessible to the platform and are passed on unchanged.

The task outputs the effective list of locations for the dataset.
If any location can't be accessed or stored, the workflow fails at this step, so a dataset is never partially onboarded.

#### Register Dataset

This task registers the dataset and its metadata in the Data Model Management service, which makes the dataset discoverable, traceable and addressable in the platform.
The registration also records provenance: which user requested the onboarding and when.

If registration fails, the workflow stops. A dataset is never loaded unless it has been registered.

#### Load Dataset

This task completes onboarding by informing the Data Model Management service that the dataset's data is in its final storage location, and updating the dataset's state.
It doesn't change the metadata recorded at registration.

If the storage location isn't available yet when this step runs (for example, because an upstream process is still making it available), the step automatically retries a few times. Any other error fails the workflow immediately. The dataset stays registered, so the problem can be investigated and loading retried.

## Completion

When the dataset has been loaded, the workflow notifies the platform that onboarding has finished. The notification includes how the dataset is stored (file-based or in a relational database), so the platform can configure and start the [Dataset Profiling](workflow-dataset-profiling.md) workflow, which is the next step of the dataset's lifecycle.
