from django.urls import path
from . import views

app_name = 'cmsinv'
urlpatterns = [
    path('item/match/delivery/<int:delivery_id>', views.MatchDeliveryInventoryItemList.as_view(), name='MatchDeliveryInventoryItemList'),
    path('item/match/<str:reg_no>', views.MatchInventoryItemList.as_view(), name='MatchInventoryItemList'),
    path('item/<int:pk>/update/', views.InventoryItemUpdate.as_view(), name='InventoryItemUpdate'),
    # path('item/<int:pk>/delete/', views.InventoryItemDelete.as_view(), name='InventoryItemDelete'),
    path('item/<int:pk>', views.InventoryItemDetail.as_view(), name='InventoryItemDetail'),
    path('item/<int:pk>/modal/', views.InventoryItemModalDetail.as_view(), name='InventoryItemModalDetail'),
    # path('item/new/', views.NewItem.as_view(), name='NewItem'),
    path('items/', views.InventoryItemList.as_view(), name='InventoryItemList'),
    ]
