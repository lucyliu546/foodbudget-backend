from django.contrib import admin
from .models import Budgets, Expenses
# Register your models here.
admin.site.register(Budgets)
admin.site.register(Expenses)