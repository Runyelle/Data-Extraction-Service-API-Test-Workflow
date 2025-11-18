"""
Database seeding utilities for seeded data tests.

NOTE: This module requires database access. If you don't have direct database access,
you may need to use an API endpoint to seed data, or skip seeded data tests.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from config import settings

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """
    Utility class for seeding test data into the database.
    
    This class provides methods to create test jobs and associated data.
    If direct database access is not available, you may need to implement
    an alternative seeding mechanism via API endpoints.
    """
    
    def __init__(self):
        """Initialize the database seeder."""
        self.db_connection = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection if credentials are available."""
        if all([
            settings.db_host,
            settings.db_name,
            settings.db_user,
            settings.db_password,
        ]):
            try:
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                connection_string = (
                    f"postgresql://{settings.db_user}:{settings.db_password}"
                    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
                )
                engine = create_engine(connection_string)
                Session = sessionmaker(bind=engine)
                self.db_connection = Session()
                logger.info("Database connection established for seeding")
            except Exception as e:
                logger.warning(
                    f"Could not establish database connection: {e}. "
                    "Seeded data tests may need to use API endpoints instead."
                )
        else:
            logger.warning(
                "Database credentials not configured. "
                "Seeded data tests may need to use API endpoints instead."
            )
    
    def create_test_job(
        self,
        status: str = "pending",
        record_count: int = 0,
        connection_id: Optional[str] = None,
    ) -> str:
        """
        Create a test job in the database.
        
        Args:
            status: Job status (pending, in_progress, completed, cancelled, failed)
            record_count: Number of records associated with this job
            connection_id: Optional connection ID (generated if not provided)
        
        Returns:
            The job_id of the created job
        """
        job_id = str(uuid.uuid4())
        connection_id = connection_id or str(uuid.uuid4())
        
        if self.db_connection:
            # Direct database insertion
            try:
                # NOTE: Adjust table and column names based on your actual schema
                from sqlalchemy import text
                self.db_connection.execute(
                    text("""
                        INSERT INTO extraction_jobs (
                            job_id, connection_id, status, record_count,
                            start_time, created_at
                        ) VALUES (:job_id, :connection_id, :status, :record_count, :start_time, :created_at)
                    """),
                    {
                        "job_id": job_id,
                        "connection_id": connection_id,
                        "status": status,
                        "record_count": record_count,
                        "start_time": datetime.utcnow(),
                        "created_at": datetime.utcnow(),
                    },
                )
                self.db_connection.commit()
                logger.info(f"Created test job {job_id} with status {status}")
            except Exception as e:
                self.db_connection.rollback()
                logger.error(f"Error creating test job: {e}")
                raise
        else:
            logger.warning(
                "No database connection available. "
                "You may need to seed data via API endpoints or configure database access."
            )
        
        return job_id
    
    def create_test_records(
        self,
        job_id: str,
        count: int,
        start_index: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Create test extraction records for a job.
        
        Args:
            job_id: The job ID to associate records with
            count: Number of records to create
            start_index: Starting index for generating test data
        
        Returns:
            List of created record dictionaries
        """
        records = []
        for i in range(count):
            record = {
                "email": f"test{start_index + i}@example.com",
                "first_name": f"First{start_index + i}",
                "last_name": f"Last{start_index + i}",
                "id_from_service": f"service_id_{start_index + i}",
            }
            records.append(record)
        
        if self.db_connection:
            try:
                # NOTE: Adjust table and column names based on your actual schema
                from sqlalchemy import text
                for record in records:
                    self.db_connection.execute(
                        text("""
                            INSERT INTO extraction_records (
                                job_id, email, first_name, last_name, id_from_service, created_at
                            ) VALUES (:job_id, :email, :first_name, :last_name, :id_from_service, :created_at)
                        """),
                        {
                            "job_id": job_id,
                            **record,
                            "created_at": datetime.utcnow(),
                        },
                    )
                self.db_connection.commit()
                logger.info(f"Created {count} test records for job {job_id}")
            except Exception as e:
                self.db_connection.rollback()
                logger.error(f"Error creating test records: {e}")
                raise
        
        return records
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        record_count: Optional[int] = None,
    ):
        """Update the status of a test job."""
        if self.db_connection:
            try:
                update_data = {
                    "status": status,
                    "updated_at": datetime.utcnow(),
                }
                if status == "completed":
                    update_data["end_time"] = datetime.utcnow()
                if record_count is not None:
                    update_data["record_count"] = record_count
                
                from sqlalchemy import text
                self.db_connection.execute(
                    text("""
                        UPDATE extraction_jobs
                        SET status = :status, updated_at = :updated_at,
                            end_time = :end_time, record_count = :record_count
                        WHERE job_id = :job_id
                    """),
                    {
                        "job_id": job_id,
                        **update_data,
                        "end_time": update_data.get("end_time"),
                        "record_count": update_data.get("record_count"),
                    },
                )
                self.db_connection.commit()
                logger.info(f"Updated job {job_id} status to {status}")
            except Exception as e:
                self.db_connection.rollback()
                logger.error(f"Error updating job status: {e}")
                raise
    
    def cleanup_job(self, job_id: str):
        """Remove a test job and its associated records."""
        if self.db_connection:
            try:
                from sqlalchemy import text
                # Delete records first (foreign key constraint)
                self.db_connection.execute(
                    text("DELETE FROM extraction_records WHERE job_id = :job_id"),
                    {"job_id": job_id},
                )
                # Delete job
                self.db_connection.execute(
                    text("DELETE FROM extraction_jobs WHERE job_id = :job_id"),
                    {"job_id": job_id},
                )
                self.db_connection.commit()
                logger.info(f"Cleaned up job {job_id}")
            except Exception as e:
                self.db_connection.rollback()
                logger.error(f"Error cleaning up job: {e}")
                raise
    
    def cleanup_all_test_data(self):
        """Remove all test data (use with caution)."""
        if self.db_connection:
            try:
                from sqlalchemy import text
                # This is a destructive operation - use only in test environments
                self.db_connection.execute(text("DELETE FROM extraction_records"))
                self.db_connection.execute(text("DELETE FROM extraction_jobs"))
                self.db_connection.commit()
                logger.info("Cleaned up all test data")
            except Exception as e:
                self.db_connection.rollback()
                logger.error(f"Error cleaning up test data: {e}")
                raise
    
    def close(self):
        """Close the database connection."""
        if self.db_connection:
            self.db_connection.close()
            logger.info("Database connection closed")

