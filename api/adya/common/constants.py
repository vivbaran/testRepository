import os

AAPI_HOST = os.environ.get('API_HOST', 'http://localhost:5000')
REDIRECT_STATUS = os.environ.get('REDIRECT_STATUS', 'http://localhost:3000/success')

