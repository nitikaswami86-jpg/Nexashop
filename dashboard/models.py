from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='📦')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=10, default='📦')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock < 10

    @property
    def total_sold(self):
        from django.db.models import Sum
        result = self.orders.filter(status='completed').aggregate(total=Sum('quantity'))
        return result['total'] or 0

    @property
    def total_revenue(self):
        from django.db.models import Sum
        result = self.orders.filter(status='completed').aggregate(total=Sum('amount'))
        return result['total'] or 0


class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    avatar_color = models.CharField(max_length=7, default='#7c4dff')
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.name} <{self.email}>"

    @property
    def initials(self):
        parts = self.name.split()
        return (parts[0][0] + (parts[1][0] if len(parts) > 1 else '')).upper()

    @property
    def total_spent(self):
        from django.db.models import Sum
        result = self.orders.filter(status='completed').aggregate(total=Sum('amount'))
        return result['total'] or 0

    @property
    def total_orders(self):
        return self.orders.count()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    STATUS_COLORS = {
        'pending': 'warning',
        'processing': 'info',
        'shipped': 'primary',
        'completed': 'success',
        'cancelled': 'danger',
    }

    order_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_id} — {self.customer.name}"

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    def save(self, *args, **kwargs):
        if not self.order_id:
            import random
            self.order_id = f'NX-{random.randint(10000, 99999)}'
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    TYPE_CHOICES = [
        ('order_new', 'New Order'),
        ('order_status', 'Order Status Changed'),
        ('product_low', 'Low Stock Alert'),
        ('customer_new', 'New Customer'),
        ('review', 'New Review'),
        ('payment', 'Payment Received'),
    ]
    COLOR_MAP = {
        'order_new': 'blue',
        'order_status': 'green',
        'product_low': 'yellow',
        'customer_new': 'purple',
        'review': 'purple',
        'payment': 'green',
    }

    activity_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type}: {self.message[:50]}"

    @property
    def color(self):
        return self.COLOR_MAP.get(self.activity_type, 'blue')
