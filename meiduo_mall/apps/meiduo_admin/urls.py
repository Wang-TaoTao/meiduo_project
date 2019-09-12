
# meiduo_admin 子应用路由


from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from .views import statistical
from .views import user
from .views import image
from .views import sku
from .views import spu
from .views import order




urlpatterns = [


  ############################# 数据统计url ########################################

  # 后台管理登录页面入口路由
  url(r'^authorizations/$', obtain_jwt_token),

  # 统计用户总量
  url(r'statistical/total_count/$', statistical.UserTotalCountAPIView.as_view()),

  # 统计日增用户
  url(r'^statistical/day_increment/$', statistical.UserDailyCountAPIView.as_view()),

  # 统计日活跃用户
  url(r'^statistical/day_active/$', statistical.UserDailyActiveCountAPIView.as_view()),

  # 统计日下单用户量
  url(r'^statistical/day_orders/$', statistical.UserDailyOrderCountAPIView.as_view()),

  # 统计月增用户
  url(r'^statistical/month_increment/$', statistical.UserMonthCountAPIView.as_view()),

  # 统计日分类商品访问量
  url(r'^statistical/goods_day_views/$', statistical.UserCategoryCountAPIView.as_view()),

  ############################# 用户管理 ########################################

  # 查询用户信息
  url(r'^users/$', user.UserListView.as_view()),

  ############################# 图片 ########################################

  # 新增图片时获取sku表id
  url(r'skus/simple/$', image.SKUView.as_view()),

  ############################# SKU ########################################

  # 新增SKU数据时候的 三级分类信息
  url(r'^skus/categories/$',sku.SKUCategoriesView.as_view()),

  # 新增SKU数据时候的 获取SPU表名
  url(r'^goods/simple/$', sku.SPUSimpleView.as_view()),

  # 新增SKU数据时候的 获取SPU商品规格信息
  url(r'^goods/(?P<pk>\d+)/specs/$', sku.SPUSpecView.as_view()),





  ############################# SPU ########################################


  # 新增SPU表数据---获取品牌信息
  # url(r'^goods/brands/simple/$' ,spu.SPUBrandView.as_view()),

  # 新增SPU表数据---获取一级分类信息
  # url(r'^goods/channel/categories/' ,spu.ChannelCategorysView.as_view()),







]


from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# 图片管理url
router.register(r'^skus/images',image.ImageView,basename='skus/images')
# SKU管理url
router.register(r'^skus', sku.SKUModelViewSet,basename='skus')
# SPU管理url
router.register(r'^goods', spu.SPUGoodsView,basename='goods')
# 订单管理url
router.register(r'^orders', order.OrdersView,basename='orders')

urlpatterns += router.urls
