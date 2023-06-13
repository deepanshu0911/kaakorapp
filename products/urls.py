from django.urls import path
from products import views

urlpatterns = [
    path('products', views.ProductAPI.as_view()),
    path('admin/products', views.AuthProductsAPI.as_view()),
    path('products/images', views.ProductImageAPI.as_view()),
    path('products/status', views.SetProductStatusAPI.as_view()),
    path('products/search', views.SearchProductsAPI.as_view()),

    path('orders', views.OrderAPI.as_view()),
    path('orders/add', views.OrderAPI.as_view()),
    path('orders/file', views.OrderPrintableAPI.as_view()),
    path('orders/update', views.AuthOrdersAPI.as_view()),
    path('orders/track', views.TrackOrderAPI.as_view()),
    path('orders/invoice', views.UpdateInvoiceAPI.as_view()),

    path('user/orders', views.UserOrderAPI.as_view()),
]
