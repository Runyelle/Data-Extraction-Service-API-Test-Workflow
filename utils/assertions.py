"""
Common assertions and validations for API tests.
"""
import time
from typing import Dict, Any, List, Optional
import jsonschema
import pytest


class APIAssertions:
    """Collection of common assertions for API testing."""
    
    @staticmethod
    def assert_status_code(response, expected_code: int):
        """Assert that the response has the expected HTTP status code."""
        assert response.status_code == expected_code, (
            f"Expected status code {expected_code}, but got {response.status_code}. "
            f"Response: {response.text[:500]}"
        )
    
    @staticmethod
    def assert_json_schema(response_data: Dict[str, Any], schema: Dict[str, Any]):
        """Assert that the response data matches the expected JSON schema."""
        try:
            jsonschema.validate(instance=response_data, schema=schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"JSON schema validation failed: {e.message}")
    
    @staticmethod
    def assert_health_status(health_response: Dict[str, Any]):
        """Assert that the health check response indicates a healthy service."""
        assert "status" in health_response, "Health response missing 'status' field"
        assert health_response["status"] == "ok", (
            f"Expected health status 'ok', but got '{health_response['status']}'"
        )
    
    @staticmethod
    def assert_job_status(
        status_response: Dict[str, Any],
        expected_status: str,
        job_id: Optional[str] = None,
    ):
        """Assert that a job has the expected status."""
        assert "status" in status_response, "Status response missing 'status' field"
        actual_status = status_response["status"]
        assert actual_status == expected_status, (
            f"Job {job_id or 'unknown'} expected status '{expected_status}', "
            f"but got '{actual_status}'"
        )
    
    @staticmethod
    def assert_job_status_transition(
        initial_status: str,
        final_status: str,
        valid_transitions: Dict[str, List[str]],
    ):
        """Assert that a job status transition is valid."""
        if initial_status in valid_transitions:
            assert final_status in valid_transitions[initial_status], (
                f"Invalid status transition from '{initial_status}' to '{final_status}'. "
                f"Valid transitions: {valid_transitions[initial_status]}"
            )
    
    @staticmethod
    def assert_extraction_result_structure(result_response: Dict[str, Any]):
        """Assert that extraction results have the expected structure."""
        assert "data" in result_response or "results" in result_response, (
            "Result response missing 'data' or 'results' field"
        )
        
        # Get the data array
        data = result_response.get("data") or result_response.get("results", [])
        assert isinstance(data, list), "Result data should be a list"
        
        # If there are records, validate their structure
        if data:
            expected_fields = ["email", "first_name", "last_name", "id_from_service"]
            first_record = data[0]
            for field in expected_fields:
                assert field in first_record, (
                    f"Result record missing expected field: {field}"
                )
    
    @staticmethod
    def assert_extraction_result_count(
        result_response: Dict[str, Any],
        expected_count: int,
    ):
        """Assert that extraction results contain the expected number of records."""
        data = result_response.get("data") or result_response.get("results", [])
        actual_count = len(data)
        assert actual_count == expected_count, (
            f"Expected {expected_count} records, but got {actual_count}"
        )
    
    @staticmethod
    def assert_pagination(
        response: Dict[str, Any],
        expected_limit: Optional[int] = None,
        expected_offset: Optional[int] = None,
    ):
        """Assert that pagination is working correctly."""
        if expected_limit is not None:
            data = response.get("data") or response.get("results", [])
            assert len(data) <= expected_limit, (
                f"Pagination limit {expected_limit} exceeded. Got {len(data)} records"
            )
        
        # Check for pagination metadata
        if "total" in response:
            assert isinstance(response["total"], int), "Total count should be an integer"
        
        if "next" in response:
            assert response["next"] is None or isinstance(
                response["next"], str
            ), "Next link should be a string or None"
    
    @staticmethod
    def assert_error_message(
        error_response: Dict[str, Any],
        expected_keywords: List[str],
    ):
        """Assert that an error response contains expected keywords in the message."""
        # Check both 'message' and 'error' fields, and also check nested error fields
        message = error_response.get("message") or error_response.get("error", "")
        
        # Also check if error_response itself is a string or list
        if isinstance(error_response, str):
            message = error_response
        elif isinstance(error_response, list) and len(error_response) > 0:
            message = str(error_response[0])
        elif isinstance(error_response, dict):
            # Check all string values in the dict
            all_text = " ".join(str(v) for v in error_response.values() if isinstance(v, (str, list)))
            message = message + " " + all_text if message else all_text
        
        message_lower = message.lower()
        
        for keyword in expected_keywords:
            assert keyword.lower() in message_lower, (
                f"Error message should contain '{keyword}'. "
                f"Actual response: {error_response}"
            )
    
    @staticmethod
    def assert_response_time(response_time: float, max_seconds: float = 5.0):
        """Assert that a response completed within the expected time."""
        assert response_time <= max_seconds, (
            f"Response took {response_time:.2f}s, which exceeds "
            f"the maximum of {max_seconds}s"
        )
    
    @staticmethod
    def assert_statistics_structure(stats_response: Dict[str, Any]):
        """Assert that statistics response has the expected structure."""
        expected_fields = ["total_jobs", "completed_jobs"]
        for field in expected_fields:
            assert field in stats_response, (
                f"Statistics response missing expected field: {field}"
            )
            assert isinstance(stats_response[field], int), (
                f"Statistics field '{field}' should be an integer"
            )
    
    @staticmethod
    def assert_job_in_list(jobs_list: List[Dict[str, Any]], job_id: str):
        """Assert that a specific job ID appears in the jobs list."""
        job_ids = [job.get("job_id") or job.get("id") for job in jobs_list]
        assert job_id in job_ids, (
            f"Job {job_id} not found in jobs list. "
            f"Found jobs: {job_ids[:10]}"  # Show first 10 for debugging
        )


# Common JSON schemas for validation
JOB_STATUS_SCHEMA = {
    "type": "object",
    "required": ["status", "job_id"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["pending", "in_progress", "completed", "cancelled", "failed"],
        },
        "job_id": {"type": "string"},
        "record_count": {"type": "integer"},
        "start_time": {"type": "string"},
        "end_time": {"type": ["string", "null"]},
    },
}

EXTRACTION_RESULT_SCHEMA = {
    "type": "object",
    "required": ["data"],
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["email", "first_name", "last_name", "id_from_service"],
                "properties": {
                    "email": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "id_from_service": {"type": "string"},
                },
            },
        },
        "total": {"type": "integer"},
        "limit": {"type": "integer"},
        "offset": {"type": "integer"},
        "next": {"type": ["string", "null"]},
    },
}

HEALTH_SCHEMA = {
    "type": "object",
    "required": ["status"],
    "properties": {
        "status": {"type": "string", "enum": ["ok", "error"]},
    },
}

