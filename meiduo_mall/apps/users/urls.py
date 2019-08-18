
# users 子应用路由


from django.conf.urls import url
from . import views
urlpatterns = [

    # 注册的视图
    url(r'^register/$',views.RegisterView.as_view(),name='register'),

    # 用户名是否重复
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',views.UserCountView.as_view()),

    # 手机号是否重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.PhoneCountView.as_view()),


]
