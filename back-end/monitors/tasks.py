from celery import shared_task
from django.utils import timezone
from .models import Server, Alarm


def check_thresholds(server_id, cpu, ram, disk):
    """Check metric values against thresholds and create alarms if needed."""
    try:
        server = Server.objects.get(id=server_id)
        checks = [
            ('CPU', cpu, server.cpu_threshold),
            ('RAM', ram, server.ram_threshold),
            ('DISK', disk, server.disk_threshold),
        ]
        for alarm_type, value, threshold in checks:
            if value > threshold:
                severity = 'critical' if value > threshold + 10 else 'medium'
                Alarm.objects.create(
                    server=server,
                    alarm_type=alarm_type,
                    severity=severity,
                    message=f"{alarm_type} à {value:.1f}% (seuil: {threshold}%)"
                )
            else:
                Alarm.objects.filter(
                    server=server,
                    alarm_type=alarm_type,
                    is_resolved=False
                ).update(is_resolved=True, resolved_at=timezone.now())
    except Server.DoesNotExist:
        pass


@shared_task
def monitor_all_servers():
    """
    Periodic task that checks all active servers.
    Since we use manual metric entry, this just logs active servers.
    You can extend this to auto-check via SSH if needed later.
    """
    servers = Server.objects.filter(is_active=True)
    for server in servers:
        if server.last_check is None:
            Alarm.objects.get_or_create(
                server=server,
                alarm_type='SERVICE',
                is_resolved=False,
                defaults={
                    'severity': 'low',
                    'message': f"Aucune métrique reçue pour {server.name}"
                }
            )
    return f"Checked {servers.count()} servers"