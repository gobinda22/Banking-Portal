from django.db import models
# Create your models here.

class Customer_data(models.Model):
    cust_ID =models.AutoField(primary_key = True)
    Name = models.CharField(max_length = 200)
    phn_no = models.CharField(max_length = 80)
    Email = models.EmailField()
    class Meta:
        db_table = 'customer'

class Account_data(models.Model):
    Account_no = models.IntegerField(primary_key = True)
    owner = models.ForeignKey(Customer_data, on_delete = models.CASCADE)
    Balance = models.FloatField()
    class meta:
        db_table = 'account'

class Transactions(models.Model):
    T_ID = models.AutoField(primary_key = True)
    Account_no = models.ForeignKey(Account_data, on_delete=models.CASCADE)
    Amount = models.FloatField()
    Type = models.CharField(max_length=30)
    class Meta:
        db_table = 'transactions'
        
class Money_Transfer(models.Model):
    T_ID = models.AutoField(primary_key = True)
    From_accno = models.ForeignKey(Account_data, on_delete = models.CASCADE, related_name = 'From_accno')
    To_accno = models.ForeignKey(Account_data, on_delete=models.CASCADE, related_name = 'To_accno')  
    Amount = models.FloatField()
    class Meta:
        db_table = 'transfers'

            
