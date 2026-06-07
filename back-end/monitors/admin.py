from django.contrib import admin
from .models import Server, Metric, Alarm


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'server_type', 'is_active', 'last_check']
    list_filter = ['server_type', 'is_active']
    search_fields = ['name', 'ip_address']


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['server', 'cpu_percent', 'ram_percent', 'disk_percent', 'recorded_at']
    list_filter = ['server']
    readonly_fields = ['recorded_at']


@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ['server', 'alarm_type', 'severity', 'is_resolved', 'created_at']
    list_filter = ['severity', 'is_resolved', 'alarm_type']
    search_fields = ['server__name', 'message']
    readonly_fields = ['created_at']