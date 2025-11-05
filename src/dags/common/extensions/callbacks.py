from services.logging.logger import Logger


def on_execute_callback(context):
    log = Logger(context)
    log.info("Task executing")


def on_retry_callback(context):
    log = Logger(context)
    log.info("Task retrying")


def on_success_callback(context):
    log = Logger(context)
    log.info("Task succeeded")


def on_failure_callback(context):
    log = Logger(context)
    log.error("Task failed")


def on_skipped_callback(context):
    log = Logger(context)
    log.warning("Task skipped")
