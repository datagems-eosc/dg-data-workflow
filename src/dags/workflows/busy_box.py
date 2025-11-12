from time import sleep as time_sleep

from airflow.sdk import task, dag, Param, get_current_context

from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_failure_callback, on_skipped_callback


@dag("BUSYBOX", tags=["BUSYBOX", "SLEEP", "SWEET_DREAMS"], dag_display_name="Busy Box",
     description="A helper Dag to have constantly running", params={"forHours": Param(type="integer", minimum=0)})
def busy_box():
    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback)
    def sleep():
        time_sleep(get_current_context()["params"]["forHours"] * 3600)
        return True

    _ = sleep()


busy_box()
