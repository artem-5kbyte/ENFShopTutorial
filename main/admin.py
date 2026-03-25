from django.contrib import admin
from .models import Category, Size, Product, ProductSize, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Кількість початкових полів інлайнів

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
# /\ Ці дві моделі рахуються як окремі проте нам треба щоб вони були зареєстровані і повязані разом з Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'color', 'price']
    # Список який ми бачитимемо не при заході на товар, а на сторінці загалом
    list_filter = ['category', 'color',]
    # Параметри за яким зможемо фільтрувати

    search_fields = ['name', 'color', 'description']

    prepopulated_fields = {'slug': ('name',)}
    # Конструкція яка дозволяє нам заповнювати певні параметри з тих параметрів які в нас вже є

    inlines = [ProductSizeInline, ProductImageInline] # Тепер ті двоє будуть в нас на сторінці додавання продукту


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size, SizeAdmin)