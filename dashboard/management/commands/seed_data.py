import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from dashboard.models import Category, Product, Customer, Order, ActivityLog


CATEGORIES = [
    ('Electronics', 'electronics', '📱'),
    ('Fashion', 'fashion', '👗'),
    ('Home & Garden', 'home-garden', '🏡'),
    ('Sports', 'sports', '⚽'),
    ('Books', 'books', '📚'),
]

PRODUCTS = [
    ('Sony WH-1000XM5 Headphones', 'electronics', '🎧', 28990, 45),
    ('Samsung 65" QLED 4K TV', 'electronics', '📺', 78000, 12),
    ('OnePlus 13R Smartphone', 'electronics', '📱', 42999, 30),
    ('Apple MacBook Air M3', 'electronics', '💻', 114900, 8),
    ('Canon EOS R50 Camera', 'electronics', '📷', 69999, 15),
    ('Nike Air Max 270', 'fashion', '👟', 9499, 60),
    ("Levi's 511 Slim Fit Jeans", 'fashion', '👖', 3199, 80),
    ('Tommy Hilfiger Polo', 'fashion', '👕', 2499, 55),
    ('Ray-Ban Aviators', 'fashion', '🕶️', 7500, 25),
    ('Puma Running Shoes', 'fashion', '👞', 5999, 40),
    ('Philips Air Fryer', 'home-garden', '🍳', 8999, 35),
    ('Prestige Induction Cooktop', 'home-garden', '🔥', 3499, 50),
    ('Garden Tool Set Pro', 'home-garden', '🌿', 1899, 20),
    ('Luxury Dinner Set (12 pcs)', 'home-garden', '🍽️', 4599, 18),
    ('Memory Foam Pillow', 'home-garden', '🛏️', 1299, 70),
    ('Yoga Mat Premium', 'sports', '🧘', 2199, 65),
    ('Fitbit Charge 6', 'sports', '⌚', 14999, 22),
    ('Decathlon Cricket Set', 'sports', '🏏', 3799, 30),
    ('Protein Powder 2kg', 'sports', '💪', 2899, 100),
    ('Badminton Racket Set', 'sports', '🏸', 1599, 45),
    ('Atomic Habits - James Clear', 'books', '📖', 499, 200),
    ('Python Programming Guide', 'books', '🐍', 799, 150),
    ('Rich Dad Poor Dad', 'books', '💰', 399, 180),
    ('Design of Everyday Things', 'books', '🎨', 699, 90),
    ('Deep Work - Cal Newport', 'books', '🧠', 599, 120),
]

CUSTOMERS = [
    ('Priya Sharma', 'priya.sharma@gmail.com', '9876543210', 'Mumbai', 'Maharashtra', '#00e5ff'),
    ('Rahul Verma', 'rahul.verma@gmail.com', '9876543211', 'Delhi', 'Delhi', '#7c4dff'),
    ('Sunita Patel', 'sunita.patel@gmail.com', '9876543212', 'Ahmedabad', 'Gujarat', '#ff4081'),
    ('Amit Singh', 'amit.singh@gmail.com', '9876543213', 'Lucknow', 'Uttar Pradesh', '#00e676'),
    ('Meera Joshi', 'meera.joshi@gmail.com', '9876543214', 'Pune', 'Maharashtra', '#ffab40'),
    ('Vikram Rao', 'vikram.rao@gmail.com', '9876543215', 'Bangalore', 'Karnataka', '#00e5ff'),
    ('Kavya Menon', 'kavya.menon@gmail.com', '9876543216', 'Chennai', 'Tamil Nadu', '#7c4dff'),
    ('Deepak Kumar', 'deepak.kumar@gmail.com', '9876543217', 'Kolkata', 'West Bengal', '#ff4081'),
    ('Anjali Gupta', 'anjali.gupta@gmail.com', '9876543218', 'Jaipur', 'Rajasthan', '#00e676'),
    ('Rohit Mishra', 'rohit.mishra@gmail.com', '9876543219', 'Hyderabad', 'Telangana', '#ffab40'),
    ('Sneha Nair', 'sneha.nair@gmail.com', '9876543220', 'Kochi', 'Kerala', '#00e5ff'),
    ('Arjun Tiwari', 'arjun.tiwari@gmail.com', '9876543221', 'Bhopal', 'Madhya Pradesh', '#7c4dff'),
    ('Pooja Yadav', 'pooja.yadav@gmail.com', '9876543222', 'Patna', 'Bihar', '#ff4081'),
    ('Suresh Reddy', 'suresh.reddy@gmail.com', '9876543223', 'Vijayawada', 'Andhra Pradesh', '#00e676'),
    ('Nisha Chauhan', 'nisha.chauhan@gmail.com', '9876543224', 'Chandigarh', 'Punjab', '#ffab40'),
    ('Karan Malhotra', 'karan.malhotra@gmail.com', '9876543225', 'Amritsar', 'Punjab', '#00e5ff'),
    ('Divya Pandey', 'divya.pandey@gmail.com', '9876543226', 'Varanasi', 'Uttar Pradesh', '#7c4dff'),
    ('Mohit Saxena', 'mohit.saxena@gmail.com', '9876543227', 'Agra', 'Uttar Pradesh', '#ff4081'),
    ('Lakshmi Iyer', 'lakshmi.iyer@gmail.com', '9876543228', 'Coimbatore', 'Tamil Nadu', '#00e676'),
    ('Gaurav Bhatt', 'gaurav.bhatt@gmail.com', '9876543229', 'Dehradun', 'Uttarakhand', '#ffab40'),
]


class Command(BaseCommand):
    help = 'Seeds the database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding database...')

        # Admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nexashop.com', 'admin123')
            self.stdout.write('  ✅ Admin user: admin / admin123')

        # Categories
        cat_map = {}
        for name, slug, icon in CATEGORIES:
            c, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})
            cat_map[slug] = c
        self.stdout.write(f'  ✅ {len(cat_map)} categories')

        # Products
        prod_map = {}
        for name, cat_slug, icon, price, stock in PRODUCTS:
            p, _ = Product.objects.get_or_create(
                name=name,
                defaults={'category': cat_map[cat_slug], 'icon': icon, 'price': price, 'stock': stock,
                          'description': f'High quality {name} available at the best price.'}
            )
            prod_map[name] = p
        self.stdout.write(f'  ✅ {len(prod_map)} products')

        # Customers
        cust_list = []
        for i, (name, email, phone, city, state, color) in enumerate(CUSTOMERS):
            days_ago = random.randint(0, 365)
            c, _ = Customer.objects.get_or_create(
                email=email,
                defaults={'name': name, 'phone': phone, 'city': city, 'state': state,
                          'avatar_color': color,
                          'joined_at': timezone.now() - timedelta(days=days_ago)}
            )
            cust_list.append(c)
        self.stdout.write(f'  ✅ {len(cust_list)} customers')

        # Orders
        statuses = ['pending', 'processing', 'shipped', 'completed', 'completed', 'completed', 'cancelled']
        order_count = 0
        products = list(prod_map.values())
        for i in range(80):
            customer = random.choice(cust_list)
            product = random.choice(products)
            qty = random.randint(1, 3)
            status = random.choice(statuses)
            days_ago = random.randint(0, 90)
            import string
            oid = 'NX-' + ''.join(random.choices(string.digits, k=5))
            if not Order.objects.filter(order_id=oid).exists():
                Order.objects.create(
                    order_id=oid,
                    customer=customer,
                    product=product,
                    quantity=qty,
                    amount=product.price * qty,
                    status=status,
                    created_at=timezone.now() - timedelta(days=days_ago),
                )
                order_count += 1
        self.stdout.write(f'  ✅ {order_count} orders')

        # Activity logs
        ActivityLog.objects.all().delete()
        logs = [
            ('order_new', 'New order NX-00824 placed by Priya Sharma for Sony WH-1000XM5'),
            ('order_status', 'Order NX-00821 marked as Delivered'),
            ('review', 'Vikram Rao left a 5-star review on OnePlus 13R'),
            ('product_low', 'Low stock alert: Apple MacBook Air M3 (8 left)'),
            ('order_new', 'New order NX-00820 placed by Meera Joshi for Luxury Dinner Set'),
            ('customer_new', 'New customer Gaurav Bhatt signed up from Dehradun'),
            ('payment', 'Payment of ₹78,000 received for Samsung 65" QLED 4K TV'),
            ('order_status', 'Order NX-00819 cancelled by customer Vikram Rao'),
            ('order_new', 'New order NX-00818 placed by Kavya Menon for Levi\'s 511'),
            ('product_low', 'Low stock alert: Samsung 65" QLED 4K TV (12 left)'),
        ]
        for i, (atype, msg) in enumerate(logs):
            ActivityLog.objects.create(
                activity_type=atype, message=msg,
                created_at=timezone.now() - timedelta(minutes=i * 25)
            )
        self.stdout.write(f'  ✅ {len(logs)} activity logs')

        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeded! Login: admin / admin123'))
