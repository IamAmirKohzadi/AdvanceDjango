from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    class Meta:
        model = Task
        fields = ('owner_email','id','owner','title','description','status','due_date','created_date','updated_date')
        read_only_fields = ('id','owner','created_date','updated_date')


