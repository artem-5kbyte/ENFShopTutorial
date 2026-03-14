from tkinter.constants import CASCADE
from tkinter.font import names

from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug: # Якщо вручну не було задано слаг
            self.slug = slugify(self.name) # Викликаємо slugify яка автоматично перетворює назву в слаг
        super().save(*args, **kwargs) # І збергіаємо все разом викликаючи батьківську функцію


    def __str__(self):
        return self.name # То як відображатиметься на сторінці


class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products') # related_name задає назву для доступу у зворотну сторону.
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True) # blank=True - воно може бути пустим при заповненні адмінки джанго
    color = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to='products/main/') # Фото зберігатимкться в зазначенній MEDIA URL + шлях з upload to
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug: # Якщо вручну не було задано слаг
            self.slug = slugify(self.name) # Викликаємо slugify яка автоматично перетворює назву в слаг
        super().save(*args, **kwargs) # І зберігаємо все разом викликаючи батьківську функцію

    def __str__(self):
        return self.name


class ProductSize(models.Model): # Кількість наявних розмірів одягу
    product = models.ForeignKey(Product, on_delete=models.CASCADE , related_name='product_sizes') # related_name задає назву для доступу у зворотну сторону.
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.size.name} ({self.stock}) - {self.product.name}"

# Приклад роботи related names
#
# Звернення від ProductSize → Product
# product_size = ProductSize.objects.first()
# product_size.product
#
# Зворотне звернення (related_name) Product -> ProductSize
# product = Product.objects.get(id=1)
# product.product_size.all()

class ProductImage(models.Model): # З'єднання товару з його зображеняМИ
    # В каталозі 1 зображення головне. Тут ж зображення які вже показують товар з інших ракурсів (Таке собі Детальніше)
    product = models.ForeignKey(Product, on_delete=models.CASCADE , related_name='images')
    image = models.ImageField(upload_to='product/extra/')
