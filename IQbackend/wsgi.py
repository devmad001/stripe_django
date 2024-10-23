"""
WSGI config for IQbackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
# import sys


from django.core.wsgi import get_wsgi_application


# sys.setrecursionlimit(100)  # Set recursion limit to a higher value

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IQbackend.settings')

application = get_wsgi_application()
