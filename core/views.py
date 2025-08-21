from django.shortcuts import render
from .models import Product
from django.conf import settings
import stripe, json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

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
    request_data = json.load(request.body)
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