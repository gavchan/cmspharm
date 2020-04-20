from django.urls import path
from . import views

app_name = 'drugdb'
urlpatterns = [
    path('drugs/', views.RegisteredDrugList.as_view(), name='DrugList'),
    path('drug/<int:pk>', views.RegisteredDrugDetail.as_view(), name='DrugDetail'),
    path('deliveries/', views.DrugDeliveryList.as_view(), name='DrugDeliveryList'),
    path('deliveries/<int:pk>', views.DrugDeliveryDetail.as_view(), name='DrugDeliveryDetail'),
    path('new-delivery/', views.NewDrugDelivery.as_view(), name='NewDrugDelivery'),
]
