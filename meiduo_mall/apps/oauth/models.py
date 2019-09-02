from django.db import models

from utils.models import BaseModel

# QQ 登录模型类
class OAuthQQUser(BaseModel):
    """QQ登录用户数据"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

# 微博 登录模型类
class OAuthSinaUser(BaseModel):
    """
    Sina登录用户数据
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    uid = models.CharField(max_length=64, verbose_name='access_token', db_index=True)

    class Meta:
        db_table = 'tb_oauth_sina'
        verbose_name = 'sina登录用户数据'
        verbose_name_plural = verbose_name

