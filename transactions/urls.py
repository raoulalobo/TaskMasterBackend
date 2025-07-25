from django.urls import path
from . import views

# URLs pour l'application transactions
urlpatterns = [
    path('transactions/', views.TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
]