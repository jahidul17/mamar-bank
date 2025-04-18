from django.db import models
from django.contrib.auth.models import User
from .constants import Gender_Type,Account_Type 


# Create your models here.
class UserBankAccount(models.Model):
    user=models.OneToOneField(User,related_name='account',on_delete=models.CASCADE)
    account_type=models.CharField(max_length=10,choices=Account_Type)
    account_no=models.IntegerField(unique=True)
    birth_date=models.DateField(null=True,blank=True)
    gender=models.CharField(max_length=10,choices=Gender_Type)
    initial_deposite_date=models.DateField(auto_now_add=True)
    balance=models.DecimalField(default=0,max_digits=12,decimal_places=2)
    #akjon user 12 digit er taka rakte parbe and decimal 2 digit porjonto
    def __str__(self):
        return str(self.account_no)
    

class UserAddress(models.Model):
    user=models.OneToOneField(User,related_name='address',on_delete=models.CASCADE)
    street_address=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    postal_code=models.IntegerField()
    country=models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.email
    
        
