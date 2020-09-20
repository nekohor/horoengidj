import pandas as pd
import cx_Oracle
from dateutil.parser import parse
from pprint import pprint

from django.db import connections
from django.views import View
from rest_framework import views
from rest_framework import permissions
from rest_framework_simplejwt import authentication
from rest_framework.response import Response


from celery.result import AsyncResult
from .tasks import test_task
from .tasks import tempo_data_calculation

# Your code here..
# Create your views here.


class AsyncTempoExportTaskView(views.APIView):
    authentication_classes = (authentication.JWTAuthentication,)

    def post(self, request):
        data = request.data
        print(data)
        mill_line_tag = data.get("millLineTag", "").upper()
        start_time = data.get("startTime", "")
        end_time = data.get("endTime", "")

        if (mill_line_tag == "") | (start_time == "") | (end_time == ""):
            resp = {}
            resp["code"] = 500
            resp["msg"] = "需要参数 [轧线, 时间跨度]"

        else:
            res = tempo_data_calculation.delay(
                mill_line_tag, start_time, end_time)
            resp = {}
            resp["code"] = 200
            resp["data"] = {
                "taskId": res.id
            }
            resp["msg"] = "获取任务ID并开始排队计算"

        return Response(resp)


class AwaitTempoExportTaskView(views.APIView):
    authentication_classes = (authentication.JWTAuthentication,)

    def post(self, request):
        task_id = request.data.get("taskId", "")

        if task_id == "":
            resp = {}
            resp["code"] = 500
            resp["msg"] = "需要参数 [任务ID]"
        else:
            res = AsyncResult(task_id)
            resp = {}
            resp["code"] = 200
            resp["data"] = {}
            resp["msg"] = "查询任务结果"

            content = {}
            content["state"] = res.state
            if res.state == "PENDING":
                content["info"] = "任务在等待，尚未执行"
            elif res.state == "STARTED":
                content["info"] = "任务正在运行中"
            elif res.state == "FAILURE":
                content["info"] = "任务执行失败"
            elif res.state == "SUCCESS":
                content["info"] = "任务执行成功"
                content["fileUrl"] = res.get()
                content["fileUrlWithHost"] = (
                    "http://" + request.get_host() + res.get())
            else:
                raise Exception("unhandled task state: {}".format(res.state))

            resp["data"] = content
            return Response(resp)


def test_start(request):
    res = test_task.delay()
    resp = {}
    resp["data"] = res.id
    return Response(resp)


def test_end(request):
    res = AsyncResult(request.GET.get("id"))
    print(res.state)

    resp = {}
    resp["data"] = {}
    if res.state == "SUCCESS":
        resp["data"]["state"] = res.state
        resp["data"]["result"] = res.get()
    else:
        resp["data"]["state"] = "RUNNING"

    return Response(resp)
