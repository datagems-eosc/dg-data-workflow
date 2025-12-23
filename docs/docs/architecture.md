# Service Architecture

This service is built using the [Apache/Airflow](https://airflow.apache.org/) tool. Apache Airflow is an open-source platform for developing, scheduling, and monitoring batch-oriented workflows. It offers an extensible Python framework that enables us to build workflows connecting with virtually any technology. A web-based UI helps us visualize, manage, and debug our workflows.

## Why Apache Airflow

Apache Airflow was selected as the orchestration layer for this solution because it provides explicit, observable, and resilient workflow coordination across multiple services. The platform is particularly well-suited for environments where execution order, timing, and reliability are first-class architectural concerns. Rather than embedding orchestration logic inside individual services, Airflow centralizes workflow control while keeping services loosely coupled and independently deployable.

### Explicit Workflow Orchestration

In Airflow, workflows are defined declaratively using _"Directed Acyclic Graphs"_, in short __DAGs__. Inside a DAG, dependencies between execution steps are explicit, deterministic and inspectable. These individual execution pieces of work are called Tasks, arranged with dependencies and data flows taken into account.

![alt text](images/example_operators.png)

A Dag specifies the dependencies between tasks, which defines the order in which to execute the tasks. Tasks describe what to do, be it fetching data, running analysis, triggering other systems, or more.

### Workflows as code

Airflow workflows are defined entirely in Python. This "workflows as code" approach brings several advantages:
* __Dynamic__: Pipelines are defined in code, enabling dynamic DAG generation and parameterization.
* __Extensible__: The Airflow framework includes a wide range of built-in operators and can be further extended to cover a wide variety of programming needs.

### Centralized Control Without Centralized Logic

Airflow acts as a control plane, not a business logic engine:
* Services remain autonomous and focused on domain responsibilities
* Airflow coordinates when and under what conditions services interact
* No service needs awareness of downstream consumers or execution order

This architecture reduces cross-service dependencies, improves service reusability and enables independent scaling and deployment.

### Built-in Reliability and Failure Semantics

Airflow provides failure handling as a core architectural feature:
* Task-level retries with configurable backoff
* Timeouts and execution limits
* Partial re-runs without restarting from the beginning

This allows the system to recover gracefully from transient service outages, avoid cascading failures and maintain predictable operational behavior.

### Strong Observability and Operational Transparency

Airflow exposes execution state as part of its core model. DAGs and their tasks can be inspected visually, as well as logs and timestamps kept. 
Also, the historical audit trail of all workflow executions is kept.

These features provide immediate insight into system behavior and even controlled manual intervention when required.

![alt text](images/example_airflow_ui.png)