# Create your tasks here

from celery import shared_task


# Example code
@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y
