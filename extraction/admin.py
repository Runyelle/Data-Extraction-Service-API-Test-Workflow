"""
Admin configuration for extraction app.
"""
from django.contrib import admin
from .models import ExtractionJob, ExtractionRecord


@admin.register(ExtractionJob)
class ExtractionJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'status', 'record_count', 'start_time', 'end_time', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['job_id', 'connection_id']
    readonly_fields = ['job_id', 'connection_id', 'created_at', 'updated_at']


@admin.register(ExtractionRecord)
class ExtractionRecordAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'id_from_service', 'job', 'created_at']
    list_filter = ['created_at', 'job__status']
    search_fields = ['email', 'first_name', 'last_name', 'id_from_service']
    readonly_fields = ['created_at']

