from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from .throttles import TaskWriteRateThrottle
from .permissions import IsOwnerOrReadOnly
from .services import get_task_stats_for_user
from django.db.models import Count, Max, OuterRef, Subquery


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title','description']
    ordering_fields = ['created_date','due_date','updated_date']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        base_qs = Task.objects.select_related('owner').prefetch_related('comments','comments__author').order_by('-created_date')
        if user.is_staff or user.is_superuser:
            return base_qs
        return base_qs.filter(owner=user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_throttles(self):
        if self.action in ['create','update','partial_update','destroy']:
            return[TaskWriteRateThrottle()]
        return[]
    @action(detail=False,methods=['get'],permission_classes=[permissions.IsAuthenticated])
    def stats(self,request):
        return Response(get_task_stats_for_user(request.user))




