# Django backend tweak guide

## GENERAL INSTALL AND SETUP

### vitrual environment and package install

```shell
# virtual env build
mkvirtualenv horoengi
workon horoengi

# if you want to leave
deactivate

# pip install packages
pip install django==2.2
pip install djangorestframework


# start proj and apps
django-admin startproject backend
cd backend

```

### setup restframework

```shell
# 在proj的settings.py中增加相关设置

INSTALLED_APPS = [
    ...
    'rest_framework',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

```

### setup jwt

安装simplejwt

```
pip install djangorestframework_simplejwt
```

setup jwt in settings.py

```pytho
REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	],
}

# 默认鉴权用户，可更改
AUTH_USER_MODEL = "auth_user"
```

add url routers

```python
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt import views as JWTAuthenticationViews

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token', JWTAuthenticationViews.TokenObtainPairView.as_view(),
         name='get_token'),
    path('api/token/refresh',
         JWTAuthenticationViews.TokenRefreshView.as_view(), name='refresh_token'),

]
```

### 设置自己的JWT处理函数



### 数据库迁移和新用户设置

```
python manage.py migrate

python manage.py createsuperuser
```

### 出现编码错误

出现类似`UnicodeDecodeError: ‘gbk’ codec can’t decode byte 0xa6 in position 9737`这样的错误，需要对虚拟环境中的`\Lib\site-packages\django\views\debug.py`文件进行修改。属于平台上的问题。

如下所示：

```python
with Path(CURRENT_DIR, 'templates', 'technical_500.html').open() as fh:
```

改为

```python
 with Path(CURRENT_DIR, 'templates', 'technical_500.html').open(encoding='utf-8') as fh:
```

进行编码设置 ，然后再重新启动runserver，出错信息即可正常显示在页面显示。新增`encoding="utf-8"`。

```python
Path(CURRENT_DIR, 'templates', 'technical_500.html').open(encoding="utf-8")
```

或者对时区进行修改(经测试无效)
```python

LANGUAGE_CODE = 'zh-hans'
 
TIME_ZONE = 'Asia/Shanghai'
 
USE_I18N = True
 
USE_L10N = True
 
USE_TZ = False

```

### 测试api接口

在需要挂代理的机子上，必须在firefox的restclient里测试

Content-Type必须为application/json

```
{
    "username": "nekohor",
    "password": "11235813"
}
```

## MCI APP

### add new app called mci

```shell
python manage.py startapp mci

```



## 安装和配置Celery

### install celery and redis

```shell
pip install celery
pip install redis

# 如果在win10上运行容易出错，ValueError: not enough values to unpack (expected 3, got 0)
# 需要以eventlet作为celery启动时的-P线程池的参数
pip install eventlet
```

### setup celery

在项目目录下新建文件celery.py

```python
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

```

在项目的`__init__.py` 文件下新增

```python
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
```

在settings中添加配置

```python
# Celery application definition
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_MAX_TASKS_PER_CHILD = 10
CELERYD_LOG_FILE = os.path.join(BASE_DIR, "logs", "celery_work.log")
CELERYBEAT_LOG_FILE = os.path.join(BASE_DIR, "logs", "celery_beat.log")

# 这里是定时任务的配置
CELERY_BEAT_SCHEDULE = {
    'task_method': { # 随便起的名字
        'task': 'app.tasks.method_name', # app 下的tasks.py文件中的方法名
        'schedule': timedelta(seconds=10), # 名字为task_method的定时任务, 每10秒执行一次
    },
}
```

在响应的app中新建tasks.py文件

在view中使用task。

### 启动调试celery

```shell
celery -A backend worker -l info -P eventlet
```

若出现以下错误

```shell
[ERROR/MainProcess] consumer: Cannot connect to redis://localhost:6379/0: Error 11002 connecting to localhost:6379. Lookup timed out.
```

则设置redis-conf中的保护模式为关闭（非必须）

```shell
protected-mode no
```

修改django settings中的CELERY_BROKER_URL和CELERY_RESULT_BACKEND。使其为127.0.0.1而不是默认值localhost。



## oracle配置

oracle在django中有两种配置方法，如下所示。

```python
# service_name
　　DATABASES = {
　　　　'default': {
　　　　　　'ENGINE': 'django.db.backends.oracle',
　　　　　　'NAME': 'IP:端口号/service_name',
　　　　　　'USER': '用户名',
　　　　　　'PASSWORD': '密码',
　　　　}
　　}
 
# SID
　　DATABASES = {
　　　　'default': {
　　　　　　'ENGINE': 'django.db.backends.oracle',
　　　　　　'NAME': '数据库SID',
　　　　　　'USER': '用户名',
　　　　　　'PASSWORD': '密码',
　　　　　　'HOST':'IP',
　　　　　　'PORT':'端口号'
　　　　}
　　}
```

原生查询，如果有多个数据，则使用django.db 的connections进行查询

```python
from django.db import connections
with connections['my_db_alias'].cursor() as cursor:
	# Your code here..
```

结果发现有层层包装，不如直接使用`cx_Oracle`。



## MEDIA相关的设置

设置settings中media的相关参数。

```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = "/media/"
```

配置路由

```python
from django.conf import settings
from django.views.static import serve as static_serve
from django.urls import re_path

re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
```



## urls分解

各个app中分别新建urls.py文件。

```python
from django.urls import path
from .views import XXX

urlpatterns = [
    path('index/', XXX.as_view()),
]
```

项目的urls设置。注意引入include，这样就能成功分离路由文件，而网页的访问地址不会改变

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app1.urls')),
]
```


## 模板的注意事项

在APP中的模板与静态文件的文件夹，其中必须在文件夹内新建一个与APP同名的文件夹放置文件。

模板中使用static命令需要先加载。

```
{% load static %}
```

## 生成requirements.txt

单虚拟环境生成

```shell
pip freeze > requirements.txt
```

局部生成

```shell
# 安装
pip install pipreqs
# 在当前目录生成
pipreqs . --encoding=utf8 --force
```

注意：

 `--encoding=utf8` 为使用utf8编码，不然可能会报UnicodeDecodeError: 'gbk' codec can't decode byte 0xae in position 406: illegal multibyte sequence 的错误。

`--force` 强制执行，当 生成目录下的requirements.txt存在时覆盖。