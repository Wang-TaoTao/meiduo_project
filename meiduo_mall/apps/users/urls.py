
# users 子应用路由


from django.conf.urls import url
from . import views
urlpatterns = [

    # 注册的视图
    url(r'^register/$',views.RegisterView.as_view(),name='register')
]
