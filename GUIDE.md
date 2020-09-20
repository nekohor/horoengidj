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

安装 simplejwt

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

### 设置自己的 JWT 处理函数

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

进行编码设置 ，然后再重新启动 runserver，出错信息即可正常显示在页面显示。新增`encoding="utf-8"`。

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

### 测试 api 接口

在需要挂代理的机子上，必须在 firefox 的 restclient 里测试

Content-Type 必须为 application/json

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

## 安装和配置 Celery

### install celery and redis

```shell
pip install celery
pip install redis

# 如果在win10上运行容易出错，ValueError: not enough values to unpack (expected 3, got 0)
# 需要以eventlet作为celery启动时的-P线程池的参数
pip install eventlet
```

### setup celery

在项目目录下新建文件 celery.py

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

在 settings 中添加配置

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

在响应的 app 中新建 tasks.py 文件

在 view 中使用 task。

### 启动调试 celery

```shell
celery -A backend worker -l info -P eventlet
```

若出现以下错误

```shell
[ERROR/MainProcess] consumer: Cannot connect to redis://localhost:6379/0: Error 11002 connecting to localhost:6379. Lookup timed out.
```

则设置 redis-conf 中的保护模式为关闭（非必须）

```shell
protected-mode no
```

修改 django settings 中的 CELERY_BROKER_URL 和 CELERY_RESULT_BACKEND。使其为 127.0.0.1 而不是默认值 localhost。



### celery在windows下的错误

`celery`在4.x版本不再支持 windows 环境，在 windows 环境下运行，会出现`ValueError: not enough values to unpack (expected 3, got 0)`的报错，可行的解决方案有两种： 

1. 设置环境变量`FORKED_BY_MULTIPROCESSING=1`，完美解决问题（推荐）。吐槽一句，网上搜索到的 90% 的解决办法都是建议用`eventlet`甚至`solo`，实际上这个`celery`核心成员在 [issues#4081](https://github.com/celery/celery/issues/4081#issuecomment-349535810) 中提到的方法才是最优解。
2. 使用`eventlet`作为并发模型，需要注意由于`eventlet`和`gevent`使用了猴子补丁，所以使用过程中可能出现一些难以解决的奇怪问题，特别是不一定支持某些第三方模块的使用。官方文档强调不要用配置文件的方式指定`eventlet`和`gevent`，而是用启动命令`-P`，以免太迟应用猴子补丁而导致一系列奇怪问题。

### 时区问题

`celery`默认时区为`UTC`，比国内晚8个小时，需要配置时区：

```
enable_utc = True  # 默认为 Truetimezone = 'Asia/Shanghai'
```



如果不修改时区的话，会影响定时任务和`Flower`内的时间显示。

### Worker BrokenPipeError 问题

在使用`celery==4.3.0 kombu==4.6.3 amqp==2.5.0 redis==3.2.1`时，出现 worker 退出的情况，日志显示抛出`BrokenPipeError`的异常，根据 [issues#3773](https://github.com/celery/celery/issues/3773) ，应该是个尚未解决的 bug。建议用系统服务或守护进程的方式启动 worker 进程，保证进程抛出异常退出后能够重新启动。

## oracle 配置

oracle 在 django 中有两种配置方法，如下所示。

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

原生查询，如果有多个数据，则使用 django.db 的 connections 进行查询

```python
from django.db import connections
with connections['my_db_alias'].cursor() as cursor:
	# Your code here..
```

结果发现有层层包装，不如直接使用`cx_Oracle`。

## MEDIA 相关的设置

设置 settings 中 media 的相关参数。

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

## urls 分解

各个 app 中分别新建 urls.py 文件。

```python
from django.urls import path
from .views import XXX

urlpatterns = [
    path('index/', XXX.as_view()),
]
```

项目的 urls 设置。注意引入 include，这样就能成功分离路由文件，而网页的访问地址不会改变

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app1.urls')),
]
```

## 模板的注意事项

在 APP 中的模板与静态文件的文件夹，其中必须在文件夹内新建一个与 APP 同名的文件夹放置文件。

模板中使用 static 命令需要先加载。

```
{% load static %}
```

## 生成 requirements.txt

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

`--encoding=utf8` 为使用 utf8 编码，不然可能会报 UnicodeDecodeError: 'gbk' codec can't decode byte 0xae in position 406: illegal multibyte sequence 的错误。

`--force` 强制执行，当 生成目录下的 requirements.txt 存在时覆盖。

## 数据库错误

mysql 驱动情况下，出现错误

```python
AttributeError: 'str' object has no attribute 'decode'

```

则直接修改`C:\Users\nekohor\Envs\horoengi\lib\site-packages\django\db\backends\mysql\operations.py`，decode 换成 encode。

```python
    def last_executed_query(self, cursor, sql, params):
        # With MySQLdb, cursor objects have an (undocumented) "_executed"
        # attribute where the exact query sent to the database is saved.
        # See MySQLdb/cursors.py in the source distribution.
        query = getattr(cursor, '_executed', None)
        if query is not None:
            query = query.encode(errors='replace')
        return query
```

## pylint 错误

vscode 提示。

```json
{
  "resource": "/d:/NutCloudSync/code/horoengidj/backend/mci/charts.py",
  "owner": "python",
  "code": "no-member",
  "severity": 8,
  "message": "Class 'SomeModel' has no 'objects' member",
  "source": "pylint",
  "startLineNumber": 16,
  "startColumn": 14,
  "endLineNumber": 16,
  "endColumn": 14
}
```

需要安装以下包并在 vscode 中 pylint args 配置 add item: `--load-plugins=pylint_django`。

```shell

pip install pylint-django

```
