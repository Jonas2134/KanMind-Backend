from functools import wraps

from django.http import Http404
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

def handle_task_exceptions(action: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                return func(self, request, *args, **kwargs)
            except Http404:
                return Response(
                    {'detail': 'Task not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except (DjangoPermissionDenied, DRFPermissionDenied) as e:
                return Response(
                    {'detail': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except Exception:
                msg = f'Internal server error when {action} comment.'
                return Response(
                    {'detail': msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator
