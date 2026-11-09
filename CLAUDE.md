# dg-data-workflow

Apache Airflow 3 DAGs for the DataGEMS Data Workflow Orchestrator, plus the mkdocs documentation site.

## Layout

- `src/dags/` — the Airflow DAG folder. **Imports are rooted here** (`from common.enum import ...`, `from configurations import ...`), because Airflow puts the dags folder on `sys.path`. Do not add `src.` or `dags.` prefixes.
- `docs/` — mkdocs-material site (`docs/mkdocs.yml`, pages in `docs/docs/`, images in `docs/docs/images/`). Published with `mike` through the manual GitHub Action `.github/workflows/deploy-docs-on-demand.yml`.
- There is no `requirements.txt`, test suite, or linter config in the repo. The local Airflow `compose.yml`, `config/`, `logs/` and `plugins/` under `src/` are gitignored.

## How a DAG is put together

Every DAG is split over parallel packages, named after the DAG:

| Piece | Location | Contents |
|---|---|---|
| DAG definition | `workflows/<name>.py` | `@dag` function, `@task` / `@task.sensor` bodies, task wiring |
| Constants | `services/<name>/constants.py` | `DAG_ID`, `DAG_PARAMS` (Airflow `Param`s), `DAG_TAGS`, poke intervals, schedules |
| Request builders | `services/<name>/implementations.py` | `*_builder(...)` functions that return `(url, headers[, payload])` |
| UI docs | `documentations/<name>.py` | `DAG_DISPLAY_NAME`, `<TASK>_ID` and `<TASK>_DOC` (markdown shown in the Airflow UI) |
| Config | `configurations/<service>_config.py` | Wraps Airflow Variables (JSON) for one external service |
| Auth | `authorization/<service>_auth.py` | `BaseAuthService` subclass, OAuth client-credentials and a cached token |

Conventions:
- Task bodies run inside `with xcom_task_logging() as log:` and use `log.context` / `log.info_payload(...)`. Logs are pushed to XCom so the callbacks can forward them.
- HTTP goes through `common/extensions/http_requests.py` (`http_get/post/put`). They raise on non-2xx, sanitize NaN in JSON, and use a 1200s read timeout.
- Gateway-triggered DAGs take a `workflow_process_step_information` param (`id`, `process_id`, `step_id`). Every task wires the `on_*_callback`s from `common/extensions/callbacks.py`, which report step status to the DataGEMS Gateway. The final task uses the DAG-specific `on_success_<x>_callback` that marks the step as Succeeded.
- Use `AirflowFailException` for non-retryable failures and `AirflowException` for retryable ones.
- Data Model Management (MoMa) payloads are analytical-pattern graphs rendered from Jinja templates in `configurations/analytical_pattern_templates/` through `services/graphs/analytical_pattern_parser.py`.

## DAGs

| DAG_ID | File | Trigger | Talks to |
|---|---|---|---|
| DATASET_ONBOARDING | workflows/dataset_onboarding.py | Gateway | staging FS, Data Model Management |
| DATASET_PROFILING | workflows/dataset_profiling.py | Gateway | Profiler, MoMa convert, Data Model Management (heavy profile only) |
| CDD_INGEST | workflows/discovery_ingestion.py | Gateway | Profiler, Cross-Dataset Discovery |
| DATASET_PACKAGING | workflows/dataset_packaging.py | Gateway | Dataset Packaging |
| DATASET_RECOMMENDATION_REGISTERING | workflows/dataset_recommendation_registering.py | Gateway | Dataset Recommender |
| DATASET_LINKING_REPORT | workflows/dataset_linking_report.py | Gateway | Dataset Linking |
| STREAMING_INTERVAL_PROFILING | workflows/streaming_interval_profiling.py | every 60 min | Streaming Interval Profiler, Data Model Management |
| GEO_INGEST | workflows/store_weather.py | every 10 min | NOA geo API, TimescaleDB (`timescale_db` connection) |
| BUSYBOX | workflows/busy_box.py | manual | helper that sleeps |

## Airflow Variables and Connections used

`dwo_aai_clientid`, `dwo_aai_clientsecret`, `aai` (JSON: `base_url`), `gateway`, `data_model_management`, `dataset_profiler`, `moma_management`, `dataset_discovery`, `dataset_packaging`, `dataset_recommender`, `dataset_linking`, `streaming_interval_profiler`, `db_server_registry`, `noa_geo` (all JSON), `local_staging_path`, `local_dataset_path`. Connection: `timescale_db`.

When you add or rename a config key, update the matching `configurations/*_config.py` and `docs/docs/configuration.md`.

## Docs

- Build locally: `cd docs && pip install mkdocs mkdocs-material mike neoteroi-mkdocs pymdown-extensions && mkdocs serve`
- **The site is public.** Describe behaviour at a high level. Leave out Variable and secret names, hosts, endpoint paths, internal workarounds, helper or test DAGs (e.g. BUSYBOX) and history like "X was removed". Being vague is better than putting readers off.
- Every page under `docs/docs/` must be listed in the `nav` in `docs/mkdocs.yml`, and every nav entry must exist. The on-demand Action publishes whatever the nav lists.
- Draw flow diagrams as inline ```` ```mermaid ```` blocks (enabled through `pymdownx.superfences` custom fences), not PNGs.
- If you change a DAG's params, tasks or wiring, update the matching `docs/docs/workflow-*.md` page and the `documentations/<name>.py` strings in the same change.
- Commit messages reference the GitHub issue as `#<n> <summary>`.
