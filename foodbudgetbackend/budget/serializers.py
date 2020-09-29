from .models import Budgets, Expenses
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from django.db import models


    

class ExpensesSerializer(serializers.ModelSerializer):
    total_expenses = serializers.DecimalField(decimal_places=2, max_digits=20, read_only=True)
    class Meta:
        model = Expenses
        fields = "__all__"
    
class ExpensesAllSerializer(serializers.ModelSerializer):
    budget = serializers.SerializerMethodField('get_budget_name')
    """ def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(ExpensesAllSerializer, self).__init__(many=many, *args, **kwargs) """
    def get_budget_name(self, obj):
        return obj.bID.bName
    class Meta:
        model = Expenses
        fields = ("budget", "eDate", "eAmount", "eID", "bID", "eUser", "eName")


class BudgetsSerializer(serializers.ModelSerializer):
    total_expenses = serializers.DecimalField(decimal_places=2, max_digits=20, read_only=True)
    class Meta:
        model = Budgets
        fields = ("bName", "bAmount", "total_expenses", "bUser", "bID")



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'id')

class UserSerializerWithToken(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(method_name='get_token') # create custom field for token
    password = serializers.CharField(write_only=True) # passwords should not be readable 

    def get_token(self, obj): # payload is the user being tokenized
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):  # overwrite create to call set_password to properly hash the password
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password')