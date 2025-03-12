from django.urls import path
from . import views

urlpatterns = [
    path('', views.starting_page, name='starting_page'),
    path('transactions/', views.all_transactions, name='transactions'),
    # slug is a unique identifier (slug is checking the format)
    path('transactions/<slug:slug>', views.transaction_detail, name='transaction'),

]