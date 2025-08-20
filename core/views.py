from django.shortcuts import render
from .models import Product

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, 'core/index.html', {'products': products})

def detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'core/detail.html', {'product':product})