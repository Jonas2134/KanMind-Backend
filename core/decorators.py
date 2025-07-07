from functools import wraps

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework import status

def handle_exceptions(action: str):
    """
    Decorator factory to wrap view methods and handle common exceptions uniformly.

    The returned decorator catches:
      - NotFound: returns HTTP 404 with the exception's detail.
      - PermissionDenied (Django or DRF): returns HTTP 403 with the exception message.
      - ValidationError: lets DRF handle it (will typically return HTTP 400).
      - Any other Exception: returns HTTP 500 with a generic message including the action.

    Args:
        action (str): A description of the action being performed (e.g., 'creating board'),
                      used to format the internal server error message.

    Returns:
        function: A decorator that wraps a view method, handling the above exceptions.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                return func(self, request, *args, **kwargs)
            except NotFound as e:
                return Response({'detail': e.detail}, status=status.HTTP_404_NOT_FOUND)
            except (DjangoPermissionDenied, DRFPermissionDenied) as e:
                return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
            except ValidationError as e:
                raise e
            except Exception:
                msg = f'Internal server error when {action}.'
                return Response({'detail': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return wrapper
    return decorator
