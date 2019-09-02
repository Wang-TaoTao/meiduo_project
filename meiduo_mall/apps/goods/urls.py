
# goods 子应用路由


from django.conf.urls import url
from . import views

urlpatterns = [

    # 商品列表页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(),name='list'),

    # 热销排行
    url(r'^hot/(?P<category_id>\d+)/$',views.HotGoodsView.as_view()),

    # 商品详情页
    url(r'^detail/(?P<sku_id>\d+)/$',views.DetailView.as_view(),name='detail'),

    # 分类统计商品访问量
    url(r'^detail/visit/(?P<category_id>\d+)/$',views.DetailVisitView.as_view()),

    # 用户浏览记录
    url(r'^browse_histories/$',views.UserBrowseHistory.as_view()),

    # 显示用户所有订单界面
    url(r'^orders/info/(?P<page_num>\d+)/$',views.ShowOrderView.as_view()),


    # 去评价 保存评价信息
    url(r'^orders/comment/$',views.CommentView.as_view()),


    # 获取商品评价详情
    url(r'^comments/(?P<sku_id>\d+)/$', views.CommentDetailView.as_view()),



]
