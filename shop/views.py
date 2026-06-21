from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Category, Product, ProductVariant, Cart, CartItem, Order, OrderItem, Banner, UserProfile, City, Comment
from .forms import SignUpForm, LoginForm, CheckoutForm, CommentForm
from .json_translations import t
import uuid

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
    return cart

def home(request):
    category_slug = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    selected_size = request.GET.get('size', '').strip()
    selected_color = request.GET.get('color', '').strip()
    in_stock = request.GET.get('in_stock', '')

    products = Product.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            min_price = ''

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            max_price = ''

    if selected_size:
        products = products.filter(variants__size=selected_size)

    if selected_color:
        products = products.filter(variants__color=selected_color)

    if in_stock:
        products = products.filter(variants__stock__gt=0)

    products = products.distinct()

    all_sizes = ProductVariant.objects.values_list('size', flat=True).distinct().order_by('size')
    all_colors = ProductVariant.objects.values_list('color', flat=True).distinct().order_by('color')

    new_collection_products = Product.objects.filter(is_new_collection=True)[:5]
    banners = Banner.objects.filter(is_active=True)

    has_filters = any([q, min_price, max_price, selected_size, selected_color, in_stock])

    context = {
        'products': products,
        'new_collection_products': new_collection_products,
        'selected_category': category_slug,
        'banners': banners,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'selected_size': selected_size,
        'selected_color': selected_color,
        'in_stock': in_stock,
        'all_sizes': all_sizes,
        'all_colors': all_colors,
        'has_filters': has_filters,
    }
    return render(request, 'shop/home.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    variants = product.variants.all()
    comments = product.comments.select_related('user').all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                product=product,
                user=request.user,
                text=form.cleaned_data['text'],
            )
            messages.success(request, t('msg.comment_added'))
            return redirect('product_detail', pk=pk)
    else:
        form = CommentForm()

    context = {
        'product': product,
        'variants': variants,
        'comments': comments,
        'form': form,
    }
    return render(request, 'shop/product_detail.html', context)

def new_collection(request):
    products = Product.objects.filter(is_new_collection=True)
    context = {
        'products': products,
    }
    return render(request, 'shop/new_collection.html', context)

def category_new_collection(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    new_products = Product.objects.filter(category=category, is_new_collection=True)
    regular_products = Product.objects.filter(category=category, is_new_collection=False)
    context = {
        'category': category,
        'new_products': new_products,
        'regular_products': regular_products,
    }
    return render(request, 'shop/category_new_collection.html', context)

def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    if variant.stock <= 0:
        messages.error(request, t('msg.out_of_stock'))
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
    if not created:
        if cart_item.quantity < variant.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, t('msg.qty_increased', name=variant.product.name, size=variant.size, color=variant.color))
        else:
            messages.error(request, t('msg.insufficient_stock'))
    else:
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, t('msg.added_to_cart', name=variant.product.name, size=variant.size, color=variant.color))
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('variant__product')
    total = sum(item.variant.product.price * item.quantity for item in items)

    context = {
        'cart': cart,
        'items': items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)

def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=get_or_create_cart(request))
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart_item.delete()
        elif quantity <= cart_item.variant.stock:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            messages.error(request, t('msg.insufficient_stock'))
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=get_or_create_cart(request))
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, t('msg.cart_empty'))
        return redirect('home')

    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    available_points = profile.bonus_points
    bonus_value_per_point = 10

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            points_to_use = form.cleaned_data.get('use_bonus_points') or 0
            if points_to_use > available_points:
                form.add_error('use_bonus_points', t('msg.insufficient_points', pts=available_points))
            else:
                total = sum(item.variant.product.price * item.quantity for item in cart.items.all())
                bonus_discount = points_to_use * bonus_value_per_point
                total_discount = min(bonus_discount, total)
                total_with_discount = total - total_discount

                with transaction.atomic():
                    for item in cart.items.select_related('variant'):
                        variant = item.variant
                        if variant.stock < item.quantity:
                            messages.error(request, t('msg.insufficient_stock_item', name=variant.product.name, size=variant.size, color=variant.color))
                            return redirect('cart_detail')

                    order = Order.objects.create(
                        user=request.user,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        phone=form.cleaned_data['phone'],
                        city=form.cleaned_data['city'],
                        address=form.cleaned_data['address'],
                        total_price=total_with_discount,
                        discount_applied=0,  
                        bonus_points_used=points_to_use,
                        bonus_points_earned=0,
                    )

                    for item in cart.items.select_related('variant'):
                        variant = item.variant
                        variant.stock -= item.quantity
                        variant.save()
                        OrderItem.objects.create(
                            order=order,
                            variant=variant,
                            quantity=item.quantity,
                            price=variant.product.price,
                        )

                    if points_to_use > 0:
                        profile.bonus_points -= points_to_use
                        profile.save()

                    cart.items.all().delete()
                    messages.success(request, t('msg.order_placed'))
                    return redirect('profile')
    else:
        form = CheckoutForm()

    items = cart.items.select_related('variant__product')
    total = sum(item.variant.product.price * item.quantity for item in items)

    context = {
        'form': form,
        'items': items,
        'total': total,
        'available_points': available_points,
        'bonus_value_per_point': bonus_value_per_point,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    total_spent = profile.total_spent
    discount = profile.discount_percent()

    next_threshold = (total_spent // 100000 + 1) * 100000
    need_to_next = next_threshold - total_spent
    next_discount = discount + 1 if discount < 30 else 30

    context = {
        'orders': orders,
        'total_spent': total_spent,
        'discount': discount,
        'need_to_next': need_to_next,
        'next_discount': next_discount,
        'profile': profile,
    }
    return render(request, 'shop/profile.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            try:
                session_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
                user_cart, _ = Cart.objects.get_or_create(user=user)
                for item in session_cart.items.all():
                    user_item, created = CartItem.objects.get_or_create(cart=user_cart, variant=item.variant)
                    if not created:
                        user_item.quantity += item.quantity
                        user_item.save()
                    else:
                        user_item.quantity = item.quantity
                        user_item.save()
                session_cart.delete()
            except Cart.DoesNotExist:
                pass
            messages.success(request, t('msg.registered'))
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'shop/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            try:
                session_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
                user_cart, _ = Cart.objects.get_or_create(user=user)
                for item in session_cart.items.all():
                    user_item, created = CartItem.objects.get_or_create(cart=user_cart, variant=item.variant)
                    if not created:
                        user_item.quantity += item.quantity
                        user_item.save()
                    else:
                        user_item.quantity = item.quantity
                        user_item.save()
                session_cart.delete()
            except Cart.DoesNotExist:
                pass
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('variant__product')
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'shop/order_detail.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')