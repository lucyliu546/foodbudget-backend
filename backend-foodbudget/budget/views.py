from django.shortcuts import render
from .serializers import BudgetsSerializer, ExpensesSerializer, ExpensesAllSerializer
from .models import Budgets, Expenses
from django.db.models import Sum, Count, F
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, viewsets
from .serializers import UserSerializer, UserSerializerWithToken
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import datetime
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncMonth
import datetime
import calendar

# Create your views here.

class BudgetsAPI(viewsets.ModelViewSet):
    """
    Returns list of budgets and total expenses formatted as JSON objects
    [
        {
            "bName": "Bars",
            "bAmount": "200.00",
            "total_expenses": "115.58",
            "bUser": 1
        },
        {
            "bName": "Grocery",
            "bAmount": "600.00",
            "total_expenses": "11.98",
            "bUser": 1
        }
    ]
    """
    
    serializer_class = BudgetsSerializer
    def get_queryset(self):
        req = self.request
        user = req.user
        if req.query_params.get('startdate'):
            start_date = datetime.datetime.strptime(req.query_params.get('startdate'), '%Y-%m-%d')
            end_date =  datetime.datetime.strptime(req.query_params.get('enddate'), '%Y-%m-%d')
            
            return Budgets.objects.filter(bUser=user).annotate(total_expenses = Coalesce(Sum('budget__eAmount', filter=Q(budget__eDate__gte=start_date, budget__eDate__lte=end_date)), 0))
        return Budgets.objects.filter(bUser=user).annotate(total_expenses = Sum('budget__eAmount'))

class AllExpensesAPI(viewsets.ModelViewSet):
    
    serializer_class = ExpensesAllSerializer

    def create(self, request, *args, **kwargs):
        many = True if isinstance(request.data, list) else False
        serializer = ExpensesAllSerializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response( 
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        user = self.request.user 
        return Expenses.objects.filter(eUser=user)
        
        
class ExpensesAPI(APIView):
    """
        Returns dictionary of expenses (includes individual and sum)
        For individual expenses add ?format=json&type=all to url
    """
    def get(self, request, format=None):
        user = request.user
        # determines if a date filter is used
        if request.query_params.get('startdate'):
            start_date = datetime.datetime.strptime(request.query_params.get('startdate'), '%Y-%m-%d')
            end_date =  datetime.datetime.strptime(request.query_params.get('enddate'), '%Y-%m-%d')
            print(start_date, end_date)
            budget_list = Expenses.objects.values_list('bID__bName', flat=True).distinct()
            group_by_value = {}
            date_list = Expenses.objects.filter(eUser=user).filter(eDate__gte=start_date, eDate__lte=end_date).order_by('eDate').values_list('eDate', flat=True).distinct()
            print(date_list)
        else:
            budget_list = Expenses.objects.values_list('bID__bName', flat=True).distinct()
            group_by_value = {}

        # determines if the filter is annual or monthly
        if request.query_params.get('datetype') == 'Annually':
            date_list = Expenses.objects.filter(eUser=user).filter(eDate__gte=start_date, eDate__lte=end_date).annotate(month = TruncMonth('eDate')).values_list('month', flat=True).order_by('month').distinct('month')
            date_list = [str(s.month) for s in date_list]
            print(date_list)
                
        else:
            date_list = Expenses.objects.filter(eUser=user).values_list('eDate', flat=True).order_by('eDate').distinct()
            date_list = [str(s) for s in date_list]
        
        
        # below groups individual expenses by budget then date
        if request.query_params.get('type') == 'all':
            for budget in budget_list:
                group_by_value[budget] = {
                        Expenses.objects.filter(eUser=user).filter(bID__bName = budget).filter(eDate__gte=start_date, eDate__lte=end_date).order_by('eDate').values() 
                    }
                
                
        # below aggregates total expenses by date then budget
        else:
            if request.query_params.get('datetype') == 'Annually':
                for d in date_list:
                    budget_list = Expenses.objects.filter(eUser=user).filter(eDate__gte=start_date, eDate__lte=end_date).filter(eDate__month=d).values_list('bID__bName', flat=True).distinct()
                    
                    group_by_value[d] = {}
                    for budget in budget_list:
                        group_by_value[d][budget] = {
                            Expenses.objects.filter(eUser=user).filter(bID__bName = budget).filter(eDate__month = d).aggregate(total_expenses = Sum('eAmount')).values()
                            # 'all_expenses': Expenses.objects.filter(eUser=user).filter(bID__bName = value).filter(eDate = date).values() 
                        } 
                
            else:
                 for d in date_list:
                    budget_list = Expenses.objects.filter(eUser=user).filter(eDate=d).values_list('bID__bName', flat=True).distinct()
                    
                    group_by_value[d] = {}
                    for budget in budget_list:
                        group_by_value[d][budget] = {
                            Expenses.objects.filter(eUser=user).filter(bID__bName = budget).filter(eDate = d).aggregate(total_expenses = Sum('eAmount')).values()
                            # 'all_expenses': Expenses.objects.filter(eUser=user).filter(bID__bName = value).filter(eDate = date).values() 
                        } 
        
        # below groups individual expenses by date then budget
        """ if request.query_params.get('type') == 'all':
            for date in date_list:
                budget_list = Expenses.objects.filter(eUser=user).filter(eDate=date).values_list('bID__bName', flat=True).distinct()
                group_by_value[date] = {}
                for budget in budget_list:
                    group_by_value[date][budget] = {
                        Expenses.objects.filter(eUser=user).filter(bID__bName = budget).filter(eDate = date).values() 
                    }
        """
        
        return Response(group_by_value)
    
    def post(self, request):
        expense = request.data.get('expense')
        serializer = ExpensesSerializer(data = expense)
        if serializer.is_valid(raise_exception=True):
            expense_saved = serializer.save()
        return Response({'success': "expense '{}' created successfully".format(expense_saved)})


@api_view(['GET'])
def current_user(request): 
    """
    Use this view when a user revisits the site, reloads, etc. 
    """
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)