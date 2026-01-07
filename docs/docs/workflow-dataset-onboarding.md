# Dataset Onboarding Workflow

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
- Database: TODO

## Tasks

This workdlow follows the diagram that will be explained below:

![alt text](images/onboarding_flow.png)

#### Stage Dataset Files

The files corresponding to the Dataset are collected and staged in a predetermined location. File (0), Remote (3) and Staged (4) locations are omitted.

#### Register Dataset

The task gets the corresponding authorization token and communicates with the Data Model Management service to register the dataset.

#### Choose if the Dataset will be loaded

In case the dataset is stored inside a relational database, the execution ends here. Otherwise, it continues downstream.

#### Load Dataset

The task gets the corresponding authorization token and communicates with the Data Model Management service to load the dataset. The execution ends here.
