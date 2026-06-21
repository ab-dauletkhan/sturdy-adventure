from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Атауы")
    slug = models.SlugField(unique=True, verbose_name="Сілтеме")

    class Meta:
        verbose_name = "Санат"
        verbose_name_plural = "Санаттар"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Санаты")
    name = models.CharField(max_length=200, verbose_name="Атауы")
    description = models.TextField(verbose_name="Сипаттамасы")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Бағасы")
    image = models.ImageField(upload_to='products/', verbose_name="Суреті")
    is_new_collection = models.BooleanField(default=False, verbose_name="Жаңа топтама")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Киім"
        verbose_name_plural = "Киімдер"

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="Киім")
    size = models.CharField(max_length=10, verbose_name="Өлшем")
    color = models.CharField(max_length=30, verbose_name="Түс")
    stock = models.PositiveIntegerField(default=0, verbose_name="Қалдық")

    class Meta:
        unique_together = ('product', 'size', 'color')
        verbose_name = "Нұсқа"
        verbose_name_plural = "Нұсқалар"

    def __str__(self):
        return f"{self.product.name} - {self.size} / {self.color}"

class Cart(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Пайдаланушы")
    session_key = models.CharField(max_length=255, null=True, blank=True, verbose_name="Сессия кілті")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Себет"
        verbose_name_plural = "Себеттер"

    def __str__(self):
        return f"Себет {self.user or self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Себет")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, verbose_name="Нұсқа")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Саны")

    class Meta:
        unique_together = ('cart', 'variant')
        verbose_name = "Себет элементі"
        verbose_name_plural = "Себет элементтері"

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="Қала атауы")
    order = models.PositiveIntegerField(default=0, verbose_name="Реті")

    class Meta:
        ordering = ['order']
        verbose_name = "Қала"
        verbose_name_plural = "Қалалар"

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Жаңа'),
        ('processing', 'Өңделуде'),
        ('completed', 'Орындалды'),
        ('cancelled', 'Бас тартылды'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Пайдаланушы")
    first_name = models.CharField(max_length=50, verbose_name="Аты")
    last_name = models.CharField(max_length=50, verbose_name="Тегі")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL, verbose_name="Қала", related_name='orders')
    address = models.TextField(verbose_name="Мекенжай")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Құрылған уақыт")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Жалпы баға")
    discount_applied = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Қолданылған жеңілдік (%)")
    is_viewed = models.BooleanField(default=False, verbose_name="Қаралды ма?")   
    bonus_points_used = models.PositiveIntegerField(default=0, verbose_name="Қолданылған баллдар")
    bonus_points_earned = models.PositiveIntegerField(default=0, verbose_name="Жинақталған баллдар")

    class Meta:
        verbose_name = "Тапсырыс"
        verbose_name_plural = "Тапсырыстар"

    def __str__(self):
        return f"Тапсырыс #{self.id} - {self.first_name} {self.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Тапсырыс")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, verbose_name="Нұсқа")
    quantity = models.PositiveIntegerField(verbose_name="Саны")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сатып алу бағасы")

    class Meta:
        verbose_name = "Тапсырыс элементі"
        verbose_name_plural = "Тапсырыс элементтері"

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name="Атауы (админ үшін)")
    banner_title = models.CharField(max_length=200, blank=True, verbose_name="Баннер тақырыбы")
    banner_subtitle = models.CharField(max_length=300, blank=True, verbose_name="Баннер асты мәтіні")
    image = models.ImageField(upload_to='banners/', verbose_name="Сурет")
    link = models.CharField(max_length=500, blank=True, verbose_name="Сілтеме", help_text="Бос қалдырсаңыз, баннер басылмайды")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Категория", help_text="Егер категория бетіне сілтеме болса, таңдаңыз")
    order = models.PositiveIntegerField(default=0, verbose_name="Реті")
    is_active = models.BooleanField(default=True, verbose_name="Белсенді")

    class Meta:
        ordering = ['order']
        verbose_name = "Баннер"
        verbose_name_plural = "Баннерлер"

    def __str__(self):
        return self.title or f"Баннер №{self.id}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Жинақталған сома")
    bonus_points = models.PositiveIntegerField(default=0, verbose_name="Бонус баллдары")  # Жаңа өріс

    class Meta:
        verbose_name = "Пайдаланушы профилі"
        verbose_name_plural = "Пайдаланушы профильдері"

    def discount_percent(self):
        if self.total_spent < 100000:
            return 0
        base = 3
        steps = (self.total_spent // 100000) - 1
        discount = base + steps
        return min(discount, 30)

    def __str__(self):
        return self.user.username

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Пікір"
        verbose_name_plural = "Пікірлер"

    def __str__(self):
        return f"{self.user.username} — {self.product.name}"