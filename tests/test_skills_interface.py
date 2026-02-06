import pytest

def test_skill_input_output_contract():
    """
    Requirement: Verifies skill input/output schemas.
    Ensures that the Worker output is ready for PostgreSQL audit logs.
    """
    incoming_task = {"task_id": "task_123", "action": "scrape"}
    
    # Any skill we build must have a standard 'execute' function
    from skills.skill_trend_scraper.logic import execute_skill
    
    response = execute_skill(incoming_task)
    
    # The output must contain these keys for the Judge to validate
    assert "status" in response
    assert "payload" in response
    assert "metadata" in response

def test_skill_error_handling():
    """
    Requirement: Validates error handling structure.
    The Swarm needs a standard way to see if a Worker failed.
    """
    from skills.skill_trend_scraper.logic import execute_skill
    
    # Simulate a bad task
    response = execute_skill({})
    
    assert response["status"] == "error"
    assert "error_message" in response