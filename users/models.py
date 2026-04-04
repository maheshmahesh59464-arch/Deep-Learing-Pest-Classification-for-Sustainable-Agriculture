from django.db import models

class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=10)  # Adjusted max_length to 10 for mobile numbers
    email = models.EmailField(unique=True, max_length=100)  # Use EmailField for better validation
    locality = models.CharField(max_length=100)
    address = models.TextField(max_length=1000)  # Use TextField for longer addresses
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default='waiting')

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'user_registrations'


class PestPredictionModel(models.Model):
    user = models.ForeignKey(UserRegistrationModel, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='predictions/')
    predicted_class = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    harmful_percentage = models.FloatField(default=0.0, null=True, blank=True)
    eco_solution = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.loginid} - {self.predicted_class}"

    class Meta:
        db_table = 'pest_predictions'

