
# oauth 子应用路由


from django.conf.urls import url
from . import views
urlpatterns = [

    # qq 专门负责返回登录网址
    url(r'^qq/login/$',views.QQAuthURLView.as_view()),

    # 接收QQ返回来的code
    url(r'^oauth_callback/', views.QQAuthUserView.as_view()),



]
