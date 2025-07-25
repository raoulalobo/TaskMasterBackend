from django.urls import path
from . import views

# URLs pour l'application properties
urlpatterns = [
    # Gestion des propriétés
    path('properties/', views.PropertyListCreateView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),
    
    # Gestion des images de propriétés
    path('property-images/', views.PropertyImageView.as_view(), name='property-image-create'),
    path('property-images/<int:pk>/', views.PropertyImageDeleteView.as_view(), name='property-image-delete'),
    
    # Endpoints pour les signalements de propriétés
    path('property-reports/', views.PropertyReportListCreateView.as_view(), name='property-report-list-create'),
    path('property-reports/<int:pk>/', views.PropertyReportDetailView.as_view(), name='property-report-detail'),
    
    # Endpoints pour les demandes de visite
    path('visit-requests/', views.VisitRequestListCreateView.as_view(), name='visit-request-list-create'),
    path('visit-requests/<int:pk>/', views.VisitRequestDetailView.as_view(), name='visit-request-detail'),
]