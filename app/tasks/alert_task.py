from celery import shared_task
import asyncio
from app.database.database import get_task_cache
from app.utils.gold_price_utility import get_current_gold_price
import logging

logger = logging.getLogger("alert_task_logger")


@shared_task(name="send_alert_notification", bind=True, max_retries=3)
def send_alert_notification(
    self,
    alert_id: int,
    user_id: int,
    alert_price: float,
    current_price: float,
    metal_type: str
):
    """
    Send notification to user (queued task)
    """
    logger.info(f"Processing notification for alert {alert_id}")

    try:
        asyncio.run(_send_notification_async(
            alert_id, user_id, alert_price, current_price, metal_type
        ))

    except Exception as exc:
        logger.error(f"❌ Failed to send notification: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(name="check_gold_price_and_send_alert", bind=True)
def check_gold_price_and_send_alert(self):
    """
    Check gold price and trigger alerts (scheduled task)
    """
    logger.info("Starting alert check task")
    result = asyncio.run(_check_and_process_alerts())
    logger.info("Task completed")
    return result


async def _send_notification_async(
    alert_id: int,
    user_id: int,
    alert_price: float,
    current_price: float,
    metal_type: str
):
    """
    Async function to send notification
    """
    await asyncio.sleep(1)  # Simulate network delay
    logger.info(f"Notification sent to user {user_id} for alert {alert_id}")


async def _check_and_process_alerts():
    """
    Main async function to process alerts
    """
    cache = get_task_cache()

    try:
        # Get current gold price from cache
        current_gold_price = await get_current_gold_price()
        current_gold_price = float(current_gold_price)

        logger.info(f"Current gold price: ₹{current_gold_price}")

        # Process gold alerts
        gold_count = await process_alerts_by_metal_type(
            cache=cache,
            metal_type="gold",
            threshold_price=current_gold_price,
            batch_size=100
        )

        return f"Processed {gold_count} gold alerts"

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


async def process_alerts_by_metal_type(
    cache,
    metal_type: str,
    threshold_price: float,
    batch_size: int = 100
) -> int:
    """
    Process alerts for a specific metal type using cursor-based pagination
    """
    redis_key = f"alerts:{metal_type}"
    cursor_score = 0
    processed_count = 0

    while True:
        # Get alerts where alert_price <= threshold_price
        results = await cache.zrangebyscore(
            redis_key,
            min=cursor_score,
            max=threshold_price,
            withscores=True,
            start=0,
            num=batch_size
        )

        # No more results
        if not results or len(results) == 0:
            break

        # Process each alert in the batch
        for member, score in results:
            await process_single_alert(
                cache=cache,
                member=member.decode() if isinstance(member, bytes) else member,
                alert_price=score,
                current_price=threshold_price,
                metal_type=metal_type
            )
            processed_count += 1

        # Move cursor forward
        _, last_score = results[-1]
        cursor_score = last_score + 0.01

        # If we got fewer results than batch_size, we're done
        if len(results) < batch_size:
            break

    return processed_count


async def process_single_alert(
    cache,
    member: str,
    alert_price: float,
    current_price: float,
    metal_type: str
):
    """
    Process a single alert and queue notification

    Args:
        member: "user_id:alert_id" format
        alert_price: The price at which alert should trigger
        current_price: Current market price
        metal_type: "gold" or "silver"
    """
    # Parse member string
    try:
        user_id, alert_id = member.split(":")
        user_id = int(user_id)
        alert_id = int(alert_id)
    except ValueError as e:
        logger.error(f"Invalid member format: {member}, error: {e}")
        return

    # Queue notification task

    send_alert_notification.delay(
        alert_id=alert_id,
        user_id=user_id,
        alert_price=alert_price,
        current_price=current_price,
        metal_type=metal_type
    )
