from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, OrderDetail
from django.conf import settings
import stripe, json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotFound
from .forms import ProductForm, UserRagistrationForm
from django.db.models import Sum, Count, Q
import datetime

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, 'core/index.html', {'products': products})

def detail(request, id):
    product = Product.objects.get(id=id)
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    return render(request, 'core/detail.html', {'product':product, 'stripe_publishable_key' : stripe_publishable_key})

@csrf_exempt
def create_checkout_session(request, id):
    request_data = json.loads(request.body)
    product = Product.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = request_data['email'],
        payment_method_types= ['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100)
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url= request.build_absolute_uri(reverse('success')) +
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url= request.build_absolute_uri(reverse('failed')),
    )

    order = OrderDetail()
    order.customer_email = request_data['email']
    order.product = product
    # order.stripe_payment_intent = checkout_session['payment_intent']
    order.stripe_session_id=checkout_session.id
    order.amount = int(product.price)
    order.save()

    return JsonResponse({'session_id':checkout_session.id})

def payment_success_view(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    order = get_object_or_404(OrderDetail, stripe_session_id=session.id)
    order.has_paid = True
    order.stripe_payment_intent = session.payment_intent
    order.save()

    return render(request, 'core/payment_success.html', {'order': order})

def payment_failed_view(request):
    return render(request, 'core/failed.html')

def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            new_product = product_form.save(commit=False)
            new_product.seller = request.user
            new_product.save()
            return redirect('index')
    product_form = ProductForm() 
    return render(request, 'core/create_product.html', {'product_form': product_form})

def product_edit(request, id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    product_form = ProductForm(request.POST or None, request.FILES or None,instance=product)
    if request.method == 'POST':
        if product_form.is_valid():
            product_form.save()
            return redirect('index')
    return render(request, 'core/product_edit.html', {'product_form': product_form})

def product_delete(request, id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    if request.method == 'POST':
        product.delete()
        return redirect('index')
    return render(request, 'core/product_delete.html', {'product': product})

def dashboard(request):
    products = Product.objects.filter(seller=request.user).annotate(
        total_orders=Count('orderdetail', filter=Q(orderdetail__has_paid=True)),
        total_earnings=Sum('orderdetail__amount', filter=Q(orderdetail__has_paid=True))
    )
    return render(request, 'core/dashboard.html', {'products': products})


def register(request):
    if request.method == 'POST':
        user_form = UserRagistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return redirect('index')
    user_form = UserRagistrationForm()
    return render(request, 'core/register.html', {'user_form': user_form})

def invalid_response(request):
    return render(request, 'core/invalid.html')

def my_purchases(request):
    orders = OrderDetail.objects.all()
    return render(request, 'core/my_purchases.html', {'orders':orders})

def sales(request):
    orders = OrderDetail.objects.filter(product__seller=request.user, has_paid=True)
    total_sales = orders.aggregate(Sum('amount'))

    # weekly sales sum
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    orders = OrderDetail.objects.filter(product__seller=request.user, has_paid=True, created_on__gt=last_week)
    weekly_sales = orders.aggregate(Sum('amount'))

    # monthly sales sum
    today = datetime.date.today() - datetime.timedelta(days=30)
    orders = OrderDetail.objects.filter(product__seller=request.user, has_paid=True, created_on__year=today.year, created_on__month=today.month)
    monthly_sales = orders.aggregate(Sum('amount'))

    # 365 day sales sum
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    orders = OrderDetail.objects.filter(product__seller=request.user, has_paid=True, created_on__gt=last_year)
    yearly_sales = orders.aggregate(Sum('amount'))

    # Everyday sum for the last 30 days
    daily_sales_sum = OrderDetail.objects.filter(product__seller=request.user, has_paid=True).values('created_on__date').order_by('created_on__date').annotate(total=Sum('amount'))
    
    # Product sales sum for the last 30 days
    product_sales_sum = OrderDetail.objects.filter(product__seller=request.user, has_paid=True).values('product__name').order_by('product__name').annotate(total=Sum('amount'))

    return render(request, 'core/sales.html', {'total_sales': total_sales, 'yearly_sales': yearly_sales, 'monthly_sales': monthly_sales, 'weekly_sales': weekly_sales, 'daily_sales_sum':daily_sales_sum, 'product_sales_sum': product_sales_sum})