from celery import shared_task
import logging

logger = logging.getLogger("alert_task_logger")


@shared_task(name="check_gold_price_and_send_alert")
def check_gold_price_and_send_alert():
    logger.info("Checking gold price and sending alert if necessary.")
    # Add the logic to check gold price and send alert here
    return None
