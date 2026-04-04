import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pest_Classifier.settings')
django.setup()

from django.test import Client

client = Client(enforce_csrf_checks=False, HTTP_HOST='127.0.0.1')

response = client.post('/UserRegisterForm', {
    'name': 'Test User',
    'loginid': 'testu123',
    'password': 'password123',
    'mobile': '0123456789',
    'email': 't3@example.com',
    'locality': 'Test Loc',
    'address': 'Test Addr',
    'city': 'Test City',
    'state': 'Test State'
})

print("Status Code:", response.status_code)
if response.status_code == 302:
    print("Redirected to:", response.url)
else:
    print(response.content.decode('utf-8'))
