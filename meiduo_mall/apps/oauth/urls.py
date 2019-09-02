
# oauth 子应用路由


from django.conf.urls import url
from . import views
urlpatterns = [

    # 获取QQ登录网址
    url(r'^qq/login/$', views.QQAuthURLView.as_view()),

    # 接收QQ返回来的code  --回调处理
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view()),

    # 获取微博登录扫码页面
    url(r'^sina/login/$', views.WeiboAuthURLView.as_view()),

    # 用户微薄扫码的回调处理
    url(r'^sina_callback/$', views.WeiboAuthOpenidView.as_view()),


]


