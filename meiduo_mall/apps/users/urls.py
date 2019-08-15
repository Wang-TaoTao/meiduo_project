
# users 子应用路由


from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [

    # 注册视图
    url(r'^register/$',views.RegisterView.as_view())
]
