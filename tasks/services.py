from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from tasks.models import Task, TaskComment

def create_task_with_first_comment(*,owner,title,description="",status=Task.Status.TODO,due_date=None,comment_body=None,):
    with transaction.atomic():
        task = Task.objects.create(
            owner=owner,
            title=title,
            description=description,
            status=status,
            due_date=due_date,
        )
        if comment_body:
            TaskComment.objects.create(
                task=task,
                author=owner,
                body=comment_body,
            )
    return task

def get_task_stats_for_user(user):
    qs = Task.objects.all() if (user.is_staff or user.is_superuser) else Task.objects.filter(owner=user)

    by_status = dict(
        qs.values_list('status').annotate(c=Count('id'))
    )

    over_due = qs.filter(due_date__lt=timezone.now()).exclude(status=Task.Status.DONE).count()

    return {
        'total tasks': qs.count(),
        'by_status': by_status,
        'over_due': over_due,
    }