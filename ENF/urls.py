
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Необхідно для аналогової роботи з продакшином медіа і статики на дебазі
# Дозволяє бачити наші фото на сайті і працювати з ними
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)