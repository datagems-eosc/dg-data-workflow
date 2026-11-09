# Frequently Asked Questions (FAQ)

## Which workflows are available?

The [Workflow Overview](workflow-overview.md) lists every workflow, how it's started and what it does.

## How is a workflow started?

Most workflows are started automatically by the DataGEMS platform as steps of a dataset's lifecycle. Authorised operators can also start them from the Airflow UI or through the Airflow REST API. Scheduled workflows run automatically at their configured interval. See [Starting a Workflow](workflow-overview.md#starting-a-workflow).

## How can I follow the progress of a workflow?

Workflows started by the platform report the status of each step back to the platform, so progress can be followed there. Operators can also look at each run, its tasks and their logs in the Airflow UI. See [Platform Integration](integration.md#progress-reporting).

## Dataset onboarding failed at the staging step. What should I check?

The staging step fails if any declared data location can't be retrieved. Check that every location is correct and reachable, for example that the URLs can be accessed and the FTP servers accept the connection. Also check that each location's `kind` matches the type of location. See [Data Locations](workflow-dataset-onboarding.md#data-locations).

## Cross-Dataset Discovery indexing fails with "Dataset is not profiled". Why?

Indexing needs the profile produced by the [Dataset Profiling](workflow-dataset-profiling.md) workflow. Run profiling successfully for the dataset first, then start indexing again.

## Can a failed workflow be resumed?

Yes. Airflow keeps the state of every task, so an operator can clear a failed task in the Airflow UI and the run continues from that point, without repeating the tasks that already succeeded.

## Known Issues

Known issues and their status are tracked in the [GitHub issues](https://github.com/datagems-eosc/dg-data-workflow/issues) of the repository.
