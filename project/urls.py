from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^doc/', include('rest_framework_swagger.urls')),
    url(r'^', include('core.urls')),
]
