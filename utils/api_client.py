"""
API Client utility for making requests to the Data Extraction Service.
"""
import time
import logging
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import settings

logger = logging.getLogger(__name__)


class APIClient:
    """Client for interacting with the Data Extraction Service API."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = base_url or settings.api_base_url
        self.timeout = timeout or settings.api_timeout
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        
        logger.info(f"{method} {url}")
        if json:
            logger.debug(f"Request body: {json}")
        if params:
            logger.debug(f"Request params: {params}")
        
        response = self.session.request(
            method=method,
            url=url,
            json=json,
            params=params,
            headers=request_headers,
            timeout=self.timeout,
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text[:500]}")  # Log first 500 chars
        
        return response
    
    def start_extraction(self, api_token: str) -> Dict[str, Any]:
        """Start a new extraction job."""
        response = self._make_request(
            method="POST",
            endpoint="/api/v1/scan/start",
            json={"api_token": api_token},
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of an extraction job."""
        response = self._make_request(
            method="GET",
            endpoint=f"/api/v1/scan/status/{job_id}",
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_result(
        self,
        job_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get the results of a completed extraction job."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        
        response = self._make_request(
            method="GET",
            endpoint=f"/api/v1/scan/result/{job_id}",
            params=params if params else None,
        )
        response.raise_for_status()
        return response.json()
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a pending or in-progress extraction job."""
        response = self._make_request(
            method="POST",
            endpoint=f"/api/v1/scan/cancel/{job_id}",
        )
        response.raise_for_status()
        return response.json()
    
    def remove_job(self, job_id: str) -> None:
        """Remove extraction data for a job."""
        response = self._make_request(
            method="DELETE",
            endpoint=f"/api/v1/scan/remove/{job_id}",
        )
        response.raise_for_status()
        # DELETE might return 204 No Content, which has no body
        if response.status_code == 204:
            return {}
        return response.json() if response.content else {}
    
    def list_jobs(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all extraction jobs."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status:
            params["status"] = status
        
        response = self._make_request(
            method="GET",
            endpoint="/api/v1/jobs/jobs",
            params=params if params else None,
        )
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about all extraction jobs."""
        response = self._make_request(
            method="GET",
            endpoint="/api/v1/jobs/statistics",
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health status of the API."""
        response = self._make_request(
            method="GET",
            endpoint="/api/v1/health",
        )
        response.raise_for_status()
        return response.json()
    
    def poll_job_status(
        self,
        job_id: str,
        expected_statuses: List[str] = ["completed", "failed"],
        max_attempts: Optional[int] = None,
        interval: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Poll job status until it reaches an expected status.
        
        Args:
            job_id: The job ID to poll
            expected_statuses: List of statuses to wait for (default: ["completed", "failed"])
            max_attempts: Maximum number of polling attempts (default: from settings)
            interval: Seconds between polls (default: from settings)
        
        Returns:
            The final job status response
        
        Raises:
            TimeoutError: If max_attempts is reached without reaching expected status
        """
        max_attempts = max_attempts or settings.max_poll_attempts
        interval = interval or settings.poll_interval_seconds
        
        for attempt in range(max_attempts):
            try:
                status_response = self.get_job_status(job_id)
                current_status = status_response.get("status")
                
                if current_status in expected_statuses:
                    logger.info(
                        f"Job {job_id} reached expected status: {current_status} "
                        f"(after {attempt + 1} attempts)"
                    )
                    return status_response
                
                logger.debug(
                    f"Job {job_id} status: {current_status} "
                    f"(attempt {attempt + 1}/{max_attempts})"
                )
                
                if attempt < max_attempts - 1:
                    time.sleep(interval)
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error polling job status (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(interval)
                else:
                    raise
        
        # If we get here, we've exhausted all attempts
        final_status = self.get_job_status(job_id)
        raise TimeoutError(
            f"Job {job_id} did not reach expected statuses {expected_statuses} "
            f"within {max_attempts} attempts. Final status: {final_status.get('status')}"
        )

