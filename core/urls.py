from django.urls import path
from .views import index, detail, payment_success_view

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:id>/', detail, name='detail'),
    path('success/', payment_success_view, name='success'),
]