from django.urls import path
from .views import index, detail, payment_success_view, payment_failed_view, create_checkout_session, create_product, product_edit, product_delete, dashboard, register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:id>/', detail, name='detail'),
    path('success/', payment_success_view, name='success'),
    path('failed/', payment_failed_view, name='failed'),
    path('api/checkout-session/<int:id>/', create_checkout_session, name='api_checkout_session'),
    path('create-product/', create_product, name='create_product'),
    path('edit-product/<int:id>/', product_edit, name='product_edit'),
    path('delete-product/<int:id>/', product_delete, name='product_delete'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='core/logout.html'), name='logout'),
]