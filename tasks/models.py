from django.db import models
from django.conf import settings

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'todo','To Do'
        IN_PROGRESS = 'in_progress','In Progress'
        DONE = 'done','Done'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    due_date = models.DateTimeField(null=True,blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status'],name='task_status_idx'),
            models.Index(fields=['created_date'],name='task_created_idx'),
            models.Index(fields=['owner','-created_date'],name='task_owner_created_idx')
        ]


    def __str__(self):
        # Return the title for admin and display usage.
        return self.title
    
class TaskComment(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='task_comment')
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f'Comment #{self.id} on task #{self.task.id}'