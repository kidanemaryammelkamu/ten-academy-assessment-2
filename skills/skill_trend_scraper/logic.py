def execute_skill(task: dict):
    """
    Standard skill execution contract.
    """

    # Invalid task handling
    if not task or "task_id" not in task:
        return {
            "status": "error",
            "payload": None,
            "error_message": "Invalid task input"
        }

    # Success response
    return {
        "status": "success",
        "payload": {
            "task_id": task.get("task_id"),
            "data": "mocked_result"
        },
        "metadata": {
            "worker": "trend_scraper",
            "version": "1.0"
        }
    }


def validate_trend_schema(trend: dict) -> bool:
    """
    Validates required trend fields.
    """
    required_fields = [
        "topic",
        "platform",
        "reach",
        "confidence_score"
    ]

    for field in required_fields:
        if field not in trend:
            return False

    return True
