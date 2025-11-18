"""
Serializers for the extraction app.
"""
from rest_framework import serializers
from .models import ExtractionJob, ExtractionRecord


class ExtractionRecordSerializer(serializers.ModelSerializer):
    """Serializer for extraction records."""
    
    class Meta:
        model = ExtractionRecord
        fields = ['email', 'first_name', 'last_name', 'id_from_service']


class ExtractionJobSerializer(serializers.ModelSerializer):
    """Serializer for extraction jobs."""
    
    class Meta:
        model = ExtractionJob
        fields = [
            'job_id', 'connection_id', 'status', 'record_count',
            'start_time', 'end_time', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'job_id', 'connection_id', 'status', 'record_count',
            'start_time', 'end_time', 'error_message', 'created_at', 'updated_at'
        ]


class StartExtractionSerializer(serializers.Serializer):
    """Serializer for starting an extraction."""
    api_token = serializers.CharField(
        required=True, 
        write_only=True,
        allow_blank=False,
        error_messages={
            'required': 'API token is required. Invalid or missing API token provided.',
            'blank': 'API token cannot be blank. Invalid or missing API token provided.'
        }
    )


class ExtractionResultSerializer(serializers.Serializer):
    """Serializer for extraction results."""
    data = ExtractionRecordSerializer(many=True)
    total = serializers.IntegerField()
    limit = serializers.IntegerField(required=False)
    offset = serializers.IntegerField(required=False)
    next = serializers.URLField(required=False, allow_null=True)


class JobListSerializer(serializers.Serializer):
    """Serializer for job list response."""
    data = ExtractionJobSerializer(many=True)
    total = serializers.IntegerField()
    limit = serializers.IntegerField(required=False)
    offset = serializers.IntegerField(required=False)
    next = serializers.URLField(required=False, allow_null=True)


class StatisticsSerializer(serializers.Serializer):
    """Serializer for job statistics."""
    total_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    pending_jobs = serializers.IntegerField()
    cancelled_jobs = serializers.IntegerField()
    average_extraction_time = serializers.FloatField(required=False, allow_null=True)

