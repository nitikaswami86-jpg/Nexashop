from .models import Order, Product

def sidebar_context(request):
    return {
        'pending_orders': Order.objects.filter(status='pending').count(),
        'low_stock_products': Product.objects.filter(stock__lt=10).count(),
    }
