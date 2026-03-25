from django.shortcuts import get_object_or_404
from django.template.context_processors import request
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from unicodedata import category

from .models import Category, Product, Size
from django.db.models import Q


# Ми використовуємо класові представлення при роботі з великим масивом даних
# render для функціонального представлення
# get object or 404 для класового представлення

# Головна сторінка сайту. Ренедерить базовий шаблон
class IndexView(TemplateView):
    template_name = "main/base.html" # Шлях до базового файлу

    # Отримати контекст. дані які шаблон може використовувати
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Викликаємо батьківську функцію яка бере контекст. Він повертає kwargs з URL(slug, id, тощо)
        context['categories'] = Category.objects.all() # Створюємо своє поле категорії і записуємо записи з БД
        context['current_category'] = None # В поточну категорію по дефолту ставимо ноне
        return context # Повертаємо оновленний контекст

    # Отримання шаблонів
    # Коли ми зайшли на індекс.
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs) # Ініціалізуємо контекст
        if request.headers.get('HX-Request'): # Якщо get = HX-request . Тобто якщо був саме HTMX запит на отримання даної сторінки тоді. сторінка запитана через HTMX, а не через повне оновлення браузера.
            return TemplateResponse(request, 'main/home_content.html', context) # Повертаємо тільки частину сторінки. Не base а лиш додатковий фрагмент. заміна частини сторінки без перезавантаження.
        # Тоді в base html людини в блок content замість старого вмісту прийде новий блок з іншим контекстом
        return TemplateResponse(request, self.template_name, context) # Якщо людина зайшла на сайт звичайно через браузер, то просто повернемо стандартну сторінку


class CatalogView(TemplateView):
    template_name = "main/base.html"  # Шлях до базового файлу

    # Словник параметрів. Прапорців. За якими можна сортувати
    FILTER_MAPPING = {
        #Якщо людина щось вибирає воно перехоплюється і виконується фільтрація
        'color': lambda queryset, value: queryset.filter(color__iexact=value), # queryset масив з товарами value значення яке задав користувач
        'min_price': lambda queryset, value: queryset.filter(price_gte=value),
        'max_price': lambda queryset, value: queryset.filter(price_lte=value),
        'size': lambda queryset, value: queryset.filter(product_sizes__size_name=value),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug') # Беремо слаг з url
        categories = Category.objects.all()
        products = Product.objects.all().order_by('-created_at')
        current_category = None

        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug) # Пробуємо дістати категорію по тому слагу яку вказав користувач з БД (де в урл був відповідний слаг)
            products = products.filter(category=current_category) # Фільтруємо наші товари по категорії які вибрав користувач

        # Пошук
        query = self.request.GET.get('q') # q параметр з url
        if query: # якщо є запит на пошук
            products = products.filter( # Фільтруємо товари за q пошуком
                Q(name__icontains=query) | Q(description__icontains=query) # Шукаємо або за назвою або за описом
            ) # icontains - регістр не важливий


        filter_params = {} # Це словник, де будуть усі активні фільтри.

        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param) # беремо параметр з url при фільтрації. Воно перехопилось
            if value: # Якщо щось перехопилось з урл (В 40 рядку перелік всіх варіантів які воно може взяти)
                products = filter_func(products, value) # викликає lambda функцію з FILTER_MAPPING.
                filter_params[param] = value # Зберігаємо активний фільтр
            else:
                filter_params[param] = '' # Якщо параметра нема Значить фільтр не використовується.

        filter_params['q'] = query or '' # Збереження пошуку Якщо: query = nike то filter_params['q'] = nike Якщо пошуку нема: '' Це потрібно щоб поле пошуку не очищалось після фільтрації.

        context.update( # Додавання багато даних в context. теж саме що context['categories'] = categories
            {
                'categories': categories,
                'products': products,
                'current_category': category_slug,
                'filter_params': filter_params,
                'sizes': Size.objects.all(),
                'search_query': query or '',

            }
        )

        if self.request.GET.get('show_search') == 'true': # Якщо в посиланні є ?show_search=true
            context['show_search'] = True  # Тоді додаємо в контекст значення істинна
        elif self.request.GET.get('reset_search') == 'true':
            context['reset_search'] = True
        # Потім у get()по них вирішуємл який шаблон повернути
        return context


    def get(self, request, *args, **kwargs): # Метод який обробляє запити відкриття сторінки
        context = self.get_context_data(**kwargs) # Записуємо в контекст дані з сторінки і загального контексту
        if request.headers.get('HX-Request'): # Якщо в заголовках htmx запит
            if context.get('show_search'): # якщо в контексті є дані чи є параметр в посиланні повертаємо відповідні шаблони
                return TemplateResponse(request, 'main/search_input', context) #
            elif context.get('reset_search'): #
                return TemplateResponse(request, 'main/search_button.html', {}) #
            template = 'main/filter_modal.html' if request.GET.get('show_filters') == 'true' else 'main/catalog.html' #
            return TemplateResponse(request, template, context) #
        return TemplateResponse(request, self.template_name, context) #
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/base.html'
    slug_field = 'slug' # Поле моделі, по якому буде шукатись об'єкт (у Product це поле slug)
    slug_url_kwarg = 'slug' # Назва параметра в URL, з якого береться slug

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Отримуємо базовий context від DetailView
        product = self.get_object() #  # Отримуємо конкретний товар на основі slug з URL. З реквесту дістаємо товар на детальну сторінку якого нам треба перейти
        context['categories'] =  Category.objects.all() # в контекст категорії записуємо всі категорії з БД
        context['related_products'] = Product.objects.filter( # Для пов'язаних товарів витягуємо дані з БД
            category=product.category # Ті, що мають ту ж категорію, що і поточний товар
        ).exclude(id=product.id)[:4] # Вибираємо все окрім рднакових ід. І беремо тільки 5 записів. Це треба для "Рековмендоване"
        context['current_category'] = product.category.slug # Передаємо slug поточної категорії (для підсвітки/логіки в шаблоні)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object() # Беремо наш обєкт. Товар який будемо показувати.
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/product_detail.html', context) # Повертаємо шаблон з окремим товаром
        raise TemplateResponse(request, self.template_name, context) # Якщо не HX-Request
    

