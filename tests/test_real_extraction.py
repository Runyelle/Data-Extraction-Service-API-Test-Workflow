"""
Real Extraction Tests

These tests validate the integration with the service provided API and
the complete data extraction pipeline using actual API tokens.
"""
import pytest
import time
import requests
from typing import Dict, Any

from utils.api_client import APIClient
from utils.assertions import (
    APIAssertions,
    JOB_STATUS_SCHEMA,
    EXTRACTION_RESULT_SCHEMA,
)
from config import settings


class TestRealExtractionWorkflow:
    """Test suite for real extraction workflow."""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient, service_provided_token: str):
        """Setup test fixtures."""
        self.api_client = api_client
        self.service_token = service_provided_token
        self.created_job_ids = []
    
    def teardown_method(self):
        """Cleanup after each test."""
        if settings.test_data_cleanup:
            for job_id in self.created_job_ids:
                try:
                    self.api_client.remove_job(job_id)
                except requests.exceptions.HTTPError:
                    # Job may already be removed or not exist
                    pass
    
    def test_start_new_extraction(self):
        """Test starting a new extraction job."""
        # Start extraction
        start_response = self.api_client.start_extraction(self.service_token)
        
        # Verify response
        assert "job_id" in start_response, "Start response missing 'job_id'"
        job_id = start_response["job_id"]
        self.created_job_ids.append(job_id)
        
        assert isinstance(job_id, str), "job_id should be a string"
        assert len(job_id) > 0, "job_id should not be empty"
    
    def test_poll_job_status_to_completion(self):
        """Test polling job status until completion."""
        # Start extraction
        start_response = self.api_client.start_extraction(self.service_token)
        job_id = start_response["job_id"]
        self.created_job_ids.append(job_id)
        
        # Poll until completion
        final_status = self.api_client.poll_job_status(
            job_id,
            expected_statuses=["completed", "failed"],
        )
        
        # Verify final status
        APIAssertions.assert_json_schema(final_status, JOB_STATUS_SCHEMA)
        assert final_status["status"] in ["completed", "failed"]
        assert final_status["job_id"] == job_id
        
        if final_status["status"] == "failed":
            # If failed, verify error details are present
            assert "error" in final_status or "message" in final_status
    
    def test_retrieve_extracted_results(self):
        """Test retrieving extracted results from a completed job."""
        # Start extraction
        start_response = self.api_client.start_extraction(self.service_token)
        job_id = start_response["job_id"]
        self.created_job_ids.append(job_id)
        
        # Poll until completion
        final_status = self.api_client.poll_job_status(
            job_id,
            expected_statuses=["completed", "failed"],
        )
        
        # Skip if job failed
        if final_status["status"] == "failed":
            pytest.skip(f"Extraction job {job_id} failed: {final_status.get('error', 'Unknown error')}")
        
        # Retrieve results
        result_response = self.api_client.get_job_result(job_id)
        
        # Verify results structure
        APIAssertions.assert_json_schema(result_response, EXTRACTION_RESULT_SCHEMA)
        APIAssertions.assert_extraction_result_structure(result_response)
        
        # Verify data content
        data = result_response.get("data", [])
        if data:
            # Verify expected fields are present
            first_record = data[0]
            assert "email" in first_record
            assert "first_name" in first_record
            assert "last_name" in first_record
            assert "id_from_service" in first_record
    
    def test_retrieve_results_with_pagination(self):
        """Test pagination for extraction results."""
        # Start extraction
        start_response = self.api_client.start_extraction(self.service_token)
        job_id = start_response["job_id"]
        self.created_job_ids.append(job_id)
        
        # Poll until completion
        final_status = self.api_client.poll_job_status(
            job_id,
            expected_statuses=["completed", "failed"],
        )
        
        if final_status["status"] == "failed":
            pytest.skip(f"Extraction job {job_id} failed")
        
        # Check if there are enough records for pagination
        result_response = self.api_client.get_job_result(job_id)
        total_records = len(result_response.get("data", []))
        
        if total_records < 2:
            pytest.skip("Not enough records to test pagination")
        
        # Test pagination
        page1 = self.api_client.get_job_result(job_id, limit=1, offset=0)
        APIAssertions.assert_pagination(page1, expected_limit=1)
        
        if total_records > 1:
            page2 = self.api_client.get_job_result(job_id, limit=1, offset=1)
            APIAssertions.assert_pagination(page2, expected_limit=1)
            
            # Verify no overlap
            page1_data = page1.get("data", [])
            page2_data = page2.get("data", [])
            if page1_data and page2_data:
                assert page1_data[0]["id_from_service"] != page2_data[0]["id_from_service"]
    
    def test_remove_extraction_data(self):
        """Test removing extraction data after verification."""
        # Start extraction
        start_response = self.api_client.start_extraction(self.service_token)
        job_id = start_response["job_id"]
        self.created_job_ids.append(job_id)
        
        # Poll until completion
        final_status = self.api_client.poll_job_status(
            job_id,
            expected_statuses=["completed", "failed"],
        )
        
        if final_status["status"] == "failed":
            pytest.skip(f"Extraction job {job_id} failed")
        
        # Verify results exist
        result_response = self.api_client.get_job_result(job_id)
        assert len(result_response.get("data", [])) > 0
        
        # Remove the job
        self.api_client.remove_job(job_id)
        
        # Verify job no longer exists
        try:
            self.api_client.get_job_status(job_id)
            pytest.fail("Job should not exist after removal")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404
        
        # Remove from cleanup list since we already removed it
        if job_id in self.created_job_ids:
            self.created_job_ids.remove(job_id)
    
    def test_job_status_transitions(self):
        """Test that job status transitions correctly through lifecycle."""
        # Start extraction
        start_response = self.api_client.start_extraction(self.service_token)
        job_id = start_response["job_id"]
        self.created_job_ids.append(job_id)
        
        # Get initial status
        initial_status = self.api_client.get_job_status(job_id)
        initial_status_value = initial_status["status"]
        
        # Valid initial statuses
        assert initial_status_value in ["pending", "in_progress"]
        
        # Poll until final state
        final_status = self.api_client.poll_job_status(
            job_id,
            expected_statuses=["completed", "failed", "cancelled"],
        )
        final_status_value = final_status["status"]
        
        # Verify valid transition
        valid_transitions = {
            "pending": ["in_progress", "completed", "failed", "cancelled"],
            "in_progress": ["completed", "failed", "cancelled"],
        }
        
        if initial_status_value in valid_transitions:
            APIAssertions.assert_job_status_transition(
                initial_status_value,
                final_status_value,
                valid_transitions,
            )

