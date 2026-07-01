from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    ROLE_CHOICES = (

        ('VENDEUR', 'Vendeur'),

        ('ADMIN', 'Admin'),
    )

    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default="VENDEUR")

    phone = models.CharField(max_length=20,blank=True)
    address = models.TextField(blank=True)

    def __str__(self):

        return self.username