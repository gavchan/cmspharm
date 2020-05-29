from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('category/new/', views.NewCategory.as_view(), name='NewCategory'),
    path('category/<int:pk>/update', views.CategoryUpdate.as_view(), name='CategoryUpdate'),
    path('category/<int:pk>/delete', views.CategoryDelete.as_view(), name='CategoryDelete'),
    path('category/', views.CategoryList.as_view(), name='CategoryList'),
    path('delivery/new/<int:item_id>', views.NewItemDelivery.as_view(), name='NewItemDelivery'),
    path('delivery/<int:pk>/update/', views.ItemDeliveryUpdate.as_view(), name='ItemDeliveryUpdate'),
    path('delivery/<int:pk>/delete/', views.ItemDeliveryDelete.as_view(), name='ItemDeliveryDelete'),
    path('delivery/<int:pk>', views.ItemDeliveryDetail.as_view(), name='ItemDeliveryDetail'),
    path('delivery/', views.ItemDeliveryList.as_view(), name='ItemDeliveryList'),
    path('item/new/<int:vendor_id>', views.NewItem.as_view(), name='NewItem'),
    path('item/new/', views.NewItem.as_view(), name='NewItem'),
    path('item/<int:pk>/update/', views.ItemUpdate.as_view(), name='ItemUpdate'),
    path('item/<int:pk>/delete/', views.ItemDelete.as_view(), name='ItemDelete'),
    path('item/<int:pk>', views.ItemDetail.as_view(), name='ItemDetail'),
    path('item', views.ItemList.as_view(), name='ItemList'), 
    path('vendor/new/', views.NewVendor.as_view(), name='NewVendor'),
    path('vendor/new/modal/', views.NewVendorModal.as_view(), name='NewVendorModal'),
    path('vendor/<int:pk>/update/', views.VendorUpdate.as_view(), name='VendorUpdate'),
    path('vendor/<int:pk>/delete/', views.VendorDelete.as_view(), name='VendorDelete'),
    path('vendor/<int:pk>', views.VendorDetail.as_view(), name='VendorDetail'),
    path('vendor/', views.VendorList.as_view(), name='VendorList'),
]
