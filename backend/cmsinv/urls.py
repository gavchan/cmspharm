from django.urls import path
from . import views

app_name = 'cmsinv'
urlpatterns = [
    path('delivery/new/fromorder/<int:delivery_id>/modal/', views.NewDeliveryFromDeliveryOrderModalView, name='NewDeliveryFromDeliveryOrderModal'),
    path('suppliers/', views.SupplierList.as_view(), name='SupplierList'),
    path('supplier/<int:pk>/quickedit/modal/', views.SupplierQuickEditModal.as_view(), name='SupplierQuickEditModal'),
    # path('item/match/delivery/<int:delivery_id>/', views.MatchDeliveryInventoryItemList.as_view(), name='MatchDeliveryInventoryItemList'), # Non-CMS Delivery
    path('item/match/<str:reg_no>/', views.MatchInventoryItemList.as_view(), name='MatchInventoryItemList'),
    # path('item/match/<int:pk>/update/', views.InventoryItemMatchUpdate.as_view(), name='InventoryItemMatchUpdate'),
    path('item/<int:pk>/quickedit/modal/', views.InventoryItemQuickEditModal.as_view(), name='InventoryItemQuickEditModal'),
    path('item/<int:pk>/update/', views.InventoryItemUpdate.as_view(), name='InventoryItemUpdate'),
    # path('item/<int:pk>/delete/', views.InventoryItemDelete.as_view(), name='InventoryItemDelete'),
    path('item/<int:pk>/', views.InventoryItemDetail.as_view(), name='InventoryItemDetail'),
    path('item/<int:pk>/modal/', views.InventoryItemModalDetail.as_view(), name='InventoryItemModalDetail'),
    path('item/new/', views.NewInventoryItem.as_view(), name='NewInventoryItem'),
    path('items/', views.InventoryItemList.as_view(), name='InventoryItemList'),
    path('movelog/', views.InventoryMovementLogList.as_view(), name='InventoryMovementLog'),
    ]
