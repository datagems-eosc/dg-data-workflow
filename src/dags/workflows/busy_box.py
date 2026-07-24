from time import sleep as time_sleep

from airflow.sdk import task, dag, Param, get_current_context


@dag("BUSYBOX", tags=["BUSYBOX", "SLEEP", "SWEET_DREAMS"], dag_display_name="Busy Box",
     description="A helper Dag to have constantly running", params={"forHours": Param(type="integer", minimum=0)})
def busy_box():
    @task()
    def sleep():
        time_sleep(get_current_context()["params"]["forHours"] * 3600)
        return True

    _ = sleep()


busy_box()
