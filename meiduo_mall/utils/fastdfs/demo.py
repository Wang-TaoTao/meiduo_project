

#1.导包
from fdfs_client.client import Fdfs_client

#2.实例化
client = Fdfs_client('client.conf')

#3.上传图片
re = client.upload_appender_by_filename('/home/python/Desktop/en.jpg')


#检验
print(re)