
# meiduo_admin 子应用路由


from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from .views import statistical
from .views import user
from .views import image
from .views import sku
from .views import spu
from .views import order
from .views import spec
from .views import option
from .views import brand
from .views import channel
from .views import permission
from .views import group
from .views import admin



urlpatterns = [

  # 后台管理登录页面入口路由 使用DRF JWT 提供的登录签发JWT的视图路由
  url(r'^authorizations/$', obtain_jwt_token),

  ############################# 数据统计url ########################################

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

  # 获取用户信息
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
  url(r'^goods/brands/simple/$' ,spu.SPUBrandView.as_view()),

  # 新增SPU表数据---获取一级分类信息
  url(r'^goods/channel/categories/$' ,spu.ChannelCategorysView.as_view()),

  # 新增SPU表数据---获取二级和三级分类信息
  url(r'^goods/channel/categories/(?P<pk>\d+)/$', spu.ChanelCategory23View.as_view()),


  ############################# 规格选项 ########################################

  # 新增规格选项数据---获取SPU表名
  url(r'^goods/specs/simple/$', option.SPUOptionSimpleView.as_view()),


  ############################# 商品频道 ########################################

  # 新增商品频道数据---获取频道组信息
  url(r'^goods/channel_types/$', channel.ChannelsView.as_view({'get':'channel_types'})),

  # 新增商品频道数据---获取一级分类信息
  url(r'^goods/categories/$', channel.ChannelsView.as_view({'get':'categories'})),

  ############################# 权限管理 ########################################

  # 新增权限数据---获取权限类别信息
  url(r'^permission/content_types/$', permission.ContentTypeAPIView.as_view()),

  ############################# 用户组管理 ########################################

  # 新增用户组数据---获取权限表信息
  url(r'^permission/simple/$', group.GroupSimpleAPIView.as_view()),

  ############################# 管理员管理 ########################################

  # 新增管理员---获取用户组信息
  url(r'^permission/groups/simple/$', admin.AdminSimpleAPIView.as_view()),

]


from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# 图片管理url
router.register('^skus/images',image.ImageView,basename='skus/images')
# SKU管理url
router.register('^skus', sku.SKUModelViewSet,basename='skus')

# 商品频道管理url
router.register('^goods/channels', channel.ChannelsView,basename='channels')
# 规格表管理url
router.register('^goods/specs', spec.SpecsView,basename='specs')
# 规格选项表管理url
router.register('^goods/options', option.OptionsView,basename='options')
# 品牌管理url
router.register('^goods/brands', brand.BrandsView,basename='brands')

# SPU管理url
router.register('^goods', spu.SPUGoodsView,basename='goods')
# 订单管理url
router.register('^orders', order.OrdersView,basename='orders')

# 权限管理url
router.register('^permission/perms',permission.PermissionView,basename='perms')
# 分组管理url
router.register('^permission/groups',group.GroupView,basename='groups')
# 管理员管理url
router.register('^permission/admins',admin.AdminView,basename='admins')



urlpatterns += router.urls


