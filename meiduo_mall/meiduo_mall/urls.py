"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 配置users路由
    url(r'^', include('apps.users.urls',namespace='users')),
    # 配置content路由
    url(r'^', include('apps.contents.urls',namespace='contents')),

    # 配置verifications路由
    url(r'^',include('apps.verifications.urls')),

    # 配置oauth路由
    url(r'^',include('apps.oauth.urls')),

    # 配置areas路由
    url(r'^',include('apps.areas.urls')),

    # 配置goods路由
    url(r'^',include('apps.goods.urls',namespace='goods')),

    # 配置carts路由
    url(r'^',include('apps.carts.urls')),

    # 配置orders路由
    url(r'^',include('apps.orders.urls')),

    # 配置payment路由
    url(r'^',include('apps.payment.urls')),

    # 配置haystack 对接搜索引擎的框架总路由
    url(r'^search/', include('haystack.urls')),


    # 配置美多后台管理路由
    url(r'^meiduo_admin/', include('apps.meiduo_admin.urls', namespace='meiduo_admin')),

]
