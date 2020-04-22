from django.urls import path
from . import views

app_name = 'drugdb'
urlpatterns = [
    path('', views.RegisteredDrugList.as_view(), name='DrugList'),
    path('drug/<int:pk>', views.RegisteredDrugDetail.as_view(), name='DrugDetail'),
    path('delivery/', views.DrugDeliveryList.as_view(), name='DrugDeliveryList'),
    path('delivery/<int:pk>', views.DrugDeliveryDetail.as_view(), name='DrugDeliveryDetail'),
    path('delivery/new/<str:reg_no>', views.NewDrugDelivery.as_view(), name='NewDrugDelivery'),
    path('delivery/<int:pk>/update/', views.DrugDeliveryUpdate.as_view(), name='DrugDeliveryUpdate'),
    path('delivery/<int:pk>/delete/', views.DrugDeliveryDelete.as_view(), name='DrugDeliveryDelete'),

]
