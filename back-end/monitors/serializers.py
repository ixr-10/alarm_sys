from rest_framework import serializers
from .models import Server, Metric, Alarm

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = '__all__'

class AlarmSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)

    class Meta:
        model = Alarm
        fields = '__all__'

class ServerSerializer(serializers.ModelSerializer):
    latest_metric = serializers.SerializerMethodField()
    alarm_count = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = '__all__'

    def get_latest_metric(self, obj):
        m = obj.metrics.first()
        if m:
            return MetricSerializer(m).data
        return None

    def get_alarm_count(self, obj):
        return obj.alarms.filter(is_resolved=False).count()

    def get_status(self, obj):
        if not obj.is_active:
            return 'offline'
        m = obj.metrics.first()
        if not m:
            return 'online'
        if (m.cpu_percent > obj.cpu_threshold or
            m.ram_percent > obj.ram_threshold or
            m.disk_percent > obj.disk_threshold):
            return 'warning'
        return 'online'