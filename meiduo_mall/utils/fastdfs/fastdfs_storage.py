from django.conf import settings
from django.core.files.storage import Storage


class FastDFSStorage(Storage):

    def __init__(self):

        self.base_url = settings.PDFS_BASE_URL


    # 必写的函数
    def _open(self,name,mode='rb'):

        pass

    def _save(self,name,content,max_length=None):

        pass


    # 重写父类的 url函数  返回一个 IP：port/00/00/meizi.png  全路径
    def url(self,name):

         return self.base_url + name


