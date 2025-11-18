"""
URL configuration for extraction app.
"""
from django.urls import path
from . import views

app_name = 'extraction'

urlpatterns = [
    path('health', views.health_check, name='health'),
    path('scan/start', views.start_extraction, name='start_extraction'),
    path('scan/status/<uuid:job_id>', views.get_job_status, name='get_job_status'),
    path('scan/result/<uuid:job_id>', views.get_job_result, name='get_job_result'),
    path('scan/cancel/<uuid:job_id>', views.cancel_job, name='cancel_job'),
    path('scan/remove/<uuid:job_id>', views.remove_job, name='remove_job'),
    path('jobs/jobs', views.list_jobs, name='list_jobs'),
    path('jobs/statistics', views.get_statistics, name='get_statistics'),
]

