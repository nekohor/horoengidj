import pandas as pd
import cx_Oracle
from dateutil.parser import parse
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.http import HttpResponse, JsonResponse
from django.views import View

from celery.result import AsyncResult
from .tasks import test_task
from .tasks import tempo_data_calculation

# Your code here..
# Create your views here.


class TempoDataDemandView(View):

    def get(self, request):
        mill_line_tag = request.GET.get("line", "").upper()
        start_time = request.GET.get("start", "")
        end_time = request.GET.get("end", "")

        if (mill_line_tag == "") | (start_time == "") | (end_time == ""):
            resp = {}
            resp["code"] = 500
            resp["msg"] = "需要 [轧线, 开始时间, 结束时间] 3个参数"

        else:
            res = tempo_data_calculation.delay(
                mill_line_tag, start_time, end_time)
            resp = {}
            resp["code"] = 200
            resp["data"] = res.id
            resp["msg"] = "获取任务ID并开始排队计算"

        return JsonResponse(resp)


class TempoDataFetchView(View):
    def get(self, request, id):
        res = AsyncResult(id)

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
            content["fileUrlWithHost"] = request.get_host() + res.get()
        else:
            raise Exception("unhandled task state: {}".format(res.state))

        resp["data"] = content
        return JsonResponse(resp)


def test_start(request):
    res = test_task.delay()
    resp = {}
    resp["data"] = res.id
    return JsonResponse(resp)


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

    return JsonResponse(resp)
