from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import json

from .models import Order, Product, Customer, Category, ActivityLog
from .forms import OrderForm, OrderStatusForm, ProductForm, CustomerForm


# ─── DASHBOARD ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = timezone.now()
    start = today - timedelta(days=30)
    prev_start = today - timedelta(days=60)

    # KPIs
    rev_now  = Order.objects.filter(created_at__gte=start, status='completed').aggregate(t=Sum('amount'))['t'] or 0
    rev_prev = Order.objects.filter(created_at__range=(prev_start, start), status='completed').aggregate(t=Sum('amount'))['t'] or 1
    ord_now  = Order.objects.filter(created_at__gte=start).count()
    ord_prev = Order.objects.filter(created_at__range=(prev_start, start)).count() or 1
    cust_now = Customer.objects.count()
    new_cust = Customer.objects.filter(joined_at__gte=start).count()
    completed = Order.objects.filter(status='completed').count()
    total_orders = Order.objects.count() or 1
    conv_rate = round((completed / total_orders) * 100, 1)

    # Monthly revenue chart (last 12 months)
    months, rev_data, ord_data = [], [], []
    for i in range(11, -1, -1):
        d = today - timedelta(days=30 * i)
        label = d.strftime('%b')
        m_rev = Order.objects.filter(
            created_at__year=d.year, created_at__month=d.month, status='completed'
        ).aggregate(t=Sum('amount'))['t'] or 0
        m_ord = Order.objects.filter(
            created_at__year=d.year, created_at__month=d.month
        ).count()
        months.append(label)
        rev_data.append(float(m_rev))
        ord_data.append(m_ord)

    # Category pie
    cat_labels, cat_vals = [], []
    for cat in Category.objects.annotate(cnt=Count('products__orders')).order_by('-cnt')[:5]:
        cat_labels.append(cat.name)
        cat_vals.append(cat.cnt)

    # Top products
    top_products = Product.objects.annotate(
        sold=Sum('orders__quantity'), revenue=Sum('orders__amount')
    ).filter(sold__isnull=False).order_by('-sold')[:5]
    max_sold = top_products[0].sold if top_products else 1

    # Weekly orders sparkline
    week_labels = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
    week_data = [Order.objects.filter(created_at__date=(today - timedelta(days=i)).date()).count() for i in range(6, -1, -1)]

    # Recent orders & activity
    recent_orders = Order.objects.select_related('customer', 'product').order_by('-created_at')[:8]
    activity = ActivityLog.objects.order_by('-created_at')[:10]

    ctx = {
        'page': 'dashboard',
        'rev_now': rev_now, 'rev_change': round(((rev_now - rev_prev) / rev_prev) * 100, 1),
        'ord_now': ord_now, 'ord_change': round(((ord_now - ord_prev) / ord_prev) * 100, 1),
        'cust_now': cust_now, 'new_cust': new_cust,
        'conv_rate': conv_rate,
        'avg_order': Order.objects.filter(status='completed').aggregate(a=Avg('amount'))['a'] or 0,
        'pending_count': Order.objects.filter(status='pending').count(),
        'low_stock_count': Product.objects.filter(stock__lt=10).count(),
        'months_json': json.dumps(months),
        'rev_data_json': json.dumps(rev_data),
        'ord_data_json': json.dumps(ord_data),
        'cat_labels_json': json.dumps(cat_labels),
        'cat_vals_json': json.dumps(cat_vals),
        'week_labels_json': json.dumps(week_labels),
        'week_data_json': json.dumps(week_data),
        'top_products': top_products,
        'max_sold': max_sold,
        'recent_orders': recent_orders,
        'activity': activity,
    }
    return render(request, 'dashboard/index.html', ctx)


# ─── ORDERS ────────────────────────────────────────────────────────────────────

@login_required
def order_list(request):
    qs = Order.objects.select_related('customer', 'product').order_by('-created_at')
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(order_id__icontains=q) | Q(customer__name__icontains=q) | Q(product__name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'orders/list.html', {
        'page': 'orders', 'page_obj': page_obj,
        'q': q, 'status': status,
        'status_choices': Order.STATUS_CHOICES,
        'counts': {s: Order.objects.filter(status=s).count() for s, _ in Order.STATUS_CHOICES},
        'total': Order.objects.count(),
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('customer', 'product'), pk=pk)
    form = OrderStatusForm(instance=order)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            updated = form.save()
            if old_status != updated.status:
                ActivityLog.objects.create(
                    activity_type='order_status',
                    message=f'Order {order.order_id} status changed from {old_status} to {updated.status}'
                )
            messages.success(request, f'Order {order.order_id} updated successfully!')
            return redirect('order_detail', pk=pk)
    return render(request, 'orders/detail.html', {'page': 'orders', 'order': order, 'form': form})


@login_required
def order_create(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            ActivityLog.objects.create(
                activity_type='order_new',
                message=f'New order {order.order_id} placed by {order.customer.name} for {order.product.name}'
            )
            messages.success(request, f'Order {order.order_id} created!')
            return redirect('order_list')
    return render(request, 'orders/form.html', {'page': 'orders', 'form': form, 'action': 'Create'})


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated!')
            return redirect('order_detail', pk=pk)
    return render(request, 'orders/form.html', {'page': 'orders', 'form': form, 'action': 'Edit', 'order': order})


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        oid = order.order_id
        order.delete()
        messages.warning(request, f'Order {oid} deleted.')
        return redirect('order_list')
    return render(request, 'orders/confirm_delete.html', {'page': 'orders', 'order': order})


# ─── PRODUCTS ──────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
    qs = Product.objects.select_related('category').order_by('-created_at')
    q = request.GET.get('q', '')
    cat = request.GET.get('cat', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    if cat:
        qs = qs.filter(category__slug=cat)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'products/list.html', {
        'page': 'products', 'page_obj': page_obj,
        'q': q, 'cat': cat,
        'categories': Category.objects.all(),
        'total': Product.objects.count(),
        'low_stock': Product.objects.filter(stock__lt=10).count(),
        'inactive': Product.objects.filter(is_active=False).count(),
    })


@login_required
def product_create(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            p = form.save()
            if p.stock < 10:
                ActivityLog.objects.create(activity_type='product_low', message=f'Low stock: {p.name} ({p.stock} left)')
            messages.success(request, f'Product "{p.name}" created!')
            return redirect('product_list')
    return render(request, 'products/form.html', {'page': 'products', 'form': form, 'action': 'Add'})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated!')
            return redirect('product_list')
    return render(request, 'products/form.html', {'page': 'products', 'form': form, 'action': 'Edit', 'product': product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.warning(request, f'Product "{name}" deleted.')
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'page': 'products', 'product': product})


# ─── CUSTOMERS ─────────────────────────────────────────────────────────────────

@login_required
def customer_list(request):
    qs = Customer.objects.order_by('-joined_at')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(city__icontains=q))
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'customers/list.html', {
        'page': 'customers', 'page_obj': page_obj, 'q': q,
        'total': Customer.objects.count(),
    })


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.select_related('product').order_by('-created_at')
    return render(request, 'customers/detail.html', {
        'page': 'customers', 'customer': customer,
        'orders': orders,
        'total_spent': customer.total_spent,
        'total_orders': customer.total_orders,
    })


@login_required
def customer_create(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c = form.save()
            ActivityLog.objects.create(activity_type='customer_new', message=f'New customer: {c.name} ({c.email})')
            messages.success(request, f'Customer "{c.name}" added!')
            return redirect('customer_list')
    return render(request, 'customers/form.html', {'page': 'customers', 'form': form, 'action': 'Add'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated!')
            return redirect('customer_detail', pk=pk)
    return render(request, 'customers/form.html', {'page': 'customers', 'form': form, 'action': 'Edit', 'customer': customer})
