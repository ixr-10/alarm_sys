from django.db import models

class Server(models.Model):
    SERVER_TYPES = [('linux','Linux'),('windows','Windows'),('other','Other')]
    STATUS = [('online','Online'),('offline','Offline'),('warning','Warning')]

    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    server_type = models.CharField(max_length=20, choices=SERVER_TYPES, default='linux')
    description = models.TextField(blank=True)
    cpu_threshold = models.IntegerField(default=80)
    ram_threshold = models.IntegerField(default=85)
    disk_threshold = models.IntegerField(default=90)
    is_active = models.BooleanField(default=True)
    last_check = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='metrics')
    cpu_percent = models.FloatField()
    ram_percent = models.FloatField()
    disk_percent = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

class Alarm(models.Model):
    SEVERITY = [('low','Low'),('medium','Medium'),('critical','Critical')]
    TYPE = [('CPU','CPU'),('RAM','RAM'),('DISK','Disk'),('SERVICE','Service'),('UNREACHABLE','Unreachable')]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='alarms')
    alarm_type = models.CharField(max_length=20, choices=TYPE)
    severity = models.CharField(max_length=10, choices=SEVERITY)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.alarm_type} on {self.server.name}"