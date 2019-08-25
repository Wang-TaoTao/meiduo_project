
# areas 子应用路由


from django.conf.urls import url
from . import views

urlpatterns = [

  # 省市区数据 ---三级联动
  url(r'^areas/',views.AreasView.as_view()),

  # 新增收货地址
  url(r'^addresses/create/$',views.CreateAddressView.as_view()),

  # 修改和删除收货地址
  url(r'^addresses/(?P<address_id>\d+)/$',views.UpdateDestroyAddressView.as_view()),

  # 设置默认收货地址
  url(r'^addresses/(?P<address_id>\d+)/default/$',views.DefaultAddressView.as_view()),

  # 修改地址标题
  url(r'^addresses/(?P<address_id>\d+)/title/$',views.UpdateTitleAddressView.as_view()),

  # 修改密码
  url(r'^password/',views.ChangePasswordView.as_view()),


]
