
# verifications子应用路由


from django.conf.urls import url
from . import views
urlpatterns = [

  # 图形验证码
  url(r'^image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view()),

  # 短信验证码
  url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$',views.SMSCodeView.as_view()),

  # 找回密码第一步 （验证用户名和图形验证码）
  url(r'^accounts/(?P<username>\w+)/sms/token/$', views.PwdCodeView.as_view()),


  # 找回密码第二步 （验证access_token)
  url(r'^sms_codes/$', views.PwdTokenView.as_view()),

  # 找回密码第二步 （验证短信验证码）
  url(r'^accounts/(?P<username>\w+)/password/token/$',views.PwdSMSCodeView.as_view()),

  # 找回密码第三步 (设置密码）
  url(r'^users/(?P<username>\w+)/password/$',views.PwdRetpasswordView.as_view()),




]
