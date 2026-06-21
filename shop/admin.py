from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Banner, Cart, CartItem, Category, City, Order, OrderItem, Product, ProductVariant, UserProfile

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'quantity', 'price')

@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'category', 'price', 'is_new_collection', 'stock_total')
    list_filter = ('category', 'is_new_collection')
    search_fields = ('name',)
    inlines = [ProductVariantInline]
    actions = ['duplicate_product']  
    def stock_total(self, obj):
        return sum(v.stock for v in obj.variants.all())
    stock_total.short_description = "Жалпы қалдық" 

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock')
    list_filter = ('product__category', 'size', 'color')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'variant', 'quantity')

@admin.register(City)
class CityAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'city', 'total_price', 'status', 'is_viewed', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'total_price', 'discount_applied', 'bonus_points_used', 'bonus_points_earned')
    actions = ['mark_as_completed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        for obj in queryset:
            obj.status = 'completed'
            obj.save()
        self.message_user(request, f"{queryset.count()} тапсырыс орындалды деп белгіленді.")
    mark_as_completed.short_description = "Орындалды деп белгілеу"  

    def mark_as_cancelled(self, request, queryset):
        for obj in queryset:
            obj.status = 'cancelled'
            obj.save()
        self.message_user(request, f"{queryset.count()} тапсырыс бас тартылды деп белгіленді.")
    mark_as_cancelled.short_description = "Бас тартылды деп белгілеу"  
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'variant', 'quantity', 'price')

@admin.register(Banner)
class BannerAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'banner_title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    fields = ('title', 'banner_title', 'banner_subtitle', 'image', 'link', 'category', 'order', 'is_active')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_spent', 'bonus_points')
    readonly_fields = ('total_spent', 'bonus_points')