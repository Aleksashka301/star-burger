from collections import defaultdict
from django import forms
from django.db.models import F, Sum
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from star_burger import settings
from .services import get_common_restaurants, get_restaurants_with_distances


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.prefetch_related('items__products').annotate(
        total_price=Sum(F('items__quantity') * F('items__price'))
    )

    products_in_restaurants = RestaurantMenuItem.objects.filter(availability=True).values(
        'product_id',
        'restaurant__name',
        'restaurant__address'
    )
    product_to_restaurants = defaultdict(set)

    for item in products_in_restaurants:
        product_to_restaurants[item['product_id']].add(
            (item['restaurant__name'], item['restaurant__address'])
        )

    address_cache = {}
    order_details = []
    yandex_key = settings.YANDEX_API

    for order in orders:
        if order.status == 'completed':
            continue

        if order.restaurant and order.status not in ['work', 'delivery']:
            order.status_update()
            order.save()

        common_restaurants = get_common_restaurants(order, product_to_restaurants)

        restaurants_with_distances = get_restaurants_with_distances(
            common_restaurants, order.address, yandex_key, address_cache
        )

        order_details.append({
            'id': order.id,
            'buyer': f'{order.firstname} {order.lastname}' if order.lastname else order.firstname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'total_price': order.total_price if order.total_price else 0,
            'comment': order.comment,
            'status': order.get_status_display(),
            'payment_method': order.get_payment_method_display(),
            'available_restaurants': restaurants_with_distances,
            'restaurant': str(order.restaurant).replace('Star Burger', 'BRB') if order.restaurant else '',
        })

    return render(request, template_name='order_items.html', context={'order_items': order_details})

