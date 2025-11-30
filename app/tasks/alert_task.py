
from celery import shared_task
import asyncio
from app.database.database import get_task_cache
from app.utils.gold_price_utility import get_current_gold_price
import logging

logger = logging.getLogger("alert_task_logger")


@shared_task(name="check_gold_price_and_send_alert", bind=True)
def check_gold_price_and_send_alert(self):
    """
    Check gold price and trigger alerts
    """
    result = asyncio.run(_check_and_process_alerts())
    logger.info("check_gold_price_and_send_alert : Task completed")
    return result


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
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise


async def process_alerts_by_metal_type(
    cache,
    metal_type: str,
    threshold_price: float,
    batch_size: int = 100
) -> int:
    """
    Process alerts for a specific metal type using cursor-based pagination

    Pseudocode implementation:
    cursor_score = threshold_price
    while True:
        results = ZRANGEBYSCORE alerts (cursor_score +inf WITHSCORES LIMIT 0 batch_size
        if empty(results): break
        for item in results: process(item)
        cursor_score = last.score
    """
    redis_key = f"alerts:{metal_type}"
    cursor_score = 0  # Start from 0 to get all alerts <= threshold
    processed_count = 0

    logger.info(
        f"Processing {metal_type} alerts with threshold: ₹{threshold_price}")

    while True:
        # ZRANGEBYSCORE key min max WITHSCORES LIMIT offset count
        # Get alerts where alert_price <= threshold_price
        # Using cursor_score as min to avoid re-processing
        results = await cache.zrangebyscore(
            redis_key,
            min=cursor_score,           # Start from cursor (0 initially)
            max=threshold_price,        # Up to current price
            withscores=True,            # Include scores (alert prices)
            start=0,                    # Offset (always 0 with cursor)
            num=batch_size              # Batch size
        )

        # Check if we got any results
        if not results or len(results) == 0:
            break

        # Process each alert in the batch
        for member, score in results:
            # member format: "user_id:alert_id"
            # score: alert_price
            await process_single_alert(
                cache=cache,
                member=member.decode() if isinstance(member, bytes) else member,
                alert_price=score,
                current_price=threshold_price,
                metal_type=metal_type
            )
            processed_count += 1

        # Get last item's score for next cursor
        last_member, last_score = results[-1]

        # Move cursor to next position (last_score + small increment to avoid duplicates)
        cursor_score = last_score + 0.01

        # If we got fewer results than batch_size, we're done
        if len(results) < batch_size:
            break

    logger.info(f"Processed total {processed_count} {metal_type} alerts")
    return processed_count


async def process_single_alert(
    cache,
    member: str,
    alert_price: float,
    current_price: float,
    metal_type: str
):
    """
    Process a single alert

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

    # 3. Queue notification task
    send_alert_notification.delay(
        alert_id=alert_id,
        user_id=user_id,
        alert_price=alert_price,
        current_price=current_price,
        metal_type=metal_type
    )


@shared_task(name="tasks.send_alert_notification", bind=True, max_retries=3)
def send_alert_notification(
    self,
    alert_id: int,
    user_id: int,
    alert_price: float,
    current_price: float,
    metal_type: str
):
    """
    Send notification to user
    """

    try:
        # TODO: Add your notification logic here
        # - Send email
        # - Send SMS
        # - Send push notification

        asyncio.run(_send_notification_async(alert_id, user_id,
                    alert_price, current_price, metal_type))

    except Exception as exc:
        logger.error(f"❌ Failed to send notification: {exc}")
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)


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
    # TODO: Send actual notification
    logger.info(f"📨 Sending notification to user {user_id}")
