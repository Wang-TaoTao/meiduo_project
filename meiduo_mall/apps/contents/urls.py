
# contents 子应用路由


from django.conf.urls import url
from . import views
urlpatterns = [

  # 首页子路由
  url('^$',views.IndexView.as_view(),name='index'),
]
