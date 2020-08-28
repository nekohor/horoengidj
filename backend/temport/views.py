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
        mill_line_tag = request.GET.get("mill_line_tag", "")
        start_time = request.GET.get("start_time", "")
        end_time = request.GET.get("end_time", "")

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
            resp["msg"] = "正在计算中"

        return JsonResponse(resp)


class TempoDataFetchView(View):
    def get(self, request):
        task_id = request.GET.get("task_id")
        res = AsyncResult(task_id)

        resp = {}
        resp["code"] = 200
        resp["data"] = {}
        if res.state == "SUCCESS":
            resp["data"]["state"] = res.state
            resp["data"]["file_url"] = res.get()
        else:
            resp["data"]["state"] = "RUNNING"
        resp["msg"] = "获得计算结果"
        return JsonResponse(resp)


def test_start(request):
    res = something.delay()
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
