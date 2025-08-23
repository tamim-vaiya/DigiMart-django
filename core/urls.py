from django.urls import path
from .views import index, detail, payment_success_view, payment_failed_view, create_checkout_session

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:id>/', detail, name='detail'),
    path('success/', payment_success_view, name='success'),
    path('failed/', payment_failed_view, name='failed'),
    path('api/checkout-session/<int:id>/', create_checkout_session, name='api_checkout_session'),
]