from rest_framework.throttling import UserRateThrottle

class TaskWriteRateThrottle(UserRateThrottle):
    scope = 'task_write'