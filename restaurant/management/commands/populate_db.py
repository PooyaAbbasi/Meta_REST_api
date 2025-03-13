from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User, Group
from restaurant.models import Category, MenuItem, Cart, Order, OrderItem
import random
from decimal import Decimal


class Command(BaseCommand):
    help = "Populates the database with fake data for testing"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create groups
        manager_group, _ = Group.objects.get_or_create(name='manager')
        delivery_crew_group, _ = Group.objects.get_or_create(name='delivery_crew')
        # customer_group, _ = Group.objects.get_or_create(name='customer')

        # Create users
        for _ in range(5):  # Managers
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123'
            )
            manager_group.user_set.add(user)

        for _ in range(10):  # Delivery crew
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123'
            )
            delivery_crew_group.user_set.add(user)

        for _ in range(20):  # Customers
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123'
            )
            # customer_group.user_set.add(user)

        # Create categories
        categories = []
        for _ in range(5):
            category = Category.objects.create(
                title=fake.unique.word()
            )
            categories.append(category)

        # Create menu items
        menu_items = []
        for _ in range(50):
            menu_item = MenuItem.objects.create(
                title=fake.unique.word(),
                price=Decimal(fake.random_int(min=5, max=50)),
                featured=fake.boolean(),
                category=random.choice(categories)
            )
            menu_items.append(menu_item)

        # Create carts
        customers = User.objects.filter(groups__name='customer')
        for customer in customers:
            for _ in range(random.randint(1, 5)):
                Cart.objects.create(
                    user=customer,
                    menu_item=random.choice(menu_items),
                    quantity=random.randint(1, 5)
                )

        # Create orders
        delivery_crew = User.objects.filter(groups__name='delivery_crew')
        for customer in customers:
            for _ in range(random.randint(1, 3)):
                total_price = Decimal(fake.random_int(min=20, max=200))
                order = Order.objects.create(
                    user=customer,
                    status=fake.boolean(),
                    total_price=total_price,
                    delivery_crew=random.choice(delivery_crew) if fake.boolean() else None
                )

                # Create order items
                for _ in range(random.randint(1, 5)):
                    menu_item = random.choice(menu_items)
                    quantity = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        unit_price=menu_item.price
                    )

        self.stdout.write(self.style.SUCCESS('Database populated with fake data successfully!'))
