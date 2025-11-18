"""
Seeded Data Tests

These tests validate the core API behavior and internal logic using
pre-populated database entries. This approach removes external dependencies,
allowing for rapid, controlled, and deterministic testing.
"""
import pytest
import requests
from typing import Dict, Any

from utils.api_client import APIClient
from utils.assertions import (
    APIAssertions,
    JOB_STATUS_SCHEMA,
    EXTRACTION_RESULT_SCHEMA,
    HEALTH_SCHEMA,
)
from utils.database_seeder import DatabaseSeeder


class TestSeededDataWorkflow:
    """Test suite for seeded data workflow."""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient, db_seeder: DatabaseSeeder):
        """Setup test fixtures."""
        self.api_client = api_client
        self.db_seeder = db_seeder
        self.created_job_ids = []
    
    def teardown_method(self):
        """Cleanup after each test."""
        if settings.test_data_cleanup:
            for job_id in self.created_job_ids:
                try:
                    self.db_seeder.cleanup_job(job_id)
                except Exception as e:
                    pytest.fail(f"Failed to cleanup job {job_id}: {e}")
    
    def test_health_check(self):
        """Test that the health endpoint returns a healthy status."""
        response_data = self.api_client.health_check()
        
        APIAssertions.assert_json_schema(response_data, HEALTH_SCHEMA)
        APIAssertions.assert_health_status(response_data)
    
    def test_verify_job_status_pending(self):
        """Test verifying status of a seeded pending job."""
        # Create a pending job
        job_id = self.db_seeder.create_test_job(status="pending", record_count=0)
        self.created_job_ids.append(job_id)
        
        # Verify status
        status_response = self.api_client.get_job_status(job_id)
        
        APIAssertions.assert_json_schema(status_response, JOB_STATUS_SCHEMA)
        APIAssertions.assert_job_status(status_response, "pending", job_id)
        assert "job_id" in status_response
        assert status_response["job_id"] == job_id
    
    def test_verify_job_status_completed(self):
        """Test verifying status of a seeded completed job."""
        # Create a completed job with records
        job_id = self.db_seeder.create_test_job(
            status="completed", record_count=10
        )
        self.created_job_ids.append(job_id)
        self.db_seeder.create_test_records(job_id, count=10)
        self.db_seeder.update_job_status(job_id, "completed", record_count=10)
        
        # Verify status
        status_response = self.api_client.get_job_status(job_id)
        
        APIAssertions.assert_json_schema(status_response, JOB_STATUS_SCHEMA)
        APIAssertions.assert_job_status(status_response, "completed", job_id)
        assert status_response.get("record_count") == 10
        assert "end_time" in status_response
    
    def test_fetch_extraction_results(self):
        """Test fetching extraction results for a completed job."""
        # Create a completed job with records
        job_id = self.db_seeder.create_test_job(
            status="completed", record_count=5
        )
        self.created_job_ids.append(job_id)
        expected_records = self.db_seeder.create_test_records(job_id, count=5)
        self.db_seeder.update_job_status(job_id, "completed", record_count=5)
        
        # Fetch results
        result_response = self.api_client.get_job_result(job_id)
        
        APIAssertions.assert_json_schema(result_response, EXTRACTION_RESULT_SCHEMA)
        APIAssertions.assert_extraction_result_structure(result_response)
        APIAssertions.assert_extraction_result_count(result_response, 5)
        
        # Verify data content
        data = result_response.get("data", [])
        assert len(data) == 5
        for i, record in enumerate(data):
            assert record["email"] == expected_records[i]["email"]
            assert record["first_name"] == expected_records[i]["first_name"]
            assert record["last_name"] == expected_records[i]["last_name"]
            assert record["id_from_service"] == expected_records[i]["id_from_service"]
    
    def test_fetch_extraction_results_pagination(self):
        """Test pagination for extraction results."""
        # Create a completed job with many records
        job_id = self.db_seeder.create_test_job(
            status="completed", record_count=25
        )
        self.created_job_ids.append(job_id)
        self.db_seeder.create_test_records(job_id, count=25)
        self.db_seeder.update_job_status(job_id, "completed", record_count=25)
        
        # Fetch first page
        page1 = self.api_client.get_job_result(job_id, limit=10, offset=0)
        APIAssertions.assert_pagination(page1, expected_limit=10)
        assert len(page1.get("data", [])) == 10
        
        # Fetch second page
        page2 = self.api_client.get_job_result(job_id, limit=10, offset=10)
        APIAssertions.assert_pagination(page2, expected_limit=10)
        assert len(page2.get("data", [])) == 10
        
        # Verify no overlap
        page1_ids = {r["id_from_service"] for r in page1.get("data", [])}
        page2_ids = {r["id_from_service"] for r in page2.get("data", [])}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_list_all_jobs(self):
        """Test listing all extraction jobs."""
        # Create multiple jobs with different statuses
        pending_job = self.db_seeder.create_test_job(status="pending")
        completed_job = self.db_seeder.create_test_job(status="completed", record_count=3)
        cancelled_job = self.db_seeder.create_test_job(status="cancelled")
        
        self.created_job_ids.extend([pending_job, completed_job, cancelled_job])
        
        # List all jobs
        jobs_response = self.api_client.list_jobs()
        
        assert "data" in jobs_response or "jobs" in jobs_response
        jobs_list = jobs_response.get("data") or jobs_response.get("jobs", [])
        
        # Verify all created jobs appear in the list
        job_ids = [job.get("job_id") or job.get("id") for job in jobs_list]
        assert pending_job in job_ids
        assert completed_job in job_ids
        assert cancelled_job in job_ids
    
    def test_list_jobs_with_pagination(self):
        """Test pagination for listing jobs."""
        # Create multiple jobs
        job_ids = []
        for i in range(15):
            job_id = self.db_seeder.create_test_job(status="completed")
            job_ids.append(job_id)
            self.created_job_ids.append(job_id)
        
        # Fetch first page
        page1 = self.api_client.list_jobs(limit=10, offset=0)
        APIAssertions.assert_pagination(page1, expected_limit=10)
        
        # Fetch second page
        page2 = self.api_client.list_jobs(limit=10, offset=10)
        APIAssertions.assert_pagination(page2, expected_limit=10)
    
    def test_list_jobs_with_status_filter(self):
        """Test filtering jobs by status."""
        # Create jobs with different statuses
        pending_job = self.db_seeder.create_test_job(status="pending")
        completed_job1 = self.db_seeder.create_test_job(status="completed")
        completed_job2 = self.db_seeder.create_test_job(status="completed")
        
        self.created_job_ids.extend([pending_job, completed_job1, completed_job2])
        
        # Filter by completed status
        completed_jobs = self.api_client.list_jobs(status="completed")
        jobs_list = completed_jobs.get("data") or completed_jobs.get("jobs", [])
        
        # Verify only completed jobs are returned
        job_ids = [job.get("job_id") or job.get("id") for job in jobs_list]
        assert completed_job1 in job_ids
        assert completed_job2 in job_ids
        # Pending job should not be in filtered results
        assert pending_job not in job_ids or all(
            job.get("status") == "completed"
            for job in jobs_list
            if (job.get("job_id") or job.get("id")) == pending_job
        )
    
    def test_retrieve_job_statistics(self):
        """Test retrieving job statistics."""
        # Create jobs with different statuses
        self.db_seeder.create_test_job(status="pending")
        self.db_seeder.create_test_job(status="completed", record_count=5)
        self.db_seeder.create_test_job(status="completed", record_count=10)
        self.db_seeder.create_test_job(status="cancelled")
        
        # Get statistics
        stats_response = self.api_client.get_statistics()
        
        APIAssertions.assert_statistics_structure(stats_response)
        assert stats_response["total_jobs"] >= 4
        assert stats_response["completed_jobs"] >= 2
    
    def test_cancel_pending_job(self):
        """Test cancelling a pending job."""
        # Create a pending job
        job_id = self.db_seeder.create_test_job(status="pending")
        self.created_job_ids.append(job_id)
        
        # Cancel the job
        cancel_response = self.api_client.cancel_job(job_id)
        
        # Verify cancellation was successful
        assert cancel_response is not None
        
        # Verify status changed to cancelled
        status_response = self.api_client.get_job_status(job_id)
        APIAssertions.assert_job_status(status_response, "cancelled", job_id)
    
    def test_remove_job_data(self):
        """Test removing job data."""
        # Create a completed job with records
        job_id = self.db_seeder.create_test_job(
            status="completed", record_count=5
        )
        self.created_job_ids.append(job_id)
        self.db_seeder.create_test_records(job_id, count=5)
        self.db_seeder.update_job_status(job_id, "completed", record_count=5)
        
        # Remove the job
        self.api_client.remove_job(job_id)
        
        # Verify job no longer exists
        try:
            self.api_client.get_job_status(job_id)
            pytest.fail("Job should not exist after removal")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404

