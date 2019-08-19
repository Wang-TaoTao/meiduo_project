from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer


class SecretOauth(object):

    # 1 加密
    def dumps(self,data):

        # 1.1 实例化加密的类--->设置签名--->设置过期时间

        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=3600)
        # 1.2 加密数据
        result = s.dumps(data)
        # 1.3 转成字符串 bytes--->str
        return result.decode()


    # 2 解密
    def loads(self,data):
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=3600)

        result = s.loads(data)

        return result.decode()