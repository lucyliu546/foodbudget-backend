"""
WSGI config for foodbudgetbackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import os
import time
import traceback
import signal
import sys
from django.core.wsgi import get_wsgi_application




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodbudgetbackend.foodbudgetbackend.settings')

application = get_wsgi_application()

