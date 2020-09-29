from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Budgets(models.Model): 
    bID = models.AutoField(primary_key=True)
    bChoices = [('Grocery', 'Grocery'), 
                    ('Fast Food','Fast Food'), 
                    ('Restaurants', 'Restaurants'), 
                    ('Bars', 'Bars'),
                    ('Coffee', 'Coffee'),
                    ('Dessert', 'Dessert')]
    bName = models.CharField(max_length=40, choices=bChoices, default='Grocery')
    bAmount = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    bUser = models.ForeignKey(User, related_name="budget_owner", on_delete=models.CASCADE)

class Expenses(models.Model):
    eID = models.AutoField(primary_key=True)
    eName = models.CharField(max_length=100, null=True)
    eAmount = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    eDate = models.DateField()
    bID = models.ForeignKey(Budgets, related_name='budget', null=True, on_delete=models.SET_NULL)
    eUser = models.ForeignKey(User, related_name="expense_owner", null=True, on_delete=models.CASCADE)


