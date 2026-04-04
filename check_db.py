import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pest_Classifier.settings')
django.setup()

from users.models import UserRegistrationModel

users = UserRegistrationModel.objects.all()
for u in users:
    print(u.id, u.name, u.loginid, u.password, u.mobile, u.email, u.status)
