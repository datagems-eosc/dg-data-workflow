# Configuration

The orchestrator is configured in two layers:

- **Airflow configuration**: the settings of the Airflow deployment itself, such as the executor, metadata database and logging. These follow the standard [Airflow configuration reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html).
- **Workflow configuration**: the settings that the DataGEMS workflows need to reach the services they coordinate. These are provided as Airflow [Variables](https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html) and [Connections](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html).

## Workflow Configuration

The workflow configuration covers the following areas.

### Integrated Services

Each DataGEMS service that the workflows call has its own configuration entry, which holds:

- the service's base address,
- the authorisation scope to request when calling it,
- the paths of the operations the workflows use, and
- for services with long-running jobs, how often the job status is checked.

The integrated services are the Platform Gateway, Data Model Management, MoMa management, the Profiler, the Streaming Interval Profiler, Cross-Dataset Discovery, Dataset Packaging, the Dataset Recommender and Dataset Linking.

### Authentication

These are the address of the DataGEMS AAI and the orchestrator's client credentials. See [Platform Integration](integration.md#authentication).

### Storage

These are the locations of the staging area and of the dataset storage area that the [Dataset Onboarding](workflow-dataset-onboarding.md) workflow uses. See [Data Stores](datastore.md).

### Database Servers

This is the list of database servers that host database-backed datasets, plus a default server. The [Dataset Profiling](workflow-dataset-profiling.md) workflow uses it to tell the Profiler how to reach a dataset stored in a relational database.

### Scheduled Workflows

These are the settings for the scheduled workflows: the dataset monitored by [Streaming Interval Profiling](workflow-streaming-interval-profiling.md), and the observation source and time-series database connection used by [Weather Observations Ingestion](workflow-weather-ingestion.md).

## Secrets

Some configuration values are sensitive, such as client credentials and database connection details. Keep them separate from the rest of the configuration, using whatever the infrastructure offers: Kubernetes secrets, or an Airflow [secrets backend](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/secrets-backend/index.html). Never store them in the workflow code.
