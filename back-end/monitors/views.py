from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from .models import Server, Metric, Alarm
from .serializers import ServerSerializer, MetricSerializer, AlarmSerializer
from .tasks import check_thresholds


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email
        })
    return Response({'error': 'Identifiants incorrects.'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'message': 'Déconnecté.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    total = Server.objects.count()
    online = Server.objects.filter(is_active=True).count()
    active_alarms = Alarm.objects.filter(is_resolved=False).count()
    availability = round((online / total * 100) if total > 0 else 0)
    recent_alarms = Alarm.objects.order_by('-created_at')[:5]
    servers_status = Server.objects.all()[:5]
    return Response({
        'total_servers': total,
        'online': online,
        'alarms': active_alarms,
        'availability': availability,
        'recent_alarms': AlarmSerializer(recent_alarms, many=True).data,
        'servers_status': ServerSerializer(servers_status, many=True).data,
    })


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all().order_by('-created_at')
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submit_metrics(self, request, pk=None):
        server = self.get_object()
        cpu = request.data.get('cpu_percent')
        ram = request.data.get('ram_percent')
        disk = request.data.get('disk_percent')

        if cpu is None or ram is None or disk is None:
            return Response(
                {'error': 'cpu_percent, ram_percent and disk_percent are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        metric = Metric.objects.create(
            server=server,
            cpu_percent=float(cpu),
            ram_percent=float(ram),
            disk_percent=float(disk)
        )

        server.last_check = timezone.now()
        server.save()

        check_thresholds(server.id, float(cpu), float(ram), float(disk))

        return Response(MetricSerializer(metric).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def metrics_history(self, request, pk=None):
        server = self.get_object()
        metrics = server.metrics.all()[:20]
        return Response(MetricSerializer(metrics, many=True).data)

    @action(detail=True, methods=['get'])
    def alarms(self, request, pk=None):
        server = self.get_object()
        alarms = server.alarms.all()
        return Response(AlarmSerializer(alarms, many=True).data)


class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all().order_by('-recorded_at')
    serializer_class = MetricSerializer
    permission_classes = [IsAuthenticated]


class AlarmViewSet(viewsets.ModelViewSet):
    queryset = Alarm.objects.all().order_by('-created_at')
    serializer_class = AlarmSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active(self, request):
        active = Alarm.objects.filter(is_resolved=False).order_by('-created_at')
        return Response(AlarmSerializer(active, many=True).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alarm = self.get_object()
        alarm.is_resolved = True
        alarm.resolved_at = timezone.now()
        alarm.save()
        return Response(AlarmSerializer(alarm).data)