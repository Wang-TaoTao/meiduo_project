
# 1.导包 Celery
from celery import Celery

# 2.配置celery可能加载到的美多项目的包
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 3.创建celery实例
app = Celery('celery_tasks')


# 4.加载celery配置
app.config_from_object('celery_tasks.config')

# 5.注册任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])




