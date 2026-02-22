from rest_framework import serializers
from .models import Task,TaskComment


class TaskCommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email',read_only=True)

    class Meta:
        model = TaskComment
        fields = ('id','author','author_email','body','created_date')
        read_only_fields = ('id','author','author_email','created_date')


class TaskSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    comments =  TaskCommentSerializer(many=True,read_only=True)
    class Meta:
        model = Task
        fields = ('owner_email','id','owner','title','description','status','comments','due_date','created_date','updated_date')
        read_only_fields = ('id','owner','comments','created_date','updated_date')



