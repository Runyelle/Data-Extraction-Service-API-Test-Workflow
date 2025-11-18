"""
Edge Case Tests

These tests validate the API's behavior when confronted with invalid inputs,
unexpected states, or boundary conditions to ensure robustness and proper error handling.
"""
import pytest
import requests
from typing import Dict, Any

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from config import settings


class TestEdgeCases:
    """Test suite for edge cases and error scenarios."""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient):
        """Setup test fixtures."""
        self.api_client = api_client
    
    def test_invalid_api_token_empty(self):
        """Test starting extraction with empty API token."""
        try:
            self.api_client.start_extraction("")
            pytest.fail("Should have raised an error for empty token")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 401]
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["token", "api", "invalid", "missing", "required"],
            )
    
    def test_invalid_api_token_malformed(self):
        """Test starting extraction with malformed API token."""
        try:
            self.api_client.start_extraction("invalid_token_12345")
            pytest.fail("Should have raised an error for invalid token")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 401]
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["token", "api", "invalid", "unauthorized", "authentication"],
            )
    
    def test_nonexistent_job_id_status(self):
        """Test requesting status for non-existent job ID."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        try:
            self.api_client.get_job_status(fake_job_id)
            pytest.fail("Should have raised 404 for non-existent job")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["not found", "job", "exist"],
            )
    
    def test_nonexistent_job_id_result(self):
        """Test requesting results for non-existent job ID."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        try:
            self.api_client.get_job_result(fake_job_id)
            pytest.fail("Should have raised 404 for non-existent job")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["not found", "job", "exist"],
            )
    
    def test_nonexistent_job_id_cancel(self):
        """Test cancelling non-existent job ID."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        try:
            self.api_client.cancel_job(fake_job_id)
            pytest.fail("Should have raised 404 for non-existent job")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["not found", "job", "exist"],
            )
    
    def test_nonexistent_job_id_remove(self):
        """Test removing non-existent job ID."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        try:
            self.api_client.remove_job(fake_job_id)
            pytest.fail("Should have raised 404 for non-existent job")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["not found", "job", "exist"],
            )
    
    def test_access_results_incomplete_job(self, service_provided_token: str):
        """Test accessing results for an incomplete job."""
        # Start extraction
        start_response = self.api_client.start_extraction(service_provided_token)
        job_id = start_response["job_id"]
        
        # Immediately try to get results (job should still be pending/in_progress)
        try:
            self.api_client.get_job_result(job_id)
            pytest.fail("Should have raised error for incomplete job")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 409]
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["complete", "pending", "progress", "not ready"],
            )
        finally:
            # Cleanup
            if settings.test_data_cleanup:
                try:
                    self.api_client.remove_job(job_id)
                except:
                    pass
    
    def test_cancel_completed_job(self, service_provided_token: str):
        """Test cancelling a completed job."""
        # Start extraction and wait for completion
        start_response = self.api_client.start_extraction(service_provided_token)
        job_id = start_response["job_id"]
        
        try:
            # Poll until completion
            final_status = self.api_client.poll_job_status(
                job_id,
                expected_statuses=["completed", "failed"],
            )
            
            if final_status["status"] != "completed":
                pytest.skip(f"Job {job_id} did not complete, status: {final_status['status']}")
            
            # Try to cancel completed job
            try:
                self.api_client.cancel_job(job_id)
                pytest.fail("Should have raised error for cancelling completed job")
            except requests.exceptions.HTTPError as e:
                assert e.response.status_code in [400, 409]
                error_data = e.response.json()
                APIAssertions.assert_error_message(
                    error_data,
                    ["cannot", "cancel", "completed", "state"],
                )
        finally:
            # Cleanup
            if settings.test_data_cleanup:
                try:
                    self.api_client.remove_job(job_id)
                except:
                    pass
    
    def test_malformed_request_body(self):
        """Test sending malformed request body."""
        # Try to send invalid JSON
        try:
            response = self.api_client._make_request(
                method="POST",
                endpoint="/api/v1/scan/start",
                json={"invalid": "json", "missing": "required_fields"},
            )
            # If it doesn't raise, check status code
            if response.status_code not in [400, 422]:
                pytest.fail(f"Expected 400 or 422, got {response.status_code}")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 422]
            error_data = e.response.json()
            APIAssertions.assert_error_message(
                error_data,
                ["invalid", "required", "missing", "validation"],
            )
    
    def test_job_id_injection_sql(self):
        """Test SQL injection attempt in job_id parameter."""
        # Try SQL injection pattern
        malicious_job_id = "1' OR '1'='1"
        try:
            self.api_client.get_job_status(malicious_job_id)
            # Should either return 404 or 400, not 500 (which would indicate vulnerability)
            pytest.fail("Should have raised 400 or 404 for invalid job_id")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]
            # Should not be a 500 error (which would indicate SQL injection vulnerability)
            assert e.response.status_code != 500
    
    def test_job_id_injection_long_string(self):
        """Test excessively long job_id string."""
        # Try very long string
        long_job_id = "a" * 1000
        try:
            self.api_client.get_job_status(long_job_id)
            pytest.fail("Should have raised 400 or 404 for invalid job_id")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]
    
    def test_job_id_special_characters(self):
        """Test job_id with special characters."""
        # Try special characters
        special_job_id = "../../etc/passwd"
        try:
            self.api_client.get_job_status(special_job_id)
            pytest.fail("Should have raised 400 or 404 for invalid job_id")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]
    
    def test_pagination_invalid_limit(self):
        """Test pagination with invalid limit values."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        # Test negative limit
        try:
            self.api_client.get_job_result(fake_job_id, limit=-1)
            pytest.fail("Should have raised error for negative limit")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]
        
        # Test zero limit
        try:
            self.api_client.get_job_result(fake_job_id, limit=0)
            pytest.fail("Should have raised error for zero limit")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]
        
        # Test very large limit
        try:
            self.api_client.get_job_result(fake_job_id, limit=1000000)
            # This might be valid (just return all), or might be rejected
            # Either way, should not crash
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]
    
    def test_pagination_invalid_offset(self):
        """Test pagination with invalid offset values."""
        fake_job_id = "00000000-0000-0000-0000-000000000000"
        
        # Test negative offset
        try:
            self.api_client.get_job_result(fake_job_id, offset=-1)
            pytest.fail("Should have raised error for negative offset")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code in [400, 404]

