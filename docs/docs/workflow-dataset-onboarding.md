# Dataset Onboarding Workflow

The Dataset Onboarding Workflow provides a unified and controlled process for registering and ingesting datasets into the platform, regardless of their original storage location.
The workflow accepts dataset metadata together with one or more dataset locations and guides the dataset through a well-defined lifecycle that separates physical data handling from logical dataset management.

## Input

In in the initial step, the workflow is provided with the following information:

| Parameter         | Type                                              | Special Format | Mandatory |
| ----------------- | ------------------------------------------------- | -------------- | --------- |
| id                | string                                            | uuid           | yes       |
| code              | string                                            |                | no        |
| name              | string                                            |                | no        |
| description       | string                                            |                | no        |
| headline          | string                                            |                | no        |
| fields_of_science | array of strings                                  |                | no        |
| languages         | array of strings                                  |                | no        |
| keywords          | string                                            |                | no        |
| countries         | array of strings                                  |                | no        |
| publishedUrl      | string                                            | uri            | no        |
| citeAs            | string                                            |                | no        |
| conformsTo        | string                                            |                | no        |
| license           | string                                            |                | no        |
| size              | number                                            | integer        | no        |
| dataLocations     | array of objects {Kind: string, location: string} |                | yes       |
| version           | string                                            |                | no        |
| mime_type         | string                                            |                | no        |
| date_published    | string                                            | date           | no        |
| userId            | string                                            |                | no        |

All the fields except dataLocations contain metadata information. The dataLocations contains the information where the Dataset is located. The following locations are supported:

- File: The dataset is stored inside a file somewhere in the mounted filesystem.
- Http: The dataset can be accessed via a URI.
- Ftp: The dataset is stored inside an FTP server. The location should be an FTP URI.
- Remote: TODO
- Staged: The dataset is already staged.
- Database: The dataset is stored inside a relational database.

## Tasks

This workflow follows the diagram that will be explained below:

![alt text](images/onboarding_flow.png)

#### Stage Dataset Files

This task ensures that all dataset files are available in a controlled, local staging area before the dataset is registered or loaded.
Because datasets may originate from heterogeneous storage systems, this step acts as a normalization phase: regardless of where the data comes from, downstream tasks interact with a consistent file-based representation whenever applicable.
The task iterates over all declared dataset locations and applies the appropriate handling strategy for each one.

If the dataset is already available on the local filesystem, already staged by a previous process, stored in a relational database, or referenced by a location type that does not require materialization, then no action is performed and the location is passed through unchanged.

If the dataset is hosted externally (for example via HTTP or FTP), the dataset files are retrieved from the remote source, stored in a predefined staging directory associated with the dataset and assigned unique filenames to avoid collisions or ambiguity.

The task produces a normalized list of dataset locations that reflects the effective access points for the dataset:

- unchanged locations for sources that do not require staging,
- staged file locations for externally retrieved datasets.

This output is used by subsequent tasks to register the dataset metadata and decide whether the dataset should be physically loaded or only registered.

If any dataset location cannot be accessed, retrieved, or staged successfully, the workflow fails at this step.
This prevents partial or inconsistent dataset onboarding.

#### Register Dataset

This task registers the dataset and its metadata in the central Data Model Management system, making the dataset discoverable, traceable, and addressable within the platform. The task uses the metadata provided at workflow start, together with the effective dataset locations produced by the staging step, to create a canonical dataset representation.
The task returns the response from the Data Model Management system, which is primarily informational; downstream control flow is determined by the dataset location types rather than this response.

If the registration request fails, the workflow terminates immediately. No dataset loading is attempted unless the dataset has been successfully registered.

#### Choose if the Dataset will be loaded

This step determines whether the workflow should proceed with physically loading the dataset or stop after registration. The decision is based on the types of dataset locations associated with the dataset: If the dataset is stored in a relational database, the workflow ends after registration. Otherwise, the workflow continues to the loading step.
By explicitly separating registration from loading, the workflow supports multiple dataset lifecycle patterns while maintaining a consistent onboarding process.


#### Load Dataset

This task performs the physical ingestion of the dataset into downstream systems after it has been successfully registered. Loading is only executed for datasets that require file-based processing. Database-resident datasets and other non-loadable sources are explicitly excluded by the preceding decision step. This operation does not redefine dataset metadata; it acts upon the dataset entity created during registration.

The task returns the response from the Data Model Management system which is primarily informational and does not affect further workflow execution.

If loading fails, the workflow fails at this stage. The dataset remains registered but is not marked as loaded, allowing the issue to be diagnosed and retried without re-registration.