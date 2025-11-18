"""
Services for handling extraction logic.
"""
import os
import requests
import threading
from django.utils import timezone
from .models import ExtractionJob, ExtractionRecord


class ExtractionService:
    """Service for handling data extraction from third-party APIs."""
    
    @staticmethod
    def start_extraction(api_token: str) -> ExtractionJob:
        """
        Start a new extraction job.
        
        Args:
            api_token: API token for the third-party service
            
        Returns:
            ExtractionJob instance
            
        Raises:
            ValueError: If the API token format is invalid
        """
        # Basic token validation - check if it looks like a valid HubSpot token
        if not api_token or len(api_token) < 10:
            raise ValueError("Invalid API token format")
        
        # Check if token starts with expected prefix (HubSpot tokens start with 'pat-')
        if not api_token.startswith('pat-'):
            raise ValueError("Invalid API token format. Unauthorized: Authentication failed. Token should start with 'pat-'")
        
        job = ExtractionJob.objects.create(status='pending')
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=ExtractionService._perform_extraction,
            args=(job.job_id, api_token)
        )
        thread.daemon = True
        thread.start()
        
        return job
    
    @staticmethod
    def _perform_extraction(job_id: str, api_token: str):
        """
        Perform the actual data extraction in background.
        
        Args:
            job_id: The job ID
            api_token: API token for the third-party service
        """
        try:
            job = ExtractionJob.objects.get(job_id=job_id)
            job.status = 'in_progress'
            job.save()
            
            # Simulate extraction from third-party service
            # In a real implementation, this would call the actual API
            records = ExtractionService._fetch_data_from_service(api_token)
            
            # Save records
            for record_data in records:
                ExtractionRecord.objects.create(
                    job=job,
                    email=record_data['email'],
                    first_name=record_data['first_name'],
                    last_name=record_data['last_name'],
                    id_from_service=record_data['id_from_service']
                )
            
            # Mark job as completed
            job.mark_completed(record_count=len(records))
            
        except Exception as e:
            job = ExtractionJob.objects.get(job_id=job_id)
            job.mark_failed(error_message=str(e))
    
    @staticmethod
    def _fetch_data_from_service(api_token: str) -> list:
        """
        Fetch data from the third-party service.
        
        This method makes actual API calls to the third-party service.
        Currently implements HubSpot API integration as an example.
        
        Args:
            api_token: API token for the service
            
        Returns:
            List of record dictionaries with keys: email, first_name, last_name, id_from_service
        """
        import time
        
        try:
            # HubSpot API example
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            # Fetch contacts from HubSpot
            url = 'https://api.hubapi.com/crm/v3/objects/contacts'
            params = {
                'limit': 100,
                'properties': 'email,firstname,lastname'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            records = []
            
            for contact in data.get('results', []):
                properties = contact.get('properties', {})
                records.append({
                    'email': properties.get('email', ''),
                    'first_name': properties.get('firstname', ''),
                    'last_name': properties.get('lastname', ''),
                    'id_from_service': contact.get('id', '')
                })
            
            # Simulate processing time
            time.sleep(2)
            
            return records
            
        except requests.exceptions.RequestException as e:
            # If API call fails, raise exception to mark job as failed
            raise Exception(f"Failed to fetch data from service: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing data: {str(e)}")
    
    @staticmethod
    def cancel_job(job_id: str) -> ExtractionJob:
        """
        Cancel a pending or in-progress job.
        
        Args:
            job_id: The job ID to cancel
            
        Returns:
            ExtractionJob instance
        """
        job = ExtractionJob.objects.get(job_id=job_id)
        
        if job.status not in ['pending', 'in_progress']:
            raise ValueError(f"Cannot cancel job with status: {job.status}")
        
        job.mark_cancelled()
        return job

