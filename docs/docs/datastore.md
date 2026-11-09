# Data Stores

The orchestrator is mainly the data processing workflow layer that serves the related DataGEMS flows. Apart from the state of its workflow executions, it uses a small number of data stores to support specific workflows.

## Relational Database

The primary data store is a PostgreSQL relational database. It holds Airflow's metadata: workflow definitions, workflow runs, task states, execution history and related information.

The schema of this database is managed by Airflow.

## Dataset Storage

The [Dataset Onboarding](workflow-dataset-onboarding.md) workflow uses shared storage that every orchestrator component can reach:

- a **staging area**, where dataset files retrieved from external sources (files, HTTP or FTP) are placed, with one directory per dataset, and
- a **dataset storage area**, where each dataset's data is kept for the rest of the platform. Data Model Management references this location for each dataset.

The orchestrator only places data in these areas. The services that consume it manage the datasets after that.

## Time-Series Database

The [Weather Observations Ingestion](workflow-weather-ingestion.md) workflow stores weather station information and observations in a PostgreSQL database with time-series support (TimescaleDB). This store holds use-case data, not orchestrator state. Its connection is part of the workflow [configuration](configuration.md).

## Updates

When Airflow is updated to a newer version, any changes needed in the metadata database are applied by Airflow's migration process.
