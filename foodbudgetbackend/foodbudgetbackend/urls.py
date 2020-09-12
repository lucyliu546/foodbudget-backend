"""foodbudgetbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from budget import views
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token

router = routers.DefaultRouter()
# router.register(modelname, viewname)
router.register(r'budgets', views.BudgetsAPI, 'budgets')
router.register(r'expenses', views.AllExpensesAPI, 'expenses')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('token-auth/', obtain_jwt_token),
    path('token-auth/verify/', verify_jwt_token),
    path('token-auth/refresh/', refresh_jwt_token),
    path('current_user/', views.current_user),
    path('users/', views.UserList.as_view()),
    path('sumexpenses/', views.ExpensesAPI.as_view()),
]
