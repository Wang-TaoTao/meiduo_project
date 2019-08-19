import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User

# 定义一个函数，根据用户输入值来判断输入的是用户名还是手机号
def get_user_by_account(account):

    '''根据account查询用户'''

    try:
        if re.match('^1[3-9]\d{9}$',account):

            # 手机号登录
            user = User.objects.get(mobile = account)
        else:
            # 用户名登录
            user = User.objects.get(username = account)

    except Exception as e:
        return None

    else:
        return user



# 自定义用户认证后端
class UsernameMobileAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        '''重写认证方法，实现多账号登录'''

        # 根据传入的username获取user对象。username可以是手机号也可以是用户名
        user = get_user_by_account(username)

        # 校验user是否存在并校验密码是否曾雀
        if user and user.check_password(password):
            return user

