"""
Models for the extraction app.
"""
import uuid
from django.db import models
from django.utils import timezone


class ExtractionJob(models.Model):
    """Model representing an extraction job."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection_id = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    record_count = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'extraction_jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job {self.job_id} - {self.status}"
    
    def mark_completed(self, record_count=0):
        """Mark job as completed."""
        self.status = 'completed'
        self.record_count = record_count
        self.end_time = timezone.now()
        self.save()
    
    def mark_failed(self, error_message=None):
        """Mark job as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.end_time = timezone.now()
        self.save()
    
    def mark_cancelled(self):
        """Mark job as cancelled."""
        self.status = 'cancelled'
        self.end_time = timezone.now()
        self.save()


class ExtractionRecord(models.Model):
    """Model representing an extracted record."""
    
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(ExtractionJob, on_delete=models.CASCADE, related_name='records')
    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    id_from_service = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'extraction_records'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.email} - {self.id_from_service}"

