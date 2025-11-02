from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/transactions/', views.get_transactions, name='get_transactions'),
    path('api/transactions/ajouter/', views.ajouter_transaction, name='ajouter_transaction'),
    path('api/transactions/export-pdf/', views.export_transactions_pdf, name='export_pdf')
]